# P009-T008 — Piloto Codex→Codex (detenida en la revisión)

Fecha: 2026-10-21. Decisión [D128](../DECISIONS.md#d128--p009-t008-detenida-una-ruta-de-directorio-no-cubre-sus-archivos).
Base: `2ae39f9` (sin cambios de `src/` ni `frontend/` desde el wheel de `1f8aa7a`). Autorización: petición del usuario
en el chat de continuar con la siguiente tarea, dentro de D121 y de la [propuesta](P009-T006_PROPUESTA_PILOTO.md) §§3–6.

**Resultado:** P001-T001 del hijo se planifica, se ejecuta y pasa las seis validaciones del perfil. El revisor Codex
la bloquea porque la política de rutas marca como infracción los seis archivos que el ejecutor escribió en `core/`,
aunque `core/` figura en la allowlist. Es un defecto del producto: una entrada de directorio con barra final no
cubre ningún archivo. El piloto se detiene (§5 de la propuesta), sin reintento ni revalidación. Sin commit.

## 1. Precondiciones y arranque (sin proveedores)

| Comprobación | Resultado |
|---|---|
| SHA-256 de los binarios de §1 de la propuesta | idénticos |
| 8031/8032, servicio y CLI del área | libres, sin procesos |
| Hijo `harness-django-pilot` | limpio en `d762e77`, P001 activa con sus cuatro tareas |
| Wheel instalado | `7218250e…5b229fd` (`1f8aa7a`, `cli-13`); el checkout no cambia `src/` ni `frontend/` desde entonces |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets |
| `serve` en 8031 con `TMPDIR=…/harness-local/tmp` | lanzado por el usuario en su terminal; clave de sesión dentro del área |

El clasificador del modo automático de la sesión rechazó lanzar `serve` desde el agente, y el usuario lo arrancó
en su terminal. `serve` exige rutas absolutas en `--database`. La guardia de origen rechazó la navegación directa
de la extensión (`origin_rejected`, como en T007 §2) y la recarga desde el propio origen pasó. El usuario inició
la sesión con la clave local: el agente no la leyó ni la escribió.

## 2. Recibo de preparación invalidado por el QA de T007

La UI no dejaba encolar: `preparation_required: identidad, archivos protegidos o entorno preparados cambiaron`.
El recibo de la receta acredita cada byte de `.venv`, también el bytecode (`environment_snapshot`, D119). El
`runserver` de comprobación de T007 (§7.3), lanzado sin `PYTHONDONTWRITEBYTECODE`, escribió 366 `.pyc` en
`.venv` entre 20 y 21 s después del commit técnico. Todos nacieron después del commit; antes no había ninguno.

Por decisión del usuario se borraron exactamente esos `.pyc` y los `__pycache__` vacíos. Con eso el entorno vuelve
a los bytes acreditados (los directorios no entran en el hash) y la UI muestra «Django preparado». No se tocaron
código Django, TOML ni SQLite. El QA de T012 debe lanzar `runserver` sin escribir bytecode (propuesta §9).

## 3. Run `fc340afb`

Ajustes antes de encolar: revisor Codex `gpt-6-luna`/`medium`, ejecutor Codex solo catálogo `gpt-6-luna` ×
{low, medium, high}, planificación por el revisor, 2 ciclos; coincide con D121. Contrato enviado desde «Encolar
tarea en esta fase»: la sección P001-T001 literal del `docs/NEXT_STEPS.md` del hijo (977 bytes), sin añadidos.

| Intento | Selección congelada | Resultado | Tokens (der.) | Turnos | Duración |
|---|---|---|---|---|---|
| 1 planificador | `gpt-6-luna`/`medium` (política) | COMPLETE | 46 148 | 4 | 12,4 s |
| 2 ejecutor | `gpt-6-luna`/`medium`, elegida por el revisor | COMPLETE | 527 527 | 35 | 1 min 1 s |
| 3 revisor | `gpt-6-luna`/`medium` (política) | COMPLETE, **BLOCKED** | 68 301 | 4 | 12,5 s |

- **Selección del ejecutor:** el revisor eligió `gpt-6-luna`/`medium` con un motivo propio de la tarea (coordinar
  modelo, migración, formulario, vistas, plantillas, pruebas y documentación en una allowlist estrecha). El intento
  2 usa exactamente esa selección: se cumple el criterio de procedencia de T008.
- **Contrato:** `allowed_paths = ["core/", "docs/DDBB-DIAGRAM.md", "docs/flows/tasks.md"]`, copiado de la nota
  del NEXT_STEPS del hijo. Prohibiciones del harness añadidas (archivo, documentos de seguimiento e instrucciones).
- **Cambio del ejecutor:** 8 rutas, diff de 7 907 bytes (`d26263b0…5fd777f9e9`): modelo `Task` con título obligatorio,
  descripción opcional, `completed` falso y `created_at`; migración `0001_initial`, `TaskForm`, vista con POST y
  redirección, plantilla con CSRF, tres tests, diagrama Mermaid y flujo. Revisión de contenido fuera de alcance: el
  revisor no llegó a valorarlo.
- **Validaciones:** pytest (3 casos JUnit, todos OK), ruff check, ruff format, mypy, `manage.py check` y
  `makemigrations --check`, todas con salida 0.
- **Revisión:** veredicto BLOCKED con un hallazgo bloqueante de categoría `policy`. La evidencia marca como
  infracciones `core/forms.py`, `core/migrations/0001_initial.py`, `core/models.py`, `core/templates/core/tasks.html`,
  `core/tests.py` y `core/views.py`. Pregunta bloqueante: si el harness puede resolver la discrepancia con la allowlist.

## 4. Causa

`check_paths` (`core/engine/evidence.py`) compara cada ruta cambiada con `fnmatchcase(path, pattern)`, y
`fnmatchcase("core/models.py", "core/")` es falso, mientras que `core/**` sí coincide. `task_contract`
(`core/engine/contracts.py`) acepta `core/` como ruta relativa válida, así que el contrato se congela con una entrada
que no cubre ningún archivo y el fallo solo aparece después de gastar ejecución y revisión. Las dos rutas exactas
de `docs/` no se marcan. La notación `core/` viene del NEXT_STEPS que redactó el revisor en la definición (T007).
El ensayo T005 no lo detectó porque su planificador falso devolvía `templates/**`. La plantilla `plan-task` solo
ilustra rutas exactas y no dice cómo expresar un directorio.

## 5. Consumo, parada y estado que queda

- **Consumo de T008:** 3 invocaciones de proveedor de 7, todas con modelo. Del piloto, 6 de 60.
- **Parada:** rechazo del revisor (§5 de la propuesta). No se pulsó «Revalidar y revisar», «Reintentar ejecutor» ni
  «Confirmar commit»; no se registraron concesiones de ficheros.
- **Hijo:** HEAD sigue en `d762e77`; los cambios del ejecutor siguen sin confirmar en el checkout, ligados al run
  BLOCKED. Por decisión del usuario se conservan. `.venv` sigue sin bytecode.
- **Al terminar:** sesión de la UI cerrada, servicio detenido con SIGTERM, `tmp/` vacío, 8031/8032 libres y sin
  procesos de CLI. Prompts, streams y SQLite siguen privados en `state/`.
- **No probado aquí:** aceptación y commit de una tarea con ejecutor real, T009–T012 y QA funcional del Django.

## 6. Siguiente paso

[P009-T017](../NEXT_STEPS.md#p009-t017--rutas-de-directorio-en-el-contrato-de-tarea) corrige la semántica de las rutas
de directorio con regresiones. Reanudar T008 exige wheel reconstruido y verificado, decidir qué hacer con el run
`fc340afb` y los cambios conservados, y **una autorización nueva del usuario** con el consumo restante de T008 (4 de 7).
