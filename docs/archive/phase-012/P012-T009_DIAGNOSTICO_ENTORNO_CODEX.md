# P012-T009 — Diagnóstico offline del entorno de escritura Codex

Fecha: 2026-10-24. Base: `c7d5ddc`, checkout limpio al empezar.
**Estado: completada offline; continuidad con otro fixture limpio elegida por HITL, sin ejecución real.**
Decisiones: [D191](../DECISIONS.md#d191--p012-t002-incorporación-b-confirmada-y-parada-del-escritor-codex)
y [D192](../DECISIONS.md#d192--p012-t009-entorno-del-escritor-y-continuidad-con-fixture-limpio). T002 conserva su resultado parcial: B COMMITTED y tarea REVISION_LIMIT.

## 1. Hechos y límites de la evidencia

Se leen el TOML aprobado, los artefactos del intento `723ac4fc…` y una copia temporal de SQLite junto con WAL/SHM.
El WAL no está vacío: abrir solo el archivo principal con `immutable=1` no representa el estado final. La consulta
final se hace sobre copias desechables, con conexión `mode=ro`; nunca sobre una conexión escritora a la base original.
No se imprimen prompts completos, credenciales, tokens ni el historial completo en esta entrega.

| Hecho comprobado | Procedencia y alcance |
|---|---|
| Codex recibe solo HOME, LANG, PATH, PYTHONDONTWRITEBYTECODE y USER | Intención `managed_processes.spec`; TMPDIR ausente. El hash del entorno coincide con el TOML aprobado |
| PATH del ejecutor no resuelve `python` | Inspección de rutas con `shutil.which`, sin ejecutar herramientas del fixture; stream con `command not found: python`, exit 127 |
| PATH del validador sí resuelve el Python del venv Django | `[compositions.django]`; ejecutables absolutos y entorno propios, sin compartir automáticamente el entorno del agente |
| `workspace-write`, checkout canónico, `exclude_slash_tmp=true`, red false, approval never y confianza untrusted | Argv congelado; no hay override `exclude_tmpdir_env_var` |
| Git informa que no puede obtener DARWIN_USER_TEMP_DIR y falla creando caché xcrun bajo `/tmp` | Salida de comandos del ejecutor; no demuestra por sí sola que Git entero fallara ni que TMPDIR redirija esa caché |
| El ejecutor declara un rechazo de temporales de heredocs; después falla la verificación de un parche | Mensajes/salida conservados. No está el comando de heredoc rechazado ni una secuencia suficiente para reconstruir el truncamiento |
| Las tres rutas autorizadas tienen 0 bytes y el diff elimina 60 líneas | Lectura por bytes y evidencia de T002 §24; no se restauran ni se revalidan |
| Run REVISION_LIMIT, revisiones 0, límite 0; proceso ejecutor STOPPED y 0 jobs pendientes/activos/inciertos | Consulta sobre copia completa de la base; no se cambia el límite ni se encola nada |

Identidades saneadas para contrastar sin copiar los originales:

| Contenido | SHA-256 |
|---|---|
| TOML operativo original | `d882c42d1385599279e740fce9a687905b4ae51330cf07767bcedb1cc72c3843` |
| Entorno del ejecutor congelado | `e671ce03832f522a7982706ae2a58ca864b83993fd9279ddb0f2e447484c39e8` |
| Stdout del ejecutor, 7589 bytes | `89d2352ef6a746fbddca30f523848562fba7f661c97944b49a3da089284b7ccd` |
| Diff de revisión de T002, 2545 bytes | `1651c973dd3913b938e317029a30f72102c880559500ff3fc66b4aff8806be1e` |

**Conclusión:** hay un prerrequisito operativo ausente demostrado (`python` en el PATH del escritor) y una
omisión de temporales explícitos compatible con el problema reportado. No hay causa raíz demostrada para los
archivos vacíos ni defecto del harness acreditado. Añadir TMPDIR/PATH es una propuesta para trabajo nuevo;
no es una corrección probada del truncamiento ni garantiza que la caché xcrun deje de usar `/tmp`.

## 2. Fronteras del producto y Codex

- `adapters/cli_agents.py`, `CLIProcessAdapter.invoke`: pasa `env=dict(config.environment)`;
  no hereda el TMPDIR del servicio, el PATH de la sesión ni las variables de `[compositions.django]`.
  La intención sella claves/hash del entorno antes del efecto. `argv_for` conserva las guardias D059/D068.
- `adapters/commands.py`, `ManagedCommandRunner`: resuelve los nombres del perfil con el mapa de ejecutables y
  usa el entorno de la composición, más los overrides del comando. Que las preparaciones encuentren Python
  no prueba que el escritor lo encuentre. El ejecutor no usa este runner para sus comandos internos.
- [D059](../DECISIONS.md#d059--diagnóstico-del-escritor-codex-y-raíces-explícitas-cli-7) y su
  [diagnóstico archivado](../archive/phase-007/CODEX_WRITER_ROOTS.md) conservan el comportamiento predeterminado
  de la CLI para TMPDIR explícito, excluyen la concesión amplia de `/tmp` y no prometen una única raíz efectiva
  para cualquier TMPDIR del operador. No se añade una raíz padre ni se cambia `exclude_slash_tmp`.
- [D068](../DECISIONS.md#d068--condición-de-confianza-del-pin-acreditada-y-supresión-específica-cli-9) acredita
  una versión histórica; [D174](../DECISIONS.md#d174--p011-t012-clientes-automáticos-y-compatibilidad-condicionada)
  admite posteriores bajo el contrato conocido, con efectos internos sin verificar. Las pruebas falsas del
  transporte no certifican qué permisos renderiza/aplica Codex 0.164.0, qué shell usa o dónde escribe xcrun.
- La lectura local y la documentación histórica bastan para formular esta propuesta condicional. Se aplica
  OpenAI Docs con el límite offline de T009: no se consulta la web ni se lanza Codex para investigar su versión.

## 3. Continuaciones existentes: por qué el run fallido no se relanza

| Vía del producto | Resultado para este caso |
|---|---|
| Reintentar el run original con su composición | `OfflineEngine.resume`: ya hubo ejecución y `revisions >= max_revision_cycles` (0 >= 0); devuelve revision_limit antes de invocar o preparar. No repone presupuesto |
| Revalidar el run original | Conserva código y contrato; repite preparaciones/validaciones y una revisión, sin ejecutar ni corregir. No solventa tres archivos vacíos y consumiría Claude |
| Cambiar entorno y reusar el job/run | `LocalComposer._composed` compara versiones/huellas congeladas; composición distinta se rechaza antes de efectos. No se edita el snapshot para adoptar el entorno |
| Encolar otro run en el mismo checkout sucio | `OfflineEngine.start`, documentos v2: rechaza cambios previos antes de preparar/planificar; evita mezclar el diff fallido con otra ejecución |
| Restaurar archivos, aumentar el límite o cambiar SQLite | Contraviene la conservación y los límites acordados; no es la continuación propuesta |

Fuentes: `core/engine/workflow.py` (`start`, `resume`), `services/local_config.py` (`compose`, `_composed`),
`storage/managed.py` (`resume`) y [flujo de tarea vigente](../flows/task-run.md). No se cambia ese flujo, modelos,
migraciones, permisos, codec o producto. No procede abrir una tarea de corrección de código con la evidencia actual.

## 4. Propuesta concreta para trabajo nuevo, todavía sin autorizar

La continuación viable sin reparar el fallo es **otro fixture sintético limpio y otra incorporación B**, conservando
la ruta, HEAD, diff, archivos, venv, historial y registro originales. Repite parte de B; la elección requiere HITL
porque T001 solo fijó un fixture. **El usuario elige esta alternativa en T009**; no se crea ni se opera el nuevo hijo.
La elección confirma el diseño de continuación, sin conceder el consentimiento operativo posterior.

Sea `AREA=$HOME/Documents/harness-validation/p012-20261024` y
`B2=AREA/projects/onboarding-b-t009`. Ampliación propuesta:

1. Crear B2 sin enlaces ni contenido previo a partir del commit inicial **`f6a2d9d`** del fixture sintético,
   anterior a la incorporación. Clonar localmente sin checkout ni optimización local (`git clone --no-local
   --no-hardlinks --no-checkout` desde la ruta local original a B2), retirar el remoto origin solo de B2 y hacer
   checkout detached del commit completo `f6a2d9dc054725b2cd1f9e323bf387ce092925c2`. Comprobar commit/árbol/modos
   contra la base y ausencia de remotos, alternates o enlaces al original; no copiar archivos no versionados.
   No copiar el checkout sucio, `.venv`, `.local`, SQLite ni documentos generados en B. No hacer reset/stash del original.
2. Preparar `B2/.venv` con Python 3.13.13 y los mismos 17 wheels por hashes del lock, offline. Crear únicamente
   `B2/.local/codex-tmp` con modo 0700; `.local/` ya está ignorado en la base, comprobarlo sin cambiar `.gitignore`.
   TMPDIR queda **dentro del checkout autorizado**, sin conceder otra raíz efectiva fuera de él, y separado de
   `AREA/tmp` (temporales del servicio/evidencia). No se modifica la lista de rutas que el contrato deja editar.
3. Escribir una **copia nueva** `AREA/config/harness-local-t009.toml`, modo 0600, conservando el original por bytes.
   Conservar service/state, Git, defaults `[agents.*]`, registro, perfiles, recetas y composiciones existentes.
   Añadir solo dos presets y una composición nueva según el siguiente delta; no cambiar agentes del proyecto viejo.
4. Usar el wheel/venv ya verificado de T008 (`6efbd82`, `dist-t008`/`venv-t008`): no cambia producto y no requiere
   reconstrucción. Cargar la nueva configuración de forma pura, comprobar que `p012-b` conserva sus huellas,
   que los destinos son nuevos y que el único cambio efectivo del escritor nuevo es PATH/TMPDIR.
   Cualquier deriva de CLI/identidad, guardia o hash obliga a parar, no a actualizar o adoptar el job antiguo.
5. Bajo consentimiento posterior, preflight explícito de la copia, ocho checks iniciales del nuevo fixture y servicio
   en 8024 con el mismo entorno explícito de T001. Alta desde UI como **`p012-b-t009`**, composición `django-t009`,
   presets `claude-t009`/`codex-t009`, idiomas es/es y misma política (plan agent, catálogo gpt-6-luna/low, 0 correcciones).
   Repetir B por UI y una tarea con los mismos criterios funcionales de D191, sin reparar o reintentar el run viejo.

### Delta exacto de entorno y selección

`agent_presets.claude-t009`: copia de las capacidades operativas de `[agents.reviewer]` de T001, sin claves
`model`/`effort`; añadir `roles=["reviewer"]`, `models=["sonnet"]`, `efforts=["low"]`,
`allow_open_executor=false`. Proveedor, ejecutable, timeout y entorno idénticos al revisor original.

`agent_presets.codex-t009`: copia de `[agents.executor]` de T001; añadir `roles=["executor"]`,
`models=["gpt-6-luna"]`, `efforts=["low"]`, `allow_open_executor=false`. Proveedor, ejecutable y timeout idénticos.
Sustituir **solo** su entorno por esta tabla completa (expandir B2 al materializar, sin variables literales TOML):

```toml
[agent_presets.codex-t009.environment]
HOME = "$HOME"
USER = "acosta"
PATH = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b-t009/.venv/bin:$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin"
TMPDIR = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b-t009/.local/codex-tmp"
LANG = "C.UTF-8"
PYTHONDONTWRITEBYTECODE = "1"
```

`compositions.django-t009`: copia completa de `compositions.django`, mismo perfil y autorizaciones. Sustituir
`projects/onboarding-b/.venv/bin` por `projects/onboarding-b-t009/.venv/bin` en sus cuatro ejecutables y su PATH;
mantener literalmente el resto, incluido su TMPDIR `AREA/tmp`, HOME privado y DJANGO_SETTINGS_MODULE.
No añadir preparación/formateador, grants, red, variables globales ni paquetes. Los presets nuevos se seleccionan
solo para el nuevo registro; los defaults y la composición de `p012-b` siguen iguales.

La carga sin procesos admite presets adicionales sin cambiar la composición efectiva de un proyecto que hereda
los defaults: `compose` incluye solo su composición y los presets seleccionados. Debe comprobarse antes de arrancar;
no se da por acreditado el futuro arranque/UI o la composición operativa de B2 por una prueba sintética.

## 5. Consentimiento posterior propuesto y paradas

Confirmar esta alternativa en HITL **solo elige la propuesta**, no autoriza ejecutarla. La solicitud de operación
posterior debe cubrir explícitamente B2, la copia del TOML, presets/composición, preparación offline, preflight,
servicio/UI e incorporación/tarea nuevas en la misma base SQLite, sin editarla directamente. Su historial se amplía
por las API normales; los registros previos no se reescriben. El TOML original, B, sus artefactos y distribuciones
se conservan. No hay reemplazo de candidato público ni build nuevo.

Consumo acumulado **Claude 4/12 y Codex 1/3**; saldo **8 Claude y 2 Codex**, sin reiniciar contadores. Previsión de
la alternativa: hasta dos turnos B + plan + revisión = **4 Claude**, una ejecución = **1 Codex**, cero correcciones.
Un turno extra no es automático; queda fuera del guion y exige decidir antes de consumirlo. Mantener los límites
de tiempo de T001 (por llamada: Claude 1800 s, Codex 3600 s; sesión T002 de hasta 4 h), sin fallback de pareja,
modelo o esfuerzo. No repetir la prueba de reenvío ya acreditada para B, salvo requisito nuevo autorizado.

Parar al primer fallo de identidad/preflight, caché, permisos/temporales, validación, esquema, proveedor, timeout,
CAS/hash o cuarentena. Conservar lo producido y detener el servicio sin jobs/locks activos, con confirmación de
parada de procesos inciertos si procede; no restaurar resultados, conceder `/tmp`, reparar a mano o reintentar.
Si el nuevo stream vuelve a fallar con temporales explícitos, conservar el hecho y abrir diagnóstico separado;
no atribuir de antemano éxito a esta propuesta. T003/T004, red adicional, instalaciones globales, push, tags y
publicación siguen fuera del consentimiento propuesto.

## 6. Verificación de esta tarea

- **11 tests existentes correctos**: argv/raíces y escapes (3), presupuesto agotado, revalidación sin ejecutor,
  contexto cambiado, cero correcciones, composición sin procesos, cuarentena por composición/layout (2) y
  rechazo de checkout sucio. Puerto/servicio/proveedores reales no intervienen. Un aviso existente de
  deprecación Starlette/httpx en la prueba documental.
- [Comprobador reproducible](P012-T009_CHECK_ENVIRONMENT.py): configuración sintética v7 derivada del TOML
  documental T001, ejecutables de marcador que nunca se lanzan, `subprocess.Popen` bloqueado. Carga sin procesos,
  huellas originales idénticas al añadir presets/composición, selección nueva válida, solo PATH/TMPDIR distintos,
  Python resoluble, TMPDIR 0700 dentro del checkout, entorno de validación separado y límite de correcciones 0.
  No prueba el arranque con CLI reales ni instala/ejecuta el Python de marcador.
- Consulta sobre copias temporales de SQLite/WAL/SHM: estado y entorno congelado contrastados; hashes de los
  siete originales leídos (TOML, base/WAL/SHM y tres artefactos del ejecutor) iguales antes/después de la consulta.
  Los tres archivos fallidos siguen vacíos. No se ejecutan sus tests ni sus validaciones.
- Parsers: **12 fases, 9 tareas y 192 decisiones**; **580 enlaces/anclas relativos** válidos en los cinco Markdown
  modificados/nuevos. Base acumulada y cuerpos D001–D191 conservados, sin cambios en archivos históricos,
  documento T001/T002, fuentes, flujos, esquema o baseline pública. Presupuestos STATE/base/NEXT_STEPS dentro
  de 24/12/48 KiB; `git diff --check` correcto.

Comandos de los checks dirigidos:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_codex_workspace_write.py::test_writer_root_is_canonical_and_toml_escaped tests/product/test_engine.py::test_revision_budget_is_not_replenished_by_resume_or_explicit_retry tests/product/test_engine.py::test_revalidation_is_new_review_without_executor_or_replanning tests/product/test_engine.py::test_resume_rejects_changed_context_and_unrelated_changes_without_erasing tests/product/test_engine.py::test_zero_revision_budget_keeps_initial_execution_and_review tests/product/test_local_config.py::test_valid_configuration_composes_fresh_ports_without_processes tests/product/test_local_config.py::test_changed_composition_after_admission_quarantines_before_effects
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_documents.py::test_executor_cannot_edit_harness_documents_and_dirty_checkout_never_starts
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P012-T009_CHECK_ENVIRONMENT.py
```

Una primera versión desechable del check puro seleccionó el bloque TOML de selección en vez del TOML completo
T001 y terminó con `KeyError: recipes`; se corrigió la selección por `format=local-config-7` antes del pase válido.
No se interpretó como fallo del producto ni motivó cambios operativos.
No se ejecutan CLI/proveedores reales, servicio, navegador, revalidaciones, tests del fixture fallido ni suites
completas. No se cambia producto, TOML operativo, SQLite original, confianza, red, modelos/esfuerzo o configuración global.
