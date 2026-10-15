# Plan archivado — P006 Calidad de uso y distribución local (antes H5)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 5 — Calidad de uso y distribución local

- Importación de reportes JUnit y detalle por test con cobertura declarada por perfil.
- Backup/restore, retención de logs y diagnósticos de compatibilidad.
- Assets web empaquetados y comando único de inicio.
- Sesión local, protección de endpoints, rutas y renderizado seguro de logs.
- Recorridos E2E: crear, importar, ejecutar, bloquear, denegar, reintentar y recuperar.
- Criterio: instalar en entorno limpio, completar un flujo y restaurar backup sin depender del checkout de desarrollo.

Después del cierre del hito 5 (D045/D046) se añadieron a esta fase el ejecutor de validaciones (D047/D048), la configuración local TOML (D049), el primer uso real (D050/D051) y el comando de desarrollo (D053), con los alcances siguientes.

## Alcances conservados

### Siguiente tarea — H5.1 Importación JUnit y detalle de tests

_Origen: `docs/discovery/H5.1_SCOPE.md`._

H4.3 segundo perfil se completó offline el 2026-10-13 (D038).
`typescript-web` declara preparación npm offline desde lock, tipos, tests y build
estático, comandos y reglas. Fixture con Node 24.15.0, npm 11.12.1 y TypeScript
5.9.3; procesos reales por el puerto de prueba, agentes falsos y Git/SQLite
temporales hasta COMMITTED. Sin condiciones de stack nuevas en el núcleo.
Ver [entrega y límites](../phase-005/H4.3_TYPESCRIPT_PROFILE.md).

Estado verificado:

- esquema `0013_bootstrap` y codec conservados;
- 526 pruebas pytest y 121 subtests (16 nuevas de H4.3);
- 12 checks ligeros y 4 pruebas Node;
- check TypeScript del frontend; checks existentes de esquema/OpenAPI;
- preparación → tipos → tres tests Node → build con evidencia Git intacta;
- tarea corregida en worktree → ACCEPTANCE_READY → commit exacto → COMMITTED;
- fallos de tests/tipos/build/política, caché, engines y lock impiden continuar;
  permisos y snapshots conservados, cambios externos bloquean commit.

No se usaron proveedores ni se migró la SQLite de trabajo. El runner real es de
prueba para fixture confiable; no añade un ejecutor de comandos al servicio. La
plantilla de bootstrap H4.2 sigue siendo documental. **H5.1 no está iniciado.**
Los consentimientos de smokes siguen agotados.

#### Objetivo y alcance (primer incremento del hito 5)

1. Importar reportes JUnit XML de validaciones y conservar el original con hash y
   procedencia vinculados al comando, intento y evidencia de contenido exacto.
2. Exponer detalle por test (id/suite/resultado/duración/error), distinguiendo
   datos observados, ausentes y parciales; no sumar duraciones como tiempo real.
3. Declarar rutas de reportes y cobertura de validación por perfil, sin introducir
   condiciones específicas de frameworks en el núcleo.
4. Incorporar consulta API/UI y pruebas offline con reportes sintéticos válidos,
   parciales e inválidos. Acotar el incremento a JUnit; otros trabajos del hito 5
   permanecen pendientes.

#### Criterios de aceptación

- Un run conserva el reporte original y muestra detalle por test con procedencia
  y cobertura declarada; no presenta datos ausentes como éxitos o ceros.
- Reporte inválido/ausente/parcial produce diagnóstico explícito, sin fabricar
  casos ni reemplazar resultados observados del comando.
- El parser no lee rutas externas ni ejecuta contenido XML. Tests y review siguen
  vinculados al contenido exacto, sin aceptar ni hacer commit por el reporte solo.
- Pasan las regresiones offline pertinentes y se actualiza la documentación.

#### Fuera de alcance

- Backup/restore, retención, empaquetado/distribución y demás incrementos de H5.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.2 Backup y restauración local

_Origen: `docs/discovery/H5.2_SCOPE.md`._

