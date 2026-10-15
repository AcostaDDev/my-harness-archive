# Plan archivado — P003 Núcleo reusable y ejecución gestionada (antes H2)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 2 — Núcleo reusable y ejecución gestionada

#### H2.1 Extracción del motor

- Sustituir rutas globales por `ProjectContext`.
- Extraer planificación, evidencias, revisión, validación y aceptación en módulos.
- Mantener el comportamiento de sesiones nuevas y los límites de revisión.
- Trasladar dependencias Django/Docker a un perfil ReferenceProject.
- Criterio: pruebas de caracterización verifican las garantías anteriores en repositorios temporales.

#### H2.2 Persistencia, cola y exclusión

- Estados y eventos atómicos, jobs persistidos, idempotencia y bloqueo por checkout.
- Snapshot de contrato, políticas, prompts y versiones por intento.
- Criterio: doble clic y solicitudes concurrentes lanzan una sola ejecución; ningún lock se mantiene mediante una transacción larga.

#### H2.3 Adaptadores CLI

- Codex planificador/revisor; Claude ejecutor; captura incremental y cancelación de grupos de procesos.
- Pruebas con procesos falsos para timeout, salida inválida, error y falta de resultado final.
- Después, un smoke test real acotado en repositorio desechable con consumo autorizado.
- Criterio: un error conserva evidencias y detiene el run sin fallback ni reintento oculto.

#### H2.4 Git y aceptación

- Worktree por tarea, baseline y fingerprint de contenido, diff con staged y untracked.
- Commit limitado a lo revisado; recuperación de commit creado antes de guardar resultado.
- Criterio: una modificación externa después de review invalida la aceptación; el reinicio no duplica commits.

#### H2.5 Migración a gestionado

- Vista previa de importación, copia consistente y comprobación de modo exclusivo.
- Reglas de autoridad para documentos y base de datos.
- Criterio: motor legacy y nuevo no pueden gestionar simultáneamente el checkout; los históricos importados siguen accesibles.

**Salida del hito:** una tarea puede ejecutarse, revisarse y completarse desde la UI con recuperación verificable.

## Alcances conservados

### Siguiente tarea — H2.1 (pendiente)

_Origen: `docs/discovery/H2.1_SCOPE.md`._

H0 y H1 completados el 2026-10-11. [Alcance original de H1.3](../phase-002/NEXT_STEPS.md)
y [entrega/verificaciones](../phase-002/H1.3_OBSERVATION.md) conservados para revisión.
Esta entrega no inicia H2.1.

#### Objetivo

Extraer el motor reusable con `ProjectContext`, separando planificación, evidencias,
revisión, validación y aceptación de reglas específicas de proyectos. Conservar
sesiones nuevas y límites de revisión mediante caracterización offline.

#### Alcance de la siguiente sesión

1. Revisar H2.1 del backlog, arquitectura/invariantes de la especificación y
   D006/D009/D010/D012–D014. Consultar la referencia anterior solo en lectura.
2. Delimitar `ProjectContext` y las dependencias del motor antes de trasladar
   comportamiento; sustituir rutas globales y mantener el núcleo independiente
   de web, proveedores y stacks. Señalar contradicciones materiales antes de cambiar diseño.
3. Extraer módulos de planificación, evidencias, revisión, validación y aceptación,
   usando checkouts sintéticos y adaptadores falsos. Mantener sesiones nuevas,
   historial, límites de revisión, stop operativo y ausencia de fallback silencioso.
4. Trasladar reglas Django/Docker a un perfil ReferenceProject sin modificar el proyecto
   de referencia ni ejecutar su harness. No activar el motor desde la web ni
   introducir escritores sin la persistencia/exclusión futura de H2.2.
5. Añadir pruebas de caracterización offline en repositorios temporales,
   conservar H0/H1, ejecutar checks pertinentes, actualizar STATE/NEXT_STEPS
   y registrar decisiones duraderas.

#### Criterios de aceptación

- El motor extraído usa contexto explícito y módulos independientes del stack
  de proyecto; las reglas Django/Docker permanecen en un perfil.
- Pruebas offline caracterizan las garantías anteriores: sesiones nuevas,
  historial, límites de revisión y separación de revisión/validación/aceptación.
- H0.3 y observación H1.1–H1.3 siguen funcionando; contratos/checks/build pasan.
- No se presenta como ejecución gestionada una extracción aislada del motor.

#### Fuera de alcance

H2.2 cola/persistencia gestionada/bloqueo escritor, H2.3 adaptadores reales,
chat, permisos interactivos, SDKs y distribución. No ejecutar harness/agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global. No usar runs
reales; smoke con proveedores requiere autorización explícita de consumo posterior.

### Siguiente tarea — H2.2 (pendiente)

_Origen: `docs/discovery/H2.2_SCOPE.md`._

H0, H1 y H2.1 completados el 2026-10-11. [Alcance original de H2.1](NEXT_STEPS.md)
y [entrega/verificaciones](H2.1_ENGINE.md) conservados para revisión.
Esta entrega no inicia H2.2.

#### Objetivo

Añadir persistencia gestionada, cola local y exclusión por checkout al motor
extraído, con estados/eventos atómicos, jobs idempotentes y snapshots congelados
por intento. Mantener la autoridad de observación separada.

#### Alcance de la siguiente sesión

1. Revisar H2.2 del backlog, estados/persistencia/seguridad de la especificación
   y D003/D010/D012–D015. Delimitar entidades gestionadas y su autoridad antes
   de añadir migraciones; no convertir simulaciones o evidencia legacy en intentos.
2. Persistir runs/intentos, estados, resultados y eventos mediante transacciones
   cortas. Congelar contrato, contexto, políticas, prompts y versiones por intento;
   conservar los anteriores y el presupuesto de correcciones al recuperar.
3. Implementar jobs locales idempotentes y cola, con lease/heartbeat y exclusión
   por raíz canónica del checkout. No mantener una transacción SQLite abierta
   mientras un trabajo se ejecuta. Recuperar paradas/reinicios sin llamadas ocultas.
4. Comprobar concurrencia, claves repetidas y fallos entre transiciones con
   adaptadores falsos y repositorios/bases sintéticos. Un solo escritor por checkout;
   checkouts distintos pueden progresar según la política explícita de cola.
