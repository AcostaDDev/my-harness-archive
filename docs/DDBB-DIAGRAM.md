# Diagrama de datos — my_harness

Esquema SQLite del servicio local (Alembic `0025_project_work_languages`, 51 tablas). Generado en P008-T001 desde el metadata de `src/harness_local/storage/models.py` (actualizado en P009-T004 con preparación y propietarios compartidos, en P010-T003 con la proyección de runs, en P011-T007 con las preferencias de idioma y en P011-T008 con el idioma de trabajo por proyecto); cualquier cambio de modelos o migraciones actualiza este documento en la misma tarea (regla de paridad, D088).

P009-T002 implementa autoridad y creación de hijos (D117); T004 implementa preparación/pasos/journal y amplía
locks/procesos compartidos (D119). [Diseño de partida](archive/phase-009/P009-T001_CONTRATO_CREACION.md#6-persistencia-propuesta-y-migraciones).

Convenciones: `PK` clave primaria, `FK` clave ajena declarada, `UK` unicidad de columna; «null» marca columnas opcionales. Las unicidades compuestas y los índices únicos parciales se listan bajo cada diagrama. Las entidades de otro contexto aparecen solo con las columnas que relacionan. Los artefactos pesados (streams, capturas, copias) viven fuera de SQLite y se referencian por ruta y hash.

## Observación legacy y simulaciones (P001–P002)

Tablas de compatibilidad conservadas tras P011-T019 (D161). No hay indexador, visor ni observadores activos;
`watch_enabled` anterior queda inerte. `simulations` conserva el esqueleto sintético propio H0.3. No cambia metadata
ni ninguna revisión Alembic por esta retirada.

```mermaid
erDiagram
    simulations {
        string id PK
        string title
        string created_at
        json events
    }
    legacy_sources {
        string root PK
        string observed_at
        boolean watch_enabled
        text diagnostic "null"
    }
    legacy_runs {
        string root PK, FK "→ legacy_sources.root"
        string path PK
        string identity
    }
    legacy_artifacts {
        string root PK, FK "→ legacy_sources.root, legacy_runs.root"
        string path PK
        string run_path FK "null; → legacy_runs.path"
        string kind
        string format
        string status
        string sha256 "null"
        integer size_bytes "null"
        json payload "null"
        text diagnostic "null"
    }
    legacy_events {
        integer id PK
        string root FK "→ legacy_sources.root"
        string kind
        string observed_at
        json payload
    }
    legacy_sources ||--o{ legacy_runs : "root"
    legacy_sources ||--o{ legacy_artifacts : "root"
    legacy_runs |o--o{ legacy_artifacts : "root, run_path"
    legacy_sources ||--o{ legacy_events : "root"
```

## Ejecución gestionada (P003)

Autoridad operativa de runs, intentos, cola, exclusión por checkout, procesos y commits (D015–D027). `managed_runs.root` es la raíz canónica del checkout; no hay tabla de proyecto.

P011-T012 (D174) no cambia tablas ni revisiones: amplía los JSON propios. `versions_json` congela la versión CLI
observada, `reviewer/executor_cli_launch_sha256`, hash de política y, en v7, procedencia automática/aserción y
PATH/ruta explícita. `managed_processes.spec.preflight_observed` conserva diagnóstico, mínimo, huella de lanzamiento
y perfil/procedencia condicional por intento. Un rechazo previo al target tiene `launch_permitted=false`, identidad
de proceso nula y captura `refused`; si ya hay un grupo esperando GO se registra su parada observada. Campos ausentes
en historiales anteriores siguen ausentes; no se rellenan ni se recalculan. [Flujo](flows/cli-compatibility.md).

```mermaid
erDiagram
    managed_runs {
        string id PK
        string root
        string task_id
        string phase_id "→ managed_phases.id (lógica, sin FK)"
        text context_json
        text versions_json
        text history_json
        string status
        string stage
        integer revisions
        integer revision_limit
        integer version
        string created_at
        string updated_at
        string purpose
    }
    managed_attempts {
        string id PK
        string run_id FK "→ managed_runs.id"
        integer number
        text request_json
        text versions_json
        string status
        text result_json "null"
        string started_at
        string finished_at "null"
        json language_context "null; copia del job (0025)"
    }
    managed_events {
        integer id PK
        string run_id FK "→ managed_runs.id"
        integer sequence
        string kind
        string recorded_at
        json payload
    }
    managed_jobs {
        integer id PK
        string idempotency_key UK
        string run_id FK "→ managed_runs.id"
        text request_json
        string status
        string owner_token "null"
        string heartbeat_at "null"
        string lease_until "null"
        string created_at
        string finished_at "null"
        text diagnostic "null"
        json process_owner "null"
        boolean owner_closed
        string activation_id FK "null; → managed_activations.id"
        json language_context "null; ui-language-1 (0024) | language-context-1 (0025)"
    }
    checkout_locks {
        string root PK
        integer job_id FK, UK "null; → managed_jobs.id"
        string preparation_id FK, UK "null; → project_preparation_operations.id"
    }
    managed_processes {
        string id PK
        string attempt_id FK, UK "null; → managed_attempts.id"
        integer job_id FK "null; → managed_jobs.id"
        string preparation_id FK "null; → project_preparation_operations.id"
        json spec
        json identity "null"
        string status
        json capture "null"
    }
    managed_commits {
        string operation_id PK
        string run_id FK "→ managed_runs.id"
        integer job_id FK "→ managed_jobs.id"
        string status
        string base_revision
        string reviewed_fingerprint
        string expected_tree
        string expected_commit
        text intent_json
        text result_json "null"
        string commit_sha "null"
        string created_at
        string finished_at "null"
    }
    managed_activations {
        string id PK
        string root
        string repository_key "null"
        string status
        string preview_sha256
        text legacy_stopped
        text rules_json
        text marker
        string marker_sha256
        string snapshot_root
        text manifest_json "null"
        string manifest_sha256 "null"
        string owner_token "null"
        integer version
        string created_at
        string activated_at "null"
        string finished_at "null"
        text diagnostic "null"
        text revert_reason "null"
        string export_path "null"
        string export_sha256 "null"
    }
    managed_runs ||--o{ managed_attempts : "run_id"
    managed_runs ||--o{ managed_events : "run_id"
    managed_runs ||--o{ managed_jobs : "run_id"
    managed_activations |o--o{ managed_jobs : "activation_id"
    managed_jobs |o--o{ checkout_locks : "job_id"
    managed_attempts |o--o| managed_processes : "attempt_id"
    managed_jobs |o--o{ managed_processes : "job_id"
    managed_runs ||--o{ managed_commits : "run_id"
    managed_jobs ||--o{ managed_commits : "job_id"
```

Unicidad: `managed_attempts` (run_id, number); `managed_events` (run_id, sequence); `uq_managed_commits_live` sobre `managed_commits` (run_id) donde status IN ('INTENT', 'COMMITTED'); `uq_managed_activations_live_root` sobre `managed_activations` (root) donde status IN ('PREPARING', 'ACTIVE', 'REVERTING'); `uq_managed_activations_live_repository` sobre `managed_activations` (repository_key) donde status IN ('PREPARING', 'ACTIVE', 'REVERTING').

## Prompts y permisos (P004)

Catálogo versionado por ámbito y peticiones de permiso exactas con su consumo (D030–D031).

```mermaid
erDiagram
    prompt_heads {
        string scope PK
        string owner PK
        string name PK
        integer generation
        string active_id "null"
    }
    prompt_versions {
        string id PK
        string scope
        string owner
        string name
        text template
        string sha256
        text source
        string created_at
    }
    prompt_activations {
        string id PK
        string scope
        string owner
        string name
        string previous_id "null"
        string version_id FK "→ prompt_versions.id"
        integer generation
        text reason
        string created_at
    }
    permission_requests {
        string id PK
        string run_id FK "→ managed_runs.id"
        integer version
        string status
        json request
        string fingerprint
        string expires_at
        string created_at
        json decision "null"
        string consumed_by "null"
        string supersedes FK "null; → permission_requests.id"
    }
    managed_runs {
        string id PK
    }
    prompt_versions ||--o{ prompt_activations : "version_id"
    managed_runs ||--o{ permission_requests : "run_id"
    permission_requests |o--o{ permission_requests : "supersedes"
```

## Fases y creación (P004–P005)

Fases con definición versionada, preguntas, operaciones (check, cierre, transición, edición documental), autorizaciones y eventos (D032–D037). `managed_runs.phase_id` es una referencia lógica sin FK.

```mermaid
erDiagram
    managed_phases {
        string id PK
        string root
        string code
        json definition
        string definition_sha256
        json documents
        string status
        integer version
        string created_at
        string updated_at
        integer definition_number
    }
    phase_definitions {
        string id PK
        string phase_id FK "→ managed_phases.id"
        integer number
        json definition
        string definition_sha256
        json documents
        string origin
        text reason "null"
        json actor "null"
        string created_at
    }
    phase_questions {
        string id PK
        string phase_id FK "→ managed_phases.id"
        text text
        json source
        string status
        json answer "null"
        integer version
        string created_at
    }
    phase_operations {
        string id PK
        string phase_id FK "→ managed_phases.id"
        string kind
        string run_id FK "null; → managed_runs.id"
        string status
        string previous_status
        json request
        json result "null"
        string created_at
        string finished_at "null"
    }
    phase_authorizations {
        string id PK
        string phase_id FK "→ managed_phases.id"
        string kind
        string status
        json scope
        string fingerprint
        json actor
        text reason
        string expires_at
        string created_at
        json closed "null"
        integer version
    }
    phase_events {
        integer id PK
        string phase_id FK "→ managed_phases.id"
        integer sequence
        string kind
        string recorded_at
        json payload
    }
    project_bootstraps {
        string id PK
        string root UK
        string run_id FK, UK "→ managed_runs.id"
        string phase_id FK "null; → managed_phases.id"
        string status
        json preview
        json intent
        json decision
        json result "null"
        string created_at
        string finished_at "null"
    }
    managed_runs {
        string id PK
        string phase_id "→ managed_phases.id (lógica, sin FK)"
    }
    managed_phases |o..o{ managed_runs : "phase_id (lógica)"
    managed_phases ||--o{ phase_definitions : "phase_id"
    managed_phases ||--o{ phase_questions : "phase_id"
    managed_phases ||--o{ phase_operations : "phase_id"
    managed_runs |o--o{ phase_operations : "run_id"
    managed_phases ||--o{ phase_authorizations : "phase_id"
    managed_phases ||--o{ phase_events : "phase_id"
    managed_runs ||--o{ project_bootstraps : "run_id"
    managed_phases |o--o{ project_bootstraps : "phase_id"
```

Unicidad: `managed_phases` (root, code); `uq_managed_phases_open_root` sobre `managed_phases` (root) donde status NOT IN ('CLOSED', 'ABANDONED'); `phase_definitions` (phase_id, number); `phase_events` (phase_id, sequence).

## Chat y planificación conversacional (P005, P007, P008)

Chat contextual (D035, D083), conversaciones de definición y planificación de fase (D075, D086) e importación del
Flujo A histórico (`kind = 'project_import'`, D098), conservado solo como datos tras D161: `source`, turnos,
propuestas y `import-drafts/<id>/` anteriores no se borran ni vuelven a ejecutarse. El Flujo B (`kind = 'onboarding'`, D102) usa la misma
columna `source` para congelar inventario, HEAD y árbol, y `onboarding-drafts/<id>/` para sus borradores. No añade
tablas, columnas ni índices. `managed_runs.purpose = 'onboarding'` enlaza sus turnos con la autoridad de planificación;
la intención de exportación queda en eventos antes del efecto. La guardia de downgrade de 0019 protege ambos orígenes.

```mermaid
erDiagram
    chat_conversations {
        string id PK
        string root
        string title
        string phase_id FK "null; → managed_phases.id"
        string task_run_id FK "null; → managed_runs.id"
        json actor
        integer version
        string created_at
        string updated_at
        string idempotency_key UK "null"
        string request_sha256 "null"
    }
    chat_turns {
        string id PK
        string conversation_id FK "→ chat_conversations.id"
        integer number
        string run_id FK, UK "→ managed_runs.id"
        string status
        text message
        json request
        string request_sha256
        json result "null"
        json actor
        string created_at
        string finished_at "null"
    }
    chat_proposals {
        string id PK
        string conversation_id FK "→ chat_conversations.id"
        string turn_id FK "→ chat_turns.id"
        integer number
        string status
        json proposal
        string proposal_sha256
        string run_id FK, UK "null; → managed_runs.id"
        json decision "null"
        integer version
        string created_at
    }
    planning_conversations {
        string id PK
        string root
        string kind
        string phase_id FK "null; → managed_phases.id"
        string title
        json brief "null"
        json known
        json deferred
        json log
        json actor
        integer version
        string created_at
        string updated_at
        string idempotency_key UK "null"
        string request_sha256 "null"
        json source "null"
    }
    planning_turns {
        string id PK
        string conversation_id FK "→ planning_conversations.id"
        integer number
        string run_id FK, UK "→ managed_runs.id"
        string status
        text message
        json request
        string request_sha256
        json result "null"
        json actor
        string created_at
        string finished_at "null"
    }
    planning_proposals {
        string id PK
        string conversation_id FK "→ planning_conversations.id"
        string turn_id FK "→ planning_turns.id"
        integer number
        string kind
        string path "null"
        text content
        text reason
        string content_sha256
        string base_sha256 "null"
        string proposal_sha256
        string status
        json decision "null"
        integer version
        string created_at
    }
    managed_runs {
        string id PK
    }
    managed_phases {
        string id PK
    }
    managed_phases |o--o{ chat_conversations : "phase_id"
    managed_runs |o--o{ chat_conversations : "task_run_id"
    chat_conversations ||--o{ chat_turns : "conversation_id"
    managed_runs ||--o{ chat_turns : "run_id"
    chat_conversations ||--o{ chat_proposals : "conversation_id"
    chat_turns ||--o{ chat_proposals : "turn_id"
    managed_runs |o--o{ chat_proposals : "run_id"
    managed_phases |o--o{ planning_conversations : "phase_id"
    planning_conversations ||--o{ planning_turns : "conversation_id"
    managed_runs ||--o{ planning_turns : "run_id"
    planning_conversations ||--o{ planning_proposals : "conversation_id"
    planning_turns ||--o{ planning_proposals : "turn_id"
```

Unicidad: `uq_chat_conversations_key` sobre `chat_conversations` (idempotency_key); `chat_turns` (conversation_id, number); `uq_chat_turns_pending` sobre `chat_turns` (conversation_id) donde status = 'QUEUED'; `chat_proposals` (conversation_id, number); `uq_planning_conversations_key` sobre `planning_conversations` (idempotency_key); `uq_planning_definition` sobre `planning_conversations` (root) donde kind = 'definition'; `planning_turns` (conversation_id, number); `uq_planning_turns_pending` sobre `planning_turns` (conversation_id) donde status = 'QUEUED'; `planning_proposals` (conversation_id, number).

## Incorporación documental confirmada (P008-T012/T015)

`project_imports` conserva una operación por checkout y conversación: vista previa íntegra, intención de commit
sellada antes del efecto, decisión y resultado (D100). El Flujo B reutiliza esta tabla (D103), sin columnas ni
índices nuevos: `preview.flow = "onboarding"` identifica el origen; `preview.profile` y `profile_sha256` sellan el
perfil de la composición, y `decision.profile_sha256` registra su confirmación. Conserva el propósito compartido
`managed_runs.purpose = 'import_commit'`; la conversación mantiene `kind = 'onboarding'`. El job, lock, lease y recuperación son los de `managed_jobs`.
La fase y su base documental se insertan en la misma transacción que el resultado y el fin del job. Un estado
`INTERRUPTED` conserva la intención y bloquea trabajo nuevo y la reversión D027 hasta conciliarla.

```mermaid
erDiagram
    project_imports {
        string id PK
        string root UK
        string conversation_id FK, UK
        string run_id FK, UK
        string phase_id FK "null"
        string status
        json preview
        text intent
        json decision
        json result "null"
        string created_at
        string finished_at "null"
    }
    planning_conversations ||--o| project_imports : "conversation_id"
    managed_runs ||--o| project_imports : "run_id"
    managed_phases |o--o{ project_imports : "phase_id"
```

## Métricas y registro de proyectos (P007)

Métricas por intento con procedencia (D074) y registro de proyectos desde la UI (D078).
P009-T003 (D118) amplía el JSON `row` de fila/eventos con `agent_selection` opcional en v5:
`reviewer = {preset_id, model, effort}` y `executor = {preset_id}`; catálogo/modo siguen en `row.policy`.
Sin tablas/columnas ni migración nuevas. Cambio de versión/evento e invalidación de propuestas de planificación
son atómicos; solo cambian status/version/decision de la propuesta, nunca request/result del turno ni snapshots
del run. La fila sin selección conserva la pareja heredada y los eventos anteriores intactos.

```mermaid
erDiagram
    attempt_metrics {
        string attempt_id PK, FK "→ managed_attempts.id"
        string run_id FK "→ managed_runs.id"
        integer number
        string root
        string phase_code
        string task_id
        string purpose
        string role
        string provider "null"
        string adapter_version "null"
        string cli_version "null"
        string requested_model "null"
        string requested_effort "null"
        json reported_models "null"
        string reported_effort "null"
        string status
        text error "null"
        string verdict "null"
        integer executor_round
        string accounting "null"
        string input_semantics "null"
        integer input_tokens "null"
        integer cache_read_tokens "null"
        integer cache_write_tokens "null"
        integer output_tokens "null"
        integer reasoning_tokens "null"
        integer uncached_input_tokens "null"
        integer total_tokens "null"
        integer turns "null"
        integer tool_calls "null"
        json tools "null"
        integer permission_denials "null"
        integer wall_ms "null"
        integer duration_ms "null"
        integer api_duration_ms "null"
        float cost_usd "null"
        string started_at
        string finished_at "null"
        string day
        string source
        string normalization "null"
        string catalog
        json provenance
        json diagnostics
        string recorded_at
    }
    attempt_model_metrics {
        string attempt_id PK, FK "→ attempt_metrics.attempt_id"
        string model PK
        integer input_tokens "null"
        integer cache_read_tokens "null"
        integer cache_write_tokens "null"
        integer output_tokens "null"
        integer reasoning_tokens "null"
        float cost_usd "null"
    }
    registered_projects {
        string id PK
        string creation_id FK, UK "null; → project_creation_operations.id"
        integer version
        string status
        string root
        string composition
        string profile
        json row
        string row_sha256
        json trust
        string created_at
        string updated_at
    }
    registered_project_events {
        integer id PK
        string project_id FK "→ registered_projects.id"
        integer version
        string action
        json row
        string row_sha256
        string previous_sha256 "null"
        string preview_sha256
        json actor
        text reason "null"
        string recorded_at
    }
    managed_attempts {
        string id PK
    }
    managed_runs {
        string id PK
    }
    managed_attempts ||--o| attempt_metrics : "attempt_id"
    managed_runs ||--o{ attempt_metrics : "run_id"
    attempt_metrics ||--o{ attempt_model_metrics : "attempt_id"
    registered_projects ||--o{ registered_project_events : "project_id"
```

Unicidad: `ix_attempt_metrics_run` sobre `attempt_metrics` (run_id, number); `uq_registered_projects_active_root` sobre `registered_projects` (root) donde status = 'ACTIVE'; `registered_project_events` (project_id, version).

## Autoridad de carpeta y creación de hijos (P009-T002)

D116/D117. La selección UI autoriza hijos directos nuevos; no amplía las raíces TOML de D078. El singleton
no existe hasta la primera selección. Eventos de raíz conservan snapshots de cada revisión, sin FK a una fila
mutable como prueba de autoridad. Intención sellada antes de mkdir; identidad del hijo solo tras fsync del padre.
Alta, evento D078, `creation_id` y resultado REGISTERED se confirman juntos. No hay jobs, agentes o procesos
asociados a estas operaciones de creación; preparación de Django se registra por separado en T004 (D119).

```mermaid
erDiagram
    project_creation_root {
        integer id PK "singleton; CHECK id = 1"
        integer version
        string status
        string path "null"
        json identity "null; device, inode"
        string row_sha256
        string updated_at
    }
    project_creation_root_events {
        integer id PK
        integer version UK
        string idempotency_key UK
        string request_sha256
        json payload "antes, después, preview, actor, motivo, fecha y hashes"
    }
    project_creation_operations {
        string id PK
        string idempotency_key UK
        string request_sha256
        integer version
        string project_id
        string directory_name
        string target
        boolean reserved
        json authority "revisión vigente autorizada; intención original intacta"
        json intent
        string intent_sha256
        string status
        json child_identity "null"
        json result "null"
        text diagnostic "null"
        string created_at
        string updated_at
    }
    project_creation_operation_events {
        integer id PK
        string operation_id FK
        integer version
        string idempotency_key UK "null; reanudar/cancelar"
        string request_sha256 "null"
        json payload "snapshot, transición, actor, fecha y cadena de hashes"
    }
    registered_projects {
        string id PK
        string creation_id FK, UK "null; filas previas conservadas"
    }
    project_creation_root ||..o{ project_creation_root_events : "revisión lógica"
    project_creation_root ||..o{ project_creation_operations : "autoridad lógica congelada"
    project_creation_operations ||--o{ project_creation_operation_events : "operation_id"
    project_creation_operations |o--o| registered_projects : "creation_id"
```

Unicidad: `uq_creation_reserved_id` sobre (project_id) y `uq_creation_reserved_target` sobre (target) donde
reserved = 1; `project_creation_operation_events` (operation_id, version); `uq_registered_creation` sobre
registered_projects (creation_id). Las reservas se contrastan transaccionalmente con filas D078 y destinos
anidados, incluidos alias físicos de mayúsculas. Los índices textuales no sustituyen esa comprobación.
REGISTERED libera la reserva de operación y manda D078; CANCELLED solo la libera con ausencia
acreditada. No caducan por timeout. Autoridad/retirada/efectos cortos comparten la exclusión de escritura SQLite.


## Preparación Django (P009-T004)

D119. Intención previa y reserva única por checkout; confirmación y admisión/registro comparten la transacción
SQLite. No hay run/attempt ficticio. Las capturas y bytes de preparación permanecen dentro de SQLite, sin
artefactos externos nuevos para backup o retención. El recibo solo se adopta junto a COMPLETED y la liberación
del lock; su SHA-256 se congela en jobs posteriores como `project_environment_sha256`.

```mermaid
erDiagram
    project_preparation_operations {
        string id PK
        string project_id FK "→ registered_projects.id"
        string root
        string idempotency_key UK
        string request_sha256
        string previous_id FK "null; → project_preparation_operations.id"
        integer version
        string status
        boolean reserved
        json plan
        string plan_sha256
        string owner_token "null"
        string lease_until "null"
        json process_owner "null"
        boolean owner_closed
        boolean cancel_requested
        json commit_intent "null"
        json receipt "null"
        text diagnostic "null"
        string created_at
        string updated_at
    }
    project_preparation_steps {
        string id PK
        string operation_id FK
        integer number
        json spec
        string status
        json evidence "null; captura y snapshot de bytes acreditados"
    }
    project_preparation_events {
        integer id PK
        string operation_id FK
        integer version
        string kind
        json payload "actor, confirmación, proceso, captura o transición"
        string recorded_at
    }
    registered_projects ||--o{ project_preparation_operations : project_id
    project_preparation_operations |o--o{ project_preparation_operations : previous_id
    project_preparation_operations ||--o{ project_preparation_steps : operation_id
    project_preparation_operations ||--o{ project_preparation_events : operation_id
    project_preparation_operations |o--o| checkout_locks : preparation_id
    project_preparation_operations |o--o{ managed_processes : preparation_id
```

Unicidad: `uq_preparation_reserved` sobre (root) donde reserved = 1; pasos (operation_id, number), eventos
(operation_id, version). Reintentar crea otra operación enlazada y copia únicamente el prefijo DONE acreditado;
los registros/payloads de intentos anteriores conservan sus bytes. La sucesión se audita y traspasa la reserva.
Cancelación sin efectos libera la reserva; efectos inciertos se conservan reservados, incluso sin lock vivo.
Controles CAS guardan clave/hash en el payload del evento bajo la misma exclusión SQLite para replay.

`checkout_locks` conserva root como PK y exige exactamente un propietario (job_id o preparation_id). En
`managed_processes`, id sustituye a la PK attempt_id: las filas antiguas conservan id=attempt_id, su FK y su
job; para preparación, attempt_id/job_id son null y preparation_id es obligatorio. El CHECK impide propietarios
vacíos o mixtos. Ambas tablas hoja se reconstruyen con FKs activas, copiando todas las filas previas. Downgrade
solo sin historia de preparación; de lo contrario se usa backup en consulta, sin borrar evidencia.

## Proyección de runs (P010-T003)

D142/D144. `run-projection-1`: tablas derivadas de `managed_runs.history_json`, que sigue siendo la autoridad. Se
escriben en la misma transacción que el historial (`_queue_new_run` y `_history`) y `0023_run_projection` las rellena
decodificando una vez cada historial existente (formatos 1–8), sin modificarlo. Las vistas de runs solo leen estas
tablas, y las métricas y la vista previa de exportación (P010-T011, D145) las leen junto a `managed_attempts`; el motor,
la recuperación, los checks, el chat y los permisos siguen leyendo el historial. Las columnas
`*_json` guardan el texto exacto del historial o JSON congelado. El diff revisado se guarda en tramos fijos de 64 KiB
(`chunk` desde 0). El backup recalcula cada run y compara filas y recuentos; nunca reconstruye.

```mermaid
erDiagram
    run_projections {
        string run_id PK, FK "→ managed_runs.id"
        string projection "run-projection-1"
        string history_sha256 "del texto del que se derivó"
        string history_status
        text task_json "null"
        integer attempts
        integer executor_attempts
        integer cycle_count
        integer stop_count
        text stop_stage "null; parada actual"
        text stop_reason "null"
        text acceptance_json "null"
    }
    run_projection_stops {
        string run_id PK, FK "→ managed_runs.id"
        integer ordinal PK
        text stage
        text reason
    }
    run_projection_cycles {
        string run_id PK, FK "→ managed_runs.id"
        integer number PK
        text verdict "null"
        text fingerprint
        text changed_paths_json
        string diff_sha256
        integer diff_bytes
        text provenance_json "null"
        text review_json "null"
        text formatting_json "null"
        text validation_json "vista sin casos ni diff"
        text validation_evidence_json
        text validation_run_id "null"
        text validation_source_attempt_id "null"
    }
    run_projection_diff_chunks {
        string run_id PK, FK "→ managed_runs.id"
        integer cycle PK
        integer chunk PK
        blob data "≤ 64 KiB de bytes UTF-8"
    }
    run_projection_reports {
        string run_id PK, FK "→ managed_runs.id"
        integer cycle PK
        integer entry PK
        integer report PK
        text command_id "null"
        text summary_json
        text original_base64 "null"
        string sha256 "null"
        integer size_bytes "null"
        integer case_count
    }
    run_projection_cases {
        string run_id PK, FK "→ managed_runs.id"
        integer cycle PK
        integer entry PK
        integer report PK
        integer ordinal PK
        text case_json
    }
    managed_runs {
        string id PK
    }
    managed_runs ||--|| run_projections : "run_id"
    managed_runs ||--o{ run_projection_stops : "run_id"
    managed_runs ||--o{ run_projection_cycles : "run_id"
    managed_runs ||--o{ run_projection_diff_chunks : "run_id"
    managed_runs ||--o{ run_projection_reports : "run_id"
    managed_runs ||--o{ run_projection_cases : "run_id"
```

Las claves primarias compuestas fijan el orden estable de lectura: paradas por ordinal, ciclos por número, tramos,
reportes y casos por sus índices. `cycle` de tramos, reportes y casos es el `number` del ciclo, sin FK declarada.
Downgrade: elimina solo estas tablas.

## Preferencias de idioma (P011-T007)

Una fila por instalación/base (D166). `0024_product_preferences` la crea con `en`/`en` y versión 1; leerla nunca la
crea ni la repara. Sin FK: el resto del esquema solo la consulta al admitir un job.

```mermaid
erDiagram
    product_preferences {
        integer id PK "CHECK id = 1"
        string format "product-preferences-1"
        string ui_language "CHECK en | es"
        string default_work_language "CHECK en | es"
        integer version
        string updated_at
    }
    product_preference_events {
        integer id PK
        integer version UK
        string idempotency_key UK
        string request_sha256
        json payload "before, after, actor, recorded_at, previous_sha256, sha256"
    }
```

Cada `PUT /api/managed/preferences` con la versión esperada incrementa `version` y añade un evento encadenado por
hash; la misma clave con la misma petición devuelve el resultado registrado. `managed_jobs.language_context` sella
`{format: ui-language-1, ui_language, preferences_version}` en la transacción que admite el job; reanudar un run
(reintento, revalidación, bootstrap, importación, exportación o edición documental) copia el del primer job del
run, también null. Jobs anteriores a `0024` quedan null («no registrado»). Downgrade: rechazado si hay eventos;
sin ellos, todas las capturas son `en` de fábrica y se eliminan con la columna.

## Idioma de trabajo por proyecto (P011-T008)

Una fila por raíz canónica (D167), escrita una vez y nunca actualizada ni borrada. `0025_project_work_languages`
crea la tabla vacía: los proyectos anteriores quedan sin idioma de trabajo confirmado, sin inferirlo. Sin FK: la
raíz identifica el checkout aunque el registro se dé de baja, cambie de id o el proyecto venga del TOML.

```mermaid
erDiagram
    project_work_languages {
        string root PK "raíz canónica"
        string format "work-language-1"
        string project_id "proyecto que lo confirmó"
        string work_language "CHECK en | es"
        string source "CHECK registration | creation | toml | migration"
        json confirmation "preview_sha256 o hash del TOML, actor, motivo, default y versión de preferencias"
        string sha256 "hash de la fila"
        string confirmed_at
    }
```

Se escribe en la transacción que confirma el alta (registro, registro del hijo creado), al arrancar con un TOML
`local-config-6` que lo declara, o en la confirmación explícita ausente → valor. Otro valor para la misma raíz se
rechaza. Desde `0025`, `managed_jobs.language_context` sella `language-context-1` (`ui_language`,
`preferences_version`, `work_language`, `work_language_source`, `work_language_sha256`) al admitir cada job nuevo;
sin fila no se admite trabajo nuevo. `managed_attempts.language_context` copia el del job al iniciar cada intento
(null antes de `0025`). Downgrade: rechazado si hay alguna fila (una confirmación explícita no se representa antes);
sin filas elimina la tabla y la columna.
