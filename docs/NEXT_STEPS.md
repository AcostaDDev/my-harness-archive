# P011 — Preparación para apertura pública en GitHub

Objetivo y criterios en [ROADMAP](ROADMAP.md#p011--preparación-para-apertura-pública-en-github).
Decisión: [D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github).
[Plan y alcance](phase/P011_PLAN_APERTURA_PUBLICA.md).

**Estado:** en ejecución desde el 2026-10-22. T001/T002/T019/T003–T010/T020–T022 completadas (D159–D172); ocho
tareas pendientes (T010 desglosó T021 y T021 desglosó T022 por HITL). Licencia/avisos, retirada legacy/A,
código/pruebas en inglés, preferencias globales e idioma de trabajo inmutable por proyecto con el par congelado por
job/intento; recetas v2; directiva al agente y documentos en W; interfaz React, diagnósticos HTTP propios y todos
los textos visibles del servicio/CLI en en/es (los técnicos ingleses, listados); QA visual conjunta sin autorizar.
**Planificación:** base finalizada en D156 y afinada por D155/D157/D158; contrato T001 disponible.
No equivale a fase completada.
**Siguiente:** P011-T011. Sin autorización de publicación.
P001–P010 siguen cerradas; la primera versión local mantiene el alcance de D151/D153.

## Restricciones compartidas

- Una tarea acotada cada vez, desarrollo manual, decisiones duraderas en DECISIONS y artefactos por tarea en
  `docs/phase/`. Los checks siguientes son previsiones; registrar base, comandos, resultados y omisiones al ejecutar.
- No operar este repositorio con el harness ni lanzar agentes, proveedores, smokes, instalaciones/red o servicios
  por efecto de esta planificación; cada operación que lo requiera conserva autorización explícita propia.
  Sin commits, tags, push, Releases, PyPI, cambio de visibilidad ni publicación automática.
- Fixtures sintéticos; sin credenciales, datos privados ni runs operativos. ReferenceProject solo se lee; no operar
  el hijo de P009 ni reutilizar sus consentimientos. No modificar configuración global.
- Preservar CAS, aceptación por contenido, permisos separados, locks, intención, cuarentena y recuperación.
  No reescribir archivos de fases cerradas, historiales, snapshots, catálogos ni recibos congelados.
- Inglés como base del código, comentarios/docstrings, prompts originales y documentación pública vigente;
  en los proyectos gestionados, defaults globales de idioma visual y de trabajo (en/es). El visual es global,
  mutable y gobierna UI/conversación/respuestas humanas, nunca un ajuste de proyecto. El de trabajo se elige
  al crear/incorporar, queda inmutable y gobierna documentación/código. Público my_harness: trabajo en inglés.
  Datos originales, logs externos y fixtures necesarios no se traducen por sustitución masiva.
- No renombrar protocolos, rutas canónicas, revisiones Alembic o claves persistidas por estética. Fuentes de
  recetas ligadas a huellas requieren el tratamiento T001 antes de tocarlas, incluso sus comentarios.
- Modelos/migraciones con DDBB-DIAGRAM; flujos con `docs/flows/`; API con OpenAPI/tipos en la misma tarea.
  Bibliotecas/formatos nuevos con decisión previa; incongruencias de diseño se resuelven antes de implementarse.
- D155 retira del alcance público la observación/importación del harness anterior y el Flujo A; solo se mantienen
  crear desde cero e incorporar un repositorio existente sin harness (Flujo B). T019 se ejecuta tras T002 y antes
  de T003 para no traducir ni empaquetar funcionalidades destinadas a eliminación. No ocultarlas dejando API/CLI activas.
- B y D095 conservan el aplazamiento D151; A queda fuera del soporte futuro por retirada, sin validarlo por ello.
  Licencia, versión y publicación son decisiones distintas; no se deducen por silencio.
  Los tests sintéticos no acreditan uso real. Ninguna tarea pendiente figura como capacidad entregada.
- D156 reserva el modo continuo `tareas → commits → check → cierre/archivo → planificación y ejecución de la
  siguiente fase` para v0.2.0 después de abrir el proyecto en GitHub, fuera de estas tareas. P011 mantiene
  cierre con READY y autorización propia, nueva fase sin tareas y confirmación del plan posterior.
  El commit D156 y los ajustes D157/D158 ya se realizaron. La petición actual autoriza ejecutar la siguiente
  tarea (T022) y su commit local en inglés, sin encadenar tareas ni publicar.
- D157 elige instantánea pública inicial revisada, con Git/documentación de partida nuevos y sin historia privada.
  Desde la apertura, código/decisiones/fases se desarrollan en el repositorio público, fuente principal; este
  checkout conserva su historia privada. No sincronizar dos desarrollos activos ni congelar para siempre `docs/` pública.

## P011-T001 — Inventario y contrato de la apertura pública

**Estado:** completada el 2026-10-22 (diseño, sin implementación de producto), D159.
**Evidencia:** [contrato](phase/P011-T001_CONTRATO_APERTURA.md) e
[inventario](phase/P011-T001_INVENTARIO.md): 688 archivos de `2730f54`, propietarios/excepciones,
persistencia/catálogos, par por job/turno, mapa de campos, compatibilidad de recetas/datos y corte inicial.
Contraste estático, cobertura de rutas, hashes, parsers, enlaces/presupuestos e integridad/diff correctos;
sin suites, procesos de agentes, proveedores, servicios, instalaciones o red.
**Objetivo:** Hacer implementables la traducción, los idiomas y la distribución sin romper compatibilidad.
**Alcance:** inventario por archivo de comentarios/docstrings/descripciones e identificadores españoles;
superficies UI/API/CLI/documentos/prompts; fuentes congeladas, hashes y lectores antiguos; brechas de primer uso
y mapa de retirada del harness anterior con separación de infraestructura compartida por B, configuración
global de idiomas y frontera de la instantánea inicial pública respecto de historia/documentación privadas.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Matriz por archivo/grupo con tarea propietaria, idioma actual, tratamiento y excepción justificada; revisar
  también español sin tildes. Separar texto de código, contenido de usuario y fixtures de compatibilidad.
- Contrato con defaults globales `ui_language` y `default_work_language` (en/es, inicial en); proyecto guarda solo
  `work_language` elegido al crear/incorporar e inmutable. UI/conversación/respuestas humanas usan el visual global
  actual; documentación y código usan trabajo. Cambiar defaults afecta solo a futuras altas, sin cascada a proyectos.
  Definir persistencia, fallback/formatos, compatibilidad/migración y controles API/UI de inmutabilidad.
- Congelar ambas lenguas al admitir cada job/turno; un cambio visual rige nuevas interacciones, sin mutar llamadas,
  reintentos o pendientes ya congelados. Mapear por campo la prosa humana y los artefactos técnicos en respuestas
  estructuradas; definir inyección controlada en contexto de instrucciones para ambos proveedores, sin inventar flags.
- Decidir la solución React/Python mínima con justificación y decisión de dependencias; no elegir `.po` por
  analogía con Django. Definir tratamiento de recetas cuyo texto entra en `fingerprint()`, prompts versionados,
  ADR históricas, anclas, parsers D088 y fixtures congelados antes de editarlos.
- Inventario de licencia, privacidad/historial Git, metadatos, cachés y setup; matriz inicial de diez criterios
  de salida, tareas/evidencias y decisiones pendientes, sin implantar producto ni dar auditorías por realizadas.
- Identificar entradas legacy/A, observadores, prompts, módulos/tablas propios y dependencias compartidas por B,
  recuperación, backups e historiales propios. Definir disposición no destructiva de datos/jobs antiguos para T019.
- Definir exportación inicial por lista permitida, docs públicas suficientes para forks/agentes sin referencias
  privadas rotas y continuidad pública posterior con decisiones/fases; no reescribir el historial de este checkout.

**Validación:** contraste estático de código, decisiones, parsers y enlaces; sin suites ni procesos de agentes.
**Entregables:** `docs/phase/P011-T001_CONTRATO_APERTURA.md`, inventario y decisión de diseño.

Contrato implementable para las siguientes tareas: [D159](DECISIONS.md#d159--p011-t001-contrato-de-idiomas-fuentes-y-corte-público).
T004 preserva v1 y prepara recetas v2; T007 usa SQLite/catálogos JSON sin nuevas dependencias; T008 incorpora
asociación inmutable para proyectos de registro/TOML, migración explícita y `local-config-6`; T009 aplica el mapa
V/W/T y generación v2. T019 extrae dependencias/guardias antes de retirar entradas y conserva datos/jobs antiguos
según el contrato. Los formatos/esquemas/flujos nuevos se implementan con su paridad en esas tareas.

## P011-T002 — Licencia y revisión del contenido publicable

**Estado:** completada el 2026-10-22 (licencia/revisión estática del origen), D160. **Depende de:** T001.
**Evidencia:** [informe](phase/P011-T002_CONTENIDO_PUBLICABLE.md),
[inventario por ruta/hash](phase/P011-T002_INVENTARIO.tsv), [dependencias](phase/P011-T002_DEPENDENCIAS.tsv)
y [script local](phase/P011-T002_audit.py). Usuario delega licencia/canal y confirma titular: MIT, David Acosta;
LICENSE/metadatos, CONTRIBUTING/SECURITY y avisos de 123 entradas runtime frontend. Escaneo de 690 archivos y
4.009 objetos alcanzables; sin credenciales reales identificadas en los patrones usados. Censo de 247 entradas,
19 términos de dependencias externas sin evidencia local declarados. Historia/evidencia privadas y paquetes
antiguos excluidos del futuro candidato; sin reescritura, copia o publicación. GitHub privado elegido, sin activar;
T015/T016 completan staging/avisos/assets y comprobación del candidato. Checks estáticos y consulta oficial
MIT/GitHub; sin suites, builds, servicios, proveedores o instalaciones. Siguiente T019.
**Objetivo:** Preparar derechos, atribuciones y contenido revisados para abrir el repositorio y sus artefactos.
**Alcance:** licencia/titularidad elegidas por el usuario, avisos de terceros, archivos rastreados e historial Git
alcanzable, soporte/contribución y reporte responsable; exclusión de estado y evidencias privadas.
**Rutas permitidas:** `LICENSE*`, `NOTICE*`, `CONTRIBUTING*`, `SECURITY*`, `.gitignore`, `.gitattributes`,
`pyproject.toml`, `frontend/package.json`, `docs/**`.
**Criterios de aceptación:**

- Registrar elección explícita de licencia y titularidad antes de escribir términos/metadatos. La autoridad de
  planificación no elige licencia; su ausencia es bloqueo identificado de esta tarea y de la preparación pública.
- Auditar contenido actual, historial alcanzable y archivos previstos de wheel/sdist; informe saneado con
  cobertura/límites, sin copiar secretos. `.gitignore` no constituye saneamiento del historial.
- Separar auditoría de origen privado y del árbol/historial público nuevos: inventario permitido para exportación,
  sin `.git`, archivo de fases, ADR internas, evidencias/rutas privadas o enlaces a ellas. No publicar el historial
  privado ni asumir que borrar `docs/` de un clon lo elimina. Documentación pública nueva conserva contexto técnico útil.
- No borrar ni reescribir historia automáticamente. Un hallazgo histórico necesita resolución explícita antes
  de declarar publicable el conjunto. Preservar atribuciones; documentos públicos ingleses sin contactos inventados.

**Validación:** revisión estática y escaneo local documentado sin red ni exposición de valores sensibles;
contenidos exactos del artefacto final se verifican en T016.
**Entregables:** `docs/phase/P011-T002_CONTENIDO_PUBLICABLE.md` y archivos públicos acordados.

## P011-T003 — Comentarios e identificadores en inglés: núcleo y perfiles

**Estado:** completada el 2026-10-22, D162. **Depende de:** T001, T019.
**Evidencia:** [inventario resuelto](phase/P011-T003_INGLES_NUCLEO.md): 35 archivos de `core/**`/`profiles/**`,
123 líneas de comentario y 121 docstrings en inglés; sin identificadores españoles. Literales intactos con
propietaria (T009/T010, alias bilingües, valores de perfil ligados a huellas). AST idéntico y suites registradas.
**Objetivo:** Que el núcleo mantenido tenga comentarios, docstrings y descripciones técnicas en inglés.
**Alcance:** `core/engine` y `profiles`; revisar variables, funciones/clases y descripciones de esquemas.
Mensajes visibles corresponden a T007/T010; prompts/documentos generados a T009.
**Rutas permitidas:** `src/harness_local/core/**`, `src/harness_local/profiles/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Inventario del grupo resuelto archivo a archivo, incluidos comentarios en línea y español sin tildes;
  renombrar identificadores españoles internos solo si existen, conservando referencias y comportamiento.
- Mantener protocolos, literales del parsing bilingüe y contenido de prueba; no modificar lógica, claves
  persistidas, catálogos congelados o rutas por traducción. Justificar cualquier refactor imprescindible por separado.

**Validación:** inventario/diff y pruebas existentes pertinentes del núcleo; sin tests que solo repitan comentarios.
**Entregables:** `docs/phase/P011-T003_INGLES_NUCLEO.md` e inventario actualizado.

## P011-T004 — Comentarios e identificadores en inglés: backend y recetas

**Estado:** completada el 2026-10-22, D163. **Depende de:** T001, T003.
**Evidencia:** [inventario resuelto](phase/P011-T004_INGLES_BACKEND.md): 94 archivos, 223 líneas de comentario,
318 docstrings y 84 descripciones OpenAPI en inglés (OpenAPI/tipos regenerados); 555 literales residuales con
propietaria. v1 por bytes/huellas fijadas en test; `django_2.py`/`typescript_web_2.py` sin cablear hasta T008 (HITL).
**Objetivo:** Completar el inglés del código backend sin alterar identidades persistidas.
**Alcance:** adaptadores, servicios, API, almacenamiento, CLI, migraciones y recetas según T001.
**Rutas permitidas:** `src/harness_local/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Comentarios/docstrings/nombres internos del inventario revisados y traducidos; conservar revisiones Alembic,
  formatos y códigos externos. Inventariar mensajes visibles para T010, sin mezclarlos con comentarios.
- Resolver fuentes ligadas a huellas mediante el contrato aprobado; conservar lectura/recuperación de recibos
  antiguos. No editar una receta congelada para aparentar cobertura ni invalidar entornos por cambios cosméticos.
- Cambios imprescindibles de formato/modelos/flujos con decisión, regresiones y paridad en la misma entrega;
  desglosar trabajo adicional antes de sobrepasar el contrato de compatibilidad.

**Validación:** revisión lingüística/diff, regresiones de recetas/recibos/snapshots; pytest/unittest pertinentes y
Alembic temporal si cambia esquema.
**Entregables:** `docs/phase/P011-T004_INGLES_BACKEND.md` e inventario actualizado.

## P011-T005 — Comentarios en inglés: frontend, scripts y ejemplos

**Estado:** completada el 2026-10-23, D164. **Depende de:** T001, T004.
**Evidencia:** [inventario resuelto](phase/P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md): 195 líneas de comentario
TS/TSX y 17 CSS en inglés con tokens/reglas idénticos; 1240 literales visibles candidatos para T010. Por HITL,
mensajes de scripts en inglés salvo tres acoplados a salida del producto (nota para T010) y descripción del
paquete nueva. Ejemplos vigentes en inglés con datos TOML equivalentes; guiones históricos E6 intactos.
**Objetivo:** Completar los comentarios/descripciones técnicas de cliente y herramientas mantenidas.
**Alcance:** TS/TSX, CSS/HTML, Python/shell, TOML, ejemplos vigentes y metadatos descriptivos.
**Rutas permitidas:** `frontend/**`, `scripts/**`, `examples/**`, `pyproject.toml`, `.gitignore`,
`.gitattributes`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Revisión por archivo de comentarios/docstrings/nombres; cadenas visibles inventariadas para catálogos.
  No editar a mano OpenAPI generado ni cambiar comandos, locks o autorizaciones por traducción.
- Ejemplos vigentes en inglés con datos sintéticos; guiones históricos identificados sin reescribir snapshots
  ni presentarlos como instrucciones actuales. Descripción del paquete coherente con su estado real.

**Validación:** inventario/diff, Node/tipos/build y pruebas de ejemplos/scripts según archivos afectados.
**Entregables:** `docs/phase/P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md` e inventario actualizado.

## P011-T006 — Comentarios en inglés: tests y fixtures

**Estado:** completada el 2026-10-23, D165. **Depende de:** T001, T005.
**Evidencia:** [inventario resuelto](phase/P011-T006_INGLES_PRUEBAS.md): 294 comentarios y 91 docstrings Python
en 49 archivos con AST idéntico; comentarios y cinco nombres de test frontend; un nombre de test renombrado y
cinco textos propios de pruebas traducidos. Expectativas, datos bilingües/sintéticos y fixtures intactos; por
HITL, README de fixtures en inglés. Suites offline con los mismos totales que T005.
**Objetivo:** Mantener pruebas comprensibles en inglés sin perder cobertura bilingüe e histórica.
**Alcance:** comentarios/docstrings/descripciones y nombres internos de tests/fixtures sintéticos.
**Rutas permitidas:** `tests/**`, `frontend/tests/**`, `docs/**`.
**Criterios de aceptación:**

- Inventario del grupo resuelto; traducir comentarios y nombres internos españoles si existen, conservando
  parametrizaciones, expectativas, datos bilingües, hashes y snapshots que prueban comportamiento anterior.
- Excepciones con ruta/motivo; no traducir strings indiscriminadamente ni debilitar expectativas. Las pruebas
  funcionales de nuevas capacidades pertenecen a sus tareas, sin tests que solo busquen comentarios.

**Validación:** pytest/unittest/Node sobre pruebas afectadas y revisión del inventario/excepciones.
**Entregables:** `docs/phase/P011-T006_INGLES_PRUEBAS.md` e inventario actualizado.

## P011-T007 — Infraestructura de idiomas para interfaz y mensajes

**Estado:** completada el 2026-10-23, D166. **Depende de:** T001, T006.
**Evidencia:** [entrega](phase/P011-T007_INFRAESTRUCTURA_IDIOMAS.md): `0024` con preferencias singleton (CAS,
eventos, idempotencia), `GET/PUT /api/managed/preferences`, visual `ui-language-1` sellado en cada job y heredado por
continuaciones (HITL: el par completo es de T008, la directiva de T009). Catálogos JSON en/es Python/React sin
dependencias, página `/preferences`, shell/sesión traducidos (HITL), `--ui-language`. Suites offline en verde.
**Objetivo:** Añadir ajustes globales de idiomas, catálogos en/es y conversación en el idioma visual.
**Alcance:** solución T001, ajustes/defaults globales, selector accesible, persistencia/fallback/formatos,
propagación de lengua de respuesta a nuevas interacciones y mensajes API/CLI propios.
**Rutas permitidas:** `frontend/**`, `src/harness_local/**`, `tests/**`, `pyproject.toml`, `uv.lock`, `docs/**`.
**Criterios de aceptación:**

- Ajustes globales explícitos: idioma visual mutable y default de idioma de trabajo para nuevas altas, ambos
  en/es e inicialmente en. Cambiar default no cambia proyectos existentes. Sin idioma visual guardado en el proyecto;
  definir persistencia por operador/sesión local y precedencias sin modificar TOML/configuración global del equipo.
- UI/catálogos, conversación, preguntas HITL y respuestas humanas usan visual; cambios visuales rigen nuevos
  jobs/turnos. Invocaciones y pendientes conservan su par congelado; no reencolar ni invalidar aceptaciones por cambiar UI.
- Claves estables, interpolación segura y formatos accesibles, sin concatenación de frases traducidas; mecanismo
  explícito de locale para mensajes propios API/CLI, preservando códigos, estados, estructura y evidencia original.
- Fallback para locale inválido, claves/almacenamiento ausentes; cobertura de catálogos y dependencias con decisión/
  locks. Logs externos, contenido libre y mensajes históricos mantienen original. Paridad si cambia almacenamiento/API.

**Validación:** preferencias/defaults/fallback, cambios entre turnos y aislamiento de jobs pendientes, límites API;
Node/tipos/build, pytest pertinente, Alembic temporal y OpenAPI regenerado si cambia contrato/esquema.
**Entregables:** `docs/phase/P011-T007_INFRAESTRUCTURA_IDIOMAS.md`, decisión y catálogos iniciales.

## P011-T008 — Idioma de trabajo inmutable por proyecto y contexto congelado

**Estado:** completada el 2026-10-23, D167. **Depende de:** T001, T007.
**Evidencia:** [entrega](phase/P011-T008_IDIOMA_PROYECTO.md): `0025` con una fila inmutable por raíz, alta B/creación
con valor sellado en el hash (default como procedencia), 409 `work_language_immutable`/`work_language_required`,
`local-config-6` asociado al arrancar (HITL), confirmación explícita con API/UI mínima (HITL) y `language-context-1`
por job/intento. Recetas v2 → T020 (HITL). Suites offline en verde; sin servicios, QA de navegador ni proveedores.
**Objetivo:** Fijar en/es al crear/incorporar para documentación/código del proyecto, separado de la conversación.
**Alcance:** default global, registro/creación/incorporación B, lectura de ajustes, persistencia/API y contexto
de jobs/intentos. No se añade un selector visual por proyecto ni se permite cambiar trabajo en sus ajustes.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- Selección explícita y vista previa al crear/incorporar, inicializada desde default global (en de fábrica), con
  procedencia persistida y ligada a confirmación por hash. Tras confirmar el alta es inmutable también por API/
  configuración/importaciones; ajustes existentes solo muestran el valor. Nuevos defaults no lo sobrescriben.
- Documentación/código/comentarios nuevos siguen trabajo; UI/conversación usan visual global. Leer fuentes previas
  en otro idioma sigue permitido, sin traducirlas ni renombrar interfaces automáticamente. No traducir keywords,
  comandos, formatos, rutas o códigos técnicos, ni confundirlo con idioma funcional de la app hija.
- Congelar trabajo y lengua visual de respuesta por job/turno, con procedencia en intentos/prompts; cambios globales
  posteriores no mutan pendientes/reintentos ni historia. Configuraciones/proyectos antiguos conservan lectura y
  semántica; migrar el valor explícitamente sin deducirlo por heurísticas ni retraducir archivos existentes.
- CAS/idempotencia/concurrencia, recuperación/backup y rechazo de cambios posteriores probados; paridad de
  DDBB-DIAGRAM/flujos/API/tipos. El idioma no amplía permisos ni activa escrituras/instalaciones por sí mismo.

**Validación:** cuatro combinaciones visual/trabajo en/es, inmutabilidad por UI/API, defaults antiguos/nuevos,
concurrencia y reinicio/snapshots; pytest, Alembic temporal,
OpenAPI/tipos y pruebas del cliente pertinentes.
**Entregables:** `docs/phase/P011-T008_IDIOMA_PROYECTO.md` y contratos/documentación actualizados.

## P011-T009 — Prompts ingleses y documentos generados en la lengua elegida

**Estado:** completada el 2026-10-23, D169. **Depende de:** T003, T004, T008, T020.
**Evidencia:** [entrega](phase/P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md): `language-directive-1` sellada en el snapshot
desde el par del job (V/W/T por rol, ambos proveedores por stdin; par inválido → parada antes de invocar); plantillas
inglesas sin marcadores españoles; documentos generados en el idioma de trabajo (español histórico byte a byte).
HITL: todo en T009 y commits técnicos sin cambios. Suites offline en verde; sin proveedores ni QA de navegador.
**Objetivo:** Prompts originales ingleses con prosa humana en idioma visual y documentación/código en trabajo fijo.
**Alcance:** plantillas/catálogos/esquemas, esqueletos y bloques D088, chat, planificación, revisión, definición,
incorporación B, resúmenes, check/cierre/archivo e instrucciones de proyecto; sin prompts para el Flujo A retirado.
**Rutas permitidas:** `src/harness_local/**`, `tests/**`, `frontend/tests/**`, `docs/**`.
**Criterios de aceptación:**

- Prompts originales ingleses y personalizados editables; directivas del motor tipadas para ambos proveedores:
  `Respond to the user in {ui_language}. Write project documentation and code in {work_language}.`
  Usar en/es validados y canal de instrucciones soportado por cada adaptador, sin prometer un system prompt nativo
  inexistente ni cambiar permisos. Congelar directivas/valores/identidad; no inyectar nuevos valores en un intento activo.
- Mapear campos: respuestas/resúmenes dirigidos al usuario y preguntas HITL en visual; borradores Markdown,
  contratos/planes/ADR, código/comentarios y contenido técnico persistido en trabajo. Una respuesta puede contener
  prosa española y documentos ingleses. JSON/estados/keys técnicos permanecen estables; snapshot auditable del par.
- Generación determinista en/es y parsers compatibles, sin traducir rutas, marcadores, JSON, comandos o códigos;
  no implica hacer bilingüe la app hija. Mantener único registro ADR y presupuestos D088.
- Trabajo inmutable; cambiar visual afecta solo a nuevas interacciones, no archivos/contenido previo ni versiones
  personalizadas congeladas. Lectura/reanudación antigua intacta; recorridos falsos combinan las cuatro parejas
  visual/trabajo, definición → tarea → cierre y chat. No prometer reducción fija de tokens por elegir inglés.

**Validación:** regresiones de plantillas, hashes/codec, parsers y flujos sintéticos; pytest/unittest pertinentes.
No anunciar agentes falsos como calidad lingüística probada con proveedores.
**Entregables:** `docs/phase/P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md` y plantillas nuevas.

## P011-T010 — Traducción completa de interfaz, mensajes y accesibilidad

**Estado:** completada el 2026-10-23, D170. **Depende de:** T007, T008, T009.
**Evidencia:** [entrega](phase/P011-T010_TRADUCCION_PRODUCTO.md): por HITL, T010 = interfaz React completa y
diagnósticos HTTP propios de `api/*`; servicio/CLI → T021 y QA visual conjunta tras T021. 1417 claves en/es tipadas,
plurales, `rich` sin fragmentos traducidos, formatos por idioma, visor Markdown con códigos rellenados por
`textContent`, 24 diagnósticos HTTP nuevos en el visual guardado y línea técnica fija `access key at`. Node 93/93,
tipos/build y suites offline en verde; sin servicios, navegador ni proveedores.
**Objetivo:** Completar en/es en todas las superficies propias visibles al usuario.
**Alcance:** sesión, registro/ajustes, preparación, fases, tareas/runs, docs/chat/estadísticas, incorporación B, errores,
validaciones, ayuda CLI, textos ARIA, tooltips, estados vacíos y confirmaciones.
**Rutas permitidas:** `frontend/**`, `src/harness_local/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- Inventario cubierto y claves en ambos catálogos; sin restos involuntarios del otro idioma, con excepciones
  explícitas de código/evidencia/terceros. Mensajes propios API/CLI traducidos sin cambiar significado o protocolo.
- Ajustes globales de visual/default trabajo y selección única de trabajo en el alta cubiertos; proyectos solo
  muestran trabajo inmutable. Con visual es/trabajo en, interfaz/respuesta/preguntas en español y documentación/
  código en inglés. Cambiar visual en el chat afecta próximas respuestas, sin modificar historial o jobs pendientes.
- No traducir Markdown libre ni logs automáticamente. QA en/es, claro/oscuro y escritorio/móvil: longitud,
  formatos/plurales, teclado/accesibilidad, errores y confirmaciones; entorno sintético autorizado y saneado.

**Validación:** cobertura de catálogos y pruebas funcionales, Node/tipos/build y pytest pertinente; QA visual
con datos/API sintéticos si se autoriza el navegador/servicio necesarios.
**Entregables:** `docs/phase/P011-T010_TRADUCCION_PRODUCTO.md`, catálogos y matriz QA.
**Nota (D164, resuelta por HITL en D170):** la línea de la clave es salida técnica fija en inglés y ambos scripts la
leen así (rutas ampliadas a `scripts/**` para ese cambio); `módulo:atributo` y `Esquema SQLite` pasan a T021.

## P011-T011 — Contrato de compatibilidad de CLI por capacidades

**Estado:** pendiente. **Depende de:** T001, T004.
**Objetivo:** Definir una política ampliable por capacidades para Codex y Claude Code.
**Alcance:** proveedor/rol, baselines D122/D124, mínimos/familias, flags/streams/esquemas, permisos/confianza,
memoria, autenticación/entorno, cancelación y diagnóstico.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Matriz de capacidades obligatorias con evidencia de código/documentación oficial; separar version/help,
  comportamiento e inferencia real. Fijar mínimos con evidencia, sin prometer todas las versiones futuras.
  D160 excluye ayudas reales de CLI del corte: sustituir cobertura con fixtures sintéticos en T006/T012,
  conservando los originales privados y sin presentarlos como redistribuibles bajo el MIT del proyecto.
- Una CLI posterior compatible no se rechaza solo por faltar en una lista exacta; inferiores/incompatibles
  bloquean antes del efecto. Distinguir verificada/candidata, aceptación de candidatas y semántica que help no prueba.
- Congelar versión observada/capacidades/política por intento; conservar jobs antiguos, cuarentena, confianza y
  ausencia de fallback/retry. Si no se acredita una guardia esencial, bloquear con diagnóstico; no reemplazarla por aviso.

**Validación:** revisión de fuentes/precedentes y diseño; sin CLI reales ni proveedores. Proponer una tarea
operativa separada si hace falta evidencia real para el soporte anunciado.
**Entregables:** `docs/phase/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md` y decisión.

## P011-T012 — Implementar compatibilidad y diagnósticos de CLI

**Estado:** pendiente. **Depende de:** T007, T011.
**Objetivo:** Admitir versiones posteriores compatibles sin editar allowlists por cada patch.
**Alcance:** configuración/presets, preflight, adaptadores/parsers, diagnósticos UI/CLI y soporte documentado.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- Contrato T011 en ambos proveedores/roles, conservando baselines previos y coherencia versión configurada/real;
  diagnóstico ligado al binario/capacidades actuales, sin cachear a ciegas ni modificar configuración global.
- Fixtures de versión posterior compatible aceptada y de inferior/no parseable/incompatible rechazada; flags,
  esquema/streams, permisos/read-only/writer, confianza, memoria y cancelación. Exit code cero no sustituye guardias.
- Runs congelan procedencia/política; cambios de binario/reinicio no reutilizan contratos sin validar. Diagnóstico
  en/es accionable, sin downgrade/fallback/retry; evidencia sintética distinguida de CLI/proveedores reales.

**Validación:** pytest de configuración/adaptadores/streams/recuperación/API, Node/tipos/build si procede;
CLI falsas. Caracterización o inferencia real requiere tarea y autorización propias antes de ejecutarse.
**Entregables:** `docs/phase/P011-T012_COMPATIBILIDAD_CLI.md` y matriz implementada.

## P011-T013 — Auditoría semántica de diagramas y flujos

**Estado:** pendiente. **Depende de:** T008, T009, T010, T012, T019.
**Objetivo:** Que cada diagrama vigente refleje comportamiento final, fallos y límites del software.
**Alcance:** inventario de flujos tras T019, nuevos flujos idioma/CLI si proceden, ARCHITECTURE y DDBB-DIAGRAM;
código, rutas API, permisos, estados, recuperación y persistencia.
**Rutas permitidas:** `docs/**`, `tests/**`, `frontend/tests/**`.
**Criterios de aceptación:**

- Matriz diagrama/nodo/transición relevante → código/tests para éxito, bloqueos, caída/reinicio, cancelación y
  confirmaciones. Revisar también efectos implementados omitidos en dibujos; separar piloto histórico y producto.
- Flujos legacy/A no se conservan como capacidades vigentes; la documentación histórica conserva su contexto.
  Verificar los dos accesos finales (desde cero/B) y la infraestructura compartida conservada, sin reintroducir rutas retiradas.
- Corregir documentación inglesa y relaciones/tablas frente al metadata; validar/renderizar Mermaid no prueba
  paridad semántica. Diagramas archivados intactos y nuevos tests solo para huecos de comportamiento relevantes.
- Discrepancia código/diseño identificada y resuelta antes de cambiar diseño; defectos de producto a tarea
  acotada, sin alterar comportamiento para que encaje en un dibujo ni dar la auditoría por cerrada con hallazgos.

**Validación:** revisión trazable, render Mermaid con herramientas disponibles, metadata y pruebas pertinentes;
no ejecutar el harness sobre este checkout.
**Entregables:** `docs/phase/P011-T013_MATRIZ_DIAGRAMAS.md`, diagramas y resolución de incidencias.

## P011-T014 — Documentación inglesa y README completo de primer uso

**Estado:** pendiente. **Depende de:** T002–T006, T010, T012, T013.
**Objetivo:** Instalar y probar desde GitHub sin conocimiento previo ni entorno privado del autor.
**Alcance:** README inglés y entrada española, documentación viva/instrucciones/ejemplos, requisitos, operación,
soporte, idiomas, compatibilidad y límites; excluye originales históricos congelados.
**Rutas permitidas:** `README*`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING*`, `SECURITY*`,
`docs/**`, `examples/**`.
**Criterios de aceptación:**

- Documentación pública vigente inglesa, navegación española útil, enlaces/anclas y parsers/presupuestos D088
  correctos. Baseline pública nueva en inglés con contexto técnico, arquitectura y decisiones iniciales suficientes
  para forks/agentes; sin copiar ADR/fases privadas ni dejar enlaces/DNNN internos imprescindibles sin explicación.
  Originales privados intactos; desde la apertura, nuevas decisiones/fases y docs se versionan en el repositorio público.
- README cubre propósito/estado/licencia, requisitos servicio/build/hijo, autenticación, primer clon sin cachés,
  instalación de paquete, ejemplo mínimo de un proveedor, TOML v5, sesión, preparación y primer COMMITTED.
- Presentar exactamente dos entradas: crear un proyecto nuevo o incorporar código existente sin harness;
  sin visor, observación, importación ni normalización del harness anterior en guías/opciones públicas.
- Idiomas, CLI verificadas/candidatas, red/cachés/consumo y confirmaciones; reinicio/actualización/backup de
  consulta, diagnóstico, desinstalación conservando datos y contribución. Rutas sintéticas/placeholders claros.
- Explicar visual global para UI/conversación, default global de trabajo y trabajo en/es inmutable al alta;
  ejemplo español visual/inglés técnico para ambos proveedores. La documentación pública de my_harness usa trabajo en.
- Separar desarrollo y uso instalado, sin modelos/rutas privadas ni archivos locales no distribuidos; instrucciones
  solo sobre capacidades entregadas. Declarar plataformas/evidencia pendientes; ensayo efectivo en T016.

**Validación:** parsers/enlaces, comandos contrastados con scripts/CLI y ejemplos cargados con rutas sintéticas
sin procesos; revisión inglesa/española. No anunciar aún un primer uso ensayado.
**Entregables:** `docs/phase/P011-T014_DOCUMENTACION_PUBLICA.md`, README y guías/ejemplos.

## P011-T015 — Paquete público, metadatos y checks reproducibles en GitHub

**Estado:** pendiente. **Depende de:** T002, T010, T012, T014, T019.
**Objetivo:** Preparar wheel/sdist y automatización de validación distribuibles sin secretos ni proveedores.
**Alcance:** licencia/metadatos/versión candidata, UI/migraciones/catálogos/prompts, build y CI/materiales de release.
**Rutas permitidas:** `pyproject.toml`, `uv.lock`, `frontend/**`, `scripts/**`, `tests/**`, `.github/**`,
`LICENSE*`, `NOTICE*`, `CHANGELOG*`, `docs/**`.
**Criterios de aceptación:**

- Registrar versión/política de cambios sin asumir `1.0.0`; coherencia Python/UI/locks/licencia y contenido
  permitido del paquete, sin `.local`, runs, credenciales o cachés privadas. Wheel/sdist con recursos completos.
  Integrar LICENSE/NOTICE en staging y comprobar metadatos, avisos de bundles/fuentes y las 19 entradas externas
  sin términos de versión exacta en evidencia local T002 cuando se redistribuyan; no reutilizar `dist/` antiguo.
  Respetar la reserva de v0.2.0 para una entrega posterior a la apertura inicial de GitHub (D156), sin atribuirle
  a esta fase el modo continuo aplazado ni cambiar versión por efecto de planificar.
- Sin componentes/entrypoints/prompts exclusivamente legacy/A en el paquete público; compatibilidad interna
  estrictamente necesaria para B, migraciones e historia propia documentada, sin exponer un tercer modo de proyecto.
- Construcción desde clon limpio con preparación explícita de cachés; distinguir requisitos build/servicio/hijo
  y plataforma probada. CI sintética sin login/secretos/proveedores ni publicación automática, permisos explícitos.
- Notas, hashes/manifiesto y procedimiento manual GitHub revisables. Escribir workflows no ejecuta jobs remotos,
  crea tags/Releases, cambia visibilidad ni publica. PyPI y publicación automática fuera de alcance.
  Incluir activación/verificación de reportes privados GitHub elegidos en D160 antes de abrir; SECURITY no activa
  el canal. Comprobación operativa remota solo bajo la autorización propia de apertura.
- Preparar instantánea inicial saneada con docs públicas nuevas y raíz Git independiente, sin `.git`/objetos/ramas/
  tags ni historia privada. Registrar correspondencia origen/candidato de forma privada y comparar código aprobado,
  recursos y dependencias. Después de abrir, el repositorio público será fuente principal de código/docs; no espejo
  que sobrescriba contribuciones ni dos fuentes activas. Crear repositorio/commit público solo con autorización propia.

**Validación:** inspección de contenidos/metadatos/workflows; construir/verificar solo con alcance de ejecución
autorizado. CI remota pendiente si no se ejecutó, sin equivaler validación local y remota.
**Entregables:** `docs/phase/P011-T015_PAQUETE_PUBLICO.md`, metadatos, workflows y materiales de release.

## P011-T016 — Primer uso reproducible y QA del paquete candidato

**Estado:** pendiente. **Depende de:** T013, T014, T015, T019.
**Objetivo:** Acreditar instrucciones y paquete exacto sin las cachés ni configuración privadas del autor.
**Alcance:** propuesta de ensayo, clon/cachés/venv/estado sintéticos, wheel instalado, configuración mínima,
recorridos bilingües y recuperación/migración/backup.
**Rutas permitidas:** `scripts/**`, `tests/**`, `frontend/tests/**`, `docs/**`.
**Criterios de aceptación:**

- Propuesta previa concreta carpetas/comandos, instalaciones/red, servicios/puertos y limpieza; ejecutar tras
  autorización del alcance que la requiera. No usar credenciales/configuración personal ni proveedores reales.
- Clon sin cachés privadas: primera descarga explícita y repetición offline cuando aplique; instalar fuera del
  checkout, comprobar assets/catálogos/sesión y recorrer hasta COMMITTED/cierre en/es con agentes falsos.
- Cambio de idioma sin mutar evidencia, CLI falsas posteriores/negativas, reinicio/migración/backup de consulta;
  QA navegador del candidato exacto con API sintética/integrada según autorización y procedencia separadas.
- Probar las cuatro combinaciones visual/trabajo, defaults que no cambian proyectos, rechazo de modificar trabajo
  tras el alta y cambio visual entre turnos con llamadas activas/pendientes congeladas; fuentes B mixtas legibles.
- Ensayo desde la instantánea pública permitida, sin historial/docs privados ni referencias imprescindibles ausentes;
  código/recursos equivalentes al candidato aprobado, documentación nueva útil para forks/agentes y build autónomo.
- Ambos accesos finales probados (desde cero/B); rutas/comandos/observación legacy/A ausentes o rechazados sin
  ejecutar efectos, sin activar observadores al arrancar ni al consultar respaldos de instalaciones anteriores.
- Base/versión/hashes, capturas saneadas, comandos/resultados/skips y servicios detenidos registrados; corregir
  hallazgos antes de T017. Dobles no acreditan login/inferencia/calidad lingüística o semántica de CLI reales.

**Validación:** suites finales pertinentes de AGENTS, Alembic temporal, wheel/sdist y QA autorizada; operaciones
reales necesarias exigen tarea/consentimiento propios antes del dictamen. No ampliar ensayos sin motivo.
**Entregables:** `docs/phase/P011-T016_PRIMER_USO_QA.md`, matriz y evidencia saneada del candidato.

## P011-T017 — Revisión de salida y expediente para apertura pública

**Estado:** pendiente. **Depende de:** T001–T016, T019.
**Objetivo:** Dictaminar preparación pública con evidencia trazable del candidato final.
**Alcance:** diez criterios P011, trece globales ajustados por la retirada D155, inventario/excepciones lingüísticas,
licencia/privacidad, compatibilidad/soporte, diagramas/docs, artefactos y CI.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Matriz por criterio con evidencia, base/versión/hashes, procedencia, omisiones y bloqueos; el dictamen P010 no
  sustituye verificar P011. Sin tareas obligatorias, licencia o hallazgos de privacidad/paridad pendientes.
- Retirada legacy/A completa en UI/API/CLI, arranque, docs y paquete, y cero/B conservados. Criterios globales
  1/11/13 actualizados con trazabilidad, sin exigir funcionalidad eliminada ni reescribir su matriz histórica P010.
- Excepciones históricas y CLI/plataformas no verificadas declaradas sin soporte universal. Hallazgos a tarea
  acotada y revisión afectada; dictamen favorable antes de T018.
- Expediente con contenido publicable, notas/artefactos/hashes y acciones remotas exactas propuestas; recomendar
  abrir no ejecuta push, tag, Release o cambio de visibilidad.
- Frontera inicial privada/pública y continuidad pública de código/decisiones/fases documentadas; idiomas conforme
  a D158 (visual global, defaults globales y trabajo inmutable). No exigir publicar ADR/historia privadas para cumplir.

**Validación:** contraste documental con evidencia T016 y diff final, enlaces/versiones/hashes; sin repetir
suites ya válidas salvo cambios/fallos que lo justifiquen ni lanzar nuevas operaciones reales.
**Entregables:** `docs/phase/P011_REVIEW.md`, matriz final y expediente público.

## P011-T018 — Cierre documental de P011

**Estado:** pendiente. **Depende de:** T017 con dictamen favorable.
**Objetivo:** Archivar la preparación pública conservando evidencia y separándola de publicar.
**Alcance:** resumen/revisión/cierre, archivo y actualización de STATE/NEXT_STEPS/ROADMAP/DECISIONS.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Originales conservados por bytes/manifiesto, resumen con capacidades, checks, alcance real y límites;
  sin reescribir fases/snapshots anteriores. Documentos vivos e índice al día, sin inventar sucesora.
- Cierre manual sin registrar/ejecutar este checkout, commit/tag, push, Release o publicación. Apertura remota
  posterior exige instrucción explícita sobre el expediente revisado.

**Validación:** parsers/enlaces/presupuestos, manifiesto/hashes y diff documental; sin suites si no cambia código.
**Entregables:** `docs/archive/phase-011/` con resumen, revisión, originales y registro de cierre.

## P011-T019 — Retirar el harness anterior y conservar solo creación e incorporación

**Estado:** completada el 2026-10-22, D161. **Depende de:** T001, T002. **Orden:** antes de T003; numeración previa conservada.
**Evidencia:** [informe e inventario de dependencias](phase/P011-T019_RETIRADA_LEGACY.md): retirada de UI/API/CLI,
observadores/SSE, activación y A; extracción de infraestructura B, compatibilidad de datos y cuarentena de jobs.
Checks y omisiones registrados; sin proveedores, operación sobre este checkout ni publicación.
**Objetivo:** Eliminar las funcionalidades del harness anterior y mantener solo proyectos gestionados por my_harness.
**Alcance:** visor `/legacy`, API/CLI de importación/consulta/observación legacy, SSE/feeds/watchers correspondientes,
activación/migración desde el motor anterior y normalización/importación documental A; navegación, configuración,
prompts, código/tests/fixtures exclusivos, documentación y distribución. Se mantienen crear desde cero e incorporar
un repositorio existente sin harness (B), además de su seguimiento normal dentro de my_harness.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `scripts/**`, `examples/**`,
`README*`, `pyproject.toml`, `uv.lock`, `docs/**`.
**Criterios de aceptación:**

- Retirar funcionalidad, no solo enlaces: sin pantallas/rutas de navegación, endpoints/contratos activos, comandos
  `legacy-import`/`legacy-summary`, observadores/SSE legacy, activación del motor anterior, conversación
  `project_import`/Flujo A ni sus prompts propios. Rutas/comandos antiguos no ejecutan efectos ni redirigen a A;
  diagnóstico/rechazo de retirada definido, sin modo oculto ni feature flag que reactive el soporte.
- Conservar de extremo a extremo los dos accesos: cero → definición/preparación/tareas y repositorio existente
  sin harness → inventario/incorporación B/perfil/documentos/primer run; ambos se monitorizan como gestionados.
  Registro/reapertura de proyectos ya gestionados siguen siendo operaciones normales, no un tercer tipo de alta.
- Inventario de dependencias antes de borrar: B comparte `project_imports`, `purpose = import_commit`, repositorios
  y escritor Git con A. Conservar/reubicar código común necesario por comportamiento, sin eliminarlo por el nombre
  `legacy`/`import`. Distinguir compatibilidad de runs propios/codec/configuración de soporte al harness anterior.
- Datos, historiales/snapshots y revisiones Alembic existentes intactos; no eliminar tablas/filas o archivos de usuario
  automáticamente. Precisar lectura/migración/backup y resolución de jobs legacy pendientes sin ejecutarlos ni
  reinterpretarlos como B. La compatibilidad interna necesaria no vuelve a exponer el visor/importación anterior.
- Retirar módulos/tests/fixtures únicamente exclusivos y sustituir cobertura por pruebas significativas de ausencia,
  arranque sin observadores y regresión cero/B, CAS/permisos, recuperación e historial propio. No declarar retirada
  completa si permanece un entrypoint operativo del harness anterior o un componente exclusivo en el paquete.
- Actualizar SPECIFICATION F03/F05 y §10 (criterios 1/11/13: idempotencia cero/B y observación gestionada por cursor),
  modos de proyecto, README/ejemplos, ARCHITECTURE, flujos y OpenAPI/tipos; DDBB-DIAGRAM si cambia metadata.
  Conservar archivos/decisiones históricos, sin anunciar retirada implementada antes de esta entrega.

**Validación:** pytest/unittest y Node pertinentes, comprobación de rutas/comandos/OpenAPI y wheel manifest,
tipos/build; Alembic temporal si procede. Fixtures sintéticos de cero/B e instalación anterior, sin operar el
harness sobre este checkout ni tocar datos reales. Ensayo del paquete exacto se acredita después en T016.
**Entregables:** `docs/phase/P011-T019_RETIRADA_LEGACY.md`, inventario de dependencias y decisiones de compatibilidad.

## P011-T020 — Recetas v2 cableadas por idioma de trabajo

**Estado:** completada el 2026-10-23, D168. **Depende de:** T004, T008. **Orden:** antes de T009; desglosada de T008
por HITL (D167).
**Evidencia:** [entrega](phase/P011-T020_RECETAS_V2.md): `[recipes]` en v6 → v2 (v5 → v1 intacto), composición con
la huella v2 de ambos idiomas, plan/recibo con idioma de la fila, su hash y `recipe_sha256`; 409
`work_language_required` sin fila y comprobación antes de cada paso; despacho por `id`, etiquetas visuales por
catálogo, plan tipado y ejemplos v6. Suites offline en verde (un timeout ajeno en paralelo que pasa en serie);
sin herramientas reales, red, servicios ni QA de navegador.
**Objetivo:** Que las altas nuevas con receta usen `django-recipe-2`/`typescript-web-recipe-2` con el trabajo congelado.
**Alcance:** `[recipes]` en `local-config-6`, registro de las v2 en `recipes`, preparación y comprobaciones por `id`
de paso, plan/recibo/huella con trabajo y lectura/conciliación de planes y recibos v1 intactas.
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- v6 admite `[recipes]` ligadas a v2; v5 sigue con v1 por bytes/huella. Una alta nueva desde v6 prepara con el
  trabajo de su fila; sin trabajo confirmado la preparación se rechaza antes de efectos. Ninguna inferencia.
- Pasos despachados por `id` estable, no por etiqueta; etiquetas humanas en visual sin mutar el manifiesto W.
  El idioma funcional del hijo (`LANGUAGE_CODE`, `<html lang>`) no deriva del visual ni del trabajo.
- Planes/recibos v1 legibles y conciliables con su intención sellada; sin recalcular con v2 ni reinstalar.
  Paridad de DDBB-DIAGRAM/flujos/API/tipos si cambian; ejemplos de fragmentos v6.

**Validación:** regresiones de recetas/huellas/recibos y preparación sintética en/es; pytest, Node/tipos/build si
cambia el cliente. Sin red ni instalaciones reales salvo autorización propia.
**Entregables:** `docs/phase/P011-T020_RECETAS_V2.md` y documentación actualizada.

## P011-T021 — Traducción de diagnósticos del servicio y de la CLI

**Estado:** completada el 2026-10-23, D171. **Depende de:** T010. **Orden:** antes de T011; desglosada de T010 por
HITL (D170).
**Evidencia:** [entrega](phase/P011-T021_TRADUCCION_SERVICIO_CLI.md): por HITL, todo texto propio antes español del
servicio/CLI y la ayuda argparse pasan a catálogo (471 claves, +425) y los textos de servicio ya ingleses a la nueva
T022; `tr()` emite en el visual de cada emisión (petición: guardado; job: congelado, HITL; CLI: `--ui-language`/base/
`en`); `core/` admite la hoja `harness_local.i18n` (HITL). Hash de retención sellado en inglés, scripts al texto
inglés, excepciones verificadas por test. pytest 1615 passed, unittest 8 y Node 93 en verde; QA visual no autorizada.
**Objetivo:** Completar en/es en los mensajes propios del servicio y de la CLI que T010 no cubre.
**Alcance:** diagnósticos de configuración local, backup/restauración, retención, migración, registro, creación,
preparación, runtime gestionado, lanzador y CLI (errores y ayuda argparse propia), y los textos de servicios/storage
que la API reenvía como `diagnostic`. Inventario de partida en la
[entrega de T010](phase/P011-T010_TRADUCCION_PRODUCTO.md#not-done-here-owners) (475 candidatos en 44 módulos).
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `scripts/**`, `tests/**`, `examples/**`, `docs/**`.
**Criterios de aceptación:**

- Mensajes propios por catálogo en el visual de la emisión (API: preferencias guardadas; CLI: `--ui-language` o
  base existente, si no `en`), sin cambiar códigos, estados, estructura, evidencia ni mensajes históricos persistidos.
- Excepciones explícitas y justificadas: vocabulario documental de T009, recetas v1 congeladas, alias bilingües de
  parsers, protocolos (comandos de chat) y textos de terceros (argparse/Pydantic). Sin reescribir huellas.
- `módulo:atributo` y `Esquema SQLite`: traducidos o fijados como técnicos con los scripts de mantenedor actualizados
  en el mismo cambio. Los dos textos del servicio que compara la UI (`managed blocks are generated`, `changed since`)
  se conservan o la UI pasa a códigos.
- Al terminar, QA visual conjunta T010+T021 en/es, claro/oscuro y escritorio/móvil con entorno sintético saneado,
  solo con autorización explícita del servicio/navegador; si no se autoriza, queda registrada como no realizada.

**Validación:** cobertura de catálogos Python, pytest/unittest pertinentes, mensajes CLI en ambos idiomas, Node/tipos/
build si cambia el cliente y scripts afectados sin ejecutar el producto real.
**Entregables:** `docs/phase/P011-T021_TRADUCCION_SERVICIO_CLI.md`, catálogos y matriz QA.

## P011-T022 — Catálogo en/es de los textos de servicio ya ingleses

**Estado:** completada el 2026-10-23, D172. **Depende de:** T021. **Orden:** antes de T011; desglosada de T021 por
HITL (D171).
**Evidencia:** [entrega](phase/P011-T022_TRADUCCION_SERVICIO_INGLES.md): por HITL, visibles por naturaleza (lo que el
operador causa o resuelve) a catálogo y técnicos ingleses listados con categoría en
`tests/fixtures/service_texts/english.json` (161: invariantes, entrada de agente, prefijos técnicos); 724 claves
nuevas (1195) en 56 módulos con el inglés idéntico. La UI compara códigos (`managed_blocks_generated`,
`draft_changed`); métricas de paradas por texto aceptadas por HITL; QA visual no autorizada (no realizada).
**Objetivo:** Que los diagnósticos propios del servicio que hoy son texto técnico inglés también salgan en/es.
**Alcance:** los textos ingleses de `raise`/diagnósticos de servicios, storage, adapters y core que el usuario puede
ver (directamente o reenviados por la API como `diagnostic`); inventario de partida en la
[entrega de T021](phase/P011-T021_TRADUCCION_SERVICIO_CLI.md) (≈960 `raise` con texto, muchos invariantes internos).
**Rutas permitidas:** `src/harness_local/**`, `frontend/**`, `scripts/**`, `tests/**`, `docs/**`.
**Criterios de aceptación:**

- Inventario que separe diagnósticos visibles de invariantes internas (que pueden quedar como texto técnico inglés
  justificado); los visibles por `tr()` en el visual de la emisión (D171), sin cambiar códigos, estados, estructura,
  evidencia ni mensajes históricos persistidos.
- Los dos textos que compara la UI (`managed blocks are generated`, `changed since`) se conservan o la UI pasa a
  códigos en el mismo cambio. Hashes y vistas previas no dependen del idioma o fallan de forma segura.
- Al terminar, QA visual conjunta T010+T021+T022 en/es, claro/oscuro y escritorio/móvil con entorno sintético
  saneado, solo con autorización explícita del servicio/navegador; si no se autoriza, queda registrada como no
  realizada.

**Validación:** cobertura de catálogos Python, pytest/unittest pertinentes, Node/tipos/build si cambia el cliente.
**Entregables:** `docs/phase/P011-T022_TRADUCCION_SERVICIO_INGLES.md`, catálogos y matriz QA.

