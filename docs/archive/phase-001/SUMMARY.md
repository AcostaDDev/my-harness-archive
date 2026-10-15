# Resumen de la fase P001 — Contratos y prueba de viabilidad (antes H0)

**Estado final:** completada el 2026-10-11 · **Decisiones:** D006–D011 · Redactado en P008-T001 (D088).

## Entregas

- H0.1: inventario de la referencia ReferenceProject con procedencia y separación núcleo/perfil
  ([BASELINE](BASELINE.md), [formatos legacy](LEGACY_FORMATS.md)), manifiesto SHA-256 (ahora
  `tests/fixtures/legacy/baseline.json`) y cinco escenarios sintéticos en `tests/fixtures/legacy/`.
- H0.2: versiones de Python, uv, Node y npm, matriz de capacidades y autenticación de las CLI
  ([compatibilidad](H0.2_COMPATIBILITY.md), [metadatos](h0.2-version-metadata.json)) y sonda offline de streams.
- H0.3: esqueleto con núcleo, API FastAPI, SQLite `0001_simulations` y UI React que muestra simulaciones
  ([entrega](H0.3_SKELETON.md)).

## Verificación y límites

Doce checks de biblioteca estándar (fixtures y streams) y arranque del esqueleto, sin agentes ni red. Las CLI se
comprobaron por versión y ayuda; la autenticación no se certificó.

Plan y estado archivados: [NEXT_STEPS](NEXT_STEPS.md) · [STATE](STATE.md).
