# Especificación — Harness Local

Requisitos funcionales y reglas de negocio vigentes. Consolida la especificación inicial
([archivo](archive/phase-000/01-especificacion-harness-local.md)) con las decisiones posteriores y la ampliación
planificada de P009 (D115). La columna «Estado» de
cada requisito dice si está implementado (fase en la que se entregó) o pendiente; el detalle técnico está en
[ARCHITECTURE](ARCHITECTURE.md) y el avance, en [ROADMAP](ROADMAP.md) y [STATE](STATE.md).

## 1. Propósito y alcance

Aplicación local para configurar, ejecutar, observar y controlar un harness de desarrollo asistido por agentes, sobre
repositorios nuevos o existentes. Su objetivo es reducir el tiempo desde una idea hasta una versión verificable sin
perder control: el harness facilita decisiones y muestra evidencias; el usuario acepta requisitos, arquitectura,
permisos sensibles y resultados.

- Individual, local y orientada inicialmente a macOS. UI en el navegador; un servicio local accede a los repositorios
  y lanza las herramientas. Los modelos pueden requerir conexión: local no significa inferencia offline.
- Las suscripciones del usuario se usan a través de las CLI de Codex y Claude Code (D008); no se presupone acceso API.
- Fuera de alcance: multiusuario, nube, ejecución paralela de escritores sobre un mismo checkout, marketplace de
  plugins, editor visual de flujos, terminal web genérica y despliegue automático (ver §10).

## 2. Conceptos del dominio

| Concepto | Significado |
|---|---|
| Proyecto | Checkout Git registrado con su perfil, política, composición y contrato documental |
| Fase | Hito del ROADMAP (`PNNN`) con objetivo, criterios de salida y tareas; registro de SQLite |
| Tarea | Unidad acotada (`PNNN-TNNN`) con contrato congelado: objetivo, rutas, criterios y validaciones |
| Run | Seguimiento de una tarea u operación (check, cierre, transición, chat, definición, edición documental) |
| Intento | Una invocación concreta de un agente; nunca se sobrescribe |
| Revisión | Veredicto `ACCEPT`, `REVISE` o `BLOCKED` sobre una versión exacta del trabajo |
| Validación | Comandos del perfil y de la tarea, con reportes JUnit cuando existen |
| Permiso | Petición exacta por categoría (archivos, herramientas, red, producto, aceptación) y su resolución |
| PromptVersion | Plantilla inmutable, resuelta por ámbito y congelada en cada intento |
| Conversación | Chat del proyecto, definición de un proyecto nuevo o planificación de la fase siguiente |
| Documento gestionado | Markdown del contrato documental (§6); sus bloques gestionados son proyecciones de SQLite |
| Artefacto | Diff, stream, contrato, reporte o copia, referenciado por ruta y hash |

Relaciones: proyecto → fases → tareas → runs → intentos. Revisiones, validaciones, permisos y artefactos se ligan al
run y, cuando procede, al intento exacto.

## 3. Roles

- **Revisor** (Codex o Claude, elegido por el usuario): planifica tareas, revisa, evalúa fases, responde en el chat,
  conduce la definición y la planificación de fase. Siempre en solo lectura (D052).
- **Ejecutor** (Codex o Claude): único escritor del checkout. El revisor fija su modelo y esfuerzo por tarea, dentro
  de un catálogo o en modo libre según el proyecto.
- **Harness**: decide de forma determinista estados, puertas, commits, tags, archivado y bloques gestionados. Ningún
  agente cambia estados mecánicos ni hace commits.
- **Usuario**: acepta definición, planes, permisos, commits, cierres y ediciones documentales por su hash exacto.

## 4. Requisitos funcionales