5. Mantener H0/H1/H2.1, ejecutar checks pertinentes, revisar diff, actualizar
   STATE/NEXT_STEPS y registrar decisiones duraderas. Documentar límites de la
   recuperación/exclusión sin presentar adaptadores falsos como ejecución real.

#### Criterios de aceptación

- Estados, resultados y eventos gestionados se guardan atómicamente; historial,
  snapshots y presupuesto persisten tras reiniciar.
- Doble solicitud y solicitudes concurrentes para el mismo trabajo lanzan una
  sola ejecución falsa; raíces equivalentes comparten el bloqueo escritor.
- Cola/lease/exclusión no dependen de transacciones largas; fallos y recuperación
  tienen semántica explícita y no duplican ejecuciones silenciosamente.
- Observación legacy y simulaciones conservan su autoridad/contratos; regresión,
  migraciones, checks de contratos y build pasan.

#### Fuera de alcance

H2.3 adaptadores CLI reales/smoke, H2.4 worktrees/captura Git completa/commit,
H2.5 migración de proyectos a gestionado, chat, permisos interactivos, SDKs,
cierre de fase y distribución. No ejecutar harness/agentes, tests/instalaciones
en ReferenceProject ni modificar configuración global. No usar runs reales; cualquier
smoke con proveedores requiere autorización explícita de consumo posterior.

### Siguiente tarea — H2.3 (pendiente)

_Origen: `docs/discovery/H2.3_SCOPE.md`._

H0, H1, H2.1 y H2.2 completados el 2026-10-11.
[Alcance original de H2.2](NEXT_STEPS.md) y
[entrega/verificaciones](H2.2_PERSISTENCE.md) conservados para revisión.
Esta entrega no inicia H2.3.

#### Objetivo

Añadir adaptadores CLI de Codex como planificador/revisor y Claude Code como
ejecutor, con sesiones nuevas, captura incremental y cancelación de grupos
de procesos. Conectar el flujo a las garantías persistidas H2.2 sin fallback
ni reintento oculto. Caracterizar primero con procesos falsos offline.

#### Alcance de la siguiente sesión

1. Revisar H2.3 del backlog, adaptadores/recuperación/seguridad de la especificación,
   D007–D009/D015–D016 y la matriz H0.2. Comprobar versión/help local de las CLI;
   no trasladar flags antiguos ni cambiar autenticación/configuración global.
2. Implementar adaptadores con argv/cwd/entorno/timeout explícitos, sesiones
   frescas, modelo/esfuerzo seleccionados y capacidades declaradas. Conservar
   solicitudes y metadatos observados separados; sin fallback ante fallos.
3. Capturar streams incrementales, bytes/eventos parciales y resultado terminal
   conocido/exit code. Probar timeout, UTF-8/JSON cortados, salida inválida,
   errores/cuota y ausencia de resultado final mediante procesos falsos.
4. Implementar cancelación y seguimiento de grupos de procesos. Conciliar
   propietario persistido con liveness antes de confirmar parada/liberar checkout;
   lease vencido por sí solo sigue sin demostrar muerte. No repetir efectos inciertos.
5. Mantener H0/H1/H2.1/H2.2, ejecutar checks offline pertinentes, revisar diff y
   actualizar STATE/NEXT_STEPS/DECISIONS con límites de CLI/autenticación/procesos.
6. Solo después de la caracterización offline, preparar un smoke real acotado en
   repositorio desechable. Solicitar autorización explícita de consumo antes de
   ejecutarlo; la autorización de implementación no autoriza proveedores reales.

#### Criterios de aceptación

- Adaptadores seleccionan explícitamente CLI/modelo/esfuerzo y sesión nueva;
  un error conserva evidencia y detiene el run sin fallback ni reintento oculto.
- Captura incremental y estados persistidos distinguen resultado parcial,
  completo, inválido, timeout y cancelación, sin éxito/telemetría inventados.
- Procesos falsos comprueban cancelación/grupos y recuperación conservadora:
  ningún segundo escritor arranca mientras el anterior pueda seguir vivo.
- Historial/snapshots/presupuesto/cola/exclusión H2.2 y contratos H0/H1 siguen
  pasando, con migraciones, checks de contratos y build pertinentes.
- El smoke real solo se ejecuta con autorización de consumo posterior; si falta,
  registrar expresamente esa verificación pendiente, sin presentar fakes como CLI real.

#### Fuera de alcance

H2.4 worktrees/captura Git completa/commit de producto, H2.5 migración de proyectos,
chat, SDKs, permisos interactivos vivos, cierre de fase y distribución.
No ejecutar el harness para desarrollar ni lanzar sesiones de otros agentes.
No usar runs reales, acceder a credenciales, ejecutar tests/instalaciones en
ReferenceProject ni modificar configuración global. No avanzar a H2.4.

### H2.3_SMOKE_RETRY_SCOPE

_Origen: `docs/discovery/H2.3_SMOKE_RETRY_SCOPE.md`._

Alcance conservado de `docs/NEXT_STEPS.md` en `c9cbd2f`, antes de la
verificación autorizada del 2026-10-12. No es la tarea activa actual.

### Siguiente acción — H2.3: nuevo smoke preparado, pendiente de autorización

La corrección de configuración Codex está implementada y verificada offline:
[entrega](H2.3_CONFIG_FIX.md), D019. Adaptador `cli-2`, 209 pruebas y
121 subtests correctos, 12 checks ligeros correctos. El smoke previo D018
conserva su [fallo y evidencias](H2.3_SMOKE.md); no se ha relanzado.
H2.4 no iniciado.

#### Objetivo pendiente

Verificar el transporte CLI real con la configuración corregida, sin presentar
los procesos sintéticos como proveedores reales. Codex conserva el proveedor
integrado OpenAI; sus retries internos se declaran `built-in-defaults/unknown`.
No se promete cero retries internos ni una sola inferencia por invocación CLI.

#### Propuesta concreta

- Codex 0.162.1: `gpt-6-luna`, esfuerzo `low`, planificador y revisor.
- Claude Code 2.1.295: `claude-sonnet-4-6`, esfuerzo `low`, ejecutor.
- Una ejecución de `scripts/smoke_cli.py`, hasta tres invocaciones CLI, timeout
  de 60 s por invocación, suscripciones propias y entorno sin API keys aportadas.
- Checkout Git nuevo bajo `/private/tmp`; SQLite y capturas en el área nueva,
  fuera de ese checkout y del desarrollo. No reutilizar el área del smoke fallido.