H5.1 importación JUnit y detalle de tests se completó offline el 2026-10-13
(D039). Original/hash y casos conservados en el historial, declaraciones por
comando/perfil, captura/parser acotados, procedencia de run/intento/comando/Git,
consulta paginada y descarga API/UI. TypeScript genera JUnit con el reporter Node.
Ver [entrega y límites](H5.1_JUNIT.md) y
[alcance original](NEXT_STEPS.md).

Estado verificado:

- esquema `0013_bootstrap` sin migración nueva; codec 6 y formatos 1–5 compatibles;
- 569 pruebas pytest y 121 subtests; checks de esquema/OpenAPI existentes;
- 43 casos JUnit nuevos y reporter Node real con tres casos/duraciones;
- 12 checks ligeros, cuatro pruebas del cliente Node y TypeScript/build;
- reportes válidos, truncados, inválidos, ausentes y anteriores con diagnósticos;
- XML activo, rutas externas/enlazadas, archivos especiales y límites rechazados;
- original persistido después de reiniciar y de editar/eliminar su fuente;
- revalidación y check de fase, comandos/intentos/evidencia exacta conservados;
- paginación HTTP, errores como texto en Chrome y commit exacto/invalidez por deriva.

No se usaron proveedores ni se migró la SQLite de trabajo. No se incorporó
retención, backup ni distribución. **H5.2 no está iniciado.** Los consentimientos
de smokes siguen agotados.

#### Objetivo y alcance (segundo incremento del hito 5)

1. Definir y realizar una copia local consistente de la SQLite y de los artefactos
   gestionados necesarios para recuperar su historial y referencias.
2. Restaurar explícitamente en un destino nuevo, con manifiesto, hashes y
   comprobación de compatibilidad/integridad; conservar los originales.
3. Verificar offline con bases/checkouts/artefactos sintéticos y documentar el
   procedimiento y sus límites. Una restauración no autoriza a reanudar procesos.

#### Criterios de aceptación

- La copia conserva historial, snapshots, reportes y referencias de artefactos
  con una política explícita de consistencia frente a actividad del servicio.
- Restaurar en un destino vacío produce una autoridad SQLite íntegra y artefactos
  verificables; corrupción, ausencia o versión incompatible producen diagnóstico.
- No sobrescribe el estado de trabajo ni supone que procesos inciertos terminaron;
  no ejecuta agentes ni repite efectos al restaurar.
- Pasa el recorrido offline copia → restauración → consultas con datos sintéticos,
  las regresiones pertinentes y se actualiza la documentación.

#### Fuera de alcance

- Retención/GC, empaquetado/distribución y demás incrementos de H5.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.3 Retención local de logs

_Origen: `docs/discovery/H5.3_SCOPE.md`._

H5.2 backup/restauración local se completó offline el 2026-10-13 (D040).
Copia con servicio/escritores detenidos y mecanismo de backup SQLite; manifiesto,
hashes/referencias verificadas, restauración a destino nuevo y guardia persistente
de solo lectura. No se reanudan procesos ni se repiten efectos al abrir una copia.
Ver [procedimiento y límites](H5.2_BACKUP.md) y
[alcance original](NEXT_STEPS.md).

Estado verificado:

- esquema `0013_bootstrap` y codec 6 conservados; historial 1–6 compatible;
- 612 pruebas pytest y 121 subtests, con 43 casos nuevos de backup/restauración;
- WAL real, historial/snapshots/JUnit/eventos y filas operativas conservados;
- prompts/streams CLI, rangos y colas inciertas, snapshots/exportación H2.5;
- consultas HTTP y artefactos restaurados independientes de sus originales;
- guardia SQLite/API, sin cargar configuración ni iniciar supervisor/observador;
- corrupción/ausencia/versiones/rutas/enlaces/límites/concurrencia rechazados;
- 12 checks ligeros, cuatro pruebas Node, TypeScript/build y checks de esquema/OpenAPI.

No se copió ni migró la SQLite de trabajo, no se usaron proveedores ni smokes.
No se implementaron GC, distribución ni reactivación operativa de una copia.
**H5.3 no está iniciado.** Los consentimientos de smokes siguen agotados.

