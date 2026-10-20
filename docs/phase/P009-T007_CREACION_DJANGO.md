# P009-T007 — Creación del Django desde la UI (detenida en el primer turno)

Fecha: 2026-10-20. Decisión [D123](../DECISIONS.md#d123--p009-t007-detenida-codex-rechaza-la-definición-en-un-hijo-sin-git).
Base: `21871a0` (T013). Autorización: [propuesta de T006](P009-T006_PROPUESTA_PILOTO.md), §§3–6 (D121).

**Resultado:** preparación del área, servicio y creación/registro del hijo correctos. El primer turno de la
definición con el revisor Codex falla antes de llegar al modelo y el piloto se detiene (§5 de la propuesta).
Sin definición, commit raíz, receta ni Django. No se reintentó ni se cambió de proveedor.

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
