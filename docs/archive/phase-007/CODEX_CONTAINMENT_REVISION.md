# Diagnóstico del anidamiento y frontera revisada (D065)

Completado offline el 2026-10-14 sobre `b73d9d4`, con Git inicialmente limpio.
[Tarea anterior y límites D064](CODEX_CONTAINMENT_QUALIFICATION.md),
[sonda independiente](CODEX_CONTAINMENT_REVISION.py) y
[evidencia con resultados y hashes](CODEX_CONTAINMENT_REVISION.json).

## Dictamen

**No integrar D063 ni una variante basada solo en prechecks y cierre de fd.**
Existe una composición sintética que conserva dos capas, HOME/auth en origen
y denegación de escritura global: repetir el perfil lector o escritor funciona.
Sin embargo, las composiciones ensayadas con restricciones distintas fallan
al aplicar la segunda capa. No hay evidencia de compatibilidad con el perfil
interno exacto de Codex, ni frontera demostrada frente a aliases concurrentes
o delegación general. La tarea admite este dictamen de incompatibilidad precisa;
no requiere implementar un backend que no haya satisfecho sus condiciones.

El diagnóstico acota D064: **no es una imposibilidad general de anidar un lector**.
Lector→lector funciona; escritor→lector y lector→escritor fallan. También falla
añadir una denegación de lectura al lector, aunque ese perfil funciona solo y
repetido. Cwd, archivo frente a inline y el programa objetivo no explican el
rechazo en los controles probados. No se elimina ninguna capa para aprobarlo.

## Reproducción y procedencia

Python 3.14.4, macOS 26.4.1 arm64; `/usr/bin/sandbox-exec`, Python y un control
`/usr/bin/true`. Datos nuevos exclusivamente ficticios en cada caso: HOME,
auth/config, checkout, TMPDIR con espacios/comillas y archivos sacrificiales.
USER corresponde al UID local. No se importa el producto ni se ejecuta el
harness, una CLI real, version/help, preflight, login o un agente.
OpenAI Docs se limita a las referencias locales D059–D064 por el alcance
offline; no se consulta documentación web actual para certificar el pin.

```sh
python3 docs/discovery/CODEX_CONTAINMENT_REVISION.py
```

La sonda conserva `result.json`, perfiles y fixtures en una raíz nueva
`/private/tmp/h65-synthetic-*`. Un rechazo nunca lanza el objetivo sin sandbox.
Cada caso es un experimento independiente, sin retry/fallback. `launches=1`
cuenta el lanzamiento exterior; los 22 casos anidados incluyen una segunda
aplicación deliberada, y los dos casos de pipe usan un helper propio exterior.
El cierre de fd de esos controles no es una integración en el adaptador.

Ejecuciones conservadas, con hashes de sus versiones en el manifiesto:

- `h65-synthetic-2nhg7awn`: sandbox de desarrollo rechaza ya la primera capa;
  exit 71, objetivo no iniciado, diagnóstico incompleto.
- `h65-synthetic-ompv8ox0`: ejecución exterior autorizada por permisos de
  herramienta; 15 controles exploratorios completos.
- `h65-synthetic-f5ryecrp`: 29 controles ejecutados. Una expectativa de la
  sonda era incorrecta: la denegación redundante de red sí compone. Se conserva
  el fallo de comprobación; no se presenta como fallo del SO ni resultado final.
- `h65-synthetic-lprizorw`: matriz final de **32 casos**, comprobaciones
  completas y exit 0; ejecución exterior autorizada. Hash de código coincide
  con la sonda versionada. No se atribuyen los ensayos previos a este código.

La primera denegación es una limitación del contexto de desarrollo. Las doce
denegaciones finales ocurren aplicando la segunda capa en un proceso que ya
pasó la primera, fuera de ese contexto. Se distinguen ambas observaciones.

## Resultado del diagnóstico mínimo

