# Estado — my_harness

Actualizado: 2026-10-27. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P012 cerradas. Primera versión
local completada en el alcance de D151/D153 y preparación pública archivada con expediente sin ejecutar (D181/D182).

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Formateo del perfil tras cada turno del ejecutor (D133). Codec de historial
  en formato 8 (lee 1–7).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0027_profile_proposals` (54 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams. Proyección derivada `run-projection-1` escrita con el historial y comprobada en el backup
  (P010-T003, D144).
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-14`, configuración hasta `local-config-8`, lectura de 1–7), revisor en solo lectura con esquema tipado, memoria automática desactivada,
  supresión de confianza del escritor Codex. Validaciones nativas `commands-1` con JUnit. Perfiles: `typescript-web`
  (componible desde el TOML) y perfiles declarados en `[profiles.*]` de
  `local-config-4`, con el ejemplo `python-django` (P008, D095).
  Detección automática por PATH explícito/ruta opcional en v7, sin pin obligatorio; mínimos Codex 0.163.0 /
  Claude 2.1.304, posteriores con compatibilidad condicionada al contrato conocido (P011-T012, D174).
  Política/cliente observados congelados por job y revalidación por intento/antes de GO.
  Formateador D133 optativo para perfiles declarados en v8 (P012-T010, D194), verificado offline; v1–v7 conservan
  su contrato y huellas. [Entrega](archive/phase-012/P012-T010_FORMATEADOR_DECLARATIVO.md). Recorrido real posterior con
  perfil declarado/formateador v8 y pareja Claude 2.1.310/Codex 0.164.0 hasta COMMITTED (P012-T002, D198).
- **Fases y documentos** ([P004](archive/phase-004/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md),
  [P008](archive/phase-008/SUMMARY.md)): check READY, reconciliación, preguntas, lote desatendido,
  enmiendas, abandono y cierre con tag. Contrato documental unificado y
  obligatorio de D088 desde P008-T002 (layout v2 modificado; DECISIONS único con índice): bloques regenerados en cada
  commit, edición confirmada, exportación y cierre unificado que archiva en `archive/phase-NNN/`, con
  planificación posterior confirmada (D091).
  `AGENTS.md` congelado por intento, salvo definición; `document_layout = "d088-12"`.
