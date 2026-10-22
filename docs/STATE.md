# Estado — my_harness

Actualizado: 2026-10-22. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P010 cerradas; primera versión local completada en el alcance de D151/D153.

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
  de confirmar sobre un proyecto real. A/B y ese perfil conservan su validación solo offline: el usuario aplaza
  la comprobación real complementaria en T008 (D151). El piloto no evalúa comparativamente la calidad de modelos.
  Observación de P009 pendiente: alta sin redirección (aplazada en ROADMAP). El texto de marcadores de
  define-project y la deriva tras cerrar están corregidos en P010-T004 (D146) y T005 (D147).

- **Primera versión local** ([P010](archive/phase-010/SUMMARY.md), D141–D153): doce tareas completadas,
  siete criterios de salida y trece criterios globales con dictamen en el alcance declarado. T009 verifica
  el wheel `0.1.0` con UI/migraciones fuera del checkout; pytest (1682 y 121 subtests), unittest (12), Node (82),
  tipos/build y Alembic temporal correctos, con dos opt-in omitidas. QA de escritorio con API sintética y doce
  capturas, sin integración navegador/backend adicional ni uso real nuevo. [Matriz](archive/phase-010/P010_MATRIZ_ACEPTACION.md),
  [revisión](archive/phase-010/REVIEW.md) y [paquete](archive/phase-010/P010-T009_VERIFICACION_FINAL.md).

## Fase activa

**P011 — Preparación para apertura pública en GitHub**, planificada el 2026-10-22 por encargo del usuario
([D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github),
[plan](phase/P011_PLAN_APERTURA_PUBLICA.md), [tareas](NEXT_STEPS.md)). Diecinueve tareas pendientes (ampliación D155);
esta entrega solo planifica, sin implementar traducción, selección de idiomas o nueva compatibilidad CLI.

**Planificación finalizada para comenzar su ejecución** por petición del usuario
([D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020)).
P011 no está completada: sus diecinueve tareas siguen pendientes y la siguiente es T001.
El modo continuo entre fases queda reservado para **v0.2.0, después de abrir el proyecto en GitHub**;
no forma parte de P011 ni modifica el cierre confirmado actual. El commit documental de planificación está autorizado.

Objetivo: código/comentarios/docstrings y prompts originales ingleses; interfaz y trabajo por proyecto en en/es;
CLI por capacidades/mínimos; diagramas contrastados con comportamiento; documentación inglesa y README de primer
uso; licencia/contenido publicable, paquete/CI y QA del candidato antes del dictamen. Sin publicar ni abrir
visibilidad por efecto de esta fase. Licencia/titularidad y versión candidata se resuelven en sus tareas.

[D155](DECISIONS.md#d155--p011-retirada-del-harness-anterior-y-dos-vías-de-alta) añade T019 antes de T003:
retirar visor/observación/importación legacy y normalización A, conservando solo creación desde cero e
incorporación de código existente sin harness (B). La retirada está planificada, no implementada; la base
acumulada sigue describiendo el código actual. Historiales propios y componentes compartidos por B se conservan.

**P010 cerrada y archivada documentalmente el 2026-10-22**
([D153](DECISIONS.md#d153--cierre-documental-de-p010-y-de-la-primera-versión-local),
[resumen](archive/phase-010/SUMMARY.md), [registro de cierre](archive/phase-010/P010_CIERRE.md)).
El dictamen favorable de T009 y la decisión explícita D151 permiten completar la primera versión local en ese
alcance. Originales de STATE/NEXT_STEPS y artefactos de fase conservados por bytes; sin tareas obligatorias pendientes.
El paquete sigue en `0.1.0`, sin tag ni publicación; P011 sucede ahora a ese cierre sin reescribirlo.

P009 conserva su cierre documental (D140) y el Django hijo su P001 CLOSED, cuatro tareas COMMITTED,
tag `p001` sobre `47a0557` y archivo en `3d105c6`. No se repite ninguna operación ni comprobación de su estado.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; cierre manual sin check READY ni tag propio.

**Siguiente:** P011-T001, inventario por archivo y contrato de idiomas/fuentes/setup antes de implementar.
Otras candidatas permanecen en [ROADMAP](ROADMAP.md#candidatas-sin-fase-asignada).
Los límites de la base acumulada siguen vigentes. B y D095 mantienen la validación real aplazada por D151;
A queda fuera del soporte público futuro por D155, sin considerarse validado ni retirado todavía en código.
Sin nueva fase del Django hijo ni ampliación de consentimientos.