- Herramientas concedidas vacías; Codex read-only/approval never y Claude dontAsk.
  Sin cambios/commits/aceptación de tarea inferidos ni aislamiento total certificado.
- Detención al primer fallo, sin relanzar, fallback ni sustitución de selecciones.

#### Acción acotada

1. Revisar D019, script y propuesta. Confirmar la versión instalada por help/version
   y congelar `cli-2` con las selecciones antes de cualquier inferencia.
2. Solicitar autorización específica para esta nueva ejecución con sus límites.
   La D018 finalizó al primer error; instrucciones de corrección, tests, commit o
   continuación no autorizan por sí solas una nueva ejecución con proveedores.
3. Solo con autorización, ejecutar una vez:

   ```sh
   UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/smoke_cli.py --authorize-consumption --codex-model gpt-6-luna --codex-effort low --claude-model claude-sonnet-4-6 --claude-effort low --output-parent /private/tmp
   ```

   `--offline` limita uv, no la red/consumo de las CLI. No extraer credenciales.
4. Conservar evidencia/terminales/errores/telemetría y registrar lo no demostrado.
   Ante fallo, detenerse sin corregir y relanzar dentro de esta verificación.
5. Actualizar STATE/NEXT_STEPS/DECISIONS. Sin autorización mantenerla pendiente;
   no interpretar fakes/preflight/catálogos locales como éxito real.

#### Criterios de aceptación

- Consentimiento específico y selecciones congeladas antes de consumo.
- Máximo tres invocaciones con timeout, cero fallback/reintento del adaptador;
  límite explícito de retries internos desconocidos.
- Evidencias independientes, datos sintéticos, resultado real separado del offline.
- Parada al primer error sin llamadas posteriores; ausencia/null/cero conservados.
- No certificar aceptación/commit de producto ni avanzar a H2.4.

#### Fuera de alcance

Correcciones adicionales del adaptador tras fallo, H2.4 captura Git/worktrees/commit
de producto, H2.5 migración gestionada, entradas API/CLI/UI, permisos vivos, chat,
SDKs y distribución. No ejecutar el harness para desarrollar, lanzar agentes de
colaboración automáticamente, usar datos de proyectos del usuario, extraer
credenciales, modificar configuración global ni acceder a ReferenceProject.

### Siguiente tarea — H2.3: corregir configuración MCP de Claude offline

_Origen: `docs/discovery/H2.3_MCP_FIX_SCOPE.md`._

El nuevo smoke autorizado con `cli-2` terminó el 2026-10-12: Codex planificador
COMPLETE (exit 0, terminal y uso reportado); Claude FAILED (exit 1) por
configuración MCP inválida. Revisor no lanzado, sin fallback ni relanzamiento.
[Resultado y evidencias](H2.3_SMOKE_RETRY.md), D020. El primer
[smoke D018](H2.3_SMOKE.md) queda separado e intacto.
209 pruebas y 121 subtests, 12 checks ligeros correctos. H2.4 no iniciado.

#### Objetivo

Corregir exclusivamente el argumento MCP vacío de Claude Code 2.1.295 sin
activar servidores/configuración del usuario, manteniendo herramientas vacías,
sesiones nuevas, selección explícita y denegación dontAsk. La spec real conserva
`--strict-mcp-config --mcp-config '{}'`; la CLI exige el campo `mcpServers`.
Comprobar el formato válido con help/documentación o validación local sin
inferencia. No presentar preflight/fakes como éxito real del proveedor.

#### Alcance acotado

1. Leer D020 y el informe real. Conservar sus evidencias y resultados anteriores.
2. Confirmar el contrato de `--mcp-config` para la versión fijada y sustituir el
   argumento inválido por una configuración explícita de cero servidores.
   No eliminar el modo estricto ni heredar fuentes de configuración del usuario.
3. Añadir una regresión sintética que rechace el formato observado antes de
   simular inferencia, independientemente del código del adaptador. Caracterizar
   que versión/help pueden pasar aunque el argumento sea inválido.
4. Verificar argv corregido, herramientas vacías, prompts/hooks/configuración
   aislados, captura de fallo y parada sin revisor ni llamadas adicionales.
5. Versionar el cambio del adaptador/configuración; jobs congelados `cli-2` no
   deben ejecutar silenciosamente un argv diferente. Preservar historial previo.
6. Ejecutar checks offline pertinentes, revisar diff, actualizar STATE/NEXT_STEPS/
   DECISIONS y preparar la siguiente propuesta real sin ejecutarla.

#### Criterios de aceptación

- Configuración MCP vacía válida para Claude 2.1.295, sin servidores heredados.
- Regresión independiente reproduce el rechazo antiguo y permite el argv
  corregido; preflight no se presenta como validación semántica completa.
- Herramientas/autenticación/selecciones/permisos y demás garantías H2.3
  conservados; ausencia/null/cero y resultados anteriores preservados.
- Versiones congeladas impiden sustitución silenciosa del comportamiento.
- Checks offline pasan, evidencia real separada y límites pendientes explícitos.
- Ninguna nueva inferencia, fallback, relanzamiento ni avance a H2.4.

#### Fuera de alcance

La autorización D020 concluyó al primer fallo. Corrección, tests, commit o
continuación no autorizan otro smoke: requerirá propuesta y consentimiento
específicos. No consumir proveedores, extraer credenciales, alterar configuración
global, activar SDK/MCP/herramientas ni lanzar agentes de colaboración.
H2.4 Git/worktrees/commit de producto, H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat y distribución quedan fuera de esta tarea.

### Siguiente tarea — H2.3: propuesta de nuevo smoke real con cli-3

_Origen: `docs/discovery/H2.3_SMOKE_CLI3_SCOPE.md`._

Corrección MCP offline completada el 2026-10-12 como `cli-3`: configuración
Claude explícita `{"mcpServers":{}}` con modo estricto, sin servidores ni
herramientas heredados por esas opciones. Jobs congelados `cli-2`/`cli-1`
bloqueados antes de efectos; historial anterior conservado. D021,
[entrega y límites](H2.3_MCP_FIX.md),
[alcance completado](NEXT_STEPS.md).
211 pruebas y 121 subtests, 12 checks ligeros correctos. H2.4 no iniciado.

