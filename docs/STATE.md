# Estado — my_harness

Actualizado: 2026-10-23. Sin bloques gestionados mientras el repositorio no esté registrado en el harness (D088).

## Base acumulada

Lo que existe y funciona, verificado offline con Git, SQLite y procesos temporales, agentes falsos y datos sintéticos
salvo donde se indica. Detalle por fase en `docs/archive/phase-NNN/SUMMARY.md`; P001–P010 cerradas; primera versión local completada en el alcance de D151/D153.

- **Núcleo y motor** ([P001](archive/phase-001/SUMMARY.md), [P003](archive/phase-003/SUMMARY.md)): paquete
  `harness_local` con contexto explícito por proyecto, contrato de tarea congelado, planificación determinista o por el
  revisor, bucle ejecución → validación → revisión con límite de correcciones, aceptación ligada al contenido exacto y
  commit determinista conciliable. Formateo del perfil tras cada turno del ejecutor (D133). Codec de historial
  en formato 8 (lee 1–7).
- **Persistencia y recuperación** ([P003](archive/phase-003/SUMMARY.md), [P006](archive/phase-006/SUMMARY.md)): SQLite
  `0025_project_work_languages` (51 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
  cuarentena por versión y confirmación explícita del escritor detenido; backup y restauración de consulta; retención
  explícita de streams. Proyección derivada `run-projection-1` escrita con el historial y comprobada en el backup
  (P010-T003, D144).
- **Agentes** ([P007](archive/phase-007/SUMMARY.md)): revisor y ejecutor Codex o Claude en cualquier combinación
  (`cli-14`, configuración hasta `local-config-7`, lectura de 1–6), revisor en solo lectura con esquema tipado, memoria automática desactivada,
  supresión de confianza del escritor Codex. Validaciones nativas `commands-1` con JUnit. Perfiles: `typescript-web`
  (componible desde el TOML), `reference_project` (solo biblioteca) y perfiles declarados en `[profiles.*]` de
  `local-config-4`, con el ejemplo `python-django` (P008, D095).
  Detección automática por PATH explícito/ruta opcional en v7, sin pin obligatorio; mínimos Codex 0.163.0 /
  Claude 2.1.304, posteriores con compatibilidad condicionada al contrato conocido (P011-T012, D174).
  Política/cliente observados congelados por job y revalidación por intento/antes de GO; sin uso real nuevo.
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
  Recetas v2 (`django-recipe-2`, `typescript-web-recipe-2`) en `local-config-6` con el idioma de trabajo del hijo
  sellado en plan/recibo y comprobaciones por `id` (P011-T020, D168); v5 conserva v1. Prompts con la directiva
  del par congelado y documentos generados en el idioma de trabajo (P011-T009, D169). Interfaz React completa en
  en/es por catálogos tipados y diagnósticos HTTP propios en el visual guardado (P011-T010, D170). Textos propios
  del servicio/CLI antes españoles en en/es con el visual de cada emisión: petición, job congelado o CLI (P011-T021, D171).
  Diagnósticos visibles del servicio antes ingleses (razones de parada/aceptación incluidas) también en en/es; los
  técnicos ingleses quedan listados por categoría y la UI distingue rechazos por código (P011-T022, D172).
- **Incorporación de proyectos** ([P008](archive/phase-008/SUMMARY.md), D161): inventario estático sobre HEAD,
  conversación de solo lectura y borradores privados de B, perfil/documentos confirmados y commit conciliable.
  Objetos locales, blobs por hash, filtros/gitlinks y destinos ignorados comprobados antes de escribir y recuperar.
  A, visor/observación legacy y activación/reversión retirados en P011-T019; datos y migraciones anteriores
  conservados, jobs retirados/ambiguos en cuarentena sin ejecutarlos. Guardia de activaciones ACTIVE previas
  conservada para trabajo gestionado, sin reactivar los flujos retirados.
- **API y UI** ([P007](archive/phase-007/SUMMARY.md)): `/api/managed` con sesión local, Host/Origin y CSRF; UI por URL
  (registro, proyecto, documentación, creación, fases, tareas, runs con diff paginado, chat, estadísticas); métricas por
  intento con procedencia; observación gestionada por cursor de eventos. Detalle, ciclos paginados, diff y casos JUnit de un run
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
  de confirmar sobre un proyecto real. B y ese perfil conservan su validación solo offline: el usuario aplaza
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

**P011 — Preparación para apertura pública en GitHub**, iniciada documentalmente el 2026-10-22 por encargo del usuario
([D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github),
[plan](phase/P011_PLAN_APERTURA_PUBLICA.md), [tareas](NEXT_STEPS.md)). T001/T002/T019/T003–T014/T020–T022
completadas (D159–D176), cinco pendientes (T021–T023 son desgloses HITL); retirada legacy/A
implementada, código y pruebas en inglés, preferencias globales, idioma de trabajo inmutable por proyecto, recetas v2
cableadas, directiva de idioma al agente con documentos en el idioma de trabajo, interfaz en/es y todos los textos
visibles del servicio/CLI en en/es; detección automática y compatibilidad CLI implementadas con evidencia nueva
sintética; diagramas, datos y arquitectura contrastados con el código; baseline pública inglesa y README de primer
uso. Sin QA visual conjunta (no autorizada) ni uso nuevo de proveedores reales.

**Planificación finalizada para comenzar su ejecución** por petición del usuario
([D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020)).
P011 no está completada: T001 entrega diseño/inventario, T002 licencia/revisión estática, T019 retirada funcional y
T003–T006 comentarios en inglés, T007 infraestructura de idiomas, T008 idioma de trabajo, T020 recetas v2, T009
directiva y documentos por idioma, T010 interfaz en/es, T021 servicio/CLI en/es y T022 textos de servicio ya
ingleses en en/es, T011 contrato, T012 compatibilidad/detección automática, T013 auditoría de diagramas y T014
baseline pública; siguiente T023.
El modo continuo entre fases queda reservado para **v0.2.0, después de abrir el proyecto en GitHub**;
no forma parte de P011 ni modifica el cierre confirmado actual. Commit documental D156 realizado en `6174f51`;
las ampliaciones D157/D158 se incorporaron en `2730f54`. La continuación actual autoriza T014 y su commit local
en inglés, sin proveedores reales ni publicación.

**P011-T001 completada** ([contrato](phase/P011-T001_CONTRATO_APERTURA.md),
[inventario](phase/P011-T001_INVENTARIO.md), D159): 688 archivos de base, con tratamiento/propietaria y
excepciones; defaults globales en SQLite, catálogos JSON sin nuevas dependencias, trabajo inmutable y par
congelado por job/turno con mapa de campos humanos/técnicos. Diseñadas compatibilidad de recetas v1/v2,
retirada A/legacy con infraestructura B e historial propio conservados, y lista permitida del corte público.
Contrato listo para implementar en sus tareas; contraste estático, hashes, parsers/enlaces/presupuestos e
integridad/diff verificados. Sin suites, builds, servicios, agentes/proveedores, red ni auditoría de privacidad.

**P011-T002 completada** ([informe](phase/P011-T002_CONTENIDO_PUBLICABLE.md), D160): MIT por delegación
expresa del usuario y copyright 2026 David Acosta; LICENSE/metadatos, contribución/seguridad en inglés, avisos
de 123 dependencias runtime frontend y exclusiones preventivas. Escaneo local de 690 archivos y 4.009 objetos
Git alcanzables, sin credenciales reales identificadas con los patrones usados; contenido privado excluido
mediante nueva raíz/árbol público futuro, sin reescribir el origen. Inventario por ruta/hash y 247 dependencias;
19 términos de dependencias externas sin evidencia local declarados. Reportes privados GitHub elegidos,
activación pendiente de apertura; staging/avisos/assets y candidato exacto a T015/T016. Fuentes oficiales
MIT/GitHub consultadas, sin enviar contenido. Checks estáticos, sin suites/builds/servicios/proveedores.
No se declara este historial ni los paquetes antiguos publicables; sigue pendiente el dictamen final P011.

Objetivo: código/comentarios/docstrings y prompts originales ingleses; idiomas visual/trabajo separados (D158);
CLI por capacidades/mínimos; diagramas contrastados con comportamiento; documentación inglesa y README de primer
uso; licencia/contenido publicable, paquete/CI y QA del candidato antes del dictamen. Sin publicar ni abrir
visibilidad por efecto de esta fase. Licencia/titularidad resueltas en T002; versión candidata pendiente de T015.

[D157](DECISIONS.md#d157--repositorio-público-nuevo-y-continuidad-del-desarrollo) prevé instantánea inicial
revisada sin historia/docs privados y con docs públicas nuevas útiles; después, código/decisiones/fases evolucionan
en el repositorio público como fuente principal. Este checkout conserva su historia; no hay copia/repositorio nuevos aún.
[D158](DECISIONS.md#d158--idioma-visual-global-y-trabajo-inmutable-por-proyecto): defaults globales visual/trabajo
en/es (en inicial); visual global mutable gobierna UI y conversación/respuesta humana. Trabajo se elige al alta
y es inmutable para documentación/código, sin visual por proyecto. my_harness público usará trabajo en inglés;
ambas lenguas se congelarán por job/turno, con nuevas respuestas en el visual elegido sin mutar las ya iniciadas.

**P011-T019 completada** ([informe](phase/P011-T019_RETIRADA_LEGACY.md), D161): retirada real de UI/API/CLI,
SSE/observadores, activación/reversión y normalización/conversación A. Extraídas guardias Git, borradores CAS e
integridad de activaciones previas; B conserva intención, perfil y adopción P001. Sin cambios de metadata o
migraciones, eliminación de datos del usuario o reinterpretación de jobs A como B. Cuarentena y resolución
explícita sin ejecutar intenciones retiradas; backup/restauración conserva datos y no observa orígenes.
Pruebas sintéticas, OpenAPI/tipos/build y manifiestos fuente registrados en el informe; primer uso del paquete
exacto y QA de navegador quedan para T016. D155 implementada sin reescribir evidencia de fases cerradas.

**P011-T003 completada** ([inventario](phase/P011-T003_INGLES_NUCLEO.md), D162): comentarios y docstrings de los
35 archivos de `core/**`/`profiles/**` en inglés; sin identificadores españoles. Literales sin cambios: mensajes
a T010, prosa generada/prompts a T009, alias bilingües y valores de perfil ligados a huellas conservados.
AST idéntico por archivo y suites existentes; el resto del backend sigue en T004.

**P011-T004 completada** ([inventario](phase/P011-T004_INGLES_BACKEND.md), D163): comentarios, docstrings y
descripciones OpenAPI del resto de `src/harness_local` en inglés (OpenAPI/tipos regenerados); mensajes visibles
inventariados para T010. Recetas v1 conservan bytes/huellas (fijadas por test). Por HITL, `django-recipe-2` y
`typescript-web-recipe-2` existen en inglés con prosa técnica en/es y defaults funcionales v1, sin cablear hasta T008.

**P011-T005 completada** ([inventario](phase/P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md), D164): comentarios TS/TSX/CSS
del frontend en inglés con tokens y reglas idénticos; cadenas visibles inventariadas para T010. Por HITL, mensajes de
scripts de mantenedor en inglés (tres acoplados a mensajes del producto quedan para T010) y descripción del paquete
nueva. Ejemplos vigentes en inglés con placeholders sintéticos; guiones históricos E6 sin cambios.

**P011-T006 completada** ([inventario](phase/P011-T006_INGLES_PRUEBAS.md), D165): comentarios, docstrings y nombres
de pruebas Python/frontend en inglés con AST idéntico salvo un test renombrado y cinco textos propios de pruebas.
Expectativas del producto, datos bilingües/sintéticos y fixtures conservados; por HITL, README de fixtures en inglés.

**P011-T007 completada** ([entrega](phase/P011-T007_INFRAESTRUCTURA_IDIOMAS.md), D166): migración `0024` con
preferencias globales `ui_language`/`default_work_language` (en/en, CAS, eventos), `GET/PUT /api/managed/preferences`
y página `/preferences`. Cada job sella el visual vigente al admitirse (`ui-language-1`); las continuaciones heredan
el del primer job. Por HITL, el par completo y su paso a intentos/prompts son de T008 y la directiva de T009: los
agentes aún no cambian de idioma. Catálogos JSON en/es sin dependencias; shell, sesión y preferencias traducidos (HITL),
diagnósticos propios de sesión/preferencias/lanzador localizados y `--ui-language`. Sin QA de navegador (T010).

**P011-T008 completada** ([entrega](phase/P011-T008_IDIOMA_PROYECTO.md), D167): migración `0025` con una fila
inmutable de idioma de trabajo por raíz canónica. Registro B y creación lo exigen (inicializado desde el default,
sellado en el hash); cambios/bajas/reaperturas con otro valor → 409 `work_language_immutable`. `local-config-6`
lo declara por proyecto TOML y el servicio lo asocia al arrancar (HITL); sin valor, toda admisión nueva → 409
`work_language_required` hasta una confirmación explícita con hash y motivo (API/UI mínima, HITL). Cada job sella
`language-context-1` y cada intento lo copia. Por HITL, recetas v2 → T020; sin directiva al agente (T009).

**P011-T020 completada** ([entrega](phase/P011-T020_RECETAS_V2.md), D168): `local-config-6` admite `[recipes]` con
las claves de v5 y elige `django-recipe-2`/`typescript-web-recipe-2` (v5 sigue con v1 y sus hashes). La composición
liga la huella v2 de ambos idiomas; el plan sella el idioma de la fila de la raíz, su hash y `recipe_sha256`, y el
recibo los copia; sin fila, 409 `work_language_required` antes de efectos y comprobación antes de cada paso.
Perfiles v2 propios, despacho por `id`, etiquetas de pasos en idioma visual por catálogo y `work_language`/
`recipe_sha256` tipados en el plan. Idioma funcional del hijo intacto. Sin herramientas reales, red ni QA de navegador.

**P011-T009 completada** ([entrega](phase/P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md), D169): `render_attempt`
añade a cada intento la directiva `language-directive-1` del par congelado de su job (frase visual/trabajo, mapa
V/W/T por rol y etiquetas D088 del trabajo), sellada en el snapshot y enviada por el stdin de ambos proveedores;
par inválido o distinto del contexto → parada en `prompts`, y jobs sin par se renderizan como antes. Plantillas
inglesas sin marcadores españoles. Bloques, plantilla D088, archivo, definición, transición, SUMMARY de B y texto de
tarea desde chat siguen el idioma de trabajo; sin él, bytes españoles idénticos. HITL: todo en T009 y commits
técnicos sin cambios. Recorridos falsos con las cuatro parejas; sin proveedores reales ni QA de navegador.

**P011-T010 completada** ([entrega](phase/P011-T010_TRADUCCION_PRODUCTO.md), D170): todas las superficies React
(textos, ARIA, tooltips, estados vacíos, confirmaciones) salen de 1417 claves en/es tipadas, con plurales, frases con
elementos sin fragmentos traducidos, fechas/números/coste por idioma y visor Markdown sin texto propio en el HTML.
Los diagnósticos HTTP de `api/*` usan el visual guardado; la línea de la clave de acceso es técnica fija en inglés.
HITL: servicio/CLI → T021 y QA visual conjunta tras T021. Node, tipos/build y suites offline en verde; sin navegador.

**P011-T021 completada** ([entrega](phase/P011-T021_TRADUCCION_SERVICIO_CLI.md), D171): 471 claves del servicio
en/es; `tr()` emite en el visual de cada emisión (petición HTTP: guardado; job: el congelado; CLI: `--ui-language`,
base o `en`, también la ayuda). Hash de retención sellado en inglés; registro de confianza con la declaración
confirmada; scripts al texto inglés. HITL: textos ya ingleses → T022, núcleo admite la hoja `harness_local.i18n` y QA
visual no autorizada. Suites offline en verde; sin servicios, navegador ni proveedores.

**P011-T022 completada** ([entrega](phase/P011-T022_TRADUCCION_SERVICIO_INGLES.md), D172): por HITL, los diagnósticos
visibles por naturaleza de `core/adapters/storage/services` (695 `raise` y ~90 razones/diagnósticos) pasan a 724 claves
nuevas en/es con el inglés idéntico; 161 textos técnicos ingleses listados con categoría y verificados por test. La UI
distingue `managed_blocks_generated`/`draft_changed` por código; las métricas agrupan paradas por texto emitido
(aceptado). QA visual conjunta no autorizada, registrada como no realizada; sin servicios, navegador ni proveedores.

**P011-T011 completada** ([contrato](phase/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md), D173): solo diseño.
HITL: detectar clientes/versiones automáticamente, sin pin ni aceptación de candidatas; mínimos comunes nuevos
Codex 0.163.0 / Claude 2.1.304 por D122/D124, inferiores → actualizar y lectura histórica preservada. Matriz
por proveedor/rol, perfiles semánticos mantenidos por la aplicación, guardias esenciales y procedencia congelada
por job/intento con revalidación/cuarentena al cambiar el cliente. Sin evidencia aportada por el usuario ni
allowlist exclusiva por patch; no garantiza cualquier release futura. Fuentes oficiales/parsers/enlaces/diff
revisados, aviso previo de tamaño de NEXT_STEPS; sin suites ni CLI/proveedores reales. T012 implementará.

**P011-T012 completada** ([entrega](phase/P011-T012_COMPATIBILIDAD_CLI.md), D174): `local-config-7` admite
ejecutable/versión opcionales; carga sin procesos y resolución separada de roles efectivos por PATH explícito,
mínimos 0.163.0 / 2.1.304 y diagnósticos en/es. `cli-14` congela identidad/política y observa por intento, valida
guardias del argv y comprueba identidad antes de GO; cambios no reemplazan clientes de jobs congelados. HITL:
posteriores admitidas con compatibilidad condicionada, sin afirmar efectos internos verificados ni pedir evidencia
al usuario. API con lecturas pasivas y resolución por mutación; ejemplos sin pins, ayudas propias sintéticas,
v1/v2 y hashes previos de configuración conservados. Sin esquema/API nueva, proveedores, servicio o navegador.
Validación offline y omisiones en la entrega.

**P011-T013 completada** ([matriz](phase/P011-T013_MATRIZ_DIAGRAMAS.md), D175): 14 flujos (23 diagramas), 12 ER y
ARCHITECTURE contrastados nodo/transición → código/tests. Catorce hallazgos documentales corregidos sin cambiar el
producto: estados de run, fase y creación, `/tarea`, `local-config-6/7`, resolución CLI, idioma en B, restos
A/observadores, marcas UK y dos diagramas de secuencia que no compilaban. Piloto P009 separado del flujo vigente.
Dos regresiones nuevas para transiciones sin prueba. 35 diagramas pasan el parser Mermaid local (sin DOM/render),
paridad ER de 51 tablas/520 columnas y 727 enlaces; flujos aún en su idioma.

**P011-T014 completada** ([entrega](phase/P011-T014_DOCUMENTACION_PUBLICA.md), D176): por HITL, baseline pública en
`docs/public/` (instrucciones y `docs/` del candidato), README raíz inglés de primer uso, `README.es.md` y ejemplo
mínimo de un proveedor. DECISIONS pública conserva los DNNN citados por el código (nuevas desde D200);
especificación/arquitectura/datos/flujos → T023. Comprobador estático en verde; primer uso sin ensayar (T016).

**P010 cerrada y archivada documentalmente el 2026-10-22**
([D153](DECISIONS.md#d153--cierre-documental-de-p010-y-de-la-primera-versión-local),
[resumen](archive/phase-010/SUMMARY.md), [registro de cierre](archive/phase-010/P010_CIERRE.md)).
El dictamen favorable de T009 y la decisión explícita D151 permiten completar la primera versión local en ese
alcance. Originales de STATE/NEXT_STEPS y artefactos de fase conservados por bytes; sin tareas obligatorias pendientes.
El paquete sigue en `0.1.0`, sin tag ni publicación; P011 sucede ahora a ese cierre sin reescribirlo.

P009 conserva su cierre documental (D140) y el Django hijo su P001 CLOSED, cuatro tareas COMMITTED,
tag `p001` sobre `47a0557` y archivo en `3d105c6`. No se repite ninguna operación ni comprobación de su estado.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; cierre manual sin check READY ni tag propio.

**Siguiente:** P011-T023, especificación, arquitectura, datos y flujos públicos en inglés.
La QA visual conjunta T010+T021+T022 sigue pendiente de autorización propia.
Otras candidatas permanecen en [ROADMAP](ROADMAP.md#candidatas-sin-fase-asignada).
Los límites de la base acumulada siguen vigentes. B y D095 mantienen la validación real aplazada por D151;
A queda retirado del producto por D155/D161, sin acreditarlo como validado con proveedores reales.
Sin nueva fase del Django hijo ni ampliación de consentimientos.
