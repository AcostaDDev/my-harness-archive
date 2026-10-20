# P009-T015 — Verificación del wheel con el flujo D088

Fecha: 2026-10-20. Decisión: [D126](../DECISIONS.md#d126--p009-t015-el-wheel-se-verifica-con-la-definición-d088).
Origen: la verificación del wheel de T007 falló con 405 en `POST /projects/offline/bootstrap/preview`
([§5](P009-T007_CREACION_DJANGO.md#5-verificación-del-wheel-incompleta)). Elegida por el usuario antes de reanudar T007,
para que el wheel de la reanudación se verifique entero.

## 1. Cambios

| Archivo | Cambio |
|---|---|
| `scripts/check_distribution.py` | Tramo v1 sustituido por la definición D088 por HTTP; `TMPDIR` propio y comprobado |
| `tests/fixtures/e2e/installed_config.py` | Marcador v2, `documents = "v2"`, validación sintética y respuesta `definition` |
| `docs/ARCHITECTURE.md` §9 | Qué escribe `serve` bajo `TMPDIR` y cómo mantenerlo dentro del área |

Recorrido nuevo, con el wheel instalado en un venv temporal y sin Node, proveedores ni red:

1. La ruta v1 retirada no responde (404/405). `GET /bootstrap` declara la definición habilitada.
2. Conversación `definition` (201) y un turno: el agente sintético propone README, SPECIFICATION, ARCHITECTURE,
   ROADMAP, DECISIONS, STATE y NEXT_STEPS. Cada borrador se aplica con versión, hash y confirmación.
3. Vista previa de aceptación lista. Sin confirmar devuelve 422 y no crea `.git`. Confirmada, el commit raíz
   completa la operación y deja AGENTS y DDBB-DIAGRAM desde la plantilla. Solo se ha invocado `definition`.
4. Reinicio: la misma clave de aceptación devuelve la misma operación. P001-T001, tomada del `task_text` de la vista
   previa, llega a `ACCEPTANCE_READY` con `app/outcome.txt` como único cambio y termina `COMMITTED` con el commit esperado.
5. Otro reinicio no repite agentes. Se mantienen igual que antes los errores de configuración y de esquema, el backup
   y la restauración de consulta con el checkout ausente.

Detalles fijados con criterio: el fixture usa `app/**` como ruta de la tarea porque los perfiles protegen `docs/**`
frente al ejecutor. La validación `test-runner check` se resuelve con `ScriptedCommandRunner` (salida 0), igual que en
`test_e2e_offline`. El fixture se mantiene autocontenido: lo único que importa es `harness_local` instalado.

## 2. Verificación

| Comprobación | Resultado |
|---|---|
| `build_distribution.py --out-dir <scratchpad>/dist` desde el árbol de esta tarea | sdist, wheel y `requirements.txt` sin conexión |
| `check_distribution.py --dist <scratchpad>/dist` | correcto en unos 20 s: «Wheel aislado: … definición D088/tarea/commit/reinicio …» |
| pytest completo (xdist) | 1570 passed, 1 skipped, 121 subtests en 4:18 |
| unittest | 12 tests OK |
| `test_documentation_parity` tras editar los documentos | 11 passed |

No se probó: el script no cubre la receta Django (requiere wheelhouse y herramientas reales, T005) ni CLI reales.
El área del piloto, su SQLite y `harness-django-pilot` no se tocaron.