Preflight de esta propuesta comprobado el 2026-10-12 sobre `725e65f`:
ambas versiones/help compatibles, argv `cli-3` revisado, 211 pruebas/121 subtests
y 12 checks ligeros correctos. Informe y comando exacto (archivo `docs/discovery/H2.3_SMOKE_CLI3_PREFLIGHT.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/H2.3_SMOKE_CLI3_PREFLIGHT.md`).
Preparación offline terminada; ejecución real y sus criterios de evidencia
siguen pendientes del consentimiento específico. La tarea activa se conserva.

#### Propuesta concreta pendiente de consentimiento

Una ejecución nueva de `scripts/smoke_cli.py`, hasta tres invocaciones de 60 s
cada una, en un checkout sintético nuevo bajo `/private/tmp`, con SQLite y
artefactos externos. No reanudar D018/D020 ni reutilizar sus jobs/configuraciones.

| Rol | CLI fijada | Modelo solicitado | Esfuerzo |
|---|---|---|---|
| Planificador | Codex 0.162.1 | `gpt-6-luna` | `low` |
| Ejecutor | Claude Code 2.1.295 | `claude-sonnet-4-6` | `low` |
| Revisor | Codex 0.162.1 | `gpt-6-luna` | `low` |

Adaptador `cli-3`, selección/configuración congeladas antes de lanzar.
Codex read-only/approval never; Claude dontAsk/prompts none, tools/allowedTools
vacíos, MCP vacío/estricto, fuentes de settings vacías y hooks desactivados.
Sesiones nuevas; entorno explícito `HOME`, `PATH`, `TMPDIR`, `LANG`, sin API keys
ni extracción de credenciales. Suscripciones/auth propias de las CLI.
Red e inferencia pueden consumir cuota; `uv --offline` solo limita uv.
Retries internos de ambas CLI siguen desconocidos, sin garantía de una única
inferencia por invocación. No se certifica aislamiento total con estos flags.

Parar al primer error, timeout, salida inválida/parcial o ausencia de terminal:
preservar bytes, eventos, spec y resultados; no ejecutar roles restantes,
cambiar selecciones/proveedores ni relanzar. La autorización D020 concluyó con
su fallo; esta propuesta, la corrección offline y su commit no autorizan consumo.

#### Orden de trabajo tras autorización específica

1. Revisar Git, D021, informe de corrección y script. Confirmar versión/help
   locales y selecciones exactas; incompatibilidad bloquea sin consumo.
   Preflight no certifica semántica completa de argumentos ni acceso/auth/cuota.
2. Ejecutar una sola vez el script con guardia de consumo, selecciones de la
   tabla y output nuevo. No usar el harness para desarrollar ni lanzar agentes
   de colaboración. Si no hay autorización específica, no ejecutar este paso.
3. Comprobar terminal/exit code, JSON, captura/hash/rangos y persistencia para
   cada rol efectivamente lanzado; separar selección solicitada de metadatos
   reportados y ausencia/null/cero. No inferir aceptación de tarea del transporte.
4. Al fallar, conservar RECOVERY_REQUIRED/lock y comprobar propietario cerrado
   y liveness conservadora de grupos, sin recuperación automática. No corregir
   ni relanzar dentro de esta tarea; documentar el diagnóstico y próxima tarea.
5. Revisar diff, actualizar STATE/NEXT_STEPS/DECISIONS e informe independiente
   con hashes/procedencia/límites; no copiar evidencia privada a fixtures.

#### Criterios de aceptación

- Evidencia de las CLI/argv/selecciones congeladas `cli-3`, MCP explícitamente
  vacío, permisos conservados, checkout sintético intacto y artefactos externos.
- Rama de éxito: tres transportes completos con terminal/exit 0/JSON y
  resultados persistidos; sin afirmar aceptación/commit de producto.
- Rama de error: parada al primer fallo con evidencia exacta y resultados
  persistidos, roles restantes no lanzados y ninguna llamada adicional/fallback.
- Datos observados y ausentes diferenciados; no deducir factura/cuota o retries
  efectivos a partir de telemetría incompleta.
- Historial D018/D020 separado; no corrección, relanzamiento ni avance a H2.4.

#### Fuera de alcance

Consumo sin consentimiento específico, cambios globales/auth, SDK/MCP/herramientas
activos, producto Git/worktrees/commit H2.4, H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat, distribución, publicación y push.

### Siguiente tarea — H2.3: diagnóstico de autenticación Claude en lectura

_Origen: `docs/discovery/H2.3_AUTH_DIAGNOSIS_SCOPE.md`._

Alcance conservado de `docs/NEXT_STEPS.md` en `0386629`; enlaces relativos
ajustados a esta carpeta. Tarea completada en [informe](H2.3_AUTH_DIAGNOSIS.md).

Smoke `cli-3` autorizado y ejecutado el 2026-10-12 sobre `039a01e`: Codex
planificador COMPLETE (exit 0, terminal/JSON); Claude FAILED (exit 1, terminal
de error) por `authentication_failed` y «Not logged in · Please run /login».
MCP vacío aceptado; herramientas y servidores vacíos observados. Revisor no
lanzado, sin corrección, login ni relanzamiento. D022,
[resultado y evidencias](H2.3_SMOKE_CLI3.md),
[alcance completado](NEXT_STEPS.md).
211 pruebas/121 subtests y 12 checks ligeros correctos en preparación;
persistencia, 31 eventos/hashes/rangos, grupos muertos y checkout intacto
comprobados después. H2.4 no iniciado.

#### Objetivo

Determinar por qué Claude Code 2.1.295 no dispone de autenticación en el entorno
explícito del smoke, conservando las suscripciones/auth propias de las CLI.
El fallo acredita este contexto, no ausencia de login en todo el Mac. Separar
diagnóstico observado, hipótesis y causa comprobada. No extraer credenciales ni
usar inferencia para probar autenticación.

#### Alcance acotado

1. Revisar D008/D017/D022, informe y spec del smoke. Conservar resultados,
   capturas y bloqueo anteriores sin reanudar ni recuperar automáticamente.
2. Consultar help/documentación oficial y mecanismos locales de estado de auth
   en lectura, sin ejecutar print/agentes/modelos. Filtrar la salida en memoria:
   solo estado/método de auth y diagnósticos necesarios, sin correo, IDs de cuenta,
   tokens, cookies, contenido de almacenes de credenciales ni dumps del entorno.
