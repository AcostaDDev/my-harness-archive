# Siguiente paso — Preparar la nueva ejecución de la matriz D052

Estado al 2026-10-13:

- Smoke de la matriz D055 ejecutado y detenido
  ([resultado](discovery/PROVIDER_MATRIX_RUN.md)): la combinación 1 paró en el
  planificador porque `validation_commands` llegó como listas de argv.
  Combinaciones 2–4 no lanzadas. Consentimiento agotado.
- **Corrección D056 implementada y verificada offline**
  ([entrega](discovery/CONTRACT_SHAPES.md)):
  - Esquema fijo del motor con tipos de elemento.
  - Plantilla `plan-task` aclarada.
  - Listas de argv normalizadas con `shlex.join`.
  - Forma de `findings` declarada al revisor.
  - Regresión D055 por el adaptador real en verde.

## Tarea concreta propuesta, no iniciada

**Preparar la nueva ejecución de la matriz**, sin ejecutar nada; el usuario la
autorizará aparte:

1. Reutilizar D055 (mismas cuatro combinaciones, recorrido, modelos, límites y
   reglas de fallo) salvo que el usuario elija otra cosa. Registrar como
   propuesta nueva o como enmienda fechada de D055.
2. Área nueva (no reutilizar `/private/tmp/harness-provider-matrix`, que
   conserva la evidencia de D055) y wheel construido con D056.
3. Versionar el script de recorrido en `examples/provider_matrix/`:
   - Esperar hasta `finished_at` o `RECOVERY_REQUIRED`.
   - Instantánea por API completa.
   - Órdenes para que el usuario lance con `!` las que arrancan agentes, porque
     el clasificador de permisos de Claude Code las bloquea.
4. Ensayarla offline: `check-config` y `--preflight` desde el venv, admisión sin
   supervisor y el script de recorrido contra un servicio con CLI sintéticas.

Después, y aparte: ejecutarla solo con consentimiento explícito. A
continuación, el hito de interfaz de producto (D054, H6.2).

Alternativas: empezar H6.2 antes; instalación de operación reutilizable
(D051); estudiar el `memory/` vacío que crea la CLI de Claude; endurecimientos
de D048.

Consentimientos anteriores agotados, incluidos D050 y D055. Sin proveedores/
login, instalaciones con red, publicación, push ni uso del harness para
desarrollar este repositorio. Este documento no autoriza otra ejecución con
proveedores.