| ID | Capacidad | Resultado observable | Estado |
|---|---|---|---|
| F01 | Registrar proyecto | Alta desde la UI con raíz canónica, confianza explícita, perfil y composición del TOML; o en `[[projects]]` del TOML | Implementado (P007, D078) |
| F02 | Crear proyecto desde cero | Brief, conversación con el revisor, borradores en disco con CAS, aceptación y commit raíz con P001 | Implementado (P007, D075, D082; P008-T002/T005, D092) |
| F03 | Importar un harness anterior (Flujo A) | Sin entrada operativa; datos anteriores conservados | Retirado en P011-T019 (D155, D161); implementación histórica P008 conservada en el archivo |
| F04 | Incorporar un repositorio sin harness (Flujo B) | Discovery por ingeniería inversa, documentos iniciales y archivos raíz mínimos | Inventario estático y propuesta de perfil implementados (P008-T013, D101); conversación de ingeniería inversa sobre HEAD con borradores privados (P008-T014, D102); vista previa, perfil y commit confirmados con P001 adoptada (P008-T015, D103) |
| F05 | Observar un harness anterior | Sin visor, API, CLI, SSE ni observadores; datos anteriores inertes | Retirado en P011-T019 (D155, D161) |
| F06 | Navegar proyectos, fases, tareas y runs | URL propia por recurso, carga limitada y paginada; `/runs/:id` independiente en copias de consulta | Implementado (P007, D077; P012-T012, D202) |
| F07 | Ejecutar una tarea | Planificación → ejecución → validación → revisión → aceptación o corrección → commit del harness | Implementado (P003) |
| F08 | Gestionar prompts | Versiones, diff, variables validadas, activación y rollback; snapshot por intento | Implementado (P004) |
| F09 | Resolver bloqueos y permisos | Motivo y evidencia; conceder o denegar una petición exacta; revalidar o reintentar | Implementado (P004) |
| F10 | Controlar fases | Check, reconciliación, preguntas, lote desatendido, enmienda, abandono, cierre con tag | Implementado (P004) |
| F11 | Cerrar y archivar una fase | Protocolo de §7 en un único flujo tras READY | Implementado (P008-T004/T006, D091, D093) |
| F12 | Ver y editar la documentación | Visor seguro y edición con diff confirmado y commit del harness | Implementado (P007, D080) |
| F13 | Conversar con el revisor | Chat sobre HEAD sin esperar al ejecutor; propuestas → tareas confirmadas; comandos deterministas | Implementado (P005, P007) |
| F14 | Inspeccionar tests | Suites y casos JUnit, OK/KO por tarea y evolución por fase | Implementado (P006, P007) |
| F15 | Métricas y estadísticas | Tokens, turnos, modelos, esfuerzos, duraciones y coste equivalente con procedencia | Implementado (P007, D074, D084) |
| F16 | Recuperar y conservar | Backup y restauración de consulta, UI de evidencia por id sin checkout, retención explícita de logs, recuperación tras caída | Implementado (P003, P006; P012-T012, D202) |
| F17 | Distribución local | Wheel con UI y migraciones, `init-db`, `serve`, sesión local | Implementado (P006) |
| F18 | Perfiles declarativos | Perfil de stack (preparación, tests, lint, tipos) declarado en el TOML local y confirmado por el usuario, incluido Python/Django (`pytest`, `ruff`, `mypy`) | Implementado (P008-T008, D095); ejemplo Python/Django pendiente de confirmación sobre el proyecto del usuario |
| F19 | Instrucciones del proyecto para los agentes | `AGENTS.md` incluido en el contexto congelado de cada intento | Implementada (P008-T007, D094) |
| F20 | Elegir carpeta de proyectos | Raíz elegida explícitamente en UI y persistida; concede al servicio crear nuevos hijos sin que la IA decida su ubicación | Implementado (P009-T002, D117); carpeta elegida y creación real en T007, piloto cerrado en T012 (D139) |
| F21 | Agentes configurables por proyecto | Elegir proveedores y modelo/esfuerzo del revisor en UI; selección concreta del ejecutor a cargo del revisor | Implementado (P009-T003, D118): presets v5, selección por checkout y cambios confirmados entre tareas |
| F22 | Preparar Django desde cero | Hijo nuevo, documentos D088, scaffold, entorno/dependencias y validaciones mediante receta confirmada | Implementado (P009-T004, D119); ensayo real T005 (D120) y piloto T007–T012 con P001 cerrada/archivada (D139) |
| F23 | Idioma visual y de trabajo | Defaults globales en/es: visual global mutable para UI/conversación y trabajo inmutable por proyecto para documentación/código, con ambos congelados por job/turno | Parcial (P011, D158; §13): preferencias globales y visual congelado por job (T007, D166); trabajo inmutable por proyecto y par por job/intento (T008, D167); recetas v2 preparadas con el idioma de trabajo (T020, D168); directiva tipada al agente y documentos generados en el idioma de trabajo (T009, D169). Traducción completa de UI/mensajes (T010) pendiente |
| F24 | Compatibilidad CLI ampliable | Detección automática sin pin; mínimos/capacidades por proveedor/rol, diagnóstico y versiones verificadas/candidatas sin allowlist por patch | Implementado P011-T012/D174: `local-config-7`/`cli-14`, mínimos Codex 0.163.0 / Claude 2.1.304; posteriores con compatibilidad condicionada, evidencia nueva solo sintética (§13) |

Modo de proyecto: **gestionado**. Solo se crean proyectos nuevos o se incorpora código sin harness (B);
registrar/reabrir uno ya gestionado conserva su autoridad. Nunca escriben dos motores sobre el mismo checkout.

Las copias marcadas D040 ofrecen [consulta UI](flows/backup-consultation.md) por id, con evidencia, diff,
JUnit, jobs/intentos/eventos y métricas por run. Conservan estados históricos sin sondeo de ejecución, acciones,
recuperación o configuración; no leen checkouts ni montan el workspace operativo. Sin marca se conserva la
resolución canónica habitual, incluso si faltan agentes o el supervisor está desactivado. Verificación sintética
P012-T012; [consulta UI real de T003](archive/phase-012/P012-T003_UI_RESULTADO_T012.md) acreditada en Chrome/macOS con
el wheel T012 y salvedad autorizada de identidad histórica del host (D204), sin certificar muerte de escritores.

## 5. Reglas de negocio

1. Una sola ejecución escritora por checkout; los turnos de chat leen una instantánea de HEAD sin tomar el lock.
2. Contrato, contexto, prompts, políticas, perfil y versiones se congelan por intento; cada intento es una sesión nueva.
   Reanudar trabajo no reanuda una conversación.
3. Revisión, validación y aceptación se ligan al contenido exacto (base, árbol, diff, índice). Un cambio posterior
   invalida la evidencia antes del commit; el commit contiene solo lo revisado más actualizaciones mecánicas declaradas.
4. Sin fallback de modelo, reintento ni consumo adicional silencioso. Un error de autenticación, cuota o entorno detiene.
5. Se distinguen datos solicitados, reportados, derivados, medidos y ausentes; null no es cero; no se suman acumulados
   con incrementales ni se deduce cuota.