3. Comparar el contexto explícito `HOME`, `PATH`, `TMPDIR`, `LANG`, ejecutable,
   fuentes de settings aisladas y restricciones del proceso con la sesión propia
   del usuario. Inspeccionar solo metadatos/configuración no secreta pertinentes;
   no ampliar el entorno ni heredar variables de credenciales automáticamente.
4. Si el diagnóstico exige login o intervención del usuario, documentar el
   paso concreto para su sesión sin hacerlo automáticamente. Si revela un cambio
   necesario del adaptador, proponer una tarea offline separada con regresión y
   versión congelada; no mezclar esa implementación con el diagnóstico.
5. Actualizar STATE/NEXT_STEPS/DECISIONS e informe con evidencia saneada y límites.
   No ejecutar otro smoke ni iniciar H2.4.

#### Criterios de aceptación

- Diagnóstico en lectura reproducible y limitado al contexto observado, o
  incertidumbre pendiente explícita con la comprobación/intervención necesaria.
- Estado de auth observado separado de acceso al modelo, inferencia y cuota;
  no deducirlos de help/status o de los ceros reportados en el fallo.
- Sin extracción/exposición de secretos ni modificación global/login automática.
- Modelo/proveedor/suscripción, aislamiento de herramientas/MCP y configuración
  congelada conservados; no sustitución por API keys ni ampliación silenciosa.
- Resultados/capturas de D018/D020/D022 y lock anterior preservados;
  documentación/checks proporcionales revisados, sin nuevas invocaciones de agente.

#### Fuera de alcance

La autorización D022 terminó al primer fallo. Otro smoke requiere propuesta
y consentimiento específicos; este diagnóstico o su commit no autorizan consumo.
Sin login/logout/refresh, lectura de secretos/keychain, fallback, relanzamiento,
corrección del adaptador, SDK/MCP/herramientas activos, cambios globales,
H2.4/H2.5, entradas gestionadas API/CLI/UI, permisos vivos, chat, publicación o push.

### Siguiente tarea — H2.3: corrección offline del entorno explícito del smoke

_Origen: `docs/discovery/H2.3_ENV_FIX_SCOPE.md`._

Diagnóstico de autenticación Claude completado en lectura el 2026-10-12,
D023. Fuera del sandbox, Claude Code 2.1.295 reconoce sesión `claude.ai` con
USER presente; el entorno mínimo HOME/PATH/TMPDIR/LANG no la reconoce.
Añadir solo USER la restaura, retirarlo del entorno de la sesión la impide;
LOGNAME no basta. Sin login, inferencia ni corrección. Status no admite los
flags de fuentes aisladas; transporte completo sigue pendiente.
[Informe y reproducción](H2.3_AUTH_DIAGNOSIS.md),
[alcance completado](NEXT_STEPS.md).
Doce checks ligeros correctos; D020/D022 conservan capturas/hash, resultados,
24/31 eventos y locks. D018 ya ausente según informes anteriores. H2.4 no iniciado.

#### Objetivo

Corregir offline la construcción del entorno explícito del smoke para que
Claude reciba USER correspondiente al usuario local, conservando autenticación
propia de las CLI, fuentes/tools/MCP aislados y configuración congelada.
No modificar el adaptador para heredar automáticamente el entorno del supervisor.

#### Alcance acotado

1. Revisar D008/D017/D022/D023, script del smoke y contrato de CLIConfig.
   Conservar resultados/specs/historial/locks anteriores sin recuperación.
2. Incluir USER explícito y comprobado contra el usuario local en la construcción
   del entorno del smoke; resolver ausencia/discrepancia antes de consumo con
   diagnóstico concreto. No copiar variables de credenciales ni ampliar fuentes.
3. Añadir regresión offline independiente con proceso sintético que distinga
   USER ausente/presente, pruebe entorno completo sin herencia silenciosa y
   conservación de HOME/PATH/TMPDIR/LANG y permisos/selecciones existentes.
   No usar status real ni inferencia como test automatizado.
4. Congelar la configuración nueva con hash distinto. Probar que un job con
   configuración anterior no se ejecuta silenciosamente con la nueva, sin
   reescribir historia/resultados. Si cambia el comportamiento del adaptador,
   elevar su versión; no versionarlo por mera edición documental.
5. Ejecutar checks offline pertinentes y actualizar STATE/NEXT_STEPS/DECISIONS
   e informe. Preparar por separado una propuesta de verificación real con
   sus límites, sin ejecutar otro smoke dentro de esta corrección.

#### Criterios de aceptación

- USER válido transmitido explícitamente y sin credenciales heredadas; ausencia
  o discrepancia resuelta antes de cualquier llamada a proveedor.
- Regresión sintética demuestra el defecto previo y el comportamiento corregido,
  sin requerir sesión real, secretos ni red.
- Configuración/hash nuevos congelados y selección de modelos/esfuerzos conservada;
  jobs antiguos bloqueados ante incompatibilidad, sin sustituir specs/resultados.
- Fuentes/settings/hooks, herramientas/MCP vacíos, sesiones frescas y ausencia
  de fallback/reinvocación automática conservados.
- Evidencias disponibles D020/D022 y lock anterior preservados; históricos
  documentales D018/D020/D022 intactos, sin reconstruir el área D018 ausente.
- Checks/diff/documentación revisados; no presentar pruebas offline o status
  como éxito real completo ni como prueba de acceso al modelo, inferencia o cuota.

#### Fuera de alcance

La autorización D022 terminó al fallo. Diagnóstico D023 y su commit no autorizan
consumo. Sin otro smoke, login/logout/refresh, lectura de secretos/keychain,
API keys, cambios globales, fallback, recuperación/liberación automática,
SDK/MCP/herramientas activos, H2.4/H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat, publicación o push.

### Siguiente tarea — H2.3: verificar transporte real con USER comprobado

_Origen: `docs/discovery/H2.3_ENV_SMOKE_SCOPE.md`._

Corrección offline del entorno completada el 2026-10-12 (D024): USER explícito
validado contra el UID local antes de efectos, HOME/PATH/TMPDIR/LANG conservados,
sin credenciales heredadas. Adaptador `cli-3` conservado; hash de CLIConfig
nuevo bloquea jobs/configuraciones anteriores sin reescritura.
[Informe](H2.3_ENV_FIX.md), [alcance completado](NEXT_STEPS.md).
219 pruebas y 121 subtests, 12 checks ligeros correctos; regresión independiente
reproduce el defecto previo y el recorrido sintético corregido.
D020/D022 conservan doce capturas/prompts, SQLite, 24/31 eventos y locks;
D018 sigue ausente. El transporte real completo continúa pendiente. H2.4 no iniciado.

