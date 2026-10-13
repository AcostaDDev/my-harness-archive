# Siguiente paso — nueva propuesta de la matriz D052

Estado al 2026-10-13:

- **Diagnóstico del escritor Codex completado y mitigación `cli-7`
  implementada offline (D059,
  [entrega](discovery/CODEX_WRITER_ROOTS.md)).** D057 muestra una negativa del
  modelo sin intentar herramientas, no una denegación real de escritura.
  El origen en la descripción de raíces temporales sigue como hipótesis,
  porque no se conservó el mensaje interno de permisos de Codex.
- Codex ejecutor recibe checkout canónico explícito en `writable_roots`,
  `exclude_slash_tmp=true` y una aclaración del acceso solicitado. Mantiene
  TMPDIR explícito, contrato/política y respeto a denegaciones reales. Jobs
  `cli-6` quedan en cuarentena sin reescribir historias anteriores.
- **`cli-6` completado offline (D058,
  [entrega](discovery/TYPED_JSON_SCHEMA.md)).** El lector Claude recibe el
  esquema tipado del motor. Falta comprobarlo con Claude real.
- **Matriz D057 cerrada** ([resultado](discovery/PROVIDER_MATRIX_RERUN.md)):
  1 Codex→Claude `COMMITTED`; 2 Codex→Codex `REVISION_LIMIT`; 3 Claude→Claude
  `STOPPED` en planner; 4 no lanzada. Sus áreas y evidencias se conservan.

## Tarea concreta propuesta, no iniciada

**Preparar una nueva propuesta acotada para las combinaciones 2–4 de la
matriz**, con el paquete `cli-7` y un área nueva, sin consumo durante la
preparación:

1. Concretar selecciones, herramientas, límites, entorno y criterios sobre
   D055/D057, haciendo explícitas las modificaciones D058/D059. No reutilizar
   como autorización los consentimientos anteriores.
2. Preparar y verificar offline el wheel instalado y el recorrido con CLI
   sintéticas. Conservar las áreas anteriores y no modificar ajustes globales.
3. Dejar una orden y propuesta revisables para pedir consentimiento específico
   antes de ejecutar proveedores. La ejecución real es un paso separado.

La futura comprobación real debe acreditar edición de Codex dentro del
contrato, listas/objetos tipados de Claude lector y validación/revisión/commit
por combinación. Fallos detienen su combinación sin retries ni fallback;
no marcar la mitigación del escritor como verificada con proveedor por las
pruebas sintéticas.

Después, y aparte: ejecutar la propuesta con consentimiento nuevo y, tras la
matriz, el hito de interfaz de producto (D054, H6.2).

Alternativas: endurecer `forbidden_paths` frente a prosa (observado en D057);
instalación de operación reutilizable (D051); estudiar el `memory/` vacío que
crea la CLI de Claude; endurecimientos de D048.

Consentimientos anteriores agotados, incluidos D050, D055 y D057. Sin
proveedores/login, instalaciones con red, publicación, push ni uso del harness
para desarrollar este repositorio. Este documento no autoriza ejecuciones con
proveedores. No se ha avanzado a esta nueva tarea.
