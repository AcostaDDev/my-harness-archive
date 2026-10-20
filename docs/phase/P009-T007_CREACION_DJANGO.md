# P009-T007 — Creación del Django desde la UI (detenida en el primer turno)

Fecha: 2026-10-20. Decisión [D123](../DECISIONS.md#d123--p009-t007-detenida-codex-rechaza-la-definición-en-un-hijo-sin-git).
Base: `21871a0` (T013). Autorización: [propuesta de T006](P009-T006_PROPUESTA_PILOTO.md), §§3–6 (D121).

**Resultado:** preparación del área, servicio y creación/registro del hijo correctos. El primer turno de la
definición con el revisor Codex falla antes de llegar al modelo y el piloto se detiene (§5 de la propuesta).
Sin definición, commit raíz, receta ni Django. No se reintentó ni se cambió de proveedor.

**Reanudación (2026-10-21, D127):** con autorización nueva del usuario y wheel de `1f8aa7a` (`cli-13`, T014/T015),
T007 se completa: definición en dos turnos más, commit raíz, receta offline con commit técnico y portada en
loopback. Tres invocaciones de 20 en total. Ver [§7](#7-reanudación-y-cierre-de-t007-2026-10-21).

## 1. Precondiciones comprobadas antes de crear nada

- SHA-256 de los binarios fijados idénticos a §1: Codex `8813367285524ac7…cfdee31`, Claude `b9ac5374839f14ab…aab78e6a`.
- `$HOME/.local/share/harness-local/` y `$HOME/Documents/projects/harness-django-pilot` inexistentes;
  8031/8032 sin escucha. Python 3.13.13 y uv 0.12.19 en las rutas de §3. Checkout limpio en `21871a0`.

## 2. Preparación del área (sin proveedores)

| Paso | Resultado |
|---|---|
| Área `0700` con `config/`, `state/`, `dist/`, `wheels/`, `venv/`, `tmp/` | creada |
| `scripts/build_distribution.py --out-dir …/dist` desde `21871a0` | sdist, wheel y `requirements.txt` construidos offline |
| `scripts/check_distribution.py --dist …/dist` | **parcial**: ver §5 |
| venv con CPython 3.14.4; `uv pip sync --offline --require-hashes`; wheel `--no-deps` | `harness_local` importado desde el venv del área |
| 17 wheels de PyPI, verificados contra `django-requirements.lock` y el [recibo de T005](P009-T005_WHEELS.json) | 34.425.869 bytes, todos los SHA-256 y tamaños coinciden |
| TOML `local-config-5`, chmod 600, sin secretos | `check-config` correcto |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets (Codex 0.163.0, Claude 2.1.304) |
| `init-db` | SQLite operativa en `state/harness.sqlite3` |

Detalles reversibles fijados con criterio, distintos de §3 de la propuesta:

- No hay `home-commands/`: la composición de la receta exige `environment = {}` y HOME/cache/tmp dentro del
  hijo (D119), así que esa carpeta no tendría uso.
- `serve` arrancó primero con el `TMPDIR` del sistema y escribió su clave de sesión en `/var/folders/…`, fuera
  del área. Se detuvo antes de cualquier operación (la clave se borra al salir) y se relanzó con
  `TMPDIR=…/harness-local/tmp`. Esto no está documentado en ARCHITECTURE §9.
- El navegador de la sesión llegó primero con `Sec-Fetch-Site: cross-site`, y la guardia lo rechazó con
  `origin_rejected`. Una recarga desde el propio origen pasó la guardia sin cambiar nada.

## 3. Operaciones en la UI

1. «Carpeta de proyectos»: `$HOME/Documents/projects` revisada y guardada con autorización explícita (revisión 1).
2. «Crear carpeta nueva»: id y carpeta `harness-django-pilot`, composición `django`, agentes por proyecto
   `codex-reviewer` `gpt-6-luna`/`medium` y `codex-executor`, planificación del revisor, solo catálogo
   `gpt-6-luna` × {low, medium, high}, 2 ciclos y tag ligero. La preview coincidió con D121; creación y registro confirmados.
   Resultado: carpeta vacía creada y proyecto registrado.
3. Brief de 2.099 bytes, redactado solo con lo que ya fijan el [plan](P009_PLAN_DJANGO.md#resultado-que-se-busca) y NEXT_STEPS
   T008–T011: alcance, exclusiones, base de la receta y las cuatro tareas de P001 en orden.
4. Primer mensaje al revisor: borradores completos de la plantilla y P001 con cuatro tareas.

## 4. Fallo y parada

| Campo | Valor |
|---|---|
| Intento | `definition`, Codex 0.163.0, `cli-12`, `gpt-6-luna`/`medium`, cwd el hijo |
| Duración | 302 ms; exit 1; 0 tokens, 0 turnos, sin eventos JSONL |
| stderr (76 bytes, SHA-256 `dd701e71…c401324d`) | `Not inside a trusted directory and --skip-git-repo-check was not specified.` |
| Estado | turno «Fallido, sin reintento»; job DONE; proceso STOPPED |

**Causa:** el adaptador solo añade `--skip-git-repo-check` en `chat`/`definition` cuando la raíz es una
exportación (D083/D102, `cli-12`). Una definición D088 en un hijo nuevo trabaja sobre la carpeta viva, que
todavía no es un repositorio Git porque el commit raíz llega al aceptar. Codex 0.163.0 rehúsa arrancar en ella.
La CLI falsa del ensayo T005 no reproduce esa comprobación de Codex, y ningún uso real anterior había definido
un proyecto D088 con revisor Codex.

Consumo: **1 invocación de proveedor lanzada** (de 20 para T007 y 60 en total), sin consumo del modelo.
Al parar: servicio detenido, 8031/8032 libres, sin procesos de CLI vivos, `tmp/` vacío, hijo vacío y
registrado. El área y el hijo se conservan (§5). Prompt, streams y SQLite permanecen privados en `state/`.

## 5. Verificación del wheel incompleta

`check_distribution.py` comprueba que el wheel es byte a byte igual que `src/` y `frontend/dist`, `init-db`,
`serve`, UI/assets, sesión, simulación y reinicio. Después falla con 405 en `POST /projects/offline/bootstrap/preview`:
ese tramo usa la creación v1, retirada en P008-T002/T006 (D089, D093), y el script no se actualizó.
Por decisión del usuario se continuó con la verificación parcial más `check-config --preflight` e `init-db` del
wheel instalado. La corrección queda como tarea obligatoria antes de cerrar la fase (P009-T015).

## 6. Siguiente paso

[P009-T014](../NEXT_STEPS.md#p009-t014--definición-con-revisor-codex-en-un-hijo-sin-git) corrige el transporte
con pruebas que reproduzcan la comprobación de Codex. Reanudar T007 exige otra cosa: un wheel reconstruido,
la propuesta actualizada si cambia el adaptador (§6) y **una autorización nueva del usuario** (§5). La reanudación
prevista no recrea la carpeta: sigue con el hijo ya registrado y su conversación. T014 debe comprobar si esa
conversación admite un turno nuevo con el adaptador corregido o necesita otra; aquí no se ha verificado.

## 7. Reanudación y cierre de T007 (2026-10-21)

Autorización nueva del usuario en el chat («Reanuda P009-T007»), dentro de D121 §§3–6 y de la propuesta §8.
Decisión [D127](../DECISIONS.md#d127--p009-t007-completada-django-creado-desde-la-ui-con-revisor-codex).

### 7.1 Precondiciones y preparación (sin proveedores)

| Comprobación | Resultado |
|---|---|
| SHA-256 de los binarios de §1 de la propuesta | idénticos |
| 8031/8032, servicio y CLI del área | libres, sin procesos; hijo vacío y registrado |
| Checkout de desarrollo | limpio en `1f8aa7a` (T014 + T015) |
| `build_distribution.py --out-dir …/dist` | wheel `7218250e…5b229fd` (sustituye `ae1f5640…a6f33f` de `21871a0`) |
| `check_distribution.py --dist …/dist` | **completo** por primera vez sobre el wheel operativo (T015) |
| `uv pip sync --offline --require-hashes` + wheel `--no-deps --reinstall` en el venv del área | `cli-13` instalado |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets |
| Esquema SQLite | sin migraciones nuevas desde `21871a0`; no hizo falta `init-db` |
| `serve` en 8031 con `TMPDIR=…/harness-local/tmp` | clave de sesión dentro del área |

La navegación directa de la extensión del navegador vuelve a llegar como `Sec-Fetch-Site: cross-site` y se rechaza
con `origin_rejected`; una recarga desde el propio origen pasa la guardia. Es el mismo comportamiento de §2.

### 7.2 Definición con revisor Codex

| Turno | Run | Resultado | Tokens (entrada / caché / salida / razonamiento) | Duración |
|---|---|---|---|---|
| 1 (2026-10-20, `cli-12`) | `8eb93241` | `FAILED` sin llegar al modelo (§4) | — | 302 ms |
| 2 (`cli-13`) | `fcd25961` | `ANSWERED` sin borradores y con una pregunta bloqueante | 14 070 / 9 088 / 655 / 449 | 10,2 s |
| 3 (`cli-13`) | `93d22685` | `ANSWERED`: 8 borradores, sin preguntas | 14 542 / 0 / 3 483 / 188 | 28,7 s |

Los tres usan `gpt-6-luna`/`medium`, como fija D121. El turno 2 llega al modelo con el flag de D124: la carpeta sin
Git ya no lo bloquea. El revisor no redacta y pregunta, como bloqueante, por «el contenido actual y los marcadores
gestionados» de STATE, NEXT_STEPS, ROADMAP y DECISIONS. Es una ambigüedad de la plantilla `define-project` ante
una carpeta nueva: pide conservar los marcadores «exactly where the drafts have them», pero no dice que en un borrador
nuevo son opcionales (la aceptación añade los bloques con `replace_block`). El usuario eligió responder en la
conversación en lugar de parar. El turno 3 responde solo con esos hechos del producto y repite el encargo.

Borradores del turno 3: README, SPECIFICATION, ARCHITECTURE, DECISIONS (sin ADR propias), ROADMAP (P001 y sus
criterios), STATE, NEXT_STEPS (P001-T001…T004 en el orden del brief, con los seis comandos del perfil) y
`docs/flows/tasks.md`. Se ciñen al brief y no añaden funciones; el flujo y el README describen lo planificado como
tal. Cada borrador se aplicó desde la UI con su hash revisado; en disco coinciden con `content_sha256`.

El ROADMAP no declaraba `**Tag:**`, así que la vista previa indicaba «sin tag» aunque el proyecto usa tag ligero
(el nombre sale de ROADMAP, `tag_intent`). Por decisión del usuario se añadió `**Tag:**` con el nombre `p001` como edición
propia desde el editor de la UI, sin otra invocación. Vista previa final `8aede869d2fd`: lista, 14 archivos, AGENTS
con los comandos del perfil y DDBB-DIAGRAM «Sin persistencia».

### 7.3 Commit raíz, receta y comprobación

| Paso | Resultado |
|---|---|
| Crear el proyecto (vista previa `8aede869d2fd`) | commit raíz `9b612ca`, 14 archivos, operación `COMPLETED`, P001 activa |
| Plan de preparación offline `5250fc08a214` | 18 archivos; `uv pip install --offline --no-index --find-links …/wheels --require-hashes --no-deps` |
| Preparación `934cbf76` | `COMPLETED` en 1 min 29 s; los seis checks del perfil, `migrate` local |
| Commit técnico | `d762e77` «harness: prepare Django (django-recipe-1)», identidad Git del usuario |
| Ignorados | `.venv/`, `db.sqlite3`, `.django-secret`, `.harness-preparation/`, cachés y `reports/` |
| `runserver 127.0.0.1:8032 --noreload` | `/` y `/static/core.css` responden 200; detenido después |

Ninguna edición manual del scaffold: el único cambio fuera de los borradores del revisor es la línea del tag.
P001 tiene las cuatro tareas planificadas y la primera se encola en T008.

### 7.4 Consumo, parada y límites

- **Consumo de T007:** 3 invocaciones de proveedor de 20 (1 sin modelo en la primera sesión). Del piloto, 3 de 60.
- **Al terminar:** sesión de la UI cerrada, servicio detenido con SIGTERM y apagado limpio, `tmp/` vacío, 8031/8032
  libres, sin procesos de CLI, árbol del hijo limpio. Área e hijo se conservan. Streams y SQLite siguen privados en `state/`.
- Las lecturas de comprobación por API iniciaban una sesión por consulta y acabaron recibiendo 429 del limitador
  de sesiones. El servicio se comportó como debía; el resto se leyó desde la sesión del navegador.
- **No probado aquí:** tareas con ejecutor (T008–T011) ni QA funcional del Django más allá de la portada.
