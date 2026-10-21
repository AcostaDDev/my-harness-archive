# Estado — my_harness

Actualizado: 2026-10-21. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Codec de historial en formato 7 (lee 1–6).
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

**Estado:** T001–T005 completadas el 2026-10-19; T006 (propuesta autorizada, D121), T013 (CLI caracterizadas,
D122), T014 (definición Codex sin Git, D124), T016 (suite pytest rápida, D125) y T015 (wheel verificado con D088,
D126) el 2026-10-20. T007 detenida el 2026-10-20 (D123) y completada el 2026-10-21 (D127). T008 detenida el
2026-10-21 en la revisión (D128). Tras T017 (D129) y T018 (D130) se completó el mismo día: P001-T001 del hijo
COMMITTED (D131). T009 detenida el 2026-10-21 en el límite de revisiones (D132). T010–T012 pendientes.
Objetivo y criterios en [ROADMAP](ROADMAP.md#p009--proyecto-django-desde-cero-y-piloto-con-cuatro-combinaciones-de-agentes),
tareas en [NEXT_STEPS](NEXT_STEPS.md) y diseño en el [plan](phase/P009_PLAN_DJANGO.md).
Decisión: [D115](DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto).
Contrato de T001: [diseño implementable](phase/P009-T001_CONTRATO_CREACION.md),
[D116](DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada).

- T009 (Codex→Claude, run `bb29b133`): en Ajustes solo cambia el ejecutor, a Claude (registro v2). El revisor
  Codex elige `claude-sonnet-5-5`/`medium` con motivo, y la invocación coincide. Edición y borrado con 11 tests
  verdes, pero `ruff format --check` falla por una línea: el hijo usa 100 columnas y el ejecutor Claude, sin shell,
  formatea a mano con 88. Dos REVISE iguales y el run acaba en `revision_limit`. 6 de 7 invocaciones; piloto 15 de
  60. Cambios sin confirmar en el hijo. `serve` murió por SIGBUS a mitad del run (causa probable: lectores `sqlite3`
  externos sobre la SQLite viva). La recuperación del producto funcionó sin reencolar nada
  ([evidencia](phase/P009-T009_PILOTO_CODEX_CLAUDE.md), D132).
- T008 completada en la sesión 3: run `7fbaf89c` con Codex `gpt-6-luna`/`medium` en los tres roles. El contrato
  congela `core/**`, pasan las seis validaciones y el revisor da ACCEPT sin hallazgos. Commit `98f4611` confirmado por
  el usuario. Consumo de T008: 6 de 10. Observaciones sin bloqueo: el alta no redirige y el flujo `tasks.md` del
  hijo quedó reducido al alta y el listado
  ([evidencia §8](phase/P009-T008_PILOTO_CODEX_CODEX.md#8-reanudación-2026-10-21-sesión-3-committed), D131).
- T018: tras un reinicio, macOS renumeró `st_dev` del hijo y el recibo de preparación dejó de valer. La sesión 2
  de T008 se paró antes de encolar, sin consumo. `verify_receipt` compara ahora el inodo y sigue verificando todos los
  bytes; los recibos no se reescriben. Crear otro proyecto tras un reinicio sigue exigiendo volver a elegir la
  carpeta ([entrega](phase/P009-T018_RECIBO_TRAS_REINICIO.md), D130).
- T017 corrige la causa de D128: `task_contract` congela como `dir/**` toda entrada de `allowed_paths` o
  `forbidden_paths` terminada en `/`, y `plan-task` pide `dir/**`. Rutas exactas, globs, perfiles y contratos ya
  congelados no cambian, así que no hay versión nueva. Por decisión del usuario, `fc340afb` no se revalida y queda
  BLOCKED como evidencia ([entrega](phase/P009-T017_RUTAS_DIRECTORIO.md), D129).
- T008 (Codex→Codex, run `fc340afb`) planifica y ejecuta P001-T001 con `gpt-6-luna`/`medium` en los tres roles.
  El ejecutor usa la selección que el revisor eligió con motivo, y pasan las seis validaciones. El revisor bloquea
  porque `core/` en la allowlist no cubre sus archivos: `check_paths` usa `fnmatchcase` y `task_contract` acepta la
  barra final. Parada sin reintento ni commit, 3 de 7 invocaciones (6 de 60 del piloto). Cambios conservados en el
  hijo. Antes hubo que borrar el bytecode que el `runserver` de QA de T007 dejó en `.venv`, porque invalidaba el
  recibo de preparación ([evidencia](phase/P009-T008_PILOTO_CODEX_CODEX.md), D128).
- T007 crea desde la UI el Django `harness-django-pilot` con revisor Codex `gpt-6-luna`/`medium`: definición en
  dos turnos, commit raíz `9b612ca` con P001 y sus cuatro tareas, receta offline y commit técnico `d762e77`; la portada
  responde en loopback. 3 de 20 invocaciones. Hallazgos: la plantilla `define-project` no aclara que los marcadores
  son opcionales en una carpeta nueva, y el ROADMAP del revisor no traía tag (el usuario añadió `p001`)
  ([evidencia §7](phase/P009-T007_CREACION_DJANGO.md#7-reanudación-y-cierre-de-t007-2026-10-21), D127).
- T015 devuelve a `check_distribution.py` la verificación completa del wheel: el tramo v1 retirado pasa a ser la
  definición D088 con agentes sintéticos, aceptación, primera tarea, commit y reinicios. `serve` corre con `TMPDIR`
  propio (ARCHITECTURE §9) ([entrega](phase/P009-T015_VERIFICACION_WHEEL.md)).
- T016 reduce pytest de más de 25 minutos a unos 4:20: xdist por defecto (`-n 0` en serie), Git real en macOS,
  plantilla migrada, 16 combinaciones redundantes menos y adaptador Git con menos procesos y `posix_spawn`
  ([entrega](phase/P009-T016_SUITE_RAPIDA.md)).
- T014 corrige la parada de T007 con el adaptador `cli-13`: el revisor Codex recibe `--skip-git-repo-check` al
  redactar la definición D088 (plantilla congelada `define-project`) de una carpeta aún sin Git, con sandbox de
  lectura, memoria y confianza intactos. Jobs `cli-12` pendientes quedan en cuarentena; la CLI falsa rechaza ya como
  Codex fuera de Git. Una conversación con turno fallido admite otro ([entrega](phase/P009-T014_DEFINICION_SIN_GIT.md)).
- Selección explícita en la UI de «Carpeta de proyectos»: concede al servicio la creación de nuevos proyectos
  hijos y queda guardada. La IA no propone ni descubre la ubicación. `$HOME/Documents/projects/` es
  el ejemplo del usuario, no un valor por defecto ni una autorización ejecutada en esta tarea.
- T004 implementa receta Django confirmada tras la definición D088: esqueleto propio, lock con hashes,
  entorno aislado, checks y commit técnico conciliable (D119). T005 contrasta las herramientas reales en un hijo temporal
  con Python 3.13.13/uv 0.12.19 y wheels fijados, preparados con autorización específica (D120).
  El piloto será una lista de tareas con SQLite y plantillas Django.
- T003 implementa presets del servicio en `local-config-5`, selección por proyecto y modelo/esfuerzo explícitos
  del revisor (D118). El revisor elige modelo/esfuerzo del ejecutor. Cuatro tareas previstas en el mismo proyecto: Codex→Codex, Codex→Claude,
  Claude→Claude y Claude→Codex, siempre en orden revisor→ejecutor.
- T002 implementa selección/retirada UI persistente y auditada, creación exclusiva de hijos nuevos, registro
  atómico con procedencia y enlace a definición existente (D117). Preview/CAS/claves, fd sin enlaces, reservas
  y recuperación conservadora; no borra carpetas inciertas. Compatible con v3/v4 y roots TOML vacías.
  T003 añade agentes por checkout; T004 prepara el Django con journal/lease/lock propios. La operación real sigue pendiente.
- T001 separa el permiso UI para hijos nuevos del alta existente bajo raíces TOML; fija retirada y recuperación
  por intención/identidad. Diseña presets por proyecto en v5 y receta posterior al commit documental con enlaces
  diferidos al entorno, conservando protección de configuración e historiales. Esquema/API y fronteras documentados.

P008 permanece cerrada ([archivo](archive/phase-008/SUMMARY.md), D114). Este repositorio sigue sin registrarse
ni ejecutarse con el harness. T002–T005 usan carpetas/SQLite temporales y CLI de agentes falsas;
sin proyectos reales del usuario ni proveedores. T005 añade herramientas Django reales, sin modificar el runtime del harness.

**Siguiente:** P009-T019, para que un ejecutor sin shell cumpla el formato del perfil, y la decisión sobre `bb29b133`.
Después, reanudar T009 con autorización nueva del usuario: queda 1 de 7 invocaciones, y el piloto va por 15 de 60.
Área `~/.local/share/harness-local/` con el wheel de `d557082`. Hijo en `98f4611`, con los cambios de `bb29b133` sin
confirmar. Ajustes en el registro v2 (revisor Codex, ejecutor Claude). Durante la operación no se abre la SQLite
viva con otro proceso SQLite (propuesta §11). El usuario detiene `serve` al terminar la sesión. El QA de T012 lanza
`runserver` con `PYTHONDONTWRITEBYTECODE=1` (propuesta §9). Sigue pendiente aclarar en `define-project` que una
carpeta nueva no tiene marcadores (D127).