#### Objetivo y consentimiento pendiente

Verificar una vez el transporte de las tres CLI en checkout desechable con el
entorno corregido. Propuesta concreta separada (archivo `docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md`):
Codex 0.162.1 `gpt-6-luna`/`low` para planificador/revisor y Claude 2.1.295
`claude-sonnet-4-6`/`low` para ejecutor; hasta tres invocaciones, 60 s cada una,
red/suscripciones propias y parada al primer fallo, sin fallback ni relanzamiento.
Retries internos desconocidos y posible consumo aunque falle.

**No ejecutado ni autorizado en la corrección offline.** D022 agotó su
consentimiento al fallo; diagnóstico D023, corrección D024 y commit no permiten
inferencias nuevas. Antes de lanzar, presentar esta propuesta y obtener
consentimiento específico. Si no llega, dejar esta tarea pendiente sin consumo.

#### Alcance acotado

1. Revisar D008/D017/D022/D023/D024, informes, script y propuesta; conservar
   históricos, evidencias y locks previos sin recuperación/liberación.
2. Antes del consumo, comprobar USER local y entorno explícito, ayuda/guardia
   del smoke y preflight versión/help. No extraer auth ni usar status o fakes
   como certificado de inferencia; repetir tests solo si cambia código/contexto
   o aparece una incertidumbre que lo justifique.
3. Obtener consentimiento específico para la propuesta. Ejecutar solo una vez
   el comando documentado, fuera del sandbox para auth propia de las CLI,
   con nuevo checkout/SQLite/artefactos bajo `/private/tmp`. Configuración y
   selección congeladas antes de consumo; no reutilizar jobs D020/D022.
4. Conservar specs/hash de entorno/prompt, stdout/stderr, terminales, selección,
   metadatos y eventos. Detener al primer resultado distinto de complete;
   sin login, corrección ni invocación adicional dentro de esta tarea.
5. Reabrir SQLite en lectura y verificar hashes/rangos/capturas/prompts,
   resultados/estados, owner/grupos y checkout intacto. Registrar datos ausentes,
   null y ceros sin inferir cuota/factura o esfuerzo efectivo.
6. Actualizar STATE/NEXT_STEPS/DECISIONS e informe según rama de éxito/error,
   sin avanzar a H2.4. Un fallo concluye esta verificación con resultado fallido
   y requiere una tarea separada, no una reparación o reejecución automática.

#### Criterios de aceptación

- Consentimiento específico previo y una única ejecución con los límites fijados.
- USER validado y entorno/settings/hooks/tools/MCP explícitos, sesiones nuevas,
  modelos/esfuerzos congelados; sin credenciales heredadas ni fallback.
- Éxito: tres resultados complete, terminales, exit 0 y JSON conservados;
  certificar únicamente el transporte observado, sin aceptación/commit de tarea.
- Error: resultados/evidencias preservados, roles restantes no lanzados,
  run/job RECOVERY_REQUIRED, owner cerrado y lock retenido; sin recuperar.
- Persistencia/hashes/eventos revisados; checkout sintético intacto y ausencia
  de herramientas en los eventos capturados. D020/D022 e informes intactos.
- Evidencia real separada de tests offline; no certificar retries internos,
  cuota/factura, aislamiento físico ni cancelación/timeout reales no observados.

#### Fuera de alcance

Sin login/logout/refresh, lectura de secretos/keychain, API keys, cambios
globales, ampliación de fuentes/tools/MCP, corrección de código en la rama
de error, fallback, reintento, recuperación/liberación automática, SDK,
entradas gestionadas API/CLI/UI, permisos vivos, chat, H2.4/H2.5,
publicación o push. No reconstruir el área D018 ausente.

### Siguiente tarea — H2.4: Git y aceptación offline

_Origen: `docs/discovery/H2.4_SCOPE.md`._

H2.3 verificado offline y smoke real completo el 2026-10-12 (D025), autorizado
por «Procede con el smoke»: planificador Codex, ejecutor Claude y revisor Codex
COMPLETE, terminal/exit 0/JSON `smoke-ok`, con USER validado. Sin herramientas
ni cambios de checkout. [Informe](H2.3_ENV_SMOKE.md),
[alcance completado](NEXT_STEPS.md).
57 eventos, configuración/capturas/hashes exactos tras reabrir SQLite, job DONE,
run STOPPED por fin deliberado del smoke, owner cerrado y procesos STOPPED/dead;
lock nuevo liberado por finalización normal. D020/D022 y sus locks intactos.
Doce checks ligeros correctos; suite previa del mismo código: 219 pruebas y
121 subtests. Transporte real acreditado, sin aceptación/commit de tarea real.

**H2.4 no iniciado.** La autorización del smoke se satisfizo con una ejecución;
no permite otro consumo, login o recuperación de históricos.

#### Objetivo

Implementar Git y aceptación según el backlog H2.4 y la especificación:
worktree por tarea, baseline/fingerprint del contenido completo y commit
limitado a lo validado/revisado, con recuperación idempotente tras caída.
Trabajo local offline con repositorios temporales sintéticos, sin proveedores.

#### Alcance acotado

1. Revisar especificación (consistencia frente a caídas y Git), backlog H2.4,
   D015–D017/D025 y puertos del motor, aceptación, journal y persistencia.
   Señalar contradicciones materiales antes de cambiar diseño.
2. Implementar captura Git real: base SHA, contenido/diff completo, staged,
   unstaged, untracked y borrados relevantes. Vincular validación/review al
   contenido exacto; no certificar Git mediante SyntheticWorkspace.
3. Preparar worktree por tarea y conservarlo durante revisiones; preservar
   cambios ajenos y mantener la exclusión de escritor. Integrar en la rama de
   destino sigue siendo una acción separada, fuera de esta entrega.
4. Crear commit solo del conjunto revisado/autorizado y actualizaciones
   mecánicas identificadas. Persistir intención/evidencia antes del efecto y
   resultado después; conciliar commit creado antes de guardar resultado sin
   repetirlo tras reinicio ni aceptar contenido modificado externamente.
