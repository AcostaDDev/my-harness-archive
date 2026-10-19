# P009 — Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

Objetivo y criterios en [ROADMAP](ROADMAP.md#p009--proyecto-django-desde-cero-y-piloto-con-cuatro-combinaciones-de-agentes).
Decisión: [D115](DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto).
[Diseño y matriz](phase/P009_PLAN_DJANGO.md); [flujo y estado de implementación](flows/project-creation.md).

**Estado:** T001–T003 completadas (diseño, carpeta/creación y agentes); T004–T012 pendientes. **Siguiente:** P009-T004.
[Contrato implementable](phase/P009-T001_CONTRATO_CREACION.md), decisión D116. T002 añade producto de
carpeta/creación, sin piloto ni selección de carpeta real del usuario;
la implementación no concede permisos de red, instalación o proveedores.

## Restricciones compartidas

- Una tarea acotada cada vez; P009-T002–T005 antes del piloto. El harness no se ejecuta sobre este repositorio.
- El usuario elige carpeta padre y nombre del hijo; la IA no descubre ni decide rutas. El ejemplo del usuario es
  `$HOME/Documents/projects/`, sin convertirlo en un valor por defecto para otras instalaciones.
- Elegir la raíz concede al servicio crear proyectos hijos; los agentes solo escriben en el checkout hijo.
  No se repite ese permiso de carpeta para cada creación dentro de la raíz vigente. Cada creación muestra su destino.
- Usuario: proveedor, modelo y esfuerzo del revisor; proveedor y catálogo admisible del ejecutor.
  Revisor: modelo/esfuerzo concretos del ejecutor, con motivo por tarea/revisión. Planificación `agent` en el piloto.
- Las flechas significan **revisor→ejecutor**. Las cuatro tareas usan el mismo proyecto/id/checkout e historial.
- La operación real necesita propuesta concreta y consentimiento en T006; no se reutilizan los de D050/D071.
  Instalación/red y servicios locales figuran en su alcance; una elección de carpeta no los concede por sí sola.
- Reusar sesión local, CSRF, CAS, idempotencia, intención antes de efectos, locks, cuarentena y recuperación conservadora.
  No reescribir snapshots ni debilitar las guardias de P008. Sin secretos, runs privados o datos reales en fixtures.
- Paridad al implementar: modelos/migraciones con DDBB-DIAGRAM; flujos con docs/flows; API con OpenAPI/tipos.
  Decisiones duraderas y verificaciones en DECISIONS y docs/phase. No actualizar diagramas vigentes con tablas inexistentes.

## P009-T001 — Contrato de creación, raíces y agentes por proyecto

**Estado:** completada el 2026-10-19 (solo diseño; D116).
**Objetivo:** Dejar un diseño implementable de las ampliaciones, contrastado con D049/D051/D052/D078/D095.
**Alcance:** autoridad de raíz elegida desde UI y convivencia con TOML; persistencia auditada/versionada;
creación idempotente de hijos; presets de roles por proyecto; receta Django posterior al bootstrap documental;
operaciones, contratos, compatibilidad y versiones congeladas afectadas. No ejecutar el piloto.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**
- Elegir raíz es una acción del usuario; se define su persistencia, retirada y efecto sobre creaciones pendientes,
  sin borrar proyectos ni ampliar confianza en repositorios existentes. Los proyectos previos siguen componiendo.
- Propuesta de API/UI y esquema identifica qué cambia, incluida la selección de roles que hoy es global/solo lectura.
  El TOML conserva ejecutables, entornos y secretos fuera de la UI; no se modifica configuración global.
- Se fija el orden carpeta nueva → documentos/commit raíz → receta técnica/commit → cuatro tareas del piloto.
  Se resuelve crear `manage.py`, dependencias y configuración sin quitar su protección frente al ejecutor normal.
- Diseño de recuperación y tests de frontera; ADR correspondiente. Decisiones técnicas reversibles con criterio;
  incógnitas que requieran al usuario se registran, sin inventar modelos, esfuerzos ni consentimientos.
**Validación:** parsers, enlaces y diagramas de diseño; contraste de consumidores existentes. Sin proveedores.
**Resultado:** [contrato](phase/P009-T001_CONTRATO_CREACION.md) con autoridad UI separada del TOML,
creación/retirada/recuperación, esquema y API propuestos, presets v5 y vinculación diferida del entorno Django.
Matriz de fronteras para T002–T005; ninguna incógnita de usuario bloquea T002. Selecciones reales quedan en T006.

## P009-T002 — Elegir carpeta de proyectos y crear carpetas hijas desde la UI

**Estado:** completada el 2026-10-19 (D117). **Depende de:** T001.
**Resultado:** selección/retirada persistente, creación/registro idempotente, recuperación y UI implementadas;
[entrega y verificación](phase/P009-T002_CARPETA_PROYECTOS.md). Sin operación real.
**Contrato de partida:** [D116](DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada)
y [diseño §§2–3, 6–9](phase/P009-T001_CONTRATO_CREACION.md#2-autoridad-de-carpeta-y-convivencia-con-el-toml).
**Objetivo:** Que una persona elija su ubicación y pueda crear allí un nuevo proyecto sin preparar su carpeta a mano.
**Alcance:** sección «Carpeta de proyectos», selección/ruta explícita normalizada y persistida, retirada de la raíz;
formulario con nombre del proyecto y destino completo; creación de hijo, registro y enlace a definición existente.
La selección concede capacidad de creación al servicio, sin `chmod` recursivo ni acceso padre para la IA.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- Dos instalaciones pueden elegir raíces distintas; persisten tras reinicio. Sin elección no se crea nada, ni se
  busca una carpeta por HOME/cwd/prompts. La ruta del usuario no está codificada como predeterminada.
- Solo hijos nuevos: rechazar `..`, rutas absolutas como nombre, escapes/enlaces, conflictos con proyectos/estado
  del servicio y cualquier destino existente, incluso vacío. No se tocan hermanos ni contenido ajeno.
- Doble envío, caída entre crear carpeta/registrar y retirada/cambio de raíz no duplican proyectos ni autorizan
  escrituras con un permiso obsoleto. No se borra una carpeta cuyo contenido o propiedad de operación sea incierto.
- El permiso de carpeta se conserva dentro de su alcance; no hay una petición redundante por cada hijo.
  La UI muestra qué concede la elección y qué destino va a crear. Raíces del TOML y registros antiguos compatibles.
- Migración, API/tipos y diagramas alineados; pruebas con directorios/SQLite temporales, nunca la carpeta real del usuario.
**Validación:** pytest dirigida y completa; Alembic temporal si hay esquema; Node, tipos/build y QA visual del formulario.

## P009-T003 — Configurar revisor y ejecutor por proyecto

**Estado:** completada el 2026-10-19 (D118). **Depende de:** T001.
**Resultado:** presets v5, selección efectiva por checkout y UI, cambios CAS/idempotentes, guardia transaccional
y obsolescencia de planes; [entrega y verificación](phase/P009-T003_AGENTES_PROYECTO.md). Sin proveedores reales.
**Objetivo:** Cambiar las combinaciones en el mismo proyecto sin editar el TOML entre tareas ni recrear el registro.
**Alcance:** presets de proveedor configurados por el servicio; ajustes por proyecto para ambos roles, modelo/esfuerzo
explícitos del revisor y catálogo/modo admisible del ejecutor. Mantener elección final del ejecutor en el revisor.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- Las cuatro parejas Codex/Claude son seleccionables. La UI no elige automáticamente modelo/esfuerzo del revisor
  ni presenta el ejecutor como un modelo fijado por el usuario para todas las tareas.
- Planificación `agent`: el contrato congela selección y motivo del revisor; la ejecución usa ese proveedor/modelo/
  esfuerzo. Una selección fuera del catálogo o incompatible falla sin fallback.
- Cambio confirmado entre tareas terminadas, con idempotencia y versión. Mismo id/checkout/historial; intentos
  anteriores intactos. Trabajo pendiente impide cambios o entra en la cuarentena documentada antes de efectos.
- El cliente no introduce ejecutables, credenciales o entornos; presets ausentes/incompatibles dan diagnóstico.
  Configuraciones anteriores conservan su comportamiento y lectura; modelos/esfuerzos se validan por proveedor.
**Validación:** pytest de composición/registro/plan/recuperación y suite completa; API/tipos, Node/build y QA visual.

## P009-T004 — Receta Django desde cero y perfil ejecutable

**Estado:** pendiente. **Depende de:** T001, T002, T003 (base v5 definida en D116).
**Objetivo:** Que crear un Django nuevo no exija preparar manualmente scaffold, dependencias ni entorno.
**Alcance:** receta determinista de preparación posterior al commit documental, con plan confirmado de archivos,
comandos, versiones y red necesaria; entorno aislado del hijo; perfil Django con ejecutables reales del entorno.
Versiones/locks se decidirán y registrarán al implementar; Django no se convierte en dependencia del harness.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**
- Desde hijo nuevo y documentos D088, generar proyecto Django, app base, plantillas/static mínimos, `.gitignore`,
  dependencias fijadas, configuración de pytest-django/ruff/mypy y, si procede, django-stubs. Sin modelo de tareas aún.
- Crear entorno y resolver instalación/cache/red mediante argv y límites confirmados, sin shell arbitraria.
  Comandos de `startproject`/`startapp` y `migrate` se autorizan para esta receta; no se confunden con los checks del perfil.
- Validaciones: pytest con JUnit, ruff check/format --check, mypy, `manage.py check` y
  `makemigrations --check --dry-run --noinput`. SQLite solo local al hijo; sin credenciales reales ni secretos versionados.
- La receta puede escribir sus archivos de configuración protegidos con confirmación propia; el ejecutor normal
  conserva esas protecciones. No se ejecuta código ajeno ni se relaja el bootstrap para aceptar cualquier archivo.
- Intención previa, progreso y recuperación idempotente de entorno/archivos/commit, sin sobrescribir bytes ajenos.
  Un fallo no dispara reinstalación/red ni invocaciones de agentes ocultas. UI muestra progreso y diagnóstico.
**Validación:** regresiones sintéticas de receta/permisos/caídas, perfil y compatibilidad; Node/build si cambia UI.
No instalar ni lanzar herramientas reales fuera del alcance autorizado de la tarea correspondiente.

## P009-T005 — Ensayo del recorrido sin proveedores reales

**Estado:** pendiente. **Depende de:** T002, T003, T004.
**Objetivo:** Comprobar el recorrido completo antes de consumir modelos en el piloto.
**Alcance:** raíces y checkouts temporales, agentes falsos, las cuatro parejas en un único proyecto y recuperación.
Contrastar el scaffold con Django/pytest/ruff/mypy reales en un entorno temporal con paquetes fijados disponibles;
si falta preparar esos paquetes, registrar y autorizar esa preparación, sin descargar de forma implícita.
**Rutas permitidas:** `tests/**`, `frontend/tests/**`, `docs/**`; fixes del producto se acotan y registran.
**Criterios de aceptación:**
- Seleccionar raíz → crear hijo → definición/commit → receta → cuatro tareas/cambios de roles → commits → cierre
  de fase funciona con agentes falsos. Repetición/reinicio no duplican carpeta, proyecto, intención o commit.
- Cada tarea demuestra selección del ejecutor por el revisor y preservación de historia/configuraciones previas.
- El scaffold pasa las herramientas Django reales; su configuración no se debilita para hacer verde la prueba.
  Hay casos de destino ocupado, raíz revocada, escape, deriva y fallo/cancelación de preparación.
- Suite offline del harness, API/tipos, Node/build, paridad y QA pertinentes correctos; ningún proveedor real invocado.
**Validación:** comandos de AGENTS.md y herramientas reales del entorno temporal autorizado; registro de resultados y límites.

## P009-T006 — Propuesta operativa y consentimiento del piloto

**Estado:** pendiente. **Depende de:** T005.
**Objetivo:** Concretar todo lo necesario para una ejecución real revisable, sin deducir preferencias del usuario.
**Alcance:** instalar/verificar el wheel fuera del checkout de desarrollo (D051), preparar la propuesta sin iniciar
el piloto y recoger las selecciones/autorizaciones que falten. Preflight de CLI reales solo dentro del consentimiento.
**Rutas permitidas:** `docs/**`; configuración y artefactos de operación fuera del checkout, cuando se autoricen.
**Criterios de aceptación:**
- Raíz elegida desde UI, nombre nuevo del hijo, puertos loopback, SQLite/artefactos del servicio y destino de paquete
  identificados; confirmar disponibilidad sin crear ni alterar proyectos existentes. Nombre de trabajo: `harness-django-pilot`.
- Usuario fija modelo/esfuerzo del revisor para Codex y Claude, proveedores y catálogos del ejecutor. No se heredan
  sin confirmación las elecciones históricas de D071. El revisor elegirá los modelos/esfuerzos concretos de cada ejecutor.
- Propuesta enumera las cuatro tareas, definición/receta/check/cierre, comandos/dependencias/red, versiones de CLI,
  límites de llamadas/tiempo/correcciones, criterios de parada y limpieza de procesos. Sin retry/fallback silencioso.
- Consentimiento específico antes de T007; reutilizar lo ya autorizado dentro de esos límites, sin repreguntas
  redundantes. Fallos detienen; corregir no autoriza relanzar automáticamente ni sustituir proveedores.
- Historiales/streams reales permanecen privados junto al estado del servicio; docs/phase solo lleva resumen
  saneado y referencias/hashes no sensibles, nunca credenciales ni fixtures derivados de runs privados.
**Validación:** revisión documental de propuesta y elecciones; checks del paquete/preflight según el alcance autorizado.

## P009-T007 — Crear el proyecto Django nuevo desde la UI

**Estado:** pendiente. **Depende de:** T006 con consentimiento registrado.
**Objetivo:** Empezar con un destino inexistente y llegar a Django ejecutable y documentado sin scaffold manual.
**Alcance:** elegir carpeta padre, dar nombre al hijo, definir el pequeño gestor de tareas con el revisor, aceptar
D088/P001 y preparar mediante receta su entorno/código base. Operar con el wheel instalado, no con este checkout.
**Rutas permitidas:** `docs/phase/**` para evidencia saneada; proyecto hijo y estado de operación autorizados aparte.
**Criterios de aceptación:**
- No existen carpeta hija, código ni entorno al comenzar. La UI los crea/prepara mediante operaciones registradas;
  ningún agente elige la ubicación o escribe en el padre/hermanos. Bootstrap documental y receta conservan commits propios.
- Proyecto/id/checkout único, perfil Django real seleccionado, herramientas base correctas y P001 con cuatro tareas
  de negocio planificadas. README, instrucciones, arquitectura, diagrama y flujos reflejan lo existente.
- App base responde en loopback; se excluyen SQLite local, entorno, caches, secretos y reportes del commit.
**Validación:** preparación/validaciones reales, estado Git/documental y recorrido UI; sin edición manual del scaffold.

## P009-T008 — Piloto: Codex revisor → Codex ejecutor

**Estado:** pendiente. **Depende de:** T007.
**Objetivo:** Modelo Task y creación/listado de tareas (tarea P001-T001 del proyecto hijo).
**Alcance:** título obligatorio, descripción opcional, completada inicialmente false y fecha de creación;
formulario de alta y lista mediante plantillas. Migración, tests y diagrama de datos/flujos en el mismo cambio.
**Rutas permitidas:** `docs/phase/**`; cambios del hijo solo mediante su contrato gestionado confirmado.
**Criterios de aceptación:**
- Usuario configura revisor Codex con su modelo/esfuerzo y proveedor ejecutor Codex. El revisor selecciona modelo/
  esfuerzo del ejecutor y motivo; esa selección coincide con la invocación congelada.
- Alta válida persiste y aparece en la lista; título vacío se rechaza. Validaciones/JUnit y revisión correctos;
  aceptación y commit del harness dejan P001-T001 COMMITTED, con evidencia del contenido exacto.
**Validación:** herramientas Django del perfil, tests de modelo/vistas/formulario, UI y procedencia de agentes/commit.

## P009-T009 — Piloto: Codex revisor → Claude ejecutor

**Estado:** pendiente. **Depende de:** T008 COMMITTED y sin trabajo pendiente.
**Objetivo:** Editar y borrar tareas con confirmación (P001-T002 del mismo proyecto).
**Alcance:** formularios de edición/borrado, validación de título y gestión de inexistentes; conservar datos previos.
**Rutas permitidas:** `docs/phase/**`; cambios del hijo solo mediante su contrato gestionado confirmado.
**Criterios de aceptación:**
- Cambiar solo la selección necesaria en Ajustes del mismo proyecto; revisor Codex elegido por el usuario y
  ejecutor Claude cuyo modelo/esfuerzo elige el revisor. Id/checkout y evidencia de T008 intactos.
- Editar conserva identidad/datos no editados; GET no borra y el borrado exige POST/confirmación con CSRF.
  Tests y perfil pasan; revisión y commit terminan P001-T002 COMMITTED.
**Validación:** perfil Django, casos válidos/inválidos/inexistentes y QA UI; nueva configuración y selección trazables.

## P009-T010 — Piloto: Claude revisor → Claude ejecutor

**Estado:** pendiente. **Depende de:** T009 COMMITTED y sin trabajo pendiente.
**Objetivo:** Completar/reabrir y filtrar pendientes/completadas (P001-T003).
**Alcance:** cambio de estado mediante POST, filtros de lista y estados vacíos, manteniendo CRUD anterior.
**Rutas permitidas:** `docs/phase/**`; cambios del hijo solo mediante su contrato gestionado confirmado.
**Criterios de aceptación:**
- Usuario cambia el revisor a Claude y fija su modelo/esfuerzo; ejecutor Claude seleccionado por el revisor.
  No se reinicia el proyecto ni se altera el historial de las dos tareas anteriores.
- Completar/reabrir persiste y los tres filtros son correctos; GET no modifica estado. Regresiones CRUD verdes,
  flujo actualizado, revisión y commit dejan P001-T003 COMMITTED.
**Validación:** perfil Django, tests de transición/filtros/CSRF y UI; evidencia de selección e historial conservado.

## P009-T011 — Piloto: Claude revisor → Codex ejecutor

**Estado:** pendiente. **Depende de:** T010 COMMITTED y sin trabajo pendiente.
**Objetivo:** Buscar tareas por título y verificar el recorrido completo (P001-T004).
**Alcance:** búsqueda GET combinable con filtros, sin resultados y tests de integración de alta/edición/estado/borrado.
**Rutas permitidas:** `docs/phase/**`; cambios del hijo solo mediante su contrato gestionado confirmado.
**Criterios de aceptación:**
- Revisor Claude con selección del usuario y proveedor ejecutor Codex; modelo/esfuerzo y motivo decididos por el revisor.
  Mismo proyecto/id/checkout y configuraciones anteriores preservadas por intento.
- Búsqueda correcta junto al filtro, entradas tratadas como datos y estados vacíos legibles; regresiones de las
  tres tareas anteriores y todas las validaciones pasan. Revisión y commit dejan P001-T004 COMMITTED.
**Validación:** perfil Django, integración funcional, QA de búsqueda y contraste de las cuatro parejas efectivamente usadas.

## P009-T012 — Cierre del piloto y revisión de salida de P009

**Estado:** pendiente. **Depende de:** T008–T011 COMMITTED.
**Objetivo:** Acreditar que el mismo Django soporta el cambio de agentes durante su desarrollo y un cierre completo.
**Alcance:** QA funcional en navegador, validaciones finales y check/cierre/archivo de P001 del hijo con autorización
vigente; resumen de cuatro tareas, incidencias y métricas. No cerrar P009 del harness en esta misma tarea.
**Rutas permitidas:** `docs/**`; operaciones del hijo mediante el producto dentro del consentimiento de T006.
**Criterios de aceptación:**
- Alta/listado, edición/borrado, estado/filtros y búsqueda funcionan juntos; tests/JUnit, lint, tipos, checks y
  migraciones correctos. P001 del hijo READY y CLOSED con archivo, commit/tag según configuración, sin duplicados.
- Matriz de evidencia recoge por tarea proveedor/modelo/esfuerzo del revisor elegidos por el usuario, selección/
  motivo del ejecutor por el revisor, invocación real, validaciones, commit y configuración congelada. Ausentes como tales.
- Registrar consumo/duración/intervenciones con procedencia; tareas distintas no prueban una clasificación de calidad
  entre modelos. Fallos o parejas no completadas impiden presentar el piloto como conseguido.
- Informe criterio a criterio, checks pertinentes, diff y límites; STATE/NEXT_STEPS al día. Proponer correcciones
  acotadas si hay hallazgos. Cierre/archivo documental de P009 solo después de su revisión, en otra tarea.
**Validación:** evidencia del producto instalado y proyecto hijo, comprobaciones Git/SQLite/archivos y suites pertinentes;
sin publicar, hacer push, añadir funciones o consumir llamadas fuera de la autorización.
