# Estado — my_harness

Actualizado: 2026-10-26. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

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

## Fase activa

**Sin fase activa ni sucesora definida.** P012 cerrada y archivada documentalmente el 2026-10-26
([D212](DECISIONS.md#d212--cierre-documental-de-p012-y-validación-real-archivada),
[resumen](archive/phase-012/SUMMARY.md), [revisión de cierre](archive/phase-012/REVIEW.md),
[registro](archive/phase-012/P012_CIERRE.md)). Originales congelados con manifiesto respecto de T006;
los estados parciales de esos snapshots conservan su procedencia.

El siguiente paso es la apertura que autorice el usuario sobre el
[expediente de P012](archive/phase-012/P012_EXPEDIENTE_APERTURA.md) y su
[suplemento de actualización](phase/2026-10-26_ACTUALIZACION_CANDIDATO.md): faltan owner/repo, visibilidad e identidad
pública. Candidato local `my_harness_dist` actualizado, sin Git; ninguna creación remota del candidato, push, CI remota,
visibilidad pública, tag o Release ejecutados. El expediente P011 permanece histórico y sustituido.
Después del primer push el repositorio público será la fuente principal (D157); este conserva la historia privada.
Modo continuo v0.2.0 posterior a la apertura, sin tareas definidas (D156);
[candidatas sin fase](ROADMAP.md#candidatas-sin-fase-asignada).

Este cierre es manual, separado del READY del producto y del cierre real del hijo TypeScript de T004.
Este repositorio sigue sin registrarse ni ejecutarse con el harness. Sin cambios de producto, modelos, API,
flujos, instalaciones, fixtures o configuración global; sin nuevos servicios, proveedores o permisos operativos.
