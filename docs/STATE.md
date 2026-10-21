# Estado — my_harness

Actualizado: 2026-10-21. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P009 cerradas.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Formateo del perfil tras cada turno del ejecutor (D133). Codec de historial
  en formato 8 (lee 1–7).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0022_project_preparation` (42 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams.
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-13`, `local-config-2/3/4/5`), revisor en solo lectura con esquema tipado, memoria automática desactivada,
  supresión de confianza del escritor Codex. Validaciones nativas `commands-1` con JUnit. Perfiles: `typescript-web`
  (componible desde el TOML), `reference_project` (solo biblioteca) y perfiles declarados en `[profiles.*]` de
  `local-config-4`, con el ejemplo `python-django` (P008, D095).
- **Fases y documentos** ([P004](archive/phase-004/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md),
  [P008](archive/phase-008/SUMMARY.md)): check READY, reconciliación, preguntas, lote desatendido,
  enmiendas, abandono y cierre con tag. Contrato documental unificado y
  obligatorio de D088 desde P008-T002 (layout v2 modificado; DECISIONS único con índice): bloques regenerados en cada
  commit, edición confirmada, exportación y cierre unificado que archiva en `archive/phase-NNN/`, con
  planificación posterior confirmada (D091).
  `AGENTS.md` congelado por intento, salvo definición; `document_layout = "d088-12"`.
- **Creación y chat** ([P005](archive/phase-005/SUMMARY.md), [P007](archive/phase-007/SUMMARY.md)): creación por
  conversación con borradores en disco y CAS (la v1 se rechaza desde P008-T002); planificación de fase conversacional; chat
  sobre una instantánea de HEAD sin lock, con comandos deterministas y propuestas que crean tareas confirmadas.
- **Creación y preparación Django** ([P009](archive/phase-009/SUMMARY.md), D117–D119): carpeta padre
  elegida y retirada desde UI, hijos nuevos con intención/recuperación, presets por proyecto en `local-config-5`
  y receta `django-recipe-1` confirmada tras D088; entorno acreditado y commit técnico separado. Selector de
  tareas del NEXT_STEPS con CAS y notas congeladas (D135). Wheel verificado con definición D088 (D126).
- **Importación de proyectos** ([P008](archive/phase-008/SUMMARY.md)): inventarios deterministas,
  conversación de solo lectura y borradores privados; normalización de harness anterior (A) e incorporación
  desde código sin harness (B), con perfil confirmado, originales conservados y commit conciliable.
  Frontera Git A/B sin filtros, inspección de submódulos ni lazy-fetch; objetos necesarios locales,
  blobs por hash y destinos ignorados comprobados antes de escribir, también al recuperar.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación legacy en `/legacy`.
- **Operación** ([P006](archive/phase-006/SUMMARY.md)): wheel con UI y migraciones, `init-db`, `serve`,
  `check-config`, `metrics-backfill`, `diagnose-cli`; `scripts/dev` para desarrollo.
- **Evidencia con proveedores reales** (consentimientos agotados): transporte de las tres CLI (D025), primer uso real
  COMMITTED con fase cerrada (D050), cuatro combinaciones revisor/ejecutor COMMITTED (D071) y recorrido Django
  desde creación UI hasta cuatro tareas, QA conjunto y cierre/archivo de P001 (P009-T012, D139);
  26 invocaciones de 60 previstas, sin autorización para operaciones nuevas.
- **Límites**: contención cooperativa sin aislamiento del sistema operativo; validaciones sin hora; historial del
  run decodificado completo en cada lectura; `package.json` de un `typescript-web` nuevo; dos avisos *low* de KaTeX.
  Piloto de receta Django limitado a macOS arm64/Python 3.13; el perfil Python/Django declarativo sigue pendiente
  de confirmar sobre un proyecto real. El piloto no evalúa comparativamente la calidad de modelos.
  Observaciones de P009: alta sin redirección, texto de marcadores de define-project y presentación de deriva
  tras cerrar; consolidación planificada en P010 y aplazamientos en ROADMAP.

## Fase activa

**P010 — Consolidación de la primera versión local. Planificada, sin implementación iniciada.**
El usuario acepta la propuesta el 2026-10-21 y solicita únicamente documentar la nueva fase
([D141](DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local),
[plan](phase/P010_PLAN_CONSOLIDACION.md), [tareas](NEXT_STEPS.md)). Diez tareas pendientes.
La petición actual autoriza solo esta planificación documental; no su ejecución.

P009 cerrada y archivada documentalmente el 2026-10-21
([resumen](archive/phase-009/SUMMARY.md), [revisión](archive/phase-009/REVIEW.md),
[D140](DECISIONS.md#d140--cierre-documental-manual-de-p009)). Sus veinte tareas y siete criterios de salida
están completos en el alcance acreditado. Originales conservados por bytes y referencias vigentes reubicadas.

El Django hijo conserva P001 CLOSED, cuatro tareas COMMITTED, tag `p001` sobre `47a0557` y archivo en `3d105c6`.
Última comprobación operativa en T012: servicios detenidos, cero locks y sin jobs pendientes; no se repite aquí.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; cierre manual sin check READY ni tag propio.

**Siguiente:** P010-T001, contrato de las correcciones y criterios de cierre, cuando se solicite ejecutar la fase.
Prioridades: arranque `typescript-web` con `package.json`, consultas acotadas de runs, marcadores de definición,
presentación de fases cerradas, documentación y evidencia de aceptación. Los límites actuales de la base acumulada
siguen vigentes hasta implementar y verificar cada entrega. La validación real complementaria se concreta en T008;
no se da por realizada ni autorizada. Sin nueva fase del Django hijo ni ampliación de consentimientos de P009.
