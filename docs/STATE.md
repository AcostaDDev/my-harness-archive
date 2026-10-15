# Estado — my_harness

Actualizado: 2026-10-15. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Codec de historial en formato 7 (lee 1–6).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0018_conversation_keys` (34 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams.
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-9`, `local-config-2/3`), revisor en solo lectura con esquema tipado, memoria automática desactivada, supresión
  de confianza del escritor Codex. Validaciones nativas `commands-1` con JUnit. Perfiles: `typescript-web` (componible
  desde el TOML) y `reference_project` (solo biblioteca).
- **Fases y documentos** ([P004](archive/phase-004/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): check READY,
  reconciliación, preguntas, lote desatendido, enmiendas, abandono y cierre con tag. Contrato documental v2 opcional
  (`documents = "v2"`, con `decisions/`, `architecture/` y `research/`): bloques regenerados en cada commit, edición
  confirmada, exportación y transición separada que archiva en `archive/phase-NNN/`.
- **Creación y chat** ([P005](archive/phase-005/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): bootstrap v1 desde
  carpeta vacía; creación v2 por conversación con borradores en disco y CAS; planificación de fase conversacional; chat
  sobre una instantánea de HEAD sin lock, con comandos deterministas y propuestas que crean tareas confirmadas.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación legacy en `/legacy`.
- **Operación** ([P006](archive/phase-006/SUMMARY.md)): wheel con UI y migraciones, `init-db`, `serve`,
  `check-config`, `metrics-backfill`, `diagnose-cli`; `scripts/dev` para desarrollo.
- **Evidencia con proveedores reales** (consentimientos agotados): transporte de las tres CLI (D025), primer uso real
  COMMITTED con fase cerrada (D050) y cuatro combinaciones revisor/ejecutor COMMITTED (D071).
- **Límites**: ningún recorrido de producto completo con CLI reales; contención cooperativa sin aislamiento del sistema
  operativo; validaciones sin hora; historial del run decodificado completo en cada lectura; `package.json` de un
  `typescript-web` nuevo; dos avisos *low* de KaTeX.

## Fase activa — P008 Contrato documental unificado, cierre de fase e importación de proyectos

Objetivo y criterios en [ROADMAP](ROADMAP.md); plan en [NEXT_STEPS](NEXT_STEPS.md); decisión de base D088.

**P008-T001 completada** (migración documental de este repositorio, sin cambios del motor):

- `docs/discovery/` eliminado; su contenido está en `docs/archive/phase-000…007/` con NEXT_STEPS, STATE y SUMMARY por
  fase y REVIEW donde hubo revisión de cierre. Registro e incongruencias del motor en
  [docs/phase](phase/P008-T001_MIGRACION_DOCUMENTAL.md).
- Nuevos SPECIFICATION, ARCHITECTURE, ROADMAP, DDBB-DIAGRAM y `docs/flows/` (seis flujos); DECISIONS con índice y
  D088; AGENTS (45 líneas), CLAUDE (8), GEMINI (5) y README (79).
- Código: solo la ruta de `baseline.json` (ahora en `tests/fixtures/legacy/`) en `tests/test_legacy_fixtures.py` y dos
  docstrings.
- Verificación: 12 checks ligeros; pytest 1120 pruebas y 121 subtests (un aviso de deprecación de Starlette sobre
  `httpx`, ajeno a esta tarea); 72 pruebas Node; ningún enlace relativo roto en los Markdown del repositorio; 16
  diagramas Mermaid válidos con el parser de `mermaid` 11.17.2; `parse_roadmap` (P001–P008) y `plan_tasks` (15 tareas)
  del motor aceptan ROADMAP y NEXT_STEPS; los 18 documentos activos pasan el parser de bloques; STATE 4,5 KiB (base
  3,2 KiB) y NEXT_STEPS 22 KiB dentro de presupuesto. No se ejecutaron `alembic check` ni el build del frontend: no
  cambian modelos, migraciones ni UI.

**Siguiente:** P008-T002 (layout unificado obligatorio y plantilla), sin iniciar. El motor sigue implementando el layout
v2 de D072/D073 hasta T002–T007; este repositorio no está registrado, así que no le afecta.
