# Siguiente paso — Ejecutar la nueva ejecución de la matriz (D057), solo con consentimiento

Estado al 2026-10-13:

- Smoke D055 detenido en el planificador de la combinación 1
  ([resultado](discovery/PROVIDER_MATRIX_RUN.md)). Consentimiento agotado.
- Corrección D056 implementada y verificada offline
  ([entrega](discovery/CONTRACT_SHAPES.md)).
- **Nueva ejecución D057 preparada y ensayada offline**
  ([propuesta](discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md)):
  - Mismas selecciones, límites y criterios que D055.
  - Área nueva `/private/tmp/harness-provider-matrix-2` y wheel con D056.
  - Scripts `examples/provider_matrix/run_pairing.sh` y `drive.py`.
  - Las cuatro combinaciones sintéticas llegan a `COMMITTED`.
- **No ejecutada ni autorizada.**

## Tarea concreta propuesta, no iniciada

**Ejecutar la propuesta D057 una vez**, únicamente con consentimiento
específico y explícito del usuario. Reparto:

- **Claude Code:** preparación, paquete, venv, preflight y revisión de la
  evidencia entre combinaciones.
- **Usuario, con `!`:** la orden de `run_pairing.sh` de cada combinación,
  cuando Claude Code indique que procede.

Registrar el resultado en `docs/discovery/PROVIDER_MATRIX_RERUN.md` y en D057.

Después, y aparte: el hito de interfaz de producto (D054, H6.2), cuya primera
tarea es escribir el alcance.

Alternativas: empezar H6.2 antes; instalación de operación reutilizable
(D051); estudiar el `memory/` vacío que crea la CLI de Claude; endurecimientos
de D048.

Consentimientos anteriores agotados, incluidos D050 y D055. Sin proveedores/
login, instalaciones con red, publicación, push ni uso del harness para
desarrollar este repositorio. Este documento no autoriza ejecutar la matriz.