6. Cinco decisiones separadas: alcance de archivos, herramientas, red, cambios de producto o arquitectura y aceptación.
   Una concesión no amplía otra ni la conceden los prompts.
7. Intención persistida antes de cada efecto externo y conciliación tras una caída. Un lease vencido no prueba la
   muerte del proceso: liberar exige confirmar el escritor detenido.
8. Toda escritura documental del harness (edición, exportación, creación, transición, importación) se confirma por el
   hash de su vista previa y nunca sobrescribe bytes ajenos (CAS).
9. Una fase cierra solo con check READY vigente y autorización propia; el lote desatendido nunca comprueba ni cierra.
10. Servicio solo en loopback, con sesión local, Host/Origin exacto y CSRF; Markdown y logs sin HTML ejecutable.
11. Los perfiles declaran comandos y rutas; un prefijo permitido no es una frontera de seguridad. La contención es
    cooperativa: no hay aislamiento del sistema operativo.

## 6. Contrato documental de los proyectos gestionados

Estructura obligatoria para todo proyecto, también para este repositorio (D088). Implementados (P008-T002, D089): el
layout, la plantilla, el índice de DECISIONS desde sus encabezados y la obligatoriedad (sin `documents`, el proyecto usa
esta estructura; la creación v1 se rechaza). P008-T003 (D090): rutas del ejecutor, paridad de modelos determinista y
de flujos por el revisor, y propuestas de ADR. P008-T004 (D091): cierre y archivo unificados y plan posterior
confirmado. P008-T005 (D092): prompts y definición alineados; once documentos obligatorios al aceptar, con
instrucciones y DDBB-DIAGRAM por plantilla si no hay borrador (D089). P008-T006 (D093): API y UI con índice de
decisiones único, instrucciones/diagramas/flujos/trabajo de fase, cierre unificado y planificación posterior; retirados los endpoints de creación v1 y transición. P008-T007
(D094): `AGENTS.md` con su hash en el prompt de todos los roles salvo la definición, que lo redacta.

| Ruta | Contenido | Autoría |
|---|---|---|
| `AGENTS.md` | Fuente canónica para agentes (≤60 líneas): orden de discovery, reglas inquebrantables, comandos base de test y lint | Creación, importación y usuario |
| `CLAUDE.md`, `GEMINI.md` | Envoltorios (≤15 líneas) que importan `AGENTS.md` | Creación, importación y usuario |
| `README.md` | Para personas: qué es, instalación, uso, tests, mapa de documentación | Tareas, reconciliación y usuario |
| `docs/SPECIFICATION.md` | Requisitos funcionales y reglas de negocio | Creación, tareas autorizadas y usuario |
| `docs/ARCHITECTURE.md` | Stack, patrones, módulos y convenciones | Creación, tareas autorizadas y usuario |
| `docs/ROADMAP.md` | Fases `## PNNN — título` con objetivo y criterios de salida; estado y enlace al archivo de las cerradas | Creación, planificación, usuario; estado por el harness |
| `docs/STATE.md` | Fotografía de la fase en curso: base acumulada (≤12 KiB) y fase activa (total ≤24 KiB) | Harness, reconciliación y usuario |
| `docs/NEXT_STEPS.md` | Tareas `## PNNN-TNNN — título` de la fase activa (≤48 KiB) | Planificación de fase y usuario |
| `docs/DECISIONS.md` | Registro único de ADRs `## DNNN — título`, con índice | Reconciliación, revisor (propuestas aprobadas) y usuario |
| `docs/DDBB-DIAGRAM.md` | Esquema entidad-relación en Mermaid `erDiagram`, o «Sin persistencia» | Ejecutor (paridad) y usuario |
| `docs/flows/*.md` | Diagramas Mermaid por módulo o feature (`stateDiagram-v2`, `sequenceDiagram`, `flowchart`) | Ejecutor (paridad) y usuario |
| `docs/phase/` | Artefactos de trabajo de la fase en curso | Ejecutor y usuario |
| `docs/archive/phase-NNN/` | Fase cerrada: STATE, NEXT_STEPS, REVIEW, SUMMARY y lo que hubiera en `docs/phase/` | Solo el harness |

Reglas:

- **Discovery.** Al empezar una sesión se lee `AGENTS.md`, después STATE, NEXT_STEPS, la sección de la fase activa de
  ROADMAP y lo pertinente de SPECIFICATION y ARCHITECTURE. De DECISIONS solo las ADR citadas por la tarea, o el índice
  para buscar precedentes. `DDBB-DIAGRAM.md` y `flows/` cuando la tarea toque datos o flujos. El archivo solo si se cita.
- **Sin invención.** Nada fuera de la especificación; ante una incongruencia entre documentos o con el código, se
  pregunta antes de decidir.
- **Paridad diagramas‑código.** Un cambio de modelos de datos o de flujos de negocio actualiza `DDBB-DIAGRAM.md` o
  `docs/flows/` en la misma tarea; el revisor rechaza la entrega que no lo haga. Si el perfil declara
  `data_model_paths`, un diff que los toque sin el diagrama de datos no se acepta aunque el revisor acepte.
- **Decisiones.** El ejecutor no añade ADR: las propone en su salida y el revisor o la reconciliación las consolidan.
- **Protegidos.** STATE, NEXT_STEPS, ROADMAP, DECISIONS, `docs/archive/**`, AGENTS, CLAUDE y GEMINI quedan fuera de
  los contratos de ejecutor; la reconciliación edita la prosa de STATE, NEXT_STEPS, ROADMAP y DECISIONS.
