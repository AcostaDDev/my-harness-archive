# Siguiente paso — Agentes revisor y ejecutor con proveedor elegido (D052)

Estado al 2026-10-13:

- Primer uso real D050 ejecutado y completo ([resultado](discovery/FIRST_USE_RUN.md));
  uso real desde el wheel instalado (D051). Consentimiento agotado.
- `scripts/dev` implementado y verificado (D053, [entrega](discovery/DEV_COMMAND.md)):
  un comando para dependencias, migración con instantánea previa, API :8013 y
  Vite :5173. Corregido el proxy de Vite que rompía el login de la UI de desarrollo.
- Decisión D052: revisor y ejecutor, cada uno Codex o Claude; el usuario fija
  el revisor y el revisor fija modelo y esfuerzo del ejecutor (catálogo o
  libre). [Alcance](discovery/AGENT_ROLES_SCOPE.md).

## Tarea concreta propuesta, no iniciada

**Implementar D052 offline (`cli-5`, `local-config-2`)** según el alcance:

1. Caracterizar por version/help, sin consumo: Codex `workspace-write` y sus
   eventos, salida estructurada y solo lectura de Claude, y vocabularios de
   esfuerzo. Decidir si entra Claude 2.1.296.
2. Planificación determinista confirmada como ajuste del usuario (`agent` |
   `deterministic`); validar su selección según el modo catálogo/libre.
3. Configuración por agente, argv por (proveedor, acceso), política con modo
   catálogo/libre y revisor como planificador. Capacidades H3.2 por proveedor,
   UI/API con el proveedor de cada agente y compatibilidad `local-config-1`.
4. Matriz offline de las cuatro combinaciones con CLI falsas por el adaptador
   real, más la regresión completa.

Después, y aparte: propuesta autorizable de smoke de la matriz con proveedores.

Alternativas: instalación de operación reutilizable (D051); estudiar el
`memory/` vacío que crea la CLI de Claude; QA visual (ahora con `scripts/dev`);
endurecimientos de D048.

Consentimientos anteriores agotados, incluido D050. Sin proveedores/login,
instalaciones con red, publicación, push ni uso del harness para desarrollar
este repositorio. Este documento no autoriza iniciar otra implementación ni
otra ejecución con proveedores.