#### Objetivo y alcance (siguiente incremento del hito 5)

1. Definir una política local explícita de retención de logs voluminosos y sus
   límites; separar originales purgables de contratos, snapshots, permisos,
   aprobaciones y veredictos que deben conservarse.
2. Diseñar e implementar vista previa y aplicación explícita de la política sobre
   artefactos gestionados, con diagnóstico/auditoría de bytes retirados y
   referencias ausentes deliberadamente diferenciadas de pérdida/corrupción.
3. Mantener backup/restauración compatibles con la evidencia retenida y probar
   offline sobre datos sintéticos. No purgar archivos reales del usuario.

#### Criterios de aceptación

- La política y sus efectos son visibles antes de eliminar bytes; no hay purga
  automática ni eliminación de artefactos de intentos activos/inciertos.
- Historial, contratos, decisiones, aprobación/veredicto y procedencia exacta se
  conservan; retirar un log no certifica éxito ni borra sus hashes observados.
- La consulta distingue purga autorizada de archivo perdido y no sirve otra
  versión de bytes como si fuera la registrada.
- Backup/restauración conserva lo retenido y representa las ausencias autorizadas
  sin admitir corrupción silenciosa. Las copias existentes permanecen intactas.
- Regresiones offline pertinentes correctas y documentación actualizada.

#### Fuera de alcance

- Distribución/assets/comando único de inicio, diagnósticos CLI/SDK y otros
  incrementos de H5; reactivación operativa de restauraciones y backup de Git.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.4 Diagnósticos locales de compatibilidad

_Origen: `docs/discovery/H5.4_SCOPE.md`._

H5.3 retención local de logs se completó offline el 2026-10-13 (D041).
Política explícita por corte UTC/tamaño, preview sellada, aplicación confirmada
con escritores detenidos, intenciones/resultados auditados y conciliación tras
caída. Solo retira originales externos stdout/stderr de intentos sellados;
historial/contratos/permisos/aprobaciones/veredictos/hashes quedan conservados.
Consulta CLI/API/UI distingue purga autorizada, pendiente, pérdida y corrupción.
Backup/restauración representa las ausencias autorizadas, acepta bundles anteriores
y mantiene su guardia de consulta. Ver [entrega y límites](H5.3_RETENTION.md)
y [alcance original](NEXT_STEPS.md).

Esquema `0013_bootstrap` y codec 6 conservados. Pruebas offline sintéticas de
retención/recuperación/CLI/HTTP y regresión completa de backup; checks ligeros,
Node, OpenAPI/tipos y TypeScript/build. Evidencias y recuentos en STATE.
No se purgaron archivos reales ni se migró la SQLite de trabajo. No se usaron
proveedores ni smokes. Rotación, GC y abandono de intención pendiente quedan fuera.
**H5.4 no está iniciado.** Los consentimientos de smokes siguen agotados.

#### Objetivo y alcance (siguiente incremento del hito 5)

1. Ofrecer diagnósticos locales explícitos de las capacidades/versiones CLI y
   configuración necesarias para los adaptadores existentes, reutilizando su
   preflight en lectura y separando datos solicitados de observados/ausentes.
2. Mostrar incompatibilidades y pasos concretos de corrección sin iniciar jobs,
   agentes, login, instalaciones, cambios globales, fallback ni llamadas de consumo.
3. Verificar offline con ejecutables/configuraciones sintéticos y documentar
   alcance, comandos disponibles y límites de lo que un preflight certifica.

#### Criterios de aceptación

- El diagnóstico es opt-in y no ejecuta inferencia ni efectos de checkout.
- Versiones/capacidades incompatibles o desconocidas no aparecen como compatibles;
  help/version no se presentan como prueba de autenticación, cuota o argv completo.
- No revela credenciales ni modifica configuraciones o snapshots congelados.
- Errores, timeout y salida inesperada producen diagnóstico acotado, sin fallback
  ni reintento silencioso; una corrección pertenece a una acción posterior explícita.
- Pruebas offline pertinentes y documentación actualizada.

#### Fuera de alcance