- **Bloques gestionados.** Los bloques entre comentarios `harness-local:managed-*` los escribe solo el harness; la
  prosa exterior se conserva. Superar un presupuesto genera un aviso y una reconciliación, nunca un truncado.

## 7. Cierre de fase

Al superar el check READY y autorizar el cierre, en un único flujo determinista (implementado: P008-T004, D091):

1. Tag sobre el HEAD evaluado (D032).
2. `docs/archive/phase-NNN/` con la instantánea final de STATE y NEXT_STEPS, REVIEW y SUMMARY generados desde SQLite y
   todo el contenido de `docs/phase/`.
3. STATE reiniciado con la base acumulada compacta y la fase activa N+1; NEXT_STEPS con el objetivo de N+1 tomado de
   ROADMAP y sin tareas hasta su planificación; `docs/phase/` vacía.
4. ROADMAP marca N como completada con enlace a `archive/phase-NNN/`.

Todo en un commit conciliable; si algo no cuadra (checkout sucio, documentos distintos de su base, archivo existente,
trabajo pendiente), se rechaza antes de escribir. Si ROADMAP no tiene más fases, solo se archiva. El abandono usa
el mismo archivo conciliable sin READY ni tag. Un check devuelve NEEDS_RECONCILIATION si STATE supera 24 KiB o
su base acumulada supera 12 KiB. El plan posterior de N+1 se confirma por hash: escribe NEXT_STEPS, regenera los
bloques de estado y crea una nueva versión de su definición, conservando la anterior (D034).

## 8. Incorporación de proyectos existentes

El producto tiene dos accesos: crear desde cero (F02) e incorporar código existente sin harness (F04, Flujo B).
Registrar o reabrir un proyecto ya gestionado sigue siendo una operación normal sobre su autoridad existente.
Un repositorio con documentos/historia de otro harness se rechaza; no se convierte silenciosamente en B.

B inventaría el HEAD no vacío (stack, entidades, rutas, tests y CI) y propone un perfil declarativo que el operador
confirma en su composición. El revisor consulta una exportación de solo lectura del HEAD congelado y propone
los once documentos D088 y flujos, citando hechos y decisiones inferidas. Pregunta lo no deducible. Sus propuestas
se aplican con CAS en borradores privados junto a SQLite, sin escribir el checkout ni ejecutar código/comandos.

La vista previa exige los documentos, P001 y sus criterios, preguntas bloqueantes resueltas o aplazadas y un
checkout/índice limpios sobre el HEAD original. Confirma documentos y perfil por hash, motivo e Idempotency-Key;
conserva inventario, resumen y originales sustituidos por bytes en `archive/phase-000/`. Sella una intención
antes de escribir y crea un único commit documental conciliable, con P001 ACTIVE adoptada atómicamente.
Repetir la confirmación no duplica operaciones; una caída exige confirmar el escritor detenido y reconfirmar
la intención exacta. No escribe el TOML ni instala o ejecuta herramientas del proyecto.

La frontera Git conserva las guardias D105/D108/D110/D112: objetos completos locales y `--no-lazy-fetch` desde
el primer comando, filtros clean/process e incluye rechazados antes de capturar/sellar, gitlinks de HEAD/índice
rechazados antes de consultar hijos, destinos ignorados y blobs por hash contrastados. Recuperar repite las
mismas guardias sin modificar la intención. [Flujo vigente](flows/project-onboarding.md).

La observación/importación del harness anterior y su activación/reversión están retiradas (D161). Las antiguas
rutas API devuelven 404 tras las guardias de acceso y los comandos fallan al validar argumentos, sin abrir datos.
Tablas, revisiones, historiales, snapshots y archivos del usuario permanecen intactos. Jobs A o ambiguos quedan
en cuarentena antes de cualquier invocación/escritura; la recuperación explícita cierra el job y libera el lock
solo tras comprobar propietarios, sin ejecutar su intención. Activaciones PREPARING/REVERTING bloquean para
resolución manual fuera del flujo retirado; ACTIVE solo autoriza trabajo gestionado con guardia de integridad.
Backup lee referencias selladas y restaura solo para consulta, sin observar orígenes ni reanudar tareas retiradas.
[Compatibilidad de instalaciones anteriores](flows/legacy-migration.md).

## 9. Requisitos no funcionales

P012-T010 (D194) habilita explícitamente el formateador del perfil declarado en `local-config-8`: campos
`formatter_argv` y `formatter_paths` juntos y no vacíos, argv sin shell terminado en `--`, patrones relativos
sin duplicados, ejecutable mapeado y `authorize_profile_commands = true`. El motor usa la frontera D133
antes de validar/revisar, solo sobre archivos existentes cambiados que el contrato permite. Aceptación y
commit se vinculan a esos bytes formateados; revalidar no formatea. Omitir ambos campos mantiene el flujo
anterior. V1–v7 conservan su contrato y rechazan las claves declarativas nuevas; los historiales no se adoptan
bajo otra composición. [Evidencia offline](archive/phase-012/P012-T010_FORMATEADOR_DECLARATIVO.md), sin uso real nuevo.

