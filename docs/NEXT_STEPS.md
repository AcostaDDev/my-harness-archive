# Siguiente paso — Ejecutar el smoke de la matriz D052 (D055), solo con consentimiento

Estado al 2026-10-13:

- D052 implementado y verificado offline (`cli-5`, `local-config-2`,
  [entrega](discovery/AGENT_ROLES.md)).
- **Propuesta del smoke de la matriz preparada y ensayada offline** (D055,
  [propuesta](discovery/PROVIDER_MATRIX_PROPOSAL.md),
  [`prepare.sh`](../examples/provider_matrix/prepare.sh)):
  - Cuatro combinaciones revisor → ejecutor: Codex→Claude, Codex→Codex,
    Claude→Claude y Claude→Codex.
  - El revisor planifica, el ejecutor edita y el revisor revisa; después,
    commit. Modo catálogo y `max_revision_cycles = 0`.
  - Codex `gpt-6-luna` y Claude `claude-sonnet-4-6` (2.1.296). Revisor
    `medium`; ejecutor `low`.
  - Como máximo 3 invocaciones por combinación y 12 en total. 30 min por
    combinación y 2 h para la matriz.
  - Un fallo detiene solo su combinación, sin reintento. Los fallos de
    autenticación, cuota o preflight omiten las pendientes que usan ese proveedor.
- **No ejecutada ni autorizada.**

## Tarea concreta propuesta, no iniciada

**Ejecutar la propuesta D055 una vez**, únicamente si el usuario da un
consentimiento específico y explícito para ella. Se siguen sus pasos, límites
y criterios tal como están escritos:

- Fuera del sandbox, desde el wheel instalado en `BASE/venv`.
- Preflight por combinación.
- Resultado por combinación: completa, fallida (con su etapa) o no lanzada
  (con su motivo).
- Registrar el resultado en `docs/discovery/PROVIDER_MATRIX_RUN.md` y en D055.

Cualquier cambio de combinación, modelo, esfuerzo, modo, herramientas, límites
o entorno exige actualizar antes la propuesta. Solo `BASE` puede cambiar si ya
existe, y se registra.

Después, y aparte: el **hito de interfaz de producto** (D054, backlog H6.2),
cuya primera tarea es escribir el alcance.

Alternativas: empezar H6.2 antes del smoke si el usuario lo prefiere;
instalación de operación reutilizable (D051); estudiar el `memory/` vacío que
crea la CLI de Claude; endurecimientos de D048.

Consentimientos anteriores agotados, incluido D050. Sin proveedores/login,
instalaciones con red, publicación, push ni uso del harness para desarrollar
este repositorio. Este documento no autoriza ejecutar el smoke ni iniciar otra
implementación.
