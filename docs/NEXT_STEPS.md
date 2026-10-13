# Siguiente paso — Elección del nuevo alcance tras revisar el ejecutor

Revisión independiente del ejecutor de validaciones (D047) completada el
2026-10-13 (D048). Ver [dictamen](discovery/COMMAND_RUNNER_REVIEW.md),
[entrega](discovery/COMMAND_RUNNER.md) y [alcance](discovery/COMMAND_RUNNER_SCOPE.md).

- Hallazgo medio corregido: un run con `command_config_sha256` congelado ya no
  puede ejecutarse con otro runner; el supervisor aborta antes de efectos con
  cuarentena. Prueba de regresión nueva.
- Sin hallazgos en ventana intención/identidad/GO, exclusión, captura ni
  compatibilidad de historiales. Límites conocidos registrados sin cambio de
  diseño: liveness por PGID sin instante de arranque y validador silencioso
  que continúa hasta su timeout tras fallar el heartbeat.
- 811 pruebas pytest y 121 subtests, 12 checks ligeros y 6 pruebas Node
  correctos. Esquema, codec, cli-4, OpenAPI, UI y dependencias sin cambios.

## Tarea concreta propuesta, no iniciada

Pedir al usuario el siguiente alcance entre:

1. **Composición de uso real** (recomendada): configuración explícita del
   servidor que componga agentes CLI, `ManagedCommandRunner` y Git para un
   checkout desechable, con alcance y criterios escritos antes del código y
   verificación offline. No incluye ejecutar proveedores.
2. QA visual reciente, pendiente de un navegador que permita loopback.
3. Propuesta de smoke completo (tarea → commit → check → cierre, D033.8), que
   requiere autorización específica, checkout desechable y modelos/esfuerzos
   elegidos por el usuario.

Opcionalmente, endurecimientos derivados de la revisión (cancelar validadores
al fallar el heartbeat; identidad con instante de arranque) como tarea acotada.
Consentimientos anteriores agotados. Sin proveedores/login, instalaciones con
red, publicación, push ni uso del harness para desarrollar este repositorio.
Este documento no autoriza iniciar otra implementación.