- **Creación y chat** ([P005](archive/phase-005/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): creación por
  conversación con borradores en disco y CAS (la v1 se rechaza desde P008-T002); planificación de fase conversacional; chat
  sobre una instantánea de HEAD sin lock, con comandos deterministas y propuestas que crean tareas confirmadas.
- **Creación y preparación Django** ([P009](archive/phase-009/SUMMARY.md), D117–D119): carpeta padre
  elegida y retirada desde UI, hijos nuevos con intención/recuperación, presets por proyecto en `local-config-5`
  y receta `django-recipe-1` confirmada tras D088; entorno acreditado y commit técnico separado. Selector de
  tareas del NEXT_STEPS con CAS y notas congeladas (D135). Wheel verificado con definición D088 (D126).
  Segunda receta `typescript-web-recipe-1` (P010-T002, D143): manifiesto inicial con `typescript@5.9.3`, `npm ci`
  desde la caché del operador y validaciones del perfil antes del commit técnico, para hijos TypeScript web nuevos.
  Recetas v2 (`django-recipe-2`, `typescript-web-recipe-2`) en `local-config-6` con el idioma de trabajo del hijo
  sellado en plan/recibo y comprobaciones por `id` (P011-T020, D168); v5 conserva v1. Prompts con la directiva
  del par congelado y documentos generados en el idioma de trabajo (P011-T009, D169). Interfaz React completa en
  en/es por catálogos tipados y diagnósticos HTTP propios en el visual guardado (P011-T010, D170). Textos propios
  del servicio/CLI antes españoles en en/es con el visual de cada emisión: petición, job congelado o CLI (P011-T021, D171).
  Diagnósticos visibles del servicio antes ingleses (razones de parada/aceptación incluidas) también en en/es; los
  técnicos ingleses quedan listados por categoría y la UI distingue rechazos por código (P011-T022, D172).
- **Incorporación de proyectos** ([P008](archive/phase-008/SUMMARY.md), D161): inventario estático sobre HEAD,
  conversación de solo lectura y borradores privados de B, perfil/documentos confirmados y commit conciliable.
  Objetos locales, blobs por hash, filtros/gitlinks y destinos ignorados comprobados antes de escribir y recuperar.
  A, visor/observación legacy y activación/reversión retirados en P011-T019; datos y migraciones anteriores
  conservados, jobs retirados/ambiguos en cuarentena sin ejecutarlos. Guardia de activaciones ACTIVE previas
  conservada para trabajo gestionado, sin reactivar los flujos retirados.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación gestionada por cursor de eventos. Detalle, ciclos paginados, diff y casos JUnit de un run
  (D144), métricas y vista previa de exportación (D145) leen la proyección sin decodificar el historial.
- **Operación** ([P006](archive/phase-006/SUMMARY.md)): wheel con UI y migraciones, `init-db`, `serve`,
  `check-config`, `metrics-backfill`, `diagnose-cli`; `scripts/dev` para desarrollo. `migrate` actualiza bases
  existentes con instantánea previa `premigration-1` y declaración de parada (P010-T012, D150).
- **Evidencia con proveedores reales** (consentimientos agotados): transporte de las tres CLI (D025), primer uso real
  COMMITTED con fase cerrada (D050), cuatro combinaciones revisor/ejecutor COMMITTED (D071) y recorrido Django
  desde creación UI hasta cuatro tareas, QA conjunto y cierre/archivo de P001 (P009-T012, D139);
  26 invocaciones de 60 previstas. P012-T002 añade dos B COMMITTED, idempotencia y una tarea COMMITTED con
  perfil declarado v8/CLI actuales (D191/D193/D198): Claude 9/12 y Codex 3/3, fixtures sintéticos, sin permisos nuevos.
- **Límites**: contención cooperativa sin aislamiento del sistema operativo; validaciones sin hora; manifiestos de
  receta fijos tras preparar; dos avisos *low* de KaTeX.
  Piloto de receta Django limitado a macOS arm64/Python 3.13. La validación real de B y del perfil Python/Django
  declarado aplazada en D151 queda acreditada en T002 sobre fixtures sintéticos; sin extrapolar a proyectos
  de producción, otras plataformas o parejas. El piloto no evalúa comparativamente la calidad de modelos.
  Observación de P009 pendiente: alta sin redirección (aplazada en ROADMAP). El texto de marcadores de
  define-project y la deriva tras cerrar están corregidos en P010-T004 (D146) y T005 (D147). Candidato público
  verificado solo en macOS ARM64 y Chrome; CI remota, otras plataformas y CLI reales sin ejecutar en P011.

- **Primera versión local** ([P010](archive/phase-010/SUMMARY.md), D141–D153): doce tareas completadas,
  siete criterios de salida y trece criterios globales con dictamen en el alcance declarado. T009 verifica
  el wheel `0.1.0` con UI/migraciones fuera del checkout; pytest (1682 y 121 subtests), unittest (12), Node (82),
  tipos/build y Alembic temporal correctos, con dos opt-in omitidas. QA de escritorio con API sintética y doce
  capturas, sin integración navegador/backend adicional ni uso real nuevo. [Matriz](archive/phase-010/P010_MATRIZ_ACEPTACION.md),
  [revisión](archive/phase-010/REVIEW.md) y [paquete](archive/phase-010/P010-T009_VERIFICACION_FINAL.md).
- **Preparación pública** ([P011](archive/phase-011/SUMMARY.md), D154–D182): veinticuatro tareas y diez criterios
  con dictamen favorable (T017). Licencia MIT, código/pruebas en inglés, retirada legacy/A, idiomas visual y de
  trabajo, CLI por capacidades, baseline pública en `docs/public/` y README de primer uso. Candidato `0.1.0` de 387
  archivos (manifiesto `74cc9141…ea71`, wheel `46d29c20…d9d6`), primer uso desde clon limpio y QA en Chrome con CLI
  falsas; pytest 1671 y 29 subtests, unittest 8, Node 95. [Revisión](archive/phase-011/P011_REVIEW.md) y
  [expediente de apertura](archive/phase-011/P011_EXPEDIENTE_APERTURA.md), sin CI remota ni acción ejecutada.

- **Validación real previa a apertura** ([P012](archive/phase-012/SUMMARY.md), D183–D212): trece tareas
  completadas y siete criterios con dictamen favorable. Pareja Claude 2.1.310/Codex 0.164.0 con cli-14,
  incorporación B/idempotencia, tarea Python/Django declarada v8 COMMITTED, chat/propuesta QUEUED,
  backup/restauración con consulta API/UI y TypeScript v2/es hasta tarea y cierre del hijo. Correcciones
  sintéticas T008–T013 incluidas en la suite final: **1760 pytest y 29 subtests, 8 unittest, 119 Node**,
  dos opt-in omitidas; tipos/build, Alembic temporal, distribución y documentación correctos (T005).
  Candidato `0.1.0`: **401 archivos/5.480.755 bytes**, manifiesto `cf191a40…9362a`, wheel `eef56a29…4504ab`;
  P011 conservada aparte. [Revisión](archive/phase-012/P012_REVIEW.md) y
  [expediente original](archive/phase-012/P012_EXPEDIENTE_APERTURA.md), sin acciones remotas ejecutadas.
  Evidencia real acumulada de sus wheels/tramos, fixtures sintéticos/macOS ARM64/Chrome; no acredita una
  ejecución real nueva del paquete final, otras parejas actuales, creación Django v2 ni producción.
  Dos REVISION_LIMIT, dos checks rechazados, propuesta QUEUED e identidad histórica `unknown` conservados;
  la consulta no certifica muerte de escritores ni autoriza reactivar la base. Consumo 19 Claude/4 Codex;
  consentimientos agotados, sin transferir saldos.

## Mantenimiento posterior al cierre

El 2026-10-26 se corrige la fila resumen de P012 en ROADMAP para reflejar su cierre ya documentado y se
desactiva el mantenimiento automático en el helper Git de los fixtures de incorporación. Resuelve la carrera
con `maintenance.lock` indicada por el usuario en la CI de `my-harness-archive`, conservando la comparación
completa de `.git` y sin cambiar el producto ([D213](DECISIONS.md#d213--mantenimiento-git-desactivado-en-fixtures-de-incorporación),
[informe](phase/2026-10-26_CORRECCION_CI_ARCHIVO.md)). Ese primer arreglo conserva el candidato público y los
artefactos archivados de P012; este mantenimiento no abre una fase ni publica el candidato.
Verificación local: 1761 pytest y 29 subtests pasados, 2 opt-in omitidas; 8 unittest, parsers y enlaces
documentales correctos. Regresión Trace2 roja antes del arreglo y verde después; CI remota pendiente.

Por encargo posterior del usuario, `my_harness_dist` incorpora esa corrección desde `08f27bc`: **401 archivos /
5.481.629 bytes**, manifiesto `5ef17ff3…4d4c55`, con un único archivo de pruebas modificado. Original P012
conservado en `my_harness_dist_p012_cf191a40`; P011, paquetes y snapshots intactos. El
[suplemento vigente](phase/2026-10-26_ACTUALIZACION_CANDIDATO.md) actualiza la identidad del árbol para abrirlo
sin reescribir el expediente archivado (D214). Pruebas en copia aislada; sin Git ni cachés en el candidato.
Verificación del árbol exportado: 1761 pytest y 29 subtests pasados, 2 opt-in omitidas; 8 unittest correctos.
Sustitución verificada por rutas, hashes y modos; checksums de los artefactos originales intactos.

## Fase activa — P013 Instalación guiada y configuración desde la UI

**P013 activa; T001 diseñada y T002–T013 completadas (T013 el 2026-10-27).**
[D215](DECISIONS.md#d215--p013-instalación-guiada-y-configuración-desde-la-ui),
[plan](phase/P013_PLAN.md), [tareas](NEXT_STEPS.md) y [flujo](flows/configuration-setup.md).
Dos tareas pendientes. **Siguiente: P013-T014**, revisión de salida y expediente actualizado.

| Entrega | Resultado y procedencia |
|---|---|
| [T001](phase/P013-T001_CONTRATO.md), D216–D218 | Contrato previo: instalación aislada, sesión sin TOML, autoridad privada/versionada y activación SQLite/CAS; global con reinicio, proyecto entre tareas. Contexto → propuesta → commit documental → preparación → activación. Diseño y checks documentales. |
| [T002](phase/P013-T002_INSTALACION.md), D219 | `scripts/install`: clon/paquete autocontenido, Python/uv/rutas/cachés elegibles, offline por defecto y red explícita. Venv/generaciones, recibo installation-1 y current.json atómico; replay/exclusión/actualización conservadora, fallos sin publicación parcial. Pruebas iniciales sintéticas. |
| [T003](phase/P013-T003_ARRANQUE.md), D220 | `scripts/start` verifica instalación y usa Python instalado fuera del checkout, DB/config/puerto/temporal explícitos. Solo inicializa DB ausente; migración D150 aparte. Locks heredados, señales/salidas y datos conservados. Pruebas iniciales de orquestación/señales. |
| [T004](phase/P013-T004_CONFIGURACION.md), D221 | Global v9/proyecto v1, preview/diff, CAS, TOML privados inmutables, journal recuperable por bytes. Guardar no activa. Migración aditiva 0026, tres tablas; hashes operativos 1–8 intactos. |
| [T005](phase/P013-T005_ASISTENTE_API.md), D222 | Asistente API protegido sin configuración/válida/inválida, detección por PATH y preflight D174 explícitos; guardado/activación/cancelación/recuperación. Promoción antes de componer runtime, sin hot reload; trabajo bloqueado sin autoridad. Consulta D040 sin sondas/originales. |
| [T006](phase/P013-T006_ASISTENTE_UI.md), D223 | `/setup` y `/settings/configuration` comparten formulario/TOML validados en servidor, diff y confirmaciones separadas. Candidato/base/sobre idempotente conservados en pestaña, conflicto sin rebase ni reenvío implícitos. UI/errores en/es y OpenAPI/tipos. |
| [T007](phase/P013-T007_PROPUESTA_PERFIL.md), D224 | IntakeContext sin runner/stack previo; conversación y propuesta estructurada con herramientas diferidas y evidencia funcional por comando. B inventaría HEAD sin ejecutar fuentes. Adopción CAS solo PROFILE_PROPOSED. Migración 0027: registro composición/perfil nullable, 54 tablas; planning versiona propuestas. |
| [T008](phase/P013-T008_PREPARACION.md), D225 | project-profile-preparation-1 separado de recetas: selección/plan/configuración/documentos sellados, confirmación exacta, journal/lock/lease/procesos antes de GO, argv/JUnit fresco, commit técnico conciliable y recibo propio. No activa; recuperación requiere escritores detenidos y prefijo acreditado, sin replay automático. |
| [T009](phase/P013-T009_ALTA_UI.md), D226 | Une creación/B, edición de propuesta, commit documental/P001, guardado privado, preparación y activación independiente con recibo/HEAD/barrera D118. Precompone y congela referencias; reenvíos no duplican efectos. Pruebas API/UI Go con agentes falsos; sin nueva migración. |
| [T010](phase/P013-T010_EDICION_ASISTIDA.md), D227 | Edición manual/asistida global/local con pareja/contexto activos congelados. Propuesta solo cambia borrador; cambios técnicos requieren documentos/plan/recibo nuevos. Global deriva copias privadas y activa/cancela conjunto con reinicio; recibo reutilizable solo por referencia exacta compatible. ASSIST con journal propio sin run ficticio. |
| [T011](phase/P013-T011_COMPATIBILIDAD.md), D228 | HITL confirmó preparación nueva para perfiles convertidos antes de activar conjunto/reiniciar sin fuente externa. TOML 1–8/hashes/snapshots/recibos originales intactos. Backup formato 2 con inventario/configuración/intenciones/evidencia; v1 sin configuración nueva legible. Restore de consulta lee bundle sin originales ni agentes. |

Las entregas T002–T011 detallan sus suites sintéticas y límites originales; T011: 2042 pytest/29 subtests,
153 Node, 8 unittest, tipos/build y Alembic temporal correctos; dos opt-in omitidas. No se reescribe esa evidencia.

[T012](phase/P013-T012_PRIMER_USO.md), [matriz](phase/P013_MATRIZ_ACEPTACION.md),
[D229](DECISIONS.md#d229--p013-t012-primer-uso-instalado-y-documentación-pública): instalación desde copia de
clon/caché inicialmente vacía con red de dependencias autorizada, recorrido completado offline tras corregir
scripts, actualización desde paquete/replay sin Node, rutas con espacios y caché incompleta rechazada.
Configuración global mediante formulario real en Chrome; reinicio; ambas altas con Go/CLI falsos hasta tarea
COMMITTED, original B conservado; edición formulario/TOML, backup/restauración de consulta sin originales.
QA en/es, claro/oscuro, escritorio y móvil con Tab/Enter muestreados, capturas y límites propios. Corrige sufijo
uv con ruta absoluta, configuración npm duplicada, .gitignore inesperado de uv, verificador desactualizado,
precheck de puerto en TIME_WAIT y claves React duplicadas al alternar altas. Sin cambiar modelos/API/TOML.
**2048 pytest y 29 subtests, 155 Node, 8 unittest correctos; dos opt-in omitidas**; build/tipos y documentación
verificados. El wheel de ensayo y sus hashes son propios; el candidato final tiene su evidencia separada en T013.
No usa proveedores reales, credenciales, bases P012 ni ejecuta este checkout con el harness. Servicios sintéticos
parados al terminar; originales/ensayos fallidos conservados, sin modificar configuración global del equipo.

[T013](phase/P013-T013_CANDIDATO.md), [D230](DECISIONS.md#d230--p013-t013-candidato-público-y-paquete-aislado-verificados):
candidato nuevo `my_harness_dist_p013` desde `984c287`, **445 archivos/6.389.580 bytes**, manifiesto
`ea0f74e9…00c428`; D214/P011/P012 y paquetes/snapshots intactos. Copia exacta aislada: **2048 pytest y 29 subtests,
8 unittest y 155 Node correctos**, dos opt-in omitidas; tipos/build, Alembic temporal y documentación correctos.
Wheel `2416672d…47076`, sdist/pylock/checksums propios; checker instalado sintético hasta commit/consulta,
instalación/replay y arranque/reinicio sin Node. Corrige falso positivo del scanner privado y orden del guion;
intentos fallidos conservados, sin cambios de producto ni nueva QA/proveedores reales. Servicios propios parados.
T013 no sustituye el candidato anterior ni cierra/publica: dictamen/expediente y archivo pendientes T014/T015.

**Publicación aplazada hasta cerrar P013.** Candidato D214, expedientes/paquetes/snapshots P011/P012 intactos;
[suplemento](phase/2026-10-26_ACTUALIZACION_CANDIDATO.md) conserva su procedencia. T013 entrega nuevo
candidato/paquete/manifiestos; pendientes T014 dictamen/expediente y T015 archivo/cierre. No se transfieren consentimientos
anteriores. D157 conserva la fuente principal pública tras el primer push; modo continuo D156 para v0.2.0,
fuera de P013. Owner/repo, visibilidad, identidad pública y acciones remotas siguen sin acordarse en esta fase;
ningún ensayo ni commit local autoriza push, CI remota, tag o publicación.
