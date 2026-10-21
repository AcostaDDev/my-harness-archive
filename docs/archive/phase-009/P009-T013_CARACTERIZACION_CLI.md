# P009-T013 — Caracterización de Codex 0.163.0 y Claude 2.1.304

Fecha: 2026-10-20. Decisión [D122](../DECISIONS.md#d122--p009-t013-codex-01630-y-claude-21304-en-el-baseline-cli-12).
Base: `43676a4` (T006). Autorización: [propuesta de T006](P009-T006_PROPUESTA_PILOTO.md), §§1 y 6 (D121).

## Resultado

Las dos versiones fijadas para el piloto entran en el baseline del transporte `cli-12` **sin cambiar argv,
protocolo, salidas ni controles**. Codex 0.163.0 queda admitido también como escritor. Las versiones anteriores
siguen admitidas y cualquier otra, incluidas las Claude 2.1.299–2.1.301 que hay en disco, se sigue rechazando.

| Constante | Antes | Ahora |
|---|---|---|
| `SUPPORTED["codex"]` | 0.161.0, 0.162.1 | 0.161.0, 0.162.1, **0.163.0** |
| `WRITE_SUPPORTED["codex"]` | 0.162.1 | 0.162.1, **0.163.0** |
| `SUPPORTED["claude"]` = `WRITE_SUPPORTED["claude"]` | 2.1.295, 2.1.296 | 2.1.295, 2.1.296, **2.1.304** |

Se mantiene `cli-12` porque la forma de la invocación no cambia; la versión exacta de cada CLI ya se congela
por rol en cada job (`reviewer_cli`, `executor_cli`), así que jobs y snapshots anteriores conservan su identidad.

## Procesos ejecutados

Solo las sondas autorizadas, con entorno explícito (`HOME`, `USER`, `PATH=/usr/bin:/bin`, `LANG`), stdin vacío
y cwd temporal vacío; sin llamadas a modelos. Todas terminan con exit 0 y stderr vacío.

| Binario fijado (SHA-256 sin cambios desde T006) | Orden | Salida |
|---|---|---|
| Codex nativo `8813367285524ac7…cfdee31` | `--version` | `codex-cli 0.163.0` |
| | `exec --help` | 4.331 bytes, SHA-256 `df0d864ca2076f76…0c70986c` |
| | `--help` | 5.849 bytes, SHA-256 `4a7f0188d4d6e6d8…a403c0071e` |
| Claude `2.1.304` `b9ac5374839f14ab…aab78e6a` | `--version` | `2.1.304 (Claude Code)` |
| | `--help` | 22.319 bytes, SHA-256 `b10f5c36adfe3285…312a7fbc` |

Las líneas de versión encajan exactamente con los patrones del preflight. Las ayudas de `exec --help` y de Claude
se guardan como [fixtures](../../tests/fixtures/cli_help/): son texto público sin rutas ni datos de la cuenta.
Ambas anuncian todos los flags requeridos de lectura y escritura, además de los que usa el argv
(`--color`, `--cd`, `--skip-git-repo-check`, `-c`). El vocabulario de esfuerzo de Claude que lista la ayuda
(`low, medium, high, xhigh, max`) coincide con `EFFORTS["claude"]`.

## Codex 0.163.0: fuente del pin

Mismo método que D068. La API pública resuelve `rust-v0.163.0` al objeto de etiqueta
`129b8ec7ee6f4511557a4856279f529025c25af4` (unsigned) y al commit `83086188ae0614bd882818ff1aa23f3194962012`,
que aparece como literal en el binario nativo, offset 189669691. Esto enlaza versión, fuente y binario; no
demuestra una build reproducible. Se descargaron en el scratchpad los tarballs de ese commit y del pin anterior
`092d3acd…` (SHA-256 `e57f1d4f…` y `79c8ea85…`) y se compararon en lectura, sin compilar ni ejecutar nada.

| Pieza del transporte | Comparación 0.162.1 → 0.163.0 |
|---|---|
| Guardia de `thread/start` que persiste confianza (D068) | Bloque idéntico (se desplaza 14 líneas): cwd explícito, `trust_level` ausente, no projectless y permisos que escriben el cwd. La entrada `untrusted` del transporte sigue eliminando la segunda condición. |
| Parser de overrides `-c` (`config/src/overrides.rs`) | Idéntico: la tabla `projects` inline sigue siendo necesaria. |
| `exec/src/cli.rs`, `exec_events.rs`, `event_processor_with_jsonl_output.rs` | Idénticos: flags de `exec` y eventos JSONL (`turn.completed`, `turn.failed`, `item.completed`/`agent_message`) sin cambios. |
| `exec/src/lib.rs` | Solo campos nuevos de arranque con valor `None`; los overrides CLI se siguen transmitiendo igual. |
| `ReasoningEffort` | Enumeración idéntica; `EFFORTS["codex"]` no cambia. |
| Claves usadas en `ConfigToml` (`project_doc_max_bytes`, `history`, `memories`, `features`, `web_search`, `sandbox_workspace_write`, `projects`, `approval_policy`, `model_reasoning_effort`, `model_provider`) | Presentes; `MemoriesToml`, `HistoryPersistence`, `History` y `SandboxWorkspaceWrite` idénticos. Ningún archivo que consume `use_memories`, `generate_memories`, `Feature::Memories` o `HistoryPersistence::None` cambia. |
| Carga de AGENTS.md (`core/src/agents_md.rs`, `codex-home/src/instructions`) y usos de `project_doc_max_bytes` | Idénticos. |
| Cargador de configuración | Solo cambia la ruta opt-in de `credential_masking`, que el transporte no activa. |
| Permisos y sandbox | La lectura de los alias `arg0` del runtime pasa a otra función; `SandboxOverride` se mueve al protocolo con la misma semántica: solo una escalada aprobada amplía permisos, y el transporte usa `approval_policy="never"` e `--ignore-rules`. |

Se comprobaron además los literales de memoria, sandbox, esfuerzos y eventos en el binario nativo.

## Claude 2.1.304: ayuda y literales

Claude no tiene fuente pública; el método es el de D066: ayuda de la versión y literales del binario fijado.
`--restricted` mantiene la semántica que usa el lector (sin herramientas de ejecución, ajustes de usuario/proyecto
ignorados y archivos confinados al directorio de trabajo); `--permission-prompts none` deniega lo que pediría
permiso; `--setting-sources`, `--settings`, `--json-schema`, `--no-session-persistence` y `--no-chrome` siguen
descritos como antes. El binario contiene `autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, `disableAllHooks`,
`structured_output`, `is_error` y los cinco subtipos de `result` que acepta el parser de streams.

## Pruebas

[test_cli_baseline.py](../../tests/product/test_cli_baseline.py), 30 casos, con CLI sintéticas salvo las ayudas reales:

- Baseline exacto; vecinos no caracterizados (Codex 0.162.2/0.164.0; Claude 2.1.299/2.1.300/2.1.301/2.1.303) rechazados.
- Para los ocho roles y ambos proveedores, el argv con la versión nueva es idéntico al de la versión anterior,
  incluidos la confianza `untrusted`, raíces, red y memoria del escritor Codex.
- El escritor Codex 0.161.0 sigue rechazado y el mensaje nombra 0.162.1 y 0.163.0.
- Preflight de lectura y escritura con las ayudas reales y las líneas de versión nuevas: disponible.
- Cuatro parejas por el adaptador real, configuración local y supervisor con las versiones nuevas: ACCEPTANCE_READY,
  con la versión de cada proceso igual a la congelada y a la observada por el preflight.

Suite offline completa: **1.577 tests y 121 subtests correctos, una omisión** (la variante Django real de T005,
que exige rutas explícitas de Python y wheelhouse), en tres particiones disjuntas de 527/527/526 casos con
`--basetemp` propio; duración máxima 13 min 54 s. `python3 -m unittest discover`: 12 checks correctos.
340 enlaces/anclas relativos de los documentos tocados válidos; `git diff --check` correcto. Sin Node/build,
Alembic ni OpenAPI: no cambian frontend, esquema ni API. Ni wheel operativo, ni servicio, ni piloto.

## Límites

- Sin observación en ejecución: el efecto real (escrituras de confianza, memoria, streams) se comprobará en el piloto,
  como en D071. Tampoco se certifica la ausencia de otras persistencias auxiliares, igual que en D068.
- Claude 2.1.296 ya no está en disco, por lo que su ayuda no se ha podido comparar byte a byte con la de 2.1.304;
  la compatibilidad se apoya en flags, descripciones y literales. El binario contiene subtipos de evento
  `model_fallback`/`model_refusal_fallback`. No son terminales `result`; el harness registra los modelos que
  informa cada mensaje (`message_models`), de modo que un cambio de modelo quedaría visible en la evidencia del piloto.
- Las versiones antiguas siguen admitidas sin binarios en disco; solo sirven para leer historiales y configuraciones previas.
- Los scripts históricos de `examples/first_use` y `examples/provider_matrix` conservan sus versiones de entonces.
