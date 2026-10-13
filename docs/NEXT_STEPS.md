# Siguiente paso — Propuesta autorizable del smoke de la matriz D052

Estado al 2026-10-13:

- Primer uso real D050 ejecutado y completo ([resultado](discovery/FIRST_USE_RUN.md));
  uso real desde el wheel instalado (D051). Consentimiento agotado.
- `scripts/dev` implementado y verificado (D053, [entrega](discovery/DEV_COMMAND.md)).
- **D052 implementado y verificado offline** (`cli-5`, `local-config-2`,
  [entrega](discovery/AGENT_ROLES.md)):
  - Revisor y ejecutor, cada uno Codex o Claude.
  - El usuario fija proveedor, modelo y esfuerzo del revisor.
  - El revisor fija modelo y esfuerzo del ejecutor en modo catálogo o libre.
  - Planificación `agent` | `deterministic` por proyecto.
  - Matriz de las cuatro combinaciones verificada con CLI sintéticas por el
    adaptador real.

## Tarea concreta propuesta, no iniciada

**Preparar la propuesta del smoke de la matriz D052 con proveedores**,
redactada sin ejecutar nada y que el usuario autorizará aparte. Debe:

1. Elegir con el usuario qué combinaciones prueba (las cuatro o un subconjunto),
   con qué modelos y esfuerzos, y en qué modo de selección y de planificación.
   Incluye fijar los límites de invocaciones y ciclos.
2. Definir un checkout desechable (como `examples/first_use/`) y un
   `local-config-2` por combinación, validados con `check-config --preflight`
   desde el wheel instalado (D051).
3. Indicar qué confirma cada combinación y qué se hace si falla, sin reintento
   automático:
   - Codex `workspace-write` sin red, con cambios de archivo reales.
   - Claude lector con `--json-schema` bajo `--tools Read,Glob,Grep` y
     `--restricted`.
   - Los vocabularios de esfuerzo inferidos del binario de Codex.
4. Ensayarla offline y registrar la decisión en DECISIONS.

Después, y aparte: ejecutar el smoke solo con consentimiento explícito; a
continuación, el **hito de interfaz de producto** (D054, backlog H6.2), cuya
primera tarea es escribir el alcance.

Alternativas: empezar H6.2 antes del smoke si el usuario lo prefiere;
instalación de operación reutilizable (D051); estudiar el `memory/` vacío que
crea la CLI de Claude; endurecimientos de D048.

Consentimientos anteriores agotados, incluido D050. Sin proveedores/login,
instalaciones con red, publicación, push ni uso del harness para desarrollar
este repositorio. Este documento no autoriza iniciar otra implementación ni
otra ejecución con proveedores.
