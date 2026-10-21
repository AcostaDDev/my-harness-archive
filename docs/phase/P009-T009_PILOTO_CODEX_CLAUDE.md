# P009-T009 — Piloto Codex→Claude

Fecha: 2026-10-21. Decisión [D132](../DECISIONS.md#d132--p009-t009-detenida-el-ejecutor-claude-no-puede-cumplir-ruff-format).
Base: `6f332a7` (sin cambios de `src/` ni `frontend/` desde el wheel de `d557082`). Autorización: el usuario pidió en el
chat continuar con la siguiente tarea, dentro de D121 y de la [propuesta](P009-T006_PROPUESTA_PILOTO.md) §§3–6. Encolar y
reintentar los pulsó el usuario en la UI.

**Resultado:** P001-T002 del hijo se planifica y la ejecuta Claude con la selección que eligió el revisor Codex.
Pasan cinco de las seis validaciones. Falla `ruff format --check .` por una sola línea de `core/tests.py`. Dos ciclos de
corrección no la arreglan: el ejecutor Claude no tiene shell para ejecutar Ruff y, a mano, formatea con el ancho por
defecto de 88 columnas, pero el hijo usa 100. El run `bb29b133` acaba en el límite de revisiones, sin commit.
Antes, `serve` murió por SIGBUS en mitad del primer ciclo de corrección (§3).

## 1. Precondiciones y ajustes (sin proveedores)

| Comprobación o paso | Resultado |
|---|---|
| SHA-256 de los binarios de §1 de la propuesta | idénticos, antes de encolar y tras la caída |
| Wheel instalado | `1163e0b9…5d9a86` (`d557082`); desde entonces el checkout solo cambia documentos |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets |
| Hijo | limpio en `98f4611`, «Django preparado», `.venv` sin bytecode |
| `serve` en 8031 | seguía en marcha desde la sesión 3 de T008, con la sesión de la UI abierta |

La guardia de origen volvió a rechazar la navegación directa de la extensión (`origin_rejected`). La pasó una recarga
lanzada desde el propio origen.

**Ajustes (registro v1 → v2):** solo cambia el preset del ejecutor, de `codex-executor` a `claude-executor`, con el
catálogo de D121: `claude-sonnet-5-5`, `claude-opus-5-5` × {low, medium, high}, en modo catálogo. Revisor Codex
`gpt-6-luna`/`medium`, planificación por el revisor y 2 ciclos, sin cambios. Al cambiar de proveedor, la UI vacía el
catálogo y hay que volver a escribirlo. Queda auditado con motivo. Las versiones congeladas pasan a
`executor_provider = claude` y `executor_cli = 2.1.304`.

**Contrato:** la sección P001-T002 literal del `docs/NEXT_STEPS.md` del hijo, sin los saltos de línea finales (875
bytes, SHA-256 `acd0105b…bf6790de`). El clasificador del modo automático rechazó que el agente pulsara «Encolar tarea»,
y lo pulsó el usuario.

## 2. Run `bb29b133`

`allowed_paths = ["core/**", "docs/flows/tasks.md"]`: la entrada `core/` se congela como `core/**` (D129). Las
prohibiciones del harness son las mismas que en T008.

| Intento | Selección congelada | Resultado | Duración | Actividad |
|---|---|---|---|---|
| 1 planificador | Codex `gpt-6-luna`/`medium` (política) | COMPLETE | 13,4 s | 1 comando |
| 2 ejecutor | Claude `claude-sonnet-5-5`/`medium`, elegida por el revisor | COMPLETE | 31,7 s | 17 turnos: 7 Read, 4 Edit, 4 Write, 1 Glob |
| 3 revisor | Codex `gpt-6-luna`/`medium` | COMPLETE, **REVISE** | 22,0 s | 3 comandos |
| 4 ejecutor | Claude `claude-sonnet-5-5`/`low`, elegida por el revisor | **INTERRUMPIDO** (§3) | — | 1 Read, sin escrituras |
| 5 ejecutor (reintento) | Claude `claude-sonnet-5-5`/`low` | COMPLETE, sin cambios | 11,3 s | 2 turnos: 1 Read |
| 6 revisor | Codex `gpt-6-luna`/`medium` | COMPLETE, **REVISE** → límite | — | 3 comandos |

- **Selección del ejecutor:** el planificador eligió `claude-sonnet-5-5`/`medium` con un motivo propio de la tarea
  (un CRUD acotado con validaciones ya establecidas). El intento 2 usa exactamente esa selección, y el modelo observado
  en el stream es `claude-sonnet-5-5`. Para la corrección, el revisor eligió `low` con motivo. Se cumple la procedencia de
  T009: revisor Codex elegido por el usuario y ejecutor Claude elegido por el revisor.
- **Cambio del ejecutor:** 7 rutas, 9 KiB, huella `996c5442…e1423991`. Vistas `edit` y `delete` con
  `get_object_or_404` y `require_http_methods(["GET", "POST"])`, y URLs `tasks/<pk>/edit/` y `tasks/<pk>/delete/`.
  Plantillas de edición y de confirmación con CSRF, enlaces en la lista y flujo de edición y borrado en `tasks.md`.
  8 tests nuevos (11 en total): edición que conserva datos, título vacío, 404, GET sin borrar, POST que borra, 405 y CSRF.
- **Validaciones (intentos 2 y 5, misma huella):** pytest pasa los 11 casos JUnit. `ruff check`, mypy,
  `manage.py check` y `makemigrations --check` salen con 0. `ruff format --check .` sale con 1.
- **Revisiones:** los dos REVISE tienen un único hallazgo `validation` de severidad media: `core/tests.py` «would be
  reformatted». El revisor no pone objeciones al contenido.

## 3. Caída de `serve` (SIGBUS)

A las 10:33:16, con el intento 4 recién lanzado, el proceso `serve` murió por `SIGBUS` (`EXC_BAD_ACCESS`,
`FS pagein error: 22`). El fallo se produjo en el hilo `managed-chat`, dentro de `walIndexReadHdr` de SQLite 3.53: el
índice WAL (`harness.sqlite3-shm`), mapeado en memoria, era más corto que lo mapeado.

- **Causa probable, no demostrada:** mientras corría el run, el agente leía la SQLite viva cada 3–5 s con el
  `sqlite3 -readonly` del sistema (SQLite 3.51 de Apple), con hasta tres lectores a la vez. Uno de ellos devolvió
  `database is locked` al preparar la consulta. En SQLite, solo una conexión que se cree la primera trunca el `-shm`.
  Se pararon todos los lectores y no se volvió a abrir la SQLite viva. El resto del seguimiento se hizo por la UI y
  leyendo artefactos.
- **Daño:** ninguno. `integrity_check` correcto sobre una copia, hecha con el servicio parado y borrada después. El
  intento 4 solo había leído `core/tests.py`. El grupo de procesos del ejecutor ya no existía.
- **Recuperación con el producto:** el usuario relanzó `serve`. `recover_expired` pasó el job a RECOVERY_REQUIRED sin
  reencolar nada. Con evidencia de que el grupo estaba muerto, el agente confirmó el escritor detenido desde la UI,
  y el run quedó INTERRUPTED con el intento 4 interrumpido. Por decisión del usuario, que pulsó «Reintentar ejecutor»,
  se reanudó el mismo run.

## 4. Causa de la parada

`pyproject.toml` del hijo fija `line-length = 100`. El intento 2 partió una aserción de `test_nonexistent_task_returns_404`
en tres líneas, como haría Ruff con 88 columnas, y `ruff format` la quiere en una. El ejecutor Claude trabaja con
`Read`, `Edit`, `Write`, `Glob` y `Grep`, sin Bash (D121), así que no puede ejecutar Ruff ni ninguna validación. Lo dice
en su resultado. En el intento 5 revisó el archivo a mano con la regla de 88 columnas, no vio nada y no tocó nada.
`ruff format --check` solo informa del archivo, y el hallazgo del revisor no aporta qué línea ni qué cambio. Ni el
revisor ni el ejecutor recibieron información suficiente para corregirlo.

Con el ejecutor Codex (T008) no ocurrió porque trabaja en `workspace-write` con comandos. El ensayo T005 usaba CLI falsas
que no formatean.

## 5. Consumo, parada y estado que queda

- **Consumo de T009:** 6 invocaciones de proveedor de 7: intentos 1–6, incluido el 4 interrumpido. Del piloto, 15 de 60.
- **Parada:** validación sin pasar tras agotar las correcciones (propuesta §5). No se pulsó «Revalidar y revisar» ni
  «Confirmar commit», no se registraron concesiones y no se editó el hijo a mano.
- **Hijo:** HEAD sigue en `98f4611`. Los cambios del ejecutor siguen sin confirmar en el checkout, ligados al run
  `bb29b133` en `revision_limit`. `.venv` sigue sin bytecode.
- **Al terminar:** sin CLI vivas, pestaña cerrada y copia de la SQLite borrada. El usuario detiene `serve`. Prompts,
  streams y SQLite siguen privados en `state/`.
- **No probado aquí:** aceptación y commit con ejecutor Claude, T010–T012 y QA funcional del Django.

## 6. Siguiente paso

[P009-T019](../NEXT_STEPS.md#p009-t019--el-ejecutor-sin-shell-puede-cumplir-el-formato-del-perfil) debe permitir que
un ejecutor sin shell cumpla las validaciones de formato del perfil, y decidir qué se hace con `bb29b133` y sus cambios.
Reanudar T009 exige un wheel reconstruido y verificado si cambia el producto, y **una autorización nueva del usuario**
con techo: queda 1 de 7.

## 7. Reanudación (2026-10-21, sesión 2): COMMITTED

Autorización nueva del usuario en el chat: reanudar T009 con un run nuevo y techo ampliado de 7 a 13 (propuesta §12).
`bb29b133` queda en `revision_limit` como evidencia (D133).

| Comprobación o paso | Resultado |
|---|---|
| SHA-256 de los binarios de §1 de la propuesta | idénticos |
| Wheel de `494b929` (T019) | `29a50da8…f119da`, verificado entero con `check_distribution.py` e instalado offline con `serve` detenido |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets; huella de la receta `f511c00a…` sin cambios |
| Hijo | 7 rutas de `bb29b133` retiradas (`git restore` de cinco y borrado de dos nuevas); limpio en `98f4611`; `.venv` sin bytecode |
| Copia privada | `state/bb29b133-discarded/` del área: los 7 archivos, `tracked.diff`, `cycle-evidence.diff` y `SHA256SUMS` |
| UI | «Django preparado» con el recibo real; Ajustes sin cambios (registro v2) |

**Incidencia en la copia privada.** El script de retirada pasaba las rutas en una variable que zsh no separa en
palabras. La copia falló, pero el script siguió, así que restauró y borró antes de copiar los dos archivos nuevos
(`task_edit.html` y `task_confirm_delete.html`). Se reconstruyeron desde la evidencia del propio producto: el diff
del último ciclo de `bb29b133`, tal como lo recibió el revisor en su prompt (`state/artifacts/`), con la huella
`996c5442…e1423991` de §2. La parte rastreada de ese diff es idéntica al `tracked.diff` copiado directamente del hijo
antes de restaurar. No se perdió contenido. No se abrió la SQLite viva.

**Run `bf007561`.** Contrato: la sección P001-T002 literal del hijo (875 bytes, `acd0105b…bf6790de`, igual que en §1).
Lo encoló el usuario desde la UI.

| Intento | Selección congelada | Resultado | Duración |
|---|---|---|---|
| 1 planificador | Codex `gpt-6-luna`/`medium` (política) | COMPLETE | 16,7 s |
| 2 ejecutor | Claude `claude-sonnet-5-5`/`medium`, elegida por el revisor | COMPLETE | 39,5 s |
| 3 revisor | Codex `gpt-6-luna`/`medium` | COMPLETE, **ACCEPT** | 8,8 s |

- **Selección:** el revisor eligió `claude-sonnet-5-5`/`medium` con un motivo propio de la tarea. El modelo observado
  en el stream es `claude-sonnet-5-5`. Las instrucciones del ejecutor incluyen el aviso del formateador (D133).
- **Formateo del harness:** `ruff format -- core/tests.py core/urls.py core/views.py`, con salida 0 y
  `1 file reformatted, 2 files left unchanged`. Es el caso que detuvo `bb29b133`, resuelto sin el ejecutor.
- **Cambio:** 7 rutas, diff de 10 012 bytes, huella `06ba52f3…b3f6`. Vistas de edición y borrado con
  `get_object_or_404`, `require_http_methods(["GET", "POST"])` y redirección tras POST válido. Plantillas de edición
  y de confirmación con CSRF, enlaces en la lista y flujo en `tasks.md`. Tests: 11 en total.
- **Validaciones:** las seis con salida 0, incluido `ruff format --check .`. pytest pasa los 11 casos JUnit.
- **Revisión y aceptación:** ACCEPT sin hallazgos, preguntas, concesiones ni propuestas. Aceptación elegible.
- **Commit:** confirmado desde la UI por decisión del usuario. Commit `2f2b13f` «harness: accept P001-T002 - Editar y
  borrar», con la identidad Git del usuario, sobre `98f4611`. Run COMMITTED y checkout limpio.
- **Consumo:** 3 invocaciones en esta sesión. T009: 9 de 13. Piloto: 18 de 60.
- **No probado aquí:** QA en navegador del Django (T012) y las parejas con revisor Claude (T010–T011).