- Distribución/assets/comando único de inicio, sesión local, SSE gestionado,
  App Server/SDK, reactivación de restauraciones, backup Git, push y publicación.
- Proveedores/smokes y diagnóstico real de autenticación: autorización específica
  antes de consumir o acceder a la sesión del usuario (D033 punto 8).

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.5 Assets web empaquetados y comando único de inicio

_Origen: `docs/discovery/H5.5_SCOPE.md`._

H5.4 diagnósticos locales de compatibilidad se completó offline el 2026-10-13
(D042). CLI explícita `diagnose-cli` y biblioteca, compartiendo preflight con el
adaptador: versión/help acotados, entorno explícito, resultados desconocidos o
incompatibles con pasos de corrección. No revela salidas libres ni credenciales;
no consulta autenticación ni inicia inferencia. Ver [entrega y límites](H5.4_DIAGNOSTICS.md)
y [alcance original](NEXT_STEPS.md).

Esquema `0013_bootstrap`, codec 6, adaptador `cli-4` y locks conservados.
Pruebas offline sintéticas y regresión en STATE. Sin CLI reales, proveedores,
smokes, cambios globales ni SQLite de trabajo. **H5.5 no está iniciado.**
Los consentimientos de smokes siguen agotados.

#### Objetivo y alcance (siguiente incremento del hito 5)

1. Empaquetar los assets web compilados con el producto para servirlos sin el
   checkout de desarrollo ni Node en ejecución.
2. Ofrecer una entrada local única de inicio, reutilizando FastAPI/Uvicorn,
   configuración explícita, guardias y comportamiento opt-in existentes.
3. Documentar instalación reproducible y arranque, verificando un paquete en un
   entorno temporal limpio con datos sintéticos y sin proveedores.

#### Criterios de aceptación

- El paquete contiene los assets necesarios y sirve la UI y API desde loopback
  sin depender del cwd ni del checkout de desarrollo.
- Un comando documentado inicia el servicio; configuración/errores de esquema
  tienen diagnóstico claro, sin migraciones destructivas o correcciones silenciosas.
- No se activan proveedores, proyectos, observadores ni supervisor sin opt-in;
  restauraciones conservan la guardia de consulta.
- Locks y versiones explícitos; construcción e instalación temporal verificadas,
  sin cambios globales, publicación ni uso de datos privados.
- Pruebas pertinentes y documentación de requisitos y límites actualizada.

#### Fuera de alcance

- Sesión local (incremento posterior del hito 5), SSE gestionado, App Server/SDK,
  reactivación de restauraciones, backup Git, push y publicación.
- Proveedores/smokes y diagnóstico real de autenticación: requieren autorización
  específica (D033 punto 8). No incorporar una instalación global automática.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.6 Sesión local y protección de endpoints

_Origen: `docs/discovery/H5.6_SCOPE.md`._

H5.5 assets web empaquetados y comando único de inicio completado offline el
2026-10-13 (D043). Wheel/sdist con UI y migraciones, instalación aislada con pins
y hashes, `init-db` explícito sobre destino nuevo y `serve` en loopback.
Ver [entrega y límites](H5.5_DISTRIBUTION.md) y
[alcance original](NEXT_STEPS.md).

Esquema `0013_bootstrap`, codec 6, adaptador `cli-4` y locks conservados.
Verificado paquete instalado fuera del checkout, HTTP, simulación/reinicio y
backup/restauración de consulta con datos sintéticos. **H5.6 no está iniciado.**
Los consentimientos de proveedores/smokes siguen agotados.

#### Objetivo y alcance (siguiente incremento del hito 5)

1. Incorporar sesión local para el navegador según especificación §10 y D033,
   sin convertir la cabecera X-Harness-Local en una credencial.
2. Proteger lecturas y mutaciones del producto de forma coherente, incluidas
   lecturas H0/H1, recursos de evidencias y streams; preservar Host/Origin/CSRF.
3. Integrar inicio, expiración/cierre y errores de sesión en UI/entrada instalada,
   manteniendo restauraciones en consulta y proveedores opt-in.

