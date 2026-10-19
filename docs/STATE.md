# Estado — my_harness

Actualizado: 2026-10-19. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Codec de historial en formato 7 (lee 1–6).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0021_project_creation` (39 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams.
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-12`, `local-config-2/3/4`), revisor en solo lectura con esquema tipado, memoria automática desactivada,
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
  COMMITTED con fase cerrada (D050) y cuatro combinaciones revisor/ejecutor COMMITTED (D071).
- **Límites**: ningún recorrido de producto completo con CLI reales; contención cooperativa sin aislamiento del sistema
  operativo; validaciones sin hora; historial del run decodificado completo en cada lectura; `package.json` de un
  `typescript-web` nuevo; dos avisos *low* de KaTeX; perfil Python/Django pendiente de confirmar sobre un proyecto real.


## Fase activa — P009 Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

**Estado:** T001 (diseño) y T002 (carpeta/creación) completadas el 2026-10-19; T003–T012 pendientes, sin piloto.
Objetivo y criterios en [ROADMAP](ROADMAP.md#p009--proyecto-django-desde-cero-y-piloto-con-cuatro-combinaciones-de-agentes),
tareas en [NEXT_STEPS](NEXT_STEPS.md) y diseño en el [plan](phase/P009_PLAN_DJANGO.md).
Decisión: [D115](DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto).
Contrato de T001: [diseño implementable](phase/P009-T001_CONTRATO_CREACION.md),
[D116](DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada).

- Selección explícita en la UI de «Carpeta de proyectos»: concede al servicio la creación de nuevos proyectos
  hijos y queda guardada. La IA no propone ni descubre la ubicación. `$HOME/Documents/projects/` es
  el ejemplo del usuario, no un valor por defecto ni una autorización ejecutada en esta tarea.
- Pendiente de T004: receta Django confirmada tras la definición D088 existente: esqueleto,
  dependencias, entorno y validaciones. El piloto será una lista de tareas con SQLite y plantillas Django.
- Pendiente de T003: ajustes por proyecto para elegir proveedores y modelo/esfuerzo del revisor. El revisor elige modelo y
  esfuerzo del ejecutor. Cuatro tareas sucesivas en el mismo proyecto: Codex→Codex, Codex→Claude,
  Claude→Claude y Claude→Codex, siempre en orden revisor→ejecutor.
- T002 implementa selección/retirada UI persistente y auditada, creación exclusiva de hijos nuevos, registro
  atómico con procedencia y enlace a definición existente (D117). Preview/CAS/claves, fd sin enlaces, reservas
  y recuperación conservadora; no borra carpetas inciertas. Compatible con v3/v4 y roots TOML vacías.
  Los proveedores siguen globales y en consulta; presets, receta y operación Django permanecen pendientes.
- T001 separa el permiso UI para hijos nuevos del alta existente bajo raíces TOML; fija retirada y recuperación
  por intención/identidad. Diseña presets por proyecto en v5 y receta posterior al commit documental con enlaces
  diferidos al entorno, conservando protección de configuración e historiales. Esquema/API y fronteras documentados.

P008 permanece cerrada ([archivo](archive/phase-008/SUMMARY.md), D114). Este repositorio sigue sin registrarse
ni ejecutarse con el harness. T002 solo usa carpetas/SQLite temporales y QA con respuestas sintéticas;
sin carpetas reales del usuario ni proveedores.

**Siguiente:** P009-T003, configurar revisor y ejecutor por proyecto según D116.
Entrega de T002 y checks en [registro](phase/P009-T002_CARPETA_PROYECTOS.md). T006 preparará la
propuesta de operación real con las selecciones y límites pendientes; redactar la fase no autoriza invocar proveedores, instalar dependencias,
consumir red o ejecutar el piloto. Los consentimientos anteriores siguen agotados.