5. Añadir regresión offline con Git/SQLite y agentes falsos: invalidación tras
   modificación externa, staged/untracked, límites del commit, preservación de
   cambios ajenos y caída antes/después de crear commit. No usar runs privados.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

#### Criterios de aceptación

- Una modificación externa posterior a validación/review invalida aceptación;
  no se crea un commit de contenido distinto del revisado.
- Fingerprint/diff incluye archivos nuevos, staged y cambios pertinentes;
  baseline y evidencia conservados con procedencia y hash.
- Worktree aislado por tarea y conservado durante revisiones, sin limpiar
  modificaciones desconocidas ni tratarlo como sandbox de seguridad.
- Commit acotado a lo revisado; una caída después del efecto Git y antes del
  resultado SQLite se recupera sin duplicar commits ni reescribir historial.
- Tests offline pertinentes pasan y contratos/versiones/migraciones necesarios
  documentados; no presentar diseño como implementación.

#### Fuera de alcance

Sin proveedores reales ni otro smoke, login/refresh, secretos, recuperación de
D020/D022, integración automática en rama destino, push/publicación, H2.5,
entradas gestionadas API/CLI/UI, permisos vivos, SDK, chat o distribución.
No modificar ReferenceProject, configuración global ni lanzar agentes de colaboración.

### Siguiente tarea — H2.5: migración a modo gestionado

_Origen: `docs/discovery/H2.5_SCOPE.md`._

H2.4 completado y verificado offline el 2026-10-12 (D026): captura Git completa
vinculada a árboles, worktree por tarea y commit determinista conciliable tras
caídas, con intención/resultado en `managed_commits` (`0006_git_commits`).
[Informe](H2.4_GIT.md), [alcance completado](NEXT_STEPS.md).
253 pruebas y 121 subtests, 12 checks ligeros correctos. Sin proveedores, smoke
nuevo ni commits de producto reales.

**H2.5 no iniciado.** Los consentimientos de smokes anteriores están agotados;
esta tarea es offline y no autoriza proveedores, login ni recuperación de D020/D022.

#### Objetivo

Implementar la migración controlada de un checkout legacy a modo gestionado según
el backlog H2.5 y la especificación: vista previa de importación, copia consistente
y comprobación de modo exclusivo, con reglas de autoridad para documentos y base
de datos. Trabajo local con checkouts y SQLite sintéticos.

#### Alcance acotado

1. Revisar especificación (autoridad de datos, migración controlada), backlog H2.5,
   D012–D016/D026 y el estado legacy observado (H1). Señalar contradicciones
   materiales antes de cambiar diseño; definir qué dato pasa a ser autoridad de
   SQLite y cuáles siguen como documentos de lectura.
2. Vista previa de importación sin escribir: qué runs/tareas/fases se activarían,
   qué quedaría como histórico de solo lectura y qué ausencias/incertidumbres
   existen. Reutilizar el índice H1.1 sin crear intentos inferidos.
3. Copia consistente: capturar el estado legacy con identidad/hash de cada fuente y
   detectar cambios durante la copia; sin modificar el origen ni la base legacy.
4. Comprobación de modo exclusivo: el motor legacy y el gestionado no pueden operar
   a la vez sobre el mismo checkout (incluyendo raíces canónicas/alias y worktrees
   derivados). Reglas explícitas y persistidas; un fallo no activa nada.
5. Regresión offline con Git/SQLite sintéticos: activación atómica y reanudable,
   históricos importados accesibles, rechazo ante escritor legacy/gestionado
   concurrente, reinicio y fallos inyectados. No usar runs privados.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

#### Criterios de aceptación

- Motor legacy y gestionado no pueden gestionar simultáneamente el mismo checkout;
  el intento de hacerlo falla con diagnóstico y sin efectos parciales.
- La vista previa no escribe; la activación es atómica, idempotente y conserva
  autoridad/procedencia de cada dato importado sin duplicarla.
- Los históricos importados siguen accesibles tras activar; ausencias, null y cero
  se distinguen como en H1.
- Tests offline pertinentes pasan y contratos/versiones/migraciones necesarios
  documentados; no presentar diseño como implementación.

#### Fuera de alcance

Sin proveedores reales ni otro smoke, login/refresh, secretos, recuperación de
D020/D022, integración automática en rama destino, push/publicación, H3,
entradas gestionadas API/CLI/UI, permisos vivos, SDK, chat o distribución.
No modificar ReferenceProject, configuración global ni lanzar agentes de colaboración.

#### Decisiones del usuario antes de implementar (2026-10-12)

Contradicción señalada antes de cambiar el diseño: la especificación pide
deshabilitar el arranque del motor legacy, el alcance pide no modificar el origen
y el motor legacy (solo lectura) no tiene lock ni lee nada nuestro. Respuestas:

1. Se acepta un marcador de modo gestionado escrito en el checkout.
2. La asignación de autoridad SQLite/documentos se deja al criterio de la entrega.
3. La reversión (exportar y comprobar) queda dentro de esta entrega.

### Siguiente tarea — Salida del hito 2, parte 1: API gestionada local

_Origen: `docs/discovery/H2_EXIT_API_SCOPE.md`._

H2.5 completado y verificado offline el 2026-10-12 (D027): vista previa sin
escrituras, copia consistente con manifiesto, activación atómica y reanudable,
exclusión legacy/gestionado por marcador y deriva, y reversión verificada.
Migración `0007_managed_activation`. [Informe](H2.5_MIGRATION.md),
[alcance completado](NEXT_STEPS.md). 288 pruebas y 121 subtests, 12
checks ligeros correctos. Sin proveedores ni smoke nuevo.

**No iniciada.** El backlog no numera esta tarea: la salida del hito 2 exige que
«una tarea pueda ejecutarse, revisarse y completarse desde la UI con recuperación
verificable», y hoy motor, supervisor, commit y migración solo tienen entradas de
biblioteca. Se propone dividirla en API (esta tarea) y UI (la siguiente).
Los consentimientos de smokes anteriores están agotados; esta tarea es offline.

#### Objetivo

Exponer por HTTP local (loopback) las operaciones gestionadas existentes, con
contratos Pydantic como fuente de OpenAPI y tipos generados, sin lógica nueva de
motor: el servicio delega en `SQLiteManagedRepository`, `LocalSupervisor` y
`MigrationService`, y conserva sus garantías (idempotencia, versiones esperadas,
exclusión, recuperación explícita).

