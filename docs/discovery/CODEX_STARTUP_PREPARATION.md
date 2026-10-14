# Preparación del diagnóstico de confianza Codex (D067)

Completada el 2026-10-14 sobre `e2f272c`, Git inicialmente limpio.
Petición del usuario: seguir con la preparación activa de NEXT_STEPS.
[Controlador/ensayo sintético](CODEX_STARTUP_PREPARATION.py),
[comandos proyectados, hashes y evidencia](CODEX_STARTUP_PREPARATION.json).

## Dictamen

**Preparación completada con incompatibilidad: propuesta no apta para ejecutar
la CLI real.** El perfil de lectura/escritura acotadas y denegación por defecto
no consigue un arranque útil del proceso Python mínimo en este Mac: termina
con SIGABRT antes del marcador, stdout/stderr vacíos. No se amplían permisos
de lectura o IPC para hacer pasar el ensayo. No se solicita autorización para
ejecutar esta candidata ni se proporciona una orden que ejecute Codex.

La causa interna de SIGABRT no está acreditada. No se atribuye a auth, Codex,
Mach/XPC, dyld o una operación concreta. Es diferente del rechazo inicial del
sandbox de desarrollo (exit 71 con `sandbox_apply: Operation not permitted`)
y del perfil deliberadamente inválido (exit 65). El resultado solo acredita
que la candidata actual no permite medir el objetivo con utilidad demostrada.

El criterio de la tarea admite este dictamen preciso. No se anuncia una
imposibilidad general de otro diagnóstico, ni se interpreta conservar hashes
como garantía de aislamiento. D064/D065 siguen sin calificar una frontera
para CLI real; la escritura de confianza D061/D062 continúa pendiente.

## Alcance proyectado, sin ejecutar

Los dos comandos completos están en `planned_only` del manifiesto. Se fijaron:

- Nativo Codex 0.162.1, SHA-256
  `74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0`.
  Lectura/hash de esa imagen pública, sin ejecutar wrapper/npm, version/help
  o binario. No cambia baseline, paquete instalado, modelo o esfuerzo.
- Writer de la prueba anterior: `gpt-6-luna`/`low`, `workspace-write`, sin red
  de herramientas, never, checkout canónico y exclude_slash_tmp. Parámetros
  de memoria de cli-8 completos, sesiones nuevas y fuentes/reglas omitidas.
  La elección se conserva únicamente en el borrador; no concede consumo.
- Dos variantes: sin override, y `projects."<checkout ficticio>".trust_level="trusted"`
  en el argv. TOML analizado; solo difieren en ese campo. No se declara que
  el override evite escribir; esa es precisamente la hipótesis no probada.
- HOME/CODEX_HOME/TMPDIR privados ficticios y USER del UID local, PATH mínimo.
  Auth deliberadamente ficticia/inválida, sin copiar/enlazar credenciales.
  Checkout con metadatos Git mínimos nuevos, sin clone, Git subprocess o runs.
  Ninguna garantía de alcanzar thread/start con ese estado inicial.
- Hasta **dos procesos CLI si otra candidata fuese calificada y autorizada**,
  uno por variante, sin retry/fallback: 10 s por proceso, TERM y hasta 1 s antes
  de KILL, comprobación del grupo; límite operativo propuesto de 30 s para el
  conjunto, incluida limpieza. Capturas de hasta 16 KiB por stream, archivos
  privados 0600 bajo raíz 0700. Exceso/timeout/señal, fallo de launcher, perfil,
  identidad/grupo o conservación detendrían el diagnóstico; no continuar al
  segundo tras un fallo de control. No restaurar originales después.

Nada de esto está conectado al adaptador, preflight, TOML operativo o supervisor.
El controlador retenido solo acepta preparación o modos internos de Python
sintético; no tiene un modo de ejecución de proveedor. Un cambio en el hash
del nativo rechaza la preparación. La propuesta permanece `execution_eligible=false`.

## Lectura, red, IPC y fuentes de auth

La candidata usa `(deny default)`. Permite lectura del HOME/checkout/TMPDIR
ficticios, worker e imágenes públicas concretas, bibliotecas de sistema y
runtime Python fijado; escritura solo en las tres raíces ficticias. Permite
fork/exec de imágenes concretas, sysctl-read y mapeo de código público.
No permite todo HOME real, /tmp, todas las lecturas, red o servicios Mach.
El binario futuro situado bajo el HOME real se nombraría por literal; no se
concede su directorio padre ni un almacén de auth. Esa variante no se aplica.

La prueba OS del perfil vigente aborta antes de emitir las observaciones de
lectura/escritura del worker: **esas denegaciones directas no se dan por
verificadas**. No se prueban credenciales/config reales, llavero, launch services
o servicios Mach/XPC. Los únicos destinos que el worker habría consultado son
canarios y socket ficticios dentro del ensayo; no arrancó hasta ese punto.
No se contacta red externa ni se realiza login/refresh/inferencia.

