# P011 — Plan de preparación para apertura pública en GitHub

Fecha: 2026-10-22. Decisión: [D154](../DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github).
**Estado:** T001 completada documentalmente (D159); dieciocho tareas pendientes, sin cambios de producto.
**Planificación inicial:** finalizada en D156 y commit `6174f51`; ajustes D157/D158 incorporados
en `2730f54`. La petición posterior autoriza T001 y su commit local en inglés; siguiente T002.
Contrato de ejecución: [T001](P011-T001_CONTRATO_APERTURA.md), [inventario](P011-T001_INVENTARIO.md).
[Criterios](../ROADMAP.md#p011--preparación-para-apertura-pública-en-github),
[tareas](../NEXT_STEPS.md), [estado](../STATE.md).

## Resultado y alcance

Preparar una distribución local que una persona ajena al proyecto pueda encontrar en GitHub, entender, instalar
y probar con documentación inglesa, opción española, configuración mínima, licencia y soporte claros.
El usuario encarga crear la fase y permite añadir/modificar tareas; no encarga ejecutarlas en esta entrega.
Ese fue el alcance de la planificación original; la petición posterior de continuar ejecuta únicamente T001.
La primera versión local P010 y su paquete `0.1.0` siguen siendo la base entregada, con límites D151/D153.

Se conservan los cinco objetivos pedidos: inglés del código, elección en/es, CLI más compatibles, paridad
real de diagramas y README completo. Se añaden licencia/contenido publicable, reproducibilidad, metadatos/CI
y revisión del candidato como condiciones para una apertura pública revisable. Licencia/titularidad y versión
candidata quedan para sus tareas; no se presumen aquí ni se cambia visibilidad o publica nada.

[D155](../DECISIONS.md#d155--p011-retirada-del-harness-anterior-y-dos-vías-de-alta) añade retirar todas las
funcionalidades del harness anterior antes de la apertura pública. Se incorpora T019 y un décimo criterio de
salida, manteniendo los números anteriores. La retirada es trabajo pendiente, no eliminación ya implementada.

## Corte inicial privado/público y desarrollo posterior

[D157](../DECISIONS.md#d157--repositorio-público-nuevo-y-continuidad-del-desarrollo) adopta como dirección el
segundo modelo propuesto por el usuario: instantánea pública inicial revisada con nueva raíz Git y documentación
de partida nueva, conservando este historial/ADR/fases anteriores privados. No exportar `.git`/objetos/refs/tags,
archivos internos o enlaces/contexto que requieran acceso privado; tampoco reescribir o borrar este historial.

La documentación pública inicial sí debe explicar el estado real, arquitectura, decisiones técnicas de partida,
requisitos/operación y cómo contribuir, para que usuarios/forks/agentes dispongan de contexto suficiente. No es
una carpeta vacía ni un índice de ADR internas. Se mantiene D088 con contexto público nuevo coherente, sin fingir
que decisiones/fases privadas ocurrieron en el nuevo repositorio. Mapear la procedencia del corte privadamente.

Desde la apertura, el repositorio público será fuente principal de código y docs; nuevas decisiones/fases se
registran y versionan allí y evolucionan con las releases. Este checkout conserva historia/archivo privado, sin
dos desarrollos activos sincronizados por copias que sobrescriban contribuciones. No excluir ni congelar las docs
públicas posteriores. T001/T002 definen frontera, T014 el contexto público y T015–T017 el candidato/verificación.
Aquí no se crea una copia, inicializa Git, publica, cambia visibilidad ni opera ningún checkout con el harness.

## Modo continuo reservado para v0.2.0

[D156](../DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020) reserva el
encadenamiento completo `tareas → commits → check → cierre/archivo → planificación y ejecución de siguiente fase`
para v0.2.0, después de la apertura inicial en GitHub, fuera de P011. Modo opcional con autorización inicial
acotada y parada ante errores, HITL, cambios fuera de alcance o límites de consumo; READY, aceptación por contenido
y recuperación deberán mantenerse. La fase/tareas/diseño se definirán más adelante; no se implementan ni se amplía
la autoridad por registrarlo. T015 no asigna v0.2.0 a la apertura inicial ni incorpora esa automatización.

El comportamiento vigente conserva lote de tareas/commits, check explícito y cierre con autorización propia.
El cierre confirmado archiva y abre la sucesora de ROADMAP sin tareas; su plan posterior requiere confirmación.
Finalizar esta planificación no equivale a cerrar P011, publicar el paquete o cambiar versión. El commit
documental autorizado en D156 y los ajustes D157/D158 ya se hicieron; la petición posterior autoriza T001 y su
commit local en inglés, sin encadenamiento automático ni publicación.

## Base inspeccionada

- Checkout limpio al comenzar. Según STATE/código: `cli-13`, TOML hasta v5, historial hasta formato 8,
  Alembic `0023_run_projection`, 48 tablas y wheel `0.1.0` verificado en P010.
- Git rastrea 687 archivos: 158 bajo `src/`, 55 bajo `frontend/`, 213 bajo `tests/`, siete scripts, ocho ejemplos,
  once docs de flujos y 219 archivos de archivo. Son grupos preliminares, no una auditoría lingüística completa.
- Hay comentarios/docstrings españoles y UI mayormente española. Los prompts ya contienen muchas instrucciones
  inglesas pero también ejemplos/literales españoles; no procede traducirlos por reemplazo masivo.
- No se declara solución i18n en `frontend/package.json`; ARCHITECTURE §8 sigue fijando documentación española.
  La convención cambia al implementar, no por presentar este plan como producto existente.
- `recipes/django.py` y `recipes/typescript_web.py` incorporan su fuente en `fingerprint()`: traducir comentarios
  puede invalidar recibos. Prompts/contextos también tienen identidades por contenido; T001 debe tratarlo primero.
- Las listas de CLI son exactas y por rol; existen guardias de confianza, memoria, permisos y recuperación.
  Ampliar compatibilidad no equivale a retirar el rechazo numérico sin preservar esas guardias.
- README supone cachés/herramientas preparadas y la plantilla TOML incluye dos proveedores, composiciones y un
  proyecto ficticio; falta una entrada mínima reproducible de un proveedor desde un clon limpio.
- No se localizaron LICENSE, CONTRIBUTING, SECURITY ni workflows `.github` entre archivos rastreados. Esto no
  constituye análisis jurídico ni escaneo completo del historial/secretos, que corresponde a T002.

## Política lingüística prevista

| Superficie | Resultado previsto | Conservación |
|---|---|---|
| Código mantenido, comentarios/docstrings/descripciones | Inglés y revisión de identificadores españoles internos | Protocolos, rutas/revisiones/claves persistidas no se renombran por estética |
| Prompts originales | Instrucciones inglesas con lengua efectiva de salida | Personalización y catálogos congelados intactos |
| Ajustes globales | Visual y default de trabajo en/es, inicialmente en; visual mutable y default solo para nuevas altas | No son cambios del TOML/configuración global del equipo |
| UI/API/CLI y conversación | UI/mensajes/respuestas humanas/HITL en visual global; sin ajuste visual por proyecto | Logs, mensajes históricos y datos originales no se retraducen |
| Trabajo por proyecto | en/es inmutable desde alta para documentos/planes/ADR/código/comentarios nuevos | Ambas lenguas congeladas por job/turno; fuentes previas en otros idiomas legibles |
| Documentación pública vigente | Baseline inglesa nueva y entrada española; futuras decisiones/fases públicas | Historia/ADR privadas originales conservadas y excluidas del corte inicial |
| Fixtures/evidencias | Comentarios mantenidos ingleses, entradas bilingües donde prueban comportamiento | Excepciones históricas por ruta/motivo, bytes/hashes intactos |

[D158](../DECISIONS.md#d158--idioma-visual-global-y-trabajo-inmutable-por-proyecto) afina el contrato inicial:
`ui_language` y `default_work_language` globales, en/es y en inicial. Visual es global y mutable, gobierna UI y
conversación/respuestas humanas/HITL; nunca se guarda por proyecto. `work_language` se elige al crear/incorporar
desde default global y queda inmutable por UI/API/configuración; gobierna documentación y código. Nuevos defaults
solo afectan futuras altas. El propio proyecto público my_harness se establece con trabajo en inglés.

Ejemplo: visual es/trabajo en produce conversación/respuesta española y documentos/código ingleses. Cambiar
visual durante el proyecto cambia próximas interacciones, sin cambiar trabajo. Ambas lenguas se capturan al
admitir cada job/turno y conservan en sus intentos: no mutar una llamada activa, pendientes/reintentos o historia.
Un resultado puede combinar prosa humana en visual y borradores/código en trabajo; T001/T009 mapearán sus campos.

Prompts originales ingleses, con directiva del motor tipada como `Respond to the user in {ui_language}. Write
project documentation and code in {work_language}.` por el canal de instrucciones disponible de ambos proveedores,
sin suponer system prompt/flags comunes inexistentes. Plantillas personalizadas editables y congeladas por intento.
Leer fuentes previas de otro idioma está permitido; no traducir arbitrariamente contenido, protocolos/rutas,
keywords o interfaces públicas. No impone idioma funcional a apps hijas ni garantiza ahorro fijo de tokens.
T001 concretará persistencia/precedencias/migración compatibles; T007–T010 implementarán el contrato y sus pruebas.

React permite organizar catálogos y un proveedor/contexto de idioma. T001 elegirá biblioteca o solución propia
según interpolación, plurales/fechas, accesibilidad y mantenimiento, con decisión antes de añadir dependencias.
No se presupone que `.po`, empleado en Django, sea el formato apropiado para este React/FastAPI.
La excepción histórica no se usa para dejar comentarios mantenidos sin traducir: se inventaría y justifica,
y cualquier fuente ligada a una huella tiene tratamiento compatible antes de editarla.

## Compatibilidad CLI prevista

Definir mínimos/familias por proveedor/rol y admitir versiones posteriores por capacidades necesarias, sin
editar una allowlist para cada patch. Congelar versión observada, capacidades y política por intento y separar
verificada/candidata. Una versión futura arbitraria no se anuncia compatible por su número o por arrancar.

T011 precisa las pruebas y qué semántica requiere más evidencia que version/help. Si no puede acreditarse una
guardia esencial, se bloquea con diagnóstico; no se sustituye por un aviso. T012 implementa y verifica con CLI
falsas. Mínimos concretos y aceptación de candidatas se fijan con evidencia, no por intuición en el plan.
No se cambia a App Server/SDK ni se amplía automáticamente el catálogo de modelos.

Caracterización real, inferencia o smokes requieren tarea/consentimiento propios. Si hacen falta para anunciar
soporte público, se añaden antes del dictamen y se conserva su resultado; pruebas sintéticas no acreditan uso
real. D151 mantiene aplazados B y el perfil D095; A sale del soporte futuro por D155 sin darse por validado.
P009 no concede nuevas operaciones.

## Dos entradas de proyecto y retirada del harness anterior

El producto público tendrá solo crear un proyecto desde cero o incorporar un repositorio existente sin harness
(actual Flujo B), ambos bajo control y seguimiento gestionados de my_harness. Registrar/reabrir un proyecto ya
gestionado sigue siendo operación normal; no constituye una tercera modalidad.

T019 retira visor `/legacy`, rutas API/CLI de importación/consulta/observación, SSE/feeds/watchers legacy,
activación del motor anterior y normalización/importación A, incluidos conversación `project_import`, prompts,
configuración y código/tests/fixtures exclusivos. No basta ocultar la navegación dejando servicios operativos.
Se realiza tras T002 y antes de T003, para no traducir ni empaquetar componentes destinados a eliminación.

El inventario T001 separa módulos/tablas exclusivos de infraestructura compartida por B (por ejemplo
`project_imports`, `purpose = import_commit`, repositorios y escritor Git). Conservar historial propio/codec y
componentes comunes necesarios no conserva un modo de proyecto legacy. Se precisan migración/backup/recuperación
y resolución de jobs anteriores sin ejecutarlos, reinterpretarlos como B o borrar evidencia/datos automáticamente.
No se reescriben revisiones Alembic ni historia congelada para borrar rastros de una capacidad retirada.

T019 actualiza criterios globales 1/11/13 de SPECIFICATION para idempotencia cero/B y observación gestionada por
cursor; T017 revisa los trece ajustados conservando la matriz histórica de P010. T013 audita los flujos finales,
T014 presenta las dos únicas entradas y T015/T016 acreditan ausencia de entrypoints/componentes exclusivos legacy
en el paquete y regresión de cero/B. Los apartados vigentes que describen legacy/A siguen documentando el código
actual hasta implementarse T019; no se exigen mantener como capacidades públicas por ser antecedentes.

## Secuencia de trabajo

| Tarea | Entrega | Dependencias |
|---|---|---|
| T001 | Inventario por archivo y contrato idiomas/fuentes/setup | Base P010 |
| T002 | Licencia elegida, atribuciones y contenido publicable | T001 |
| T003 | Inglés núcleo/perfiles | T001, T019 |
| T004 | Inglés backend/recetas con compatibilidad de huellas | T001, T003 |
| T005 | Inglés frontend/scripts/ejemplos | T001, T004 |
| T006 | Inglés comentarios de tests/fixtures y excepciones | T001, T005 |
| T007 | Defaults globales, catálogos, visual y conversación | T001, T006 |
| T008 | Trabajo inmutable por proyecto cero/B y snapshots del par | T001, T007 |
| T009 | Prompts ingleses: prosa visual y documentos/código en trabajo | T003, T004, T008 |
| T010 | Traducción UI/API/CLI completa y QA | T007, T008, T009 |
| T011 | Contrato CLI: capacidades, mínimos y procedencia | T001, T004 |
| T012 | Compatibilidad/diagnósticos implementados | T007, T011 |
| T013 | Matriz semántica diagramas/código/tests tras retirada | T008, T009, T010, T012, T019 |
| T014 | Documentación inglesa y README/primer uso | T002–T006, T010, T012, T013 |
| T015 | Metadatos/paquete candidato/CI/materiales de release | T002, T010, T012, T014, T019 |
| T016 | Primer uso desde clon limpio, paquete instalado y QA cero/B | T013, T014, T015, T019 |
| T017 | Matriz final, dictamen y expediente público | T001–T016, T019 |
| T018 | Cierre/archivo documental tras dictamen favorable | T017 |
| T019 | Retirada legacy/A con infraestructura compartida B conservada | T001, T002; antes de T003 |

Orden: T001 → T002 → T019 → T003–T018, una tarea cada vez. Las dependencias no autorizan ejecución paralela ni
lanzamiento de agentes. Si el inventario revela una tarea demasiado extensa, se divide antes de ejecutarla conservando
trazabilidad; defectos de producto encontrados en auditoría tienen tarea acotada y revisión antes de cerrar.

## Distribución y primer uso

Se conserva D051: operar desde el paquete instalado fuera del checkout. El servicio sigue local/individual,
loopback/sesión/CSRF, contención cooperativa; no se promete nube, multiusuario, aislamiento del SO ni plataformas
no probadas. La compatibilidad CLI no relaja por sí misma Python/Node/npm/uv; build/servicio/hijo se contrastan
por separado. No se fija todavía `1.0.0` ni se presume una nueva versión entregada.

T002 audita contenido rastreado e historial alcanzable, además de artefactos, con hallazgos saneados. Una
resolución que necesite reescribir/eliminar historia exige decisión aparte; traducir no retira atribuciones ni
altera snapshots. La auditoría privada identifica lo excluido; el candidato público lleva historia/docs nuevas
según D157, no necesita publicar esa historia interna para considerarse revisado. La licencia/titularidad debe
elegirse expresamente antes de incorporar términos al paquete.

T015 prepara metadatos/versión candidata, wheel/sdist con recursos, notas/manifiesto y CI sintética sin secretos
ni proveedores. Workflows propuestos no equivalen a ejecución remota. T016 presenta primero comandos, destinos,
instalaciones/red, cachés, servicios/puertos y limpieza para su autorización cuando corresponda; después comprueba
primer uso sin cachés privadas y repetición offline, paquete exacto, en/es y recuperación con proveedores falsos.
QA visual, integración de API e inferencia real se registran por separado. P010 es antecedente, no prueba del candidato.

## Cierre y autoridad de esta entrega

Los diez criterios de ROADMAP y trece globales de SPECIFICATION §10 ajustados por D155 tienen dictamen en T017. Licencia
pendiente, hallazgos de privacidad/paridad, guardias CLI retiradas o restos lingüísticos no justificados bloquean
la preparación pública. También bloquea conservar entrypoints operativos del soporte legacy/A retirado o romper
creación/incorporación B. Límites reales se declaran sin convertir dobles o documentación en validación real.

Una revisión favorable permite T018, archivo manual exacto. Publicación/apertura remota sigue como acción
posterior explícita sobre el expediente revisado: sin tag, push, Release, PyPI, cambio de visibilidad ni commit
por efecto de esta planificación. No se opera este checkout con el harness ni se amplían consentimientos P009.

Esta entrega solo planifica; sin implementación, auditoría exhaustiva de secretos/idiomas, suites del producto,
smokes, instalaciones, servicios ni proveedores. Comprobaciones documentales de parsers, enlaces, presupuestos,
conservación histórica y diff se registran debajo al terminar.

## Comprobación inicial de esta planificación (antes de D155)

- Parsers documentales puros: once fases, nueve criterios de P011, dieciocho tareas P011-T001–T018 en orden,
  todas pendientes y con objetivo, alcance, rutas, criterios, validación y entregables reconocidos; 154 decisiones
  con estado. Se comprueban las dependencias y la siguiente tarea sin lanzar el motor/supervisor.
- Presupuestos: STATE 8.875/24.576 bytes, base acumulada 6.548/12.288 y NEXT_STEPS 27.809/49.152.
- Veinticuatro enlaces/anclas nuevos únicos por documento comprobados contra destinos existentes; entregables
  futuros aparecen como rutas previstas, sin enlaces que pretendan que ya están entregados.
- Base acumulada, D001–D153 y su índice previo conservados por bytes; ROADMAP P001–P010 y candidatas previas
  intactos al retirar la nueva sección/fila. Sin cambios en `docs/archive/`, código, tests, scripts o ejemplos.
- Diff revisado y `git diff --check` correcto. Siete archivos Markdown nuevos/modificados, sin cambios de producto,
  esquema, dependencias o configuración. No se ejecutan unittest/pytest/Node/tipos/build/Alembic ni verificador del
  wheel: esta entrega solo planifica. Sin instalaciones, servicios, CLI reales, agentes, proveedores, smokes,
  commits, tags, push, publicación o cambio de visibilidad. Checks de tareas futuras siguen pendientes.

## Comprobación de la ampliación D155

- Parsers puros: once fases, diez criterios P011, diecinueve tareas pendientes con campos reconocidos y 155
  decisiones con estado. Dependencias ampliadas comprobadas: T001 → T002 → T019 → T003–T018, sin ciclos.
- Presupuestos actuales: STATE 9.394/24.576 bytes, base acumulada 6.548/12.288 y NEXT_STEPS 33.391/49.152.
- Cuarenta y seis enlaces/anclas locales comprobados por documento en el plan activo y las nuevas secciones.
  D001–D154, su índice previo, fases P001–P010 y base acumulada conservados respecto del plan anterior;
  la candidata A deja de estar vigente, conservando su propuesta/evidencia histórica en archivos anteriores.
- Diff revisado y `git diff --check` correcto; solo siete documentos Markdown nuevos/modificados en el conjunto
  de planificación. Sin cambios en código/tests, esquema, flujos implementados o archivos históricos; sin suites
  de producto, instalaciones, servicios, agentes/proveedores, smokes, commit/tag/push o publicación.
- La comprobación inicial anterior conserva resultados de dieciocho tareas; este registro acredita únicamente
  la ampliación documental. La retirada funcional sigue pendiente de T019.

## Verificación final de planificación y commit autorizado (D156)

- Parsers puros: once fases, diez criterios P011, diecinueve tareas pendientes con campos reconocidos y 156
  decisiones con estado. Orden/dependencias T001 → T002 → T019 → T003–T018 válidos; siguiente T001.
- Presupuestos: STATE 9.889/24.576 bytes, base acumulada 6.548/12.288 y NEXT_STEPS 34.151/49.152.
  Cincuenta y cuatro enlaces/anclas locales del plan activo y secciones nuevas comprobados.
- Base acumulada, D001–D153/índice previo y secciones P001–P010 conservados por bytes; sin cambios en archivos
  históricos, código, tests, scripts o ejemplos. D154/D155 conservan el contexto de las ampliaciones anteriores.
- Diff documental revisado y `git diff --check` correcto. Solo siete archivos Markdown en el commit autorizado,
  con mensaje inglés; planificación finalizada, no ejecución/cierre de P011. Modo continuo reservado para v0.2.0
  posterior a GitHub, sin cambiar la versión instalada ni añadir una fase sucesora.
- Sin unittest/pytest/Node/tipos/build/Alembic ni verificador del wheel: no cambia producto. Sin instalaciones,
  servicios, agentes/proveedores, smokes, tag, push, publicación o cambio de visibilidad. El commit documental
  sí está autorizado por esta petición; las verificaciones anteriores mantienen su contexto histórico.

## Comprobación de los ajustes D157/D158

- Parsers puros: once fases, diez criterios P011, diecinueve tareas pendientes con campos reconocidos y 158
  decisiones con estado. Orden/dependencias T001 → T002 → T019 → T003–T018 válidos; no se añaden tareas sin acotar.
- Presupuestos: STATE 10.792/24.576 bytes, base acumulada 6.548/12.288 y NEXT_STEPS 39.934/49.152.
  Cincuenta y siete enlaces/anclas locales comprobados por documento en el plan activo y secciones nuevas.
- D001–D156/índice previo, base acumulada, fases P001–P010 y horizonte v0.2.0 conservados por bytes respecto de
  `6174f51`; verificación de la separación visual/global/trabajo fijo y del corte inicial privado/público en tareas.
- Diff revisado y `git diff --check` correcto. Solo siete documentos del plan modificados; sin cambios de producto,
  modelos, flujos implementados, código/tests o archivos históricos. No se ejecutan suites, instalaciones,
  servicios, CLI reales, agentes/proveedores o smokes; sin stage, commit, copia/repositorio nuevo o publicación.
- Comprobaciones anteriores conservadas con su contexto; ninguna acredita idiomas implementados, ahorro de
  tokens, calidad lingüística de proveedores o existencia de un repositorio público. La implementación sigue pendiente.

## Confirmación y commit de los ajustes D157/D158

El usuario confirma las modificaciones documentales y pide su commit. Se revisan el diff y los checks puros:
once fases, diez criterios, diecinueve tareas pendientes, 158 decisiones, dependencias, 57 enlaces/anclas y
presupuestos dentro de límites; historial y código intactos. Los registros anteriores conservan su contexto.
Commit documental en inglés con los siete archivos del plan; sin suites de producto por no cambiar código,
sin implementación, nueva copia/repositorio, proveedores, servicios, push, tag o publicación.
