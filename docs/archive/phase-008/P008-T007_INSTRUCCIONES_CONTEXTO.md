# P008-T007 — Instrucciones del proyecto en el contexto congelado

Fecha: 2026-10-16. Base: D088 punto 8, D066 y D068. Decisión: [D094](../DECISIONS.md#d094--p008-t007-agentsmd-en-el-prompt-congelado-de-cada-rol).

## Verificación de los flags, sin ejecutar proveedores

Ninguna CLI se ejecutó, ni siquiera `--help`. Fuentes: bytes del nativo instalado, fuente pública del pin y
documentación oficial. Las copias descargadas quedaron fuera del repositorio, como datos.

### Codex 0.162.1

- Nativo instalado: `@openai/codex-darwin-arm64` 0.162.1, 246642624 bytes, SHA-256
  `74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0` (el mismo de D059/D062). Sus literales
  contienen `codex_core::agents_md`, `agents_md.discover`/`agents_md.load`, `AGENTS.override.md`, `AGENTS.md` y
  `project_doc_max_bytes = 32768`.
- Fuente del commit `092d3acd6bec3e3a14bdc7e7a2810ab628ab759d` (etiqueta rust-v0.162.1, D068):
  - `codex-rs/core/src/agents_md.rs` (SHA-256 `97427a87…5fc78`). En las líneas 58–66,
    `load_project_instructions` sale sin buscar archivos del proyecto si `config.active_project.is_untrusted()`.
    Después recorre desde la raíz del proyecto (marcador `.git`) hasta el cwd con el presupuesto
    `project_doc_max_bytes`; prueba `AGENTS.override.md` antes que `AGENTS.md`. Con presupuesto 0, el bucle se
    corta (líneas 70–71) y `read_agents_md` devuelve `None` (líneas 133–135).
  - `codex-rs/config/src/config_toml.rs` (SHA-256 `aaf8e8e8…f7d84`). En las líneas 614–616, `is_untrusted` solo es
    cierto con `trust_level = untrusted` explícito. Según las líneas 907–921, sin tabla `projects` no hay proyecto
    activo.
  - `codex-rs/core/src/config/mod.rs` (SHA-256 `32babb11…94259`). Las líneas 3478–3483 dan `trust_level: None`
    cuando no hay entrada; la 4380 fija `project_doc_max_bytes` por defecto en `AGENTS_MD_MAX_BYTES`.
- `--ignore-rules` solo omite los archivos execpolicy (ya documentado en
  [D061](../archive/phase-007/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md)) y no interviene en `AGENTS.md`.

Conclusión para Codex: el **escritor**, que lleva `projects={<checkout>={trust_level="untrusted"}}` (D068), no
carga el `AGENTS.md` del proyecto. El **lector** no lleva entrada de confianza y `--ignore-user-config` deja fuera
la tabla `projects` del usuario. Por eso lo carga desde el checkout vivo, sin hash, y antepone un
`AGENTS.override.md` si existe. Esto se deduce de la fuente y no se ha observado en ejecución. La configuración
gestionada del sistema, si existiera, podría declarar `projects`; no se ha comprobado.

### Claude

- La documentación oficial actual (Agent SDK, «Use Claude Code features in the SDK», consultada el 2026-10-16) dice
  que `settingSources` vacío desactiva las fuentes user, project y local. `CLAUDE.md` del proyecto y
  `.claude/rules/*.md` solo se cargan si se incluye `project`, y esa fuente carga también el `settings.json` y los
  hooks del proyecto. La memoria automática no depende de esa opción y sigue apagada por `autoMemoryEnabled=false`
  (D066).
- Los pins 2.1.295/2.1.296 ya no están instalados (en la máquina hay 2.1.299–2.1.301, fuera de `SUPPORTED`). La
  comprobación de Claude se basa en la documentación vigente y no en el binario fijado.

Conclusión para Claude: con `--setting-sources ""` no se carga `CLAUDE.md`, y por tanto tampoco el `@AGENTS.md`
que importa. Activar `project` traería `settings.json` y hooks del checkout, así que no es seguro y no se cambia.

## Entrega

- `core/engine/documents.py`: `project_instructions(context)` lee `AGENTS.md` de la raíz en cada intento. Usa
  `O_NOFOLLOW` sobre la ruta del checkout, que ya rechaza enlaces; exige un archivo regular, UTF-8, no vacío, sin NUL
  y de 32 KiB como máximo (el presupuesto por defecto de Codex), sin truncar. Devuelve el texto con ruta, SHA-256 y
  tamaño. Un contexto sin layout (congelado antes de D088) recibe un texto fijo de ausencia.
  `DOCUMENT_LAYOUT = "d088-5"`.
- `core/engine/prompts.py`: variable `{{PROJECT_INSTRUCTIONS}}` en `plan-task`, `execute-task`, `review-task`,
  `revise-task`, `close-phase`, `chat-turn` y `plan-phase`. La aporta solo `render_attempt`, que rechaza el valor si
  viene del llamador. El snapshot del intento guarda `project_instructions` (ruta, hash y bytes) y el texto en las
  variables de la parte. Las versiones anteriores sin la variable (catálogos congelados y versiones guardadas)
  siguen validando y leyéndose. Con layout no pueden invocar: el intento se detiene en `prompts` y pide activar una
  versión con la variable.
- Plantillas: un bloque `<project-instructions>` común. Las reglas del harness y las entradas congeladas prevalecen
  si hay conflicto, y las instrucciones no conceden rutas, herramientas, permisos ni efectos. Siete prompts nuevos
  por hash.
- `adapters/cli_agents.py`: `cli-11` añade `-c project_doc_max_bytes=0` a toda invocación Codex. El lector deja de
  cargar su propia copia viva, y así el único `AGENTS.md` que ven los roles es el congelado y con hash. Para el
  escritor no cambia nada (ya lo omitía). Los flags de Claude no cambian. Los controles de memoria de D066 se
  conservan.
- Quedan fuera `define-project`, porque esa conversación redacta `AGENTS.md` y su borrador o el de la plantilla ya está
  en su contexto, y `bootstrap-project`, retirada. `reconcile-phase` lo recibe a través de `execute-task`.

## Verificación

- `tests/product/test_project_instructions.py`: 28 casos nuevos.
  - Los siete roles renderizan `AGENTS.md` con su hash en el snapshot; la definición no lo lee.
  - Siete formas de archivo inválido detienen el intento; el límite exacto se admite completo.
  - Un contexto sin layout recibe la ausencia explícita, y un valor aportado por el llamador se rechaza.
  - Las versiones anteriores siguen leyéndose, pero no invocan sobre un proyecto.
  - Recorrido con Git y SQLite temporales: los intentos de una tarea congelan `AGENTS.md`. Tras cambiarlo y hacer
    commit, el check de fase usa el hash nuevo y los snapshots anteriores no cambian.
  - Un proyecto sin `AGENTS.md` se detiene en `prompts` sin ninguna petición al agente.
  - Codex lleva `project_doc_max_bytes=0` en todos los roles y versiones, y Claude conserva `--setting-sources ""`.
- Literales de versión actualizados en siete pruebas (`cli-11`). La prueba de configuración comprueba además que un
  job congelado con `d088-4` no recibe puertos ni escritor (cuarentena). La recuperación de transiciones selladas
  se prueba contra `d088-5`.
- Primera suite completa: 1.147 OK y 17 fallos, todos de checkouts v2 de prueba sin `AGENTS.md`. Eran el fixture
  `web` de TypeScript, que usan la composición local y las matrices de proveedores, y una prueba HTTP de fases. A
  ambos se añadió un `AGENTS.md` sintético, y sus archivos se re-ejecutaron con 46, 101 y 18 OK.
- Suite completa final: 1.192 OK y 121 subtests; único aviso, la deprecación conocida de Starlette/httpx.
  `unittest`: 12 checks ligeros OK.
- Documentos: 242 enlaces relativos y anclas válidos en los siete Markdown editados o nuevos, y DECISIONS indexa
  94 decisiones sin duplicados con `decision_index`. El diagrama de secuencia de `flows/task-run.md` pasa el parser
  Mermaid 11.17.2 local; la primera versión de la nota, con `;`, lo rompía y se corrigió. El diagrama de estados, sin
  cambios, falla en ese proceso sin DOM por el sanitizador, igual que en `HEAD`.
- Sin pruebas Node, build ni `alembic check`, porque no cambian UI, OpenAPI, modelos ni migraciones. No se arrancó el
  harness sobre este checkout ni se ejecutaron proveedores, smokes, push o publicación.

## Límites

- No hay observación en ejecución de ninguna CLI. La evidencia de Codex es la fuente del pin; la de Claude, la
  documentación vigente sin el binario fijado. Codex 0.161.0 (solo lector) no se ha leído en fuente. La clave
  `project_doc_max_bytes` se transmite igual y su aceptación con `--strict-config` queda sin acreditar para esa
  versión.
- El `AGENTS.md` global de Codex (`codex_home::instructions`) y la configuración gestionada del sistema no se han
  analizado; esta tarea no los cambia.
- Un job de transición sellado con `cli-10` y adaptador CLI real ya no se reanuda: el adaptador forma parte de las
  versiones congeladas, igual que ocurrió con `cli-9 → cli-10` en T003. La excepción de D092 solo cubre
  `document_layout`.
- `plan-phase` recibe `AGENTS.md` dos veces: en la variable nueva y entre los documentos de su contexto congelado
  (D092). Esos bytes salen de `storage/planning.py`, fuera de las rutas de esta tarea.
