# P012-T012 — Plan de vista UI para copias de consulta

Fecha: **2026-10-25**. Base revisada: **`df1ed22`**. **Estado: planificada; sin implementar ni operar.**
HITL: el usuario elige **«Planificar vista UI Aparte»** ante las alternativas de cerrar T003 solo con API o
mantenerla parcial y planificar una vista independiente. Decisión
[D201](../DECISIONS.md#d201--p012-t012-vista-ui-de-consulta-planificada).
Antecedente: [resultado T003](P012-T003_CHAT_BACKUP_REAL.md#5-consulta-http-acreditada-y-límite-de-ui),
D040/D083/D144/D145/D199/D200. Contrato: [T012](../NEXT_STEPS.md#p012-t012--vista-ui-de-runs-en-copias-de-consulta).

## 1. Problema y resultado buscado

Una restauración conserva los runs, sus evidencias y métricas. La API de D040 permite leerlos por id,
sin disponer de los checkouts ni configurar proyectos. Sin embargo, `RunRedirect` solo navega a una URL
de proyecto y muestra un estado vacío cuando `project_id` es null. En T003 esto impide ver por UI la tarea
COMMITTED, su diff y sus JUnit aunque las lecturas HTTP sean correctas.

T012 añadirá una **vista de consulta independiente del registro** en la ruta existente **`/runs/:id`**:
identidad, estado guardado, commit, ciclos/diff, validaciones/JUnit, jobs, intentos, eventos y métricas del
run. La página de inicio de una copia permitirá introducir el id y abrirla; el id puede obtenerse del
manifiesto del bundle. No se añade un inventario global de runs ni un endpoint de búsqueda en esta tarea.
La interfaz identificará la copia como **solo consulta** y conservará los estados históricos tal como
están, incluidos QUEUED, ACTIVE o RECOVERY_REQUIRED: abrirla no significa reanudar ni confirmar parada.

T003 permanece **parcial**, con chat, confirmación sin ejecución y backup/consulta HTTP ya acreditados.
La implementación offline de T012 no completará por sí misma su criterio de UI; será necesario un recorrido
posterior con el wheel corregido, concretado y autorizado por separado.

## 2. Contrato propuesto

### Señal explícita del servicio

Añadir **`read_only_archive: bool`** a **`SupervisorRead`**, calculado por el servicio desde la marca
persistente que ya comprueba `is_read_only_archive`. Será true tanto en un backup consultable como en una
restauración marcada; false en una instalación ordinaria, incluido un servicio sin agentes/configuración o
con supervisor=false. No se infiere el modo desde `project_id=null`, listas vacías o ausencia de puertos.

Reutilizar **`GET /api/managed/supervisor`**; no añadir otra ruta ni modificar la marca, filas, esquema,
migraciones, codec o formato del bundle. Regenerar `frontend/openapi.json` y `frontend/src/api.generated.ts`
con los comandos existentes. Conservar sesión local, Host/Origin/CSRF y rechazo 409 de mutaciones de D040.

### Entrada, navegación y presentación

- Inicio de una copia: explicación breve de consulta de evidencia y campo **id de run** que abre `/runs/:id`
  mediante el router existente, con encoding y estados de recurso ausente/error. Ninguna ruta de disco se
  introduce o interpreta como destino de lectura. No se leen ni modifican los manifiestos desde el navegador.
- En `/runs/:id`, si la señal de copia es true, presentar la evidencia directamente, sin redirección a un
  proyecto ni `ProjectWorkspace`. Si es false, conservar la resolución canónica actual para proyectos
  configurados y el estado vacío de los runs sin proyecto. No crear ids de proyecto ficticios.
- Cabecera/sidebar de copia con contexto de consulta, entrada por id y estadísticas globales existentes.
  No montar formularios de alta, preferencias persistidas, fases, permisos, recuperación, ejecución, commit,
  exportación, chat o preparación. Una URL operativa directa mostrará un mensaje de consulta y enlace de
  vuelta. No leer ni ofrecer reenviar acciones pendientes guardadas por `ProjectWorkspace` en localStorage.
- Reutilizar la presentación de evidencia del run, diff paginado, `Tests`, originales JUnit y formatos de
  métricas. Extraer solo lo necesario para que la parte de lectura no dependa del workspace de acciones.
  `actions=[]` es una defensa adicional del servidor; la vista de copia nunca monta controles de escritura,
  recuperación o permisos aunque una respuesta sintética los anunciara.
- Mostrar raíz, fase y tarea como contexto histórico; usar texto donde no exista destino de consulta.
  Los enlaces de runs apuntan a `/runs/:id`. No enlazar páginas de proyecto inexistentes ni pedir el checkout.
  Idiomas visuales en/es con los catálogos y accesibilidad existentes.

### Evidencia y métricas

Consumir únicamente lecturas ya disponibles por id: detalle, jobs, intentos, eventos por cursor, ciclos,
diff por páginas, casos JUnit y original. Para consumo del run, reutilizar
**`GET /api/managed/metrics/attempts?run_id=…`**, con sus páginas y procedencia, sin `project_id` ni filtros
de tarea que exijan un proyecto configurado. Adaptar el componente de intentos/filtrado de Stats o extraer
su tabla; no calcular métricas alternativas a partir del historial ni mezclar runs con el mismo task_id.

Conservar ausencia de datos frente a cero, modelo solicitado/reportado, cobertura y coste equivalente API.
No añadir backfill, retención, lectura del checkout, recálculo de proyección o agregados nuevos. Los payloads
de evidencia y hashes deben coincidir con la API actual. D144/D145 siguen aplicándose: lecturas acotadas sobre
proyección, sin seleccionar ni decodificar `history_json`. Los detalles pesados permanecen bajo demanda.

El render de una copia no sondea estados guardados como si hubiera un escritor vivo. Lectura inicial,
paginación bajo demanda y recarga explícita bastan para un archivo inmutable; no cambiar los estados para
obtener ese comportamiento. No se rediseña la observación de runs operativos.

## 3. Alcance de implementación y paridad

Rutas previstas, ampliables dentro de la misma responsabilidad si la extracción compartida lo necesita:

- `src/harness_local/api/schemas.py`, `src/harness_local/services/managed_runtime.py`: señal de copia.
- `frontend/src/main.tsx`, `Shell.tsx`, `router.ts`, `navigation.tsx`, `ui.tsx`, `pages/Home.tsx`,
  `pages/Run.tsx`, `pages/Stats.tsx`, `i18n/{en,es}.json`; componentes de consulta/presentación nuevos bajo
  `frontend/src/` y estilos mínimos en `styles.css` si hacen falta. Reutilizar `Tests.tsx`, `Logs.tsx` y
  `metrics.ts` sin ampliar su acceso a archivos o comandos. No cambiar el contrato del workspace operativo.
- OpenAPI y tipos generados; `tests/product/test_backup.py`, pruebas dirigidas de runtime/API/proyecciones
  y `frontend/tests/**` con datos sintéticos. Sin dependencias nuevas ni cambios de locks.
- `docs/**`: entrega, estado/tareas/decisión; ARCHITECTURE §7 y SPECIFICATION F06/F16 al implementar,
  distinguiendo entonces consulta UI de las capacidades anteriores. Añadir un flujo de consulta
  `docs/flows/backup-consultation.md` y enlazarlo desde la lectura de run/arquitectura en la misma entrega.
  Sin cambios de modelos/migraciones: DDBB-DIAGRAM solo si la implementación llegara a necesitar un cambio
  de datos, lo que exigiría revisar este alcance antes de introducirlo.

Esta planificación no cambia código, API, documentos de capacidades implementadas ni flujos vivos.
README y baseline pública se actualizarán en T005 con la evidencia que finalmente se acredite.

## 4. Criterios de aceptación de T012

1. Señal de copia explícita y tipada desde la marca D040; true en copias y false en servicios ordinarios
   sin agentes o con supervisor=false. Sin carga de configuración, puertos, jobs o checkouts al consultarla.
2. Entrada por id desde inicio y URL `/runs/:id` directa/recargable en una copia. Run conocido visible sin
   proyecto/workspace; run desconocido con estado de recurso ausente, no una oferta de registro o recuperación.
3. Detalle/commit/estados históricos, ciclos y diff paginados con hash; validaciones, casos JUnit y descarga
   del original; jobs/intentos/eventos de solo lectura y consumo filtrado por run_id con procedencia.
   Soportar sin inventar evidencia un run sin ciclos, sin métricas, incompleto o con streams purgados/ausentes.
4. Nada de escritura o configuración en la vista ni en rutas operativas directas de una copia; no montar
   ProjectWorkspace/Permissions o sus reenvíos pendientes. Sin polling de ejecución sobre estados históricos;
   guardia 409, query_only y supervisor/puertos desactivados se mantienen como autoridad del producto.
5. Misma evidencia/hash en UI y API; lecturas acotadas D144/D145, sin codec/historial completo ni fuentes
   externas. Página disponible aunque el checkout sintético original no exista.
6. Modo normal conserva `/runs/:id` → URL canónica de proyecto y controles/CAS existentes; sin proyecto y
   sin marca conserva su comportamiento. El nuevo modo no se deduce de supervisor=false ni de ports_configured.
7. Regresiones offline, tipos/build y paridad documental correctos en en/es. Fuentes anteriores y resultados
   reales de T003 intactos; entrega no opera instalaciones privadas, no reconstruye/instala wheel operativo,
   abre servicios reales o consume agentes/modelos.
8. Entrega deja propuesta concreta de verificación posterior de T003 con base/hash del código corregido y
   efectos exactos, **cero llamadas de modelos** y consentimiento nuevo antes de build/instalación/servicio.
   No declarar T003 completa solo por pasar pruebas sintéticas de T012.

## 5. Validación futura

- Backend sintético: copias con estados variados y sin checkout, señal true/false, lectura íntegra y guardia
  409 sin cambios de filas ni activación de factories/supervisor. Reutilizar los tests de backup/proyección
  que rechazan reconstrucción o dependencia de originales. Ningún fixture procede del área privada T003.
- Frontend: routing y render React real con fixtures sintéticos en en/es, usando el helper TSX existente;
  evidencia de commit/diff/JUnit/métricas ausentes o presentes y ausencia de todos los controles de escritura.
  Incluir un caso con acciones anunciadas en los datos y otro con petición pendiente en almacenamiento:
  ninguno monta ni ejecuta el carril operativo. Verificar filtrado por run_id y paginación sin cargas de historial.
- Regeneración OpenAPI/tipos, tests Node completos, `npm --prefix frontend run check` y `build`; pytest
  dirigido a backup/runtime/API/proyecciones/métricas según los archivos modificados. No hay migración nueva.
- QA posterior con el wheel, navegador y copia real queda para continuación autorizada de T003. No lanzar
  smokes, agentes, servicio operativo o validaciones de la tarea QUEUED durante la implementación offline.

## 6. Secuencia y continuidad de T003

**Siguiente trabajo: implementar T012 offline**, con el contrato anterior y datos sintéticos. Después, preparar
la continuación T003 de **consulta UI solamente**: distribución corregida en destinos nuevos, verificación e
instalación offline y servicio 8025 sin config sobre la restauración conservada, con guardias de hashes/filas
antes/después. Concretar commit, hashes, rutas, comandos, tiempo y parada en esa propuesta antes del HITL.

La continuación no repetirá chat, `/estado`, aceptación, backup o restauración ya acreditados ni cambiará
sus resultados. No abrirá la base operativa con supervisor activo, ejecutará P001-T002 o consumirá el saldo
Claude. No retirará la marca, registrará proyectos o reescribirá la copia. Si la operación requiere otro
destino o efecto no contemplado, se explicitará antes de pedir su consentimiento.

T003 cerrará solo después de observar por UI los runs T002 con su diff, JUnit y métricas, mantener los dos
REVISION_LIMIT y la tarea QUEUED sin ejecución, y acreditar conservación/parada. La evidencia acumulada
mantendrá la procedencia de cada tramo; T004 conservará su propuesta/autorización separada y la guardia D199.
T005 depende también de esta corrección y de completar T003. Los informes/consentimientos anteriores son
evidencia fechada: D001–D200 y los dos documentos T003 se conservan sin reescribirlos.

## 7. Validación de la planificación

Contraste de solo lectura con D040/H5.2, D144/D145, D199/D200, SPECIFICATION F06/F16 y reglas de negocio,
ARCHITECTURE §§4/5/7/9, [lectura de runs](../flows/task-run.md#lectura-del-run-d144), router/workspace,
RunRedirect/RunPage/Home/Shell/Stats, contrato SupervisorRead, runtime y tests existentes. No se abre el área
privada ni se operan sus bases/fixtures. Sin implementación, suites de producto, frontend/build, proveedores,
servicios, wheel nuevo o nueva evidencia real en esta tarea documental.

Checks documentales correctos: parsers con **12 fases, 7 criterios P012, 12 tareas y 201 decisiones**;
**626 enlaces/anclas relativos** en los cinco Markdown de la entrega; presupuestos STATE/base/NEXT_STEPS
**16.992/24.576**, **9.171/12.288** y **33.276/49.152 bytes**. D001–D200 y ambos artefactos T003 conservados
por bytes. Diff revisado y `git diff --check` correcto; solo documentos privados de planificación modificados.
