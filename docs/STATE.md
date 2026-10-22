# Estado — my_harness

Actualizado: 2026-10-22. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P009 cerradas.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Formateo del perfil tras cada turno del ejecutor (D133). Codec de historial
  en formato 8 (lee 1–7).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0023_run_projection` (48 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams. Proyección derivada `run-projection-1` escrita con el historial y comprobada en el backup
  (P010-T003, D144).
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
  Segunda receta `typescript-web-recipe-1` (P010-T002, D143): manifiesto inicial con `typescript@5.9.3`, `npm ci`
  desde la caché del operador y validaciones del perfil antes del commit técnico, para hijos TypeScript web nuevos.
- **Importación de proyectos** ([P008](archive/phase-008/SUMMARY.md)): inventarios deterministas,
  conversación de solo lectura y borradores privados; normalización de harness anterior (A) e incorporación
  desde código sin harness (B), con perfil confirmado, originales conservados y commit conciliable.
  Frontera Git A/B sin filtros, inspección de submódulos ni lazy-fetch; objetos necesarios locales,
  blobs por hash y destinos ignorados comprobados antes de escribir, también al recuperar.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación legacy en `/legacy`. Detalle, ciclos paginados, diff y casos JUnit de un run
  (D144), métricas y vista previa de exportación (D145) leen la proyección sin decodificar el historial.
- **Operación** ([P006](archive/phase-006/SUMMARY.md)): wheel con UI y migraciones, `init-db`, `serve`,
  `check-config`, `metrics-backfill`, `diagnose-cli`; `scripts/dev` para desarrollo. `migrate` actualiza bases
  existentes con instantánea previa `premigration-1` y declaración de parada (P010-T012, D150).
- **Evidencia con proveedores reales** (consentimientos agotados): transporte de las tres CLI (D025), primer uso real
  COMMITTED con fase cerrada (D050), cuatro combinaciones revisor/ejecutor COMMITTED (D071) y recorrido Django
  desde creación UI hasta cuatro tareas, QA conjunto y cierre/archivo de P001 (P009-T012, D139);
  26 invocaciones de 60 previstas, sin autorización para operaciones nuevas.
- **Límites**: contención cooperativa sin aislamiento del sistema operativo; validaciones sin hora; manifiestos de
  receta fijos tras preparar; dos avisos *low* de KaTeX.
  Piloto de receta Django limitado a macOS arm64/Python 3.13; el perfil Python/Django declarativo sigue pendiente
  de confirmar sobre un proyecto real. El piloto no evalúa comparativamente la calidad de modelos.
  Observación de P009 pendiente: alta sin redirección (aplazada en ROADMAP). El texto de marcadores de
  define-project y la deriva tras cerrar se corrigen en P010-T004 (D146) y T005 (D147).

## Fase activa

**P010 — Consolidación de la primera versión local. En curso: T001–T007 y T011–T012 completadas.**
Planificada el 2026-10-21 ([D141](DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local),
[plan](phase/P010_PLAN_CONSOLIDACION.md), [tareas](NEXT_STEPS.md)). El 2026-10-22 T001 deja el
[contrato](phase/P010-T001_CONTRATO_CONSOLIDACION.md) y la matriz inicial
([D142](DECISIONS.md#d142--p010-t001-receta-typescript-proyección-de-runs-y-tarea-t011)): receta
`typescript-web-recipe-1` en el marco D119, proyección derivada `run-projection-1` y una tarea nueva, T011
(métricas y exportación). El mismo día T002 implementa la receta
([entrega](phase/P010-T002_ARRANQUE_TYPESCRIPT.md), [D143](DECISIONS.md#d143--p010-t002-receta-typescript-web-recipe-1-implementada)):
un `typescript-web` nuevo llega a su primera tarea COMMITTED con las validaciones del perfil, verificado con
node/npm sintéticos y con node/npm reales sobre la caché local, offline. También el 2026-10-22, T003 implementa la
proyección `run-projection-1` ([entrega](phase/P010-T003_LECTURAS_RUNS.md),
[D144](DECISIONS.md#d144--p010-t003-proyección-run-projection-1-implementada)): migración `0023`, vistas de runs sin
decodificar el historial y ciclos paginados en la API, verificado con historiales sintéticos de los formatos 1–8 y uno
de 26 MiB. T011 lleva a la proyección las métricas y la vista previa de exportación
([entrega](phase/P010-T011_METRICAS_SIN_HISTORIAL.md),
[D145](DECISIONS.md#d145--p010-t011-métricas-y-vista-previa-de-exportación-sobre-la-proyección)); el envío
confirmado se sigue contrastando con el historial. Sin migración ni cambios de API; verificado con los formatos 1–8,
casos límite de validación y un ámbito sintético de 35,4 MiB. T004 aclara que los marcadores gestionados son
opcionales en la definición ([entrega](phase/P010-T004_MARCADORES_DEFINICION.md),
[D146](DECISIONS.md#d146--p010-t004-marcadores-opcionales-en-la-definición)): plantilla `define-project` y avisos de la
UI, sin cambios del motor; verificado con un recorrido sintético de carpeta nueva y con borradores, sin revisor real
ni QA visual. T005 presenta la evidencia histórica de una fase cerrada
([entrega](phase/P010-T005_FASES_CERRADAS.md),
[D147](DECISIONS.md#d147--p010-t005-evidencia-histórica-de-una-fase-cerrada)): `PhaseRead.closure` con check, base,
archivo y commit; la renovación del cierre deja de mostrarse como deriva y la deriva real (documentos vivos sin
sucesora y archivo alterado) se señala. Sin migración ni cambios del check; verificado con fases sintéticas abierta,
cerrada con y sin sucesora, abandonada y con deriva real. T006 contrasta README, ARCHITECTURE y ejemplos con el
código y la evidencia ([entrega](phase/P010-T006_DOCUMENTACION_VERSION.md),
[D148](DECISIONS.md#d148--p010-t006-documentación-de-instalación-y-alcance-soportado)): versiones CLI por rol,
alcance offline frente a real y límites. Por decisión del usuario, la falta de actualizador de bases en el paquete
instalado queda como límite y la valora T007. Sin cambios de código. T007 completa la
[matriz de aceptación](phase/P010_MATRIZ_ACEPTACION.md)
([D149](DECISIONS.md#d149--p010-t007-matriz-de-aceptación-sse-por-cursor-y-tarea-t012)): trece criterios cumplen
offline con tests reejecutados y dos nuevos; el usuario decide que el cursor de D029 cumple el criterio 13 en la UI
gestionada y que el hueco de migraciones del paquete instalado (§9) se corrige en la nueva T012. T012 implementa
`harness-local migrate` ([entrega](phase/P010-T012_MIGRACION_INSTALADA.md),
[D150](DECISIONS.md#d150--p010-t012-migración-explícita-de-bases-desde-la-cli-instalada)): copia previa verificada,
guardias de rutas, revisiones y propietarios/grupos vivos; no crea bases ni restaura automáticamente tras un fallo.
Verificado offline con SQLite sintética de `0022`, formatos 1–8 y revisiones antiguas; `serve` acepta el resultado
sin arrancar un servicio en la prueba. Sin esquema ni API nuevos; wheel pendiente de T009. T008–T010 pendientes.

P009 cerrada y archivada documentalmente el 2026-10-21
([resumen](archive/phase-009/SUMMARY.md), [revisión](archive/phase-009/REVIEW.md),
[D140](DECISIONS.md#d140--cierre-documental-manual-de-p009)). Sus veinte tareas y siete criterios de salida
están completos en el alcance acreditado. Originales conservados por bytes y referencias vigentes reubicadas.

El Django hijo conserva P001 CLOSED, cuatro tareas COMMITTED, tag `p001` sobre `47a0557` y archivo en `3d105c6`.
Última comprobación operativa en T012: servicios detenidos, cero locks y sin jobs pendientes; no se repite aquí.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; cierre manual sin check READY ni tag propio.

**Siguiente:** P010-T008, propuesta de validación real complementaria y alcance.
Después: verificación final del paquete (T009). Los límites actuales de la base
acumulada siguen vigentes hasta implementar y verificar
cada entrega; el SSE gestionado queda resuelto por D149. La validación real complementaria
se concreta en T008; no se da por realizada ni autorizada. Sin nueva fase del Django hijo ni ampliación de consentimientos de P009.
