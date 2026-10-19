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
| F03 | Importar un proyecto de un harness anterior (Flujo A) | Inventario, normalización al layout unificado sin perder historial, documentos sincronizados | Inventario de solo lectura (P008-T009, D096), mapa determinista (P008-T010, D097) propuesta del revisor con borradores privados (P008-T011, D098) y commit confirmado con continuidad (P008-T012, D100) |
| F04 | Incorporar un repositorio sin harness (Flujo B) | Discovery por ingeniería inversa, documentos iniciales y archivos raíz mínimos | Inventario estático y propuesta de perfil implementados (P008-T013, D101); conversación de ingeniería inversa sobre HEAD con borradores privados (P008-T014, D102); vista previa, perfil y commit confirmados con P001 adoptada (P008-T015, D103) |
| F05 | Observar un harness anterior | Índice de lectura idempotente, navegación y actualización incremental | Implementado (P002) |
| F06 | Navegar proyectos, fases, tareas y runs | URL propia por recurso, carga limitada y paginada | Implementado (P007, D077) |
| F07 | Ejecutar una tarea | Planificación → ejecución → validación → revisión → aceptación o corrección → commit del harness | Implementado (P003) |
| F08 | Gestionar prompts | Versiones, diff, variables validadas, activación y rollback; snapshot por intento | Implementado (P004) |
| F09 | Resolver bloqueos y permisos | Motivo y evidencia; conceder o denegar una petición exacta; revalidar o reintentar | Implementado (P004) |
| F10 | Controlar fases | Check, reconciliación, preguntas, lote desatendido, enmienda, abandono, cierre con tag | Implementado (P004) |
| F11 | Cerrar y archivar una fase | Protocolo de §7 en un único flujo tras READY | Implementado (P008-T004/T006, D091, D093) |
| F12 | Ver y editar la documentación | Visor seguro y edición con diff confirmado y commit del harness | Implementado (P007, D080) |
| F13 | Conversar con el revisor | Chat sobre HEAD sin esperar al ejecutor; propuestas → tareas confirmadas; comandos deterministas | Implementado (P005, P007) |
| F14 | Inspeccionar tests | Suites y casos JUnit, OK/KO por tarea y evolución por fase | Implementado (P006, P007) |
| F15 | Métricas y estadísticas | Tokens, turnos, modelos, esfuerzos, duraciones y coste equivalente con procedencia | Implementado (P007, D074, D084) |
| F16 | Recuperar y conservar | Backup y restauración de consulta, retención explícita de logs, recuperación tras caída | Implementado (P003, P006) |
| F17 | Distribución local | Wheel con UI y migraciones, `init-db`, `serve`, sesión local | Implementado (P006) |
| F18 | Perfiles declarativos | Perfil de stack (preparación, tests, lint, tipos) declarado en el TOML local y confirmado por el usuario, incluido Python/Django (`pytest`, `ruff`, `mypy`) | Implementado (P008-T008, D095); ejemplo Python/Django pendiente de confirmación sobre el proyecto del usuario |
| F19 | Instrucciones del proyecto para los agentes | `AGENTS.md` incluido en el contexto congelado de cada intento | Implementada (P008-T007, D094) |
| F20 | Elegir carpeta de proyectos | Raíz elegida explícitamente en UI y persistida; concede al servicio crear nuevos hijos sin que la IA decida su ubicación | Planificado (P009-T001/T002, D115) |
| F21 | Agentes configurables por proyecto | Elegir proveedores y modelo/esfuerzo del revisor en UI; selección concreta del ejecutor a cargo del revisor | Planificado (P009-T001/T003, D115); hoy los proveedores son globales y se consultan en solo lectura |
| F22 | Preparar Django desde cero | Hijo nuevo, documentos D088, scaffold, entorno/dependencias y validaciones mediante receta confirmada | Planificado (P009-T004, D115); la creación actual de F02 es documental |

Modos por checkout: **observación** (indexa un harness anterior) y **gestionado** (el motor nuevo controla). Nunca
escriben dos motores sobre el mismo checkout.

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

## 8. Importación de proyectos existentes

- **Flujo A — harness anterior.** Orígenes: repositorios tipo ReferenceProject (`.harness/`, `PROJECT.md`,
  `REQUIREMENTS.md`, archivo por fase sin STATE) y proyectos v1/v2 de este harness. Audita la documentación,
  reorganiza a `docs/flows/` y `docs/archive/phase-NNN/`, normaliza nombres (`SPECIFICATION`, `DECISIONS`,
  `DDBB-DIAGRAM`; variantes como `DECISSONS.md`), adelgaza `CLAUDE.md` y `AGENTS.md` y deja STATE y NEXT_STEPS listos
  para continuar sin perder historial. El historial de runs sigue la migración a gestionado existente (D027),
  confirmada antes de importar cuando hay runs legacy (D099). La vista previa confirma el árbol y los originales
  conservados; el commit sellado se concilia tras una caída y adopta la fase activa con sus documentos (D100).
  T016 (D105) rechaza filtros Git `clean`/`process` incluidos por configuración antes de consultar el estado,
  capturar o sellar; comprueba destinos nuevos ignorados y blobs por hash antes de confirmar y ejecutar.
  Las conversiones de atributos no pueden cambiar los bytes confirmados, tampoco en originales o binarios.
  T018 (D108) exige lecturas A/B sin lazy-fetch desde el primer comando Git; objetos locales ausentes o
  respuestas incompletas bloquean con diagnóstico, sin transportes, recuperación de objetos ni inventarios parciales.
  T019 (D110) rechaza gitlinks en HEAD o índice antes de consultar el estado, también fuera de `docs/`, sin
  inspeccionar submódulos. La misma guardia precede a captura, sellado, escritura y recuperación A/B; se conserva
  el requisito de checkout e índice limpios.
  T020 (D112) exige el mismo modo local en todas las operaciones del escritor A/B, incluido sellado,
  ejecución, conciliación e índice. El commit futuro aún ausente se crea localmente; la falta de un objeto
  necesario de HEAD o del árbol sellado bloquea con diagnóstico antes de escribir, incluso fuera del ámbito
  documental. Git sin soporte se rechaza también en las consultas booleanas, sin fallback ni cambios de configuración.
