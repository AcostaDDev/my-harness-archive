# Resumen de la fase P003 — Núcleo reusable y ejecución gestionada (antes H2)

**Estado final:** completada el 2026-10-12 · **Decisiones:** D015–D029 · Redactado en P008-T001 (D088).

## Entregas

- H2.1: motor extraído con `ProjectContext` y perfil ReferenceProject declarativo ([entrega](H2.1_ENGINE.md)).
- H2.2: persistencia, cola idempotente, lease y exclusión por checkout (`0004_managed_queue`)
  ([entrega](H2.2_PERSISTENCE.md)).
- H2.3: adaptadores CLI con captura incremental, cancelación y recuperación (`0005_cli_processes`)
  ([entrega](H2.3_CLI.md)). Smokes reales autorizados: fallo de configuración Codex ([D018](H2.3_SMOKE.md)),
  corrección `cli-2` ([D019](H2.3_CONFIG_FIX.md)), fallo MCP de Claude ([D020](H2.3_SMOKE_RETRY.md)), corrección
  `cli-3` ([D021](H2.3_MCP_FIX.md)), fallo de autenticación ([D022](H2.3_SMOKE_CLI3.md)), diagnóstico de `USER`
  ([D023](H2.3_AUTH_DIAGNOSIS.md)), corrección del entorno ([D024](H2.3_ENV_FIX.md)) y transporte completo de las
  tres CLI ([D025](H2.3_ENV_SMOKE.md)).
- H2.4: captura Git por árboles, worktree por tarea y commit determinista conciliable (`0006_git_commits`)
  ([entrega](H2.4_GIT.md)).
- H2.5: migración a modo gestionado con copia inmutable, marcador y reversión (`0007_managed_activation`)
  ([entrega](H2.5_MIGRATION.md)).
- Salida del hito: API `/api/managed` con supervisor opt-in ([D028](H2_EXIT_API.md)) y UI gestionada hasta
  COMMITTED ([D029](H2_EXIT_UI.md)).

## Verificación y límites

Git y SQLite sintéticos con agentes falsos; el smoke D025 acredita el transporte, no una tarea de producto real.
COMMITTED es un checkpoint del worktree, sin integración en la rama destino.

Plan y estado archivados: [NEXT_STEPS](NEXT_STEPS.md) · [STATE](STATE.md).