| Control | Observación final |
|---|---|
| Lector, escritor y sin escrituras, cada uno solo | Exit 0; auth ficticia legible, HOME/exterior no escribibles. Checkout solo para escritor; TMPDIR salvo perfil sin escrituras. |
| Escritor→escritor, lector→lector, sin escrituras→sin escrituras | Exit 0 con las restricciones esperadas. Ambas capas permanecen. |
| Escritor→lector, lector→escritor; ambos→sin escrituras o perfil default | Exit 71, `sandbox_apply: Operation not permitted`, stdout vacío. |
| Escritor→lector desde checkout, TMPDIR o exterior | Mismo rechazo en los tres cwd. |
| Escritor→lector con perfiles inline o con `/usr/bin/true` | Mismo rechazo; no depende del archivo de perfil ni del arranque Python. |
| Lector→lector inline | Exit 0; no hay rechazo general de `-p`. |
| Lector con comentario, orden de denegaciones cambiado o deny de red redundante en la segunda capa | Exit 0; el texto no tiene que ser idéntico byte a byte. |
| Lector→lector con denegación adicional de lectura del exterior | Exit 71. Ese perfil solo y repetido da exit 0; no es un error de sintaxis. |
| Default→escritor | Exit 71 aun con primera capa menos restrictiva; no basta que la segunda sea un subconjunto. |
| Default repetido y perfil mínimo repetido | Exit 0 con `/usr/bin/true`; controles de aplicación, sin intentos de escritura. No son perfiles candidatos ni permisos ampliados de operación. |

**Observado:** el SO rechaza las segundas políticas diferentes ensayadas y
admite las repeticiones y variaciones sin cambio efectivo probado.
**Hipótesis:** reutilización/equivalencia de la representación compilada del
perfil, en lugar de composición arbitraria por intersección. No se inspeccionó
esa representación ni el kernel, y no se afirma que cualquier par equivalente
componga o que cualquier diferencia falle. El errno no identifica por sí solo
la condición interna exacta. La evidencia mide estos perfiles en este SO.

Los perfiles son los mínimos de D064, no los que genera la CLI fijada. No se
extrae ni ejecuta el sandbox interno real de Codex. Repetir un perfil externo
en el fake no acredita que Codex pueda usarlo: sus herramientas, red, lectura,
auxiliares y reglas internas podrían producir otra política. Añadir una
denegación IPC al externo tampoco puede darse por compatible a partir de estos
resultados. No se propone modificar el sandbox interno para igualarlos.

## Capacidades y carreras: medidas delimitadas

Se añadieron seis controles, sin tocar servicios o archivos reales:

- **Fd de archivo:** heredarlo modifica un sacrificial exterior; con
  `close_fds=True` y sin `pass_fds`, el mismo número devuelve EBADF y el
  original permanece intacto.
- **Pipe a helper propio exterior:** heredarlo permite una petición de
  escritura exterior. Cerrarlo devuelve EBADF y el helper recibe EOF sin
  escribir. El helper se espera y termina; no hay servicio persistente.
- **Carrera de hardlink:** el escaneo admite TMPDIR sin aliases; el hijo
  contenido anuncia readiness. El padre propio añade un hardlink a un
  sacrificial exterior después de esa admisión y antes de GO. El hijo lo
  escribe y modifica el exterior. Es una carrera ordenada reproducible,
  no una hipótesis basada en probabilidades o un alias ya presente al escanear.
- **Stdout como captura inerte:** el objetivo emite `W` por fd 1, capturado
  como bytes. El padre no interpreta órdenes y el sacrificial no cambia.
  Esto delimita la autoridad del receptor; no acredita aislamiento de todo IPC.

Auth/config ficticios conservan **bytes, modo y mtime en los 32 casos**.
Solo los tres sacrificiales declarados cambian: fd heredado, pipe heredado y
hardlink posterior. No se anuncia una auditoría de todo el filesystem.
Los originales y resultados D061–D064 no se modifican.

## Frontera revisada: condiciones obligatorias, aún no calificadas

La revisión deja de tratar un perfil de rutas como una frontera suficiente.
Estos criterios definen qué tendría que demostrar otra candidata antes de
integrarse; no son capacidades ya disponibles en producto:

