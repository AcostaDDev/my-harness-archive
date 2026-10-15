# Resumen de la fase P004 — Personalización, bloqueos y cierre (antes H3)

**Estado final:** completada el 2026-10-13 · **Decisiones:** D030–D034 · Redactado en P008-T001 (D088).

## Entregas

- H3.1: catálogo de prompts por ámbito, versiones inmutables, activación y rollback, snapshot por intento
  (`0008_prompt_versions`) ([entrega](H3.1_PROMPTS.md)).
- H3.2: permisos por petición exacta con caducidad y huella, consumo once/task y CLI `cli-4` (`0009_permissions`)
  ([entrega](H3.2_PERMISSIONS.md)).
- H3.3: fases en SQLite, check READY por contenido exacto, cierre con tag por CAS y autorizaciones separadas de lote y
  cierre (`0010_phases`) ([entrega](H3.3_PHASES.md)).
- H3.4: lote desatendido con commits, enmiendas versionadas, abandono, tags anotados y reconciliación con agente
  (`0011_phase_amendments`) ([entrega](H3.4_PHASE_ADJUSTMENTS.md)). D033 recoge las decisiones del usuario tras H3.3.

## Verificación y límites

Pruebas offline y recorridos en Chrome con datos sintéticos. El cierre no editaba documentos ni instalaba la fase
siguiente (lo añadió P007 y lo unifica P008).

Plan y estado archivados: [NEXT_STEPS](NEXT_STEPS.md) · [STATE](STATE.md).