- **Flujo B — repositorio sin harness.** Inventario determinista (stack, modelos de datos, rutas, tests) e ingeniería
  inversa del revisor en solo lectura para generar ARCHITECTURE, DDBB-DIAGRAM (desde los modelos reales),
  SPECIFICATION base, STATE actual y los archivos raíz mínimos, con un perfil declarativo confirmado por el usuario.
  T013 implementa el inventario de HEAD y la propuesta de perfil (D101), sin ejecutar el proyecto ni escribir su TOML.
  Enumera tests y CI, fuentes y hashes; declara los límites del análisis estático y las expresiones dinámicas sin
  resolverlas. T014 añade la conversación `onboarding`: el revisor de solo lectura consulta ese HEAD exportado,
  propone los documentos D088 y flujos, señala las decisiones inferidas y pregunta lo no deducible. Los borradores
  se aplican por confirmación/CAS en un área privada junto a SQLite; no se reemplaza el README del checkout.
  T015 confirma por hash los documentos y el perfil de la composición del operador; conserva inventario, resumen
  y originales sustituidos en `archive/phase-000/`, crea un commit documental conciliable y adopta P001 ACTIVE
  (D103). El TOML se edita fuera del checkout por el operador; la incorporación no lo escribe ni ejecuta sus
  comandos. Vista previa y UI en el [flujo](flows/project-onboarding.md).

En ambos: el agente no escribe; el harness aplica borradores confirmados con CAS; nada del código del proyecto se
modifica ni se ejecuta sin autorización; el resultado entra en un único commit confirmado.

## 9. Requisitos no funcionales

- Navegar datos registrados no invoca modelos ni necesita red. El frontend no accede al disco ni lanza comandos.
- Listados, logs y diffs paginados con límites explícitos; nada lee un historial completo para pintar una vista.
- Instalación reproducible con lockfiles y versiones exactas; distribución como wheel con assets y migraciones; Node
  solo para construir la UI.
- Logs con retención explícita que conserva contratos, permisos, veredictos y métricas.
- Backup consistente de SQLite y artefactos verificados por hash; restauración en directorio nuevo y solo de consulta.
- Migraciones explícitas con backup previo; un adaptador de CLI con versión no caracterizada se bloquea con diagnóstico.
- El historial es trazable a nivel de aplicación, no un registro inviolable frente al propietario del equipo.

## 10. Criterios de aceptación globales

1. Importar dos veces un historial no duplica entidades ni inventa datos ausentes.
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
11. Crear un proyecto vacío produce documentos, estructura y primera tarea ejecutable; importar uno existente lo deja
    bajo el contrato documental sin perder historial.
12. Backup y restauración recuperan estados, referencias y evidencias verificadas por hash.
13. Respuesta de agente fuera de esquema: run detenido con diagnóstico y salida conservada. Ciclos sin cambios: parada
    con motivo. SSE reconecta sin huecos ni duplicados.

Métricas de producto desde el primer piloto: tiempo de configuración, tiempo hasta la primera tarea aceptada,
intervenciones manuales, errores recuperados, consumo por tarea incluidos los fallos y correcciones tras aceptar. Una
mejora de velocidad sin calidad equivalente no demuestra un menor time to market.

## 11. Fuera de alcance

Multiusuario, nube, ejecución paralela de escritores en un proyecto, App Server o Agent SDK hasta verificar
compatibilidad y autenticación, `project.yaml` portable, edición del TOML desde la UI, aislamiento físico del sistema
operativo y publicación del paquete. Cualquier uso real de proveedores requiere una propuesta y un consentimiento
específicos del usuario.

## 12. Ampliación planificada — P009

D115 añade F20–F22 para un piloto Django desde cero; todavía no están implementados. La persona elige la
carpeta de proyectos y el nombre del hijo desde la UI; la IA no descubre ni propone dónde crear el checkout.
La elección guardada concede al servicio crear hijos en esa raíz, sin repetir ese permiso por proyecto;
no entrega la carpeta padre a los agentes ni amplía confianza en repositorios existentes. No se sobrescribe
un destino existente ni se modifican permisos del sistema operativo.

La receta Django prepara scaffold, entorno y dependencias mediante un plan confirmado y recuperable, después
del bootstrap documental. Red/instalación y creación de archivos protegidos tienen alcance propio; no se
desprotegen para tareas normales. La UI no edita el TOML, ejecutables, credenciales o configuración global.

Los roles podrán configurarse por proyecto desde presets del servicio. El usuario fija proveedor/modelo/
esfuerzo del revisor y proveedor/catálogo del ejecutor; el revisor decide modelo/esfuerzo concretos del ejecutor.
El piloto usa planificación por agente y cuatro tareas del mismo Django: Codex→Codex, Codex→Claude,
Claude→Claude y Claude→Codex (revisor→ejecutor), con intentos previos conservados tras cada cambio.
Plan, alcance y puerta de operación real en [NEXT_STEPS](NEXT_STEPS.md) y [docs/phase](phase/P009_PLAN_DJANGO.md).
