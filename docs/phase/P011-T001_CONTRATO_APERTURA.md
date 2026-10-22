# P011-T001 — Contrato de apertura pública

Fecha: 2026-10-22. Base inspeccionada: `2730f54` (checkout limpio al comenzar).
**Estado: diseño completado; producto sin modificar.** Decisión [D159](../DECISIONS.md#d159--p011-t001-contrato-de-idiomas-fuentes-y-corte-público).
[Inventario por archivo](P011-T001_INVENTARIO.md), [tarea](../NEXT_STEPS.md#p011-t001--inventario-y-contrato-de-la-apertura-pública),
[plan](P011_PLAN_APERTURA_PUBLICA.md). Aplica D154–D158, conservando D027/D088/D119/D143/D151.

## 1. Alcance y evidencia

Esta entrega fija contratos para T002–T019. No traduce el producto, cambia modelos/migraciones, retira funciones,
crea un candidato ni acredita privacidad, licencia, compatibilidad CLI o primer uso. Los diagramas vigentes siguen
describiendo el código actual; su paridad se actualiza al implementar, no dibujando este diseño como entregado.
La petición actual autoriza terminar T001 y su commit local en inglés. No autoriza otra tarea, proveedores,
servicios, instalaciones, publicación ni cambios de configuración del equipo.

Se contrastaron STATE/NEXT_STEPS, ROADMAP P011, SPECIFICATION §§4–10/13, ARCHITECTURE §§3–9/13,
DECISIONS (índice y precedentes citados), DDBB-DIAGRAM y los flujos legacy/incorporación/preparación.
La evidencia es lectura estática del árbol rastreado: AST/tokenización Python, búsquedas con y sin tildes,
esquemas de salida, rutas, imports, lectores de formatos y hashes de archivos. No se importó ni ejecutó el producto.
No se leyeron runs operativos, configuración privada, ReferenceProject ni el hijo de P009. Los archivos de fases cerradas
solo se enumeraron para delimitar la exclusión pública; no se reauditan ni se reescriben.

Hallazgos que condicionan el diseño:

- No hay `ui_language`, `default_work_language` o `work_language` en la persistencia/configuración actuales.
  La sesión HTTP es efímera (`api/session.py`); no sirve de autoridad duradera de preferencias.
- `core/engine/prompts.py::output_schema` mezcla prosa y documentos en una misma respuesta. `render_attempt`
  sella variables, plantilla, esquema, instrucciones de proyecto y texto renderizado. `cli_agents.py` envía el
  mismo prompt por stdin a ambos proveedores; el esquema tipado de Claude procede del snapshot.
- Los parsers ya tienen alias ingleses/españoles: `planning.FIELD_NAMES`, `SHARED_HEADING`,
  `documents.ROADMAP_FIELDS`, `DECISION_STATUS`, `BASE_HEADING`. La generación mecánica sigue mayormente en español.
- `recipes/django.py::fingerprint` y `recipes/typescript_web.py::fingerprint` incluyen `Path(__file__).read_text()`,
  scaffold/manifiesto y `asdict(profile())`. Conservar solo el número de receta no conserva su identidad.
- `api/app.py` instancia `LegacyObserver` y escanea al arrancar una base normal. Eliminar enlaces del navegador
  no elimina la observación. También existen rutas de simulación H0 propias, independientes del harness anterior.
- B hereda `ImportRepository`, importa helpers de `import_commit.py` y `_blobs` de `adapters/project_import.py`;
  preparación también importa guardias de ese adaptador. `import_commit` es un propósito compartido.

## 2. Autoridad, persistencia y controles de idioma

La unidad de preferencias es una instalación/base SQLite local de un operador. Varias ventanas del mismo
servicio comparten el visual; bases distintas son instalaciones independientes. No hay preferencia visual por
proyecto, navegador, proveedor o conversación, ni selección automática desde el idioma de sus textos.

| Dato | Persistencia diseñada | Alta y mutación | Propietaria |
|---|---|---|---|
| `ui_language` | Nueva fila singleton de preferencias del producto en SQLite, enum `en`/`es`, inicial `en` | Mutable con versión esperada y evento de cambio | T007 |
| `default_work_language` | Misma fila, enum `en`/`es`, inicial `en` | Mutable; inicializa selecciones futuras, nunca actualiza proyectos | T007 |
| `work_language` | Asociación duradera por identidad/raíz canónica de proyecto, con valor, procedencia y confirmación | Elegido una vez al alta; solo lectura después | T008 |
| Par efectivo | Snapshot `language-context-1` del job/turno y de cada intento | Inmutable; fuente y versiones de preferencias/proyecto incluidas | T007/T008 |

La asociación de trabajo debe cubrir tanto registros SQLite como proyectos declarados directamente en TOML,
sin convertir la fila de preferencias en un catálogo de proyectos. T008 añadirá una asociación única por raíz
canónica (también para TOML), vinculada al registro cuando exista. La baja/reapertura o el cambio de id, perfil,
composición o agentes no permiten volver a elegir trabajo para la misma identidad. No se añade `ui_language`
a `RegisteredProjectRow`, `ProjectProfile` ni al TOML. La migración física se numerará al implementarse;
T007/T008 actualizarán metadata, Alembic, DDBB-DIAGRAM, backup y restauración en sus entregas.

Precedencia y confirmación:

1. La UI carga preferencias del servicio. En crear/incorporar, presenta una selección explícita de trabajo
   inicializada desde el default leído; el cuerpo enviado contiene el valor elegido y su procedencia/versiones.
2. La vista previa sella trabajo, identidad y procedencia dentro de su hash; confirmar ese hash crea la asociación
   inmutable en la misma transacción de admisión del alta. La definición/incorporación posterior usa ese trabajo.
   El resumen de aceptación documental también lo incluye, sin ofrecer volver a seleccionarlo.
3. Cambiar un default entre vista previa y confirmación no sustituye el valor elegido: se confirma ese valor
   exacto o, si cambió otro dato que invalida la vista previa, se pide otra. No se aplica un default silencioso.
4. Para proyectos ya asociados manda SQLite. Un TOML que declare otro trabajo bloquea la composición con un
   diagnóstico de inmutabilidad; no sobrescribe SQLite ni produce una nueva identidad para el mismo checkout.

T008 introducirá `local-config-6` para declarar explícitamente `[[projects]].work_language` y seleccionar las
recetas nuevas de §5. Los formatos 1–5 conservarán lectura e identidades originales; no se insertará un campo en
su serialización congelada. Nuevas altas desde ellos necesitan confirmación explícita de trabajo en SQLite;
no se deduce del contenido ni se escribe TOML desde la UI. La versión 6 conserva los techos de autorización v5.
La carga de configuración no invoca CLI ni crea asociaciones de trabajo por su cuenta.

Controles API/UI previstos (nombres nuevos; no son endpoints disponibles hoy):

- `GET /api/managed/preferences` devuelve formato, versión y ambos defaults; `PUT` exige sesión, guardia local,
  CSRF, `expected_version`, ambos enums válidos e idempotencia auditable. Conflicto de versión → 409.
- Las solicitudes de registro/creación y sus vistas previas/confirmaciones llevan `work_language`; los endpoints
  de actualización de proyecto lo excluyen. Un intento de cambiarlo, incluso mediante reapertura o TOML,
  devuelve conflicto `work_language_immutable`. Los campos de entrada desconocidos no se ignoran para eludirlo.
- Una pantalla global accesible contiene ambos ajustes; los ajustes de proyecto muestran trabajo como texto.
  Todas las pestañas refrescan preferencias al recuperar foco y al consultar sesión/estado. Una respuesta de
  admisión devuelve el par realmente congelado aunque la pestaña estuviera desactualizada.
- API y OpenAPI/tipos generados se actualizan juntos. No se editan tipos derivados a mano.

Compatibilidad de instalaciones anteriores:

- Migración de esquema con servicio detenido y copia previa D150: preferencias nuevas `en/en`, sin traducir
  datos antiguos. Los proyectos previos quedan **sin trabajo confirmado**; no se les asigna español por detectar
  tildes ni inglés por el default. Lecturas históricas siguen disponibles.
- Antes de futuras operaciones que generen trabajo o invoquen un agente, una vista previa de migración por
  proyecto pide elegir `en`/`es`, muestra que los archivos existentes se conservan y exige hash, motivo y CAS.
  Solo esa transición de ausente → valor es válida; después se aplica la misma inmutabilidad. No es cambio de
  idioma de un proyecto ya asociado. Si hay trabajo pendiente o locks, primero se resuelve su recuperación.
- Jobs/intentos anteriores sin par no reciben campos inventados. Conservan bytes y procedencia antigua; una
  incompatibilidad de versión los pone en cuarentena antes de invocar/escribir. Para continuar trabajo futuro
  se resuelve explícitamente el job y se admite una nueva operación con trabajo confirmado. Una intención
  determinista ya sellada solo puede conciliar sus bytes originales, sin regenerarlos ni llamar al agente.
- Codec/historial 1–8, catálogos, planes, recibos y snapshots antiguos siguen legibles. Si la representación nueva
  necesita otra versión del codec/contexto, se añade un lector/escritor versionado; ausencia significa
  «no registrado», nunca un idioma inferido. Backup conserva también esa ausencia.

## 3. Catálogos, fallback y formatos

Se elige una solución mínima propia: catálogos JSON UTF-8 por ámbito (`ui` y mensajes del servicio), archivos
`en.json`/`es.json`, sin dependencias npm/Python nuevas y sin `.po`. React usa un contexto/proveedor con claves
tipadas a partir de la base inglesa; Python un lector empaquetado con biblioteca estándar. Es una decisión de
dependencias para T007, no la incorporación de archivos en esta entrega.
Dos idiomas, interpolación restringida y plurales/formatos ya disponibles en el navegador no justifican añadir
un runtime de traducción y una cadena de compilación gettext a React/Python. JSON permite comprobar cobertura
y empaquetar recursos con las herramientas existentes; ampliar idiomas o reglas requerirá revisar esta decisión.

Cada clave expresa un mensaje completo. Los parámetros son nombres simples (`{project}`, `{count}`), nunca
expresiones evaluables, HTML ni fragmentos de otra traducción. Se comprueba igualdad de claves/parámetros y de
variantes plurales. Texto React escapado; errores API se renderizan como texto. No se pasa un mensaje traducido
a `dangerouslySetInnerHTML`, Markdown o Mermaid. Los textos de accesibilidad usan el mismo catálogo.

La API transmite códigos estables y parámetros estructurados; `diagnostic` humano puede localizarse sin cambiar
estado HTTP, claves JSON, enums o evidencia. Los errores propios de Pydantic/FastAPI se mapean por código, no
traduciendo por reemplazo un mensaje de tercero. Mensajes ajenos/raw quedan identificados y conservan su original.
Un error histórico persistido se muestra como original, con etiqueta de estado localizada separada. Los eventos
nuevos pueden guardar clave/parámetros y texto/idioma emitidos; nunca se traduce un campo libre a posteriori.

El visual efectivo de las operaciones del servicio procede de SQLite. La CLI offline acepta `--ui-language en|es`
para esa invocación; en su ausencia usa preferencias de la base cuando la orden ya abre una, o `en` para órdenes
sin base/sin acceso a ella. Este override no guarda preferencias ni afecta jobs admitidos. API no acepta un header
que suplante al visual global. Ni `LANG`, `Accept-Language` ni localStorage modifican la autoridad del servicio.
Antes de autenticar/cargar preferencias, el shell usa inglés; cualquier caché de navegador es solo provisional.

| Situación | Resultado diseñado |
|---|---|
| Preferencias todavía ausentes en base nueva | `en/en`; inicialización mediante migración/repositorio, no desde un GET de solo lectura |
| Valor inválido en una escritura explícita | 422/API o error de argumentos/CLI; sin persistir ni normalizar silenciosamente |
| Locale ausente/corrupto en lectura o caché | UI muestra `en`, avisa; no repara SQLite con un GET; nueva admisión bloquea si su autoridad está corrupta |
| Clave/traducción ausente | Fallback inglés; si falta también la base, etiqueta técnica de clave y diagnóstico; cobertura debe impedirlo en release |
| Interpolación incompleta | Diagnóstico de catálogo, sin revelar datos ajenos ni ejecutar plantillas |
| Backup restaurado de consulta | Lee preferencias; no las modifica ni admite jobs |

Para cantidades/fechas del navegador: `Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.PluralRules`, locales
explícitos `en`/`es`, variantes `one`/`other` para los dos idiomas. El backend conserva números, instantes ISO/UTC,
moneda y unidades técnicas en forma estructurada; no modifica `locale` global del proceso. Python selecciona
`one` para 1 y `other` en el resto de los conteos enteros; porcentajes/duraciones monetarias se presentan desde
esos datos en cliente o con formatos explícitos probados, sin depender del sistema operativo. No se traducen
hashes, ids, rutas, comandos, URLs, versiones, keywords o salida capturada de herramientas.

## 4. Congelación, concurrencia y salida estructurada

El par se lee y persiste **en la transacción que admite cada job/turno**, antes de reservarlo para el supervisor.
El contrato `language-context-1` incluye `ui_language`, `work_language`, versión del contrato y procedencia:
versión de preferencias visuales, identidad/confirmación del trabajo y origen de la selección. Se incorpora al
request/contexto congelado, versiones y snapshot de prompt, con sus hashes. El worker nunca vuelve a consultar
el visual mutable para reconstruir ese prompt. Se mantiene fuera del hash de composición/perfil que invalidaría
un proyecto por cambiar el visual; trabajo sí pertenece a su identidad de contexto.

El contexto estable del run conserva trabajo, no una preferencia visual mutable. El par de cada operación vive
en su request/snapshot de job y en el snapshot del intento; no se cambia `RunHistory.context_json` al cambiar el
visual. Así se preserva la igualdad actual request/run de ese contexto estable (`storage/managed.py::agent_started`),
sin impedir que una nueva acción sobre el mismo run capture otro visual. T008 versionará los campos de request
necesarios y su serialización; un lector antiguo no convierte un snapshot ausente en `en/en`.

| Operación | Fuente del par |
|---|---|
| Nueva tarea, check, reconciliación, edición/exportación/cierre o preparación | Visual al admitir la operación y trabajo del proyecto; textos técnicos deterministas usan trabajo |
| Nuevo turno de chat/definición/planificación/incorporación B | Visual al admitir ese turno y trabajo ya elegido; no hereda el visual del primer turno |
| Intentos/revisiones/reanudación del mismo job; repetición de Idempotency-Key | El par sellado del job original; se devuelve el mismo resultado, sin recapturar preferencias |
| Una nueva acción confirmada sobre un resultado anterior | Nuevo job captura visual actual; conserva intactos documentos, contrato y resultado que confirma |
| Lote desatendido | Cada job nuevo captura el visual al admitirse; jobs ya en cola no cambian |
| Recuperación de una intención de commit/preparación | Intención, par y bytes sellados; no vuelve a producir prosa o manifiestos |

Ejemplo obligatorio de concurrencia: admitir A con `es/en`, cambiar visual a `en`, admitir B en la misma
conversación. A y sus intentos siguen `es/en`; B usa `en/en`. La UI ya puede verse en inglés y mostrar la respuesta
española original de A. Cambiar el default de trabajo a `es` no modifica ninguno. Capturar preferencias y alta
en transacciones evita que una ventana sobrescriba una elección por otra concurrente.

Mapa de campos de `prompts.output_schema` y `cli_agents.SHAPES` (V = visual congelado; W = trabajo; T = técnico
literal/original). Una respuesta puede contener V y W. Este mapa tiene prioridad sobre una instrucción genérica
«responde en español»; no se traduce la respuesta completa tras recibirla.

| Rol | V: explicación/preguntas humanas | W: artefactos que alimentan trabajo | T: valores que no se traducen |
|---|---|---|---|
| `bootstrap` (solo compatibilidad antigua) | `summary`, `pending_decisions[]` | `requirements[]`, `alternatives[]` | Esquema/ids; no reactivar creación v1 |
| `planner` | `executor_selection.reason` | `title`, `objective`, `executor_prompt`, `acceptance_criteria[]` y restante prosa del contrato normalizado | `task_id`, `phase_id`, globs, `validation_commands[]`, selección model/effort |
| `executor` | `result` | `decision_proposals[].title/decision/rationale`, archivos/código/comentarios escritos | Rutas, identificadores públicos, herramientas y salidas originales |
| `reviewer` | `findings[].problem`, `blocking_questions[]`, `executor_selection.reason` | `next_prompt`, `decision_proposals[].title/decision/rationale` | `verdict`, task id, severity/category/file, `scope_grants` tipados de permisos |
| `phase` | `summary`, `required_actions[]`, `blocking_questions[]`, `exit_criteria_results[].evidence` | Ningún documento nuevo en esta respuesta | `phase_id`, `verdict`, `passed`, `criterion` copiado exactamente del criterio congelado |
| `chat` | `answer`, `proposals[].rationale` | `proposals[].title/objective/scope/acceptance_criteria[]` | `references[]`, comandos dentro de `proposals[].validation[]` |
| `definition` (cero/B) | `answer`, `questions[].text`, `drafts[].reason`, `pending[]` | `drafts[].content` completo | `drafts[].path`, `questions[].blocking` |
| `planning` | `answer`, `questions[].text`, `plan.reason`, `pending[]` | `plan.content` (NEXT_STEPS) | `questions[].blocking`, plan nulo, rutas/ids |

En `proposals[].validation[]`, las instrucciones de validación en prosa usan W; comandos literales permanecen T.
`scope_grants` no es prosa libre: si una forma admitida incorpora una justificación humana, esta usa V y el resto
conserva el vocabulario del permiso. Un `answer`/finding puede citar código, logs o criterios originales de otro
idioma sin traducir la cita. El lenguaje natural no se valida con heurísticas que rechacen nombres de código.
Esquemas futuros deberán asignar cada campo a V/W/T antes de añadirse; no convertir explicaciones V directamente
en documentos W. T009 actualizará también la generación determinista de mensajes/commits/bloques y resúmenes.

Inyección controlada común a ambos proveedores:

- El motor construye un bloque tipado de instrucciones de `language-context-1` con nombres canónicos de idioma,
  regla V/W/T, permiso de leer fuentes mixtas y prohibición de alterar protocolos; no concatena texto del usuario
  como una directiva. El bloque se sella fuera de las variables editables y se añade en `render_attempt`, junto
  al esquema del motor, antes del transporte. Las plantillas base nuevas siguen en inglés y son editables.
- Codex lo recibe por el prompt de stdin de `exec ... -`; Claude por el prompt de stdin de `--print` ya usado.
  No se inventa `--language`, ni un system prompt común, ni se cambian permisos, memoria, herramientas o confianza.
  El adaptador conserva el snapshot y el hash de los bytes realmente enviados, incluida su envoltura de forma.
- El par no puede ser sustituido por una variable de plantilla personalizada. Cambiar su texto crea una versión
  nueva del catálogo, no cambia el pasado. Los prompts personalizados se preservan; las instrucciones del motor
  declaran su precedencia sobre indicaciones lingüísticas contradictorias. Un contexto/par inválido o un render
  incompatible bloquea antes de efectos; no se promete detectar semánticamente toda contradicción en prosa libre.

## 5. Fuentes congeladas, recetas, documentos y compatibilidad

| Fuente | Contrato de tratamiento | Tarea |
|---|---|---|
| `recipes/django.py`, `typescript_web.py` v1 y recursos Django asociados | Conservar bytes, rutas, perfil efectivo y cálculo de huella v1 para recibos/planes antiguos; excepción explícita al inglés del código histórico | T004 |
| Recetas nuevas | Añadir `django-recipe-2` y `typescript-web-recipe-2`, con fuente mantenida inglesa y scaffold técnico parametrizado por W; nueva selección explícita en v6, nunca sustituir v1 bajo su id | T004 base; T008 binding; T009 generación |
| Plan/recibo v1 ya emitido | Leer/verificar el original y conciliar la misma intención cuando sea seguro; sin recalcular con v2 ni reinstalar por traducción | T004/T008 |
| Altas nuevas con recetas | Usar v2 y W congelado; si la configuración solo ofrece v1, bloquear con instrucción de actualización explícita antes de preparar | T008/T009 |
| `templates/*.md` y catálogo persistido | Nueva plantilla → hash/id nuevo por contenido; lectores admiten catálogos anteriores, incluida la entrada retirada de A solo como dato | T009/T019 |
| `context_json`, historial/requests/prompts y proyección de runs | Versionar formas nuevas y leer las antiguas sin inyectar valores ni recalcular fingerprints originales | T007/T008 |
| Migraciones 0001–0023 | Conservar ids, orden, DDL, semántica y datos; T004 puede traducir comentarios fuera de literales/operaciones congelados | T004/T019 |
| Alias D088/parsing bilingüe | Conservar español y su equivalencia inglesa; la generación elige W, el parser acepta ambos sin depender de UI | T009 |
| Paths, marcadores y códigos | `docs/phase`, `archive/phase-NNN`, nombres de documentos, `PNNN`, `DNNN` y `harness-local:managed-*` permanecen | T009/T014 |
| ADR y fases anteriores, snapshots, fixtures de compatibilidad/streams | No traducir ni reescribir por cosmética; conservar originales/expectativas, añadir casos nuevos separados | T006/T009/T014 |
| Documentación viva privada | Mantener contexto durante P011; la baseline pública se redacta de nuevo en inglés, no se copia el archivo privado ni se borra de este checkout | T014 |

La v2 de receta incluye versión, trabajo, manifiesto, perfil y productor en la identidad de composición/plan/recibo;
visual no entra en el scaffold ni en su huella. Los labels humanos del plan se capturan en V sin mutar el
manifiesto W. El idioma funcional de la app hija (p. ej. `LANGUAGE_CODE` de Django o `<html lang>`) es un requisito
del producto hijo, no se deriva de `ui_language` ni se impone de `work_language`; los defaults funcionales
existentes se conservan salvo decisión explícita del hijo. Los textos técnicos/comentarios del scaffold v2 sí
siguen W. No se cambian versiones de paquetes, permisos, comandos o manifiestos protegidos por traducirlos.

Mover un archivo v1 cambia `__file__` pero el cálculo lee sus bytes: T004 debe demostrar huellas antiguas idénticas,
incluidas las dependencias transitivas `profile()`/`asdict`, antes de cualquier reubicación. Preferencia: dejar
los dos módulos v1 en su ruta y añadir los nuevos. No añadir campos lingüísticos a `ProjectProfile` que cambien
su `asdict` histórico. Catálogos antiguos que contienen `import-project` son legibles como evidencia, pero
ningún cargador/despachador puede volver a invocar esa plantilla tras T019.

Anclas: al traducir encabezados vivos, inventariar enlaces entrantes y conservar anclas explícitas cuando ayuden;
los enlaces canónicos nuevos usan inglés. Nunca editar documentos archivados para reparar un enlace creado por
una traducción posterior: conservar destino/alias o explicar su procedencia en la guía nueva. La baseline pública
no depende de anclas privadas. Mantener `Status:`/`Estado:`, `Objective:`/`Objetivo:`, `Exit criteria:`/`Criterios de
salida:`, `Shared`/`Restricciones compartidas`, `Accumulated baseline`/`Base acumulada`, límites STATE 24 KiB/base
12 KiB/NEXT_STEPS 48 KiB e instrucciones 60/15 líneas y 32 KiB. Inventario, contrato y evidencias van en `phase/`,
no se expanden los presupuestos para alojarlos en STATE.

Hashes estáticos de las fuentes v1 en esta base (no son el resultado de `fingerprint()`):

| Archivo congelado v1 | SHA-256 de los bytes |
|---|---|
| `src/harness_local/recipes/django-packages.json` | `4c73e05b05cd14ac38284341e42ff3e39938ec4055e9c91f0baf4c6b3942d9e8` |
| `src/harness_local/recipes/django-requirements.lock` | `0f2ce9afc90274a6da1b6c1d8b10cc62d6f530dd0b1f1c8c95609fd27d313c1b` |
| `src/harness_local/recipes/django.py` | `95b7e804503e7bfa2535a26ec0aff95d55c9b57ef75a256d65742838b4251dad` |
| `src/harness_local/recipes/typescript_web.py` | `3ca5c7d15fcdb9fc0b209c4d35aa15c2e0b57af2bd7f3fd3316f4c80d83f8571` |

## 6. Retirada legacy/A: frontera de código y datos

T019 no borra por nombre. El inventario de imports muestra estas fronteras:

| Área y archivos | Disposición diseñada | Dependencias/regresión a conservar |
|---|---|---|
| `api/legacy.py`, `api/events.py`, `services/observation.py`, `storage/legacy.py`, `observation.py`, `navigation.py`, `adapters/legacy.py`, `evidence.py`, `core/legacy.py`, `core/evidence.py` | Retirar lectores/servicios/índice/navegación/SSE operativos exclusivos; extraer antes utilidades de integridad/ids necesarias | Backup y guardia de instalaciones antiguas no deben importar el lector/indexador eliminado |
| `core/project_import.py`, `project_normalization.py`, `engine/import_conversation.py`, `storage/import_drafts.py`, `templates/import-project.md` | Retirar A y sus borradores/normalización/conversación | Lectura de registros originales como datos; sin ejecutar un catálogo antiguo |
| `adapters/project_import.py` | Extraer `_blobs`, guardias de filtros/submódulos/objetos a infraestructura Git común; retirar inventario A | `adapters/project_onboarding.py`, `storage/onboarding_commit.py`, `storage/project_import.py`, `services/project_preparation.py`, `chat_snapshot.py`/`local_git.py` |
| `engine/import_commit.py`, `storage/project_import.py` | Separar preview A del escritor/commit/adopción común; conservar propósito `import_commit` y tabla | B hereda `ImportRepository` y usa `adopt_documents`, `check_destinations`, `preview_tree`, `seal`, `execute`; no cambiar intenciones históricas |
| `core/migration.py`, `adapters/migration.py`, `storage/migration.py`, `services/migration.py` | Retirar activar/revertir/importar; extraer guardia mínima para proyectos ya gestionados bajo D027 | `storage/managed.py`, `services/managed.py`, `adapters/git.py` y marcador/intenciones; no confundir con `storage/migrate.py` (Alembic) |
| `api/app.py`, `api/managed.py`, `schemas.py`, `services/managed_runtime.py`, `cli.py`, `launcher.py` | No crear observer ni hacer scan al arrancar; retirar router/API/CLI legacy, activación y rama `project_import` | Sesión/CSRF, supervisor, salud SQLite, jobs B/cero, migración de base y diagnósticos gestionados |
| `frontend/src/legacy.tsx`, ramas de `main.tsx`, `router.ts`, `Shell.tsx`, `pages/Home.tsx`, `Project.tsx`, `Planning.tsx`, `api.ts`, `managed-api.ts` | Retirar visor, enlace, activación y modo A; revisar `api.ts` compartido antes de borrar | `ImportPage flow="onboarding"`, registro/creación, seguimiento por cursor de gestionados, sesión y clientes compartidos |
| Modelos/esquema/backup, migraciones 0001–0023 | Mantener tablas, FKs y datos; compatibilidad de lectura y artefactos de backup sin ejecutar lectores retirados | Historial propio, métricas/proyección, recibos, evidencia y restauración de consulta |
| `core/simulation.py`, `adapters/fake.py`, `storage/repository.py`, rutas `/api/simulations` | Esqueleto sintético propio H0, independiente de legacy; conservar fuera de la retirada D155 | Sus datos no son runs/tareas gestionados ni otra vía de alta de proyecto. Tampoco confundirlo con `adapters/engine_fake.py`; pruebas sintéticas propias conservadas |
| Tests/fixtures legacy, A y simulación | Retirar solo los exclusivos; separar fixtures sintéticos de actualización, guardias, backup y B antes de borrar | Tests de ausencia, cero/B, CAS, permisos, objetos locales, recuperación e historial propio |

Superficies que deben dejar de ejecutar efectos: `/legacy`, `/api/legacy/**` (incluidos `/updates`, `/events`,
observación, contenido/entries), comandos `legacy-import`/`legacy-summary`, acciones managed de activación/
reversión y `/import`/conversación `kind="project_import"`. Eliminar sus contratos
OpenAPI y tipos; URL UI antigua → página de ruta retirada/no encontrada, API → 404 tras guardias, comando antiguo
→ error de argumentos sin abrir datos. No mantener wrappers ejecutables, flags de reactivación ni redirect a A/B.
Actualizar SPECIFICATION F03/F05/§8/criterios 1/11/13 y los flujos actuales en T019; T013 audita su resultado.

Disposición no destructiva en instalaciones anteriores:

1. Conservar `legacy_sources`, `legacy_runs`, `legacy_artifacts`, `legacy_events`, `simulations` y
   `managed_activations`; conservar campos `activation_id` y las revisiones que los crearon. `watch_enabled=true`
   antiguo queda como dato inerte: ningún observer lo consume ni se cambia para simular una baja autorizada.
2. Conservar `planning_conversations/turns/drafts` con `kind=project_import`, sus fuentes, requests y prompts;
   `project_imports` conserva también B. Clasificar por conversación y preview (`flow="onboarding"`), nunca
   por `purpose=import_commit` solamente. Discrepancia, fuente ausente o tipo desconocido → cuarentena.
3. Antes de despachar, trabajos A/legacy pendientes se rechazan/ponen en cuarentena con diagnóstico de retirada;
   no se reinterpretan como B ni se concilian escribiendo sus intenciones. Jobs ACTIVE/lease vencido requieren
   primero recuperación y declaración de escritor detenido, sin señalar PIDs persistidos. La resolución explícita
   puede cancelar/cerrar el job y liberar su lock tras verificar que no hay propietario vivo; guarda motivo y
   evento, no elimina filas/archivos/intenciones. B pendiente sigue el camino de recuperación normal.
4. Activaciones PREPARING/REVERTING no se completan ni revierten automáticamente. Bloquean nuevas escrituras
   de ese checkout y se conservan para resolución manual explícita fuera del flujo retirado. Una activación ACTIVE
   propia puede seguir protegiendo runs **gestionados** mediante guardia de compatibilidad: fila/marcador
   idénticos, snapshot/manifiesto íntegros y ausencia de deriva de los archivos antiguos antes de efectos.
   Extraer la comprobación mínima de integridad, sin reconstruir/indexar/observar runs ni exponer visor/activación.
   Marcador ajeno, `.harness/runs` sin autoridad o deriva sigue bloqueando; no se retira el marcador para eludirla.
5. Historiales gestionados completados siguen accesibles por sus vistas normales; los datos exclusivamente
   legacy permanecen en base/backup sin visor de producto. Backup captura y verifica artefactos ya referenciados
   usando manifiestos/rutas sellados, no reimporta la raíz externa ni crea un índice. Restaurar es solo consulta,
   nunca arranca un observer ni reanuda una operación retirada. Revisiones antiguas requieren actualización
   explícita D150; no se promete abrir cualquier backup antiguo con un esquema distinto.

La guardia mínima y los lectores de datos son compatibilidad de my_harness, no una tercera vía de alta.
No autoriza nuevas activaciones, migraciones A o soporte a repositorios v1/v2 que requieran normalización.
Registro/reapertura de un proyecto que ya cumple D088 sigue siendo normal; una fuente B que requiera A se rechaza.
La comparación con manifiestos no ofrece aislamiento del sistema operativo ni observación continua entre checks.

## 7. Setup, licencia, privacidad y distribución: inventario de brechas

| Superficie constatada | Brecha/tratamiento pendiente | Responsable/evidencia prevista |
|---|---|---|
| Sin LICENSE/NOTICE/CONTRIBUTING/SECURITY ni `.github/` rastreados en la base | Usuario decide licencia y titularidad antes de redactar términos; inventario de licencias/atribuciones transitivas y contactos reales | T002; decisión humana pendiente allí |
| `pyproject.toml`/`frontend/package.json`: 0.1.0, descripción española, sin licencia declarada | Metadatos coherentes, recursos/catálogos y wheel/sdist; versión candidata explícita distinta de la reserva v0.2.0 | T005/T015; elección de versión pendiente |
| `uv.lock`, `frontend/package-lock.json`, locks/manifiestos de recetas | Conservar hashes/procedencia; revisar términos de dependencias/recursos; no confundir datos técnicos con prosa traducible | T002/T015 |
| `.gitignore` excluye `.local`, venv, estado, `.env`, cachés/build | No prueba ausencia en árbol ni historia; auditar rastreados e historial alcanzable del origen sin copiar hallazgos sensibles | T002, informe saneado con cobertura/límites |
| README enlaza archivo privado y todavía dice que no hay sucesora | Se sustituirá la baseline pública, con estado real y enlaces autónomos; no corregir mediante publicar el archivo privado | T014 |
| README/build requieren cachés pobladas; TOML de ejemplo v4 con dos proveedores/proyecto ficticio | Documentar primera descarga, auth propia, ejemplo mínimo de un proveedor, v6 y separación build/servicio/hijo | T014/T016 |
| `scripts/dev` migra/arranca servicios; `check_distribution.py` prepara recorridos | No invocarlos como checks documentales; plan de ensayo sintético previo en T016 | T015/T016 |
| `examples/first_use`, `provider_matrix` y `docs/archive`, `docs/phase` | Evidencia/guiones privados e históricos; excluir del corte inicial, sin reescribirlos para publicarlos | T002/T014/T015 |
| Código/fixtures pueden contener rutas personales, modelos, DNNN o links al archivo | Auditar referencias también fuera de docs; sustituir por ejemplos/contexto público útil o explicar la referencia técnica | T002/T005/T006/T014 |
| Wheel/sdist y futura CI | Lista de recursos completa, ningún estado/historial privado; CI sintética con permisos mínimos sin proveedores/publicación | T015/T016 |

T001 no ha escaneado el historial ni emitido dictamen de secretos/derechos. Un hallazgo real de T002 exige resolución
explícita antes de declarar publicable el candidato; no autoriza a reescribir Git ni a copiar el secreto al informe.
La compatibilidad CLI sigue exactamente como en P010 hasta T011/T012: este contrato no elige mínimos nuevos.

## 8. Lista permitida del corte inicial y continuidad

La exportación es un árbol independiente ensamblado por lista positiva **de archivos exactos revisados**, no un
clon del repo privado ni `git archive HEAD` sin filtros. Estos grupos son candidatos, no aprobación de sus bytes:

| Grupo permitido candidato | Condición antes de incluirlo |
|---|---|
| `src/harness_local/**` | Solo fuentes/recursos finales tras T019; sin `__pycache__`, datos operativos ni módulos exclusivos retirados; migraciones/lectores propios conservados |
| `frontend/src/**`, `tests/**`, `frontend/tests/**` | Código/tests/fixtures sintéticos revisados tras T006/T019; generados coherentes, sin rutas/evidencias privadas imprescindibles |
| `frontend/index.html`, `package*.json`, `openapi.json`, configs TS/Vite | Generación/construcción reproducibles; excluir `node_modules`, dist/build locales, mapas/capturas no autorizados |
| `.gitignore`, `.python-version`, `alembic.ini`, `pyproject.toml`, `uv.lock`, scripts vigentes | Rutas/ejemplos saneados; versiones y licencias comprobadas; seleccionar scripts por archivo |
| Ejemplos TOML/demos nuevos o revisados | Sintéticos, autónomos, dos altas; excluir guiones históricos `first_use/` y `provider_matrix/` |
| README inglés + entrada española, LICENSE/avisos, CONTRIBUTING/SECURITY, instrucciones raíz nuevas | Derechos/identidad confirmados; instrucciones suficientes para usuarios/forks/agentes, sin referencias privadas rotas |
| Documentación pública nueva y workflows revisados | Arquitectura/especificación/modelo/flujos vigentes, operación/soporte, decisiones iniciales y plan/estado públicos propios; CI sin publicación automática |

Exclusión inicial obligatoria: `.git` y cualquier objeto/ref/tag/historia privada, worktrees/submódulos con datos
Git, este `docs/archive/**`, `docs/phase/**`, DECISIONS/STATE/NEXT_STEPS/ROADMAP privados y demás docs internas
copiadas como historia; `.local`, `.harness`, `work`, venv, credenciales, estado/SQLite/backups, streams/runs,
cachés, capturas/evidencias privadas, rutas personales y artefactos no revisados. Un archivo ignorado no entra
por existir en disco. Incluir un grupo en esta tabla no permite una copia recursiva sin revisar cada miembro.

T014 redacta documentación **nueva** de partida: propósito/estado/límites, requisitos y primer uso, arquitectura,
datos/flujos, seguridad/operación, contrato de idiomas, contribución e instrucciones de agentes; DECISIONS con
decisiones técnicas iniciales autocontenidas y ROADMAP/STATE/NEXT_STEPS que describan el punto público real.
No fingir que sus fases/ADR privadas ocurrieron en la nueva raíz, ni exigir leerlas. Referencias DNNN/Hn en código
se explican con contexto técnico público cuando sean necesarias; la tabla de correspondencias queda privada.

T015 materializa una copia nueva solo dentro del alcance autorizado, con manifiesto privado origen/candidato
(commit, ruta, hash y sustituciones/omisiones) y manifiesto publicable sin identificadores privados. Comparar
código/recursos/dependencias con el origen revisado; cambios públicos de docs/saneamiento son explícitos y
trazables. Comprobar symlinks, archivos ocultos y enlaces. Crear repositorio/commit público requiere instrucción
propia; T001 no crea directorios candidatos ni ejecuta Git allí. T016 ensaya desde ese árbol, sin acceso al archivo
privado; T017 revisa bytes exactos y acciones remotas propuestas. No push, tag, Release ni visibilidad implícitos.

Después de abrir, el repositorio público es fuente principal de código, documentación, decisiones y fases.
Su `docs/phase` y su archivo público posteriores sí se versionan y evolucionan; la exclusión anterior es la
frontera del corte inicial privado. Este checkout conserva su historia y deja de ser un desarrollo activo
paralelo sincronizado por copias. No se sobrescriben contribuciones públicas desde el origen privado.

## 9. Matriz inicial de los diez criterios de salida

Todos los criterios siguen **pendientes como producto/expediente final**. T001 entrega diseño/inventario para
ellos; ni esta matriz ni P010 equivalen a su aprobación.

| # ROADMAP | Criterio | Tareas propietarias | Evidencia exigida/decisión pendiente |
|---|---|---|---|
| 1 | Código mantenido inglés, excepciones/hashes | T003–T006/T009/T019 | Inventario resuelto por archivo, diff y regresiones; v1 histórica explícita |
| 2 | Visual/defaults globales persistentes | T007/T010/T016 | Catálogos, CAS/fallback, accesibilidad, cuatro combinaciones y concurrencia |
| 3 | Trabajo inmutable, contexto/prompts bilingües | T008/T009/T016 | Altas cero/B, TOML/SQLite, migración explícita y rechazo de mutación; snapshot de intentos |
| 4 | CLI por capacidades/mínimos | T011/T012/T016 | Contrato con fuentes oficiales y límites verificada/candidata; mínimos aún sin decidir |
| 5 | Diagramas con paridad semántica | T013 y tareas que cambien datos/flujos | Matriz nodo/transición → código/tests, fallos/recuperación y render, sin alterar archivo histórico |
| 6 | Docs inglesas y primer uso autónomo | T014/T016 | Baseline pública nueva, entrada es, ejemplo mínimo y ensayo sin docs/cachés privadas |
| 7 | Licencia/contenido/corte saneado | T002/T014/T015/T016 | Licencia/titularidad por el usuario; auditoría origen y candidato, manifest privado/público, sin hallazgos pendientes |
| 8 | Paquete/CI/QA del candidato exacto | T015/T016 | Versión pendiente (v0.2.0 reservada); recursos, hashes, builds/CI distinguida de ejecución remota |
| 9 | Retirada legacy/A, cero/B conservados | T019/T013/T015/T016 | Ausencia de rutas/comandos/observers/prompts exclusivos, recuperación antigua y regresión B/cero |
| 10 | Dictamen y expediente antes de archivo | T017/T018 | Matriz final de diez y trece globales ajustados 1/11/13; autorización de publicación separada |

No aparece una contradicción documental que exija cambiar el diseño decidido por el usuario. Las elecciones
reversibles de persistencia/catálogos/versionado se concretan en D159. Licencia/titularidad, versión candidata y
alcance de ensayos operativos siguen pendientes en sus tareas; no se eligen ni se piden por anticipado aquí.
Una discrepancia durante implementación que no encaje en este contrato requiere HITL antes de cambiarlo.

## 10. Validación de T001

Validación estática offline: inventario completo de rutas rastreadas en `2730f54`; comentarios/docstrings Python
por AST/tokenización y búsqueda con/sin tildes; candidatos en el resto de textos y revisión por grupos;
contraste de símbolos/imports/rutas/esquemas/lectores citados; hashes de fuentes de recetas; enlaces locales,
índice ADR, límites documentales, integridad de archivos congelados y revisión de diff.

Resultados concretos y conteos en el inventario. No se ejecutaron suites, Alembic, builds, smokes, servicios,
CLI de proveedores, procesos de agentes o red; no cambia código, esquema o flujo implementado. El commit solo
incluye documentos de T001 y seguimiento vivo. La siguiente tarea es T002, seguida de T019 antes de T003.

Resultados del contraste documental de esta entrega:

| Check/comando | Resultado |
|---|---|
| `git ls-tree -r --name-only 2730f54` y comparación de conjuntos con las filas/grupos | 688 rutas exactas, sin ausencias ni duplicados: 469 individuales y 219 en 11 grupos históricos |
| `python3` con `ast`/`tokenize`/`re`/`hashlib` de biblioteca estándar; sin imports del producto | 236 archivos Python y 233 textos restantes inventariados; regex/documentación de límites en inventario |
| Lectura AST de las regex D088 y validación documental con biblioteca estándar | 159 ADR con estado e índice; 19 tareas, una completada y 18 pendientes; diez criterios de salida |
| Comprobador local de enlaces/anclas en los siete Markdown modificados/nuevos | 460 enlaces locales válidos |
| Hashes estáticos SHA-256 | Cuatro fuentes/recursos v1 coinciden con la tabla; no se ejecutó `fingerprint()` |
| Presupuestos D088 | STATE/base/NEXT_STEPS dentro de 24/12/48 KiB; instrucciones raíz dentro de 60/15/15 líneas |
| `git diff --exit-code 2730f54 -- src tests frontend scripts examples docs/archive` | Sin cambios; también cuerpos D001–D158 idénticos al original (índice ampliado aparte) |
| `git diff --check` y revisión de diff completo antes del commit | Sin errores de whitespace; alcance exclusivamente documental |
