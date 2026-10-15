# Resumen de la fase P007 — Agentes configurables e interfaz de producto (antes H6)

**Estado final:** completada el 2026-10-15 por decisión del usuario (D087) · **Decisiones:** D052, D054–D087 ·
Redactado en P008-T001 (D088).

## Entregas

- H6.1: revisor y ejecutor Codex o Claude en cualquier combinación, `cli-5` y `local-config-2`
  ([D052](AGENT_ROLES.md)). Matriz con proveedores: [D055](PROVIDER_MATRIX_RUN.md), formas de salida
  ([D056](CONTRACT_SHAPES.md)), [D057](PROVIDER_MATRIX_RERUN.md), esquema tipado `cli-6` ([D058](TYPED_JSON_SCHEMA.md)),
  raíces del escritor Codex `cli-7` ([D059](CODEX_WRITER_ROOTS.md)), [D060/D061](PROVIDER_MATRIX_CLI7_RUN.md),
  diagnóstico de configuración global ([D062](CODEX_GLOBAL_CONFIG_DIAGNOSIS.md)), contención estudiada y no integrada
  ([D063](CODEX_PROCESS_CONTAINMENT_PROPOSAL.md), [D064](CODEX_CONTAINMENT_QUALIFICATION.md),
  [D065](CODEX_CONTAINMENT_REVISION.md), [D067](CODEX_STARTUP_PREPARATION.md)), memoria automática desactivada `cli-8`
  ([D066](AGENT_PERSISTENCE.md)), supresión de confianza `cli-9` ([D068](CODEX_TRUST_SUPPRESSION.md)), paradas
  [D069/D070](PROVIDER_MATRIX_CLI9_STOPS.md) y cuatro combinaciones COMMITTED ([D071](PROVIDER_MATRIX_CLI9_RUN.md)).
- Organización documental por fase ([D072/D073](DOCUMENT_ORGANIZATION.md)) e implementación H6.3 del contrato v2
  ([entrega](H6.3_DOCUMENT_CONTRACT.md)).
- H6.4: métricas por intento con procedencia (`0014_attempt_metrics`) ([D074](H6.4_METRICS.md)).
- H6.5: creación y planificación conversacionales (`0015_planning`) ([D075](H6.5_CONVERSATIONAL_CREATION.md)).
- H6.2: UI de producto en seis entregas (D076–D084): [E1](H6.2_E1_SHELL.md), [E2](H6.2_E2_REGISTRY.md)
  (`0016_project_registry`), [E3](H6.2_E3_DOCS.md), [E4](H6.2_E4_SETUP.md), [E5](H6.2_E5_CHAT.md)
  (`0017_chat_context`) y [E6](H6.2_E6_STATS.md); revisión de cierre ([REVIEW](REVIEW.md), D085) y correcciones
  ([D086](H6.2_DIFF_PAGINATION.md), `0018_conversation_keys`).

## Verificación y límites

1120 pruebas pytest y 121 subtests, 12 checks ligeros y 72 pruebas Node al cerrar (D086); QA de la UI en claro, oscuro
y móvil con datos sintéticos. Sin recorrido de producto con CLI reales; validaciones sin hora; historial del run
decodificado completo en cada lectura; dos avisos *low* de KaTeX; `package.json` de un `typescript-web` nuevo.

Plan y estado archivados: [NEXT_STEPS](NEXT_STEPS.md) · [STATE](STATE.md).
