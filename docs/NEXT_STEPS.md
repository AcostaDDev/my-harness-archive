# Siguiente paso — Revisión del ejecutor de validaciones

Ejecutor nativo de comandos de producto implementado y verificado offline el
2026-10-13 (D047). El usuario eligió este incremento expresamente, resolviendo
la elección pendiente tras H5.7/D046. Ver [entrega](discovery/COMMAND_RUNNER.md)
y [alcance previo](discovery/COMMAND_RUNNER_SCOPE.md).

- Composición explícita `ManagedCommandRunner`, configuración/hash congelados,
  confianza/autorización/política separadas, argv sin shell y entorno completo.
- Captura acotada y resultados observados; journal/gate/grupos/lock reutilizados.
- Caída/reinicio con validador vivo conserva exclusión; recuperación explícita
  sin señalar PIDs recuperados, repetir ejecución ni adoptar evidencia parcial.
- Preparación/validaciones TypeScript reales offline, JUnit, agentes falsos,
  aceptación/commit exactos y backup/restauración comprobados en temporales.
- Esquema `0013_bootstrap`, cli-4 y dependencias conservados; codec 7 para capturas
  nativas, formatos anteriores compatibles. Sin nueva UI ni proveedores.

## Tarea concreta propuesta, no iniciada

Revisión independiente del ejecutor de validaciones y su recuperación: contrastar
D047, implementación y pruebas con los criterios del alcance, especialmente la
ventana intención/identidad/GO, conservación de exclusión y compatibilidad de
historiales. El usuario coordina la herramienta revisora; no lanzar subagentes.
Resolver los hallazgos acotados que se acuerden antes de elegir composición de
uso real o piloto. Este documento no autoriza iniciar otra implementación.

QA visual reciente sigue pendiente del navegador que permita loopback.
La composición completa con proveedores y un eventual smoke (tarea → commit →
check → cierre, D033.8) requieren propuesta y autorización específica, checkout
desechable y modelos/esfuerzos elegidos por el usuario. Consentimientos anteriores
agotados. Sin proveedores/login, instalaciones con red, publicación, push ni
uso del harness para desarrollar este repositorio.