#### Criterios de aceptación

- Acceso a datos y acciones exige sesión local válida; loopback o una cabecera
  pública por sí solos no autorizan. Definir amenazas y límites frente a otros
  usuarios del SO, sin prometer aislamiento frente al propietario del proceso.
- Credenciales de sesión no aparecen en logs, evidencias, historial, enlaces
  persistentes ni respuestas ajenas al flujo de establecimiento autorizado.
- UI y clientes manejan ausencia/caducidad/cierre sin ejecutar ni repetir acciones
  automáticamente; guardias de Host/Origin/CSRF conservadas.
- Rutas y renderizado de logs/evidencias siguen siendo seguros y acotados;
  errores y pruebas negativas cubren acceso sin sesión y orígenes ajenos.
- Paquete instalado y restauración de consulta funcionan con sesión; no activa
  proyectos, observación ni proveedores ni migra datos silenciosamente.
- Tests offline pertinentes y documentación de operación/límites actualizada.

#### Fuera de alcance

- Acceso remoto/multiusuario, OAuth externo, App Server/SDK, SSE gestionado,
  reactivación de restauraciones y publicación.
- Proveedores/smokes: requieren autorización específica (D033 punto 8).
- Recorridos E2E amplios restantes del hito 5, aparte de verificar la sesión.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Siguiente tarea — H5.7 Recorridos E2E offline

_Origen: `docs/discovery/H5.7_SCOPE.md`._

H5.6 sesión local y protección de endpoints completado offline el 2026-10-13
(D044). Sesión efímera con clave en archivo privado, cookie HttpOnly, caducidad y
cierre; guardia uniforme de datos/acciones/streams, UI sin reenvíos automáticos y
paquete/restauración de consulta verificados con sesión.
Ver [entrega y límites](H5.6_SESSION.md) y
[alcance original](NEXT_STEPS.md).

Esquema `0013_bootstrap`, codec 6, adaptador `cli-4` y locks conservados.
Navegador bloqueó la URL de comprobación visual con `ERR_BLOCKED_BY_CLIENT`;
pruebas HTTP/cliente y paquete verificadas. **H5.7 no está iniciado.**
Los consentimientos de proveedores/smokes siguen agotados.

#### Objetivo y alcance (último incremento previsto del hito 5)

1. Consolidar recorridos reproducibles de crear, importar, ejecutar, bloquear,
   denegar, reintentar y recuperar, usando proyectos sintéticos y puertos falsos.
2. Ejercitar la sesión local y las confirmaciones desde UI/API, con historial,
   idempotencia, evidencias y recuperación coherentes tras reiniciar.
3. Verificar el recorrido disponible en paquete instalado y restauración de
   consulta sin depender del checkout de desarrollo; documentar los límites.

#### Criterios de aceptación

- Los recorridos cubren los escenarios del backlog H5 y distinguen fakes de
  transporte/proveedores reales; no consumen modelos ni amplían permisos.
- Un rechazo, pérdida de sesión o caída no reenvía acciones automáticamente ni
  pierde su identidad/evidencia; reintentos y recuperación siguen explícitos.
- Aceptación/commit se vinculan al contenido exacto; tests, permisos o revisión
  fallidos impiden avanzar. No integrar ramas ni cerrar fases por inferencia.
- Inicio desde instalación aislada, operación sintética y consulta de backup
  restaurado comprobados; la restauración no reanuda trabajos.
- Verificar UI si el navegador permite acceso; registrar con precisión cualquier
  bloqueo de herramienta y no presentar pruebas HTTP como QA visual.
- Checks offline pertinentes, diff y documentación de estado actualizados.

#### Fuera de alcance

- Smokes/inferencia reales (D033 punto 8 exige autorización específica), acceso
  remoto/multiusuario, OAuth, App Server/SDK, SSE gestionado y publicación.
- Reactivación de restauraciones, actualización instalada de bases existentes,
  integración de ramas, GC y ampliaciones de producto no necesarias al recorrido.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.

### Ejecutor de validaciones de producto — alcance previo

_Origen: `docs/discovery/COMMAND_RUNNER_SCOPE.md`._

