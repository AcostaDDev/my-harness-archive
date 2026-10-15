# Calificación sintética de la contención macOS (D064)

Completada el 2026-10-14 sobre `aaccad0`, con Git inicialmente limpio.
[Propuesta D063](CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
[sonda reproducible](CODEX_CONTAINMENT_QUALIFICATION.py) y
[resultados, hashes y procedencia](CODEX_CONTAINMENT_QUALIFICATION.json).

## Dictamen

**Candidata no calificada para integración en producto tal como está.**
La denegación de escrituras directas funciona en las rutas ensayadas, pero no
constituye una frontera completa contra cambios externos. Se observaron tres
vías de escritura fuera de las raíces: descriptor abierto antes del sandbox,
hardlink preexistente y delegación mediante pipe a un proceso no contenido.
Además, el sandbox interno sintético lector fue rechazado por el SO. No se
conecta el prototipo al adaptador, TOML, preflight ni jobs del producto.

Este es un resultado válido de la tarea de calificación, cuyo criterio permitía
un límite preciso de viabilidad. No certifica autenticación, comportamiento de
Codex, refresh remoto ni imposibilidad de una solución distinta. No se modifica
el diseño aceptado para sortear los hallazgos.

## Entorno, reproducción y evidencia

Python 3.14.4, macOS 26.4.1 arm64. Solo biblioteca estándar, procesos Python y
`/usr/bin/sandbox-exec`; ninguna CLI de proveedor, ni version/help. HOME y auth
son ficticios en cada caso, USER corresponde al UID local y TMPDIR es privado
bajo una raíz nueva de `mkdtemp`. El token literal ficticio no sale en las
capturas. No se leen configuración global, credenciales reales o llavero.

Desde la raíz del repositorio, en este entorno macOS:

```sh
python3 docs/discovery/CODEX_CONTAINMENT_QUALIFICATION.py
```

La sonda imprime la ruta de `result.json` y conserva perfiles, fixtures y
registros de identidad en `/private/tmp/h64-synthetic-*`. Un error termina con
exit 1 y evidencia parcial; no lanza el objetivo sin sandbox ni repite el caso.
`qualification_completed=true` significa que terminó la matriz y sus
aserciones, **no** que sea apta para producción. No usar `python -O`, que
eliminaría las aserciones de este ensayo.

Ejecuciones de esta entrega:

- `h64-synthetic-3mb5o4h9`: el sandbox de desarrollo rechaza aplicar el perfil,
  exit 71 y `sandbox_apply: Operation not permitted`, objetivo no iniciado.
- `h64-synthetic-ipawap6e`: ensayo fuera del sandbox de desarrollo, autorizado
  mediante permisos de herramienta; 24 casos completos.
- `h64-synthetic-nruz2_9v`: 26 casos, con controles de descriptor cerrado y
  fallo de identidad antes de GO; exit 0.
- `h64-synthetic-jmkwq0q_`: matriz final de 27 casos, añade launcher existente
  no ejecutable. Fuera del sandbox con autorización, exit 0. Es la evidencia
  principal y coincide con el hash de la sonda versionada. Los resultados preliminares se conservan con su hash
  de código anterior; no se atribuyen al código final.

Cada escenario tiene un lanzamiento exterior como máximo; `launches` cuenta
ese proceso, no sus hijos deliberados. Launcher ausente o no ejecutable: cero. Los casos son
experimentos separados, no retries de una invocación. La ejecución del gate
existente es un helper Python aislado; no arranca el harness ni su supervisor.

## Matriz de resultados

| Criterio | Ensayo y observación |
|---|---|
| Raíces | Una pareja canónica admitida; 17 rechazos: raíz amplia, HOME/estado/artefactos y ancestros, raíces iguales/anidadas, alias de raíz, `..`, relativa, ausente, control de línea, symlink/hardlink/FIFO preexistentes. Las raíces deben existir. |
| Lector/escritor | Lector no escribe checkout; escritor sí. Ambos escriben TMPDIR con espacios/comillas y subárbol SQLite. No se permite todo `/tmp`. |
| Escritura directa | En cada perfil: 17 operaciones denegadas sobre config/auth, unlink, chmod, utime, temporal hermano, caché, lock, SQLite en HOME, estado/artefactos, prefijo hermano, `..`, escape symlink, rename atómico, creación de hardlink y FIFO exterior. |
| Estado auxiliar | Config temporal/rename, lock exclusivo y SQLite WAL funcionan en TMPDIR. Sus equivalentes en HOME fallan. Esto no demuestra que una CLI admita redirigir su estado allí. |
| Auth ficticia | Lectura correcta; ausencia e ilegibilidad se distinguen. Refresh ficticio intenta un save, recibe denegación y sale 23; cero fallback. Hash/modo/mtime de auth/config conservados. La ilegibilidad usa una denegación explícita del perfil, sin cambiar permisos globales. |
| Descendientes | Hijo de lector y escritor recibe denegación al escribir auth. |
| Sandbox anidado | Exterior escritor con interior escritor: checkout/TMPDIR permitidos, HOME/exterior denegados. Exterior escritor con interior lector: exit 71 al aplicar, stdout vacío y ningún objetivo interno. Observación repetida en ambos ensayos completos. |
| Descriptor heredado | Un fd abierto por el padre para archivo sacrificial exterior permite escribirlo desde el hijo contenido. Control con `close_fds` y sin `pass_fds`: EBADF, archivo intacto. |
| Hardlink preexistente | Escribir por un alias ya presente en TMPDIR modifica el archivo sacrificial exterior. Crear un hardlink hacia auth después del sandbox queda denegado. El validador previo rechaza enlaces existentes, pero no es una prueba contra carreras. |
| IPC propio | Un pipe heredado permite solicitar una escritura a un helper Python externo: archivo sacrificial exterior modificado. Una conexión nueva a un socket Unix del servicio sintético propio queda denegada por `deny network*`; el servicio no recibe petición. |
| Launcher/perfil | Launcher ausente/no ejecutable, perfil ausente o sintácticamente inválido: no aparece marcador del objetivo. Perfiles erróneos salen 65, sin ejecución alternativa. El rechazo de SO del primer ensayo también detiene. |
| Gate/identidad | Gate real existente con padre/journal ficticios: PID=PGID observado, registro fsync antes de GO y marcador solo después. EOF, byte inválido y fallo simulado de persistencia de identidad salen 125 sin objetivo; cancelación previa a GO tampoco lo inicia. |
| Fin/cancelación | Terminal ausente con exit 0 no se acredita como complete. Señal TERM observada como -15. Timeout y cancelación terminan grupo con hijo cooperativo reaped; hijo que ignora TERM requiere KILL (-9). Los ocho grupos de gate se observan ausentes al acabar. |

Las comprobaciones de conservación cubren auth/config por caso, incluidos los
gates tras cancelación. Los tres archivos **sacrificiales** exteriormente
modificados son fixtures deliberados, separados de auth/config. No se afirma
que todo el directorio de ensayo permaneciera inmutable ni que se auditara todo
el filesystem. El resultado conserva las denegaciones y los escapes, sin
convertir la mera ausencia de cambio de auth en aislamiento completo.

## Límites que impiden integrar esta candidata

1. **Capacidades heredadas.** Cerrar todos los fd no autorizados es necesario.
   Stdout/stderr deberían seguir siendo pipes de captura; un archivo abierto
   por el padre no queda protegido solo porque su ruta esté fuera del perfil.
   El ensayo demuestra la diferencia, no implementa una política de fd.
2. **Alias y carreras.** Canonicalizar y rechazar `st_nlink != 1` reduce casos
   estáticos, pero el escaneo no constituye una frontera frente a escritores
   concurrentes, reemplazo de directorios o aliases introducidos después.
   Los casos de escape se ejecutan deliberadamente sin esa admisión para
   medir el SO. No se anuncia protección adversarial basada en un precheck.
3. **Delegación.** Un servicio externo con autoridad de escritura actúa fuera
   del sandbox del solicitante. La prueba solo usa un helper y un socket
   propios. No se contactan llavero, launch services, servicios Mach/XPC del
   usuario ni otros servicios del sistema. El perfil permite operaciones por
   defecto; la denegación de un socket Unix no certifica aislamiento IPC.
4. **Composición interna.** Los perfiles sintéticos reproducen la intención
   de D059 (checkout canónico, TMPDIR explícito, sin `/tmp` amplio ni red), no
   el perfil exacto generado por Codex. El rechazo del lector requiere
   diagnóstico separado; no se relaja el sandbox externo ni se elimina el
   interno. El éxito escritor no certifica la CLI real.
5. **Auth y red.** El fake solo simula lectura, error y persistencia local de
   refresh; no realiza rotación en un servidor. La red está denegada durante
   estos ensayos. Permitir inferencia podría permitir refresh remoto aunque
   su save falle; la candidata no garantiza «sin refresh». Fuente efectiva de
   auth, auxiliares obligatorios, keyring y continuidad de sesión siguen sin
   certificar. No hay prueba de otras plataformas ni de disponibilidad futura
   de sandbox-exec.
6. **Procesos.** Gate y cancelación se prueban sobre grupos propios vivos y
   descendientes cooperativos. No se certifican daemonización, escape de
   grupo, PID reutilizado ni recuperación de procesos antiguos. El journal
   es un archivo ficticio, no una nueva autoridad ni prueba SQLite de producto.

## Verificación y siguiente alcance separado

Matriz OS final de 27 escenarios completada y 14 pruebas existentes focales
correctas (39 deseleccionadas):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_cli_agents.py -k 'gate or cancel or timeout'
```

También sintaxis Python, hashes/JSON, enlaces documentales y `git diff --check`.
No suite completa, build, Node o QA visual: no cambia código de producto, UI,
API, esquema, codec, dependencias o locks. Se conservan `cli-7`, `local-config-2`,
D024/D059, modelos, permisos y snapshots históricos. Sin proveedores, red
externa, login, cambios globales, subagentes, harness de desarrollo o push.

Siguiente tarea propuesta, **no iniciada**: diagnóstico offline acotado del
rechazo de sandbox anidado lector y diseño de una frontera revisada que trate
fd, alias/carreras y delegación. Deberá emitir criterios verificables o
incompatibilidad antes de integrar; no convertir D064 en autorización de
`cli-8`. Si se propone cambiar autenticación, aislamiento o efectos aceptados,
se señalará como decisión de diseño pendiente del usuario. Cualquier prueba
real exige propuesta y consentimiento nuevos, con el límite de refresh
resuelto. La matriz 3/4 y H6.2 permanecen sin iniciar.