- Navegar datos registrados no invoca modelos ni necesita red. El frontend no accede al disco ni lanza comandos.
- Listados, logs y diffs paginados con límites explícitos; nada lee un historial completo para pintar una vista.
- Instalación reproducible con lockfiles y versiones exactas; distribución como wheel con assets y migraciones; Node
  solo para construir la UI.
- Logs con retención explícita que conserva contratos, permisos, veredictos y métricas.
- Backup consistente de SQLite y artefactos verificados por hash; restauración en directorio nuevo y solo de consulta.
- Migraciones explícitas con backup previo; las CLI inferiores al mínimo o con capacidades incompatibles se bloquean
  con diagnóstico. Las posteriores que cumplen el contrato conocido se admiten con compatibilidad condicionada (D174).
- El historial es trazable a nivel de aplicación, no un registro inviolable frente al propietario del equipo.

## 10. Criterios de aceptación globales

1. Repetir el alta desde cero o la incorporación B y sus confirmaciones no duplica proyectos, fases, jobs ni commits; no inventa datos ausentes.
2. Una tarea recorre ejecución, fallo de test, corrección, revisión y commit con historial completo.
3. Dos peticiones simultáneas no crean dos escritores sobre el mismo checkout; un reinicio con proceso vivo tampoco.
4. Una denegación no ejecuta la herramienta; una aprobación caducada o doble no se reutiliza.
5. Reiniciar el servicio durante una ejecución conserva evidencias y no repite efectos a ciegas; una caída tras el commit
   lo concilia.
6. Editar prompts no cambia la versión registrada en un intento pasado.
7. Un cambio posterior al diff revisado invalida la aceptación antes del commit.
8. El cierre de fase exige validación y autorización vigentes, y archiva la fase sin perder bytes (§7).
9. Un perfil de stack distinto funciona sin cambios en el núcleo.
10. Una petición del chat termina vinculada a una tarea y a su resultado.
11. Crear un proyecto vacío produce documentos, estructura y primera tarea ejecutable; incorporar código sin harness
    adopta P001 y el contrato documental conservando código y originales. Ambos continúan como gestionados.
12. Backup y restauración recuperan estados, referencias y evidencias verificadas por hash.
13. Respuesta de agente fuera de esquema: run detenido con diagnóstico y salida conservada. Ciclos sin cambios: parada
    con motivo. La observación de runs gestionados reanuda el cursor de eventos sin huecos ni duplicados.

Métricas de producto desde el primer piloto: tiempo de configuración, tiempo hasta la primera tarea aceptada,
intervenciones manuales, errores recuperados, consumo por tarea incluidos los fallos y correcciones tras aceptar. Una
mejora de velocidad sin calidad equivalente no demuestra un menor time to market.

## 11. Fuera de alcance

Multiusuario, nube, ejecución paralela de escritores en un proyecto, App Server o Agent SDK hasta verificar
compatibilidad y autenticación, `project.yaml` portable, edición del TOML desde la UI, aislamiento físico del sistema
operativo y publicación del paquete. Cualquier uso real de proveedores requiere una propuesta y un consentimiento
específicos del usuario.

## 12. Ampliación planificada — P009

D115 añade F20–F22 para un piloto Django desde cero. T002 implementa F20 y la creación/registro del hijo;
T003 implementa F21 con presets v5 y T004 implementa F22 mediante receta confirmada (D119). La persona elige la
carpeta de proyectos y el nombre del hijo desde la UI; la IA no descubre ni propone dónde crear el checkout.
La elección guardada concede al servicio crear hijos en esa raíz, sin repetir ese permiso por proyecto;
no entrega la carpeta padre a los agentes ni amplía confianza en repositorios existentes. No se sobrescribe
un destino existente ni se modifican permisos del sistema operativo.

La receta Django prepara scaffold, entorno y dependencias mediante un plan confirmado y recuperable, después
del bootstrap documental. Red/instalación y creación de archivos protegidos tienen alcance propio; no se
desprotegen para tareas normales. La UI no edita el TOML, ejecutables, credenciales o configuración global.

Los roles se configuran por proyecto desde presets del servicio en `local-config-5` (D118; también v6). El usuario fija proveedor/modelo/
esfuerzo del revisor y proveedor/catálogo del ejecutor; el revisor decide modelo/esfuerzo concretos del ejecutor.
El piloto usa planificación por agente y cuatro tareas del mismo Django: Codex→Codex, Codex→Claude,
Claude→Claude y Claude→Codex (revisor→ejecutor), con intentos previos conservados tras cada cambio.
Plan, alcance y puerta de operación real en el [plan archivado](archive/phase-009/NEXT_STEPS.md) y el
[diseño de P009](archive/phase-009/P009_PLAN_DJANGO.md).
Contrato de diseño completado en T001: [D116](DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada)
y [detalle](archive/phase-009/P009-T001_CONTRATO_CREACION.md). La autoridad UI para hijos nuevos se separa del registro
existente bajo raíces TOML; retirar el padre no revoca proyectos ya registrados. Presets y receta se diseñan
como v5 optativa, conservando formatos previos. La preparación posterior al commit documental habilita los
ejecutables del entorno; antes se bloquean tareas y checks que los necesitan. La carpeta y el alta del hijo están
implementadas en T002 (D117); los presets en T003 (D118). Receta implementada en T004 (D119); T005 acredita
herramientas reales y ensayo temporal completo (D120). T007–T012 acreditan el piloto real: cuatro tareas COMMITTED
con las cuatro parejas, QA conjunto y P001 cerrada/archivada (D139). P009 del harness se cierra y archiva
documentalmente en una tarea posterior (D140), con [revisión y límites](archive/phase-009/REVIEW.md).