Cerrar fd, capturar stdout/stderr como datos y congelar raíces son necesarios,
pero no resuelven aliases/carreras ni delegación general de D065. No se elige
el perfil D063 que permitía lecturas generales para sortear el fallo. No se
certifica aislamiento del propietario/root, disponibilidad de sandbox-exec,
composición interna real de Codex o supresión de efectos del SO fuera del
proceso. No se audita todo el filesystem ni se inspeccionan crash reports.

## Controlador ensayado independientemente

Una vez registrada la incompatibilidad, se prueban **otros casos** con un
Python fake fijo, sin afirmar contención OS. Los resultados identifican
`backend=controller-synthetic`; la candidata OS tiene su etiqueta distinta.
No se relanza el caso denegado sin sandbox: el objetivo filesystem de la
candidata nunca se ejecuta en el backend sintético. Este backend solo usa
código de prueba conocido y datos nuevos; no acepta una CLI como launcher.

| Caso | Observación |
|---|---|
| Fake que persiste antes de fallar auth | Cambio de hash observado; exit 23 no borra ese efecto. |
| Fake etiquetado con override que también persiste | Misma clasificación; no se supone que el override funcione. No es semántica Codex. |
| Fake sin cambio tras marcador | Clasificación explícitamente sintética; no acredita ausencia de todas las persistencias. |
| Auth ficticia falla antes del marcador | Inconcluso; no se acepta como prueba de no persistencia en thread/start. |
| Texto del marcador dentro de un error | No se acepta como evento: se analiza JSON y el campo type exacto. |
| Fd ajeno cerrado antes de exec | EBADF, canario exterior intacto. No prueba tipos/destinos de todos los fd de una CLI. |
| TERM, timeout y salida excesiva | Señal -15; límites diferenciados, grupo observado ausente. Captura incompleta marcada en timeout/exceso. |
| Launcher inexistente | Cero objetivo y cero fallback. |
| Perfil inválido, ensayo OS separado | Exit 65 sin marcador; tampoco se ejecuta su objetivo sin perfil. |

La matriz final tiene **12 casos: diez de controlador y dos OS**. Once
lanzamientos exteriores y sus grupos observados ausentes al acabar; el caso
launcher inexistente crea cero. `launches` cuenta el proceso exterior, no
procesos futuros proyectados.
Auth ficticia y canarios protegidos conservan bytes/modo/mtime en todos los
casos. Solo config.toml sacrificial de dos fakes cambia, deliberadamente.
Capturas privadas/rangos de tamaño/hashes y snapshots anteriores/posteriores
quedan en el manifiesto y las áreas retenidas.

## Reproducción y verificaciones

Solo biblioteca estándar, Python 3.14.4 y macOS 26.4.1 arm64:

```sh
python3 docs/discovery/CODEX_STARTUP_PREPARATION.py
```

Es un ensayo de preparación, sin CLI real. Conserva raíces nuevas bajo
`/private/tmp/h67-synthetic-*`, sin limpieza o adopción de áreas anteriores.
`preparation_completed=true` indica que se produjo el dictamen y pasaron los
controles independientes; nunca significa que pueda ejecutarse el borrador.

Primera ejecución bloqueada dentro del sandbox de desarrollo; segunda exterior
autorizada por permisos de herramienta termina con SIGABRT en el fake mínimo.
Añadir mapeo ejecutable solo de las imágenes/bibliotecas públicas no cambia
ese resultado. Se conservaron los ensayos con sus hashes de código distintos.
La evidencia final es `h67-synthetic-a0aig4i2`, cuyo hash coincide con la sonda
versionada. Las ampliaciones posteriores verificaron controlador, grupos,
metadatos Git ficticios, parser y snapshots; no relajaron la frontera OS.

Regresión pertinente existente: **14 passed, 39 deselected**, 2,97 s:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_cli_agents.py -k 'gate or cancel or timeout'
```

También sintaxis, JSON/TOML, hashes de perfiles/capturas/source y enlaces/diff.
No suite completa, build, Node o QA visual: producto/API/UI/configuración y
dependencias sin cambios. cli-8/local-config-2, contratos/historiales/permisos,
jobs/locks, baseline y modelos intactos. Cero CLI real/version/help, proveedores,
subagentes, harness de desarrollo, publicación o push.

## Siguiente vía separada

La candidata **no se ofrece para aprobación de ejecución**. Antes de otra
prueba real, verificar con fuente identificable del pin qué condición activa
la persistencia de confianza y si un override de transporte la evita sin
escribir. Priorizar esa capacidad específica sobre otro wrapper no calificado.
Fuente/versionado y condiciones deben estar acreditados; documentación actual
o nombres de símbolos solos no bastan. Si no hay fuente verificable o no se
puede demostrar la supresión, registrar el límite antes de cambiar transporte,
auth o aislamiento. No se investiga esa tarea en esta entrega.

Otra ejecución exige propuesta suficiente y consentimiento nuevo; D050/D055/
D057/D060 siguen agotados. No se cierran las comprobaciones de flujos ni se
inicia matriz 3/4, archivado documental o H6.2.