Elegido explícitamente por el usuario el 2026-10-13, sobre `3bb9541`, Git limpio.
Sustituye la elección pendiente de NEXT_STEPS; no inicia un piloto.

#### Diseño acotado

- Adaptador POSIX opt-in de `CommandRunner`, conectado por `ports_factory` del
  servidor y ligado al journal del job. Reutiliza cola, propietario, lease,
  compuerta de lanzamiento, grupos POSIX y recuperación H2.2/H2.3.
- Configuración inmutable: checkout confiable explícito, autorización de comandos
  exactos (argv/cwd/entorno/timeout), mapa de ejecutables absolutos, entorno base
  completo y límites de tiempo/captura. Hash/versiones congelados al admitir el
  run; discrepancia o configuración antigua sin esa identidad impide ejecutar.
  No se cambian snapshots anteriores. No se hereda el entorno del servicio.
- Confianza en código/scripts/configuración externa, autorización del comando y
  política de prefijos del perfil son decisiones separadas. No se conceden
  permisos H3.2 a agentes ni red por permitir un comando. Ejecución nativa con UID
  del servicio: sin sandbox físico; solo repositorios y programas confiables que
  no daemonizan ni escapan del grupo. npm puede ejecutar shell dentro de scripts
  autorizados; el adaptador no introduce shell.
- Registro propio por command_id mediante eventos `command_process_*` bajo el
  mismo job: intención, identidad antes de GO, fragmentos de bytes acotados y
  resultado observado. Es una proyección del journal existente, sin otra cola,
  tabla o migración. SQLite conserva los prefijos exactos en base64; no se añade
  otro almacén ni retención de comandos. Preparación y validación lo comparten.
- stdout/stderr acotados por stream, truncamiento e incompletitud explícitos,
  exit observado nullable, duración monotónica, timeout/errores y estado del
  grupo. Captura incompleta/truncada no acredita éxito. Fallo de journal o grupo
  incierto aborta el motor y conserva el lock. No relanzamientos automáticos.
- Recuperar exige la confirmación existente con job/token/versión, propietario
  cerrado o ausente y todos los grupos ausentes. Ni caída, ni lease, ni exit del
  líder prueban muerte de hijos. No se señalizan PIDs recuperados. La recuperación
  no adopta validaciones parciales ni las repite; revalidar es una acción nueva.
- Resultado aditivo con metadatos de captura y codec nuevo solo donde se usen;
  formatos anteriores mantienen su serialización. JUnit, review, evidencia Git
  exacta y commit siguen siendo puertas independientes. Backup/retención deben
  reconocer grupos de validación para comprobar parada.

#### Criterios de aceptación

1. Probar argv literal, cwd/entorno/autorización/configuración congelada; rechazar
   ejecución no compuesta, discrepancias, symlinks/escape y comandos no autorizados.
2. Procesos sintéticos: éxito, exit no cero, ejecutable ausente, timeout, stdout y
   stderr excesivos, bytes no UTF-8 y descendientes vivos tras salir el líder.
3. Intención e identidad preceden efectos; fallo antes/después de GO, caída real
   del supervisor, lease vencido y reinicio con grupo vivo mantienen exclusión.
   Confirmación explícita solo tras ausencia comprobada, sin duplicar ejecución.
4. Recorrido TypeScript real offline en Git/SQLite temporales con agentes falsos:
   preparación, tipos, tests, JUnit, build, aceptación y commit exacto. Fallos y
   cambios posteriores no permiten commit; historial y evidencia sobreviven reinicio.
5. Regresión offline pertinente, diff revisado, STATE/NEXT_STEPS/DECISIONS y
   README/AGENTS sincronizados, commit solicitado y Git final comprobado.

Fuera: proveedores, login/smokes, red/instalación online, UI nueva, configuración
completa de uso real, sandbox de código hostil, procesos escapados, GC/rotación,
publicación/push y cambios globales. No se ejecuta ReferenceProject ni el harness para
el desarrollo. No hay contradicción material con D016/D017/D031/D038/D039;
se implementa ahora la brecha expresamente aplazada por D038/D046.

