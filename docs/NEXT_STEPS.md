# Siguiente paso — Corregir el contrato de `validation_commands` del planificador

Estado al 2026-10-13:

- D052 implementado y verificado offline (`cli-5`, `local-config-2`,
  [entrega](discovery/AGENT_ROLES.md)).
- **Smoke de la matriz D055 ejecutado y detenido**
  ([resultado](discovery/PROVIDER_MATRIX_RUN.md)):
  - La combinación 1 (Codex→Claude) falló en el planificador:
    `Invalid task validation_commands`.
  - El planificador real devolvió `[["npm","run","check"], …]`: la plantilla
    `plan-task` pide «argv commands», el esquema solo dice `array` y el motor
    exige cadenas.
  - El usuario decidió parar y corregir; combinaciones 2–4 no lanzadas.
  - Consentimiento agotado.

## Tarea concreta propuesta, no iniciada

**Corregir offline el contrato de `validation_commands` del planificador**
para que un planificador real y el motor coincidan. Debe:

1. **Elegir y registrar la forma.** Opciones:
   - Aclarar la plantilla y el esquema: cadenas sin shell, con `items` de tipo
     `string` y un ejemplo.
   - Aceptar además listas de argv, normalizándolas con `shlex.join` antes de
     congelar el contrato.
   - Ambas cosas.

   Los contratos y catálogos congelados anteriores no se reescriben.
2. **Revisar los demás campos.** Ver si `allowed_paths`, `forbidden_paths`,
   `acceptance_criteria` y la review tienen la misma ambigüedad entre plantilla,
   esquema y validación.
3. **Pruebas offline.** Una CLI sintética que devuelva la forma observada (y su
   regresión); el lector Claude con `--json-schema` incluye la identidad
   corregida del rol.
4. **Script de recorrido de la próxima ejecución.** Esperar hasta `finished_at`
   o `RECOVERY_REQUIRED`, no solo hasta salir de `QUEUED`/`RUNNING`. Valorar
   versionarlo en `examples/provider_matrix/`.

Después, y aparte: preparar una nueva ejecución de la matriz (área nueva,
mismas selecciones u otras elegidas por el usuario), que exige consentimiento
nuevo. A continuación, el hito de interfaz de producto (D054, H6.2).

Alternativas: empezar H6.2 antes; instalación de operación reutilizable
(D051); estudiar el `memory/` vacío que crea la CLI de Claude; endurecimientos
de D048.

Consentimientos anteriores agotados, incluidos D050 y D055. Sin proveedores/
login, instalaciones con red, publicación, push ni uso del harness para
desarrollar este repositorio. Este documento no autoriza otra ejecución con
proveedores.
