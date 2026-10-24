# P011 — Revisión de salida

Fecha: 2026-10-24. Base: `cde2112` (T024) más los cambios de esta tarea. Tarea:
[P011-T017](../NEXT_STEPS.md#p011-t017--revisión-de-salida-y-expediente-para-apertura-pública). Decisión:
[D181](../DECISIONS.md#d181--p011-t017-dictamen-favorable-y-expediente-de-apertura-pública).
**Dictamen: favorable en el alcance declarado.** Los diez criterios de ROADMAP y los trece globales de
SPECIFICATION §10 (1/11/13 ajustados por D155/D161) se cumplen con la evidencia de abajo; los dos hallazgos de esta
revisión se corrigen aquí por HITL y no queda tarea obligatoria, licencia ni hallazgo de privacidad o paridad
pendiente. El cierre documental es T018; la apertura remota exige una autorización propia sobre el
[expediente](P011_EXPEDIENTE_APERTURA.md). Nada se ha publicado.

## 1. Método

- **Evidencia de tarea:** cada entrega de P011 registra base, comandos, resultados y omisiones; se contrasta su
  enunciado con el criterio y con el código actual. El dictamen de P010 (D152) es antecedente, no prueba de P011.
- **Reejecutado en T017:** suites completas tras el cambio de §4 (catálogos de la CLI), instantánea pública y dos
  builds del candidato final, `check_distribution` del paquete instalado y comprobador de la documentación pública
  (§7). Las pruebas citadas en §3 existen por nombre en la base y forman parte de esa ejecución.
- **No repetido:** ensayos ya válidos de T016 (clon limpio con cachés vacías) y T024 (navegador), porque el cambio
  posterior se limita a cuatro textos de catálogo, un docstring y documentación; su evidencia sigue aplicando.
- **Real frente a sintético:** P011 no usa proveedores ni CLI reales. La evidencia real archivada (D050, D071, D139)
  es histórica y de su paquete; los dobles no acreditan inicio de sesión, inferencia ni calidad lingüística.

## 2. Criterios de salida de ROADMAP

| # | Criterio | Evidencia | Dictamen y límites |
|---|---|---|---|
| 1 | Inventario por archivo; código mantenido en inglés; excepciones justificadas sin tocar congelados | T001 (inventario de 688 rutas), T003–T006 (D162–D165: AST idéntico, comentarios/docstrings/descripciones OpenAPI en inglés), T019 (D161), T009 (prompts ingleses, D169), T021/T022 (catálogos, técnicos listados en `tests/fixtures/service_texts/english.json`) | **Cumple.** Excepciones con ruta/motivo: recetas v1 por bytes/huella, alias bilingües de parsers, fixtures bilingües, guiones históricos fuera del candidato y vocabulario documental español histórico byte a byte |
| 2 | Visual/default de trabajo globales en/es; visual mutable sin ajuste por proyecto; persistencia, fallback, catálogos, QA; congelado por interacción | T007 (D166: `0024`, CAS, `ui-language-1` sellado), T010/T021/T022 (D170–D172: 1417 claves UI, 1195 de servicio/CLI), T016 (cambio sin mutar evidencia), T024 (D180: 14 pantallas × 8 combinaciones) | **Cumple.** QA solo en Chrome (500 px real, 390 px emulado); sin lectores de pantalla. Códigos técnicos visibles por HITL (D180) |
| 3 | Trabajo en/es inmutable al alta; prompts ingleses; directiva de ambos idiomas congelada; docs/código ingleses con conversación española probados | T008 (D167: `0025`, 409 `work_language_immutable`), T020 (D168: recetas v2), T009 (D169: `language-directive-1`), T016 (cuatro pares en prompts grabados, rechazo de cambio por API) | **Cumple** con agentes falsos. La calidad lingüística con proveedores reales no está acreditada |
| 4 | Política CLI por capacidades y mínimos; posteriores compatibles sin allowlist; guardias; bloqueo antes del efecto; sin soporte universal | T011 (D173: contrato y fuentes oficiales), T012 (D174: `local-config-7`/`cli-14`, mínimos Codex 0.163.0 / Claude 2.1.304), T016 (2.1.305 admitida con compatibilidad condicionada, 2.1.200 rechazada) | **Cumple** con CLI falsas. Posteriores admitidas sin afirmar efectos internos verificados; ninguna CLI real caracterizada en P011 |
| 5 | Diagramas de flujos/arquitectura/datos contrastados con código y pruebas, con matriz; sin discrepancias ocultas ni históricos reescritos | T013 (D175: 14 flujos/23 diagramas, 12 ER, catorce hallazgos corregidos), T023 (D177: versión pública con paridad ER 51/520 y 35 diagramas), residuo «observers» cerrado aquí (§4) | **Cumple.** Validación con parser Mermaid local, sin render DOM |
| 6 | Docs públicas inglesas, entrada española, README y ejemplo mínimo reproducible hasta COMMITTED; baseline para forks/agentes sin ADR privadas | T014 (D176: `docs/public/`, README/README.es, `local-config-7` mínimo), T023 (D177), T016 (D179: primer uso desde clon limpio ensayado hasta COMMITTED y fase cerrada) | **Cumple.** README cita ahora también la QA de navegador (§4). Ensayo solo en macOS ARM64 |
| 7 | Licencia/titularidad; contenido, historial y artefactos revisados; instantánea con Git independiente sin historia ni estado privado | T002 (D160: MIT, David Acosta, escaneo de 4.009 objetos), T015 (D178: lista positiva, manifiestos privado/público, perfil privado retirado del código), T016/T017 (instantánea regenerada sin problemas, §5) | **Cumple.** El historial privado se conserva sin reescritura; reflogs/inalcanzables fuera de la garantía del escaneo (D160) y no se exportan |
| 8 | Paquete coherente con versión/metadatos/recursos; CI sintética sin secretos; materiales de release; instalación/QA del artefacto exacto | T015 (D178: `0.1.0`, CHANGELOG, CI `macos-15`), T016 (D179: `pylock.toml`), T024 (D180), T017 (§5: dos builds idénticos y `check_distribution` del candidato final) | **Cumple** localmente. **CI remota no ejecutada**: se comprueba en la apertura (expediente, paso 5) |
| 9 | Legacy/A retirado de UI/API/CLI, arranque, prompts, docs y paquete; solo cero y B; historia propia sin borrar datos | T019 (D161), T015 (20 componentes retirados ausentes por check), T016 (rutas 404, comandos rechazados, ambos accesos hasta COMMITTED), T017 (texto residual de la CLI corregido, §4) | **Cumple.** Tablas/revisiones 0001–0025 conservadas; `watch_enabled` inerte |
| 10 | Dictamen de diez y trece antes del cierre; expediente sin publicar | Este documento y el [expediente](P011_EXPEDIENTE_APERTURA.md) | **Cumple.** Ninguna acción remota ejecutada |

## 3. Criterios globales de SPECIFICATION §10

Redacción vigente tras D155/D161; la [matriz histórica de P010](../archive/phase-010/P010_MATRIZ_ACEPTACION.md) se
conserva sin reescribir (su criterio 1 citaba la importación legacy, hoy retirada). Todas las pruebas citadas pasan en
la ejecución de §7.

| # | Criterio (resumen) | Evidencia offline reejecutada | Dictamen y límites |
|---|---|---|---|
| 1 | Repetir alta cero/B y confirmaciones no duplica ni inventa | `test_bootstrap.py::test_confirmed_creation_is_idempotent_under_concurrency`; `test_onboarding_commit.py::test_http_confirmation_requires_profile_hash_and_is_idempotent`, `::test_crash_reconciles_same_intent_commit_and_phase`; `test_project_preparation.py::test_preparation_api_security_strict_payload_and_idempotent_confirmation`; `test_project_onboarding.py::test_malformed_and_oversized_sources_diagnose_instead_of_inventing` | **Cumple** (ajustado por D161: la importación legacy ya no existe) |
| 2 | Ejecución → fallo → corrección → revisión → commit con historial | `test_acceptance_matrix.py::test_failed_test_correction_review_and_commit_keep_the_whole_history`; `test_managed_api.py::test_http_flow_executes_reviews_and_commits_once_across_double_submit_and_restart` | **Cumple** |
| 3 | Sin dos escritores por checkout, tampoco tras reinicio con proceso vivo | `test_managed.py::test_threaded_double_requests_and_claims_invoke_once`, `::test_processes_share_idempotency_and_writer_lock`; `test_cli_agents.py::test_recovery_blocks_live_owner_and_group_after_lease`, `::test_actual_owner_crash_restart_retains_group_lock_and_bytes`; `test_git.py::test_commit_job_holds_the_checkout_writer_lock` | **Cumple.** Contención cooperativa, sin aislamiento del SO (D064/D065) |
| 4 | Denegación no ejecuta; aprobación caducada o doble no se reutiliza | `test_permissions.py::test_denial_prevents_executor_call_and_replacement_restores_explicit_retry`, `::test_expiry_at_decision_and_at_next_attempt`, `::test_crash_after_intent_never_reuses_once_grant`, `::test_concurrent_grant_and_deny_only_one_commits` | **Cumple** |
| 5 | Reinicio sin efectos a ciegas; caída tras commit conciliada | `test_managed.py::test_persisted_history_snapshots_results_events_survive_restart`, `::test_crash_during_correction_reserves_budget_and_needs_explicit_recovery`; `test_e2e_offline.py::test_quarantine_survives_restart_and_recovery_never_repeats_executor`; `test_managed_api.py::test_recovery_over_http_requires_explicit_confirmation_and_never_repeats_the_executor`; `test_git.py::test_crash_around_the_git_effect_recovers_without_duplicate_commit`; T016 (reinicio del paquete instalado) | **Cumple** offline; reinicio con ejecución real en curso no observado |
| 6 | Editar prompts no cambia el intento pasado | `test_prompts.py::test_activation_during_attempt_keeps_snapshot_and_future_attempt_uses_new_version`, `::test_restart_stopped_run_pins_catalog_and_preserves_attempts` | **Cumple.** La directiva de idioma también queda sellada por intento (D169) |
| 7 | Cambio tras el diff revisado invalida la aceptación | `test_engine.py::test_content_change_during_review_invalidates_acceptance`, `::test_content_change_during_validation_requires_revalidation`; `test_git.py::test_content_changed_between_intent_and_effect_never_commits` | **Cumple** |
| 8 | Cierre con validación y autorización vigentes; archivo sin pérdida | `test_phases.py::test_stale_ready_never_closes_and_requires_new_evidence`, `::test_batch_and_close_authorizations_are_distinct_explicit_and_audited`; `test_phase_closure.py::test_unified_closure_exact_archive_and_successor_without_plan`, `::test_closure_refuses_before_tag_or_writes`; T016 (cierre con tag `p001` en el paquete instalado) | **Cumple** |
| 9 | Otro perfil sin cambiar el núcleo | `test_engine.py::test_stack_rules_are_in_declarative_profile_not_core` (perfil sintético desde T015); `test_declared_profiles.py`; `test_typescript_profile.py::test_profile_import_is_declarative_and_core_has_no_new_stack_conditions`; `test_typescript_preparation.py::test_both_recipes_coexist_and_django_keeps_its_fingerprint_and_hash` | **Cumple** offline. D095 sin uso real (D151) |
| 10 | Petición del chat ligada a tarea y resultado | `test_chat.py::test_confirmed_proposal_becomes_a_linked_task_planned_executed_reviewed_and_committed`, `::test_http_chat_flow_with_guard_confirmation_and_linked_task` | **Cumple** offline; sin uso real |
| 11 | Proyecto vacío con primera tarea ejecutable; incorporación B adopta P001 conservando código; ambos gestionados | `test_e2e_offline.py::test_create_confirm_restart_then_first_task_and_commit`; `test_typescript_preparation.py::test_new_child_definition_preparation_and_first_task_with_profile_validations`; `test_onboarding_commit.py::test_confirm_one_documentary_commit_preserves_code_and_adopts_p001`, `::test_first_task_uses_confirmed_profile_and_documents`; T016 (`alpha` y `beta` hasta COMMITTED instalados) | **Cumple** (ajustado por D161). B sin uso real (D151) |
| 12 | Backup y restauración con estados, referencias y hashes | `test_backup.py::test_junit_snapshots_events_and_http_queries_survive_restore`, `::test_corrupt_or_incompatible_backup_never_creates_restore`; `test_run_projection.py::test_backup_rejects_a_projection_that_differs_from_the_history`; T016 y `check_distribution` (restauración de consulta) | **Cumple** offline |
| 13 | Fuera de esquema detenido; ciclos sin cambios paran; cursor de eventos sin huecos ni duplicados | `test_engine.py::test_invalid_review_is_retained_without_new_call`, `::test_no_progress_loop_stops_before_another_executor`; `test_typed_json_schema.py`; `test_acceptance_matrix.py::test_event_cursor_resumes_across_a_restart_without_gaps_or_duplicates` | **Cumple** (ajustado por D161: sin SSE legacy; cursor gestionado, D029/D149) |

Requisitos no funcionales (§9) sin cambios respecto de P010 salvo dos ya implementados en P011: migración del paquete
instalado con copia previa (P010-T012, ensayada de nuevo en T016) y CLI bloqueadas por mínimo/capacidades con
diagnóstico (D174). Instalación con versiones exactas por `uv.lock`, `package-lock.json` y `pylock.toml` (D179).

## 4. Hallazgos de esta revisión

| # | Hallazgo | Resolución |
|---|---|---|
| H1 | La ayuda de `--writers-stopped` y el diagnóstico de `migrate` decían «service, observers and writers» (en/es) y un docstring de `storage/backup.py` también: los observadores se retiraron en T019. Pendiente desde T013/T014 | **HITL:** rutas de T017 ampliadas a esos tres archivos; texto alineado con `backup.writers` («service and writers» / «servicio y escritores»). Sin cambio de flag, código ni semántica; nadie compara esos textos |
| H2 | README/README.es no mencionaban la QA de navegador de T024 (nota de T024) | **HITL:** una frase en «Status»/«Estado» de ambos README y en los límites del STATE público: revisada en Chrome en/es, claro/oscuro, escritorio/móvil; sin otros navegadores ni lectores de pantalla |
| H3 | STATE privado en 24.933 bytes, sobre el presupuesto D088 de 24 KiB que T014 decidió mantener | Seguimiento compactado en esta tarea (§7). NEXT_STEPS supera 48 KiB desde antes de T014 (aviso conocido, sin truncar): lo resuelve el archivo de T018 |

## 5. Candidato final

Instantánea pública del árbol de esta tarea: **387 archivos, 5.402.952 bytes**, manifiesto
[`P011-T017_MANIFIESTO_PUBLICO.sha256`](P011-T017_MANIFIESTO_PUBLICO.sha256) con SHA-256
`74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71`, sin problemas (symlinks, ocultos, patrones
privados, enlaces a `docs/archive|phase`). Respecto de T016 cambian 13 rutas, todas explicadas: 7 de T024 (cliente y
su test) y 6 de T017 (dos catálogos, `backup.py`, README, README.es y STATE público). Mismas rutas que T015/T016.
Antes de los cambios de T017, la instantánea de `cde2112` difería de T016 exactamente en los 7 archivos de T024.

| Artefacto | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `46d29c209f90a8f67c02e4295753688ec0c646c5c0f0259575fed5910117d9d6` |
| `harness_local-0.1.0.tar.gz` | `79e256de8a3fa14d29465fbcbaea47b8600908b7b5a1dcfd43b3f6f83cc842c5` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` (sin cambios desde T016) |

Dos builds del mismo árbol dan `SHA256SUMS` idéntico; el build de `cde2112` reprodujo exactamente los hashes del
candidato corregido de T024 (`529e0647…`, `113e50d7…`). El candidato publicado se reconstruye desde el commit de esta
tarea y debe dar este manifiesto (expediente, paso 1); los hashes del wheel solo son comparables en esta plataforma.

## 6. Excepciones y límites declarados

- **Plataforma:** solo macOS ARM64 (Python 3.14.4 en T016/T024; receta Django real histórica con Python 3.13).
  Linux, Windows y otros runners no caracterizados; la CI remota tampoco se ha ejecutado.
- **CLI y proveedores:** mínimos Codex 0.163.0 / Claude 2.1.304 por contrato; posteriores con compatibilidad
  condicionada. Sin CLI real ni inferencia en P011; B y D095 siguen aplazados (D151); A retirado sin validarse.
- **Idioma:** códigos técnicos visibles (acciones, etapas, veredictos, campos de huella; D180); motivos y diagnósticos
  persistidos en el idioma de su emisión (T022); 161 textos técnicos ingleses listados; contenido libre sin traducir.
- **Históricos:** recetas v1, catálogos/snapshots congelados, revisiones Alembic y documentos privados archivados
  conservan su texto (incluido el nombre del perfil privado retirado en evidencias antiguas, fuera del candidato).
- **Seguridad:** contención cooperativa sin aislamiento del SO; servicio local individual con sesión/CSRF; historial
  trazable, no inviolable frente al propietario del equipo.

## 7. Validación de T017

| Comando / check | Resultado |
|---|---|
| `uv run … pytest -q` (paralelo) | 1671 passed, 2 skipped (opt-in con herramientas reales), 29 subtests |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 8 OK |
| `node --test frontend/tests/*.test.mjs` | 95/95 (sin cambios de cliente; tipos/build cubiertos por el build del paquete) |
| `P011-T015_public_candidate.py --revision HEAD` (antes de cambiar) y sobre el árbol final | 387 archivos sin problemas; diferencias con T016 explicadas en §5 |
| `build_distribution.py` ×3 (uno de `cde2112`, dos del árbol final) | Hashes de T024 reproducidos; árbol final con `SHA256SUMS` idéntico en ambos |
| `check_distribution.py` del candidato final | Miembros exactos, metadatos, licencias, `SHA256SUMS` y wheel aislado (UI/API, sesión, definición/tarea/commit/reinicio, errores y evidencia restaurada) correctos; ningún `serve` vivo al terminar |
| `harness-local migrate --help`, `--ui-language es backup-create --help` | «I declare the service and writers stopped» / «Declaro detenidos servicio y escritores» |
| `P011-T014_public_docs_check.py` | 30 Markdown públicos, 249 enlaces; layout, presupuestos y DNNN correctos |
| `P011-T013_links.py` sobre `docs/*.md`, `docs/flows/`, `docs/phase/*.md`, README y README.es | 842 enlaces relativos y anclas, ninguno roto |
| Parsers D088 del producto sobre los documentos privados | 11 fases, 10 criterios de P011, 24 tareas, 181 decisiones con estado; STATE 24.267/24.576 bytes, base 7.832/12.288, NEXT_STEPS 64.518/49.152 (aviso de H3) |
| `git diff --check`; diff de `docs/archive/` y cuerpos D001–D180 | Correcto; sin cambios en archivos congelados (DECISIONS solo añade D181 y su fila de índice) |

No ejecutado: Alembic (sin cambios de esquema), tipos/OpenAPI (sin cambios de API ni cliente), ensayo desde clon
limpio y QA de navegador (válidos de T016/T024, el cambio no los afecta), CI remota, otras plataformas, CLI reales,
proveedores, red, push, tag, Release ni cambio de visibilidad.