## 13. Ampliación planificada — P011

[D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github) encarga preparar el repositorio/paquete
para apertura pública en GitHub. Los objetivos pendientes de esta sección siguen **planificados, no implementados**;
F24 está implementado por T012/D174, además de lo indicado en F23 (preferencias T007, idioma de trabajo T008/T020
y directiva/documentos T009) y las
retiradas/traducciones de T019/T003–T006;
no cambian el alcance entregado de P010 ni sus límites D151/D153.

- Inglés como base del código mantenido, comentarios/docstrings/descripciones y prompts originales; inventario
  por archivo y revisión de identificadores españoles internos. Conservar protocolos y originales históricos,
  fuentes ligadas a huellas/recibos con tratamiento compatible y excepciones de fixtures bilingües justificadas.
- Defaults globales `ui_language` y `default_work_language` en/es, inicialmente en; visual mutable y global para
  UI, mensajes, conversación/respuestas humanas y preguntas HITL, nunca un ajuste de proyecto. Trabajo elegido
  al crear/incorporar, inmutable y persistido por proyecto para documentación/código. Defaults nuevos solo rigen altas.
- Congelar el par efectivo por job/turno y sus intentos. Cambiar visual afecta nuevas interacciones, sin mutar
  llamadas activas, jobs pendientes/reintentos, textos históricos o aceptaciones. Fuentes existentes en otros
  idiomas siguen legibles, sin traducción forzada ni cambios de interfaces/keywords/rutas por el locale.
- Prompts originales ingleses, con personalización preservada. T001 concreta i18n React/Python, configuración,
  precedencias, persistencia, migraciones, fallback y snapshots antes de implementarlos; los parsers siguen
  admitiendo documentos en/es sin cambiar rutas canónicas, marcadores, comandos o códigos de estado.
- Política CLI ampliable por mínimos/capacidades y rol, con procedencia verificada/candidata y diagnóstico;
  versión posterior compatible no rechazada solo por una lista exacta. Permisos, confianza, memoria y recuperación
  se mantienen; una guardia esencial no acreditada bloquea. No prometer todas las versiones futuras.
  T011/D173 concreta por HITL la detección automática de cliente/versión, sin pedir pin, aceptación de candidatas
  o evidencia al usuario. Mínimos nuevos comunes: Codex 0.163.0 / Claude 2.1.304; inferiores → actualizar,
  historia/configuraciones anteriores legibles. T012/D174 implementa v7/cli-14: perfil/política y cliente observados
  congelados, revalidación por intento y antes de GO. HITL adicional: compatibilidad condicionada de las posteriores
  con las guardias conocidas intactas, sin afirmar efectos internos verificados. Sin uso real nuevo.
- Paridad semántica diagramas/código/tests, documentación pública inglesa con entrada española y README completo,
  licencia/contenido publicable, metadatos/CI y ensayo del paquete final desde clon sin cachés privadas.

