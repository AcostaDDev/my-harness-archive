# Siguiente paso — diagnóstico del escritor Codex

Estado al 2026-10-13:

- **Matriz D057 ejecutada y cerrada** ([resultado](discovery/PROVIDER_MATRIX_RERUN.md)):
  1 Codex→Claude `COMMITTED`; 2 Codex→Codex `REVISION_LIMIT` porque el
  escritor Codex no editó; 3 Claude→Claude `STOPPED` en `planner` por listas
  como texto; 4 no lanzada.
- **`cli-6` completado offline (D058,
  [entrega](discovery/TYPED_JSON_SCHEMA.md)).** El lector Claude recibe como
  `--json-schema` el esquema tipado del motor congelado en el intento. El motor
  sigue rechazando listas serializadas como texto. Falta comprobarlo con
  Claude real.

## Tarea concreta propuesta, no iniciada

**Diagnosticar por qué el escritor Codex no editó en la combinación 2**, sin
consumo de proveedor:

1. Leer cómo describe Codex 0.162.1 sus raíces escribibles en
   `workspace-write`: cadenas y ayuda del binario, sin lanzar sesiones. En
   particular, cómo presenta al modelo el cwd, `/tmp`, `TMPDIR` y
   `writable_roots` cuando el checkout está bajo `/private/tmp`.
2. Contrastarlo con la evidencia conservada de D057 (prompt y stdout del
   ejecutor en `BASE/codex-codex/state/`, si sigue disponible) y con el argv de
   `cli-6`.
3. Valorar y decidir con criterio una o varias medidas, registrándolas:
   - Indicar en el prompt del ejecutor que el checkout es escribible.
   - Pasar `writable_roots` explícitos.
   - Un checkout fuera de `/tmp` en el smoke de la matriz.
4. Si la medida cambia el argv, es un incremento nuevo (`cli-7`) con cuarentena
   de los jobs `cli-6`. Pruebas offline con la CLI sintética y regresión.

Una comprobación con proveedor exige consentimiento específico.

Después, y aparte:

- **Nueva ejecución de la matriz.** Al menos las combinaciones 2–4 tras las
  correcciones, con consentimiento nuevo. Después, el hito de interfaz de
  producto (D054, H6.2).

Alternativas: endurecer `forbidden_paths` frente a prosa (observado en D057);
instalación de operación reutilizable (D051); estudiar el `memory/` vacío que
crea la CLI de Claude; endurecimientos de D048.

Consentimientos anteriores agotados, incluidos D050, D055 y D057. Sin
proveedores/login, instalaciones con red, publicación, push ni uso del harness
para desarrollar este repositorio. Este documento no autoriza ejecuciones con
proveedores.
