# P009-T006 — Propuesta operativa del piloto Django

Fecha: 2026-10-20. Decisión [D121](../DECISIONS.md#d121--p009-t006-propuesta-del-piloto-y-caracterización-previa-de-cli).
Base: `074185a` (T005). Aplica D050/D051/D052/D115–D120. Selecciones del usuario recogidas en esta sesión;
no se heredan las de D050/D071 salvo donde el usuario las ha confirmado expresamente.

**Estado:** propuesta y consentimiento registrados en D121. Nada se ha instalado, creado ni ejecutado en T006:
sin wheel, área de operación, TOML, servicio, preflight ni proveedores. Solo lecturas del sistema de archivos
(versiones de paquetes, enlaces, hashes, existencia del destino y puertos en escucha).

## 1. Bloqueo constatado: CLI fuera del baseline

`cli_agents.SUPPORTED` admite Codex 0.161.0/0.162.1 (escritura solo 0.162.1) y Claude 2.1.295/2.1.296. Lo
instalado, leído sin lanzar procesos:

| CLI | Versión | Ruta fijada para el piloto | SHA-256 (2026-10-20) |
|---|---|---|---|
| Codex | 0.163.0 (`package.json` del paquete npm) | `$HOME/.nvm/versions/node/v24.15.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex` | `8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31` |
| Claude | 2.1.304 (binario versionado; también 2.1.299–2.1.301) | `$HOME/.local/share/claude/versions/2.1.304` | `b9ac5374839f14abf3f1f45610637c332b5daee5ce0d1634726cef87aab78e6a` |

No queda ninguna versión caracterizada en disco, y `check-config` las rechazaría. El usuario elige caracterizar
las versiones actuales en una tarea de producto previa, [P009-T013](../NEXT_STEPS.md#p009-t013--caracterizar-las-cli-instaladas-para-el-piloto),
que se ejecuta antes de T007. Se fija el binario nativo de Codex, no el lanzador `codex.js`, que necesitaría `node`
en PATH, y el binario versionado de Claude, no el enlace `~/.local/bin/claude`, que se actualiza solo (precedente D050).
Si el hash de cualquiera de los dos cambia antes de terminar T012, el piloto se detiene.

## 2. Selecciones del usuario

| Elemento | Selección |
|---|---|
| Carpeta de proyectos (elegida en la UI, T007) | `$HOME/Documents/projects/` |
| Proyecto hijo | `harness-django-pilot`; destino `$HOME/Documents/projects/harness-django-pilot`, inexistente el 2026-10-20 |
| Área de operación persistente | `$HOME/.local/share/harness-local/`, inexistente el 2026-10-20 |
| Revisor Codex (T007 definición, T008, T009) | `gpt-6-luna` / `medium` |
| Revisor Claude (T010, T011, cierre T012) | `claude-sonnet-5-5` / `medium` |
| Ejecutor Codex, modo `catalog` | `gpt-6-luna` × {`low`, `medium`, `high`} |
| Ejecutor Claude, modo `catalog` | `claude-sonnet-5-5`, `claude-opus-5-5` × {`low`, `medium`, `high`} |
| Paquetes de la receta | wheelhouse offline previo con los 17 wheels del lock, verificados por hash; `allow_network = false` |
| Correcciones y tiempos | `max_revision_cycles = 2`; timeout de 1800 s para el revisor y de 3600 s para el ejecutor |

Planificación `agent` en todas las tareas. El revisor elige el modelo/esfuerzo concretos del ejecutor y el motivo
dentro del catálogo; una elección fuera del catálogo falla sin fallback (D052/D118). Los modelos son nombres del
catálogo local: el producto no comprueba de antemano que estén disponibles en la cuenta.

## 3. Área de operación y servicio

Detalles reversibles fijados con criterio (D051). Todo vive fuera de los checkouts; no se toca configuración global.

| Ruta bajo el área | Contenido |
|---|---|
| `config/harness-local.toml` | `local-config-5`, chmod 600, sin secretos |
| `state/` | `state_dir` del servicio: artefactos/streams privados de agentes |
| `state/harness.sqlite3` | SQLite operativa (`init-db`), con backups del producto |
| `dist/` | sdist, wheel y `requirements.txt` construidos con `scripts/build_distribution.py --out-dir` |
| `venv/` | venv nuevo con instalación offline por hashes (`uv pip sync --require-hashes`, wheel `--no-deps`) |
| `wheels/` | 17 wheels de la receta, descargados de PyPI y verificados contra el lock empaquetado |
| `home-commands/` | HOME privado de los comandos del perfil |

- Servicio: `harness-local serve --database …/state/harness.sqlite3 --config …/config/harness-local.toml --port 8031`,
  en loopback, con `supervisor = true` para que procese la cola. Puerto 8031 y 8032 libres el 2026-10-20 (dev usa 8013/5173).
- Django para QA en T007 y T012: `.venv/bin/python manage.py runserver 127.0.0.1:8032 --noreload` desde el hijo,
  lanzado por la operación y detenido al terminar. No forma parte de la receta ni del perfil.
- Git: `/usr/bin/git`, autor con la identidad Git del usuario (`user.name`/`user.email`); tags `lightweight`.
- Agentes: `HOME=$HOME`, `USER=acosta`, `PATH=/usr/bin:/bin`, `LANG=C.UTF-8` y `PYTHONDONTWRITEBYTECODE=1` (D119).
  Ejecutor Claude con `Read`, `Edit`, `Write`, `Glob`, `Grep`, sin `Bash` ni concesiones; ejecutor Codex en
  `workspace-write` sin red. Revisores en solo lectura con su inventario fijo.
- Registro: `roots = []` (la raíz llega desde la UI) y `bootstrap_enabled = true`. Composición `django` de la receta
  (`examples/django-recipe.example.toml`) con Python `/opt/homebrew/bin/python3.13` 3.13.13 y uv `/opt/homebrew/bin/uv`
  0.12.19, `wheelhouse = …/wheels`, `timeout_seconds = 600`, `max_output_bytes = 65536`.
- Cuatro presets v5: `codex-reviewer`, `codex-executor`, `claude-reviewer` y `claude-executor`, con los catálogos de §2.

## 4. Secuencia y consumo máximo

Las selecciones de roles se cambian en Ajustes del mismo proyecto, tras COMMITTED y sin trabajo pendiente.

| Paso | Operación | Invocaciones de proveedor (máx.) |
|---|---|---|
| T013 | `--version` y `--help` (y subcomandos de ayuda) de los dos binarios fijados; lectura de cadenas del binario de Codex. Producto, tests y wheel nuevos. | 0 |
| Preparación | Crear el área; construir y verificar el wheel desde el HEAD con T013; venv offline; descargar y verificar 17 wheels; TOML; `check-config --preflight` (version/help); `init-db`; `serve`. | 0 |
| T007 | Elegir raíz, crear hijo, definición D088 con revisor Codex y commit raíz; receta offline y commit técnico; runserver de comprobación. | 20 turnos del revisor |
| T008 | P001-T001 Codex→Codex | 7 (1 plan + 3 ejecuciones + 3 revisiones) |
| T009 | P001-T002 Codex→Claude | 7 |
| T010 | P001-T003 Claude→Claude | 7 |
| T011 | P001-T004 Claude→Codex | 7 |
| T012 | Check READY y cierre/archivo de P001 del hijo con revisor Claude; QA en navegador del Django | 2 |

Techo total: **60 invocaciones de proveedor** (50 previstas como máximo). Red: solo PyPI para los 17 wheels y
el tráfico propio de cada CLI con su proveedor. El wheel del harness se construye offline con las caches existentes.
La planificación posterior de una nueva fase del hijo (D091) no entra en este consentimiento.

## 5. Criterios de parada y limpieza

- Para en el primer fallo: proveedor, timeout, validación tras agotar correcciones, rechazo del revisor, entorno,
  permisos, cuarentena o deriva de composición. Sin retry, fallback, cambio de modelo/proveedor ni relanzamiento.
  Corregir un fallo no autoriza a repetir el consumo: se informa y se pide una nueva autorización.
- También para si cambian los hashes de §1, si `check-config --preflight` no pasa, si el destino o el área existen
  antes de crearlos, si se alcanza un techo de §4 o si aparece una escritura fuera del hijo, del área o de `/private/tmp`.
- No se edita el Django a mano para completar lo que debe hacer el flujo, ni se toca el TOML/SQLite para desbloquear.
- Al terminar cada sesión: servicio y runserver detenidos, sin procesos o grupos vivos ni locks; el área y el hijo
  se conservan. Historiales/streams quedan privados en `state/`; `docs/phase` recibe solo resúmenes saneados,
  hashes y referencias, nunca credenciales, prompts completos ni fixtures derivados de runs.
- Push, publicación y modificaciones de ReferenceProject u otros proyectos quedan fuera.

## 6. Alcance del consentimiento

El consentimiento de D121 cubre exactamente §§1–5: la caracterización de T013 sin llamadas a modelos, la preparación
del área, la descarga de los 17 wheels y T007–T012 dentro de los techos de §4. Cualquier cambio de selección,
límite, versión o ruta exige actualizar esta propuesta antes. Si T013 descubre que caracterizar la escritura de
Codex 0.163.0 requiere invocar un modelo, se detiene y se pide una autorización aparte.

## 7. Comprobación de esta tarea

- Lecturas sin procesos de proveedor: `package.json` de Codex, binarios versionados de Claude, enlaces de `uv` y
  `python3.13`, SHA-256 de §1, ausencia del destino y del área, y puertos 8031/8032 sin escucha (`lsof`).
- 12 checks unittest correctos; 317 enlaces/anclas relativos de los documentos tocados válidos; `git diff --check` correcto.
- Sin pytest, Node/build ni Alembic: solo cambia documentación, sin código, esquema, API, tipos ni versiones.