[D155](DECISIONS.md#d155--p011-retirada-del-harness-anterior-y-dos-vías-de-alta) amplía P011 con T019: retirar
observación/visor/importación del harness anterior, su activación y normalización A. El producto público tendrá
solo dos vías de alta: crear desde cero e incorporar un repositorio existente sin harness (B); después ambos
se siguen como gestionados. Reabrir/registrar proyectos ya gestionados no añade una tercera modalidad.
Retirados en T019: UI, API, CLI, observadores/SSE legacy, prompts y componentes exclusivos; no se elimina por su nombre
infraestructura compartida necesaria para B ni lectura de historiales propios de my_harness.

T019 implementa la retirada (D161) y actualiza F03/F05, §8 y criterios 1/11/13 para idempotencia cero/B y
observación gestionada por cursor. Las matrices históricas P010 permanecen intactas. D151 sigue aplazando B/D095; A sale del alcance futuro, sin acreditarse por ello.
No se destruyen datos históricos, revisiones/migraciones o backups automáticamente para retirar funcionalidades.

Los diez criterios de [P011 en ROADMAP](ROADMAP.md#p011--preparación-para-apertura-pública-en-github) y los trece
globales ajustados por la retirada se dictaminan antes de cerrar. Licencia/titularidad y versión candidata se
deciden en sus tareas; no se presuponen. Se prepara expediente de apertura, manteniendo fuera de esta entrega la publicación
remota/PyPI, cambio de visibilidad, tag/push/commit y operación del harness sobre este repositorio.
Caracterización/inferencia real y ensayos operativos conservan sus autorizaciones propias; D151 sigue vigente.
Detalle en [plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md) y [tareas](archive/phase-011/NEXT_STEPS.md).

[D157](DECISIONS.md#d157--repositorio-público-nuevo-y-continuidad-del-desarrollo) prevé una instantánea pública
inicial revisada, con historia Git y documentación de partida nuevas, sin exportar las ADR/fases/historia privadas.
Después de abrir, repositorio público como fuente principal de código, nuevas decisiones y fases, con contexto
útil para usuarios/forks/agentes; este checkout conserva su historia privada. No se congelará la documentación
pública entre versiones ni se mantendrán dos fuentes activas sobrescribiéndose.

[D158](DECISIONS.md#d158--idioma-visual-global-y-trabajo-inmutable-por-proyecto) sustituye el idioma mutable por
proyecto propuesto en D154: trabajo fijo al alta, visual global para conversación y defaults globales. Una misma
respuesta puede llevar explicación española y borradores/código ingleses; el contrato mapeará los campos humanos
y técnicos con directivas tipadas, usando el canal de instrucciones soportado por ambos proveedores. Prompts
originales ingleses, contenido técnico público de my_harness en inglés y lengua humana elegible; no implica
traducir toda entrada/archivo ni garantizar un ahorro fijo de tokens. Todo sigue planificado, no implementado.

[D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020) finaliza esta
planificación y aplaza el modo continuo entre fases a v0.2.0 después de la apertura inicial en GitHub, fuera de P011.
La cadena futura incluiría tareas/commits, check, cierre/archivo, planificación y ejecución de la siguiente fase,
con autorización inicial y parada por error/HITL/límites. No está implementada ni cambia las reglas vigentes
§5.9/§7: el lote no comprueba/cierra, el cierre se autoriza sobre READY y el plan posterior se confirma por hash.


## 14. Ampliación planificada — P013

[D215](DECISIONS.md#d215--p013-instalación-guiada-y-configuración-desde-la-ui) abre P013 antes de publicar.
**T001 completa el diseño; T002–T011 implementan instalación/arranque/empaquetado, persistencia, asistentes, perfil, preparación, edición y compatibilidad/backup; T012 verifica primer uso/QA sintéticos; T013 cualifica candidato/paquete exactos; T014 emite dictamen favorable. Cierre pendiente T015.**
Las reglas vigentes de §4/§5/§8 se mantienen hasta sus entregas. [Contrato](phase/P013-T001_CONTRATO.md), [flujo](flows/configuration-setup.md),
[plan](phase/P013_PLAN.md) y [tareas](NEXT_STEPS.md). D216–D218 concretan:

- Instalador T002 entregado ([D219](DECISIONS.md#d219--p013-t002-instalador-por-generaciones-y-paquete-autocontenido),
  [validación sintética](phase/P013-T002_INSTALACION.md)): clon o paquete verificado, con venv/generaciones
  aisladas y rutas/cachés elegibles. Offline por defecto y red explícita, sin instalar herramientas globales;
  paquete sin Node/checkout. Arranque corto T003 entregado ([validación sintética](phase/P013-T003_ARRANQUE.md),
  D220): inicializa solo base ausente; migración de existente por D150 aparte, con parada y copia previa.
  Sin TOML o con archivo inválido habilita el asistente API protegido de T005 y UI de T006.
- Asistente inicial autenticado sin TOML completo, composición ni modelos. Detectar clientes no otorga permisos;
  preflight explícito D174 no acredita inferencia real. Configuración inválida/ausente no consume trabajos.
  Consulta restaurada nunca habilita este asistente operativo. T006 entrega `/setup` y
  `/settings/configuration`, formularios y TOML con campos avanzados conservados, errores por campo en/es,
  diff y confirmaciones exactas separadas. Candidato y solicitud idempotente permanecen en la pestaña ante
  conflicto/recarga; reenvío solo explícito. Activar no reinicia desde HTTP; cancelar no recarga configuración.
  [Entrega y límites](phase/P013-T006_ASISTENTE_UI.md), D223; QA visual Chrome integrada verificada en T012, con sus límites.
- Global v9 y perfil/composición propios por proyecto v1, privados fuera de checkouts. Contenido en TOML
  versionado y activación por referencia/hash en SQLite. Guardar es distinto de activar; diff, CAS, intención
  recuperable y confirmación exacta. Edición externa no recarga autoridad ni cambia contratos congelados.
  Primitivas T004 implementadas ([entrega](phase/P013-T004_CONFIGURACION.md), D221); API y arranque global
  T005 entregados ([contrato efectivo y checks](phase/P013-T005_ASISTENTE_API.md), D222). T007 entrega registro
  documental sin perfil y propuestas; T008 entrega preparación genérica; alta/activación integradas entregadas en T009;
  legacy se importa expresamente en T011.
  T011 entrega el backup formato 2 con TOML/versiones/intenciones e inventario verificable; formato 1
  sin configuración nueva sigue consultable.
- Global requiere reinicio confirmado; proyecto puede activarse entre tareas sin reinicio. Trabajo pendiente
  bloquea activar según D118; no se cancelan jobs ni reescriben historiales/recibos para aplicar cambios.
  Impacto global y proyectos afectados visible; preferencias/idioma de trabajo conservan D166/D167.
- Crear/incorporar conversa con contexto documental/inventario antes de exigir perfil. Revisor propone;
  confirmar documentos y perfil compatible precede al commit documental raíz/B y adopción P001. Preparación
  técnica separada después, con plan de archivos/comandos/dependencias/red/ámbito y recibo; activar perfil
  confirmado habilita primera tarea. P001 ACTIVE por sí sola no abre esa puerta.
  T007 implementa contexto de alta sin perfil ejecutable, propuesta estructurada con herramientas diferidas y
  evidencia por comando; preview/confirmación adoptan borrador, sin TOML ni comandos. Registro v9 de raíz
  existente confiada; `PROFILE_REQUIRED`/`PROFILE_PROPOSED` no habilitan tareas. HEAD/documentos/preguntas/
  contexto obsoletos bloquean confirmar. [Entrega](phase/P013-T007_PROPUESTA_PERFIL.md), D224. Commit
  documental, creación de carpeta propia y activación integrados entregados en T009; preparación genérica entregada en T008.
- Ejemplos/recetas Django/TypeScript opcionales. Preparación genérica con ejecutor acotado y validaciones
  significativas del harness; agentes sin escritura general de TOML global ni ajustes del equipo. Aplicación
  guarda versiones validadas. Perfil propuesto no acredita entorno listo ni permite ejecutar código al inventariar.
  T008 entrega plan técnico separado del revisor y confirmación exacta de configuración, herramientas, archivos,
  dependencias/red/scripts, selección del ejecutor y argv/límites. Primitivas/API con journal/locks/leases,
  cancelación y recuperación enlazada, JUnit fresco, commit técnico conciliable y recibo propio. Sin activación
  por efecto de preparar; T009 entrega el handoff de commit documental/TOML y el alta/UI. Contención nativa
  cooperativa, sin sandbox nuevo. [Entrega y límites](phase/P013-T008_PREPARACION.md), D225.
- Edición posterior manual/formulario/TOML o asistida, reutilizando guardado/preparación/activación. Ayuda IA
  solo con pareja activa congelada; no adopta los clientes propuestos en la propia sesión. UI/diagnósticos en/es.
- V1–v8 siguen leyendo/operando con sus hashes; importación al editor explícita y originales intactos. Backup
  nuevo incluye versiones/archivos/intenciones verificables; restore de consulta sin originales ni agentes
  rechaza guardar, preparar, activar y reparar. Snapshots congelados y recetas/recibos anteriores intactos.

T009 entrega la excepción de §8: la aplicación guarda TOML privado fuera del checkout mediante el carril
confirmado T004/T007–T009. Los agentes conservan sus ámbitos y no reciben escritura de configuración global.
[Entrega T009](phase/P013-T009_ALTA_UI.md), [flujo](flows/configuration-setup.md#alta-y-activación-entregadas-en-t009), D226.
Alta nueva/B sella propuesta aceptada en el commit documental, guarda perfil exacto y solo activa tras recibo,
HEAD limpio, diff/confirmación independiente y barrera D118. Primera tarea bloqueada hasta activar; reenvío no
duplica versiones, alta, preparación ni commits. Edición previa versiona otro candidato con evidencia/documentos
vigentes; ejemplos copiables opcionales. Formulario/TOML, estado y evidencia en/es, con borrador/base/sobre
conservados ante conflicto y sin reenvío automático. Recorrido sintético; QA visual instalada verificada en T012, con sus límites.
T010 entrega edición posterior y asistencia opcional ([D227](DECISIONS.md#d227--p013-t010-edición-posterior-asistencia-congelada-e-impacto-conjunto),
[entrega](phase/P013-T010_EDICION_ASISTIDA.md)). Perfil activo mantiene formulario/TOML; edición técnica parte
de HEAD/documentos confirmados y plan explícito. Cambiar perfil exige actualizar documentación primero;
cambiar perfil/comandos/herramientas/plan exige nueva preparación. Agentes/política/global pueden reutilizar
solo evidencia técnica idéntica, verificada y seleccionada por la activación; no se reescribe el recibo.
Guardar global deriva copias privadas de todos los perfiles activos y muestra diff/impacto/jobs; confirma el
conjunto para reinicio, con cancelación CAS conjunta. Un borrador propio ajeno bloquea sobrescribirlo.
Asistencia congela clientes activos, selección, contenido autorizado y ámbito antes de confirmar; revisor lee,
ejecutor solo inspecciona en área privada. Propuestas y comprobaciones no guardan ni activan; preparar el
proyecto sigue T008. Reenvío consulta el mismo turno, sin otra invocación. Recuperación de escritor incierto
exige parada acreditada. Pruebas sintéticas; compatibilidad/backup e integración instalada acreditados en T011–T012, con sus límites.

README/docs públicas, QA, candidato/paquete y expediente nuevos se entregan en T012–T015. Publicación aplazada
hasta cerrar P013; su cierre no ejecuta acciones remotas ni renueva permisos P012.


T011 entrega [compatibilidad/backup](phase/P013-T011_COMPATIBILIDAD.md), D228: conversión explícita de la
configuración TOML 1–8 del producto con preview/hash y perfiles propios DRAFT. El usuario confirmó preparación
nueva antes de activar. Configuración antigua conserva autoridad hasta validar/preparar todos los perfiles,
confirmar conjunto y reiniciar seleccionando solo almacén gestionado; originales/snapshots/recibos intactos.
No modifica la incorporación B de repositorios con código. Backup formato 2 conserva contenido versionado,
intenciones parciales e inventario consistente; restore de consulta lee evidencia sin originales ni agentes y
rechaza mutaciones. Fuentes/registro ambiguos o permisos sin resolver bloquean, sin elegir autoridad por fecha.


T012 verifica el [primer uso instalado y QA](phase/P013-T012_PRIMER_USO.md) y actualiza README/baseline pública.
La [matriz](phase/P013_MATRIZ_ACEPTACION.md) conserva el alcance; [T013](phase/P013-T013_CANDIDATO.md) verifica
candidato/paquete exactos y [T014](phase/P013_REVIEW.md) emite dictamen favorable y expediente. Cierre T015 pendiente;
ninguna de esas entregas autoriza publicación, amplía evidencia con proveedores reales o cambia los contratos
de configuración, datos o permisos.
