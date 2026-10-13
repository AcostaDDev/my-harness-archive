# Siguiente paso — ejecución separada de la propuesta D060

Estado al 2026-10-13:

- **Preparación de las combinaciones 2–4 completada offline (D060).**
  [Propuesta, órdenes y criterios](discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md),
  [manifiesto de hashes y ensayo sintético](discovery/PROVIDER_MATRIX_CLI7_PREPARATION.json).
- Área nueva `/private/tmp/harness-provider-matrix-3`: wheel/sdist `cli-7`,
  venv instalado offline por hashes, tres TOML privados con `check-config`
  válido y checkouts desechables limpios con la regresión. Estado vacío, sin
  SQLite, jobs, intentos ni servicio. **CLI reales y preflight real no ejecutados.**
- Ensayo separado con CLI sintéticas y servicio instalado: Codex→Codex,
  Claude→Claude y Claude→Codex COMMITTED con un commit nuevo solo en
  `src/estimate.ts`; salida inválida detiene planner sin otros roles ni commit.
  Paquete verificado; 82 pytest focales y 12 checks ligeros correctos.
- D058 conserva el esquema tipado de Claude lector y D059 las raíces
  explícitas/aclaración de transporte del escritor Codex (`cli-7`). Las
  pruebas sintéticas **no certifican** su comportamiento con proveedores.
- Matriz D057 cerrada: 1 COMMITTED, 2 REVISION_LIMIT, 3 STOPPED en planner,
  4 no lanzada. Sus áreas/evidencias se conservan. Consentimientos agotados.

## Tarea concreta propuesta, no iniciada

**Ejecutar la propuesta D060 una sola vez, únicamente después de
consentimiento específico nuevo del usuario.** Sin consentimiento, no lanzar
ninguna combinación ni crear jobs.

1. Revisar propuesta y manifiesto con el usuario. Selecciones propuestas:
   Codex `gpt-6-luna`, Claude `claude-sonnet-4-6`; revisor medium, catálogo
   del ejecutor low, `planning_mode = "agent"`, cero correcciones. Máximo
   nueve invocaciones para 2–4, límite operativo total de 90 minutos.
2. Con consentimiento: comprobar hashes del paquete/scripts/TOML, estado
   vacío y puerto :8013 libre; preflight de las versiones fijadas desde el
   wheel instalado. Ejecutar una orden por combinación, en orden 2 → 3 → 4,
   revisando evidencia y parada entre ellas. Sin reconstruir el paquete,
   actualizar CLI ni reutilizar áreas antiguas o del ensayo.
3. Acreditar edición real de Codex dentro del contrato (2/4), listas/objetos
   tipados del lector Claude (3/4), validación/JUnit/review/commit por
   contenido exacto en cada combinación. Conservar originales, hashes y
   diferencia entre solicitado/reportado/ausente.
4. Fallos detienen su combinación sin retries ni fallback; auth/cuota/preflight
   omiten pares pendientes que usan ese proveedor. Parar todo ante efectos
   fuera de BASE, servicio no detenible o plazo total agotado. No recuperar
   jobs ni liberar locks. Registrar resultado y actualizar STATE/NEXT_STEPS.

Después, y aparte: hito de interfaz de producto (D054, H6.2). Alternativas
pendientes: `forbidden_paths` frente a prosa; instalación de operación
reutilizable (D051); `memory/` vacío de Claude; endurecimientos de D048.

Esta entrega solo ha preparado D060 y no ha avanzado a su ejecución. Este
documento no concede consentimiento. D050, D055 y D057 siguen agotados. Sin
proveedores/login, instalaciones con red, publicación, push ni uso del
harness para desarrollar este repositorio.