#### Alcance acotado

1. Revisar especificación (API, supervisor local, seguridad local), D010/D011,
   D016/D017, D026 y D027. Señalar contradicciones materiales antes de cambiar diseño.
2. Decidir y documentar cómo se ejecutan los jobs desde el servicio: supervisor
   opt-in en el proceso Uvicorn (como la observación H1.3) o acción explícita
   «ejecutar siguiente job». Sin autoarranque implícito ni proveedores por defecto.
3. Endpoints de migración: vista previa, activar, reanudar/abandonar, revertir y
   estado de un checkout. Endpoints gestionados: encolar tarea, listar runs/jobs/
   intentos/eventos paginados, revalidar/reintentar, encolar commit y confirmar
   escritor detenido. Claves de idempotencia y versiones esperadas obligatorias;
   409 con diagnóstico ante conflicto o rechazo de modo.
4. Puertos por configuración explícita: fakes en pruebas; adaptadores CLI H2.3 y
   Git H2.4 solo si se configuran expresamente, sin invocarlos en esta entrega.
5. Regresión offline con TestClient, SQLite/Git sintéticos y fakes: recorrido
   completo hasta COMMITTED, rechazos de modo, doble envío, reinicio y
   recuperación. OpenAPI y tipos regenerados; TypeScript y build correctos.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

#### Criterios de aceptación

- Un recorrido HTTP con fakes encola, ejecuta, revisa y deja COMMITTED una tarea,
  con eventos consultables y sin duplicados ante doble envío o reinicio.
- Los rechazos de modo (legacy no activado, deriva, marcador) y los conflictos de
  versión se devuelven con diagnóstico, sin efectos parciales.
- Migración por HTTP con las mismas garantías que la biblioteca (vista previa sin
  escrituras, activación reanudable, reversión verificada).
- Ningún endpoint invoca proveedores por defecto; tests offline pertinentes pasan
  y contratos/versiones documentados; no presentar diseño como implementación.

#### Fuera de alcance

UI gestionada (parte 2), proveedores reales u otro smoke, login/refresh, secretos,
recuperación de D020/D022, integración en rama destino, push/publicación, H3
(prompts versionados, permisos, fases), SDK, chat o distribución. No modificar
ReferenceProject, configuración global ni lanzar agentes de colaboración.

### Alcance original — Salida del hito 2, parte 2: UI gestionada local

_Origen: `docs/discovery/H2_EXIT_UI_SCOPE.md`._

Conservado de NEXT_STEPS antes de implementar. Entrega: [H2_EXIT_UI.md](H2_EXIT_UI.md).

Parte 1 completada y verificada offline el 2026-10-12 (D028): API `/api/managed`
con proyectos registrados en el servidor, supervisor opt-in en el proceso Uvicorn,
`Idempotency-Key`/`expected_version`, 409 con diagnóstico y guardia Host/Origin/CSRF.
[Informe](H2_EXIT_API.md), [alcance completado](NEXT_STEPS.md).
306 pruebas y 121 subtests, 12 checks ligeros correctos. Sin proveedores ni smoke.

**No iniciada.** Cierra la salida del hito 2: «una tarea puede ejecutarse,
revisarse y completarse desde la UI con recuperación verificable». Esta tarea es
offline; los consentimientos de smokes anteriores están agotados.

#### Objetivo

UI React que consuma solo los tipos generados de `/api/managed` para:

- consultar el modo del proyecto y migrarlo;
- encolar una tarea;
- seguir su ejecución;
- revisar el resultado;
- confirmar el commit;
- recuperar un job en cuarentena.

Todo ello sin lógica de motor en el cliente.

#### Alcance acotado

1. Revisar D011, D013/D014, D027, D028 y la §12 de la especificación (experiencia
   de usuario). Señalar contradicciones materiales antes de cambiar diseño.
2. Seguridad del cliente:
   - enviar `X-Harness-Local: 1` en las mutaciones gestionadas;
   - decidir y documentar si la guardia Host/Origin/CSRF se extiende a las
     mutaciones H0/H1 (simulación y observación);
   - decidir si la sesión local se implementa ahora o queda explícitamente
     pendiente.
3. Pantallas:
   - proyectos registrados, modo y estado del supervisor;
   - vista previa, activación y reversión con confirmaciones explícitas;
   - encolar tarea con clave de idempotencia generada en el cliente y conservada
     ante reintentos de red;
   - run con historial, intentos, aceptación y commit;
   - eventos paginados por cursor, con sondeo o SSE (decidir; si se añade SSE
     gestionado, solo filas confirmadas, con id creciente y reconexión);
   - acciones revalidar, reintentar, commit y confirmar escritor detenido, con
     `expected_version` de la pantalla y recarga ante 409.
4. Configuración local de desarrollo para probar la UI con puertos falsos, mediante
   un módulo de ejemplo para `HARNESS_MANAGED_CONFIG` con datos sintéticos, sin
   proveedores. Documentar cómo se configurarían los adaptadores CLI H2.3 y Git H2.4
   sin activarlos.
5. Regresión offline: pruebas API existentes, TypeScript y build. Recorrido en
   navegador sobre la UI compilada con SQLite/Git sintéticos y fakes:
   - encolar y ver ACCEPTANCE_READY;
   - commit hasta COMMITTED;
   - doble clic sin duplicados;
   - reinicio del servicio con la página abierta;
   - cuarentena, confirmación y revalidación.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE, NEXT_STEPS,
   DECISIONS e informe.

#### Criterios de aceptación

- Desde la UI, una tarea con fakes recorre ejecución, revisión y COMMITTED con
  eventos visibles y sin duplicados ante doble envío o reinicio.
- La recuperación de un job en RECOVERY_REQUIRED se completa desde la UI con
  confirmación explícita y sin repetir efectos.
- Los rechazos de modo y los conflictos de versión se muestran con su diagnóstico,
  sin estado optimista que los oculte.
- Ningún proveedor se invoca; tipos generados sin contratos duplicados a mano.

#### Fuera de alcance

Proveedores reales u otro smoke (requiere propuesta y consentimiento propios),
login/refresh, secretos, recuperación de D020/D022, integración en rama destino,
push/publicación, H3 (prompts versionados, permisos interactivos, fases), chat,
SDK, distribución. No modificar ReferenceProject, configuración global ni lanzar agentes
de colaboración.
