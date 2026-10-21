# P009 — Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

Objetivo y criterios en [ROADMAP](ROADMAP.md#p009--proyecto-django-desde-cero-y-piloto-con-cuatro-combinaciones-de-agentes).
Decisión: [D115](DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto).
[Diseño y matriz](phase/P009_PLAN_DJANGO.md); [flujo y estado de implementación](flows/project-creation.md).

**Estado:** T001–T007 y T013–T017 completadas. T007 se detuvo el 2026-10-20 (D123), se corrigió en `cli-13` (D124)
y se completó el 2026-10-21 con autorización nueva: Django creado desde la UI, commit raíz y técnico
([evidencia §7](phase/P009-T007_CREACION_DJANGO.md#7-reanudación-y-cierre-de-t007-2026-10-21), D127). T008 se detuvo el
2026-10-21 en la revisión: una ruta de directorio (`core/`) no cubre sus archivos en la política de rutas
([evidencia](phase/P009-T008_PILOTO_CODEX_CODEX.md), D128). T017 lo corrige el 2026-10-21: `dir/` se congela como
`dir/**` (D129). T009–T012 pendientes.
**Siguiente:** reanudar T008 con un run nuevo, wheel reconstruido y verificado y **autorización nueva del usuario**
(D129: antes, el hijo vuelve a quedar limpio en `d762e77`; `fc340afb` no se revalida).
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

**Estado:** completada el 2026-10-19 (D119). **Depende de:** T001, T002, T003 (base v5 definida en D116).
**Resultado:** receta empaquetada, enlaces diferidos al entorno, plan/confirmación, journal de preparación,
perfil ejecutable y UI implementados; [entrega y verificaciones](phase/P009-T004_RECETA_DJANGO.md).
Herramientas reales y ensayo completo en T005; sin instalación ni piloto en T004.
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

**Estado:** completada el 2026-10-19 (D120). **Depende de:** T002, T003, T004.
**Resultado:** recorrido API completo con cuatro parejas de CLI falsas en un hijo, reinicios/reenvíos,
recuperación del commit técnico sin repetir herramientas y cierre con archivo/tag. Scaffold contrastado con Django,
pytest/ruff/mypy reales en Python 3.13.13 y uv 0.12.19; wheels fijados preparados con autorización específica.
[Entrega, comandos y límites](phase/P009-T005_ENSAYO_DJANGO.md). Sin proveedores ni piloto.
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

**Estado:** completada el 2026-10-20 (D121). **Depende de:** T005.
**Resultado:** [propuesta autorizada](phase/P009-T006_PROPUESTA_PILOTO.md) con raíz, hijo, área, puertos, revisores,
catálogos, wheelhouse, límites, parada y limpieza. Las CLI instaladas están fuera del baseline: T013 las caracteriza
antes de T007. El wheel operativo se instala tras T013, dentro del consentimiento; nada se instaló ni ejecutó en T006.
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

**Estado:** completada el 2026-10-21 (D127), tras la parada del 2026-10-20 (D123) y su corrección (D124).
**Resultado:** definición en los turnos 2–3 con Codex, commit raíz `9b612ca` (con tag `p001` de P001 añadido por el
usuario), receta offline y commit técnico `d762e77`; portada en loopback. 3 de 20 invocaciones.
Hallazgo: la plantilla `define-project` no aclara que los marcadores son opcionales en una carpeta nueva (D127).
**Depende de:** T006 con consentimiento registrado (D121), T013, T014 y una autorización nueva del usuario.
**Avance del 2026-10-20:** área, wheel, wheelhouse, TOML, preflight e `init-db` preparados; carpeta de proyectos guardada e hijo
`harness-django-pilot` creado y registrado desde la UI. El primer turno de definición con revisor Codex falla sin
llegar al modelo (falta `--skip-git-repo-check` en un hijo sin Git). Una invocación lanzada, cero tokens.
[Evidencia saneada](phase/P009-T007_CREACION_DJANGO.md). T014 lo corrige (`cli-13`) y la propuesta está al día
([§8](phase/P009-T006_PROPUESTA_PILOTO.md#8-actualización-tras-t014)). Reanudar exige wheel reconstruido desde
T014 y **autorización nueva del usuario**; se reutilizan el hijo, su registro y su conversación (admite turno nuevo).
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

**Estado:** detenida el 2026-10-21 (D128). **Depende de:** T007; su reanudación, de T017 (completada, D129).
**Avance:** run `fc340afb` planificado y ejecutado con Codex `gpt-6-luna`/`medium` en los tres roles; selección del
ejecutor por el revisor, con motivo, igual a la invocación; seis validaciones correctas. El revisor bloquea porque la
política de rutas marca los seis archivos de `core/` aunque `core/` está en la allowlist. 3 de 7 invocaciones, sin
commit. Cambios del ejecutor conservados sin confirmar en el hijo. Antes, el recibo de preparación se restauró
borrando el bytecode que dejó el QA de T007. [Evidencia saneada](phase/P009-T008_PILOTO_CODEX_CODEX.md).
Reanudar exige wheel reconstruido y verificado y **autorización nueva del usuario**. Por decisión del usuario
(D129), `fc340afb` queda BLOCKED como evidencia y no se revalida. Se retiran del hijo exactamente las ocho rutas de su
diff, sin tocar `.venv`, TOML ni SQLite, y se encola P001-T001 en un run nuevo. Son al menos 3 de las 4 invocaciones
que quedan; la autorización dirá si se amplía el techo para un ciclo REVISE o si se para.
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

## P009-T013 — Caracterizar las CLI instaladas para el piloto

**Estado:** completada el 2026-10-20 (D122). **Depende de:** T006.
**Resultado:** Codex 0.163.0 (también escritor) y Claude 2.1.304 en el baseline `cli-12` sin cambiar argv ni controles;
[sondas, fuente, pruebas y límites](phase/P009-T013_CARACTERIZACION_CLI.md). Ningún modelo invocado.
**Objetivo:** Que el producto admita Codex 0.163.0 y Claude 2.1.304, las versiones fijadas en la propuesta, sin
debilitar las comprobaciones de versión ni los controles de lectura, escritura, memoria y confianza.
**Alcance:** ejecutar `--version`, `--help` y la ayuda de los subcomandos usados de los binarios fijados en
[§1 de la propuesta](phase/P009-T006_PROPUESTA_PILOTO.md#1-bloqueo-constatado-cli-fuera-del-baseline); leer las cadenas
del binario de Codex para su vocabulario de esfuerzo. Comparar con la caracterización vigente y ampliar `SUPPORTED`/
`WRITE_SUPPORTED`, o versionar el adaptador si cambia el argv, el protocolo o las salidas.
**Rutas permitidas:** `src/harness_local/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**
- Diferencias de ayuda/flags/esfuerzos registradas por versión; las versiones anteriores siguen admitidas y sus
  hashes y snapshots congelados no cambian. Una versión no caracterizada sigue rechazándose.
- Escritura de Codex admitida solo si su protocolo y la supresión de confianza (D066/D071) siguen comprobados;
  si hace falta invocar un modelo, parar y pedir autorización aparte. Ningún proveedor invocado con prompt.
- Regresiones offline con CLI falsas para cada versión nueva; ejemplos de configuración al día.
**Validación:** pytest dirigida y completa, unittest, Alembic check si procede; sin wheel operativo ni piloto.

## P009-T014 — Definición con revisor Codex en un hijo sin Git

**Estado:** completada el 2026-10-20 (D124). **Depende de:** T013; bloqueaba la reanudación de T007 (D123).
**Resultado:** adaptador `cli-13`; Codex recibe el flag en la definición D088 (plantilla congelada `define-project`)
y en exportaciones, nunca en importación sobre checkout vivo, otros roles ni ejecutor. Jobs `cli-12` pendientes
en cuarentena; CLI falsa con la negativa de Codex; conversación con turno fallido admite otro; propuesta §8 al día.
[Criterio, versión y verificación](phase/P009-T014_DEFINICION_SIN_GIT.md). Sin proveedores ni piloto.
**Objetivo:** que el revisor Codex pueda redactar la definición D088 de un proyecto nuevo, cuya carpeta aún no es
un repositorio Git, sin relajar el sandbox de lectura ni la memoria desactivada.
**Alcance:** decidir cuándo recibe Codex `--skip-git-repo-check` en `definition` sobre la carpeta viva (hoy solo
lo recibe con raíces exportadas, D083/D102) y si eso exige versionar el adaptador frente a `cli-12`, con su
efecto sobre jobs congelados y cuarentena. Hacer que la CLI falsa reproduzca la negativa de Codex fuera de Git,
para que un ensayo como el de T005 la detecte. Comprobar si la conversación del hijo admite un turno nuevo.
**Rutas permitidas:** `src/harness_local/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**
- Una definición con revisor Codex en un hijo vacío sin `.git` arranca. El flag no llega a ejecutores, a checkouts
  Git vivos ni a otros roles que no lo necesiten; sandbox `read-only`, memoria y confianza sin cambios.
- La CLI falsa falla como la real sin el flag; regresiones por rol, proveedor y versión. Versiones/snapshots previos intactos.
- Si cambia la identidad del adaptador, la propuesta de T006 se actualiza antes de operar (D121 §6).
**Validación:** pytest dirigida y completa, unittest, Alembic check si procede. Sin proveedores ni piloto.

## P009-T015 — Actualizar la verificación del wheel al flujo D088

**Estado:** completada el 2026-10-20 (D126); era obligatoria antes del cierre documental de P009 (D123).
**Resultado:** el script recorre definición D088 → aceptación → primera tarea → commit con agentes sintéticos y
reinicios, y lanza `serve` con `TMPDIR` propio; ARCHITECTURE §9 lo documenta. Wheel nuevo construido y verificado
entero sin conexión. [Recorrido y verificación](phase/P009-T015_VERIFICACION_WHEEL.md).
**Objetivo:** que `scripts/check_distribution.py` vuelva a verificar entero un wheel construido.
**Alcance:** sustituir el tramo de bootstrap v1 (405 en `POST /projects/offline/bootstrap/preview`, retirado en
D089/D093) por el recorrido vigente de definición/aceptación con agentes sintéticos, conservando las demás
comprobaciones del wheel instalado (contenido, sesión, reinicio, errores, backup y restauración de consulta).
Documentar en ARCHITECTURE §9 el `TMPDIR` del servicio, que hoy decide dónde queda la clave de sesión.
**Rutas permitidas:** `scripts/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- `build_distribution.py` + `check_distribution.py` terminan correctamente sobre un wheel nuevo en directorios temporales.
- Sin proveedores, red ni la SQLite/área operativa del piloto; ningún proyecto real del usuario.
**Validación:** el propio script, la suite offline completa y unittest.

## P009-T016 — Suite pytest rápida

**Estado:** completada el 2026-10-20 (D125), a petición del usuario y fuera del piloto.
**Resultado:** pytest pasa de más de 25 minutos en serie a unos 4:20 con xdist (`-n auto`), sin perder garantías:
Git real en lugar del shim de macOS, plantilla migrada por sesión, mundos A/B montados solo si se usan,
16 combinaciones redundantes menos, adaptador Git con menos procesos y `posix_spawn`.
[Diagnóstico, criterio y medidas](phase/P009-T016_SUITE_RAPIDA.md).
**Rutas permitidas:** `tests/**`, `src/harness_local/adapters/**`, `pyproject.toml`, `uv.lock`, `AGENTS.md`, `docs/**`.
**Validación:** suite pytest completa en paralelo y en serie, unittest, `node --test` y equivalencia del adaptador
contra `HEAD`. Sin proveedores, wheel ni harness.

## P009-T017 — Rutas de directorio en el contrato de tarea

**Estado:** completada el 2026-10-21 (D129, [entrega](phase/P009-T017_RUTAS_DIRECTORIO.md)): `task_contract`
congela `dir/` como `dir/**` en ambas listas; contratos ya congelados intactos; `fc340afb` no se revalida.
**Depende de:** T008 detenida (D128); bloqueaba su reanudación.
**Objetivo:** que una entrada de directorio de un contrato (`core/`) signifique lo mismo al congelar el contrato,
al restringir al ejecutor y al comprobar la política de rutas, o que se rechace antes de invocar al ejecutor.
**Alcance:** hoy `task_contract` acepta `core/` y `check_paths` lo empareja con `fnmatchcase`, que no cubre
`core/models.py`. Decidir con criterio entre normalizar la barra final como `dir/**` en ambas listas y rechazarla al
validar. Contrastarlo con el resto de consumidores de `allowed_paths`/`forbidden_paths` (restricciones del ejecutor,
revisión, `scope_grants`, concesiones de ficheros, documentos), con la orientación de `plan-task` y con los
contratos ya congelados. Decidir también cómo sigue el run `fc340afb`, BLOCKED con los cambios conservados en el
hijo: revalidarlo con la semántica nueva o descartarlo con la acción del producto y abrir otro.
**Rutas permitidas:** `src/harness_local/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**
- Una tarea con `core/` en la allowlist no marca como infracción los archivos de `core/`, o falla al congelar el
  contrato sin ejecutar nada; nunca después de ejecutar y revisar. Lo mismo con un directorio en `forbidden_paths`.
- Los contratos y snapshots ya congelados conservan su lectura y sus hashes; si cambia la semántica de un run ya
  congelado, se versiona y se documenta. Rutas exactas y globs actuales se comportan igual.
- Regresiones con agentes falsos que reproducen el contrato de T008 (rutas de directorio del NEXT_STEPS del hijo).
  El ensayo de Django usa también esa notación.
**Validación:** pytest dirigida y completa, unittest, Alembic check si procede. Sin proveedores ni piloto.
