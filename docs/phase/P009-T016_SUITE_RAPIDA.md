# P009-T016 — Suite pytest rápida

Fecha: 2026-10-20. Decisión: [D125](../DECISIONS.md#d125--p009-t016-suite-pytest-en-paralelo-y-git-sin-fork).
Petición del usuario: la suite tardaba más de 25 minutos; optimizarla al máximo eliminando redundancias y
complejidades. El usuario autorizó por separado xdist, agrupar llamadas Git del adaptador, recortar matrices con
criterio y usar `posix_spawn` en el adaptador Git.

## 1. Diagnóstico

Medido en macOS (10 núcleos: 4 de rendimiento y 6 de eficiencia), Python 3.14.4, Apple Git 2.50.1.

- 1586 pruebas pytest. Una ejecución en serie se interrumpió al 72 % tras más de 20 minutos. No había ninguna
  prueba aislada desproporcionada: 213 pruebas de 5 s o más sumaban dos tercios del tiempo.
- Más del 70 % del tiempo eran procesos Git lanzados por el producto: 591 en una sola prueba de importación y
  23 679 en tres ficheros (`test_import_commit`, `test_project_preparation`, `test_phase_closure`).
- Coste por llamada Git, en tres capas:
  - `/usr/bin/git` es un shim de `xcrun`: 11,1 ms por llamada frente a 5,8 ms del binario real.
  - `subprocess` con `cwd` y `close_fds=True` hace `fork` del proceso Python. Desde un worker de unos 300 MB cuesta
    6,9 ms por proceso, frente a 1,4 ms con `posix_spawn`, y explica que el tiempo de sistema igualase al de usuario.
  - El adaptador repetía procesos evitables. `_tree_with` lanzaba tres por fichero (`ls-tree`, `hash-object`,
    `update-index`). `bootstrap._tree` lanzaba dos. `capture` resolvía dos veces la ruta del índice.
    `LocalGit.code()` lanzaba `git --version` antes de cada pregunta booleana.
- `migrated_database` ejecutaba Alembic hasta head en cada prueba, unos 0,2 s cada vez en unas 300 pruebas.
- Las pruebas parametrizadas por flujo A/B montaban los dos mundos (checkout Git, SQLite y conversación) y solo usaban uno.

## 2. Cambios

### Pruebas

- `tests/conftest.py`: si `git` resuelve al shim de macOS, la sesión antepone al `PATH` un prefijo temporal con
  `bin/git`, `libexec` y `share` enlazados al Git real. Apple Git busca `git-core` relativo al ejecutable: un
  simple enlace o un wrapper `sh` no sirven, porque el primero pierde subcomandos como `submodule` y el segundo
  cuesta lo mismo que el shim. No cambia nada fuera de macOS ni con otro Git.
- `migrated_database`: una migración real a head por sesión (y por worker), copiada a cada prueba. El fichero
  se copia con el motor ya liberado y sin `-wal` (se comprueba). Las pruebas de ida y vuelta de migraciones
  siguen migrando sobre su copia.
- Los tests por flujo A/B solo montan el mundo de su flujo (`request.getfixturevalue`).
- xdist 3.8.0 por defecto (`-n auto --dist worksteal` en `addopts`); `-n 0` ejecuta en serie.
- Robustez bajo carga, ya frágil antes en serie con la máquina ocupada:
  - Los modos de la CLI falsa que terminan solos ya no usan el timeout de 0,2 s pensado para `hang`.
  - `group_gone` sigue esperando ante `EPERM`, que macOS devuelve mientras el grupo solo conserva zombis.

### Adaptador Git (producto)

- `_tree_with`: un solo `ls-tree -r -t --full-tree` para todos los modos (búsqueda por ruta exacta, sin pathspec).
  `hash-object` sigue siendo por ruta porque `--path` aplica los atributos de cada destino. Las altas
  consecutivas comparten un `update-index`, en el que cada `--cacheinfo` se aplica en orden y falla igual. Las
  bajas conservan su posición. Pasa de 3N+2 a N+3 procesos.
- `bootstrap._tree`: un único `hash-object -w --no-filters --stdin-paths` sobre copias temporales. Equivale a
  `--stdin` sin `--path`, que según la documentación de Git implica `--no-filters`. Un único `update-index`.
- `capture`: la ruta del índice real se resuelve una vez.
- `LocalGit.code()`: el soporte de `--no-lazy-fetch` se comprueba una vez por instancia, antes de la primera
  pregunta. Un fallo no se recuerda.
- `Git.run/code`: con el ejecutable resuelto a ruta absoluta en el `PATH` del entorno explícito, se lanza
  `git -C <raíz>` sin `cwd` y con `close_fds=False`, de modo que `subprocess` usa `posix_spawn`. Los descriptores de
  Python no son heredables (PEP 446), `os.dup`/`os.pipe` tampoco y `pass_fds` solo los marca en el hijo.
  SQLite abre con `O_CLOEXEC`. Un directorio inaccesible falla antes de lanzar Git con el mismo `GitError`
  («could not run»): nunca se convierte en un código de salida que `code()` confundiría con una respuesta. Un
  ejecutable relativo con barra o resuelto mediante una entrada relativa del `PATH` sigue el camino anterior.

Equivalencia comprobada contra la versión de `HEAD`, con mismos árboles, errores y mensajes. Casos: altas,
modificaciones, ejecutables, bajas, rutas con coma, atributos `text`/`eol=crlf`, destinos directorio o enlace,
conflicto fichero/directorio y bajas de rutas ausentes; bootstrap con 0, 1 y 4 documentos.
Nueva prueba: `test_unreachable_directory_is_a_launch_error_not_a_git_answer`.

## 3. Matrices recortadas

Criterio: se elimina una combinación solo si sus dos ejes siguen cubiertos por separado. O el producto completo
vive en otra prueba más barata, o cada valor de cada eje sigue apareciendo al menos una vez. El precedente es el
muestreo diagonal que ya usaba `test_preview_and_confirmation_refuse_new_filters_before_capture`. No se toca
ninguna matriz cuyos valores recorran caminos distintos: puntos de crash, orígenes, pasos del cierre ni etapas.

| Prueba | Antes | Después | Por qué basta |
|---|---|---|---|
| `test_cli_baseline::test_four_pairings_…_pilot_versions` | 4 | 2 | Las 4 parejas viven en `test_agent_roles` y en el recorrido Django; las mixtas ponen cada proveedor en cada papel con las versiones del piloto |
| `test_project_agents::test_selected_presets_drive_…` | 4 | 2 | Igual: el preset solo cablea proveedor por papel |
| `test_import_git_boundary::test_job_rejects_filters_…` | 4 | 2 | Diagonal (clean/local, process/include); el 2×2 completo queda en `test_inventory_rejects_filters_…` |
| `test_import_submodules::test_consumers_block_…` | 10 | 5 | Cada etapa una vez alternando ubicación; ubicación × tipo completos en `test_inventory_rejects_gitlinks_…` |
| `test_import_writer_local_objects::test_all_writer_commands_…` | 10 | 7 | A conserva los cinco puntos; B comparte escritor y prueba su composición sin crash y con recuperación tras `commit`. Los crash por flujo ya están en `test_import_commit` y `test_onboarding_commit` |
| `test_import_writer_local_objects::test_required_source_or_sealed_…` | 8 | 6 | A conserva los cuatro objetos; B, uno de origen y uno sellado |

16 combinaciones menos y 1 prueba nueva: 1571 pruebas (1570 pasan, 1 se omite).

## 4. Resultados

| Configuración | Suite pytest |
|---|---|
| Original, en serie | interrumpida al 72 % tras más de 20 min |
| Shim, plantilla y mundos A/B, en serie | 24:04 (con otras ejecuciones compitiendo) |
| + recortes y xdist (10 workers) | 5:57 (5 fallos de temporización, corregidos) |
| + agrupación Git | 5:05 |
| + `posix_spawn` (10 / 8 / 6 workers) | 4:19 / 4:25 / 4:32 |
| Final, en serie (`-n 0`) | 14:01 |
| Final, comando de AGENTS.md (`-n auto`) | 4:22 |

En la muestra de tres ficheros, las llamadas Git bajan de 23 679 a 17 816 (−25 %). Esos ficheros tardan en serie
179 s, frente a 273 s antes de tocar el adaptador. Lo que queda es necesario: unos 11 procesos por `capture` y un
`hash-object` por documento. `unittest` (0,1 s) y `node --test` (0,24 s) no requerían cambios.

## 5. Verificación y límites

- Suite pytest completa en paralelo tras cada cambio. Estado final: 1570 pasan y 1 se omite, tanto en serie
  (14:01) como con el comando de AGENTS.md (4:22), y también con 8 y 6 workers. Además pasan `unittest`,
  `node --test`, `alembic check` y la comprobación de equivalencia del adaptador contra `HEAD`.
- No se ejecutó el harness, ni proveedores, smokes ni el wheel.
- Medido en una sola máquina macOS. En Linux no hay shim de Git y `posix_spawn` ya era más barato; el
  paralelismo sí aplica.
- Una prueba que dependa de tiempos ajustados puede volver a mostrarse frágil con 10 workers. Las dos detectadas
  se corrigieron sin relajar lo que comprueban.
