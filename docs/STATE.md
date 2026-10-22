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
  `0024_product_preferences` (50 tablas, [diagrama](DDBB-DIAGRAM.md)); cola idempotente, lease, lock por checkout,
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
[plan](phase/P011_PLAN_APERTURA_PUBLICA.md), [tareas](NEXT_STEPS.md)). T001/T002/T019/T003–T007
completadas (D159–D166), once tareas pendientes; retirada legacy/A implementada, núcleo/backend/cliente/pruebas
en inglés y preferencias globales de idioma; sin trabajo por proyecto, directiva al agente ni nueva compatibilidad CLI.

**Planificación finalizada para comenzar su ejecución** por petición del usuario
([D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020)).
P011 no está completada: T001 entrega diseño/inventario, T002 licencia/revisión estática, T019 retirada funcional y
T003–T006 comentarios en inglés y T007 infraestructura de idiomas; siguiente T008.
El modo continuo entre fases queda reservado para **v0.2.0, después de abrir el proyecto en GitHub**;
no forma parte de P011 ni modifica el cierre confirmado actual. Commit documental D156 realizado en `6174f51`;
las ampliaciones D157/D158 se incorporaron en `2730f54`. La petición actual autoriza T007 y su commit local
en inglés, con checks sintéticos offline, sin ejecución del producto ni publicación.

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

**P010 cerrada y archivada documentalmente el 2026-10-22**
([D153](DECISIONS.md#d153--cierre-documental-de-p010-y-de-la-primera-versión-local),
[resumen](archive/phase-010/SUMMARY.md), [registro de cierre](archive/phase-010/P010_CIERRE.md)).
El dictamen favorable de T009 y la decisión explícita D151 permiten completar la primera versión local en ese
alcance. Originales de STATE/NEXT_STEPS y artefactos de fase conservados por bytes; sin tareas obligatorias pendientes.
El paquete sigue en `0.1.0`, sin tag ni publicación; P011 sucede ahora a ese cierre sin reescribirlo.

P009 conserva su cierre documental (D140) y el Django hijo su P001 CLOSED, cuatro tareas COMMITTED,
tag `p001` sobre `47a0557` y archivo en `3d105c6`. No se repite ninguna operación ni comprobación de su estado.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; cierre manual sin check READY ni tag propio.

**Siguiente:** P011-T008, idioma de trabajo inmutable por proyecto y contexto congelado.
Otras candidatas permanecen en [ROADMAP](ROADMAP.md#candidatas-sin-fase-asignada).
Los límites de la base acumulada siguen vigentes. B y D095 mantienen la validación real aplazada por D151;
A queda retirado del producto por D155/D161, sin acreditarlo como validado con proveedores reales.
Sin nueva fase del Django hijo ni ampliación de consentimientos.
