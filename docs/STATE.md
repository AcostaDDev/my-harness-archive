# Estado — my_harness

Actualizado: 2026-10-25. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P011 cerradas. Primera versión
local completada en el alcance de D151/D153 y preparación pública archivada con expediente sin ejecutar (D181/D182).

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Formateo del perfil tras cada turno del ejecutor (D133). Codec de historial
  en formato 8 (lee 1–7).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0025_project_work_languages` (51 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
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
  su contrato y huellas. [Entrega](phase/P012-T010_FORMATEADOR_DECLARATIVO.md). Recorrido real posterior con
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

## Fase activa

**P012 — Validación real previa a la apertura pública**, planificada el 2026-10-24
([D183](DECISIONS.md#d183--p012-validación-real-previa-a-la-apertura-pública),
[criterios](ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública), [tareas](NEXT_STEPS.md)). T001 con
propuesta confirmada (D184), T008 corrige el preflight (D187) y T009 diagnostica el entorno del escritor (D192).
Wheel corregido `6efbd82` construido/verificado/instalado y preflight real aprobado (D188); acceso UI manual
conservado tras D189/D190. Primer B **COMMITTED** en `976b1d1`, reenvío idempotente acreditado y tarea
`b94eedef…` en **REVISION_LIMIT** con tres rutas vacías (D191); originales y diff conservados.

**Continuación T009 autorizada y ejecutada** (D193): fixture limpio `onboarding-b-t009`, venv offline,
copia TOML/presets/composición propios, PATH/TMPDIR explícitos; mismo wheel, SQLite y CLI **2.1.310/0.164.0**.
Preflight y ocho checks iniciales correctos. Registro/UI es/es, un turno Claude y doce borradores CAS aplicados;
**B2 COMMITTED** en `9808fd9`, con los 15 archivos originales intactos. Tarea **`f98b16d9…` REVISION_LIMIT**:
Codex implementa vista/tests/flujo; **13 tests pasan**, mypy y Django pasan, pero Ruff check (**E501 en dos líneas**)
y formato fallan. Revisor REVISE; cero correcciones, sin aceptación ni commit de tarea. No demuestra defecto del
producto ni la causa del truncamiento previo. Ambos resultados conservados sin reparar/revalidar/reintentar.
Consumo acumulado **Claude 7/12, Codex 2/3** (nuevo 3/1). Servicio detenido, **7 jobs DONE, 9 procesos STOPPED,
0 locks**; **8186 filas previas intactas** en contraste de copias SQLite/WAL/SHM.
[Resultado entonces parcial](phase/P012-T002_CONTINUACION_T009.md); T003–T007 pendientes, T003/T004 sin autorización.

**T010 completada offline** (D194), elegida por HITL: `local-config-8` habilita el formateador en perfiles
declarados, con autorización/rutas D133 y huellas congeladas. Sin cambio de motor, runner, datos o API;
v1–v7, detección CLI y recetas v2 conservadas. 28 regresiones nuevas y checks dirigidos correctos.
Sin build/instalación operativos ni nuevas llamadas; ambos intentos reales y su parada permanecen intactos.

**Continuación T002 tras T010 autorizada y detenida** (D195): [propuesta y ejecución](phase/P012-T002_PROPUESTA_T010.md),
wheel `a7d8b33` construido/verificado/instalado, clon documental B2 limpio y TOML v8 de hash aprobado. Ajuste
de trece modos del clon confirmado por HITL; 28 blobs/modos correctos. Preflight y ocho checks iniciales pasan,
migrate no-op. Servicio/login correctos; la UI oculta presets en v8 y detiene el tramo **antes del alta**.
Sin registro/fase/tarea o llamadas nuevas: Claude 7/12, Codex 2/3. Servicio parado, 7 DONE/9 STOPPED/0 locks,
**13.785 filas previas idénticas**, B/B2/diffs/configuraciones/distribuciones anteriores intactos.

**T011 completada offline** (D196): el selector compartido de registro/creación/actualización admite presets
v8, como el backend; aviso en/es actualizado. **8 regresiones de render React, 103 tests Node, tipos/build
correctos**. [Entrega y propuesta posterior](phase/P012-T011_PRESETS_UI_V8.md). Esa entrega no opera el producto;
la continuación real posterior se autoriza por separado conforme a D197/D198.

**T002 completada con evidencia acumulada** (D198; operación 2026-10-24, cierre documental 2026-10-25):
[propuesta autorizada](phase/P012-T002_PROPUESTA_T011.md) y [resultado/matriz](phase/P012-T002_RESULTADO_T011.md).
Wheel `500a783` construido/verificado/instalado en dist-t011/venv-t011; hash `f22521ff…acd3201`. Preflight,
ocho checks iniciales y migrate no-op correctos. UI v8 permite presets; p012-b-t010/P001 registrados,
dos commits documentales por UI y única tarea **`e3fa4ae6…` COMMITTED en `6f021211b307`**: plan Claude,
ejecución Codex, formateador sobre dos archivos (sin cambios), seis validaciones/**13 casos JUnit** y ACCEPT.
Un hallazgo low de referencia de línea conservado, cero correcciones. Claude **9/12**, Codex **3/3**;
servicio detenido, **11 DONE/12 STOPPED/0 locks**, puerto cerrado/clave eliminada. **13.785 filas previas idénticas**,
1.136 filas operativas nuevas; B/B2/diffs/TOML/distribuciones anteriores intactos. P001 del clon sigue ACTIVE.
La evidencia B/idempotencia conserva su procedencia D191/D193; no se repite ni repara ningún resultado anterior.

P011 sigue cerrada y archivada ([D182](DECISIONS.md#d182--cierre-documental-de-p011-y-preparación-pública-archivada),
[resumen](archive/phase-011/SUMMARY.md)). El paso 1 de su [expediente](archive/phase-011/P011_EXPEDIENTE_APERTURA.md)
se ejecutó el 2026-10-24: candidato regenerado en `$HOME/Documents/projects/my_harness_dist` (sin Git) con el
manifiesto aprobado `74cc9141…ea71`. Los pasos remotos quedan aplazados hasta cerrar P012, que preparará un candidato
y un expediente nuevos. Tras abrir, el repositorio público es la fuente principal (D157).

P010 conserva su cierre (D153) y P009 el suyo (D140); el Django hijo sigue con P001 CLOSED, cuatro tareas COMMITTED,
tag `p001` sobre `47a0557` y archivo en `3d105c6`, sin repetir operaciones ni comprobaciones de su estado.
Este repositorio sigue sin registrarse ni ejecutarse con el harness.

**T003 parcial, ejecutada y detenida** (D200/D201):
[resultado](phase/P012-T003_CHAT_BACKUP_REAL.md), instalación T011 conservada, dos turnos Claude ANSWERED
sobre HEAD 6f02121 y `/estado` sin modelo. Propuesta confirmada por UI/hash/versión con copia TOML
`supervisor=false`: P001-T002/run `d235e9d5…` QUEUED, cero intentos/preparaciones/locks y checkout intacto.
Backup/verificación/restauración/verificación correctos, 42 artefactos/13 runs; HTTP recupera run/diff/JUnit/
métricas idénticos y rechaza mutaciones con 409. La UI no ofrece página del run sin proyecto compuesto;
D040 define consulta API, y el guion había añadido UI. HITL **«Planificar vista UI Aparte»**: se mantiene T003
parcial y se añade T012 para implementar la vista offline antes de verificar la UI con consentimiento nuevo.
Parada origin inicial y reanudación nativa autorizada conservadas, sin cambiar guardias.
Consumo **2/3 Claude, 0/0 Codex**, dentro de dos horas; servicios detenidos, puertos cerrados/claves retiradas,
**13 DONE/1 QUEUED/14 STOPPED/0 locks**. **14.921 filas previas intactas**, 1.877 nuevas, 16.798 finales iguales
en bundle/restauración; B/B2/clon/diffs/configuraciones/distribuciones intactos. No reactivar esa base antes de revisar T004.

**T012 completada offline** (D202): [entrega y propuesta de consulta UI](phase/P012-T012_VISTA_CONSULTA.md),
[plan conservado](phase/P012-T012_PLAN_VISTA_CONSULTA.md). Señal `read_only_archive` desde la marca D040,
entrada por id y `/runs/:id` independiente; evidencia/diff/JUnit/jobs/intentos/eventos/métricas por run,
componentes compartidos, navegación de consulta en en/es sin workspace/acciones, pendientes o polling de ejecución.
Sin migración, checkout o cambios de guardias. **102 tests Python dirigidos**, regresiones React/router,
Node/tipos/build correctos; solo fixtures sintéticos, sin wheel operativo, servicio o llamadas nuevas.

**Siguiente:** consentimiento nuevo para la [continuación solo UI de T003](phase/P012-T012_VISTA_CONSULTA.md#4-propuesta-de-continuación-t003-solo-ui-sin-autorizar),
con código corregido, destinos nuevos y cero llamadas de modelos;
no repetir chat/aceptación/backup o consumir saldo. Informes anteriores conservados por bytes.
T004 sigue sin autorización y necesita propuesta de arranque que respete el job QUEUED (D199).
T002 finalizada, sin reparación/revalidación de sus dos fallos. Conservar todos los fixtures, diffs, historiales,
configuraciones y distribuciones. Sin nueva fase del Django de P009, tags, push o publicación. P012 sigue
abierta; baseline pública/candidato pendientes de T005.