| Área | Medida y criterio verificable | Estado |
|---|---|---|
| Capas | Conservar sandbox interno y contener el proceso CLI desde su primer efecto. Ensayar los perfiles exactos por rol y las restricciones combinadas sin ampliar raíces ni eliminar capas; rechazo antes del objetivo implica incompatibilidad, nunca relanzamiento desnudo. | Solo perfiles sintéticos iguales/variaciones probadas componen. CLI exacta pendiente. |
| Descriptores | Cerrar todo fd ajeno antes del exec; gate cerrado tras GO, stdin de prompt y stdout/stderr como pipes sin autoridad exterior. Inventariar tipos y destinos; rechazar archivos/sockets heredados inesperados y probar fd deliberadamente filtrado, EOF, errores y descendientes. | Cierre de archivo y pipe demostrado en laboratorio; gate existente cierra su pipe antes de `execvpe`. Sin nueva política de fd en producto. |
| Raíces e inodos | Checkout/TMPDIR privados y canónicos, separados de HOME/estado/artefactos. Sin symlinks, hardlinks o especiales admitidos. Además, excluir por una frontera efectiva modificaciones de terceros al namespace/inodos durante toda la ejecución, o rechazar soporte. Probar alias introducido después de cada guardia, reemplazo de ancestros y escrituras por fd abierto. | Precheck, 0700 del mismo UID, lock cooperativo y diff posterior no satisfacen la exclusión. Carrera observada; no hay mecanismo calificado. |
| Delegación | Ningún canal a receptores con autoridad de escritura exterior. Capturas inertes; denegar creación/conexión IPC no requerida y evitar servicios de sistema como vía de escritura. Probar solo servicios propios y canales filtrados; falta de prueba de una clase IPC impide prometer aislamiento general. | Dos controles de pipe/captura y socket propio D064 delimitan casos; Mach/XPC, llavero y launch services no probados ni contactados. |
| Auth | Mantener HOME/USER y lectura del almacén existente sin copiar/enlazar secretos ni cambiar login. Save, reemplazo y metadatos globales denegados. Si exige auxiliares o keyring escritor, declarar incompatibilidad; no conceder una excepción silenciosa. | Lectura de auth ficticia; fuente efectiva y auxiliares reales sin acreditar. |
| Red/refresh | Separar tráfico de inferencia, herramientas, IPC y refresh. Antes de consumo, acreditar ausencia de rotación remota o exponer una decisión específica sobre sus efectos y continuidad de sesión. Un save denegado no cumple «sin refresh». | No resuelto; cero red externa y ningún refresh real en este diagnóstico. |
| Errores/versiones | Backend ausente o composición rechazada: cero objetivo/fallback. Solo una integración posterior definiría configuración explícita, hashes/versiones y cuarentena antes de efectos, independiente del núcleo. | No se implementan cli-8, local-config-3, migración o nuevos jobs. |

Las lecturas generales del perfil experimental tampoco protegen secretos
frente al propio objetivo. La candidata no es un aislamiento de confidencialidad
ni de recursos. Denegar `network*` en SBPL no certifica ausencia de toda
delegación; aquí no se abren conexiones externas ni se consultan servicios
Mach/XPC, llavero o launch services. No se certifican Linux/Windows, estabilidad
de sandbox-exec, daemonización o recuperación de procesos antiguos.

## Viabilidad y decisión de diseño pendiente

**Composición viable sintética, integración no viable con la evidencia actual.**
Las dos capas idénticas conservan las prohibiciones locales probadas, pero no
resuelven la carrera de aliases, IPC general, auth real ni refresh. Cerrar fd
es una medida necesaria y acotada; no convierte el conjunto en frontera segura.
No hay una variante calificada que satisfaga simultáneamente todos los criterios.
Esto no demuestra que sea imposible otra frontera o una capacidad upstream.

Antes de implementar, el siguiente alcance debe elegirse con el usuario:

1. Buscar una capacidad soportada de separación de estado/auth o una frontera
   externa compatible con las dos capas y exclusión efectiva de aliases/IPC.
   Exige evidencia nueva; no se presume disponible para el pin actual.
2. Mantener suspendida esa integración y el consumo pendiente con Codex.
3. Revisar explícitamente el modelo de aislamiento/auth/efectos admitidos.
   Una garantía cooperativa frente a terceros del mismo UID, otro almacén/cuenta
   o aceptar refresh remoto serían cambios materiales, **no decididos aquí**.

Ninguna opción autoriza escrituras globales como las de D061, copias de auth,
restauración de ajustes ni eliminación del sandbox interno. Una investigación
o prueba real nueva debe tener su propio alcance; esta entrega no la inicia.

## Verificaciones y aceptación

32 casos finales, 22 composiciones anidadas, doce rechazos de segunda capa;
errores esperados distinguidos de éxito y objetivos sin fallback. Sonda con
comprobaciones activas también bajo `python -O`; hashes/JSON, sintaxis Python,
enlaces locales y `git diff --check` comprobados. Regresión pertinente existente:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_cli_agents.py -k 'gate or cancel or timeout'
```

14 passed, 39 deselected. No suite completa, build, Node o QA visual: producto,
UI/API, dependencias y locks no cambian. Cero proveedores, credenciales reales,
configuración global, red externa, subagentes, publicación o push. Modelos,
permisos D024/D059, cli-7, local-config-2 y congelados conservados.
STATE/NEXT_STEPS/DECISIONS actualizados. No se avanza a la siguiente tarea,
matriz 3/4 o H6.2; D050/D055/D057/D060 siguen agotados.