### Composición de uso real por configuración local — alcance previo

_Origen: `docs/discovery/LOCAL_CONFIG_SCOPE.md`._

Elegido por el usuario el 2026-10-13 tras D048, sobre `5e0c374`, Git limpio.
Decisiones del usuario: archivo **TOML fuera del checkout** leído con `tomllib`
(sin dependencias nuevas) y perfil **TypeScript web** como primera composición.
No autoriza ejecutar proveedores, smokes ni piloto.

#### Diseño acotado

- Módulo `services/local_config.py` (`local-config-1`) que convierte un TOML del
  operador en `ManagedConfig`: servicio, Git, CLI Codex/Claude y proyectos.
  Sin valores implícitos para ejecutables, entorno, confianza, modelos ni
  esfuerzos. Claves desconocidas, tipos erróneos o rutas relativas se rechazan.
- El archivo es autoridad local: regular, sin enlaces, del UID del servicio, sin
  escritura de grupo/otros, ≤ 64 KiB, UTF-8 y fuera de todo checkout. No se lee
  nada del repositorio gestionado ni `.harness/project.yaml` (portable, futuro).
  No debe contener secretos: la autenticación sigue en cada CLI.
- Proyectos: id, raíz canónica existente, `repository_trusted = true` explícito,
  perfil `typescript-web` (único admitido), política de modelos/esfuerzos y
  `tag_kind` opcional; techo de permisos H3.2 opcional con la validación
  existente. Bootstrap desactivado.
- Composición por job, siempre nueva: `CLIProcessAdapter` (artefactos en
  `state_dir/artifacts/<id>`), `ManagedCommandRunner` (D047) con ejecutables
  absolutos, entorno explícito y autorización exacta de los comandos del perfil
  solo si `authorize_profile_commands = true`, más variantes declaradas, y
  `GitWorkspace` con Git absoluto e identidad explícita.
- Versiones congeladas por proyecto: adaptadores CLI y comandos con sus hashes,
  versión del paquete, `local-config-1` y hash de la composición del proyecto.
  Si al ejecutar difieren de las vigentes, el job se aborta antes de efectos
  con la cuarentena existente; no se reinterpreta ni se reescribe.
- Entorno CLI: `USER` obligatorio y comprobado contra el UID local (D024).
- Entrada: `harness-local serve --config RUTA` (incompatible con
  `HARNESS_MANAGED_CONFIG`), `harness-local check-config RUTA [--preflight]`
  (resumen sin valores de entorno; preflight solo version/help D042) y
  `local_config:from_environment` con `HARNESS_LOCAL_CONFIG` para desarrollo.
  Cargar la configuración nunca lanza procesos. Supervisor explícito.

#### Criterios de aceptación

1. Configuración válida produce proyecto, contexto, versiones y puertos nuevos
   por job sin lanzar procesos; ejemplo documentado coherente con el esquema.
2. Rechazo sin efectos de: claves desconocidas, rutas relativas o inexistentes,
   archivo enlazado/compartible/grande/dentro de un checkout, estado dentro de
   un checkout, confianza ausente, perfil no admitido, modelos ausentes, USER
   distinto, CLI no soportada, ids/raíces duplicados.
3. Cambio de composición tras admitir un job: cuarentena antes de CLI/comandos.
4. Recorrido offline con el TOML: CLI falsas por el adaptador real, Node/npm/tsc
   reales, Git/SQLite temporales hasta aceptación y commit exacto; runtime del
   servicio registra el proyecto. `check-config` sin secretos y con preflight.
5. Regresión offline, diff revisado, STATE/NEXT_STEPS/DECISIONS/README/AGENTS.

Fuera: proveedores reales, login, smokes, otros perfiles, `.harness/project.yaml`,
UI de configuración, recarga en caliente, bootstrap, red e instalación online,
publicación/push, configuración global, ReferenceProject y harness de desarrollo.
Sin contradicción material: la especificación ubica la configuración local en el
directorio de la aplicación y reserva el YAML del repositorio para datos portables.
