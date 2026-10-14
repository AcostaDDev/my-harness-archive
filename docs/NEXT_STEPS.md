# Siguiente paso: H6.4, métricas por intento y estadísticas

Estado al 2026-10-14:

- **D072 confirmado por el usuario (D073) y H6.3 implementado offline.**
  [Entrega, API y límites](discovery/H6.3_DOCUMENT_CONTRACT.md),
  [diseño](discovery/DOCUMENT_ORGANIZATION.md).
- Contrato documental v2 opt-in (`documents = "v2"`): layout con carpetas
  `decisions/`, `architecture/`, `research/` y `archive/phase-NNN/`, bloques
  legibles regenerados en cada commit de tarea con adopción de hashes,
  contratos que protegen los documentos del harness, transición de fase
  conciliable y edición documental confirmada (API y editor).
- Sin cambios de UI (D073: tarea aparte), proveedores ni migraciones.

## Tarea concreta propuesta, no iniciada

**H6.4 — Métricas por intento y estadísticas, offline (D072 §9).**

1. Caracterizar offline, sin ejecutar CLI, los campos de consumo que reportan
   Codex y Claude en los streams reales conservados de D071 (usage, modelUsage,
   num_turns, duraciones, coste, denegaciones) y fijar el catálogo con su
   procedencia: solicitado, reportado, derivado o ausente.
2. Migración `attempt_metrics` materializada en la transacción que registra el
   resultado del intento: proyecto, fase, tarea, run, rol, proveedor, modelo y
   esfuerzo solicitados y reportados, tokens por tipo y por modelo, incremental
   o acumulado, turnos, herramientas, duraciones, coste «equivalente API» y
   resultado. Null distinto de cero.
3. Ampliar la captura del terminal (turnos, duración de API) con una versión
   nueva de normalización. Relleno idempotente de los intentos anteriores desde
   `result_json` y los streams conservados verificados por hash, con
   procedencia `backfill`.
4. Agregados paginados por tarea, fase, proyecto y global: consumo por rol,
   proveedor, modelo y día; modelos y esfuerzos más usados; aceptación a la
   primera; correcciones; duración por tarea; paradas por motivo; tests OK/KO.
   Añadir tokens y turnos al SUMMARY de las fases que se archiven después.

Criterios: streams sintéticos incrementales y acumulados, campos ausentes,
varios modelos por intento, fallos y cancelaciones; relleno idempotente; la
retención H5.3 no pierde métricas; nada se cuenta dos veces; no se deduce
cuota; los historiales anteriores siguen legibles. Sin proveedores ni UI.
Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

Después: H6.5 (creación y planificación conversacionales, sobre la plantilla
de H6.3) y, como tarea aparte, la UI H6.2.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real
requiere una propuesta y un consentimiento nuevos. Sin push ni publicación.
