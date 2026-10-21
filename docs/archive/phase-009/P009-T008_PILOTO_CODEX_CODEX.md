# P009-T008 — Piloto Codex→Codex

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

## 7. Reanudación (2026-10-21, sesión 2): parada antes de encolar

Autorización nueva del usuario en el chat: reanudar T008 con un run nuevo y techo ampliado a 10 (propuesta §10, D129).

| Comprobación o paso | Resultado |
|---|---|
| SHA-256 de los binarios de §1 de la propuesta | idénticos |
| 8031/8032, servicio y CLI del área | libres, sin procesos |
| Hijo | ocho rutas de `fc340afb` retiradas (`git restore` de cinco y borrado de tres nuevas); limpio en `d762e77`; `.venv` sin bytecode. Copia privada en `state/fc340afb-discarded/` del área |
| Wheel de `0852f39` (T017) | `0301493b…cc7de`, verificado completo con `check_distribution.py` e instalado offline en el venv del área |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets |
| `serve` en 8031 | lanzado por el usuario en su terminal |

La UI volvió a mostrar `preparation_required: identidad, archivos protegidos o entorno preparados cambiaron`.
Diagnóstico de solo lectura con el recibo de la SQLite: los archivos protegidos y todos los archivos de `.venv`
coinciden. Lo único distinto es `st_dev` del checkout y de `.venv` (16777230 → 16777233), con el mismo inodo. El
Mac se había reiniciado 22 minutos antes y macOS renumeró el volumen. Se para por entorno (§5 de la propuesta), sin
tocar la SQLite y **sin consumir invocaciones**: siguen 3 de 10 en T008 y 6 de 60 en el piloto. La corrección es
[P009-T018](P009-T018_RECIBO_TRAS_REINICIO.md).

## 8. Reanudación (2026-10-21, sesión 3): COMMITTED

Misma autorización que la sesión 2, con techo de 10. Wheel de `d557082` (T017 y T018): `1163e0b9…5d9a86`, verificado
completo con `check_distribution.py` e instalado offline con `serve` detenido. Preflight correcto en los 6
roles/presets. El recibo real del piloto vuelve a valer sin tocar la SQLite, y la UI muestra «Django preparado».
Ajustes sin cambios: coinciden con D121. El usuario lanzó `serve` e inició la sesión. Contrato enviado desde
«Encolar tarea en esta fase»: la sección P001-T001 literal del hijo, sin los saltos de línea finales (976 bytes).

| Intento | Selección congelada | Resultado | Duración | Actividad del stream |
|---|---|---|---|---|
| 1 planificador | `gpt-6-luna`/`medium` (política) | COMPLETE | 13,4 s | 2 comandos |
| 2 ejecutor | `gpt-6-luna`/`medium`, elegida por el revisor | COMPLETE | 2 min 19 s | 19 comandos, 13 cambios de archivo |
| 3 revisor | `gpt-6-luna`/`medium` (política) | COMPLETE, **ACCEPT** | 10,9 s | 2 comandos |

- **Contrato (run `7fbaf89c`):** `allowed_paths = ["core/**", "docs/DDBB-DIAGRAM.md", "docs/flows/tasks.md"]`. La
  entrada `core/` del NEXT_STEPS del hijo se congeló como `core/**` (D129). El revisor eligió el ejecutor con un
  motivo propio de la tarea, y el intento 2 usa exactamente esa selección.
- **Cambio:** 8 rutas, diff de 8 478 bytes, huella `5bd87295…cbf1e527`. Modelo `Task` (título obligatorio,
  descripción opcional, `completed` falso, `created_at`), migración `0001_initial`, `TaskForm`, vista con alta por POST
  y listado, plantilla con CSRF, tres tests, `erDiagram` y flujo de alta/listado. Sin infracciones de rutas.
- **Validaciones:** las seis con salida 0. pytest pasa 3 casos JUnit: alta persistida, título vacío rechazado y listado.
- **Revisión y aceptación:** ACCEPT sin hallazgos, preguntas, concesiones ni propuestas. La aceptación es elegible y
  tiene paridad de modelos con el diagrama.
- **Commit:** confirmado desde la UI con autorización explícita del usuario. Commit `98f4611` «harness: accept
  P001-T001 - Crear y listar», con la identidad Git del usuario, árbol revisado `527061ee` y STATE/NEXT_STEPS del hijo
  regenerados. Run COMMITTED y checkout limpio.
- **Observaciones de contenido, fuera de los criterios:** tras un alta válida la vista vuelve a renderizar en lugar de
  redirigir, así que recargar la página repite el POST. `docs/flows/tasks.md` describía el plan completo de P001 y
  ahora solo describe el alta y el listado: las tareas siguientes deben volver a añadir sus flujos.
- **Consumo:** 3 invocaciones en esta sesión. T008: 6 de 10. Piloto: 9 de 60.
- **Al terminar:** sesión de la UI cerrada, sin CLI vivas, `.venv` sin bytecode. El usuario detiene `serve`.
- **No probado aquí:** QA en navegador del Django (T012) y las combinaciones con Claude (T009–T011).

