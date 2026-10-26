# Decisiones — my_harness

Registro único de decisiones de arquitectura y de negocio (ADR), en orden. Cada entrada empieza por `## DNNN — Título`
y una línea `Estado:` con fecha (y «sustituida por DMMM» cuando proceda), seguida de contexto, decisión y
consecuencias. Las decisiones no se borran ni se reescriben: se sustituyen con una nueva (D088). Al trabajar en una
tarea se leen solo las decisiones que cita; este índice sirve para buscar precedentes. La fase indica cuándo se tomó
(P000 es la definición inicial; los hitos H0–H6 son P001–P007).

## Índice

| Decisión | Título | Fase |
|---|---|---|
| [D001](#d001--alcance-local-y-arquitectura-base) | Alcance local y arquitectura base | P000 |
| [D002](#d002--desarrollo-manual) | Desarrollo manual | P000 |
| [D003](#d003--cola-local-sin-celery) | Cola local sin Celery | P000 |
| [D004](#d004--servicio-nativo-docker-por-perfil) | Servicio nativo, Docker por perfil | P000 |
| [D005](#d005--comenzar-por-h01) | Comenzar por H0.1 | P000 |
| [D006](#d006--evidencias-legacy-y-fixtures-de-h01) | Evidencias legacy y fixtures de H0.1 | P001 |
| [D007](#d007--baseline-de-versiones-h02) | Baseline de versiones H0.2 | P001 |
| [D008](#d008--suscripciones-propias-mediante-cli) | Suscripciones propias mediante CLI | P001 |
| [D009](#d009--sonda-offline-de-streams-y-permisos) | Sonda offline de streams y permisos | P001 |
| [D010](#d010--simulación-h03-separada-del-motor-y-del-legacy) | Simulación H0.3 separada del motor y del legacy | P001 |
| [D011](#d011--instalación-y-fuente-de-contratos-del-esqueleto) | Instalación y fuente de contratos del esqueleto | P001 |
| [D012](#d012--índice-legacy-por-evidencia-con-relectura-explícita) | Índice legacy por evidencia, con relectura explícita | P002 |
| [D013](#d013--navegación-de-observación-y-contenido-vinculado-al-hash) | Navegación de observación y contenido vinculado al hash | P002 |
| [D014](#d014--observación-opt-in-y-feed-persistido-del-índice) | Observación opt-in y feed persistido del índice | P002 |
| [D015](#d015--motor-extraído-aislado-y-recuperación-explícita) | Motor extraído aislado y recuperación explícita | P003 |
| [D016](#d016--autoridad-gestionada-y-recuperación-conservadora-de-jobs) | Autoridad gestionada y recuperación conservadora de jobs | P003 |
| [D017](#d017--adaptadores-cli-opt-in-y-grupos-persistidos) | Adaptadores CLI opt-in y grupos persistidos | P003 |
| [D018](#d018--smoke-h23-autorizado-selección-delegada-y-parada-al-primer-fallo) | Smoke H2.3 autorizado, selección delegada y parada al primer fallo | P003 |
| [D019](#d019--proveedor-integrado-conservado-y-retries-internos-desconocidos) | Proveedor integrado conservado y retries internos desconocidos | P003 |
| [D020](#d020--nuevo-smoke-autorizado-y-parada-ante-configuración-mcp-de-claude) | Nuevo smoke autorizado y parada ante configuración MCP de Claude | P003 |
| [D021](#d021--mcp-vacío-explícito-y-versión-congelada-cli-3) | MCP vacío explícito y versión congelada cli-3 | P003 |
| [D022](#d022--smoke-cli-3-autorizado-y-fallo-de-autenticación-claude) | Smoke cli-3 autorizado y fallo de autenticación Claude | P003 |
| [D023](#d023--user-explícito-dependencia-de-auth-observada-corrección-separada) | USER explícito: dependencia de auth observada, corrección separada | P003 |
| [D024](#d024--entorno-del-smoke-validado-por-uid-y-hash-de-configuración-nuevo) | Entorno del smoke validado por UID y hash de configuración nuevo | P003 |
| [D025](#d025--smoke-autorizado-con-user-tres-transportes-completos) | Smoke autorizado con USER: tres transportes completos | P003 |
| [D026](#d026--evidencia-git-por-árboles-y-commit-determinista-conciliable) | Evidencia Git por árboles y commit determinista conciliable | P003 |
| [D027](#d027--modo-gestionado-por-activación-marcador-y-copia-inmutable) | Modo gestionado por activación, marcador y copia inmutable | P003 |
| [D028](#d028--api-gestionada-local-proyectos-del-servidor-y-supervisor-opt-in) | API gestionada local: proyectos del servidor y supervisor opt-in | P003 |
| [D029](#d029--ui-gestionada-por-sondeo-envíos-conservados-y-evidencia-congelada) | UI gestionada por sondeo, envíos conservados y evidencia congelada | P003 |
| [D030](#d030--catálogo-de-prompts-por-ámbito-y-snapshot-por-intento) | Catálogo de prompts por ámbito y snapshot por intento | P004 |
| [D031](#d031--permisos-por-petición-exacta-y-efecto-en-un-intento-posterior) | Permisos por petición exacta y efecto en un intento posterior | P004 |
| [D032](#d032--fases-en-sqlite-ready-por-contenido-exacto-y-cierre-sin-edición-documental) | Fases en SQLite, READY por contenido exacto y cierre sin edición documental | P004 |
| [D033](#d033--decisiones-del-usuario-tras-h33-y-orden-de-trabajo) | Decisiones del usuario tras H3.3 y orden de trabajo | P004 |
| [D034](#d034--lote-desatendido-derivado-del-estado-definiciones-versionadas-y-tags-anotados-deterministas) | Lote desatendido derivado del estado, definiciones versionadas y tags anotados deterministas | P004 |
| [D035](#d035--chat-por-turnos-nuevos-de-solo-lectura-con-contexto-congelado-y-propuestas-confirmadas) | Chat por turnos nuevos de solo lectura con contexto congelado y propuestas confirmadas | P005 |
| [D036](#d036--exportación-documental-separada-diff-confirmado-e-intención-de-commit-conciliable) | Exportación documental separada, diff confirmado e intención de commit conciliable | P005 |
| [D037](#d037--bootstrap-documental-confirmado-descubrimiento-opcional-y-commit-raíz-conciliable) | Bootstrap documental confirmado, descubrimiento opcional y commit raíz conciliable | P005 |
| [D038](#d038--segundo-perfil-declarativo-con-validaciones-typescript-reales-por-los-puertos-existentes) | Segundo perfil declarativo con validaciones TypeScript reales por los puertos existentes | P005 |
| [D039](#d039--junit-observado-por-comando-exacto-y-original-congelado-en-el-historial) | JUnit observado por comando exacto y original congelado en el historial | P006 |
| [D040](#d040--backup-local-con-servicio-detenido-referencias-verificadas-y-restauración-de-consulta) | Backup local con servicio detenido, referencias verificadas y restauración de consulta | P006 |
| [D041](#d041--retención-explícita-de-streams-sellados-con-intención-previa-y-ausencias-auditadas) | Retención explícita de streams sellados con intención previa y ausencias auditadas | P006 |
| [D042](#d042--diagnóstico-cli-explícito-preflight-compartido-y-resultados-acotados) | Diagnóstico CLI explícito, preflight compartido y resultados acotados | P006 |
| [D043](#d043--distribución-local-con-assets-y-migraciones-arranque-explícito-en-loopback) | Distribución local con assets y migraciones, arranque explícito en loopback | P006 |
| [D044](#d044--sesión-efímera-local-y-guardia-uniforme-antes-del-acceso-al-producto) | Sesión efímera local y guardia uniforme antes del acceso al producto | P006 |
| [D045](#d045--recorridos-offline-consolidados-y-cierre-acotado-del-hito-5) | Recorridos offline consolidados y cierre acotado del hito 5 | P006 |
| [D046](#d046--revisión-del-cierre-offline-y-separación-de-la-preparación-para-uso-real) | Revisión del cierre offline y separación de la preparación para uso real | P006 |
| [D047](#d047--validadores-nativos-opt-in-con-captura-acotada-y-recuperación-conservadora) | Validadores nativos opt-in con captura acotada y recuperación conservadora | P006 |
| [D048](#d048--revisión-del-ejecutor-de-validaciones-runner-congelado-obligatorio) | Revisión del ejecutor de validaciones: runner congelado obligatorio | P006 |
| [D049](#d049--composición-de-uso-real-por-toml-local-del-operador) | Composición de uso real por TOML local del operador | P006 |
| [D050](#d050--propuesta-de-primer-uso-real-selecciones-del-usuario-y-límites) | Propuesta de primer uso real: selecciones del usuario y límites | P006 |
| [D051](#d051--operación-real-desde-el-wheel-instalado-no-desde-el-checkout-de-desarrollo) | Operación real desde el wheel instalado, no desde el checkout de desarrollo | P006 |
| [D052](#d052--revisor-y-ejecutor-con-proveedor-modelo-y-esfuerzo-elegidos-por-el-usuario) | Revisor y ejecutor con proveedor, modelo y esfuerzo elegidos por el usuario | P007 |
| [D053](#d053--comando-único-de-desarrollo-con-migración-y-backup-previo) | Comando único de desarrollo con migración y backup previo | P006 |
| [D054](#d054--hito-de-ui-de-producto-después-de-d052-y-registro-de-proyectos-en-sqlite) | Hito de UI de producto después de D052 y registro de proyectos en SQLite | P007 |
| [D055](#d055--propuesta-del-smoke-de-la-matriz-d052-selecciones-del-usuario-y-límites) | Propuesta del smoke de la matriz D052: selecciones del usuario y límites | P007 |
| [D056](#d056--formas-de-salida-de-los-agentes-alineadas-con-los-validadores-del-motor) | Formas de salida de los agentes alineadas con los validadores del motor | P007 |
| [D057](#d057--nueva-ejecución-de-la-matriz-d052-tras-d056) | Nueva ejecución de la matriz D052 tras D056 | P007 |
| [D058](#d058----json-schema-tipado-para-el-lector-claude-cli-6) | `--json-schema` tipado para el lector Claude (`cli-6`) | P007 |
| [D059](#d059--diagnóstico-del-escritor-codex-y-raíces-explícitas-cli-7) | Diagnóstico del escritor Codex y raíces explícitas (`cli-7`) | P007 |
| [D060](#d060--propuesta-acotada-de-las-combinaciones-24-con-paquete-cli-7) | Propuesta acotada de las combinaciones 2–4 con paquete `cli-7` | P007 |
| [D061](#d061--ejecución-de-d060-codex-escritor-real-y-parada-por-cambio-global) | Ejecución de D060: Codex escritor real y parada por cambio global | P007 |
| [D062](#d062--delta-de-confianza-acreditado-y-límite-de-contención-de-la-cli) | Delta de confianza acreditado y límite de contención de la CLI | P007 |
| [D063](#d063--propuesta-de-frontera-externa-de-escritura-auth-compatible-aún-no-certificada) | Propuesta de frontera externa de escritura; auth compatible aún no certificada | P007 |
| [D064](#d064--contención-sintética-calificada-con-límites-que-impiden-su-integración) | Contención sintética calificada con límites que impiden su integración | P007 |
| [D065](#d065--anidamiento-condicionado-por-el-perfil-y-frontera-revisada-no-calificada) | Anidamiento condicionado por el perfil y frontera revisada no calificada | P007 |
| [D066](#d066--memoria-de-trabajo-documental-y-controles-explícitos-de-auto-memory-cli-8) | Memoria de trabajo documental y controles explícitos de auto memory (`cli-8`) | P007 |
| [D067](#d067--diagnóstico-de-arranque-preparado-con-incompatibilidad-sin-cli-real) | Diagnóstico de arranque preparado con incompatibilidad, sin CLI real | P007 |
| [D068](#d068--condición-de-confianza-del-pin-acreditada-y-supresión-específica-cli-9) | Condición de confianza del pin acreditada y supresión específica (`cli-9`) | P007 |
| [D069](#d069--primer-ensayo-cli-9-detenido-por-contradicción-del-plan) | Primer ensayo cli-9 detenido por contradicción del plan | P007 |
| [D070](#d070--matriz-corregida-detenida-por-errores-de-conexión-del-planificador) | Matriz corregida detenida por errores de conexión del planificador | P007 |
| [D071](#d071--comprobación-funcional-real-de-las-cuatro-combinaciones-completada) | Comprobación funcional real de las cuatro combinaciones completada | P007 |
| [D072](#d072--organización-documental-por-fase-y-estructura-de-producto) | Organización documental por fase y estructura de producto | P007 |
| [D073](#d073--confirmación-de-d072-e-implementación-de-h63) | Confirmación de D072 e implementación de H6.3 | P007 |
| [D074](#d074--métricas-por-intento-materializadas-con-procedencia-y-agregados-sin-doble-conteo-h64) | Métricas por intento materializadas con procedencia y agregados sin doble conteo (H6.4) | P007 |
| [D075](#d075--creación-y-planificación-conversacionales-con-borradores-en-disco-y-cas-h65) | Creación y planificación conversacionales con borradores en disco y CAS (H6.5) | P007 |
| [D076](#d076--alcance-de-h62-registro-híbrido-markdown-seguro-chat-sin-lock-y-entregas) | Alcance de H6.2: registro híbrido, Markdown seguro, chat sin lock y entregas | P007 |
| [D077](#d077--h62-e1-shell-por-url-lecturas-por-código-y-sistema-de-diseño) | H6.2 E1: shell por URL, lecturas por código y sistema de diseño | P007 |
| [D078](#d078--h62-e2-local-config-3-y-registro-de-proyectos-desde-la-ui) | H6.2 E2: `local-config-3` y registro de proyectos desde la UI | P007 |
| [D079](#d079--guardia-h56-sin-cambios-ante-navegaciones-cross-site-hallazgo-de-e1) | Guardia H5.6 sin cambios ante navegaciones cross-site (hallazgo de E1) | P007 |
| [D080](#d080--h62-e3-visor-y-edición-de-documentos-con-cas-regeneración-de-bloques-y-markdown-aislado) | H6.2 E3: visor y edición de documentos con CAS, regeneración de bloques y Markdown aislado | P007 |
| [D081](#d081--rutas-protegidas-del-perfil-límite-del-ejecutor-no-de-las-escrituras-documentales-confirmadas-v2) | Rutas protegidas del perfil: límite del ejecutor, no de las escrituras documentales confirmadas (v2) | P007 |
| [D082](#d082--h62-e4-creación-y-planificación-de-fase-en-la-ui) | H6.2 E4: creación y planificación de fase en la UI | P007 |
| [D083](#d083--h62-e5-chat-sobre-head-carril-independiente-y-comandos-deterministas) | H6.2 E5: chat sobre HEAD, carril independiente y comandos deterministas | P007 |
| [D084](#d084--h62-e6-estadísticas-por-url-evolución-de-tests-por-fase-y-gráficos-svg-propios) | H6.2 E6: estadísticas por URL, evolución de tests por fase y gráficos SVG propios | P007 |
| [D085](#d085--revisión-de-cierre-de-h62-criterios-cumplidos-salvo-la-paginación-de-diffs) | Revisión de cierre de H6.2: criterios cumplidos salvo la paginación de diffs | P007 |
| [D086](#d086--hallazgos-de-d085-corregidos-diffs-paginados-conversaciones-idempotentes-y-fase-con-sucesora) | Hallazgos de D085 corregidos: diffs paginados, conversaciones idempotentes y fase con sucesora | P007 |
| [D087](#d087--h62-y-el-hito-6-cerrados-por-decisión-del-usuario) | H6.2 y el Hito 6 cerrados por decisión del usuario | P007 |
| [D088](#d088--contrato-documental-unificado-cierre-de-fase-automático-e-importación-de-proyectos-p008) | Contrato documental unificado, cierre de fase automático e importación de proyectos (P008) | P008 |
| [D089](#d089--p008-t002-layout-unificado-obligatorio-y-plantilla) | P008-T002: layout unificado obligatorio y plantilla | P008 |
| [D090](#d090--p008-t003-rutas-del-ejecutor-paridad-de-diagramas-y-propuestas-de-adr) | P008-T003: rutas del ejecutor, paridad de diagramas y propuestas de ADR | P008 |
| [D091](#d091--p008-t004-cierre-y-archivo-unificados-con-planificación-posterior) | P008-T004: cierre y archivo unificados con planificación posterior | P008 |
| [D092](#d092--p008-t005-prompts-y-definición-bajo-el-contrato-unificado) | P008-T005: prompts y definición bajo el contrato unificado | P008 |
| [D093](#d093--p008-t006-api-y-ui-del-contrato-unificado) | P008-T006: API y UI del contrato unificado | P008 |
| [D094](#d094--p008-t007-agentsmd-en-el-prompt-congelado-de-cada-rol) | P008-T007: AGENTS.md en el prompt congelado de cada rol | P008 |
| [D095](#d095--p008-t008-perfiles-declarados-en-local-config-4) | P008-T008: perfiles declarados en local-config-4 | P008 |
| [D096](#d096--p008-t009-inventario-de-importación-desde-el-árbol-de-head) | P008-T009: inventario de importación desde el árbol de HEAD | P008 |
| [D097](#d097--p008-t010-mapa-de-normalización-del-flujo-a) | P008-T010: mapa de normalización del Flujo A | P008 |
| [D098](#d098--p008-t011-conversación-de-importación-con-borradores-privados) | P008-T011: conversación de importación con borradores privados | P008 |
| [D099](#d099--flujo-a-activación-d027-antes-de-la-importación) | Flujo A: activación D027 antes de la importación | P008 |
| [D100](#d100--p008-t012-importación-confirmada-y-continuidad-del-flujo-a) | P008-T012: importación confirmada y continuidad del Flujo A | P008 |
| [D101](#d101--p008-t013-inventario-estático-del-flujo-b-y-propuesta-de-perfil) | P008-T013: inventario estático del Flujo B y propuesta de perfil | P008 |
| [D102](#d102--p008-t014-ingeniería-inversa-sobre-head-y-borradores-privados) | P008-T014: ingeniería inversa sobre HEAD y borradores privados | P008 |
| [D103](#d103--p008-t015-incorporación-confirmada-del-flujo-b) | P008-T015: incorporación confirmada del Flujo B | P008 |
| [D104](#d104--revisión-de-salida-de-p008-con-hallazgos-en-el-flujo-a) | Revisión de salida de P008 con hallazgos en el Flujo A | P008 |
| [D105](#d105--p008-t016-frontera-git-y-bytes-confirmados-en-las-importaciones) | P008-T016: frontera Git y bytes confirmados en las importaciones | P008 |
| [D106](#d106--p008-t017-referencias-vigentes-sin-cambiar-contratos) | P008-T017: referencias vigentes sin cambiar contratos | P008 |
| [D107](#d107--segunda-revisión-de-salida-de-p008) | Segunda revisión de salida de P008 | P008 |
| [D108](#d108--p008-t018-lecturas-de-importación-sin-lazy-fetch) | P008-T018: lecturas de importación sin lazy-fetch | P008 |
| [D109](#d109--tercera-revisión-de-salida-de-p008) | Tercera revisión de salida de P008 | P008 |
| [D110](#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout) | P008-T019: gitlinks rechazados antes de inspeccionar el checkout | P008 |
| [D111](#d111--cuarta-revisión-de-salida-de-p008) | Cuarta revisión de salida de P008 | P008 |
| [D112](#d112--p008-t020-escritor-de-importaciones-con-objetos-locales) | P008-T020: escritor de importaciones con objetos locales | P008 |
| [D113](#d113--quinta-revisión-de-salida-de-p008) | Quinta revisión de salida de P008 | P008 |
| [D114](#d114--cierre-documental-manual-de-p008) | Cierre documental manual de P008 | P008 |
| [D115](#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto) | P009: Django desde cero, carpeta de proyectos y agentes por proyecto | P009 |
| [D116](#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada) | P009-T001: autoridad de creación, presets por proyecto y preparación separada | P009 |
| [D117](#d117--p009-t002-carpeta-persistente-y-creación-con-intención-previa) | P009-T002: carpeta persistente y creación con intención previa | P009 |

| [D118](#d118--p009-t003-presets-v5-y-selección-de-agentes-por-proyecto) | P009-T003: presets v5 y selección de agentes por proyecto | P009 |
| [D119](#d119--p009-t004-receta-django-confirmada-y-entorno-acreditado) | P009-T004: receta Django confirmada y entorno acreditado | P009 |
| [D120](#d120--p009-t005-ensayo-temporal-con-cli-falsas-y-django-real) | P009-T005: ensayo temporal con CLI falsas y Django real | P009 |
| [D121](#d121--p009-t006-propuesta-del-piloto-y-caracterización-previa-de-cli) | P009-T006: propuesta del piloto y caracterización previa de CLI | P009 |
| [D122](#d122--p009-t013-codex-01630-y-claude-21304-en-el-baseline-cli-12) | P009-T013: Codex 0.163.0 y Claude 2.1.304 en el baseline `cli-12` | P009 |
| [D123](#d123--p009-t007-detenida-codex-rechaza-la-definición-en-un-hijo-sin-git) | P009-T007: detenida; Codex rechaza la definición en un hijo sin Git | P009 |
| [D124](#d124--p009-t014-cli-13-codex-define-un-proyecto-nuevo-fuera-de-git) | P009-T014: `cli-13`, Codex define un proyecto nuevo fuera de Git | P009 |
| [D125](#d125--p009-t016-suite-pytest-en-paralelo-y-git-sin-fork) | P009-T016: suite pytest en paralelo y Git sin fork | P009 |
| [D126](#d126--p009-t015-el-wheel-se-verifica-con-la-definición-d088) | P009-T015: el wheel se verifica con la definición D088 | P009 |
| [D127](#d127--p009-t007-completada-django-creado-desde-la-ui-con-revisor-codex) | P009-T007: completada; Django creado desde la UI con revisor Codex | P009 |
| [D128](#d128--p009-t008-detenida-una-ruta-de-directorio-no-cubre-sus-archivos) | P009-T008: detenida; una ruta de directorio no cubre sus archivos | P009 |
| [D129](#d129--p009-t017-una-ruta-de-directorio-se-congela-como-dir) | P009-T017: una ruta de directorio se congela como `dir/**` | P009 |
| [D130](#d130--p009-t018-el-recibo-de-preparación-compara-el-inodo-no-el-dispositivo) | P009-T018: el recibo de preparación compara el inodo, no el dispositivo | P009 |
| [D131](#d131--p009-t008-completada-codexcodex-committed) | P009-T008: completada; Codex→Codex COMMITTED | P009 |
| [D132](#d132--p009-t009-detenida-el-ejecutor-claude-no-puede-cumplir-ruff-format) | P009-T009: detenida; el ejecutor Claude no puede cumplir `ruff format` | P009 |
| [D133](#d133--p009-t019-el-harness-formatea-con-la-herramienta-del-perfil-tras-cada-turno-del-ejecutor) | P009-T019: el harness formatea con la herramienta del perfil tras cada turno del ejecutor | P009 |
| [D134](#d134--p009-t009-completada-codexclaude-committed) | P009-T009: completada; Codex→Claude COMMITTED | P009 |
| [D135](#d135--p009-t020-encolar-desde-los-documentos-con-notas-adicionales) | P009-T020: encolar desde los documentos, con notas adicionales | P009 |
| [D136](#d136--p009-t010-completada-claudeclaude-committed) | P009-T010: completada; Claude→Claude COMMITTED | P009 |
| [D137](#d137--p009-t011-completada-claudecodex-committed) | P009-T011: completada; Claude→Codex COMMITTED | P009 |
| [D138](#d138--p009-t012-qa-correcto-y-cierre-detenido-por-revise-documental) | P009-T012: QA correcto y cierre detenido por REVISE documental | P009 |
| [D139](#d139--p009-t012-completada-piloto-django-con-p001-cerrada-y-archivada) | P009-T012: completada; piloto Django con P001 cerrada y archivada | P009 |
| [D140](#d140--cierre-documental-manual-de-p009) | Cierre documental manual de P009 | P009 |
| [D141](#d141--p010-consolidación-de-la-primera-versión-local) | P010: consolidación de la primera versión local | P010 |
| [D142](#d142--p010-t001-receta-typescript-proyección-de-runs-y-tarea-t011) | P010-T001: receta TypeScript, proyección de runs y tarea T011 | P010 |
| [D143](#d143--p010-t002-receta-typescript-web-recipe-1-implementada) | P010-T002: receta `typescript-web-recipe-1` implementada | P010 |
| [D144](#d144--p010-t003-proyección-run-projection-1-implementada) | P010-T003: proyección `run-projection-1` implementada | P010 |
| [D145](#d145--p010-t011-métricas-y-vista-previa-de-exportación-sobre-la-proyección) | P010-T011: métricas y vista previa de exportación sobre la proyección | P010 |
| [D146](#d146--p010-t004-marcadores-opcionales-en-la-definición) | P010-T004: marcadores opcionales en la definición | P010 |
| [D147](#d147--p010-t005-evidencia-histórica-de-una-fase-cerrada) | P010-T005: evidencia histórica de una fase cerrada | P010 |
| [D148](#d148--p010-t006-documentación-de-instalación-y-alcance-soportado) | P010-T006: documentación de instalación y alcance soportado | P010 |
| [D149](#d149--p010-t007-matriz-de-aceptación-sse-por-cursor-y-tarea-t012) | P010-T007: matriz de aceptación, SSE por cursor y tarea T012 | P010 |
| [D150](#d150--p010-t012-migración-explícita-de-bases-desde-la-cli-instalada) | P010-T012: migración explícita de bases desde la CLI instalada | P010 |
| [D151](#d151--p010-t008-validación-real-complementaria-aplazada) | P010-T008: validación real complementaria aplazada | P010 |
| [D152](#d152--p010-t009-paquete-final-verificado-y-dictamen-favorable) | P010-T009: paquete final verificado y dictamen favorable | P010 |
| [D153](#d153--cierre-documental-de-p010-y-de-la-primera-versión-local) | Cierre documental de P010 y de la primera versión local | P010 |
| [D154](#d154--p011-preparación-para-apertura-pública-en-github) | P011: preparación para apertura pública en GitHub | P011 |
| [D155](#d155--p011-retirada-del-harness-anterior-y-dos-vías-de-alta) | P011: retirada del harness anterior y dos vías de alta | P011 |
| [D156](#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020) | Planificación de P011 finalizada y modo continuo aplazado a v0.2.0 | P011 |
| [D157](#d157--repositorio-público-nuevo-y-continuidad-del-desarrollo) | Repositorio público nuevo y continuidad del desarrollo | P011 |
| [D158](#d158--idioma-visual-global-y-trabajo-inmutable-por-proyecto) | Idioma visual global y trabajo inmutable por proyecto | P011 |
| [D159](#d159--p011-t001-contrato-de-idiomas-fuentes-y-corte-público) | P011-T001: contrato de idiomas, fuentes y corte público | P011 |
| [D160](#d160--p011-t002-licencia-mit-y-frontera-del-contenido-publicable) | P011-T002: licencia MIT y frontera del contenido publicable | P011 |
| [D161](#d161--p011-t019-retirada-legacya-y-compatibilidad-no-destructiva) | P011-T019: retirada legacy/A y compatibilidad no destructiva | P011 |
| [D162](#d162--p011-t003-núcleo-y-perfiles-en-inglés-sin-cambiar-comportamiento) | P011-T003: núcleo y perfiles en inglés sin cambiar comportamiento | P011 |
| [D163](#d163--p011-t004-backend-en-inglés-y-recetas-v2-sin-cablear) | P011-T004: backend en inglés y recetas v2 sin cablear | P011 |
| [D164](#d164--p011-t005-cliente-scripts-y-ejemplos-en-inglés) | P011-T005: cliente, scripts y ejemplos en inglés | P011 |
| [D165](#d165--p011-t006-pruebas-y-fixtures-en-inglés-sin-tocar-datos) | P011-T006: pruebas y fixtures en inglés sin tocar datos | P011 |
| [D166](#d166--p011-t007-preferencias-globales-de-idioma-catálogos-y-visual-congelado-por-job) | P011-T007: preferencias globales de idioma, catálogos y visual congelado por job | P011 |
| [D167](#d167--p011-t008-idioma-de-trabajo-inmutable-por-raíz-y-par-congelado-por-job-e-intento) | P011-T008: idioma de trabajo inmutable por raíz y par congelado por job e intento | P011 |
| [D168](#d168--p011-t020-recetas-v2-en-local-config-6-con-el-idioma-de-trabajo-sellado-en-plan-y-recibo) | P011-T020: recetas v2 en local-config-6 con el idioma de trabajo sellado en plan y recibo | P011 |
| [D169](#d169--p011-t009-directiva-de-idioma-sellada-y-documentos-generados-en-el-idioma-de-trabajo) | P011-T009: directiva de idioma sellada y documentos generados en el idioma de trabajo | P011 |
| [D170](#d170--p011-t010-interfaz-enes-por-catálogos-tipados-y-diagnósticos-http-propios-en-el-visual-guardado) | P011-T010: interfaz en/es por catálogos tipados y diagnósticos HTTP propios en el visual guardado | P011 |
| [D171](#d171--p011-t021-textos-propios-del-servicio-y-la-cli-en-el-visual-de-cada-emisión) | P011-T021: textos propios del servicio y la CLI en el visual de cada emisión | P011 |
| [D172](#d172--p011-t022-textos-de-servicio-ya-ingleses-en-enes-y-rechazos-por-código) | P011-T022: textos de servicio ya ingleses en en/es y rechazos por código | P011 |
| [D173](#d173--p011-t011-detección-automática-de-cli-mínimos-y-contrato-por-capacidades) | P011-T011: detección automática de CLI, mínimos y contrato por capacidades | P011 |
| [D174](#d174--p011-t012-clientes-automáticos-y-compatibilidad-condicionada) | P011-T012: clientes automáticos y compatibilidad condicionada | P011 |
| [D175](#d175--p011-t013-diagramas-contrastados-con-el-código-sin-cambiar-el-producto) | P011-T013: diagramas contrastados con el código sin cambiar el producto | P011 |
| [D176](#d176--p011-t014-baseline-pública-en-docspublic-y-readme-inglés-de-primer-uso) | P011-T014: baseline pública en `docs/public/` y README inglés de primer uso | P011 |
| [D177](#d177--p011-t023-documentación-técnica-pública-autocontenida-en-inglés) | P011-T023: documentación técnica pública autocontenida en inglés | P011 |
| [D178](#d178--p011-t015-paquete-candidato-010-ci-sintética-e-instantánea-pública) | P011-T015: paquete candidato 0.1.0, CI sintética e instantánea pública | P011 |
| [D179](#d179--p011-t016-primer-uso-ensayado-pylock-y-validación-de-tarea-igual-al-perfil) | P011-T016: primer uso ensayado, pylock y validación de tarea igual al perfil | P011 |
| [D180](#d180--p011-t024-qa-de-navegador-del-candidato-y-tres-correcciones-de-presentación) | P011-T024: QA de navegador del candidato y tres correcciones de presentación | P011 |
| [D181](#d181--p011-t017-dictamen-favorable-y-expediente-de-apertura-pública) | P011-T017: dictamen favorable y expediente de apertura pública | P011 |
| [D182](#d182--cierre-documental-de-p011-y-preparación-pública-archivada) | Cierre documental de P011 y preparación pública archivada | P011 |
| [D183](#d183--p012-validación-real-previa-a-la-apertura-pública) | P012: validación real previa a la apertura pública | P012 |
| [D184](#d184--p012-t001-propuesta-operativa-y-codex-01640) | P012-T001: propuesta operativa y Codex 0.164.0 | P012 |
| [D185](#d185--p012-t002-autorizada-y-detenida-por-caché-django-incompleta) | P012-T002: autorizada y detenida por caché Django incompleta | P012 |
| [D186](#d186--p012-t002-descargas-autorizadas-y-falso-rechazo-de-choices-multilínea) | P012-T002: descargas autorizadas y falso rechazo de choices multilínea | P012 |
| [D187](#d187--p012-t008-listas-multilínea-en-el-preflight-cli) | P012-T008: listas multilínea en el preflight CLI | P012 |
| [D188](#d188--p012-t002-preflight-corregido-aprobado-y-parada-en-la-apertura-de-chrome) | P012-T002: preflight corregido aprobado y parada en la apertura de Chrome | P012 |
| [D189](#d189--p012-t002-rechazo-cross-site-también-desde-la-barra-de-chrome) | P012-T002: rechazo cross-site también desde la barra de Chrome | P012 |
| [D190](#d190--p012-t002-acceso-manual-al-login-y-diagnóstico-local-sin-cabeceras) | P012-T002: acceso manual al login y diagnóstico local sin cabeceras | P012 |
| [D191](#d191--p012-t002-incorporación-b-confirmada-y-parada-del-escritor-codex) | P012-T002: incorporación B confirmada y parada del escritor Codex | P012 |
| [D192](#d192--p012-t009-entorno-del-escritor-y-continuidad-con-fixture-limpio) | P012-T009: entorno del escritor y continuidad con fixture limpio | P012 |
| [D193](#d193--p012-t002-fixture-limpio-incorporado-y-rechazo-por-ruff) | P012-T002: fixture limpio incorporado y rechazo por Ruff | P012 |
| [D194](#d194--p012-t010-formateador-declarativo-optativo-en-local-config-8) | P012-T010: formateador declarativo optativo en local-config-8 | P012 |
| [D195](#d195--p012-t002-continuación-con-formateador-y-preparación-operativa) | P012-T002: continuación con formateador y preparación operativa | P012 |
| [D196](#d196--p012-t011-paridad-del-selector-de-presets-ui-con-local-config-8) | P012-T011: paridad del selector de presets UI con local-config-8 | P012 |
| [D197](#d197--p012-t002-propuesta-de-continuación-tras-t011) | P012-T002: propuesta de continuación tras T011 | P012 |
| [D198](#d198--p012-t002-tarea-real-committed-con-perfil-declarado-v8) | P012-T002: tarea real COMMITTED con perfil declarado v8 | P012 |
| [D199](#d199--p012-t003-confirmación-en-cola-con-supervisor-detenido) | P012-T003: confirmación en cola con supervisor detenido | P012 |
| [D200](#d200--p012-t003-chat-real-y-backup-restaurado-con-límite-de-ui) | P012-T003: chat real y backup restaurado con límite de UI | P012 |
| [D201](#d201--p012-t012-vista-ui-de-consulta-planificada) | P012-T012: vista UI de consulta planificada | P012 |
| [D202](#d202--p012-t012-vista-ui-de-consulta-implementada) | P012-T012: vista UI de consulta implementada | P012 |
| [D203](#d203--p012-t003-parada-previa-al-build-por-identidad-histórica-del-host) | P012-T003: parada previa al build por identidad histórica del host | P012 |
| [D204](#d204--p012-t003-consulta-ui-restaurada-verificada-con-salvedad-autorizada) | P012-T003: consulta UI restaurada verificada con salvedad autorizada | P012 |
| [D205](#d205--p012-t004-propuesta-con-base-independiente-y-sucesora-vacía) | P012-T004: propuesta con base independiente y sucesora vacía | P012 |
| [D206](#d206--p012-t004-receta-completada-y-parada-por-preparation_required) | P012-T004: receta completada y parada por preparation_required | P012 |
| [D207](#d207--p012-t013-vínculo-del-recibo-tras-resolución-cli) | P012-T013: vínculo del recibo tras resolución CLI | P012 |
| [D208](#d208--p012-t004-tarea-committed-y-check-sin-ready) | P012-T004: tarea COMMITTED y check sin READY | P012 |
| [D209](#d209--p012-t004-estado-documental-confirmado-y-cierre-real-del-hijo) | P012-T004: estado documental confirmado y cierre real del hijo | P012 |

| [D210](#d210--p012-t005-alcance-público-y-candidato-verificados) | P012-T005: alcance público y candidato verificados | P012 |
| [D211](#d211--p012-t006-dictamen-favorable-y-expediente-actualizado) | P012-T006: dictamen favorable y expediente actualizado | P012 |
| [D212](#d212--cierre-documental-de-p012-y-validación-real-archivada) | Cierre documental de P012 y validación real archivada | P012 |
| [D213](#d213--mantenimiento-git-desactivado-en-fixtures-de-incorporación) | Mantenimiento Git desactivado en fixtures de incorporación | Sin fase |
| [D214](#d214--candidato-público-actualizado-tras-la-corrección-de-ci) | Candidato público actualizado tras la corrección de CI | Sin fase |
| [D215](#d215--p013-instalación-guiada-y-configuración-desde-la-ui) | P013: instalación guiada y configuración desde la UI | P013 |
| [D216](#d216--p013-t001-instalación-aislada-y-arranque-sin-configuración) | P013-T001: instalación aislada y arranque sin configuración | P013 |
| [D217](#d217--p013-t001-archivos-versionados-y-activación-de-configuración) | P013-T001: archivos versionados y activación de configuración | P013 |
| [D218](#d218--p013-t001-perfil-tras-contexto-y-preparación-antes-de-activar) | P013-T001: perfil tras contexto y preparación antes de activar | P013 |
| [D219](#d219--p013-t002-instalador-por-generaciones-y-paquete-autocontenido) | P013-T002: instalador por generaciones y paquete autocontenido | P013 |
| [D220](#d220--p013-t003-arranque-instalado-y-exclusión-de-instancia) | P013-T003: arranque instalado y exclusión de instancia | P013 |
| [D221](#d221--p013-t004-journal-y-referencias-de-configuración) | P013-T004: journal y referencias de configuración | P013 |
| [D222](#d222--p013-t005-asistente-api-y-arranque-con-autoridad-global-versionada) | P013-T005: asistente API y arranque con autoridad global versionada | P013 |
| [D223](#d223--p013-t006-asistente-y-editor-global-con-confirmaciones-exactas) | P013-T006: asistente y editor global con confirmaciones exactas | P013 |

## D001 — Alcance local y arquitectura base

Estado: base aceptada por el usuario el 2026-10-11.

Desarrollar para uso local individual, conservando Python y extrayendo el motor existente. FastAPI, SQLite y React/TypeScript forman el stack propuesto en la especificación aceptada. La nube queda abierta a futuro, sin implementación preventiva.

## D002 — Desarrollo manual

Estado: confirmado por el usuario.

Codex y Claude Code ayudan a desarrollar el producto mediante sesiones dirigidas por el usuario. No usar el harness para construirlo. Ambos pueden implementar; sus roles dentro del producto no se imponen a estas sesiones.

## D003 — Cola local sin Celery

Estado: aclaración del diseño inicial; revisable si cambian requisitos.

El supervisor local ejecuta jobs persistidos en SQLite. Que una tarea dure mucho o continúe al cerrar el navegador no exige Celery. No hay una fase comprometida para añadirlo.

Reconsiderar Celery si aparece necesidad demostrada de workers independientes/distribuidos, varios hosts o un despliegue con volumen que lo justifique. Esa decisión debe incluir broker, semántica de entrega, idempotencia, cancelación, recuperación y migración de almacenamiento. Celery no sustituye la máquina de estados ni resuelve por sí solo aprobaciones y control de procesos.

Referencia: [introducción oficial de Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html).

## D004 — Servicio nativo, Docker por perfil

Estado: aclaración del despliegue inicial; revisable.

API, supervisor y CLI de agentes se ejecutan directamente en el Mac. En desarrollo, Vite sirve la UI; al empaquetar, el servicio sirve assets compilados. SQLite y artefactos permanecen en almacenamiento local.

Docker es opcional para dependencias y validaciones de proyectos gestionados, por ejemplo PostgreSQL y Django en el perfil ReferenceProject. No es requisito de todos los perfiles ni del núcleo. No crear un Dockerfile/Compose vacío como parte del arranque documental.

Contenerizar todo el servicio requiere resolver CLI, credenciales, mounts, propietarios de archivos, procesos y diferencias host/contenedor. Un contenedor no dispone automáticamente de las herramientas ni del contexto del Mac. No montar el socket Docker ni credenciales globales por comodidad. Valorar empaquetado en H5 si existe una necesidad concreta.

Referencia: [red y límites host/contenedor en Docker Desktop](https://docs.docker.com/desktop/features/networking/).

## D005 — Comenzar por H0.1

Estado: secuencia de trabajo inicial.

La documentación permite empezar. Completar inventario y fixtures antes de construir API/UI o portar el motor. Las versiones exactas, contratos de proveedores y autenticación se verificarán en H0.2; su incertidumbre no bloquea H0.1.

## D006 — Evidencias legacy y fixtures de H0.1

Estado: convención de inventario adoptada el 2026-10-11.

Identificar la referencia por commit y SHA-256 local/HEAD separados en
`docs/discovery/baseline.json`. Los fixtures son checkouts imaginarios independientes;
solo los cuatro esquemas estáticos se copian de la referencia. El manifest de
fixtures describe muestras y ausencias, no es un contrato operativo nuevo.
Los extractos Git sintéticos se mantienen fuera de los runs: legacy no escribe
un resultado persistido de aceptación/cierre que certifique el commit.

No equiparar iteración de evidencia a invocación de agente, ACCEPT a commit,
READY a cierre, ni stop operativo a review. Preservar campos ausentes/null sin
rellenarlos con defaults actuales o cero. `contract_source` es una extensión
producida por el planificador determinista aunque no figure en su schema de
respuesta. Estos hechos guiarán la importación de lectura; no definen aún los
modelos futuros ni implementan el importador. Detalles en `discovery/LEGACY_FORMATS.md`.

La verificación de esta entrega usa cuatro checks de biblioteca estándar, solo
datos locales y sin procesos/red. Versiones y dependencias del producto siguen
pendientes de H0.2.

## D007 — Baseline de versiones H0.2

Estado: seleccionado y resuelto el 2026-10-11; instalación del subconjunto usado
comprobada en H0.3 (D011).

Usar CPython 3.14.4 estándar, uv 0.12.19, Node 24.15.0 y npm 11.12.1 en el
Mac actual. Pins directos y fuentes en
[H0.2_COMPATIBILITY.md](archive/phase-001/H0.2_COMPATIBILITY.md); restricciones y
resolución conjunta en [snapshot](archive/phase-001/h0.2-version-metadata.json).
TypeScript queda en 5.9.3 porque openapi-typescript 7.13.0 requiere `^5.x`.
Codex 0.161.0 y Claude Code 2.1.295 son el baseline observado; versiones nuevas
exigirán comprobar capacidades, no trasladar flags legacy por suposición.

La resolución temporal sin instalación de H0.2 comprueba disponibilidad y
restricciones, no ejecución del stack. H0.3 creó locks y verificó instalación,
arranque y build al introducir el esqueleto; [evidencias](archive/phase-001/H0.3_SKELETON.md).
Los parsers H0.2 siguen usando biblioteca estándar.

## D008 — Suscripciones propias mediante CLI

Estado: confirmado por el usuario durante H0.2 el 2026-10-11.

La integración inicial usará las suscripciones de cada usuario mediante Codex
y Claude Code instalados y autenticados en su ordenador. Cada CLI conserva
su autenticación; Harness Local no extrae tokens ni ofrece un login propio.
No sustituir suscripciones por API de pago, cambiar modelo/proveedor ni renovar
un intento silenciosamente ante error de autenticación o cuota.

Codex login status reporta ChatGPT; el usuario confirma también Claude
autenticado. El status de Claude ejecutado en sandbox reportó falta de sesión:
conservar esa observación y su límite sin concluir que el Mac carece de login.
No se necesita conocer plan exacto, correo ni identificadores para H0.2.

App Server queda como candidato documentado con ChatGPT gestionado por Codex,
sin iniciar servidor ni implementar login. Claude Agent SDK no se habilita con
la suscripción por inferencia: su documentación de terceros exige API salvo
aprobación previa. La documentación legal actual contempla ejecutar el binario
CLI publicado con credenciales propias del usuario bajo sus condiciones;
esto no habilita ofrecer login claude.ai propio en el SDK. Reevaluar antes de
distribuir o introducir SDK/login propio.
Fuentes: [Codex auth](https://learn.chatgpt.com/docs/auth),
[App Server](https://learn.chatgpt.com/docs/app-server),
[Claude auth](https://code.claude.com/docs/en/authentication),
[integración CLI](https://code.claude.com/docs/en/legal-and-compliance),
[SDK](https://code.claude.com/docs/en/agent-sdk/overview).

## D009 — Sonda offline de streams y permisos

Estado: comprobado offline en H0.2; adaptadores de producto pendientes.

Un mensaje de agente no certifica fin de intento. La sonda requiere terminal
conocido y exit code cero, conserva bytes/eventos/cola y campos desconocidos,
y no rellena telemetría ausente. Errores, salida inválida o incompleta nunca
certifican éxito. `complete` es fin de stream, no aceptación de tarea ni commit.
La sonda vive bajo `tests/`, no lanza procesos ni realiza reintentos/fallback.
No demuestra ausencia de reintentos internos de las CLI; caracterizarlos en H2.3.

`dontAsk` es denegación para peticiones no resueltas, no aprobación interactiva.
En CLI inicial, conceder permisos afecta un intento posterior explícito. SDK
puede tener callback condicionado por política, pero no está integrado ni
habilitado. Fuentes y límites en la matriz H0.2; [política oficial](https://code.claude.com/docs/en/agent-sdk/permissions).

## D010 — Simulación H0.3 separada del motor y del legacy

Estado: implementado y comprobado el 2026-10-11.

H0.3 usa un caso de uso síncrono e inmediato con adaptador determinista sin
procesos/red/checkouts. La tabla `simulations` guarda un resultado completo y
sus mensajes atómicamente; `completed` significa solo fin de simulación.
No introduce estados de intentos, aceptación, commits, modelos o consumo
ficticios. El motor, jobs persistidos y exclusión por checkout se implementarán
en H2; no usar este endpoint como mecanismo para ejecutar agentes en background.

El núcleo contiene dataclasses, protocolos y casos de uso de biblioteca estándar;
Pydantic/FastAPI, SQLAlchemy y adaptadores quedan fuera. El futuro importador
H1.1 mantiene su índice de observación separado de los resultados simulados,
sin convertir estos en intentos ni crear doble autoridad. Migraciones explícitas
con el servicio detenido; el arranque no usa `create_all` y rechaza esquemas
no preparados. [Alcance y evidencia](archive/phase-001/H0.3_SKELETON.md).

## D011 — Instalación y fuente de contratos del esqueleto

Estado: implementado y comprobado el 2026-10-11.

`src/harness_local` se instala como paquete mediante `uv_build==0.12.19`;
locks uv/npm versionados y dependencias locales aisladas. Se conservan pins H0.2
solo para componentes usados: no añadir PyYAML, Vitest o Playwright sin uso.
pytest/HTTPX se usan para las comprobaciones de API y persistencia. El aviso de
deprecación de Starlette sobre HTTPX queda visible; revisar al modificar de
nuevo esas pruebas, sin cambiar el baseline silenciosamente.

Los esquemas Pydantic del límite HTTP son la fuente de OpenAPI. Exportar sin
servicio/SQLite y generar los tipos con openapi-typescript; versionar ambos
artefactos, comprobar su sincronización y no mantener copias manuales de los
contratos en React. Uvicorn sirve assets compilados; Vite usa proxy `/api` en
desarrollo, con ambos servicios enlazados a loopback. Comandos verificados en
README/AGENTS; H0.3 no habilita SDK, proveedores ni distribución.

## D012 — Índice legacy por evidencia, con relectura explícita

Estado: implementado y comprobado en H1.1 el 2026-10-11.

En observación, SQLite guarda la última lectura por raíz canónica y ruta relativa,
identidad de directorio de run, SHA-256/tamaño, objetos JSON completos y diagnóstico
local. Unicidad por ruta evita duplicados; un cambio de hash reemplaza la observación
actual. Los originales son autoridad y mantienen el historial; el índice se puede
reconstruir. Las simulaciones H0.3 siguen en una tabla separada. No crear intentos de
agente a partir de índices de review/validación, ni estados de aceptación/commit/cierre
por interpretar ACCEPT o READY. Identidades de tarea/fase se conservan en los payloads.

Campos ausentes y null se etiquetan «no registrado» con procedencia distinta; cero
reportado sigue siendo cero. JSON/UTF-8 inválido queda pendiente de relectura; errores
locales se diagnostican por archivo y no abortan el resto ni declaran fallo del agente.
Las ausencias de compañeros de evidencia son observaciones, no requisitos incumplidos.
Un archivo desaparecido pierde el payload actual del índice. Enlaces no se siguen;
texto/logs/diffs se referencian por ruta/hash sin copiar sus cuerpos. La CLI rechaza
SQLite dentro del checkout de origen antes de conectar para mantener lectura de origen.

`legacy-import` y `legacy-summary` son entradas explícitas locales, sin watcher ni
navegación web. Consulta no relee archivos; reconstrucción/relectura requiere importar.
H1.3 resolverá actualización incremental; H1.2 resolverá navegación sobre evidencias.
No se acredita consistencia frente a escritores concurrentes ni transición a modo
gestionado. [Entrega y verificaciones](archive/phase-002/H1.1_IMPORT.md).

## D013 — Navegación de observación y contenido vinculado al hash

Estado: implementado y comprobado en H1.2 el 2026-10-11.

La navegación usa el índice H1.1 sin añadir entidades gestionadas ni modificar su
esquema. Cada raíz canónica importada es un proyecto/origen; tareas se agrupan por
identidad del directorio, conservando todos sus runs. La identidad declarada en
task.json se muestra como evidencia independiente, sin resolver discrepancias por
inferencia. Fases proceden de directorios de run/archivo y campos phase_id o
next_phase_id del JSON observado; se ofrece una ruta de muestra por tipo de origen.
STATE/NEXT_STEPS/ROADMAP siguen accesibles como documentos, sin interpretar sus
textos como nuevas invocaciones o certificados operativos. Una tarea futura solo
documentada no aparece como tarea con ejecución observada.

Los IDs HTTP son codificaciones reversibles de raíz/ruta, acotadas al proyecto e
índice, no identidades nuevas de intentos ni secretos de autorización. Los listados
se paginan por offset en orden estable de ruta/identidad; la timeline declara ese
orden, sin timestamps de agente inferidos. JSON pointers, ruta/hash y estado local
identifican la proyección del payload indexado. Las entradas grandes se truncan
explícitamente; campos desconocidos siguen accesibles en el original por tramos.

Para servir contenido se exige una ruta indexada, se abren todos los componentes
con descriptores/O_NOFOLLOW y solo archivos regulares, y se calcula SHA-256/tamaño
por bloques antes de devolver el tramo capturado. Cambios, enlaces, desapariciones,
errores y límites devuelven diagnóstico sin texto. UTF-8 no se sustituye por bytes
ficticios. La verificación tiene un máximo de 64 MiB por petición; cada tramo relee
el archivo, sin cache de contenido. No es una certificación de snapshot entre varios
archivos ni frente a escritores concurrentes.

La UI identifica campos del índice y contenido del origen por sus propios hashes,
avisa si se reimportó desde que se abrió la lista y muestra diagnósticos/pendientes
sin juicios sobre el agente. Renderiza texto plano, nunca ejecuta históricos; no
agrega copias de consumo ni deduce factura/cuota de coste equivalente API. Reimportar
continúa siendo explícito por CLI. Watcher/SSE pertenecen a H1.3, no a esta entrega.
[Entrega y verificaciones](archive/phase-002/H1.2_NAVIGATION.md).

## D014 — Observación opt-in y feed persistido del índice

Estado: implementado y comprobado en H1.3 el 2026-10-11.

Conservar importación explícita H1.1 y permitir activar/detener observación por origen
ya importado. Un observador por polling en el servicio local agrupa cambios cada 0,5 s,
cachea archivos disponibles por metadatos, relee pendientes/errores y reconcilia los
activados al iniciar y cada 30 s. Un solo proceso Uvicorn; no añade jobs ni supervisor
del motor. Archivos originales son autoridad; última observación por ruta y runs
históricos se conservan. Una raíz inaccesible conserva el índice con diagnóstico local.

Migración `0003_legacy_observation`: control por origen y eventos de invalidación en
SQLite. Un cambio del índice y su evento se confirman juntos; comparaciones serializadas
por la primera escritura SQLite evitan eventos duplicados en importaciones idénticas.
No se abren transacciones escritoras durante lecturas del filesystem. Releer sin cambios
no genera actividad. El feed tiene IDs globales crecientes, sin purga en esta entrega;
no es event sourcing ni una copia de cada versión del archivo.

JSON paginado y SSE entregan filas confirmadas. Last-Event-ID prevalece sobre el cursor
inicial; el cliente deduplica y conserva cursor local, con recarga del índice al abrir
y ante cursores adelantados. Conexiones SSE acotadas a 15 s permiten drenaje de apagado
con reconexión por ID. La UI conserva identidades y reinicia tramos en la versión actual,
ocultando respuestas cuyo hash difiera de sus metadatos. No interpreta diagnósticos como
fallos de agente, ni ACCEPT/READY como aceptación/commit/cierre. Lecturas de evidencias
por descriptores, solo archivos regulares y máximo 64 MiB. Límites y verificaciones en
[H1.3_OBSERVATION.md](archive/phase-002/H1.3_OBSERVATION.md).

## D015 — Motor extraído aislado y recuperación explícita

Estado: implementado y caracterizado offline en H2.1 el 2026-10-11.

`ProjectContext` fija raíz canónica, rutas relativas, perfil y política. El núcleo
`core/engine` solo usa biblioteca estándar y puertos de agente, comandos y evidencia.
El perfil ReferenceProject contiene las reglas de stack, sin imports condicionales del
núcleo. No se conecta este motor a API/CLI ni a la autoridad SQLite de observación.

H2.1 conserva historial como valores inmutables y snapshots JSON por petición en
memoria. Cada invocación exige identidad/sesión nueva; no expone resume de conversación.
Revalidar conserva trabajo y solo valida/revisa; reintentar ejecución es explícito
y consume el presupuesto previo, incluso tras fallo. No cambia modelo ni repite
llamadas tras errores. H2.2 deberá persistir estas garantías atómicamente.

El contrato no se amplía ni se restauran cambios automáticamente: scope grants y
preguntas detienen el flujo para una decisión posterior. Este límite aplica las
invariantes aceptadas de contratos congelados y preservación de cambios, en lugar
de trasladar la mutación/restore del legacy. La planificación `auto` llama al
planificador solo ante contrato documental incompleto; una selección inválida o
error de proveedor detiene el flujo.

`acceptance_ready` es una decisión offline condicionada a review ACCEPT, validación,
política y evidencia vigente, nunca un commit ni estado de tarea gestionada. La
captura sintética no certifica Git; H2.4 añadirá captura completa/worktree/commit
idempotente. El formatter/helpers son declaraciones del perfil aún sin adaptador
real. [Entrega, trazabilidad y límites](archive/phase-003/H2.1_ENGINE.md).

## D016 — Autoridad gestionada y recuperación conservadora de jobs

Estado: implementado y comprobado offline en H2.2 el 2026-10-11.

Tablas `managed_*` y `checkout_locks` separadas de simulaciones/observación,
migración explícita `0004_managed_queue`. El motor admite un journal opcional
de biblioteca estándar. Intención antes de cada invocación/comando, resultado
y evento atómicos después; snapshots/contexto/contrato/versiones y presupuesto
conservados. Versiones declaradas separadas de datos observados; null no se
convierte en versión CLI ni telemetría ficticia. No activa modo gestionado
de proyectos legacy ni añade ejecución HTTP/CLI.

Idempotencia por clave de acción y payload congelado; clave repetida devuelve
el mismo job, contenido distinto da conflicto. FIFO entre jobs elegibles y un
escritor por raíz canónica dentro de la misma base; otras raíces pueden avanzar
mediante llamadas explícitas concurrentes al supervisor. Transacciones cortas
y ningún lock SQL abierto durante el motor; heartbeat con token y lease UTC.

Un lease vencido/fallo de persistencia deja RECOVERY_REQUIRED y mantiene el
bloqueo. No demuestra que terminó el escritor. Confirmar su parada exige
conciliación previa, job/token, versión esperada y evidencia registrada; entonces
se marcan intentos pendientes de resultado desconocido y se libera la raíz.
La detección/cancelación de procesos reales pertenece a H2.3. Revalidar o
reintentar requiere un job nuevo explícito; una corrección iniciada consume
presupuesto aunque caiga antes de guardar resultado. No se repite conversación,
planificación ni efecto de resultado incierto automáticamente.

DONE indica fin de acción del job; ACCEPTANCE_READY conserva la elegibilidad
offline, sin certificar commit/cierre. Exclusión cooperativa local, sin promesa
de exactamente una vez ni protección contra escritores externos/otra base.
[Entrega y pruebas](archive/phase-003/H2.2_PERSISTENCE.md).

## D017 — Adaptadores CLI opt-in y grupos persistidos

Estado: implementado y caracterizado offline en H2.3 el 2026-10-11;
smoke real autorizado ejecutado con fallo de configuración el 2026-10-11
(D018); integración exitosa con proveedores pendiente.

Codex planificador/revisor y Claude ejecutor usan CLI fijadas y nuevas sesiones.
El preflight final observa Codex 0.162.1 (H0.2 registró 0.161.0) y Claude
2.1.295. Ambas versiones Codex se admiten por selección explícita, con checks
de help y caracterización offline; nunca se cambia automáticamente una CLI
congelada al detectar otra versión. La factory debe aportar configuración cuyo
hash/versiones coincidan con el job
congelado; preflight comprueba versión/help sin acceder a autenticación. Entorno
completo y permisos explícitos por intento, sin herencia silenciosa. El prompt
transmitido y spec quedan vinculados a hashes/artefactos fuera del checkout.
No se activa ejecución gestionada desde API/CLI/UI ni proveedores automáticamente.

Migración `0005_cli_processes` conserva un propietario del supervisor y grupos por
intento. Gate por pipe: la CLI no ejecuta antes de que su identidad esté confirmada.
Intención antes de efectos, captura fsync antes de evento por rango/hash y resultado
atómico H2.2; un fallo conserva bytes e incertidumbre. Historial CLI en formato
2; lectura de formato 1 y comparación de resultados antiguos preservadas sin
reescribirlos. Cancelación TERM/KILL del
grupo, sin considerar muerte del líder prueba de muerte de sus hijos.

La confirmación explícita de parada exige comprobar ausencia de grupos y de un
propietario cuyo ámbito siga abierto. Lease vencido no libera checkout. Permiso
denegado, host distinto y PID reutilizado vivo mantienen bloqueo conservador.
No se señalizan PIDs recuperados automáticamente: la identidad no basta para
certificar que aún corresponden al mismo proceso. La garantía cubre grupos POSIX
cooperativos locales, no hijos escapados ni aislamiento físico de Claude.

El adaptador nunca relanza/fallback ante fallo. `cli-1` solicitaba retries HTTP/stream
cero mediante overrides reservados, rechazados en D018. `cli-2` elimina esos
overrides y declara los retries internos de Codex desconocidos (D019).
Claude carece de control equivalente verificado. No prometer cero retries
internos o una inferencia por invocación CLI sin medirlo con una cuenta real.
`dontAsk` sigue siendo denegación; conceder herramientas configura un intento
posterior, no responde a una operación viva. Capturas no son commits/aceptación.
Ver [entrega, fuentes y límites](archive/phase-003/H2.3_CLI.md).

## D018 — Smoke H2.3 autorizado, selección delegada y parada al primer fallo

Estado: verificación real ejecutada el 2026-10-11; fallo conservado sin relanzar.

El usuario respondió «Si, autorizo» a la propuesta de hasta tres invocaciones
reales de 60 s, Codex planificador/revisor y Claude ejecutor, suscripciones propias,
checkout nuevo bajo `/private/tmp`, sin herramientas concedidas y detención al
primer error. Después delegó la elección de modelos/esfuerzos («decídelo tú»).
Se fijaron antes de lanzar: Codex `gpt-6-luna`/`low` y Claude
`claude-sonnet-4-6`/`low`. Esta delegación permite seleccionar para este smoke;
no convierte fallos en permiso para cambiar proveedor/modelo o relanzar.

Una ejecución de `scripts/smoke_cli.py` lanzó solo el planificador Codex 0.162.1.
La CLI rechazó los overrides `model_providers.openai` por ID integrado reservado;
exit 1, stdout vacío, sin terminal ni telemetría observada. El adaptador preservó
stderr, hashes/eventos y resultado FAILED; el script conservó job/run en
RECOVERY_REQUIRED, ámbito cerrado y lock retenido. Claude y revisor no se lanzaron.

El preflight versión/help sigue siendo una comprobación local limitada: este
fallo demuestra que no certifica la validez semántica de todos los argumentos.
Corregir esa configuración y añadir regresión offline es la próxima tarea;
no se ejecuta en esta entrega ni se repite el smoke automáticamente.
La autorización acotada concluyó al primer error. No se acredita acceso al modelo,
autenticación/cuota, inferencia, retries internos ni aislamiento total.
Resultado, procedencia y límites en [H2.3_SMOKE.md](archive/phase-003/H2.3_SMOKE.md).
La corrección posterior offline se registra en D019, sin repetir esta ejecución.

## D019 — Proveedor integrado conservado y retries internos desconocidos

Estado: implementado y verificado offline el 2026-10-11; nuevo smoke no ejecutado.

La [referencia oficial](https://learn.chatgpt.com/docs/config-file/config-reference)
reserva los IDs de proveedores integrados y documenta `request_max_retries` /
`stream_max_retries` en definiciones de proveedores personalizados. No se encontró
un override compatible para exigir cero retries del integrado en las CLI fijadas.
Eliminar los dos overrides de `model_providers.openai`, conservando
`model_provider="openai"`, autenticación propia de la CLI y selección por intento.
No inventar claves ni renombrar el proveedor para cambiar de ruta de autenticación.

Capabilities y spec persistida declaran `built-in-defaults/unknown` para Codex;
los defaults documentados no son mediciones ni límites efectivos certificados.
El adaptador no relanza ni hace fallback: una invocación CLI puede tener retries
internos del proveedor que no se han medido. Esta distinción ya aplicaba a Claude;
ahora no se presenta tampoco una solicitud inválida de cero como garantía Codex.

El cambio de argv/capabilities eleva la versión del adaptador a `cli-2`.
La comparación previa al lanzamiento rechaza jobs congelados `cli-1`, sin
reescribirlos ni actualizar selecciones automáticamente. No hay migración de
esquema, cambio de codec ni alteración del resultado/evidencias de D018.
La siguiente verificación real se propone con sus límites explícitos, sin
ejecutarla dentro de la corrección offline. [Entrega](archive/phase-003/H2.3_CONFIG_FIX.md).

## D020 — Nuevo smoke autorizado y parada ante configuración MCP de Claude

Estado: verificación real ejecutada el 2026-10-12; fallo conservado sin corregir
ni relanzar. [Resultado y evidencias](archive/phase-003/H2.3_SMOKE_RETRY.md).

Tras revisar la propuesta y preflight offline, el usuario respondió «Sí, autorizo
esta ejecución»: una ejecución `cli-2`, hasta tres CLI de 60 s, modelos/esfuerzos
fijos Codex `gpt-6-luna`/`low` y Claude `claude-sonnet-4-6`/`low`, red/suscripciones
propias, checkout nuevo, herramientas vacías y parada al primer fallo. Se
explicitaron retries internos desconocidos. La autorización concluyó al error.

Codex planificador completó el transporte con terminal, exit 0, JSON y uso
reportado; no reportó modelo/esfuerzo efectivo ni coste. Claude salió con exit 1
al validar `--mcp-config '{}'`: falta `mcpServers`. Sin terminal/payload/uso Claude.
Revisor no lanzado. Run/job RECOVERY_REQUIRED, propietario cerrado, grupos
STOPPED y lock conservado; capturas/eventos/hashes y checkout intacto verificados.

Help/version no certifican semántica del argumento MCP, igual que no detectaron
los overrides Codex de D018. La siguiente tarea corrige y caracteriza offline
solo esa configuración, preservando cero servidores/herramientas y aislamiento
de fuentes/hooks. Deberá versionar el cambio para no sustituir jobs congelados
`cli-2`. No se implementa en esta verificación ni se autoriza inferencia nueva.

No se concluye éxito completo H2.3, aceptación/commit de producto, acceso/auth
Claude, ausencia de retries internos ni consumo de cuota cero a partir del fallo.
El historial D018/D019 se conserva sin convertir esta ejecución en reintento
automático. H2.4 no iniciado.

## D021 — MCP vacío explícito y versión congelada cli-3

Estado: implementado y verificado offline el 2026-10-12; smoke nuevo no ejecutado.

Claude Code 2.1.295 requiere el mapa `mcpServers` en el JSON MCP; `{}` fue
rechazado en D020. Help local y documentación oficial describen JSON inline,
el wrapper y el modo estricto. Usar `--strict-mcp-config` junto a
`--mcp-config '{"mcpServers":{}}'`: cero servidores declarados, conservando herramientas,
settings y hooks aislados por las opciones H2.3 existentes. No cambia auth,
modelos/esfuerzos, permisos, sesiones ni controles de retries.

El cambio de argv eleva el adaptador a `cli-3`: jobs congelados `cli-2` o
`cli-1` se bloquean antes de efectos sin reescribir historial/specs/resultados.
No hay migración ni cambio de codec. El executable sintético exige el mapa
independientemente del adaptador: help/version pasan con el JSON inválido,
pero la ejecución falla antes de emitir inferencia simulada. Parada tras Claude
sin revisor ni relanzamiento y preservación de resultados antiguos verificadas.

Documentación y fakes no equivalen a validación real completa del proveedor.
D020 conserva su resultado/evidencia; su autorización concluyó al fallo.
NEXT_STEPS prepara una propuesta nueva, sin ejecutarla ni consumir proveedores
dentro de esta entrega. [Contrato, fuentes y límites](archive/phase-003/H2.3_MCP_FIX.md).

## D022 — Smoke cli-3 autorizado y fallo de autenticación Claude

Estado: verificación real ejecutada el 2026-10-12; rama de error concluida,
sin login, corrección ni relanzamiento. [Informe](archive/phase-003/H2.3_SMOKE_CLI3.md).

El usuario respondió «Doy consentimiento para el smoke» tras la propuesta y
preflight offline: una ejecución, hasta tres invocaciones de 60 s, Codex
`gpt-6-luna`/`low` y Claude `claude-sonnet-4-6`/`low`, suscripciones propias,
checkout nuevo, herramientas/MCP vacíos y parada al primer fallo. Retries
internos desconocidos. Consentimiento agotado con el fallo; no habilita otro smoke.

Planificador Codex COMPLETE, terminal/exit 0/JSON y uso reportado. Claude
acepta MCP `{"mcpServers":{}}` y emite init con tools/mcp_servers vacíos y
dontAsk. Falla con `authentication_failed` y «Not logged in · Please run /login».
Terminal `result` con subtype success, pero `is_error=true` y exit 1;
FAILED/payload null persistidos correctamente. Revisor no lanzado. Ceros de
tokens/coste reportados no certifican cuota/factura ni ausencia de consumo.

Run/job RECOVERY_REQUIRED, propietario cerrado, procesos STOPPED y lock retenido;
31 eventos consecutivos, hashes/rangos/prompts y resultados comprobados tras
reabrir SQLite. Grupos muertos, checkout sintético intacto. Históricos separados.
No hay aceptación/commit de producto ni éxito real completo H2.3. H2.4 no iniciado.

El fallo de auth acredita el proceso/entorno explícito de este smoke fuera del
sandbox; no demuestra ausencia de login en otras sesiones del Mac ni establece
causa raíz. Siguiente tarea: diagnóstico local/documental de autenticación en
lectura, con salida filtrada y sin secretos, inferencia o login automático.
Una posible corrección o intervención del usuario se propondrá por separado;
no ampliar silenciosamente entorno, proveedor, permisos ni ruta de autenticación.

## D023 — USER explícito: dependencia de auth observada, corrección separada

Estado: diagnóstico en lectura completado el 2026-10-12; corrección no implementada.
[Informe y reproducción](archive/phase-003/H2.3_AUTH_DIAGNOSIS.md).

Claude 2.1.295 reconoce la sesión `claude.ai` fuera del sandbox en el contexto
de esta sesión, pero no con el entorno mínimo HOME/PATH/TMPDIR/LANG del smoke.
Añadir únicamente USER restaura status; retirarlo del entorno de la sesión
lo impide. LOGNAME no basta, cwd no explica la diferencia. La omisión de USER
es una causa reproducible local; no acredita el mecanismo interno de acceso
al llavero ni éxito del argv de inferencia. Status no admite los flags de
fuentes aisladas. El hash actual de las cuatro variables difiere del D022 y
sus valores históricos no están persistidos: no afirmar reproducción exacta.

No solicitar login como solución al estado observado: hay sesión reconocida.
Proponer corrección offline del constructor del entorno explícito del smoke,
transmitiendo USER del usuario local sin heredar credenciales ni fuentes de
settings. Nueva configuración/hash congelados y regresión sintética; cambios
de comportamiento del adaptador exigirán su versión nueva. Jobs/specs antiguos
se conservan y no se ejecutan con la configuración nueva silenciosamente.

Diagnóstico y commit no autorizan inferencia. D022 continúa fallido, con lock
retenido; no reanudar ni recuperar automáticamente. Otro smoke requerirá
propuesta/consentimiento específico después de la corrección. Sin API keys,
login propio, refresh ni cambios globales. Status no prueba cuota/modelos.
H2.4 no iniciado.

## D024 — Entorno del smoke validado por UID y hash de configuración nuevo

Estado: implementado y verificado offline el 2026-10-12.
[Informe y alcance](archive/phase-003/H2.3_ENV_FIX.md).

El constructor de `scripts/smoke_cli.py` transmite USER explícitamente junto a
HOME/PATH/TMPDIR/LANG. USER debe ser no vacío y coincidir con el nombre local
obtenido mediante `pwd.getpwuid(os.getuid())`; no se confía en LOGNAME ni se
rellena automáticamente. Ausencia/discrepancia o UID no resoluble terminan
con diagnóstico antes de crear área, resolver CLI, preflight o consumir.
No se heredan credenciales, selectores ni fuentes de configuración.

El adaptador mantiene el mapping completo recibido y no incorpora variables
del supervisor. Su comportamiento/argv permanecen `cli-3`; el hash congelado
de CLIConfig cambia por USER. La comparación existente bloquea configuraciones
anteriores antes del preflight sin migración ni reescritura. Regresión con
proceso independiente reproduce el fallo previo, permite el recorrido sintético
corregido y verifica filas SQL exactas, specs, resultados y capturas antiguas.
Permisos, sesiones nuevas, selecciones y ausencia de fallback conservados.

D020/D022 y locks conservados; D018 ausente no reconstruido. D023 acredita
una dependencia local en status, no el mecanismo de auth ni inferencia aislada.
La corrección offline tampoco prueba auth/cuota/modelo ni éxito completo H2.3.
Sin status, login, secretos, CLI reales, recuperación o cambios globales.
Propuesta posterior separada (archivo `docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md`) pendiente
de consentimiento específico; no ejecutar por la corrección o su commit.
H2.4 no iniciado.

## D025 — Smoke autorizado con USER: tres transportes completos

Estado: verificación real completada el 2026-10-12.
[Resultado y evidencias](archive/phase-003/H2.3_ENV_SMOKE.md).

El usuario indicó «Procede con el smoke» para la propuesta D024: una ejecución,
hasta tres invocaciones de 60 s, Codex `gpt-6-luna`/`low` como planificador/revisor
y Claude `claude-sonnet-4-6`/`low` como ejecutor, suscripciones propias y checkout
nuevo. USER comprobado contra UID local; resto del entorno, MCP/tools vacíos,
fuentes/hooks aislados y sesiones nuevas conservados. Retries internos desconocidos.

Las tres invocaciones completaron terminal, exit 0 y JSON `smoke-ok`; Claude
supera el fallo de auth D022 en este proceso/entorno y reporta respuesta/modelo/
uso/coste de lista. Esos datos no certifican factura/cuota ni esfuerzo efectivo.
Codex no reporta modelo efectivo/coste; no se sustituyen datos ausentes.

SQLite conserva 57 eventos, resultados/requests/specs/hash exactos tras reabrir,
owner cerrado y procesos STOPPED/dead. Job DONE y run STOPPED por fin deliberado
del smoke, sin aceptación. Lock nuevo liberado por finalización normal;
D020/D022 y sus locks/archivos permanecen intactos. Sin herramientas ni cambios
de checkout, sin fallback, login, relanzamiento o recuperación de históricos.

H2.3 acredita transporte real de tres roles en este contexto, no tarea real,
review ACCEPT, validación Git ni commit de producto. Autorización satisfecha por
esta única ejecución; otro consumo requerirá consentimiento propio. No se
certifican retries internos, aislamiento físico, cuota, permisos vivos ni
cancelación/timeout reales. Siguiente tarea H2.4 offline definida, sin iniciarla.

## D026 — Evidencia Git por árboles y commit determinista conciliable

Estado: implementado y verificado offline el 2026-10-12.
[Entrega, protocolo y límites](archive/phase-003/H2.4_GIT.md).

La evidencia de contenido de un checkout Git se define por identificadores de
árbol: base (`HEAD`), `worktree_tree` (lo que `git add -A` registraría, copia
temporal del índice) e `index_tree` (índice real). El fingerprint vincula los tres;
el staging forma parte de lo revisado y cambiarlo invalida la aceptación. El parche
completo y su SHA-256 se guardan en la evidencia; no se trunca (fallo de evidencia
si supera el límite). Gitlinks, índices con conflictos y rutas no UTF-8 detienen el
flujo. `SyntheticWorkspace` no certifica Git ni puede respaldar un commit.

El commit no usa `git add -A`/`git commit`: se construye desde el árbol revisado
(más actualizaciones mecánicas declaradas, validadas y selladas en la intención),
con identidad y marca de tiempo explícitas, de modo que su id es determinista y
se persiste antes del efecto. Reconciliar es comprobar ese id: ya alcanzable →
`reconciled`, nunca otro commit; HEAD movido sin commit propio → invalidar si el
objeto no existe, recuperación manual con evidencia si existe sin ser alcanzable.
La referencia se mueve con compare-and-swap. Hooks, firma y configuración global
no intervienen; no se descarta staging posterior ni ediciones sin revisar.

El commit se encola como acción `commit` bajo el lock de checkout existente y se
registra en `managed_commits` (migración `0006_git_commits`). `COMMITTED` es un
checkpoint en el worktree de la tarea: no equivale a integración en la rama de
destino ni a COMPLETED/cierre. Un run con operación pendiente/registrada no se
reanuda con `resume`. El worktree por tarea (`GitWorktrees`) es idempotente,
conservador y fuera del checkout de origen, sin remove/clean/reset; no es un
sandbox de seguridad.

Quedan fuera y sin implementar: integración en rama destino, push, retirada de
worktrees, entradas API/CLI/UI gestionadas, abandono explícito de una intención
ambigua y formateador real. H2.5 no iniciado.

## D027 — Modo gestionado por activación, marcador y copia inmutable

Estado: implementado y verificado offline el 2026-10-12.
[Entrega, protocolo y límites](archive/phase-003/H2.5_MIGRATION.md).

Contradicción señalada antes de implementar: la especificación pide deshabilitar
el arranque del motor legacy, el alcance pedía no modificar el origen y el motor
legacy no tiene lock ni lee nada nuestro. El usuario aceptó un marcador
`.harness/managed-mode.json` en el checkout (única escritura en el origen, con
creación exclusiva; se retira solo si coincide byte a byte), dejó la autoridad a
criterio de la entrega e incluyó la reversión. La exclusión frente al motor legacy
es cooperativa y detectada: nunca se presenta como impedida.

Autoridad: SQLite para el estado operativo y para el modo (`managed_activations`,
migración `0007_managed_activation`); el marcador es su proyección y una
discrepancia rechaza. El histórico legacy importado vive en una copia inmutable
fuera del checkout, con hash por archivo en un manifiesto cuyo hash se guarda en
SQLite, indexada como origen H1 de solo lectura. Ningún run legacy se convierte en
intento, aceptación ni commit; las identidades observadas se conservan con su
procedencia. Tras activar, `.harness/runs` del checkout no es autoridad: entradas
nuevas o modificadas son actividad legacy. Los documentos siguen siendo producto
en Git; sus cambios por hash son propuestas, nunca mezcla silenciosa. El índice
previo del origen queda congelado, sin observación ni reimportación.

Exclusión por raíz canónica y por common dir Git (índices únicos parciales). El
motor gestionado exige activación ACTIVE, marcador idéntico y ausencia de deriva;
un checkout con `.harness/runs` (propio o del checkout principal) sin activación,
o un marcador sin activación viva en esta base, rechaza. Se comprueba al admitir
cada job (con reverificación en la transacción), al reclamarlo (rechazo `REFUSED`
sin efectos, lock liberado) y antes de cada invocación de agente e intención de
commit (cuarentena H2.2 si ocurre a mitad de run).

Activación: PREPARING con token → inventario igual a la vista previa → copia
verificada → inventario igual tras copiar → publicación atómica → marcador → una
transacción ACTIVE con índice y manifiesto. Un fallo antes del marcador deja
FAILED sin nada activo; una caída deja PREPARING, que solo se reanuda o abandona
explícitamente. Reversión: REVERTING → exportación verificada del estado
gestionado admitido bajo la activación → marcador retirado → REVERTED; el checkout
vuelve a ser legacy y el histórico copiado sigue accesible.

Quedan fuera: entradas API/CLI/UI de migración o ejecución gestionada, exportación
mecánica de STATE/NEXT_STEPS, conversión de runs gestionados a legacy, retención
de copias `staging-*` y detección entre comprobaciones o en otros worktrees.

## D028 — API gestionada local: proyectos del servidor y supervisor opt-in

Estado: implementado y verificado offline el 2026-10-12.
[Entrega, contratos y límites](archive/phase-003/H2_EXIT_API.md).

Los proyectos gestionados se registran en el servidor (`ManagedConfig`, pasado a
`create_app` o cargado al arrancar desde `HARNESS_MANAGED_CONFIG=módulo:atributo`).
El cliente HTTP los nombra por identificador y nunca aporta raíces, comandos,
perfiles, políticas ni selecciones. Así se evita que una petición defina qué se
ejecuta (§14). Las versiones congeladas también vienen de esa configuración.
`POST /projects` de la §13 queda pendiente; no se implementa un registro
persistido. Sin configuración no hay proyectos, puertos ni supervisor: la API
gestionada solo lee y ningún endpoint invoca proveedores.

Los jobs se ejecutan con un supervisor opt-in: un único hilo del proceso Uvicorn
que llama a `LocalSupervisor.run_once`, despertado al encolar o confirmar. Se
descarta la acción «ejecutar siguiente job» porque mantendría abierta una petición
HTTP durante una invocación CLI que puede ser larga. Este modelo coincide con la
§5: el supervisor comparte servicio con la API y es el único propietario de la
cola. La cola, la exclusión, el lease y la cuarentena siguen en SQLite, sin
cambios. Un fallo deja el job en RECOVERY_REQUIRED y el hilo continúa con otros
checkouts. El apagado espera como máximo un lease y no libera un job a medias. Los
puertos CLI H2.3 y Git H2.4 solo intervienen si se inyectan en la configuración.

Contratos (Pydantic como fuente de OpenAPI y tipos):

- `Idempotency-Key` obligatorio al crear jobs (encolar tarea, revalidar,
  reintentar, commit).
- `expected_version` obligatorio al cambiar un recurso existente: acciones de run,
  confirmación de escritor detenido y transiciones de activación. Esta última
  comprobación se añade dentro de la transacción de `take_over` y `begin_revert`.
- La activación es idempotente por el hash de la vista previa.
- 409 con `{code, diagnostic}` distingue `mode_refused`, `conflict`,
  `migration_conflict`, `migration_refused`, `ownership_lost`,
  `checkout_unreadable` y `commit_writer_unavailable`.
- Las acciones solo operan sobre checkouts registrados.
- El commit por HTTP no admite actualizaciones mecánicas.

Seguridad local (§10), solo en `/api/managed`:

- `Host` de loopback en toda ruta.
- `Origin` de loopback si existe y cabecera `X-Harness-Local: 1` en mutaciones.
- Sin CORS.

La sesión local frente a otros usuarios del sistema operativo y la extensión de la
guardia a las rutas H0/H1 quedan pendientes y no se presentan como implementadas.
UI gestionada, SSE gestionado, registro de proyectos por HTTP, pausa o cancelación
y actualizaciones mecánicas por HTTP quedan fuera de esta parte.

## D029 — UI gestionada por sondeo, envíos conservados y evidencia congelada

Estado: implementado y verificado offline el 2026-10-12.
[Entrega y reproducción](archive/phase-003/H2_EXIT_UI.md).

La UI consume los contratos generados de `/api/managed`; no decide aceptación,
recuperación ni ejecución. Proyectos/selecciones/comandos permanecen configurados
en el servidor. La proyección de cada ciclo se amplía con diff, procedencia,
validación y review ya persistidos, para poder revisar el contenido antes de
confirmar el commit. No recaptura el checkout ni inventa evidencia actual.
OpenAPI/Pydantic siguen siendo la fuente; no hay migración SQLite ni codec nuevo.

Se elige sondeo de detalle/estado cada 1,5 s y supervisor cada 2 s, con eventos
confirmados paginados por cursor (50 por página) y deduplicación por secuencia.
Las páginas pendientes se drenan antes del siguiente intervalo; el cursor solo
avanza con una respuesta aceptada del run seleccionado. Desmontar una pantalla
invalida sus respuestas pendientes. Reiniciar el servicio conserva selección y
evidencias, muestra desconexión y recupera lecturas sin ejecutar nuevas acciones.
SSE gestionado queda pendiente; H1 conserva su SSE independiente.

Cada envío de job congela ruta, cuerpo y UUID en `sessionStorage` antes de enviarse.
Un fallo de red/5xx conserva esa solicitud para repetición explícita; no hay
reenvío automático. La última solicitud idéntica consecutiva conserva su clave
aun después de una respuesta rápida y al recargar la pestaña. Cambiar cuerpo o
versión crea una acción nueva. Un 4xx definitivo retira el envío pendiente; el
409 muestra código/diagnóstico y recarga lecturas sin sustituir silenciosamente
la versión en la acción rechazada. La persistencia es por pestaña y origen, no
una deduplicación entre navegadores ni ante borrar almacenamiento/restaurar DB.

Activar/revertir requiere motivo y confirmación explícita; commit, evidencia
revisada de la versión mostrada; confirmar escritor detenido, motivo, token y
versión observados. Los consentimientos se limpian cuando cambia la versión.
Revalidar y reintentar son acciones distintas; la segunda advierte del consumo
del presupuesto y de posibles cambios. COMMITTED sigue siendo un checkpoint,
sin integración/cierre de fase.

Todas las mutaciones gestionadas envían `X-Harness-Local: 1`. Se conserva la
guardia Host/Origin/CSRF de D028 solo en `/api/managed`; extenderla a H0/H1 queda
pendiente para abordar también los clientes existentes y sus pruebas. La sesión
local frente a otros usuarios del SO continúa pendiente: la cabecera no es una
credencial ni autenticación. Esta entrega no presenta cumplida toda la §10.

`examples/managed_demo.py` prepara exclusivamente un directorio nuevo con Git,
fixtures legacy y puertos sintéticos. Cargar su configuración no crea repos ni
invoca proveedores. Un fallo sintético de review, registrado fuera del checkout,
permite verificar cuarentena y recuperación incluso al reiniciar el servicio.
Ninguna configuración CLI real se activa en esta entrega. H3.1 queda siguiente,
sin iniciarlo; los consentimientos de smokes anteriores siguen agotados.

## D030 — Catálogo de prompts por ámbito y snapshot por intento

Estado: implementado y verificado offline el 2026-10-13.
[Entrega, procedencia y límites](archive/phase-004/H3.1_PROMPTS.md).

Ocho recursos Markdown (los siete nombres legacy y `execute-task`) adaptados al
contrato H2, sin modelos o stack fijos en el núcleo. Reemplazo completo por
jerarquía base → core global → perfil por nombre → proyecto por raíz canónica.
Instrucciones específicas siguen en el perfil. Las plantillas de bootstrap y
fases no autorizan ni implementan esos flujos.

SQLite gestiona versiones insertadas, punteros/generaciones y auditoría de
activación (`0008_prompt_versions`). Guardar crea UUID/hash nuevos; rollback
crea otro borrador con referencia al origen. Activar requiere versión esperada,
motivo y confirmación HTTP; compare-and-swap transaccional, sin reenvíos
silenciosos. API/UI bajo la guardia gestionada D028, tipos generados.

Variables fijas obligatorias por plantilla, interpolación en una pasada y
validación de hashes antes de invocar. Esquemas de salida fijos del motor,
fuera del editor. Cada intento conserva plantilla/versiones/procedencia,
variables, renderizado, referencias y hashes antes del efecto. La activación
no muta contratos, resultados ni peticiones anteriores. Routing se compone en
planificación/review sin otra llamada. Ningún prompt concede permisos.

Codec 4 conserva catálogo para recuperación y snapshot por petición. Formatos
1–3 siguen legibles sin metadatos inferidos ni reescritura de filas de intentos.
Runs en curso resuelven activaciones antes del siguiente intento; runs detenidos
conservan el último catálogo confirmado al reanudar. Aplicar versiones nuevas a
un run detenido exigiría una acción explícita auditada; esa acción no se expone
en H3.1. Para runs anteriores sin catálogo, la primera acción nueva lo captura,
sin atribuirlo retrospectivamente. El adaptador cli-3 y su captura del envoltorio
de transporte se conservan, sin cambiar permisos ni autenticación.

H3.2 queda siguiente sin iniciarse; consentimientos de smokes agotados.

## D031 — Permisos por petición exacta y efecto en un intento posterior

Estado: implementado y verificado offline el 2026-10-13.
[Entrega y límites](archive/phase-004/H3.2_PERMISSIONS.md).

Ledger `permission_requests` (0009) separado por ficheros, herramientas, red,
producto y aceptación. UUID/huella, contexto/contrato/versiones, solicitante,
intento de procedencia, operación/objetivo, motivo y caducidad explícitos.
Conceder/denegar exige versiones observadas y huella vigente; sustituir conserva
la decisión anterior y la invalida. Transacciones serializadas con la cola:
ninguna modificación con jobs pendientes del checkout ni permisos a llamadas vivas.

La autoridad es una intersección de objetivos exactos en cuatro techos del servidor:
global/proyecto/contrato/proveedor, congelados en versiones al crear el run.
Una ausencia deniega; ficheros también respetan el contrato y rutas del perfil.
No se amplían contratos por grants/reviews/prompts. Producto y aceptación quedan
auditoría separada, sin resolver preguntas ni producir aceptación/cierre/commit.
Identidad auditada: UID/nombre del usuario local del servicio; no autentica al
humano del navegador. La sesión local sigue pendiente, sin inventar identidad.

Snapshot con hash e identidad del intento persistido junto a la intención (codec
5, formatos 1–4 legibles). `once` consume al guardar intención, aun ante caída o
rechazo antes de lanzar; `task` sirve solo para ese run, hasta caducidad/sustitución.
Una denegación operativa vigente impide invocar el ejecutor y conserva la parada y
el presupuesto; una denegación once también se consume en ese intento. Confirmar
escritor detenido no recupera concesiones consumidas. Conceder no encola trabajo.

CLI `cli-4`: reglas concedibles declaradas/hash congelado, inventario cerrado para
esas herramientas hasta concesión/baseline explícito, adición de la regla exacta
solo al argv del intento. Conserva dontAsk, MCP/settings aislados y sesiones nuevas.
Ficheros no conceden tools; red por dominio no soportada se rechaza antes de lanzar.
No se presenta esto como sandbox físico ni se certifican permisos vivos de CLI
real mediante fakes. Configuraciones/versiones anteriores se rechazan sin reescritura.

Revalidar no llama al ejecutor, tampoco tras una review REVISE: se detiene y exige
reintento explícito. Se corrige esa rama previa para cumplir §8 y D015; las revisiones
automáticas de una acción de ejecución conservan su política/presupuesto existente.
API/UI exponen ledger, decisiones, snapshots y acciones calculadas por el servidor,
con versiones, confirmación y guardia gestionada. H3.3 siguiente, sin iniciarse;
smokes anteriores siguen sin autorización disponible.

## D032 — Fases en SQLite, READY por contenido exacto y cierre sin edición documental

Estado: implementado y verificado offline el 2026-10-13.
[Entrega y límites](archive/phase-004/H3.3_PHASES.md).

La fase es autoridad SQLite (`0010_phases`): definición congelada creada por el
usuario (criterios, tareas, documentos, tag opcional), base documental adoptada
por hash, preguntas, operaciones, autorizaciones y eventos atómicos. No se infiere
ninguna fase ni cierre del legacy. Check y cierre son runs (`purpose`) con job bajo
el lock del checkout, reutilizando supervisor, guardia de modo, cuarentena y
persistencia de intentos; no se crea otra cola.

READY se vincula a definición, HEAD, fingerprint Git limpio, documentos, commits
alcanzables de las tareas aceptadas y preguntas/respuestas. El cierre vuelve a
observar ese vínculo antes de cualquier efecto: un READY obsoleto nunca cierra y
pasa a `NEEDS_RECONCILIATION`. Preguntas pendientes impiden check, cierre y lote.

Diferencia deliberada con el legacy, sin trasladar sus reglas: el cierre no edita
documentos, no archiva planes, no instala la fase siguiente ni hace commit; la
exportación mecánica de STATE/NEXT_STEPS sigue pendiente (§7). Su único efecto Git
es un tag ligero declarado, con intención previa y creación por CAS: se concilia si
ya apunta al READY y nunca se mueve. «Reconciliar» es adoptar explícitamente
documentos cambiados por hash revisado; las ediciones se hacen como tareas
revisadas y confirmadas. La plantilla `reconcile-phase` con agente queda sin
ejecutar.

Lote y cierre son autorizaciones distintas, explícitas, con vigencia e identidad
del servicio: el lote encola de una en una tareas exactas y no comprueba, cierra ni
confirma commits; el cierre está ligado al READY mostrado y no encola tareas. Las
concesiones H3.2 no deciden producto ni cierre. Rol `phase` añadido al transporte
Codex de solo lectura de forma aditiva, sin cambiar `cli-4` para roles existentes.
H4.1 queda siguiente sin iniciarse; smokes anteriores siguen sin autorización.

## D033 — Decisiones del usuario tras H3.3 y orden de trabajo

Estado: decidido por el usuario el 2026-10-13 en un flujo de preguntas explícito;
nada de lo siguiente está implementado salvo lo que ya recoge D032.

1. **Cierre de fase:** se mantiene D032 (transición CLOSED + tag, sin editar
   documentos). La exportación mecánica de STATE/NEXT_STEPS será una tarea propia
   después de H4.1 y antes de H4.2; hasta entonces el cierre no escribe documentos.
2. **Chat H4.1:** turnos nuevos por la CLI de Codex en solo lectura, con contexto
   explícito y salida estructurada; App Server/SDK en un incremento posterior.
3. **Seguridad:** extender ya la guardia Host/Origin/`X-Harness-Local` a las rutas
   H0/H1; la sesión local frente a otros usuarios del SO queda para el hito 5.
4. **Lote desatendido con commit:** la autorización de lote incluye, de forma
   explícita, encadenar tareas y confirmar el commit de cada aceptación elegible por
   contenido exacto (H2.4); se detiene en el primer bloqueo, pregunta, caducidad o
   revocación. Nunca comprueba ni cierra la fase. Excepción acotada a D026, que
   sigue exigiendo acción propia fuera de un lote autorizado.
5. **Reconciliación con agente:** genera una tarea con contrato determinista
   limitado a los documentos de la fase (plantilla `reconcile-phase`), ejecutada,
   revisada y confirmada por el flujo normal; después se adopta la base por hash.
6. **Tags:** tipo configurable por proyecto; por defecto ligero. Un tag anotado
   fija mensaje, identidad y fecha en la intención para que su id sea determinista
   y conciliable; nunca se mueve ni sobrescribe.
7. **Definición de fase:** enmienda versionada con motivo, confirmación y
   auditoría, que conserva la anterior e invalida READY y autorizaciones de lote;
   se añade abandono explícito de fase.
8. **Consumo real:** sin smoke de la evaluación de fase por ahora. Más adelante, un
   smoke autorizado de recorrido completo (tarea → commit → check → cierre) en
   checkout desechable, con modelos/esfuerzos fijados por el usuario.
9. **Push:** lo hace el usuario; las sesiones no publican.
10. **Orden:** H3.4 (puntos 3–7) → H4.1 (punto 2) → exportación mecánica de
    STATE/NEXT_STEPS (punto 1) → H4.2.

## D034 — Lote desatendido derivado del estado, definiciones versionadas y tags anotados deterministas

Estado: implementado y verificado offline el 2026-10-13 (puntos 3–7 de D033).
[Entrega y límites](archive/phase-004/H3.4_PHASE_ADJUSTMENTS.md).

La guardia local (Host de loopback, Origin local y `X-Harness-Local: 1`) se comparte
desde `api/security.py` y se aplica a las mutaciones H0/H1 (simulaciones y
observación legacy). La guardia se ejecuta antes de buscar el recurso. Las lecturas
H0/H1 quedan fuera de este alcance y la sesión local sigue pendiente (hito 5).

El lote desatendido es una autorización con el alcance explícito
`chain_commits`. Congela tareas, plan, definición, contexto y versiones. El
supervisor lo conduce en `run_once`, antes de reclamar, con un paso por tick. Cada
paso se deriva del estado SQLite y usa claves idempotentes deterministas
(`batch:{auth}:start|commit:…`). No se usa ningún hilo ni cola nueva. Se descarta
encadenar dentro de `finish`, porque mezclaría lecturas de modo en disco con la
transacción de cierre del job.

El lote se detiene en el primer bloqueo, pregunta, caducidad, revocación, cambio de
definición, fase no `ACTIVE`, cuarentena o commit no completado. No adopta runs
iniciados fuera de él y nunca comprueba ni cierra la fase. Su excepción a D026 se
limita a encolar el commit H2.4 de una aceptación elegible que el propio lote
inició; el commit sigue revalidando el contenido exacto.

La definición de fase se versiona en `phase_definitions` (migración 0011). Una
enmienda crea una versión nueva y conserva la anterior. Mantiene el código, exige
motivo y confirmación, invalida READY y los lotes activos, y adopta con su hash
actual los documentos añadidos, que quedan auditados. `ABANDONED` es un estado
terminal explícito y auditado que libera el checkout. Las filas anteriores se
marcan como `migrated`, sin inferir motivo ni identidad.

El tipo de tag es configuración del proyecto en el servidor (`ManagedProject.tag_kind`,
ligero por defecto) y queda congelado en la autorización de cierre. Un tag anotado
fija en la intención mensaje, identidad del escritor Git y fecha, junto con el id
del objeto calculado antes del efecto. El mensaje no incluye el id de la
operación. Un cierre explícito posterior reutiliza la intención incierta del mismo
READY, así que obtiene el mismo objeto y concilia. Nunca se mueve ni se sobrescribe
un tag, tampoco uno ligero existente.

La reconciliación con agente es una tarea normal (`<fase>-RECONCILE-<n>`) con un
contrato determinista del servidor, sin planificador. El contrato limita
`allowed_paths` a los documentos de la fase y usa como instrucciones la plantilla
`reconcile-phase` renderizada, con su id y hash registrados. Hay una tarea abierta
como máximo. La base se adopta por hash solo después de su commit `COMMITTED`, y
el origen queda registrado. La plantilla se reescribe para describir la ejecución
bajo contrato, lo que cambia su id base.

H4.1 queda como siguiente tarea, sin iniciar. Los smokes anteriores siguen sin
autorización disponible.

## D035 — Chat por turnos nuevos de solo lectura con contexto congelado y propuestas confirmadas

Estado: implementado y verificado offline el 2026-10-13 (punto 2 de D033).
[Entrega y límites](archive/phase-005/H4.1_CHAT.md).

La conversación es autoridad SQLite separada del flujo de ejecución (`0012_chat`):
conversaciones, turnos y propuestas. Cada turno es un run `chat` con job bajo el
lock del checkout. Se reutilizan el supervisor, la guardia de modo, la cuarentena y
el journal de intentos; no se crea otra cola ni otro ejecutor. Se descarta ejecutar
el turno dentro de la petición HTTP (D028) o en un hilo aparte, porque duplicaría
la propiedad de procesos y la recuperación. Esperar el lock tiene un coste (un
turno espera a la tarea en curso), pero cumple la §13: los mensajes recibidos
durante un intento se encolan.

El contexto explícito se congela en la transacción que encola el turno: proyecto,
fase, documentos acotados con hash, evidencias de runs y turnos anteriores. Así
refleja lo que el usuario seleccionó y no cambia si los archivos cambian antes de
ejecutarse. El prompt renderizado (plantilla `chat-turn` versionada y editable) se
persiste como intención antes de invocar. Cada turno es una invocación nueva del
rol `chat`, con Codex en solo lectura, sesión efímera y la selección del
planificador. App Server/SDK quedan para un incremento posterior. La salida tiene
un esquema fijo y estricto: un fallo o una salida inválida detienen el turno sin
fallback ni reintento, y una caída lo deja `UNKNOWN` tras la confirmación
explícita. Además del sandbox de la CLI, se compara la evidencia del checkout antes
y después: un cambio invalida el turno y sus propuestas.

Una propuesta no ejecuta nada. Aceptarla exige confirmación, versión y hash exacto,
y encola una tarea normal con una sección de plan y su origen. Deliberadamente, la
sección no lleva rutas permitidas ni ejecutor legibles por máquina: el planificador
fija el contrato con la política del proyecto, y después siguen ejecución, revisión
y commit H2.4 explícito. El chat no concede permisos, no fija ni amplía contratos y
no tiene ruta lateral de escritura. No hay encolado automático dentro de un modo
autorizado; queda para cuando se decida explícitamente.

`chat-turn` se añade al catálogo. Los catálogos congelados antes de H4.1 siguen
siendo válidos al reanudar (`ADDED_LATER`), sin reescritura. Siguiente tarea:
exportación mecánica de STATE/NEXT_STEPS (D033 punto 1), sin iniciar; los smokes
anteriores siguen sin autorización.

## D036 — Exportación documental separada, diff confirmado e intención de commit conciliable

Estado: implementado y verificado offline el 2026-10-13 (punto 1 de D033).
[Entrega y límites](archive/phase-005/STATE_EXPORT.md).

El cierre sigue siendo D032: CLOSED + tag, sin invocar la exportación. Exportar es
una acción propia, también disponible para la última fase cerrada o abandonada,
hasta crear otra fase. Así el tag conserva el HEAD evaluado; exportar después no
lo mueve. Una exportación previa a cerrar vuelve obsoleto el vínculo READY por
sus documentos/HEAD: se exige un check nuevo. La evaluación histórica se conserva.

STATE y NEXT_STEPS usan las rutas del contexto del servidor, distintas y presentes
en la base documental adoptada. Los documentos regulares UTF-8 se acotan a 512 KiB.
Se añade o reemplaza únicamente el bloque entre los comentarios HTML
`harness-local:managed-state:start` y
`harness-local:managed-state:end`. La prosa exterior y sus terminaciones
de línea se conservan; marcadores parciales, repetidos o mal colocados se rechazan.
El bloque contiene JSON estable, con fase/estado, tareas/aceptación/commit,
preguntas abiertas, último check (incluida validación) y lotes registrados.
NEXT_STEPS proyecta tareas sin commit. null conserva datos ausentes. Se escapan
valores libres para que no inyecten HTML, fences ni marcadores. No se incluye el
reloj actual, las versiones/eventos de exportación ni su propio commit, evitando
un ciclo de actualizaciones del documento sobre sí mismo.

La revisión de contenido exacto es humana: GET previsualiza el diff y POST exige
su SHA-256, versión de fase, motivo, confirmación e Idempotency-Key. La API no
acepta contenidos o rutas arbitrarios. El checkout/índice deben estar limpios,
todos los documentos deben coincidir con sus hashes adoptados y se debe revocar
un lote activo antes de exportar. Deriva externa → conflicto y reconciliación
por hash existente; nunca mezcla silenciosa. Las rutas usan la guardia local.

Un run `document_export` reutiliza jobs, lock, lease, propietarios, cuarentena,
operaciones y eventos de fase. No invoca agentes. La operación conserva snapshot,
bytes/diff, hashes revisados y el CommitIntent H2.4, fijando árbol, mensaje,
identidad, fecha e id del commit antes de escribir. El escritor Git utiliza CAS.
La conciliación tras confirmar el escritor detenido y volver a confirmar el diff
reutiliza la misma operación/run/intención; no crea otro commit. Una escritura
parcial solo admite cada documento con su hash anterior o sellado y exige que
completar los bloques produzca exactamente el árbol sellado con índice intacto.
Cualquier byte ajeno o cambio del checkout invalida sin sobrescribirlo.

La adopción de hashes, resultado y evento ocurre atómicamente al terminar el job,
después de verificar el commit y todos los documentos. Una caída antes de esa
transacción conserva la intención. Las mutaciones de fase y nuevas tareas quedan
bloqueadas mientras una intención incierta exige conciliación. La autoridad se
almacena en `phase_operations`, no en `managed_commits`, que sigue certificando
aceptaciones de tareas. No se añade migración ni codec; esquema `0012_chat`.

La exclusión frente a escritores externos sigue siendo cooperativa: se comprueban
hashes/árboles entre efectos, sin prometer atomicidad de dos archivos ni aislamiento
físico. Si cambian documentos después de un commit incierto, hay que restaurar
manualmente el contenido sellado para conciliar/adoptar; no se revierte ni fusiona
por el motor. Abandonar una intención ambigua y retener temporales siguen fuera.
H4.2 es la siguiente tarea, sin iniciarla. Los smokes siguen sin autorización.

## D037 — Bootstrap documental confirmado, descubrimiento opcional y commit raíz conciliable

Estado: implementado y verificado offline el 2026-10-13.
[Entrega, uso y límites](archive/phase-005/H4.2_BOOTSTRAP.md).

Una carpeta existente registrada por el servidor necesita `bootstrap_enabled=True`
y escritor Git explícito. El cliente solo nombra su identificador; perfil,
selecciones, rutas canónicas, versiones y permisos siguen siendo autoridad del
servidor. No se habilita registro HTTP de proyectos ni selector arbitrario de
rutas. Carpeta no vacía, oculta, enlazada o dentro de otro Git → flujo de
importación existente, nunca sobrescritura ni suposición de importabilidad.

La plantilla mantenida `project-foundation` v1/hash genera seis documentos de
fundamentos: brief, decisiones, perfil/política, README, STATE y NEXT_STEPS. Su
primera fase `P001` y tarea `P001-T001` concretan un escenario de entrega
verificable; la tarea solo permite `docs/DELIVERY_CHECKLIST.md`. No introduce otro
stack/perfil ni genera todo el producto desde un brief. La plantilla documental
se versiona con el paquete y el prompt de descubrimiento se edita con H3.1.

Codex puede proponer requisitos, alternativas y decisiones pendientes mediante
una acción propia (`bootstrap_discovery`), sesión nueva de solo lectura y selección
del planificador. Brief y prompt versionado quedan congelados al encolar; ningún
mensaje decide producto, concede permisos ni escribe documentos. Salida inválida
se descarta sin fallback/reintento; cambios del destino invalidan la propuesta y
se conservan. Una caída deja `UNKNOWN` tras confirmar escritor detenido. El
usuario puede aportar decisiones completas sin invocar al agente.

Preview determinista con archivos íntegros, contrato/fase, política/perfil y
comandos declarados. Confirmación humana del hash exacto, motivo y clave encola
`bootstrap`, sin agentes. No ejecuta preparación ni instala dependencias; comprueba
Git, destino y compatibilidad del contrato/política. La primera tarea se encola por
acción separada y sigue ejecución/validación/revisión/commit existentes.

Ambos flujos reutilizan jobs, lock, leases, propietarios y cuarentena; ninguna
cola o hilo adicional. `0013_bootstrap` guarda preview/decisión/intención/resultado
y vínculo de fase; el codec se conserva. La intención del commit raíz (sin padre)
fija bytes/árbol, identidad, mensaje, fecha e id antes del efecto. Usa el entorno
Git, captura e índices temporales H2.4; no fabrica aceptación ni `managed_commits`.
Archivos nuevos exclusivos, marca propia dentro de `.git`, índice/refs conservados
y CAS permiten conciliar tras reconfirmación explícita con el mismo run/intención/
commit. Solo el job de conciliación es nuevo. Sin marca fiable exige recuperación
manual. Datos externos jamás se restauran, fusionan ni descartan.

La fase/versiones/base documental se insertan junto al resultado/fin del job en
una transacción. Trabajo nuevo queda bloqueado mientras el bootstrap es incierto.
La UI conserva los envíos con su clave y muestra el estado de la primera tarea
tras reiniciar. Exclusión externa cooperativa; sin atomicidad del conjunto de
archivos, abandono automático de intención ni limpieza de temporales. CLI real y
preparación de un stack no verificadas. H4.3 siguiente, sin iniciar; smokes agotados.

## D038 — Segundo perfil declarativo con validaciones TypeScript reales por los puertos existentes

Estado: implementado y verificado offline el 2026-10-13.
[Entrega, comandos y límites](archive/phase-005/H4.3_TYPESCRIPT_PROFILE.md).

`typescript-web` demuestra una web estática de otro stack sin modificar el núcleo:
preparación con Node/npm e instalación offline desde lock; validaciones de tipos,
tests y build; prefijos de comandos, rutas protegidas/sensibles e instrucciones.
Se configura en `ProjectContext` por el servidor y se congela con el run. Las
reglas del perfil no conceden herramientas/red ni superan permisos del contrato.

Fixture sintética con Node 24.15.0, npm 11.12.1 y TypeScript 5.9.3 (única dependencia,
lock propio). Usa tsc, tests Node y módulos web estáticos, sin framework adicional.
Scripts, tests, configuración del compilador y lock quedan protegidos. La caché
se inyecta explícitamente; falta de paquete, engines incompatibles o lock
inconsistente detienen antes del agente, sin instalación online ni corrección
silenciosa. Los artefactos/dependencias ignorados no cambian la evidencia Git.

Pruebas por `CommandRunner` existente con subprocess real y entorno explícito
temporal para fixture confiable; agentes falsos y Git/SQLite temporales hasta
commit H2.4 en worktree, conservando snapshots, permisos y contenido exacto.
ACCEPT no supera tests/tipos/build/política fallidos. No se añade un adaptador de
comandos de producto, cola, servicio, proceso automático o cambio de esquema/codec.
Recuperación de validadores de producto, permisos de CLI real y aislamiento físico
no certificados; interacción con DOM mínimo sin navegador. ReferenceProject no ejecutado.

La plantilla de bootstrap H4.2 sigue siendo documental: declarar el segundo
perfil no genera ni instala una app desde el brief. No se modifica esa decisión.
H5.1 importación JUnit y detalle de tests es la siguiente tarea, sin iniciarla;
proveedores y smokes siguen sin autorización disponible.

## D039 — JUnit observado por comando exacto y original congelado en el historial

Estado: implementado y verificado offline el 2026-10-13.
[Entrega y límites](archive/phase-006/H5.1_JUNIT.md).

El perfil del servidor declara comando completo, ruta de reporte relativa al
checkout y cobertura de tests como selección textual. No es cobertura de código
medida ni una concesión de herramientas. Se congela con el contexto; una ruta XML
o petición HTTP no añade reportes ni comandos. TypeScript genera JUnit Node junto
a TAP; ReferenceProject no declara un original inexistente.

La captura compara archivo/hash antes y después del comando sin eliminar reportes
anteriores. Frescura significa cambio local observado, no certificación frente a
escritores externos. Sin cambio se etiqueta `stale`, con diagnóstico; ausencia,
errores y límites no se convierten en éxito. Descriptores/O_NOFOLLOW, archivos
regulares sin enlaces duros y límites explícitos evitan rutas externas y bloqueo
por archivos especiales. El parser rechaza DTD/entidades, preserva únicamente
casos completos en XML truncado y no ejecuta ni sigue contenido XML.

Original exacto en base64/hash/tamaño y casos en `managed_runs.history_json`, codec
6 sin migración; formatos 1–5 y snapshots sin declaraciones conservados. Se elige
el historial acotado existente para conservar atómicamente reportes y ciclos,
sin introducir un almacén de blobs, doble autoridad ni reglas de retención en
H5.1. Vincula run/ciclo/command_id de eventos/intento ejecutor/evidencia Git. Checks
de fase también guardan reportes en su run, con ejecutor null. Una caída antes del
checkpoint no certifica importación; recuperar exige revalidar explícitamente.

El reporte nunca sustituye exit/stdout/stderr/timeout/duración observados. Un
comando fallido sigue impidiendo aceptación aunque el XML muestre éxitos. Fallos
observados de casos en un reporte nuevo añaden una puerta de aceptación/READY,
incluido exit 0; no atribuye fallos del archivo anterior a la ejecución actual.
Sin reporte compatible sigue siendo necesaria la validación por comando. Review,
política y contenido exacto continúan siendo puertas independientes.

API/UI leen historial, con casos paginados y descarga binaria del original con
hash comprobado, attachment/nosniff. Los resúmenes de sondeo y los prompts omiten
base64; React muestra errores como texto. Ausencias permanecen null, cero es cero
y las duraciones individuales nunca se suman como tiempo real. No hay importación
de XML legacy, medición de cobertura de código ni retención/backup en esta entrega.
H5.2 backup/restauración local queda siguiente, sin iniciar. Smokes agotados.

## D040 — Backup local con servicio detenido, referencias verificadas y restauración de consulta

Estado: implementado y verificado offline el 2026-10-13.
[Procedimiento y límites](archive/phase-006/H5.2_BACKUP.md).

La consistencia del conjunto exige detener servicio, observadores y escritores,
con declaración `--writers-stopped`. Se rechazan propietarios abiertos/grupos
conocidos vivos; una identidad desconocida no se interpreta como parada. El
operador debe comprobarla. `BEGIN IMMEDIATE` bloquea escrituras DB mientras una
segunda conexión usa el mecanismo de backup SQLite y se copian/verifican los
artefactos. Se descarta una copia online que pudiera mezclar el historial con
streams en progreso sin un protocolo de pausa de escritores de archivos.
No se copia únicamente el fichero principal cuando hay WAL.

Bundle local formato 1 con SQLite íntegra, hashes por archivo, procedencia y mapeo
de referencias históricas. Incluye prompts/streams CLI (rangos y colas inciertas),
snapshots legacy H2.5 y exportación de reversión; JUnit y snapshots restantes ya
viven en SQLite. Solo se leen ubicaciones conocidas dentro de raíces permitidas
explícitas. Los originales externos del índice H1 y el código/objetos Git requieren
su propia copia; sus referencias se conservan y el límite se declara. Ningún
contrato, raíz o resultado congelado se reescribe para cambiar de ubicación.

La creación reclama un destino inexistente, fuera de los checkouts y los
originales, con escrituras exclusivas y fsync. Se publica `COMPLETE` con hash del
manifiesto al finalizar; errores dejan un parcial no reutilizable, sin GC.
Verificación de hashes, referencias completas, esquema, integridad/FK, historial
1–6 y originales JUnit; un WAL/journal no vacío en el bundle se rechaza. Una
restauración valida primero y vuelve a verificar en otro destino nuevo; no
migra, sobrescribe ni repara originales. Las rutas históricas no se consultan al
verificar/restaurar, de modo que el bundle no depende de su existencia actual.

Copias y restauraciones tienen marca persistente `PRAGMA user_version=0x483532`.
No cambia filas operativas ni revisión Alembic `0013_bootstrap`. `make_engine`
activa `query_only=ON`, incluso si se mueve solo el fichero; marca desconocida
rechaza apertura. La API verifica el bundle al iniciar, omite configuración
ambiental/puertos/supervisor/observador y bloquea mutaciones con 409. Lecturas por
ID de run y de JUnit siguen disponibles; el contenido legacy copiado usa el mapeo
y su hash indexado. No registra proyectos gestionables ni toca checkouts.

Esta guardia evita que abrir una copia dispare jobs/lotes históricos. Una
restauración no certifica muerte de procesos, libera locks, revive concesiones ni
repite efectos. La reactivación operativa necesita un procedimiento separado,
fuera de H5.2; no hay acción automática para retirar la marca. La exclusión
frente a escritores externos y la comprobación de parada siguen siendo
cooperativas; no se promete defensa frente a manipulación del propietario.

Límites explícitos: SQLite/fichero hasta 256 MiB, artefactos hasta 2 GiB, 10.000
referencias, manifiesto hasta 4 MiB; sin benchmark, retención/GC o distribución.
H5.3 retención local de logs queda siguiente, sin iniciar. Smokes agotados.

## D041 — Retención explícita de streams sellados con intención previa y ausencias auditadas

Estado: implementado y verificado offline el 2026-10-13.
[Procedimiento y límites](archive/phase-006/H5.3_RETENTION.md).

La política local formato 1 tiene corte UTC obligatorio y umbral de tamaño
configurable (1 MiB predeterminado); sin invocación explícita se conserva todo.
Solo afecta stdout/stderr externos de CLI gestionadas terminadas y selladas,
sin locks/trabajo pendiente en el checkout ni resultados/grupos inciertos.
No elimina prompts, contratos, snapshots, permisos, aprobaciones, veredictos,
JUnit, migraciones, resultados o hashes/rangos históricos. Retirar bytes no cambia
el juicio ni el estado operativo del run.

El mantenimiento se hace por CLI/biblioteca, con servicio/escritores detenidos,
raíces explícitas fuera de checkouts y confirmación del hash de la vista previa,
motivo y UID local. Se reutiliza `managed_events` para intenciones/resultados y
sus versiones/secuencias: no hay una segunda autoridad, migración ni codec nuevo.
`BEGIN IMMEDIATE` protege las decisiones DB; intención confirmada antes de unlink,
reverificación de elegibilidad/bytes y descriptores sin enlaces antes de retirar.
La intención sella también las referencias con rangos/hashes parciales, para
detectar su corrupción posterior aunque el original ya esté retirado.

Una caída deja intención pendiente y exige preview y confirmación nuevas, con
evento de reconfirmación; no se repite automáticamente. Ausencia tras intención
puede conciliarse explícitamente, con bytes retirados observados null cuando no
se observó el unlink. Los contenidos ajenos no se eliminan y requieren recuperar
manualmente el original sellado para conciliar. No existe abandono de intención
pendiente. La parada y exclusión frente a escritores externos son cooperativas,
sin atomicidad DB/filesystem ni promesa de defensa ante manipulación del dueño.

Consulta explícita CLI/API/UI diferencia retenido verificado, purgado, pendiente,
perdido y no verificado, manteniendo hash/procedencia. No sirve cuerpos distintos
ni relee grandes logs en cada sondeo. Un original reaparecido tras purga no se
adopta ni vuelve a eliminar por esta política.

El bundle H5.2 formato 1 añade `absent_purged` contrastado con el journal y las
referencias selladas; pérdidas, pruebas inválidas, corrupción o purgas pendientes
impiden publicar un backup. Los bundles anteriores sin purgas siguen verificando
sin ese campo; las copias existentes permanecen intactas. Restauraciones conservan
ausencias autorizadas y guardia de consulta; no pueden purgarse ni reactivarse.

Se limita a 256 MiB por fichero, 2 GiB por operación y 10.000 referencias. No
implementa rotación/caps nuevos de captura, retención de SQLite/legacy/JUnit,
GC de temporales ni benchmark. Solo se eliminaron capturas sintéticas temporales.
H5.4 diagnósticos locales de compatibilidad queda siguiente, sin iniciar.
Smokes/proveedores siguen sin autorización disponible.

## D042 — Diagnóstico CLI explícito, preflight compartido y resultados acotados

Estado: implementado y verificado offline el 2026-10-13.
[Uso, verificaciones y límites](archive/phase-006/H5.4_DIAGNOSTICS.md).

`diagnose-cli` recibe un JSON explícito de una CLIConfig, sin importar factories,
abrir SQLite, crear jobs ni acceder al estado de autenticación. La configuración
se valida estructuralmente; no se revelan sus valores, rutas, argv ni errores
libres. `diagnose(config)` reutiliza la misma comprobación de biblioteca.

El adaptador comparte el preflight: version/help con stdin cerrado, entorno
completo explícito, cwd temporal, máximo 10 segundos y 256 KiB de salida combinada
por comando. Fallos/timeout/salida inesperada se representan como desconocidos;
versión distinta o flags ausentes como incompatibles. Se detiene la secuencia de
sondas de ese proveedor al primer fallo, sin reintento/fallback/corrección.
Se termina únicamente el grupo POSIX propio, también ante pipes de hijos.

Versión solicitada y observada separadas; flags requeridos/ausentes y pasos de
corrección estáticos. `version_help_match` es coincidencia local limitada, nunca
certificación de autenticación/cuota/modelos, semántica del argv, permisos o
retries internos. El ejecutable debe ser de confianza: esto no es un sandbox
físico ni garantiza ausencia de efectos internos de un binario arbitrario.

Se conserva cli-4 porque no cambia el argv de inferencia, permisos, capacidades
ni hash de configuración; el preflight es más estricto y sus nuevos campos son
aditivos. No se modifica ningún snapshot congelado o resultado previo. Sin
migración/codec/dependencias/API/UI nuevos. Configuración global, autenticación
real y smokes quedan fuera; consentimientos anteriores agotados.
Siguiente tarea H5.5: assets web empaquetados y comando único de inicio, sin iniciar.

## D043 — Distribución local con assets y migraciones, arranque explícito en loopback

Estado: implementado y verificado offline el 2026-10-13.
[Construcción, instalación y límites](archive/phase-006/H5.5_DISTRIBUTION.md).

Pipeline explícito `scripts/build_distribution.py`: npm ci offline desde lock,
comprobación de versiones/tipos/build, staging temporal y sdist/wheel con UI,
plantillas y migraciones. Dependencias de producción exportadas desde uv.lock con
pins/hashes. No se versionan assets generados ni se publica; el build de desarrollo
mediante uv directo no es un paquete de distribución con UI. No cambia el baseline.

Las migraciones canónicas se trasladan al paquete sin cambiar sus revisiones ni
operaciones; alembic.ini de desarrollo apunta allí. `harness-local init-db` reclama
una SQLite nueva por ruta absoluta y ejecuta esas migraciones. Rechaza destinos
existentes/auxiliares huérfanos y conserva parciales; no es un actualizador.
`harness-local serve --database RUTA` exige esquema y assets preparados y sirve
UI/API por Uvicorn en 127.0.0.1, un worker, sin reload ni proxy headers. No crea
ni migra bases al iniciar, no necesita Node/cwd/checkout y diagnostica fallos.

Assets predeterminados relativos al paquete; `create_app(ui_dir=...)` conserva
el override explícito de biblioteca y Vite sigue siendo la UI de desarrollo.
La nueva entrada requiere SQLite explícita e ignora HARNESS_DATABASE_URL; las
entradas anteriores conservan su contrato. HARNESS_MANAGED_CONFIG y observación
persistida mantienen opt-in; no se auto descubren proyectos ni CLI. Restauraciones
conservan verificación de bundle y guardia de consulta, sin cargar configuración.

Verificación de wheel en venv limpio offline, dependencias con hashes, cwd ajeno y
PATH sin Node: recursos exactos, HTTP loopback, simulación/reinicio, diagnósticos,
backup y restauración de consulta. Solo datos temporales sintéticos. No certifica
otras plataformas, identidad binaria del build, navegador ni recorrido de agentes.
Sesión local, actualización instalada de bases existentes, publicación y E2E
amplios siguen fuera. H5.6 sesión local y protección de endpoints queda siguiente,
sin iniciar; consentimientos de proveedores/smokes siguen agotados.

## D044 — Sesión efímera local y guardia uniforme antes del acceso al producto

Estado: implementado y verificado offline el 2026-10-13.
[Operación, amenazas, pruebas y límites](archive/phase-006/H5.6_SESSION.md).

Clave aleatoria por proceso en archivo temporal exclusivo 0600/directorio 0700,
fuera de proyectos/SQLite. Arranque anuncia solo su ruta. Sirve como capacidad
de establecimiento durante ese proceso; no crea una contraseña permanente ni
toca las credenciales/almacenes de proveedores. Sesiones con tokens independientes,
hashes en memoria, cookie HttpOnly/SameSite=Strict/Path=/api, ocho horas absolutas,
32 sesiones máximas y diez intentos de acceso por minuto. Reinicio invalida todas;
apagado normal retira el archivo. Caída puede dejar un secreto privado ya inválido.

La guardia HTTP compartida precede a validación/lectura/escritura: Host loopback,
Origin exacto (esquema/host/puerto) incluso en GET, rechazo cross-site y cabecera
CSRF en mutaciones. Loopback/X-Harness-Local nunca son credenciales. Solo assets
estáticos y POST de establecimiento son públicos; toda API, OpenAPI, evidencias,
health y SSE requieren sesión. Respuestas no-store/no-referrer/nosniff/DENY.
Entrada de login acotada y errores sin eco de credenciales. Solo Set-Cookie del
intercambio autorizado entrega el token al navegador; no hay URLs con tokens.

Caducidad/cierre impiden peticiones nuevas y terminan streams antes de eventos
posteriores. No cancelan acciones admitidas ni trabajos/lotes autorizados. UI
retira datos al perder sesión, permite acceso/cierre explícitos y conserva los
sobres pendientes para repetición humana, sin reenvío automático. Restauraciones
permiten sesión en memoria y mantienen las restricciones H5.2 del producto.
No cambia esquema/codec/adaptador/locks, identidad auditada ni opt-in de runtime.

Frontera: permisos POSIX frente a lectores de otros UID y páginas web ajenas;
no aislamiento contra propietario/root, navegador/extensiones comprometidos,
lectura del perfil/portapapeles o código ejecutado con el UID. HTTP loopback sin
TLS ni Secure; las cookies no aíslan puertos. Un servidor local hostil visitado
en el mismo hostname puede recibirlas en una ruta /api: ese escenario queda
fuera de protección. No se promete seguridad multiusuario endurecida, bloqueo
de DoS ni soporte de otras plataformas. Los secretos persistentes de proveedores
siguen en sus almacenes existentes; no se añade un almacén persistente de login.

Paquete instalado comprobado offline con sesión, simulación/reinicio y restauración
de consulta. Navegador bloqueó la URL sintética (`ERR_BLOCKED_BY_CLIENT`), sin
acreditar QA visual. H5.7 recorridos E2E offline es la siguiente tarea, sin iniciar;
consentimientos de proveedores/smokes agotados. No hay publicación ni push.

## D045 — Recorridos offline consolidados y cierre acotado del hito 5

Estado: implementado y verificado offline el 2026-10-13.
[Recorridos, matriz de cobertura y límites](archive/phase-006/H5.7_E2E.md).

H5.7 conecta las fronteras existentes mediante seis pruebas de API/sesión,
Git/SQLite y puertos de agente/comandos falsos. Reutiliza la regresión anterior
para caídas de procesos sintéticos, streams, conciliación Git, expiración de
permisos, SSE y segundo perfil. Sin cambios del producto, esquema, codec o locks.

El verificador de distribución incorpora bootstrap/primera tarea/commit/reinicio
y comparación de evidencia restaurada. La factory sintética autónoma se copia a
un directorio temporal, no se empaqueta ni importa código del checkout durante
el servicio instalado. Git es real, los agentes falsos y la red solo loopback.
Restauración de consulta sin checkout original, supervisor ni mutaciones.

Chrome rechaza la URL local con ERR_BLOCKED_BY_CLIENT: no se acredita QA visual
ni recorrido por clic en H5.7. El criterio condicional de NEXT_STEPS permite
registrar ese bloqueo; las pruebas HTTP/cliente quedan identificadas como tales.
No se altera la protección del navegador ni se interpreta como fallo del producto.

Concluye el último incremento offline previsto del hito 5, sin certificar un
recorrido real de proveedores ni todos los límites del MVP. Siguiente paso:
revisar el cierre y acordar nuevo alcance con el usuario, sin implementar otra
tarea ni consumir proveedores. D033.8 y los consentimientos agotados se conservan.

## D046 — Revisión del cierre offline y separación de la preparación para uso real

Estado: revisión documental/estática completada el 2026-10-13; próximo incremento
pendiente de elección del usuario en esa revisión. [Dictamen](archive/phase-006/REVIEW.md).
Elección resuelta e incremento implementado posteriormente en D047.

La evidencia H5.7 satisface el criterio de instalación/flujo/restauración para
puertos sintéticos. No certifica el MVP completo, QA visual reciente ni un piloto
con proveedores. Se hace explícita la ausencia del ejecutor de validaciones de
producto ya delimitada en D038: existen protocolo/inyección y runner real de
tests, pero no un adaptador de comandos del servicio con recuperación verificada.

Se recomienda concretar ese incremento offline antes de operar sobre proyectos
reales. Prioridad consultada al usuario junto a QA visual y preparación de smoke;
no se registra ninguna opción como elegida sin respuesta. Sin cambio de diseño,
implementación adicional ni consumo; D033.8 conserva su autorización específica.

## D047 — Validadores nativos opt-in con captura acotada y recuperación conservadora

Estado: implementado y verificado offline el 2026-10-13.
[Entrega y límites](archive/phase-006/COMMAND_RUNNER.md), según el
[alcance escrito antes de implementar](archive/phase-006/NEXT_STEPS.md).
El usuario eligió explícitamente este incremento y autorizó commit; resuelta la
prioridad pendiente de D046. No autoriza proveedores, smokes ni piloto.
Revisión independiente completada en D048, con un hallazgo corregido.

`ManagedCommandRunner`/`CommandConfig` (`commands-1`) se inyectan por la factory
del servidor, con journal ligado al job. Checkout confiable explícito,
autorización por Command completo, ejecutables absolutos, entorno sin herencia y
límites congelados por hash en versiones. Configuración ausente/anterior/distinta
no ejecuta silenciosamente el nuevo adaptador. No reescribe contexto, contratos,
prompts, permisos ni snapshots anteriores. Los prefijos del perfil siguen siendo
política, no permisos de agentes ni aislamiento físico de scripts o red.

Se reutilizan cola, propietario/lease, lock, gate y grupos POSIX H2.2/H2.3.
Intención e identidad confirmadas antes de GO; journal propio por command_id en
`managed_events`, sin tabla/migración/cola nueva ni intentos de agente ficticios.
Captura incremental exacta en fragmentos base64 con offsets/hashes dentro de
SQLite; 64 KiB predeterminados y máximo 1 MiB por stream. Al exceder el límite,
termina el grupo propio y marca truncamiento; captura incompleta no acredita
éxito. Exit nullable observado, duración, timeout, errores, bytes leídos/guardados,
EOF y estado del grupo separados de JUnit/review. Sin retry/fallback del runner.

Los fallos de persistencia y grupos inciertos abortan el motor sin más efectos.
Un líder muerto no acredita muerte de hijos. Caída o lease vencido conservan
exclusión y recuperación pendiente; la confirmación existente exige propietario
cerrado/ausente y grupos ausentes, incluidos validadores. No envía señales a PIDs
recuperados ni relanza/adopta resultados parciales. Revalidación exige una acción
explícita posterior. Garantía cooperativa POSIX: código confiable sin daemonizar,
escapar del grupo o delegar procesos a servicios externos; no sandbox físico,
cuotas de recursos/red ni defensa frente al dueño/root.

Preparación, validación y check de fase conservan sus puertas. JUnit y aceptación
siguen vinculados al contenido exacto; un ACCEPT no supera fallos ni deriva Git.
Codec 7 solo cuando hay captura nativa; lectura/roundtrip de formatos 1–6 sin
campos nuevos en resultados antiguos. Esquema `0013_bootstrap`, cli-4 y dependencias
sin cambios. Backup conserva los bytes en SQLite; backup/retención consideran
estos grupos al exigir parada. Restaurar sigue siendo de consulta, sin reactivar.

Pruebas sintéticas de procesos y caída real del supervisor, Git/SQLite temporales,
Node/npm/TypeScript offline y agentes falsos hasta commit y restauración. Ningún
proveedor, red, configuración global, ReferenceProject ni harness de desarrollo.
Composición completa para uso real, piloto, aislamiento físico, otras plataformas,
QA visual y retención de capturas SQLite quedan fuera. Siguiente tarea propuesta:
revisión independiente del incremento y su recuperación, sin iniciarla.

## D048 — Revisión del ejecutor de validaciones: runner congelado obligatorio

Estado: revisión completada y hallazgo corregido offline el 2026-10-13.
[Dictamen](archive/phase-006/COMMAND_RUNNER_REVIEW.md) sobre D047, pedido por el usuario
en sesión manual. No autoriza proveedores, smokes, piloto ni composición real.

Un run cuyas versiones congeladas incluyen `command_config_sha256` solo ejecuta
comandos mediante un runner que se enlace al journal y verifique esa
configuración. Si la composición devuelve otro runner, el supervisor aborta
antes de efectos con cuarentena y confirmación explícita existente; no degrada
al runner disponible ni reescribe versiones. Runs sin esa clave no cambian.

Sin hallazgos en la ventana intención/identidad/GO, exclusión, captura ni
compatibilidad de historiales. Se registran como límites conocidos la liveness
por PGID sin instante de arranque y la continuación de un validador silencioso
tras fallar el heartbeat; no se cambia el diseño. Esquema, codec, cli-4,
OpenAPI, UI y dependencias sin cambios.

## D049 — Composición de uso real por TOML local del operador

Estado: implementado y verificado offline el 2026-10-13.
[Entrega y operación](archive/phase-006/LOCAL_CONFIG.md), según el
[alcance escrito antes de implementar](archive/phase-006/NEXT_STEPS.md).
Decisiones del usuario: TOML fuera del checkout leído con `tomllib`, sin
dependencias nuevas, y perfil TypeScript web como primera composición.
No autoriza proveedores, smokes ni piloto; D033.8 conserva su autorización.

`local-config-1` es la autoridad local del operador para proyectos, confianza,
ejecutables, entornos, CLI, modelos/esfuerzos, autorizaciones exactas de comandos
y Git. Archivo privado, sin enlaces y fuera de todo checkout; no contiene
secretos. Nada se lee del repositorio gestionado; el `project.yaml` portable de
la especificación queda como trabajo posterior y nunca concedería confianza.
Sin valores implícitos para lo que concede efectos; claves desconocidas se
rechazan. Cargar no lanza procesos.

Cada job compone adaptadores nuevos (cli-4, commands-1, Git). Las versiones
congeladas incluyen hashes de adaptadores y de la composición del proyecto; si
difieren al ejecutar o hacer commit, el job entra en cuarentena antes de
efectos. Cambiar la composición exige terminar o detener antes los jobs.
`USER` del entorno CLI se comprueba contra el UID local (D024). Entrada por
`serve --config`, incompatible con `HARNESS_MANAGED_CONFIG`, y `check-config`
con preflight opcional de version/help. Esquema, codec, cli-4, OpenAPI y UI sin
cambios; la validación de proyectos del runtime se reutiliza sin alterarla.

## D050 — Propuesta de primer uso real: selecciones del usuario y límites

Estado: propuesta preparada y ensayada offline el 2026-10-13; **ejecutada una vez
con autorización del usuario el mismo día** y completa ([resultado](archive/phase-006/FIRST_USE_RUN.md),
D051). Consentimiento agotado. Propuesta (archivo `docs/discovery/FIRST_USE_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/FIRST_USE_PROPOSAL.md`). Concreta D033.8.

Selecciones elegidas por el usuario en esta sesión: ejecutor Claude
`claude-sonnet-4-6`/`low` con herramientas `Read`, `Edit`, `Write`, `Glob`,
`Grep` (sin `Bash` ni concesiones); revisor y evaluación de fase Codex
`gpt-6-luna`/`medium`; planificador `gpt-6-luna`/`low` declarado pero no
invocado (`planning_mode = "deterministic"`). `max_revision_cycles = 0`: como
máximo tres invocaciones de proveedor, sin reintentos ni correcciones.

Checkout desechable fuera del repositorio desde la fixture `typescript_web` con
una regresión deliberada, preparado por `examples/first_use/prepare.sh`. Claude
se fija al binario versionado 2.1.295 porque el enlace del usuario ya apunta a
2.1.296, que `cli-4` no admite; no se amplía el baseline ni se sustituye la
versión. Los tags de fase son nombres simples (`first-use-p001`).

Ejecutar requiere consentimiento específico del usuario para esta propuesta;
cualquier cambio de modelo, esfuerzo, herramientas, límites o entorno exige
actualizarla antes (solo `BASE` puede cambiar si ya existe, registrándolo). Sin cambios de diseño, código, esquema,
codec, cli-4, OpenAPI ni UI.

## D051 — Operación real desde el wheel instalado, no desde el checkout de desarrollo

Estado: decidido y aplicado el 2026-10-13 durante la ejecución D050, tras
consultar al usuario («la opción más mantenible… modular y reutilizable»).
[Resultado](archive/phase-006/FIRST_USE_RUN.md).

`harness-local serve` exige los assets web empaquetados (D043), que la
instalación editable de desarrollo no tiene. No se añade un modo de desarrollo
ni se sirve con uvicorn directo para uso real. El uso real se opera desde un
paquete construido y verificado con el procedimiento existente: primero
`build_distribution.py --out-dir` en un directorio propio de la operación,
después `check_distribution.py --dist` sobre ese paquete, y por último un venv
nuevo con instalación offline por hashes. `check-config` y `serve --config` se
ejecutan con el binario instalado, fuera del checkout del producto. El `dist/`
del repositorio no es autoridad: puede estar desactualizado.

Las versiones congeladas no dependen de la vía de instalación (`engine`
incluye la versión del paquete), por lo que el TOML y sus hashes no cambian.
La entrada `HARNESS_MANAGED_CONFIG` + uvicorn sigue siendo solo de desarrollo.
Sin cambios de código, esquema, codec, cli-4, OpenAPI ni UI.

## D052 — Revisor y ejecutor con proveedor, modelo y esfuerzo elegidos por el usuario

Estado: decidido por el usuario el 2026-10-13; **implementado y verificado offline**
el mismo día como `cli-5` / `local-config-2` ([entrega](archive/phase-007/AGENT_ROLES.md)).
[Alcance](archive/phase-007/NEXT_STEPS.md). Sustituye la asignación fija
«Codex planifica y revisa, Claude ejecuta» de la especificación (§1, F05 y la
tabla de prompts) y de los adaptadores `cli-1`…`cli-4`.

Dos agentes: revisor (planificación, revisión, fase, chat y bootstrap; solo
lectura) y ejecutor (único escritor). Cada uno puede ser Codex o Claude, en
cualquier combinación. El usuario fija proveedor, modelo y esfuerzo del
revisor. El revisor fija modelo y esfuerzo del ejecutor en cada tarea y en cada
revisión, en uno de dos modos configurables por proyecto: catálogo acotado por
el usuario, o libre. Toda tarea pasa por el revisor y, por ahora, el revisor
siempre planifica. La decisión de planificar o despachar directamente
(«JEV», término del usuario) queda para el futuro. La planificación
determinista se mantiene como ajuste del usuario: con ella, el ejecutor recibe
el contrato y la selección directamente de NEXT_STEPS, sin planificación del
revisor, que sigue revisando el resultado.

No se reescriben historiales ni versiones congeladas anteriores.

Detalles de la implementación, resueltos con criterio y sin cambiar el diseño:

- Claude 2.1.296 entra en el baseline porque su ayuda es idéntica a la de 2.1.295.
- La escritura con Codex exige 0.162.1, la única versión caracterizada.
- El vocabulario de esfuerzo de Codex se toma de las cadenas del binario, porque
  la ayuda no lo enumera.
- El lector Claude añade `--restricted` y `--json-schema`.
- En modo libre, el catálogo queda como selección de referencia para los
  contratos del servidor.
- `local-config-1` se sigue leyendo con su política, planificador separado incluido.
- Los jobs pendientes congelados con `cli-4` entran en cuarentena al actualizar.

Esquema, codec y locks sin cambios; OpenAPI y UI añaden `agents` al proyecto. No
autoriza el smoke con proveedores.

## D053 — Comando único de desarrollo con migración y backup previo

Estado: implementado y verificado offline el 2026-10-13.
[Entrega](archive/phase-006/DEV_COMMAND.md). Decisiones del usuario: modo desarrollo
(API + Vite) y migración automática con backup.

`scripts/dev` sincroniza Python por `uv run --frozen`, reinstala el frontend
solo si cambió su lock, prepara la SQLite con `storage/migrate.py` y supervisa
API (:8013) y Vite (:5173) como grupos propios que se detienen juntos. Antes de
migrar, una instantánea SQLite verificada (`premigration-1`) sustituye al
bundle H5.2, que exige el esquema actual. Se rechazan una revisión desconocida,
una restauración de consulta, una base sin Alembic y un servicio vivo. Un fallo
no restaura automáticamente. `serve`/`init-db` del paquete conservan D043.

Corregido de paso el proxy de Vite (forma objeto con `changeOrigin: false`):
la abreviatura de cadena reescribía Host y rompía el login de la UI de
desarrollo frente a la guardia H5.6. Sin cambios de esquema, codec, cli-4,
OpenAPI ni dependencias.

## D054 — Hito de UI de producto después de D052 y registro de proyectos en SQLite

Estado: decidido por el usuario el 2026-10-13; **no implementado**; forma concretada en D076. Backlog,
hito 6 (H6.1 = D052, H6.2 = UI).

La UI actual es una superficie funcional construida hito a hito para verificar
entregas. No sigue un sistema de diseño ni las convenciones de un dashboard, y
nunca tuvo QA visual con navegador. Se planifica un hito de interfaz de producto
**después** del backend de D052, para no rediseñar dos veces la configuración
de agentes.

Alta de proyectos desde la UI: registro en SQLite con confirmación explícita de
confianza, ruta canónica y perfil, auditable y versionado. Esto relaja la regla
de D028/D049, según la cual solo el servidor registra proyectos. Los ejecutables
y entornos de los agentes no se conceden por HTTP sin validación; su forma
exacta (archivo del operador o ajustes globales validados) se concreta en el
alcance de H6.2, igual que la convivencia con el TOML `local-config`.

## D055 — Propuesta del smoke de la matriz D052: selecciones del usuario y límites

Estado: propuesta preparada y ensayada offline el 2026-10-13. **Ejecutada con
autorización del usuario el mismo día y detenida**
([resultado](archive/phase-007/PROVIDER_MATRIX_RUN.md)). La combinación 1 falló en el
planificador por un contrato ambiguo de `validation_commands`; el usuario
decidió parar y corregir, así que 2–4 no se lanzaron. Una sola invocación de
proveedor. Consentimiento agotado. Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_PROPOSAL.md`).

Los comandos que lanzan agentes los ejecutó el usuario con `!`, porque el
clasificador de permisos de Claude Code bloqueó el script de recorrido.

Selecciones del usuario en esta sesión:

- Las cuatro combinaciones revisor → ejecutor.
- `planning_mode = "agent"`: el revisor planifica, el ejecutor edita y el
  revisor revisa; después, commit sin proveedor. Sin check ni cierre de fase.
- Modelos de D050: Codex `gpt-6-luna` y Claude `claude-sonnet-4-6`. Revisor
  `medium`; catálogo del ejecutor `low`.
- Un fallo detiene solo su combinación, sin reintento; las demás continúan.

Concretado con criterio:

- `executor_mode = "catalog"` con un solo modelo y un solo esfuerzo, y
  `max_revision_cycles = 0`. Como máximo tres invocaciones por combinación y
  doce en total.
- Claude 2.1.296 por ruta versionada, con `DISABLE_AUTOUPDATER=1`.
- Un área, un TOML `local-config-2` y un servicio por combinación, operados
  desde un único wheel instalado (D051).
- Autorizadas exactamente las variantes `npm run check|test|build` de 1800 s
  que el planificador puede proponer.
- Si un fallo es de autenticación, cuota o preflight de un proveedor, las
  combinaciones pendientes que lo usan no se lanzan.

Ejecutar requiere consentimiento específico del usuario para esta propuesta.
Cualquier cambio de combinación, modelo, esfuerzo, modo, herramientas, límites
o entorno exige actualizarla antes. Solo `BASE` puede cambiar si ya existe, y
el cambio se registra. Sin cambios de código, esquema, codec, `cli-5`,
OpenAPI ni UI.

## D056 — Formas de salida de los agentes alineadas con los validadores del motor

Estado: decidido con criterio, implementado y verificado offline el 2026-10-13.
[Entrega](archive/phase-007/CONTRACT_SHAPES.md). Origen: el smoke D055 se detuvo porque
un planificador real devolvió `validation_commands` como listas de argv.

Se aplican las dos medidas, porque la plantilla es editable por el usuario
(H3.1) y el modelo puede volver a interpretarla así:

- **Aclarar.** La plantilla integrada `plan-task` pide una cadena sin shell por
  comando, y `[]` cuando bastan las validaciones del perfil. El esquema fijo del
  motor tipa los elementos de toda lista. El revisor declara como opcionales sus
  campos y la forma de `findings`. Los campos obligatorios no cambian.
- **Normalizar.** `task_contract` convierte una lista de argv de
  `validation_commands` en `shlex.join(argv)`, que es equivalente y vuelve al
  mismo argv. Las demás formas se siguen rechazando.
  - Contrato congelado en cadenas; salida original conservada en el intento.
  - Los contratos del servidor deben ser canónicos.

Sin cambios de argv (`cli-5`), esquema, codec, OpenAPI ni UI. Los historiales,
contratos y catálogos congelados no se reescriben. No autoriza ninguna
ejecución con proveedores.

## D057 — Nueva ejecución de la matriz D052 tras D056

Estado: propuesta preparada y ensayada offline el 2026-10-13. **Ejecutada el
mismo día y cerrada** ([resultado](archive/phase-007/PROVIDER_MATRIX_RERUN.md)):

- 1 (Codex→Claude) `COMMITTED`.
- 2 (Codex→Codex) `REVISION_LIMIT`, porque el escritor Codex no editó.
- 3 (Claude→Claude) `STOPPED` en `planner`: el `--json-schema` sin tipos hizo
  que Claude serializara listas como texto.
- 4 no lanzada por decisión del usuario.

Siete invocaciones de proveedor. Consentimiento agotado.
Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md`).

Repite D055 sin cambiar selecciones, límites ni criterios, con lo siguiente:

- Área nueva `/private/tmp/harness-provider-matrix-2`.
- Wheel con D056.
- Scripts versionados en `examples/provider_matrix/`: `run_pairing.sh` y
  `drive.py`. Este espera hasta el final real del job y guarda la instantánea
  completa.
- Reparto de la ejecución:
  - Claude Code prepara, verifica y revisa la evidencia entre combinaciones.
  - El usuario lanza con `!` cada orden que arranca agentes, porque el
    clasificador de permisos de Claude Code las bloquea.

Ejecutarla requiere consentimiento específico del usuario. Cualquier cambio de
selecciones, límites o entorno exige actualizarla antes (solo `BASE` puede
cambiar si ya existe, y se registra). Sin cambios de código del producto.

## D058 — `--json-schema` tipado para el lector Claude (`cli-6`)

Estado: decidido con criterio, implementado y verificado offline el 2026-10-13.
[Entrega](archive/phase-007/TYPED_JSON_SCHEMA.md). Origen: en la combinación 3 de D057,
el lector Claude devolvió listas y objetos como cadenas JSON porque el
`--json-schema` de `cli-5` solo declaraba `required`.

- **Adaptador `cli-6`.** El `--json-schema` del lector Claude es el
  `output_schema` del motor congelado en la instantánea del prompt del intento
  (comprobado contra su hash), el mismo que lee el agente. Sin instantánea, el
  esquema fijo del rol. El resto del argv, el escritor y Codex no cambian.
- **`additionalProperties: true`**, como en el prompt: un único contrato. Los
  validadores del motor siguen siendo la autoridad.
- **Sin normalización** de listas u objetos serializados como texto: se siguen
  rechazando. La causa se corrige en el transporte; una cadena JSON es un
  error de tipo, no una forma equivalente como el argv de D056, y las rutas
  delimitan permisos.
- Los jobs pendientes congelados con `cli-5` entran en cuarentena al actualizar,
  como en D052. Preflight, esquema, codec, OpenAPI, UI y `local-config-2` sin
  cambios. Historiales y congelados no se reescriben.

No autoriza ninguna ejecución con proveedores.

## D059 — Diagnóstico del escritor Codex y raíces explícitas (`cli-7`)

Estado: diagnóstico completado y mitigación implementada offline el 2026-10-13.
[Evidencia, medidas y límites](archive/phase-007/CODEX_WRITER_ROOTS.md). Petición del
usuario: completar esta tarea sin lanzar sesiones y realizar commit.

La causa inmediata observada en D057 es una interpretación incorrecta del
modelo: negó que el checkout fuese escribible sin intentar herramientas, aunque
el archivo estaba dentro de la raíz `/private/tmp` que mencionaba. No hay
denegación real de escritura observada. La lectura de Codex 0.162.1 identifica
la plantilla que permite editar cwd y writable_roots, la descripción de raíces
y las vías cwd, `/tmp` y TMPDIR. La lista generada internamente no se conservó;
el origen de la confusión en las raíces temporales sigue siendo una hipótesis.

Se eligen dos medidas complementarias solo para Codex ejecutor: declarar
`sandbox_workspace_write.writable_roots` con el checkout canónico y
`sandbox_workspace_write.exclude_slash_tmp=true`, y aclarar en la entrada de
transporte que el acceso solicitado incluye sus subdirectorios. Se conserva
TMPDIR del entorno explícito con el comportamiento predeterminado de la CLI.
El contrato y la política siguen delimitando qué editar; las denegaciones
reales deben respetarse. Sin ampliar red/aprobaciones ni modificar ajustes
globales. No se mueve el checkout del smoke: esa medida solo cubriría el ensayo.

El cambio de argv y entrada de transporte exige `cli-7`. El texto añadido queda
persistido por hash en la intención de proceso, sin reescribir prompts,
contratos, permisos o historiales congelados. Jobs `cli-6` quedan en cuarentena
antes del preflight/efectos por la comparación existente de versiones.
Lectores y Claude conservan su transporte. Esquema, codec, local-config,
OpenAPI, UI y dependencias sin cambios.

Pruebas de argv/TOML, CLI sintética, recorridos de ambos revisores con Codex
ejecutor y cuarentena. La mitigación no certifica una escritura real ni qué
mensaje de permisos verá Codex. No autoriza otra matriz con proveedores.

## D060 — Propuesta acotada de las combinaciones 2–4 con paquete `cli-7`

Estado: preparada y verificada offline el 2026-10-13; **ejecutada una vez con
consentimiento específico el mismo día y cerrada con parada preventiva (D061)**.
[Resultado](archive/phase-007/PROVIDER_MATRIX_CLI7_RUN.md).
Propuesta y órdenes (archivo `docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md`),
[manifiesto de paquete/configuración y ensayo sintético](archive/phase-007/PROVIDER_MATRIX_CLI7_PREPARATION.json).
Petición inicial del usuario: completar únicamente la preparación activa de
NEXT_STEPS y realizar commit, sin autorizar entonces la ejecución. Autorización
posterior específica y resultado registrados en D061.

Se propone conservar las selecciones, herramientas, entorno y recorrido de
D055/D057 para 2 Codex→Codex, 3 Claude→Claude y 4 Claude→Codex, en ese orden.
La combinación 1 ya completa no se repite. Codex `gpt-6-luna`, Claude
`claude-sonnet-4-6`; revisor medium, catálogo del ejecutor low, planificación
agent, cero ciclos de corrección. Máximo nueve invocaciones (cinco Codex y
cuatro Claude), con timeouts 600/900 s; límite operativo total propuesto de
90 minutos. Sin retry, fallback, check/cierre ni otros flujos.

Área nueva `/private/tmp/harness-provider-matrix-3`: tres TOML privados,
checkouts desechables, wheel/sdist `cli-7` y venv instalado offline por hashes
(D051). `prepare.sh` admite pares explícitos y conserva las cuatro
combinaciones por defecto. Incluye las modificaciones de transporte
D058/D059 sin alterar historiales anteriores. El manifiesto fija los hashes
del paquete y de las configuraciones. Estado vacío y check-config válido;
preflight real pendiente, no se ejecutaron las CLI reales ni version/help.

Ensayo separado con CLI sintéticas por el servicio instalado: tres COMMITTED
con commit único acotado, validaciones/JUnit y evidencias congeladas;
salida inválida detiene planner sin ejecutor/revisor/commit. No acredita la
escritura real de Codex, el mensaje interno de permisos ni Claude real con el
esquema tipado. Áreas D055/D057 conservadas.

Ejecutar D060 requiere consentimiento específico nuevo para una sola matriz
acotada. Revisar entre combinaciones: fallos detienen su par; auth/cuota/preflight
omiten pares pendientes que usan el proveedor afectado; efectos fuera del área,
servicio no detenible o plazo total agotado paran todo. Sin reutilizar los
consentimientos agotados D050/D055/D057 ni avanzar a H6.2.

## D061 — Ejecución de D060: Codex escritor real y parada por cambio global

Estado: ejecutada una vez y cerrada con parada preventiva el 2026-10-13.
[Resultado y límites](archive/phase-007/PROVIDER_MATRIX_CLI7_RUN.md),
[manifiesto](archive/phase-007/PROVIDER_MATRIX_CLI7_RESULT.json). El usuario autorizó
D060 («Autorizo») después de revisar propuesta, selecciones y límites.
Consentimiento agotado; no se reutiliza para continuar las combinaciones.

Solo la 2 Codex→Codex se ejecutó: tres invocaciones COMPLETE, edición real
acotada, check/test/build y JUnit correctos, review ACCEPT y commit por
contenido exacto (`585a35c`). Valida la escritura de Codex con D059 en este
ensayo; no demuestra la causa de la negativa de D057. Jobs DONE, propietarios
cerrados, procesos muertos, cero locks y servicio detenido con clave retirada.

La comprobación entre combinaciones detecta cambio de hash en
`~/.codex/config.toml`. mtime coincide con el inicio del escritor y se observa
una entrada de confianza para su checkout. La línea base solo contiene hashes:
delta exacto y atribución a la CLI quedan sin demostrar. Se aplica la condición
de parada global de D060 preventivamente; 3/4 no se lanzan y conservan estado
vacío. No se restaura ni edita directamente la configuración global.
No es una auditoría exhaustiva; se distingue observación de inferencia.

Sin cambios de diseño, producto o versiones. Claude real con D058 continúa
pendiente. Siguiente tarea: diagnóstico offline del cambio global, separado
de esta ejecución y sin nuevas invocaciones. Cualquier matriz posterior exige
propuesta y consentimiento nuevos; H6.2 no se inicia.

## D062 — Delta de confianza acreditado y límite de contención de la CLI

Estado: diagnóstico offline completado el 2026-10-13; **sin corrección de
transporte implementada**. [Evidencia y opciones](archive/phase-007/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
[manifiesto](archive/phase-007/CODEX_GLOBAL_CONFIG_DIAGNOSIS.json). Petición del
usuario: «continúa», sobre el diagnóstico activo, sin consumo nuevo.

Se acredita el delta D061 por SHA-256: la inversa en memoria que quita solo
la sección observada de 93 bytes coincide con la línea base previa. La entrada
de confianza del checkout de la 2 fue añadida y es todo el delta de bytes;
no se guardan/copían contenidos completos ni se restaura el archivo global.

La CLI fijada contiene una vía interna de thread/start que llama a
`set_project_trust_level` y aplica cambios a `config.toml`. Omisión de carga
de config/reglas y no persistencia de sesiones no son una frontera de escritura
para el proceso CLI. Delta, vía estática y tiempos apuntan al arranque de
Codex; atribución al proceso original inferida sin auditoría de syscalls.

No se añade un override de confianza sin demostrar que evite persistencia,
ni se cambia CODEX_HOME/HOME/almacén de auth sin comprobar autenticación
existente. `FileAuthStorage` usa auth.json y la ayuda liga auth a CODEX_HOME;
redirigir estado puede perder la sesión. No se copian/enlazan credenciales,
restauran ajustes globales ni amplían permisos para pasar un ensayo.

Límite registrado antes de modificar diseño. Siguiente: concretar propuesta
de contención del proceso Codex compatible con auth, antes de implementación.
Sin cambios de producto, `cli-7`, esquema, codec o congelados. Sin CLI reales,
red, proveedores o avance a la matriz/H6.2; consentimientos siguen agotados.

## D063 — Propuesta de frontera externa de escritura; auth compatible aún no certificada

Estado: propuesta concretada y experimento sintético completado el 2026-10-13;
**sin implementación en producto**. [Alcance, alternativas y criterios](archive/phase-007/CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
[evidencia](archive/phase-007/CODEX_PROCESS_CONTAINMENT_EVIDENCE.json).

Se elige como candidata para calificación offline una frontera externa macOS
que conserve HOME/USER y lectura de auth en origen, denegando escrituras fuera
de checkout/TMPDIR explícitos. No se adopta CODEX_HOME privado sin una vía de
auth separada acreditada para 0.162.1; símbolos de file/keyring/ephemeral no
prueban compatibilidad ni el almacén efectivo. No copiar/enlazar credenciales,
cambiar login/almacén, restaurar configuración ni precrear confianza.

Experimento independiente de producto: sandbox-exec con HOME y token ficticios
permite lectura y escrituras en raíces de ensayo, deniega ocho operaciones
fuera de ellas y una escritura de hijo; originales conservados. El primer
intento dentro del sandbox de desarrollo no pudo aplicar el perfil; el ensayo
fuera fue autorizado. No se equipara esto al sandbox interno de Codex ni al
comportamiento real de auth. Perfil experimental permite lecturas/IPC generales;
no acredita aislamiento contra delegación a servicios o exposición de secretos.

Límite material registrado antes de implementar: denegar persistencia local no
impide refresh remoto ni garantiza continuidad de sesión. Compatibilidad de
sandbox anidado, auxiliares, fuente de auth y efectos de refresh requieren
calificación; si no se puede garantizar ausencia de refresh, no se consume sin
una decisión específica sobre ese riesgo. No se relaja la prohibición global.

La propuesta detalla errores sin retries/fallback del harness, futura versión
cli-8/configuración versionada y cuarentena antes de efectos, solo si se integra
tras calificación. No se cambia cli-7, local-config-2, D024/D059, esquema, codec,
permisos o congelados. Siguiente tarea: calificación offline sintética acotada,
sin CLI real. Otra prueba real necesita propuesta y consentimiento específicos;
D050/D055/D057/D060 agotados, matriz y H6.2 sin iniciar.

## D064 — Contención sintética calificada con límites que impiden su integración

Estado: calificación offline completada el 2026-10-14; **candidata no apta para
integración tal como está**, sin cambios de producto. [Dictamen y reproducción](archive/phase-007/CODEX_CONTAINMENT_QUALIFICATION.md),
[evidencia](archive/phase-007/CODEX_CONTAINMENT_QUALIFICATION.json).

La matriz final de 27 casos con HOME/auth ficticios confirma denegación de
escrituras directas y diferenciación lector/escritor/TMPDIR, auxiliares,
descendientes, errores de auth ficticia, launcher/perfil y gate/cancelación.
Auth/config ficticios conservan bytes, modo y mtime. El sandbox de desarrollo
rechaza aplicar el perfil; los ensayos exteriores fueron autorizados mediante
permisos de herramienta. Ningún rechazo provoca lanzamiento sin contención.

Tres escapes observados en archivos sacrificiales separados: fd abierto antes
del sandbox, hardlink preexistente y delegación por pipe a un helper externo.
Cerrar fd evita el primero; admisión canónica y rechazo de aliases no prueban
protección contra carreras. Socket Unix propio denegado no acredita Mach/XPC,
llavero ni otros servicios, que no se tocaron. Anidamiento escritor sintético
correcto; lector rechazado con exit 71 antes del objetivo. No se atribuye este
resultado al perfil interno exacto de Codex ni se elimina ese sandbox.

No integrar el perfil D063, ampliar raíces, permitir escrituras globales ni
cambiar almacén para superar el ensayo. Antes de cualquier integración, tarea
separada de diagnóstico del anidamiento lector y propuesta de frontera revisada
con criterios para fd, aliases/carreras e IPC. Un cambio de auth/aislamiento o
riesgo aceptado deberá exponerse como decisión de diseño pendiente del usuario.
No se implementa cli-8 ni local-config-3; núcleo, permisos e historiales intactos.

Refresh ficticio solo prueba save local denegado, no rotación remota ni
continuidad de sesión. Ninguna CLI real, preflight, login, lectura/copia/enlace
de credenciales reales, cambio global o red externa. Consumo futuro requiere
propuesta/consentimiento nuevos con el límite de refresh resuelto. Matriz y
H6.2 sin iniciar; D050/D055/D057/D060 siguen agotados.

## D065 — Anidamiento condicionado por el perfil y frontera revisada no calificada

Estado: diagnóstico y dictamen offline completados el 2026-10-14; **sin
integración en producto**. [Resultados y criterios](archive/phase-007/CODEX_CONTAINMENT_REVISION.md),
[evidencia](archive/phase-007/CODEX_CONTAINMENT_REVISION.json) y
[sonda sintética](archive/phase-007/CODEX_CONTAINMENT_REVISION.py).
Petición del usuario: completar solo la tarea activa y realizar commit.

D064 no demuestra una imposibilidad general de anidar un lector. Perfiles
sintéticos lector→lector y escritor→escritor funcionan con ambas capas y
HOME/auth ficticios en origen. Composiciones ensayadas con restricciones
distintas fallan en la segunda aplicación con exit 71 antes del objetivo;
cwd, archivo/inline y programa objetivo no explican el rechazo. Comentarios,
reordenación y deny redundante sí componen. Equivalencia de la representación
compilada es hipótesis; no se inspecciona kernel ni ejecuta perfil real Codex.

Cerrar fd no concedidos corta escritura por archivo y pipe heredados en los
controles propios. Captura inerte no delega. Hardlink introducido por el padre
propio después de la admisión y readiness modifica un sacrificial exterior:
precheck, permisos del mismo UID y lock cooperativo no certifican exclusión
frente a carreras. No se anuncia aislamiento general de IPC por denegar un
socket propio; Mach/XPC, llavero y launch services no se contactan.

La frontera revisada exige capas exactas compatibles, inventario/cierre de fd,
exclusión efectiva de aliases durante toda la ejecución y canales sin receptores
con autoridad exterior. No hay mecanismo calificado que cumpla el conjunto,
ni fuente de auth/auxiliares reales o refresh resueltos. Dictamen: no integrar
D063 o una variante basada solo en cerrar fd y prechecks; no demuestra que
toda solución alternativa sea imposible. No eliminar sandbox interno, ampliar
raíces ni conceder escrituras globales para hacer pasar los ensayos.

32 casos finales y 14 pytest focales correctos. Auth/config ficticios mantienen
bytes/modo/mtime; únicamente tres sacrificiales explícitos cambian. El sandbox
de desarrollo rechaza aplicar la primera capa; ejecuciones exteriores autorizadas
mediante permisos de herramienta. Errores sin fallback y evidencia preliminar
con expectativa incorrecta conservada. Sin CLI real, red externa, credenciales
reales, configuración global, cambios del adaptador/TOML/jobs o congelados.

Siguiente: elegir el alcance con el usuario tras este dictamen, **sin iniciar**
otra investigación o implementación. Una capacidad soportada de separación de
estado/auth o frontera distinta requiere evidencia propia. Relajar aislamiento,
cambiar cuenta/almacén o aceptar refresh remoto son decisiones materiales
pendientes, no concesiones implícitas. También se puede suspender la integración.
No se implementan cli-8/local-config-3 ni se autoriza consumo. Matriz 3/4 y H6.2
sin iniciar; consentimientos D050/D055/D057/D060 siguen agotados.

## D066 — Memoria de trabajo documental y controles explícitos de auto memory (`cli-8`)

Estado: controles de transporte implementados y verificados offline el
2026-10-14; **persistencia externa completa sin resolver**.
[Entrega, inventario y límites](archive/phase-007/AGENT_PERSISTENCE.md),
[evidencia](archive/phase-007/AGENT_PERSISTENCE.json).

El usuario requiere que los modelos no conserven estado/memoria global de
proyecto: el contexto duradero se mantiene en Markdown organizado en `docs/`,
historial por fase y STATE/NEXT_STEPS frescos. Después pide continuar con la
persistencia de las CLI. Se concreta la opción de capacidades soportadas de
D065, sin aceptar cambios globales, otro almacén ni aislamiento relajado.
SQLite conserva la autoridad operativa del harness; archivado/continuidad
documental real son otro alcance y no se declaran implementados.

Se desactivan explícitamente generación/inyección de memorias y la función
memories de Codex, además de history.persistence=none y ephemeral. Claude
recibe autoMemoryEnabled=false en settings inline, conservando no-session-
persistence. Un override ambiental CLAUDE_CODE_DISABLE_AUTO_MEMORY distinto
de 1, si se declara, rechaza CLIConfig antes de efectos: 0 puede reactivar la
memoria pese al setting. No se añaden variables al entorno completo recibido,
se cambian HOME/USER/auth, copian/enlazan credenciales o borran memorias existentes.

El cambio de argv exige cli-8; jobs cli-7 quedan en cuarentena antes del
preflight/efectos, sin reescribir congelados. Esta versión identifica controles
de memoria, no la integración hipotética de contención D063, que sigue sin
calificación. local-config-2 (y lectura 1), esquema/codec/API/UI/dependencias,
modelos, permisos y sandbox de herramientas conservados.

Documentación oficial actual contrastada con literales/hashes de Codex 0.162.1
y Claude 2.1.295/2.1.296, sin ejecutar esos binarios ni leer auth/config reales.
Codex 0.161.0 no disponible para lectura; baseline conservado, controles nuevos
solo probados sintéticamente para ese lector. 20 casos nuevos y 215 pertinentes
correctos, incluidas las cuatro combinaciones sintéticas. Consulta web solo
documental; ninguna inferencia, auth real o prueba de ausencia de archivos.

No se equipara memoria automática con confianza, logs/cachés/SQLite de CLI,
instrucciones estáticas o contención física. D061/D062 sigue pendiente: la CLI
puede persistir confianza al arrancar el escritor; apagar memories no acredita
supresión de esa ruta. Auth/refresh y otros auxiliares tampoco certificados.
La prohibición global y los dictámenes D064/D065 se mantienen.

Siguiente tarea separada: preparar diagnóstico de arranque Codex sin inferencia,
HOME/auth ficticios y red denegada, con controles contra lectura de secretos/
globales y límites congelados. No se ejecuta ni se da por autorizado un proceso
CLI real por esta entrega; ejecución requiere propuesta y consentimiento
específicos nuevos. Matriz 3/4 y H6.2 sin iniciar; fase de comprobaciones sin
cerrar y consentimientos D050/D055/D057/D060 agotados.

## D067 — Diagnóstico de arranque preparado con incompatibilidad, sin CLI real

Estado: preparación y dictamen completados el 2026-10-14; **candidata no apta
para ejecución real**. [Propuesta, controles y límites](archive/phase-007/CODEX_STARTUP_PREPARATION.md),
[evidencia](archive/phase-007/CODEX_STARTUP_PREPARATION.json) y
[controlador/ensayo](archive/phase-007/CODEX_STARTUP_PREPARATION.py).
El usuario pide seguir con la preparación activa; no autoriza CLI real.

Se concretan dos comandos proyectados, sin override y con confianza solo en
el transporte, nativo/hash D059/D062, memoria cli-8, HOME/CODEX_HOME/auth
ficticios, metadatos Git nuevos y límites de procesos/capturas/tiempo. El
controlador no dispone de una vía que ejecute Codex u otro proveedor.
No se restaura/precrea confianza real ni se copian/enlazan credenciales.

Cambiar HOME no basta para impedir lectura de auth/config reales. La candidata
deniega por defecto, permite solo lecturas públicas/ficticias y escrituras
ficticias, sin conceder red o servicios Mach. El proceso Python mínimo aborta
con SIGABRT antes de emitir marcador, stdout/stderr vacíos; no acredita la causa
ni la compatibilidad de Codex. El primer contexto de desarrollo falla al aplicar
perfil con exit 71; perfil inválido de control sale 65. No se equiparan errores
ni se amplían permisos para pasar. Ejecuciones exteriores sintéticas autorizadas
por el mecanismo de herramientas; ninguna CLI real.

Diez casos de controlador independiente, con Python fake fijo, verifican
persistencia observada incluso tras auth error, override que en el fake no
la evita, ausencia de cambio tras marcador sintético, auth anterior inconclusa,
evento estructurado frente a texto, fd cerrado, señal/timeout/exceso y launcher
ausente. Se distinguen del backend OS; no son fallback del caso rechazado ni
prueba de semántica del proveedor. Doce casos finales, once grupos ausentes,
originales protegidos con bytes/modo/mtime conservados, solo dos configs
sacrificiales cambian. 14 pytest focales correctos; producto sin cambios.

Dictamen permitido por los criterios: preparación completada con incompatibilidad
precisa de esta candidata. No ofrecerla para aprobación de ejecución; el siguiente
alcance debe verificar en fuente identificable del pin la condición que persiste
confianza y una posible supresión por transporte. Nombres de símbolos o docs
actuales no acreditan esa supresión. Si falta evidencia, registrar límite antes
de tocar transporte/auth/aislamiento. No se investiga ese alcance aquí.

Sin integración del perfil D063/D067, actualización de baseline, cli-8/local-
config-2, permisos, jobs/locks o congelados. Sin auth real, refresh, red externa,
subagentes, harness de desarrollo o push. Matrices 3/4, archivado y H6.2 sin
iniciar; fase de comprobaciones abierta. D050/D055/D057/D060 siguen agotados.

## D068 — Condición de confianza del pin acreditada y supresión específica (`cli-9`)

Estado: implementada/verificada el 2026-10-14. [Fuente, corrección y límites](archive/phase-007/CODEX_TRUST_SUPPRESSION.md),
[procedencia](archive/phase-007/CODEX_TRUST_SUPPRESSION.json). El usuario pide comprobar
el flujo hasta cerrarlo; se completa el prerrequisito activo D067 antes de consumir.

Etiqueta pública Codex rust-v0.162.1 resuelta al commit
092d3acd6bec3e3a14bdc7e7a2810ab628ab759d, también embebido en el nativo de
hash D059/D062. No se afirma build reproducible ni firma de tag (unsigned).
Fuente fija: thread/start persiste confianza si cwd explícito, trust ausente,
proyecto no projectless y permisos efectivos que permiten escribir cwd.
Ephemeral no forma parte de esa guardia. El writer puede evitarla con una
entrada explícita de confianza para su cwd transmitida por CLI.

Se elige untrusted solo en el transporte para no activar config/hooks locales;
workspace-write/raíces D059/network false/approval never siguen explícitos.
Tabla projects inline completa: el parser separa claves dotted por puntos sin
interpretar quoting, por lo que una ruta entre comillas en una clave dotted
sería incorrecta. No se edita/precrea/restaura config global ni cambia auth/HOME.
Solo escritores Codex 0.162.1 reciben ese override. cli-9 pone jobs cli-8 y
anteriores en cuarentena antes de preflight por la comparación existente,
sin reescribir congelados. Lectores/Claude/local-config-2/API/UI/codec conservados.

Fuente pública consultada en lectura, sin ejecutar código externo o actualizar
CLI. 217 tests de transporte pasan, dos adicionales; build y wheel instalado
offline verificados. La ausencia de toda persistencia auxiliar no se deduce:
el pin inicializa SQLite auxiliar incluso para un thread efímero. No se
integra contención D063/D067 ni se confunde memoria automática con logs/auth.
Supresión dinámica específica verificada después en D069/D071.

## D069 — Primer ensayo cli-9 detenido por contradicción del plan

Estado: ejecutado una vez y cerrado el 2026-10-14. Propuesta (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_PROPOSAL.md`),
[resultados D069/D070](archive/phase-007/PROVIDER_MATRIX_CLI9_STOPS.md) y
[evidencia](archive/phase-007/PROVIDER_MATRIX_CLI9_STOPS.json). Solo Codex→Codex,
tres COMPLETE y edición/validaciones correctas, sin cambio en muestras globales.
El planner autoriza src/estimate.ts y prohíbe **; deny prevalece. Reviewer
BLOCKED, sin aceptación/commit. Otros tres pares no lanzados. Cero locks,
owners/procesos/servicio cerrados y evidencia conservada, sin recuperación.

Se corrige el contrato antes del escritor: rechazar rutas concretas también
prohibidas, deny universal y patrones idénticos. No se eliminan prohibiciones,
ni se exige resolver toda intersección de globs; exclusiones parciales válidas
se mantienen. Prompt/esquema aclarados, cinco regresiones nuevas. Originales
y catálogo congelado del ensayo previo no se modifican. El usuario pide
continuar el trabajo de cierre; nueva ejecución separada preparada en D070.

## D070 — Matriz corregida detenida por errores de conexión del planificador

Estado: ejecutada una vez y cerrada el 2026-10-14. Propuesta nueva (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_CORRECTED_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_CORRECTED_PROPOSAL.md`),
resultado/evidencias junto a D069. Solo planner Codex de Codex→Codex:
timeouts de modelos/routing/MCP y tres eventos error de reconexión. Después
JSON válido sin contradicción y turn.completed/exit 0, pero el adaptador
existente rechaza cualquier evento error. STOPPED planner/CLI failed, ningún
ejecutor/revisor/commit; no se ocultan errores porque después haya terminal.
No se atribuye a cuota/auth ni a incapacidad del escritor. Git/docs/muestras
globales intactos, owner cerrado, proceso/grupo muerto, cero locks y servicio
detenido con clave retirada. Otros pares vacíos, sin retry/fallback.

Se informa y pide autorización nueva para doce invocaciones como máximo en
otra matriz con parada al primer fallo. Usuario: «Autorizar una nueva matriz».
No cambia parser/permisos/modelos/auth para pasar; D071 queda separado.

## D071 — Comprobación funcional real de las cuatro combinaciones completada

Estado: completada el 2026-10-14. Propuesta autorizada (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_FINAL_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_FINAL_PROPOSAL.md`),
[resultado y límites](archive/phase-007/PROVIDER_MATRIX_CLI9_RUN.md),
[manifiesto](archive/phase-007/PROVIDER_MATRIX_CLI9_RESULT.json). Nueva área matrix-6,
mismo wheel corregido instalado offline, código contrastado byte a byte.
Codex 0.162.1 gpt-6-luna, Claude 2.1.296 claude-sonnet-4-6; planner/reviewer
medium y executor low. Doce COMPLETE, tres por combinación, sin retry/fallback
del harness. Autorización satisfecha y agotada, no habilita más consumo.

Codex→Codex, Claude→Claude, Claude→Codex y Codex→Claude COMMITTED con edición
real solo en src/estimate.ts. Plans tipados, tests/check/build y cuatro JUnit
de tres casos pasan, review ACCEPT y aceptación elegible por contenido exacto.
Commits 75bef356, 293643f2, 347f4a7d y 584ed7e0 respectivamente, autor Harness
Provider Matrix. El ejecutor escribe sin commit; el revisor acepta y el harness
realiza el commit mecánico. Docs de fixture intactos. Ocho jobs DONE/owners
cerrados, procesos/grupos muertos, cero locks y servicios/claves cerrados.

La supresión específica de confianza mantiene config global muestreada sin
cambios mientras Codex escribe. Controles D066 presentes en todos los roles;
muestras de archivos de memoria automática/config/settings/gitconfig intactas.
No se copian secretos/auth ni se restauran globales. No se afirma contención
OS, ausencia de logs/cachés/SQLite auxiliares/refresh, cuota/factura o retries
internos. D069/D070 originales conservados; ajustes de verificador no relanzan
recorridos. Memoria de proyecto sigue documental; SQLite autoridad operativa.

948 pytest + 121 subtests, 12 checks estándar, builds y wheel instalado
correctos. Siete regresiones nuevas, diff/hashes/SQL/Git revisados. Se cierra
la comprobación funcional de flujos de modelos, sin afirmar archivado ni
continuidad documental por fase implementados/probados. La organización
documental exigida por el usuario queda como tarea separada de NEXT_STEPS,
antes del alcance UI H6.2; no se inicia aquí. Sin tag/cierre de fases de ensayo,
push/publicación, nuevo smoke, recuperación o modificaciones de ReferenceProject.

## D072 — Organización documental por fase y estructura de producto

Estado: diseño completado el 2026-10-14; puntos confirmados por el usuario en D073;
H6.3 (D073), H6.4 (D074) y H6.5 (D075) implementados offline. La UI (H6.2) sigue pendiente.
[Diseño, diferencias e incrementos](archive/phase-007/DOCUMENT_ORGANIZATION.md).

Requisitos del usuario: creación desde un brief en Markdown seguida de una
conversación con el revisor, que genera SPECIFICATION, ARCHITECTURE (con
diagramas de datos si proceden), ROADMAP, STATE y NEXT_STEPS. El ROADMAP fija
las fases y NEXT_STEPS las tareas de la fase activa. `docs/archive/phase-N/`
guarda STATE y NEXT_STEPS de cada fase. El README lo lee el usuario. Los
documentos se ven y editan desde el editor y desde el sistema. La creación
termina al aceptar roadmap y documentación. Cada proyecto, fase y tarea tiene su
URL, con carga limitada. Hay chat global, sección de documentación, métricas por
tarea (agentes, tokens, turnos, modelo, esfuerzo), tests OK/KO y estadísticas
por proyecto y globales.

Contrato propuesto: SQLite manda en el estado operativo; Markdown, en la
intención; los bloques gestionados son proyecciones que se comparan con su
regeneración y nunca se vuelven a leer como fuente. Se añaden `decisions/` (un
archivo por decisión con índice gestionado) y, opcionales, `architecture/`
(Mermaid) y `research/`. No hay carpeta por tarea. El archivo de cada fase
contiene STATE, NEXT_STEPS, REVIEW y SUMMARY; `phase-000` contiene BRIEF y
DEFINITION. STATE separa la base acumulada (compactada en la reconciliación y
trasladada literal) de la fase activa, con presupuestos de tamaño que generan
avisos. Los ejecutores no editan STATE, NEXT_STEPS, ROADMAP, el índice ni el
archivo. Cada commit de tarea regenera los bloques por `MechanicalUpdate`.

Cierre D032 sin cambios. La operación nueva `phase_transition` archiva por bytes
el HEAD cerrado, abre STATE y NEXT_STEPS frescos e instancia la fase siguiente
desde ROADMAP en un único commit conciliable. Toda edición humana, desde la UI o
el editor, entra por un job `document_edit` con diff confirmado y CAS. Con
documentos sin confirmar se bloquean tarea, check, exportación y transición. La
creación v2 sustituye para proyectos nuevos la plantilla v1 y el descubrimiento
de un turno de D037: conversación `definition` y borradores en disco que el
agente nunca escribe. El chat añade comandos deterministas con las mismas
confirmaciones.

Métricas: tabla `attempt_metrics` materializada al terminar cada intento, con
procedencia por campo y relleno idempotente. No se suman acumulados con
incrementales y no se deduce cuota. Hay que capturar `num_turns`, que hoy no se
guarda, y caracterizar el catálogo con los streams de D071.

Incrementos propuestos: H6.3 contrato documental y transición, H6.4 métricas,
H6.5 creación y planificación conversacionales, y H6.2 UI ampliada al final.
Puntos a confirmar: carpetas, contenido del archivo, autoría de STATE,
borradores en disco, chat sin lock (cambia D035), orden e idioma. No se ha tocado
código, esquema, API ni UI. ReferenceProject se leyó sin modificarlo y sin consumir
proveedores.

## D073 — Confirmación de D072 e implementación de H6.3

Estado: decidido por el usuario el 2026-10-14 e **implementado y verificado offline**
el mismo día. [Entrega, API y límites](archive/phase-007/H6.3_DOCUMENT_CONTRACT.md).

Confirmaciones del usuario sobre D072 §12, aceptando las recomendaciones:

1. `decisions/`, `architecture/` y `research/` se crean desde el principio; el agente
   decide si las usa. Ninguna carpeta por tarea.
2. Archivo por fase con STATE, NEXT_STEPS, REVIEW y SUMMARY; `phase-000` con BRIEF y
   DEFINITION.
3. Los ejecutores no editan STATE, NEXT_STEPS ni ROADMAP; el progreso es mecánico y la
   prosa se escribe en la reconciliación.
4. Borradores de creación en la carpeta destino antes del commit raíz (H6.5).
5. Turnos de chat sobre una instantánea de HEAD, sin esperar al lock (cambia D035; no
   implementado).
6. Orden H6.3 → H6.4 → H6.5 → H6.2. La UI es una tarea completamente distinta, con su
   plugin de diseño.
7. Plantillas en español con alias en inglés en el parser.

H6.3 se activa por proyecto (`documents = "v2"`); sin esa clave nada cambia y los
snapshots anteriores conservan su forma. Decisiones de implementación tomadas con
criterio:

- Los documentos de fase son ROADMAP, DECISIONS, STATE y NEXT_STEPS. README,
  SPECIFICATION y ARCHITECTURE no se ligan a READY para no exigir una adopción manual
  tras cada tarea; la reconciliación v2 puede editarlos.
- Los bloques pasan a Markdown legible con escape en línea; `managed-state` conserva los
  marcadores de D036. La exportación D036 en v2 usa el mismo render.
- Los contratos v2 añaden prohibiciones (archivo siempre; documentos del harness salvo en
  `<fase>-RECONCILE-<n>`); nunca se retira una prohibición.
- Cada commit de tarea regenera los bloques y adopta, en la transacción del resultado,
  solo los de documentos no revisados cuya base coincidía con la revisión base.
- La transición es una operación posterior al cierre (D032 intacto). Archiva por bytes,
  abre documentos frescos y crea la fase siguiente en un único commit conciliable. El plan
  de la fase siguiente lo aporta quien la confirma (H6.5 lo propondrá).
- La edición confirmada se rechaza con trabajo pendiente en el checkout, en lugar de
  esperar su turno. Con documentos sin confirmar no arranca ninguna tarea v2.
- Los avisos de presupuesto se muestran sin afectar al check.

No se añaden migración ni codec: las operaciones nuevas usan `phase_operations`, runs y
jobs existentes (`purpose` `document_edit` y `phase_transition`). No hay cambios de UI,
dependencias ni proveedores. Siguiente: H6.4 (métricas), sin iniciar.

## D074 — Métricas por intento materializadas con procedencia y agregados sin doble conteo (H6.4)

Estado: implementado y verificado offline el 2026-10-14. [Catálogo, entrega y límites](archive/phase-007/H6.4_METRICS.md),
[caracterización reproducible](archive/phase-007/H6.4_STREAM_CATALOG.py) y [su salida](archive/phase-007/H6.4_STREAM_CATALOG.json).
H6.3 (D072/D073), que estaba sin commit en el árbol, se commiteó por separado antes de empezar.

Caracterización offline de los doce stdout conservados de D071, leídos sin modificarlos y verificados por
SHA-256 contra su captura sellada; solo se publican nombres de campo, tipos y comprobaciones. En Claude el
`usage` del `result` es exactamente la suma por mensaje de `message_start` + `message_delta`; los eventos
`assistant` repiten el mismo mensaje con una salida parcial y no sirven para contar; `modelUsage` suma el
total; el razonamiento es parte de la salida. Codex emite un único `turn.completed` cuyo uso incluye la caché
leída (caché ≤ entrada en las seis muestras) y no informa modelo, esfuerzo, coste, duración ni turnos.
`rate_limit_event` y el recuento estimado de razonamiento no entran en el catálogo: la cuota no se deduce.

Decisiones tomadas con criterio:

- Catálogo `metrics-1` con procedencia por campo (`requested`, `reported`, `derived`, `measured`, `absent`).
  Null nunca es cero. Turnos: `num_turns` reportado en Claude; en Codex, elementos completados únicos,
  marcados como derivados y nunca sumados con los reportados.
- Contabilidad única por intento: el total del terminal; sin terminal, en Claude, el uso por mensaje
  deduplicado (`messages`, derivado y parcial). Dos terminales cuentan el último. Los agregados no suman la
  entrada cruda (semántica distinta por proveedor) sino la entrada sin caché derivada; un total de Codex con
  escritura de caché distinta de cero queda ausente.
- Captura `terminal-2`: el mismo acumulador lee el stream y sella `num_turns`, `duration_api_ms` y los
  contadores derivados en los metadatos del intento. Sin cambios de argv ni de versión de adaptador
  (`cli-9`): los jobs congelados no se ponen en cuarentena.
- Migración `0014_attempt_metrics` (`attempt_metrics`, `attempt_model_metrics`). La fila se inserta en la
  transacción que registra el resultado o la interrupción del intento; no se reescribe y sobrevive a la
  retención H5.3. Downgrade permitido salvo con filas rellenadas desde un stream verificado.
- Relleno explícito e idempotente (`harness-local metrics-backfill`), no automático al arrancar. Usa
  `result_json` y, bajo raíces autorizadas, el stdout sellado verificado por tamaño y SHA-256 que no tenga
  purga autorizada ni pendiente. Solo completa lo que el sello no tenía.
- Agregados de solo lectura en `/api/managed/metrics/*`: resumen, intentos, grupos (rol, proveedor,
  modelo/esfuerzo solicitados, día, fase, tarea…; favoritos por frecuencia o tokens y rol), modelos
  reportados y tareas (agentes, correcciones, aceptación a la primera, tiempos, tests OK/KO, paradas,
  consumo con fallos). Global sin proyecto; fase y tarea exigen proyecto.
- El SUMMARY de las fases archivadas añade tokens y turnos por tarea y una tabla de consumo por rol, sin el
  chat y con la cobertura de cada suma. Una transición revisada antes de migrar se ejecuta tal como se
  revisó.

Sin UI, proveedores, CLI reales ni cambios de dependencias. Siguiente: H6.5 (creación y planificación
conversacionales), sin iniciar.

## D075 — Creación y planificación conversacionales con borradores en disco y CAS (H6.5)

Estado: implementado y verificado offline el 2026-10-14.
[Entrega, API y límites](archive/phase-007/H6.5_CONVERSATIONAL_CREATION.md).

Base: D072 §5.1 y §11, D073 puntos 4 y 7. Dos conversaciones sobre la infraestructura del chat (D035):
`definition` (proyecto v2 nuevo desde un brief Markdown) y `phase_planning` (plan NEXT_STEPS de la fase
siguiente). Solo con `documents = "v2"`; la definición exige además `bootstrap_enabled` y el escritor Git,
como D037. Sin v2 nada cambia. Decisiones tomadas con criterio:

- Autoridad propia en `0015_planning` (`planning_conversations`, `planning_turns`, `planning_proposals`) en
  lugar de ampliar las tablas del chat: el chat contextual no lista estas conversaciones y su contrato no
  cambia. Se reutilizan cola, lock, supervisor, guardia de modo, cuarentena, journal de intentos y la regla de
  un turno pendiente. Runs `definition`/`phase_planning`, acción `planning_turn`, sin codec nuevo.
- Turnos nuevos, de solo lectura, del revisor (roles aditivos `definition` y `planning` en `cli-9`, sin cambiar
  argv de los roles anteriores), con plantillas versionadas `define-project` y `plan-phase` y esquemas fijos.
  Salida inválida o ruta no admitida → turno FAILED sin fallback ni reintento; caída → UNKNOWN.
- El agente nunca escribe. Lo observado del destino se compara antes (definición: con lo congelado; si ya
  cambió, no se invoca) y después de invocar; cualquier cambio descarta la respuesta y conserva los bytes.
- Aplicar un borrador exige confirmación y el hash mostrado, y escribe con CAS sobre el hash que leyó el turno
  (temporal propio + `os.replace`, segunda comprobación justo antes). La API de edición usa la misma CAS. Las
  ediciones del usuario se detectan por hash frente al último turno **respondido** o a la última propuesta
  aplicada: un turno fallido no las oculta al siguiente. Con turno pendiente no se aplica, edita ni acepta.
- Rutas admitidas: plantilla v2, `decisions/*.md` y `architecture/*.md` de un nivel. `research/` solo con su
  README, según el diseño. Lo demás (también ocultos, carpetas y enlaces) es ajeno y bloquea la aceptación.
- Las preguntas bloqueantes se resuelven en un turno o se aplazan explícitamente con motivo; los pendientes del
  revisor son avisos, no bloqueos.
- La aceptación es la vista previa del bootstrap D037 con plantilla v2: regenera los bloques de STATE,
  NEXT_STEPS, ROADMAP y DECISIONS para P001 ACTIVE, completa los README de carpeta y añade
  `archive/phase-000/{BRIEF,DEFINITION}.md`. Como los bloques cambian los bytes de cuatro borradores, el
  adaptador D037 se generaliza solo para documentos con `before_sha256`: acepta el borrador revisado o los
  bytes sellados y los sustituye con CAS. La intención, el commit raíz y la recuperación son los de D037. La
  fase adopta solo sus documentos de fase. El modo de planificación decide si la primera tarea debe ser
  determinista.
- Para no cambiar el tipo que consume la UI v1, `GET …/bootstrap` expone la operación v2 en
  `definition_operation`. En un proyecto v2 el bootstrap v1 y su descubrimiento se rechazan.
- La transición acepta `plan_proposal` (referencia exacta con hash) en lugar de `next_steps`; `plan_origin`
  entra en el hash revisado solo cuando existe, y la propuesta pasa a ACCEPTED en la transacción que encola la
  transición. El SUMMARY de fase excluye estas conversaciones, como el chat.

Sin UI, proveedores, CLI reales ni dependencias nuevas. El TOML local no expone todavía `bootstrap_enabled`.
Siguiente: H6.2 (UI de producto), tarea completamente distinta (D073), sin iniciar.

## D076 — Alcance de H6.2: registro híbrido, Markdown seguro, chat sin lock y entregas

Estado: decidido por el usuario el 2026-10-14; **no implementado**.
[Alcance, entregas y criterios](archive/phase-007/NEXT_STEPS.md).

Decisiones del usuario, todas por la opción recomendada:

1. **Registro de proyectos híbrido (concreta D054).** El TOML del operador sigue siendo la autoridad de
   agentes, Git, ejecutables y entornos, y agrupa los comandos en composiciones con nombre
   (`local-config-3`, con `bootstrap_enabled` y raíces autorizadas para el registro). La UI registra
   proyectos en SQLite, versionados y auditados: raíz canónica, confianza explícita, perfil, `documents`,
   bootstrap, política y composición elegida. Nada ejecutable se concede por HTTP. Los `[[projects]]` del
   TOML siguen siendo válidos y no se editan desde la UI.
2. **`markdown-it` (`html: false`) y Mermaid (`securityLevel: "strict"`) con carga diferida**, con versiones
   fijadas, como únicas dependencias nuevas del cliente.
3. **El chat global entra en H6.2 en una entrega propia.** Primero el backend de turnos sobre una
   instantánea de solo lectura del HEAD, sin lock (D073 punto 5; cambia D035 al implementarse), y los
   comandos deterministas de D072 §8. Después la UI.
4. **Enrutador mínimo propio sobre History API y CSS propio con tokens** y modo oscuro, sin dependencias.
   Fallback a `index.html` solo fuera de `/api/`.

Entregas en orden, cada una como tarea aparte: E1 shell y sistema de diseño, E2 registro, E3 documentación,
E4 creación y planificación, E5 chat global y E6 estadísticas. La legacy H1 se conserva en `/legacy` y las
simulaciones H0.3 salen de la navegación. Fuera de alcance: proveedores reales, `project.yaml`, multiusuario,
edición del TOML desde la UI e historial Git de documentos. Siguiente: E1, sin iniciar.

## D077 — H6.2 E1: shell por URL, lecturas por código y sistema de diseño

Estado: implementado y verificado offline el 2026-10-14. [Entrega, diseño y límites](archive/phase-007/H6.2_E1_SHELL.md).

Decisiones tomadas con criterio dentro de D076:

- El servidor del wheel entrega `index.html` solo en `GET`/`HEAD` fuera de `/api/` y nunca en lugar de un asset
  estático. Los 404 de la API no cambian.
- Las URLs usan códigos. El servidor añade lecturas por código de fase y un resumen de tareas por fase que también
  funciona sin fase definida (runs v1 o demo), en lugar de traer listas completas al cliente.
- `/runs/:id` es un enlace corto que se sustituye por la URL canónica; una URL con otra fase o tarea se corrige igual.
- El envío idempotente y el pendiente (H2) pasan a un espacio de acciones por proyecto compartido entre páginas.
  Solo las acciones que crean un run navegan a él.
- Identidad visual: papel verde-gris, cobalto para acciones, códigos en monoespaciada como titulares y el raíl del
  ciclo de vida de la fase como elemento distintivo. El ámbar se reserva a lo que espera una decisión ahora.
  Fuentes del sistema, sin dependencias.
- No se cambia la guardia H5.6. Que rechace la carga de la página con `Sec-Fetch-Site: cross-site` queda como
  hallazgo para el usuario.

Sin migración, codec ni dependencias. Siguiente: E2 (registro de proyectos), sin iniciar.

## D078 — H6.2 E2: `local-config-3` y registro de proyectos desde la UI

Estado: implementado y verificado offline el 2026-10-14. [Entrega, API y límites](archive/phase-007/H6.2_E2_REGISTRY.md).

Decisiones tomadas con criterio dentro de D054/D076:

- `[registration]` lleva `roots` y `bootstrap_enabled`, que es un techo: la UI solo activa bootstrap en un proyecto
  registrado si el operador lo autoriza. Las composiciones fijan el perfil; el proyecto (del TOML o registrado) solo
  nombra una. `[[projects]]` pasa a ser opcional en `local-config-3`.
- `local-config-1` y `-2` conservan su hash congelado y no admiten registro. Las filas registradas que no componen con
  el TOML actual quedan no disponibles con su motivo; el servicio arranca igual.
- La confirmación se liga a `preview_sha256` (acción, versión esperada, filas antes y después y versiones congeladas,
  que incluyen la composición). La confianza se confirma aparte con la raíz canónica exacta. Repetir una confirmación
  aplicada devuelve el resultado sin otra versión.
- La raíz no cambia tras el alta. Raíces iguales o anidadas con otro proyecto se rechazan, igual que las que contienen
  el estado del servicio o tienen un enlace en cualquier componente. El id `new` queda reservado por `/projects/new`.
- Baja lógica: el id queda reservado y su historial se conserva; la raíz queda libre para otro id, que hereda la
  lectura de los runs de ese checkout.
- La versión y el hash de la fila del registro entran en `local_config_sha256` y en `project_registry`. Cambio o baja
  con trabajos sin terminar se rechazan en la transacción; el resto lo cubre la cuarentena existente.
- «Quién» es `actor()`, la identidad del servicio, como en las demás auditorías: la sesión local no identifica
  personas.

Migración `0016_project_registry`; sin codec ni dependencias. Siguiente: E3 (documentación), sin iniciar.


## D079 — Guardia H5.6 sin cambios ante navegaciones cross-site (hallazgo de E1)

Estado: decidido por el usuario el 2026-10-15.

La guardia de sesión (D044) sigue rechazando con `origin_rejected` toda petición con `Sec-Fetch-Site: cross-site`,
también la carga de la propia página fuera de `/api/`. Un enlace al harness pulsado desde otro sitio (correo, chat)
no abre la URL. Escribirla, usar un marcador o recargar siguen funcionando. Se descarta por ahora admitir
navegaciones `GET` de documento; puede reconsiderarse con una decisión nueva. Sin cambios de código.

## D080 — H6.2 E3: visor y edición de documentos con CAS, regeneración de bloques y Markdown aislado

Estado: implementado y verificado offline el 2026-10-15. [Entrega, verificación y límites](archive/phase-007/H6.2_E3_DOCS.md).

Decisiones tomadas con criterio dentro de D072 §6 y D076:

- Versiones: `markdown-it@15.0.2` y `mermaid@11.17.2`, instaladas con `--before` dos semanas antes para que las
  transitivas cumplan la misma regla. Se descarta Mermaid 12 (primera versión mayor y publicaciones recientes); sus
  dos avisos *low* de KaTeX quedan anotados.
- La URL usa la ruta del documento en el checkout (`/projects/p/docs/docs/STATE.md`): exacta y sin ambigüedad entre
  el README de la raíz y los de las carpetas.
- El hash base es un campo opcional de cada cambio (`base_sha256`; `null` = no debe existir), comprobado en la vista
  previa con el código `document_changed`. Sin el campo, el contrato H6.3 no cambia.
- «Regenerar» (D072 §6) es una variante explícita de la edición `worktree`: conserva la prosa local, devuelve cada
  bloque gestionado a los bytes de la base y muestra lo que se descarta. El escritor admite esos bytes locales exactos
  además de los de la base; la adopción sigue ligada al hash de la base. No se regenera con marcadores rotos.
- Mermaid se dibuja con `securityLevel: "strict"` y el SVG resultante se muestra como `<img>` desde un Blob, de modo que
  el diagrama no puede ejecutar nada aunque la sanitización de Mermaid fallara. Las imágenes del checkout salen por
  la API con CSP `sandbox`; las externas no se cargan.
- La página de documentación se carga de forma diferida (chunk propio) para no engordar el bundle principal.
- `usePoll` conserva la última lectura al releer el mismo recurso: releer tras una acción ya no desmonta la página.

Sin migración ni codec. Siguiente: E4 (creación y planificación de fase), sin iniciar.

## D081 — Rutas protegidas del perfil: límite del ejecutor, no de las escrituras documentales confirmadas (v2)

Estado: decidido por el usuario el 2026-10-15 (opción recomendada); implementado y verificado offline.
[Hallazgo y verificación](archive/phase-007/H6.2_E4_SETUP.md#hallazgo-resuelto-antes-de-seguir-d081).

Hallazgo de E4: `typescript-web`, único perfil de las composiciones de `local-config-3`, protege `docs/**`, y la
exportación (D036), la edición y la transición (H6.3) y la aceptación de la definición (H6.5) rechazaban cualquier ruta
protegida. Un proyecto registrado con `documents = "v2"` no podía crearse, editarse ni pasar de fase, y D072 pedía
proteger `docs/archive/**`, que la transición escribe.

- En v2, las rutas protegidas del perfil siguen limitando al ejecutor (`check_paths`, `forbidden_paths` del contrato),
  a los permisos concedibles y a la tarea de reconciliación con agente.
- Las escrituras del harness confirmadas por el usuario sobre el contenido exacto del contrato documental (README,
  Markdown editable de la documentación y Markdown del archivo de fases) no se rechazan por el perfil: el contrato tiene
  sus propias reglas (rutas editables, archivo de solo lectura para ediciones, bloques gestionados, CAS). Es el criterio
  que ya seguía la regeneración mecánica de bloques en cada commit de tarea.
- Fuera del contrato y en v1 la protección del perfil no cambia. Un solo punto: `documents.protected_write`.

Sin cambios en los perfiles, el esquema ni el codec.

## D082 — H6.2 E4: creación y planificación de fase en la UI

Estado: implementado y verificado offline el 2026-10-15. [Entrega, verificación y límites](archive/phase-007/H6.2_E4_SETUP.md).

Decisiones tomadas con criterio dentro de D075/D076:

- Rutas `/projects/:p/setup[/*ruta]` (la ruta es la del borrador en la carpeta, como en E3) y
  `/projects/:p/phases/:code/plan[/:conversación]`. La transición vive en la página de la fase terminada, donde se
  elige el plan: un plan propuesto, texto propio o ninguno.
- Lectura nueva `GET …/planning/{c}/drafts/content` por la misma inspección que el turno y la CAS, en lugar de reutilizar
  la lectura de documentos (que no conoce borradores inválidos ni la base de la CAS).
- Se reutilizan el visor de Markdown, el diff coloreado y el seguimiento del run de E3. El editor de borradores es de
  texto completo (los bloques se regeneran al aceptar) y guarda por `PUT …/drafts` con el hash con que se abrió; antes de
  guardar relee el disco y avisa. Sin dependencias: un diff por líneas propio (`diff.ts`) que solo muestra.
- Cada confirmación va ligada a su hash (propuesta, base del borrador, vista previa de la aceptación o de la transición) y
  a la versión de la conversación o de la fase; mensajes, aceptación y transición usan clave idempotente y el envío
  pendiente de H2. Las vistas previas se descartan si cambia la versión o los bytes en disco.
- En proyectos v2 el resumen sustituye el formulario v1 de bootstrap por el acceso a la creación, y el alta v2 con
  bootstrap lleva a `/setup`.

Sin migración, codec ni dependencias. Siguiente: E5 (chat global), sin iniciar.

## D083 — H6.2 E5: chat sobre HEAD, carril independiente y comandos deterministas

Estado: implementado y verificado offline el 2026-10-15. [Entrega, verificación y límites](archive/phase-007/H6.2_E5_CHAT.md).

Cambio deliberado de D035 previsto por D073/D076:

- Las preguntas nuevas congelan HEAD y consultan un árbol exportado de solo lectura, con evidencia antes/después,
  sin lock del checkout. El servicio tiene un carril escritor y uno de chat; las propuestas aceptadas siguen creando
  tareas normales. Jobs `chat_turn` anteriores conservan sus reglas; nuevos `chat_snapshot` identifican la variante.
- Exportación acotada sin `.git`, symlinks ni submódulos, en carpeta privada junto a SQLite. Intención persistida antes
  de crearla, limpieza al finalizar o al confirmar procesos detenidos tras caída; nunca se registra un worktree.
  Los permisos son cooperativos, no aislamiento OS. Sin HEAD, objetos ausentes o exceso de tamaño se falla sin fallback.
- Los comandos slash usan una gramática cerrada y un preview sin efectos. La UI reutiliza los controles de fase y
  sus confirmaciones/CAS; `/tarea` genera una propuesta literal sin agente y requiere la aceptación normal por hash
  y versión. Comandos inválidos nunca se envían al modelo. `/check` solo usa revisor tras pulsar el control normal.
- Contexto opcional de tarea por run (evidencia observada, no conversación reanudada), compatible con fase;
  `0017_chat_context` añade una referencia nullable. No cambia el codec ni se añaden dependencias.
- Codex recibe `--skip-git-repo-check` solo al consultar una exportación; opción acreditada por fuente del pin y
  prueba de argv, conservando lectura y memoria de `cli-9`. No se ejecutaron proveedores reales.

Siguiente: E6 (estadísticas y tests), sin iniciar. Los consentimientos previos siguen agotados.

## D084 — H6.2 E6: estadísticas por URL, evolución de tests por fase y gráficos SVG propios

Estado: implementado y verificado offline el 2026-10-15. [Entrega, verificación y límites](archive/phase-007/H6.2_E6_STATS.md).

Decisiones tomadas con criterio dentro de D074/D076:

- Lectura nueva `GET /metrics/validations` (por fase, tarea o raíz): cuenta cada ciclo de validación, revalidaciones
  incluidas, con OK/KO, comandos y casos JUnit. Los ciclos no guardan su hora (`source_attempt_id` solo existe con
  JUnit), así que **no se agrupa por día**: la evolución de los tests se lee por fase. Añadir la hora al ciclo cambiaría
  el formato del historial y queda para una decisión aparte.
- `order=key` en los grupos de consumo para la serie por día; ninguna otra lectura nueva. El resumen de un proyecto no
  trae tareas: cada panel lee su recurso y las listas van paginadas.
- Rutas `/stats` y `/projects/:p/stats` en un chunk diferido; panel de métricas en la página de la tarea. La vista global
  agrupa por proyecto (raíz) donde la del proyecto agrupa por fase.
- Null es «sin dato» también en los gráficos (marca propia, nunca longitud cero); una suma parcial lleva su cobertura;
  turnos reportados y derivados nunca se suman; el coste es «equivalente API».
- Gráficos SVG propios, sin dependencias. OK/KO no usan el verde/rojo de estado, que falla la separación para
  daltonismo, sino tokens `--chart-ok`/`--chart-ko` validados en claro y oscuro, con leyenda y tabla equivalente.

Sin migración, codec ni dependencias. Las seis entregas de H6.2 están completas; siguiente: revisión de los criterios
del hito, sin iniciar. Los consentimientos previos siguen agotados.


## D085 — Revisión de cierre de H6.2: criterios cumplidos salvo la paginación de diffs

Estado: revisión completada el 2026-10-15 sobre `b04ed5d`; **el hito queda pendiente de la decisión del usuario sobre
el hallazgo 1**. [Dictamen, evidencia y hallazgos](archive/phase-007/REVIEW.md).

- Cumplidos con evidencia de esta sesión: recorrido sintético completo desde la UI (alta → creación → primera tarea →
  revisión → commit → cierre → transición con plan propuesto, más chat y estadísticas), URLs por carga directa y recarga
  en `scripts/dev` y desde el wheel instalado en un venv propio, reintentos sin efectos repetidos, Markdown hostil
  inerte, QA en claro, oscuro y 386 px, y checks en verde.
- Parcial: «diffs paginados». `GET /runs/{id}` incluye el diff completo de cada ciclo y la página del run lo relee cada
  1,5 s, también en runs terminales. Corregirlo cambia el contrato de la API y el cliente: no es un defecto acotado de
  la revisión. Se propone como tarea correctiva, sin iniciar.
- Hallazgos menores anotados, sin corregir: crear conversaciones de chat o de planificación de fase no es idempotente
  (una conversación vacía de más tras un reintento); deriva en ámbar y exportación habilitada en una fase cerrada y ya
  transicionada.
- Método: con el servidor del wheel, el iframe no sirve (`X-Frame-Options: DENY`) y la navegación de la extensión llega
  como `cross-site` (D079); las cargas se hicieron como documentos completos del mismo origen.

Sin cambios de código, esquema, API, UI ni dependencias. Los consentimientos previos siguen agotados.

## D086 — Hallazgos de D085 corregidos: diffs paginados, conversaciones idempotentes y fase con sucesora

Estado: implementado y verificado offline el 2026-10-15 sobre `22d592f`; **los siete criterios de H6.2 quedan
cumplidos**. [Entrega, verificación y límites](archive/phase-007/H6.2_DIFF_PAGINATION.md).

Pedido por el usuario: el hallazgo 1 (obligatorio) y también el 2 y el 3. Decisiones tomadas con criterio:

- La lectura del run lleva de cada ciclo solo `diff_sha256` y `diff_bytes`, también en su evidencia validada y en la de
  los casos JUnit. El diff se lee en `GET /runs/{id}/cycles/{n}/diff` por páginas de bytes UTF-8 terminadas en fin de
  línea (4–512 KiB, 64 KiB por defecto), con cursor exacto y `sha256` opcional (409 si no coincide). El hash es el del
  texto almacenado. El historial, los agentes y el resto de diffs (documentos, exportación, transición) no cambian.
- `/runs/{id}/jobs` paginado, del más reciente al más antiguo. `ManagedRunRead.active_job` dice si el run avanza solo:
  la UI sondea cada 1,5 s con job y cada 15 s sin él, y pide el diff al abrirlo, página a página, sin repintarlo con el
  sondeo.
- Crear conversaciones de chat o de planificación exige `Idempotency-Key`; misma clave y petición devuelven la misma
  conversación, y la clave se resuelve antes de reevaluar el destino. Migración `0018_conversation_keys` (columnas
  nullable; las conversaciones anteriores no tienen clave). El cliente conserva la clave hasta la respuesta.
- `PhaseRead.successor` (código de la fase posterior, null en la última). Con sucesora, la deriva es una nota neutra,
  sin adopción ni exportación habilitada: el ámbar queda para lo que espera una decisión.

Cambio de contrato deliberado: `CycleRead.diff` desaparece y `/jobs` devuelve una página; se actualizaron los
consumidores del repositorio (UI, pruebas, `check_distribution.py`, `examples/provider_matrix/drive.py`, que ahora
guarda los diffs por páginas). Sin codec ni dependencias nuevas. El cierre formal del hito queda a decisión del usuario.
Los consentimientos previos siguen agotados.

## D087 — H6.2 y el Hito 6 cerrados por decisión del usuario

Estado: decidido por el usuario el 2026-10-15, tras D086 (`01b4f6d`).

- H6.2 queda cerrado: los siete criterios de D076 están cumplidos (D085 + D086). Con él se cierra el Hito 6
  (H6.1–H6.5); el backlog no tiene más hitos definidos.
- Los límites abiertos no bloquean el cierre y se conservan como candidatos, sin iniciar: `package.json` de un proyecto
  `typescript-web` nuevo, hora de las validaciones, decodificación completa del historial por lectura, avisos *low* de
  KaTeX y ningún recorrido de producto con CLI reales.
- La siguiente tarea la elige el usuario. Los consentimientos previos siguen agotados.

## D088 — Contrato documental unificado, cierre de fase automático e importación de proyectos (P008)

Estado: decidido por el usuario el 2026-10-15 tras el análisis de incongruencias de esa sesión; **P008-T001
(migración documental de este repositorio) implementada el mismo día**; P008-T002 implementada (D089); P008-T003
implementada (D090); P008-T004 implementada (D091); P008-T005 implementada (D092); P008-T006 implementada (D093);
P008-T007 implementada (D094); P008-T008 implementada (D095); P008-T009 implementada (D096);
P008-T010 implementada (D097); P008-T011 implementada (D098); P008-T012–T015 pendientes. Fase: P008.
Sustituye en parte D072/D073 (carpetas `decisions/`, `architecture/` y `research/`; layout v2 opcional), D032/D073
(cierre y transición separados) y D037 (creación v1). Plan: [NEXT_STEPS](NEXT_STEPS.md).

Decisiones del usuario:

1. **Estructura obligatoria** para todo proyecto gestionado y para este repositorio. Raíz: `AGENTS.md` canónico
   (≤60 líneas: orden de discovery, reglas inquebrantables, comandos de test y lint), `CLAUDE.md` y `GEMINI.md` como
   envoltorios de ≤15 líneas que importan `AGENTS.md` (GEMINI se genera ya, sin proveedor todavía), y `README.md`
   reducido para personas. `docs/`: SPECIFICATION, ARCHITECTURE, ROADMAP, STATE, NEXT_STEPS, DECISIONS,
   DDBB-DIAGRAM (Mermaid `erDiagram`, o «Sin persistencia»), `flows/`, `phase/` y `archive/phase-NNN/`.
2. **`DECISIONS.md` único** con índice; desaparecen `decisions/DNNN-*.md` y el presupuesto de 8 KiB. Los agentes
   leen solo las ADR citadas por la tarea, o el índice para buscar precedentes. Añaden ADR la reconciliación, el
   usuario y el revisor mediante propuestas aprobadas; el ejecutor las propone en su salida.
3. **Archivo `phase-NNN`** con tres dígitos, como los códigos `PNNN`.
4. **Cierre unificado.** Tras el check READY y la autorización de cierre, un único flujo y commit conciliable: tag
   sobre el HEAD evaluado; `docs/archive/phase-NNN/` con STATE, NEXT_STEPS, REVIEW, SUMMARY y el contenido de
   `docs/phase/`; STATE con la base acumulada compacta (≤12 KiB) y la fase N+1; NEXT_STEPS con el objetivo de N+1
   tomado de ROADMAP, sin exigir su plan (se planifica después); `docs/phase/` vacía; ROADMAP con N completada y
   enlace a su archivo.
5. **`docs/phase/`** sustituye a `research/` como carpeta de trabajo efímera de la fase en curso.
6. **Paridad diagramas‑código.** Perfiles, `protected_write` y `allowed_draft` permiten al ejecutor `docs/flows/**`,
   `docs/DDBB-DIAGRAM.md`, `docs/ARCHITECTURE.md`, `docs/SPECIFICATION.md` y `docs/phase/**` cuando su contrato lo
   incluya; STATE, NEXT_STEPS, ROADMAP, DECISIONS y `docs/archive/**` quedan para el harness. El revisor rechaza
   cualquier cambio de modelos de datos o de flujos de negocio sin su diagrama actualizado.
7. **v2 se modifica en su sitio** para adoptar esta estructura y pasa a ser obligatorio: no hay proyectos v2 reales
   que conservar. Se retira la creación v1 (H4.2); el lector legacy y v1 quedan solo como entrada del Flujo A.
8. **Archivos de instrucciones.** El harness puede crear y actualizar AGENTS, CLAUDE y GEMINI en la creación y la
   importación. Como Claude se lanza con `--setting-sources ""` y Codex con `--ignore-rules`, `AGENTS.md` se inyecta
   en el contexto congelado de cada intento (o se ajustan los flags solo si se verifica que es seguro).
9. **`architecture/` y `research/`** salen del layout.
10. **Flujo A** (harness anterior) acepta repositorios tipo ReferenceProject y proyectos v1/v2 de este harness, con una
    normalización común.
11. **Perfiles declarativos en el TOML local** (preparación, tests, lint y tipos detectados y confirmados por el
    usuario), para el Flujo B y para proyectos nuevos de otros stacks; el primero, Python/Django con pytest, ruff y
    mypy, que el usuario usará en su próximo proyecto.
12. **Este repositorio.** Los hitos H0–H6 pasan a ser P001–P007 y la definición inicial, P000; este trabajo es P008.
    Sin bloques gestionados por ahora, pero con el formato del parser para poder registrarlo más adelante. Se borran
    los `*_SCOPE.md` (fusionados), las propuestas ya ejecutadas y `docs/discovery/`.

Implementación de T001, sin cambios del motor:

- `docs/discovery/` (131 archivos) se reparte en `docs/archive/phase-001…007/` con `git mv`: 71 Markdown y los 19
  JSON y scripts de evidencia; 01, 02, 03 y START_HERE van a `phase-000/`; las revisiones de cierre de H5 y H6.2 pasan
  a `REVIEW.md` de su fase. Los 31 `*_SCOPE.md` se fusionan con la sección del backlog en el `NEXT_STEPS.md` de su fase y
  el `STATE.md` acumulado se reparte entre los `STATE.md` archivados, sin perder líneas. Se eliminan 9 propuestas ya
  ejecutadas; sus enlaces pasan a texto con la orden `git show 8622a43:<ruta>`.
- `baseline.json` pasa a `tests/fixtures/legacy/` (único cambio de código: la ruta en `tests/test_legacy_fixtures.py`;
  además se actualizan dos docstrings que citaban la ruta antigua).
- Enlaces relativos reescritos por script y comprobados; 14 enlaces que ya estaban rotos en los alcances quedan
  corregidos. `DDBB-DIAGRAM.md` se genera desde el metadata SQLAlchemy y los 16 diagramas Mermaid se validan con el
  parser de `mermaid` 11.17.2 del frontend, sin red.
- Documentos activos nuevos: SPECIFICATION, ARCHITECTURE, ROADMAP, STATE, NEXT_STEPS, DDBB-DIAGRAM, seis flujos y
  `SUMMARY.md` por fase archivada; AGENTS, CLAUDE y README reducidos y GEMINI añadido.

Consecuencias: hasta T002 el motor sigue implementando el layout v2 de D072/D073; este repositorio no está registrado
como proyecto gestionado, así que la diferencia no afecta a su desarrollo manual. Los consentimientos de proveedores
siguen agotados.

## D089 — P008-T002: layout unificado obligatorio y plantilla

Estado: implementada y verificada offline el 2026-10-15. Fase: P008. Aplica D088 puntos 1, 2, 5, 7 y 9; sustituye en
parte D073 (carpetas `decisions/`, `architecture/` y `research/`; `documents = "v2"` opcional) y D037/H4.2 (creación
v1).

Implementado:

- `Layout` (D088 punto 7, v2 modificado en su sitio): añade `AGENTS.md`, `CLAUDE.md` y `GEMINI.md` en la raíz,
  `docs/DDBB-DIAGRAM.md` (documento de producto) y las carpetas `flows/` y `phase/`; retira `decisions/`,
  `architecture/` y `research/`. `archive(code)` conserva `phase-NNN`.
- `skeleton()` genera exactamente AGENTS, CLAUDE, GEMINI, README, SPECIFICATION, ARCHITECTURE, ROADMAP, STATE,
  NEXT_STEPS, DECISIONS y DDBB-DIAGRAM («Sin persistencia»); `flows/` y `phase/` sin plantilla. AGENTS (≤60 líneas)
  lleva discovery, reglas inquebrantables y los comandos de preparación y validación del perfil (como mucho 12 por
  grupo; un argv con tres acentos graves no se transcribe); CLAUDE y GEMINI (≤15) importan `@AGENTS.md`. Los límites
  se comprueban por test. La plantilla de la definición pasa a la versión 3.
- `DECISIONS.md` único: el bloque `managed-decisions` indexa los encabezados `## DNNN — título` del propio archivo
  (id, título y la primera línea `Estado:`, en negrita o no), sin leer el bloque. Una numeración repetida, también
  con otro relleno de ceros, se rechaza en la regeneración del commit de tarea, en la edición confirmada, en la
  transición y como bloqueo de la aceptación de la definición. Sin presupuesto de 8 KiB.
- Obligatoriedad: la configuración local compone siempre `documents = "v2"`; omitir la clave equivale a "v2" y otro
  valor se rechaza. Las versiones congeladas incluyen `document_layout = "d088-1"`, así que un job pendiente admitido
  con la composición anterior no recibe puertos ni escritor y queda en cuarentena. `ProjectContext.documents = None`
  solo describe contextos congelados anteriores, que se siguen leyendo sin cambios.
- Creación v1 retirada en el backend: `BootstrapRepository.preview` (y con él `submit`) rechaza un contexto sin layout
  y el descubrimiento de un turno rechaza cualquier petición nueva, con un diagnóstico «D088: v1 project creation …
  is retired». Se eliminan la plantilla `bootstrap-foundation.json`, `proposal()` y la validación del formulario, y
  `examples/bootstrap_demo.py`. Las operaciones v1 registradas se siguen leyendo; su ejecución y conciliación no cambian.

Decisiones tomadas con criterio:

- La obligatoriedad vive en la composición (TOML y registro), no en `ProjectContext`: así los contextos congelados sin
  la clave conservan su lectura, como exige T002, y los contextos construidos a mano en pruebas siguen siendo
  explícitos.
- La reconciliación de fase puede editar la prosa de DECISIONS (ya no está prohibida en su contrato), porque D088
  punto 2 le asigna añadir decisiones y ya no hay carpeta donde hacerlo; su restricción pide secciones
  `## DNNN — title` con «Estado:» y el siguiente número libre. Las tareas normales siguen sin poder tocarlo.
- `protected_write` exime AGENTS, CLAUDE y GEMINI del layout para que la creación pueda escribirlos aunque el perfil
  los proteja frente al ejecutor (D081). Su edición confirmada (`Layout.editable`) y el resto de rutas del ejecutor
  quedan para T003.
- Los borradores de la definición admiten la plantilla y `docs/flows/*.md` (adelanto mínimo de T005, porque las
  carpetas anteriores desaparecen); AGENTS, CLAUDE, GEMINI y DDBB-DIAGRAM no redactados salen de la plantilla con el
  título de la conversación y los comandos del perfil congelado. La carpeta de documentación no puede estar en `.git`.
- La API conserva la forma del índice (`file`, `date`, `phase`, con `file = "DECISIONS.md"` y los otros a null) hasta
  T006, sin regenerar OpenAPI ni tocar la UI.
- Las pruebas de la creación v1 se reescriben sobre una definición v2 lista para aceptar (misma intención, caídas,
  conciliación y guardias) o pasan a comprobar el rechazo; el recorrido HTTP de extremo a extremo usa la conversación
  de definición.

Límites hasta T003–T007: los prompts (`define-project`, `plan-phase`, `reconcile-phase`, `review-task`,
`execute-task`) siguen nombrando `decisions/` y `architecture/`; los perfiles protegen `docs/**`; el cierre y la
transición siguen separados; la UI enlaza `decisions/DNNN`. Este repositorio sigue sin registrarse en el harness.

## D090 — P008-T003: rutas del ejecutor, paridad de diagramas y propuestas de ADR

Estado: implementada y verificada offline el 2026-10-15. Fase: P008. Aplica D088 puntos 2, 6 y 8; modifica D081 para
la reconciliación de fase.

Implementado:

- **Perfil `typescript-web`.** La protección `docs/**` se sustituye por `docs/STATE.md`, `docs/NEXT_STEPS.md`,
  `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/archive/**`, `AGENTS.md`, `CLAUDE.md` y `GEMINI.md`; el resto de rutas
  protegidas no cambia. Un contrato que permita `docs/flows/**`, `docs/DDBB-DIAGRAM.md`, ARCHITECTURE, SPECIFICATION o
  `docs/phase/**` deja escribir al ejecutor.
- **`harness_owned_paths`.** Además del archivo y de STATE, NEXT_STEPS, ROADMAP y DECISIONS (salvo en la
  reconciliación), prohíbe siempre AGENTS, CLAUDE y GEMINI, también a la reconciliación.
- **Un solo punto para el perfil frente al ejecutor**: `documents.executor_protected(context, task_id, path)`, usado
  por `check_paths`, `permissions.allowed` y el contrato de reconciliación. En v2, los cuatro documentos de control los
  gobierna el contrato documental: la reconciliación (`<fase>-RECONCILE-<n>`) edita su prosa aunque el perfil los
  proteja (cambio respecto a D081, donde el perfil también limitaba la reconciliación). Fuera de v2 manda el perfil. Un
  perfil que protege cualquier otra ruta permitida a la reconciliación (por ejemplo `docs/**`) sigue exigiendo
  reconciliar a mano.
- **Edición confirmada de las instrucciones.** `Layout.editable` incluye AGENTS, CLAUDE y GEMINI, así que la edición
  confirmada, la lectura de documentos y `protected_write` los admiten. `protected_write` rechaza explícitamente
  cualquier ruta con `..` (antes solo la rechazaba un perfil que protegía `docs/**`).
- **Paridad de modelos de datos, determinista.** `ProjectProfile.data_model_paths` (patrones, vacío por defecto; el
  snapshot del contexto omite la clave vacía para conservar los anteriores). Con el layout v2, si el diff del ciclo
  toca esos patrones sin tocar `DDBB-DIAGRAM.md`, `assess_acceptance` (que ahora recibe el contexto) añade el motivo
  «Data model changed without docs/DDBB-DIAGRAM.md (D088): …»: el run se detiene en `acceptance` y el commit se
  rechaza, también al reevaluar en `prepare_commit`.
- **Paridad de flujos, por el revisor.** `review-task` (versión nueva) recibe en su entrada `documentation` (patrones y
  cambios de modelos, diagrama de datos, carpeta y cambios de flujos; solo con layout v2) y la regla: un cambio de
  modelos sin diagrama no se acepta y un cambio de flujo de negocio sin su documento en `flows/` es un REVISE.
- **Propuestas de ADR.** El ejecutor no edita DECISIONS (prohibido por contrato). Mecanismo de su salida: campo
  opcional `decision_proposals` del JSON final del ejecutor (como `permission_denials`), lista de como mucho 5 objetos
  `{title ≤200, decision ≤4000, rationale ≤4000}` sin otras claves; mal formada detiene el run en `executor`. El motor
  la pasa al revisor como `executor_decision_proposals` y el revisor devuelve en `decision_proposals` (misma forma,
  validada en `review_contract`; mal formada detiene en `reviewer`) las que respalda el trabajo. No cambian el
  veredicto ni la aceptación. Quedan con el intento (salida del ejecutor y `review_json` del ciclo, visible en
  `cycles[].review` de la API sin cambiar su esquema) y la reconciliación recibe en su evidencia las de la última
  revisión de cada tarea COMMITTED, con la instrucción de consolidarlas en DECISIONS si describen la realidad aceptada.
- **Versiones.** Adaptador `cli-10` (las formas de ejecutor y revisor que se añaden al prompt incluyen
  `decision_proposals`) y `document_layout = "d088-2"`: los jobs pendientes admitidos antes quedan en cuarentena. Los
  intentos anteriores conservan su catálogo de prompts y su esquema congelados.

Decisiones tomadas con criterio:

- El perfil `reference_project` (solo biblioteca, no componible desde el TOML) conserva `docs/**`: describe un repositorio
  con el layout anterior hasta que el Flujo A lo normalice (T009–T012) y T008 traiga los perfiles declarativos.
- `typescript-web` no declara `data_model_paths` (web estática sin persistencia); el primer perfil con patrones será
  `python-django` (T008). La regla se prueba con perfiles sintéticos.
- La paridad de modelos bloquea la aceptación aunque el revisor acepte, como pide T003; la de flujos depende del
  juicio del revisor porque «flujo de negocio» no es deducible por rutas.
- `execute-task` no cambia hasta T005: el ejecutor conoce el campo por el esquema JSON y la forma que acompañan al
  prompt.

Pendiente: prompts restantes (T005), API y UI de las propuestas y las clases de documento (T006).

## D091 — P008-T004: cierre y archivo unificados con planificación posterior

Estado: implementada el 2026-10-15; verificación offline en [registro de trabajo](archive/phase-008/P008-T004_CIERRE_UNIFICADO.md).
Fase: P008. Aplica D088 punto 4; sustituye el cierre sin edición de D032 y la nueva transición separada de D073.
Conserva las definiciones versionadas de D034 y los historiales anteriores.

- El cierre confirmado congela el archivo desde ROADMAP y SQLite, sin exigir un plan para N+1. Rechaza antes de
  escribir checkout sucio, deriva documental, archivo existente, colisiones de nombres y trabajo pendiente. El job
  vuelve a observar el vínculo READY bajo el lock, sella y persiste la intención del commit, después la del tag, crea
  el tag sobre el HEAD evaluado y ejecuta un único commit de archivo. El tag sigue siendo opcional y conserva el
  tipo declarado por el proyecto (D034).
- STATE y NEXT_STEPS originales se archivan por bytes; REVIEW y SUMMARY salen de SQLite. Todo `docs/phase/**` se
  mueve al archivo conservando sus bytes, incluidos binarios y CRLF. Las colisiones con STATE, NEXT_STEPS, REVIEW y
  SUMMARY, los enlaces y los objetos no regulares se rechazan. Se mantiene el límite documental de 512 KiB por
  archivo; no hay truncado. El escritor Git admite contenido base64 y borrados CAS para estos movimientos: es la
  extensión técnica necesaria de `adapters/git.py` a las rutas de T004. Los campos anteriores de la intención se
  siguen leyendo con UTF-8 por defecto.
- El mismo commit deja STATE con la base acumulada, NEXT_STEPS con objetivo y criterios de N+1 sin tareas y ROADMAP
  con N completada y columna Archivo. La transacción que registra el resultado cierra N y crea N+1 ACTIVE con sus
  documentos adoptados. Sin sucesora no se crea fase. El check devuelve NEEDS_RECONCILIATION antes de invocar al
  revisor cuando STATE supera 24 KiB o la sección Base acumulada supera 12 KiB; compactar sigue siendo explícito.
- El abandono usa la misma operación `close` y run `phase_close`, con destino ABANDONED, sin READY ni tag. Invalida
  lotes y conserva las preguntas en el archivo. La API conserva la lectura PhaseRead, exige Idempotency-Key y devuelve
  CLOSING mientras se procesa el job; el cliente observa después ABANDONED. No se añade migración ni estado nuevo.
- Tras una caída se confirma el escritor detenido y se pide explícitamente el cierre/abandono otra vez. Se reusa la
  operación, el run y la intención sellada: incluso después del commit se concilia el mismo tag y commit y se crea
  una sola sucesora. Finalizar una intención existente no vuelve a exigir el READY sobre los documentos ya escritos
  ni recalcula su contenido por caducidad de la autorización inicial.
- `PhasePlanRepository` permite confirmar después el texto del usuario o una propuesta de `phase_planning`, solo
  sobre la última fase ACTIVE sin tareas. La vista previa incluye el plan y la definición; la confirmación por hash
  reutiliza la edición documental conciliable. El commit escribe NEXT_STEPS y regenera STATE; al registrar su
  resultado se añade una versión de la definición (D034). La conversación toma como destino la fase activa vacía.
  Prompts y UI se adaptan en T005/T006; los endpoints mínimos de plan y sus contratos generados se incluyen aquí para
  hacer operable esta tarea.
- Nuevas transiciones separadas H6.3 rechazadas. Una intención de transición interrumpida mantiene su vista previa y
  su recuperación; solo esa vía admite cambiar `document_layout` d088-1/2 → d088-3 al comprobar el escritor, si todo
  el resto del contexto/versiones coincide. El run conserva sus versiones y bytes originales. No se invocan agentes.
  Los endpoints antiguos se mantienen para recuperación hasta T006.
- `document_layout = "d088-3"` congela el protocolo nuevo; los demás jobs pendientes de composiciones anteriores
  se detienen por la guardia de versión habitual. No se cambian prompts, proveedores ni configuración global.

Validación y límites concretos en el registro de trabajo. No se ejecutó el harness sobre este repositorio ni se
invocaron proveedores reales.

## D092 — P008-T005: prompts y definición bajo el contrato unificado

Estado: implementada el 2026-10-15; verificación offline en el [registro de trabajo](archive/phase-008/P008-T005_PROMPTS_DEFINICION.md).
Fase: P008. Aplica D088 y conserva los valores por defecto de D089 y el plan posterior de D091.

- Nuevas versiones por hash de `define-project`, `plan-phase`, `reconcile-phase`, `close-phase`, `review-task` y
  `execute-task`, sin referencias a las carpetas retiradas. `revise-task` recibe las mismas reglas para conservarlas
  en cada corrección: discovery desde AGENTS, DECISIONS único, diagramas de datos y flujos, artefactos de fase y ADRs
  como propuestas. Solo la reconciliación autorizada consolida decisiones en la prosa de DECISIONS, conservando
  numeración e historia. Ni el prompt de revisión ni el de ejecución prohíben esa excepción documentada.
- La definición versión 4 declara obligatorios los once documentos del resultado aceptado. Se mantienen los siete
  borradores obligatorios y el completado de AGENTS, CLAUDE, GEMINI y DDBB-DIAGRAM desde la plantilla de D089; nunca
  sustituye un borrador existente. Los valores por defecto (título y comandos del perfil congelado) entran también
  en el contexto del turno. AGENTS de más de 60 líneas y CLAUDE/GEMINI de más de 15 bloquean la aceptación.
- Los únicos borradores variables siguen siendo `flows/*.md` de un nivel. No se admiten artefactos de fase,
  archivos individuales de decisiones, carpetas antiguas ni flujos anidados como borradores de creación. La vista
  previa y el commit raíz incluyen las instrucciones propuestas, o las de la plantilla cuando faltan.
- `plan-phase` usa exactamente `context.next`: la fase ACTIVE sin tareas que deja el cierre, o la siguiente fase de
  las conversaciones anteriores. La confirmación posterior instala el plan y versiona la definición; no pide otra
  transición. Su contexto incluye DDBB-DIAGRAM y los archivos de instrucciones con las lecturas acotadas existentes.
  El check de cierre no exige un plan de la sucesora para devolver READY.
- `document_layout = "d088-4"`, definido en el núcleo documental y consumido por la composición, pone en cuarentena
  los jobs pendientes anteriores antes de efectos. Extensión técnica mínima a las rutas de T005:
  `services/local_config.py` importa la versión y `services/managed.py` conserva la recuperación D091 de transiciones
  con intención ya sellada. Solo esa conciliación admite d088-1/2/3 → d088-4, si coinciden el resto de versiones y el
  contexto, sin agentes ni recálculo de bytes; el run sigue guardando su versión original.
- Los catálogos e intentos anteriores conservan identidad, contenido, esquema y snapshot; no hay cambio de codec,
  adaptador CLI, modelos, migraciones, dependencias ni contrato de salida de los agentes. La inyección de AGENTS en
  todos los roles y la verificación de los flags de las CLI siguen pendientes de T007.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D093 — P008-T006: API y UI del contrato unificado

Estado: implementada y verificada offline el 2026-10-15; detalle en el [registro](archive/phase-008/P008-T006_API_UI.md).
Fase: P008. Aplica D088 y alinea la UI de D080/D082 con el cierre y el plan posterior de D091. Sustituye sus enlaces
a decisiones individuales, la creación v1 y la transición separada de fase en la API/UI.

- `DocumentKind` distingue `phase`, `product`, `instructions`, `diagram`, `flow`, `phase_work`, `archive` y `other`.
  La proyección de API clasifica por el `Layout` configurado y añade AGENTS/CLAUDE/GEMINI al árbol y al estado; no los
  incorpora a los hashes adoptados de la fase. No sigue enlaces simbólicos en las instrucciones. La representación
  interna de almacenamiento y los historiales congelados se conservan.
- El índice público de decisiones tiene solo `id`, `title` y `status`, desde los encabezados y la primera línea
  `Estado:` de DECISIONS. La UI enlaza al encabezado del registro con el mismo slug que su renderizador Markdown;
  no ofrece archivos individuales ni columnas de fecha/fase que el índice ya no produce.
- Se retiran POST de bootstrap, su preview y discovery, y ambos POST de transición, junto con sus esquemas públicos
  de entrada. Se conserva GET `/projects/{id}/bootstrap` como estado de la definición conversacional, con `enabled`,
  `import_required`, `diagnostic` y `definition_operation`. Las lecturas de runs/operaciones conservan los tipos
  históricos y el motor mantiene la conciliación de intenciones antiguas selladas, sin exponer otra transición.
- `Bootstrap.tsx` se elimina. Cierre y abandono explican el archivo en un commit y la sucesora ACTIVE sin tareas (o
  solo archivo si ROADMAP termina). La planificación de esa fase vive en su propia página: texto o propuesta,
  vista previa, diff, hash, motivo y confirmación idempotente por `/phases/{id}/plan`. Una versión distinta de la fase
  o un cambio del plan descarta la vista previa. El registro deja de ofrecer el layout como una opción desactivable.

Sin modelos, migraciones, dependencias ni cambio de versión congelada: la tarea cambia la superficie de API/UI,
no los contratos del motor. OpenAPI y tipos del cliente regenerados desde los esquemas.

## D094 — P008-T007: AGENTS.md en el prompt congelado de cada rol

Estado: implementada y verificada offline el 2026-10-16; evidencia y límites en el
[registro](archive/phase-008/P008-T007_INSTRUCCIONES_CONTEXTO.md). Fase: P008. Aplica D088 punto 8 y conserva D066 y D068.

Verificación previa, sin ejecutar ninguna CLI:

- Codex 0.162.1, según la fuente del pin y los literales del nativo de D059: el escritor no carga el `AGENTS.md`
  del proyecto, porque `trust_level="untrusted"` (D068) corta la búsqueda. El lector, sin entrada de confianza, lo
  carga desde el checkout vivo y antepone un `AGENTS.override.md` si existe. `--ignore-rules` solo afecta a
  execpolicy.
- Claude, según la documentación oficial vigente (los pins ya no están instalados): con `--setting-sources ""` no
  carga `CLAUDE.md` ni, por tanto, `@AGENTS.md`. Incluir `project` cargaría también `settings.json` y hooks del
  checkout, así que no se cambia.

Decisión:

- El motor lee `AGENTS.md` de la raíz del checkout del intento en cada intento. Exige un archivo regular sin enlaces,
  UTF-8, no vacío, sin NUL y de 32 KiB como máximo, sin truncar. Lo inyecta con la variable `{{PROJECT_INSTRUCTIONS}}`,
  que solo aporta `render_attempt`, y guarda ruta, SHA-256 y tamaño en `project_instructions` del snapshot.
  Ausente o inválido, el intento se detiene en `prompts` antes de invocar.
- La variable está en `plan-task`, `execute-task`, `review-task`, `revise-task`, `close-phase`, `chat-turn` y
  `plan-phase` (la reconciliación la recibe por `execute-task`). La definición queda fuera porque redacta ese archivo y
  su borrador ya está en su contexto; `bootstrap-project` está retirada. Las reglas del harness y las entradas
  congeladas prevalecen sobre `AGENTS.md`, y este no concede rutas, herramientas ni permisos.
- Las versiones de plantilla anteriores siguen siendo válidas para leer catálogos congelados y versiones guardadas.
  Con layout no pueden invocar: piden activar una versión con la variable. Un contexto sin layout (congelado antes de
  D088) recibe un texto fijo de ausencia.
- Adaptador `cli-11`: toda invocación Codex lleva `-c project_doc_max_bytes=0`, para que el lector no cargue una copia
  viva sin hash y el único `AGENTS.md` sea el congelado. Es seguro porque solo quita una entrada, como verifica la
  fuente del pin. Los flags de Claude no cambian.
- `document_layout = "d088-5"` y `cli-11` dejan en cuarentena los jobs pendientes anteriores. Un cambio de `AGENTS.md`
  solo afecta a los intentos posteriores; los snapshots guardados no se reescriben.

Límites: ninguna observación en ejecución; Codex 0.161.0, el `AGENTS.md` global de Codex y la configuración gestionada
sin analizar. Una transición sellada con `cli-10` y adaptador CLI real deja de reanudarse, como ocurrió con
`cli-9 → cli-10`; la excepción de D092 solo cubre `document_layout`. `plan-phase` recibe `AGENTS.md` también en su
contexto congelado. Sin modelos, migraciones, dependencias, API ni UI.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D095 — P008-T008: perfiles declarados en local-config-4

Estado: implementada y verificada offline el 2026-10-16; detalle y límites en el
[registro](archive/phase-008/P008-T008_PERFILES_DECLARATIVOS.md). Fase: P008. Aplica D088 punto 11 y conserva D049 y D078.

Decisiones tomadas con criterio dentro de la tarea:

- `local-config-4` es `local-config-3` más `[profiles.<nombre>]` opcional. Las composiciones nombran un perfil
  integrado (`typescript-web`) o uno declarado; los proyectos siguen nombrando una composición y el registro desde la
  UI funciona igual. `local-config-1/2/3` se leen sin cambios, con sus hashes congelados, y v1–v3 no admiten
  `[profiles]`. Los nombres integrados quedan reservados; `reference_project` sigue siendo solo de biblioteca.
- Claves explícitas, como en D049: `preparation`, `validations` (al menos una), `allowed_command_prefixes`,
  `protected_paths` y `sensitive_paths` (no vacías), `data_model_paths` (puede ir vacía) y
  `executor_instructions`; solo `sensitive_allowlist` es opcional. Cada comando es una tabla con `argv` y
  `timeout_seconds`, más `cwd` y `environment` opcionales. El JUnit se declara junto a su validación con
  `junit = { path, coverage }`, así que el reporte siempre se refiere a un comando exacto del perfil. No se exponen
  `formatter_*`, porque nada los ejecuta. Una clave desconocida, una ruta que sale del checkout o un comando repetido
  se rechazan.
- «argv sin shell»: el primer elemento es un nombre simple de `executables` y no un intérprete de órdenes (sh, bash,
  zsh…). Ningún argumento puede ser un operador de shell (`&&`, `|`, `;`, `>`…) ni contener `` ` `` o `$(`. En v4 la
  regla cubre también los prefijos, las autorizaciones extra y los ejecutables de la composición, que no pueden
  apuntar a un shell. Un prefijo permitido no autoriza ejecutar nada: ejecutar exige la autorización exacta.
- En v4 el contenido completo del perfil de cada composición, integrado o declarado (`asdict` del `ProjectProfile`),
  entra en `local_config_sha256`. Si cambia, los jobs pendientes quedan en cuarentena antes de efectos. El snapshot
  del run ya guardaba el perfil completo, así que el codec no cambia.
- `check-config` muestra en `profiles` cada perfil declarado con su SHA-256, los argv de preparación y validación,
  los reportes JUnit y `data_model_paths`, sin valores de entorno. Las opciones de registro de la API no cambian.
- El ejemplo `python-django` de `examples/local_config.example.toml` incluye: preparación `python --version` y
  `python -m django --version`; validaciones `pytest --junitxml=.local/junit.xml -q` (con JUnit), `ruff check .`,
  `ruff format --check .`, `mypy .`, `manage.py check` y `makemigrations --check --dry-run --noinput`; protección de
  los documentos de control, de las instrucciones y de la configuración de herramientas; y paridad sobre
  `models.py`, `models/` y `migrations/`. Es una propuesta que el usuario debe confirmar antes de usarla.

Límites: los textos de `serve --help`, el diagnóstico del registro y la UI (Home y Registry) siguen citando
`local-config-3`, porque esos archivos quedan fuera de las rutas de la tarea. El perfil no se ha ensayado con un
proyecto Django ni con herramientas reales. Sin modelos, migraciones, codec, dependencias, API ni UI.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D096 — P008-T009: inventario de importación desde el árbol de HEAD

Estado: implementada y verificada offline el 2026-10-16; detalle y límites en el
[registro](archive/phase-008/P008-T009_INVENTARIO_FLUJO_A.md). Fase: P008. Aplica D088 punto 10; conserva D012 y D027.

Decisiones tomadas con criterio dentro de la tarea:

- El inventario lee el árbol de HEAD de un checkout limpio con Git de solo lectura (`rev-parse`, `status` sin locks
  opcionales, `ls-tree` y `cat-file --batch` sin filtros), con el entorno controlado de `adapters/git.py`. Lo ignorado
  no se lee, los enlaces simbólicos y submódulos son entradas rechazadas que bloquean el Flujo A, y releer el mismo
  checkout da el mismo resultado. Se rechaza sin Git, sin commits, con HEAD vacío o con cambios o archivos sin
  seguimiento. Límites: 5.000 entradas, 16 MiB por entrada y 256 MiB en total, sin truncar.
- Ámbito documental: Markdown de la raíz, `docs/` (la carpeta de STATE del contexto) y `.harness/` salvo sus runs,
  que solo se cuentan por lstat porque siguen la migración D027.
- Cinco clases (`canonical`, `renameable`, `mergeable`, `historical`, `foreign`), cada entrada con la regla que la
  justifica y el documento canónico cuando es inequívoco. Los alias son una lista explícita (mayúsculas,
  `DECISSONS.md`, `ADR*.md`, documentos de `docs/` en la raíz, `architecture/data-model.md`). Un alias que chocaría
  con un destino existente o compartido pasa a `mergeable` (`alias-conflict`); igual con la renumeración del archivo.
  Lo ambiguo (`PROJECT.md`, `REQUIREMENTS.md`, `HARNESS_COMMANDS.md`, `UI_*.md`, `DELIVERY_CHECKLIST.md`) es
  `mergeable` para la propuesta del revisor; `.harness/**` y lo que no es Markdown fuera del archivo son `foreign`.
- Origen por señales: un único origen (ReferenceProject, v1 o v2) lo determina; varios dan `mixed`; ninguno, `unified` con
  los once documentos de D088 o `unknown`. `phase-000` sin STATE no es señal de ReferenceProject.
- Las fases de ROADMAP (`## PNNN —` o `## Phase NNN —`), STATE, NEXT_STEPS y archivo se informan tal como se detectan,
  sin reconciliarlas. La huella `inventory_sha256` excluye raíz y commit e incluye árbol, entradas y runs.
- Sin persistencia, API ni UI: el inventario es un valor recalculable que T011 congelará con la conversación de
  importación.

Límites: un filtro `clean` definido en la configuración local del repositorio podría ejecutarse durante `status`
(configuración del usuario, no contenido del proyecto). No hay entrada HTTP ni CLI todavía. Sin modelos, migraciones,
codec, dependencias, prompts ni contratos generados.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D097 — P008-T010: mapa de normalización del Flujo A

Estado: implementada y verificada offline el 2026-10-16; reglas, salida y límites en el
[registro](archive/phase-008/P008-T010_MAPA_NORMALIZACION.md). Fase: P008. Aplica D088 punto 10 sobre el inventario de D096.

Decisiones tomadas con criterio dentro de la tarea:

- El mapa es una función pura del inventario y de sus bytes, que se comprueban contra la huella y los SHA-256 del
  inventario. Sin adaptador, persistencia, API ni UI: T011 lo congela y T012 lo aplica. Formato
  `harness-local/import-map/1` con huella `map_sha256`.
- Cada operación cita una regla con identificador. Los movimientos conservan los bytes; ningún destino coincide, sin
  distinguir mayúsculas, con una ruta del árbol original distinta de su origen, con otro destino o con un directorio.
  Lo que choca pasa a la propuesta del revisor (`target-conflict`). No hay cadenas de movimientos.
- Lo retirado sin fase propia (BRIEF y PROJECT_PROFILE de v1, los README de las carpetas v2 y los originales de las
  decisiones compuestas) va a `archive/phase-000/` conservando su ruta bajo `docs/`, como el Flujo B guarda en
  `phase-000` lo sustituido.
- `research/**` y los archivos de la raíz de `docs/` que empiezan por `PNNN` son artefactos de fase: a `docs/phase/`
  si su único código es la fase activa (STATE y NEXT_STEPS deben coincidir) y a `archive/phase-NNN/` si es otra con
  archivo. Sin código único o sin destino conocido, al revisor (`phase-unknown`).
- `decisions/DNNN-*.md` se compone en DECISIONS en orden numérico: base intacta y cada archivo con un `#` delante
  (título a nivel 2). Solo entra lo que no admite dos lecturas: primera línea `# DNNN — título` con el número del
  nombre, UTF-8, sin otros encabezados de nivel 1 o 2 ni marcadores, número único y ausente de la base. Sin
  DECISIONS ni alias, la base es una plantilla mínima con el bloque vacío; el índice lo regenera el commit (T012).
- Lo ambiguo (fuentes de SPECIFICATION, detalle de arquitectura, checklist v1, Markdown sin clasificar, conflictos de
  alias y del archivo) queda en `review` con su motivo; `.harness/**` y lo no Markdown, en `foreign` para el usuario.
  `missing` lista los documentos de D088 que el árbol resultante no tiene.

Límites: la prosa de una base v2 de DECISIONS («Registro en `decisions/`…») y el cuerpo antiguo de su bloque siguen
tal cual hasta T011 y el commit. Sin modelos, migraciones, codec, dependencias, prompts ni contratos generados.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D098 — P008-T011: conversación de importación con borradores privados

Estado: implementada y verificada offline el 2026-10-16; detalle y límites en el
[registro](archive/phase-008/P008-T011_PROPUESTA_REVISOR.md). Fase: P008. Aplica D088 punto 10 sobre D075, D096 y D097.

Decisiones tomadas con criterio dentro de la tarea:

- Tercer tipo de conversación de H6.5, `project_import`, con las mismas tablas, cola, lock, guardia, cuarentena y
  reglas de turno (FAILED sin fallback; caída → UNKNOWN). La migración `0019_import_conversations` añade
  `planning_conversations.source`, donde se congelan al crearla el inventario de HEAD (T009) y su mapa (T010). Solo
  para proyectos que el harness aún no gestiona: sin creación por bootstrap ni fases propias.
- El turno reutiliza el rol de solo lectura `definition` y su esquema (respuesta, preguntas, borradores completos y
  pendientes) con una plantilla nueva, `import-project`; el adaptador sigue en `cli-11`. La plantilla no inyecta
  `AGENTS.md`: el del proyecto es parte del origen (puede faltar o exceder D088) y llega con los demás textos.
- Cada turno comprueba que el checkout sigue dando la misma huella de inventario (si no, no se encola) y congela los
  textos del árbol resultante del mapa, comprobados contra sus hashes, salvo el archivo, que va por ruta y hash, junto
  con los borradores (2 MiB en total como máximo). Antes y después de invocar se observan la huella y el área: un
  cambio descarta la respuesta.
- Rutas admitidas: las de la definición (plantilla D088 y `docs/flows/*.md`). Un borrador sustituye el documento de
  su ruta en el árbol resultante; lo demás conserva el resultado del mapa.
- Borradores en `import-drafts/<conversación>/` junto a la base SQLite (carpeta 0700 derivada solo de la base y del
  id), con la CAS de los borradores de la definición; aplicar exige confirmación y el hash mostrado. El checkout no se
  escribe hasta T012.
- `GET …/planning/{c}/import` relee checkout y área y da los bloqueos para pasar a la vista previa: turno pendiente,
  checkout distinto del inventariado, entradas bloqueadas del inventario, borradores inválidos, preguntas bloqueantes
  sin responder ni aplazar, documentos de D088 ausentes del mapa y de los borradores, AGENTS >60 líneas o
  CLAUDE/GEMINI >15, bloques gestionados ajenos y numeración de DECISIONS. Los documentos con contenido por defecto
  (AGENTS, CLAUDE, GEMINI, DDBB-DIAGRAM) ausentes, las entradas que el mapa dejó al revisor, lo ajeno y los pendientes
  son avisos.
- Extensiones técnicas fuera de las rutas de la tarea, como en D091/D092: `services/managed.py` (observación del turno),
  `frontend/openapi.json` y `frontend/src/api.generated.ts` regenerados, y la etiqueta «Importación» del nuevo
  `purpose` en `frontend/src/pages/shared.tsx` y `frontend/src/metrics.ts`, que el tipo exige.

Límites: con `.harness/runs` sin activar, la guardia de modo D027 rechaza los turnos (la conversación sí se crea). El
orden entre la activación D027 y la importación queda para T012, porque el marcador de modo gestionado cambia el
estado limpio que exige el inventario. La coherencia de STATE y NEXT_STEPS con la fase activa y el destino de las
entradas en revisión no se comprueban aquí: son de la vista previa de T012. Sin UI propia de la importación.

No se ejecutó el harness sobre este repositorio, ni proveedores reales, smokes, push o publicación.

## D099 — Flujo A: activación D027 antes de la importación

Estado: decidida por el usuario el 2026-10-16, a propuesta de la sesión; pendiente de implementar en P008-T012. Fase:
P008. Resuelve la pregunta abierta de D098 (límites); conserva D027 y su guardia de modo.

Contexto: con `.harness/runs` sin activar, la guardia D027 rechaza los turnos de la conversación `project_import`.
Activar el modo gestionado escribe `.harness/managed-mode.json`, que en ReferenceProject no está ignorado
(`.harness/.gitignore` solo ignora `runs/`, comprobado en solo lectura), y el inventario de D096 exige un checkout
limpio, así que las dos operaciones se bloqueaban entre sí.

Decisión:

1. **Orden.** Con runs legacy, la activación D027 (operación confirmada aparte, con su copia verificada del historial)
   va antes de la conversación de importación y de su commit. La guardia no se exime para ningún run del Flujo A.
2. **Inventario.** El inventario tolera un único archivo sin seguimiento, `.harness/managed-mode.json`, y solo cuando
   la guardia confirma que coincide por hash con una activación viva y `ACTIVE`. Cualquier otro cambio, o un marcador
   sin activación o distinto de ella, sigue bloqueando como checkout sucio.
3. **Commit de T012.** No versiona el marcador ni modifica ningún `.gitignore` del proyecto: el marcador es estado
   local de esta instalación y queda fuera del contrato documental.
4. **API y UI.** Si hay runs legacy sin activar, la importación presenta como primer paso la vista previa de la
   activación D027 en lugar de crear la conversación.

Motivos: el commit de normalización es una escritura del harness y necesitaría la activación de todos modos; el
historial queda copiado y verificado antes de mover ningún documento; no se abre una excepción en la guardia de
seguridad de D027; activación (`.harness/`) e importación (documentos; `.harness/**` es ajeno en el mapa) no se
solapan. Alternativa descartada: importar primero, que exigía eximir de la guardia los turnos (y el commit o un
orden inverso dentro de T012) y dejaba al harness anterior escribir runs durante la conversación sin copia verificada.


## D100 — P008-T012: importación confirmada y continuidad del Flujo A

Estado: implementada y verificada offline el 2026-10-16; detalle y límites en el
[registro](archive/phase-008/P008-T012_COMMIT_CONTINUIDAD.md). Fase: P008. Aplica D088 punto 10 e implementa D099, sobre D027,
D037 y D098. No reescribe historiales ni intenciones anteriores.

- **Árbol confirmado.** Inventario y mapa de la conversación + borradores privados y valores por defecto de D089.
  El mapa resuelve movimientos; las entradas de `review` fuera del archivo se retiran al archivo como parte de la
  confirmación del árbol completo. Los archivos ajenos quedan donde están, listados para la revisión. Cada original
  cuyo destino cambie por borradores, composición o bloques se conserva por bytes en
  `docs/archive/phase-000/import-originals/<ruta original>`. Los originales ya conservados en un destino del mapa no
  se duplican. Ningún destino de conservación ocupado se sobrescribe; colisiones de mayúsculas, archivos y
  directorios bloquean. El archivo previo permanece intacto.
- **Coherencia.** STATE y NEXT_STEPS deben declarar inequívocamente la misma fase; ROADMAP debe describirla con
  objetivo y criterios. Se regeneran los cuatro bloques de control y el índice de decisiones. Se adopta esa fase
  `ACTIVE` con las tareas del plan (puede estar vacía); no se infiere aceptación ni intentos desde runs legacy.
- **Persistencia y recuperación.** `0020_project_imports` añade una tabla (35 en total), única por raíz,
  conversación y run, con preview, intención, decisión, resultado y fase. La confirmación exige hash, motivo y clave
  idempotente, congela versiones, contexto y autor y sella árbol/commit antes de escribir archivos o refs. El mensaje
  es «docs: normalizar al contrato documental». Reutiliza jobs, locks, leases, cuarentena y el escritor documental CAS.
  Una caída requiere confirmar el escritor detenido y reconfirmar la misma intención: mismo run y commit, job nuevo.
  La adopción y el resultado/fin del job son atómicos. La intención incierta cierra los borradores y bloquea trabajo
  nuevo, la creación de fases y la reversión D027. Repetir la vista previa completada informa que no hay cambios.
- **D099.** La API ofrece la vista previa de activación antes de crear la conversación cuando hay runs legacy.
  El inventario solo tolera el marcador sin seguimiento de una activación propia `ACTIVE`, coincidente por hash y
  sin deriva. La misma autoridad, inyectada en los puertos Git, lo excluye de la evidencia y de los commits también
  en tareas posteriores. Un marcador versionado se rechaza. No se toca ningún `.gitignore`.
- **Git y límites.** Las grafías de rutas son exactas: en macOS los alias de mayúsculas se borran antes de crear el
  canónico y la captura descarta del índice temporal la grafía ausente. No se modifica la configuración del usuario.
  La vista previa materializa blobs/árboles Git sin mover refs ni cambiar el índice real y comprueba que el diff
  resultante cabe en el límite de captura. Los binarios se congelan como base64 y se escriben por bytes.
- **API y UI.** `GET /projects/{p}/import`; `POST /projects/{p}/planning/{c}/import/preview` y `…/import/confirm`.
  Ruta `/projects/:p/import[/:c/*borrador]`, con activación previa D027, conversación, editor CAS, revisión del árbol,
  hash/motivo, progreso, recuperación y enlace a la fase adoptada. OpenAPI y tipos regenerados, sin rediseño visual.
  `document_layout = "d088-6"` congela estas reglas; jobs pendientes anteriores quedan en cuarentena.

Extensiones técnicas de las rutas de T012: `frontend/openapi.json`, tipos generados y prueba Node del enrutador para
los contratos y la nueva navegación. Sin dependencias nuevas, proveedores reales, smokes ni publicación.

## D101 — P008-T013: inventario estático del Flujo B y propuesta de perfil

Estado: implementada el 2026-10-16; verificación offline y límites en el
[registro](archive/phase-008/P008-T013_INVENTARIO_FLUJO_B.md). Fase: P008. Aplica D088 punto 11 sobre el perfil declarativo de D095.

Decisiones tomadas con criterio dentro de la tarea:

- **Fuente y frontera.** `adapters/project_onboarding.read_inventory(root)` describe un HEAD no vacío por su árbol
  sellado, usando solo `rev-parse`, `ls-tree` por id y `cat-file --batch`, con el entorno Git controlado existente.
  Exige `--no-lazy-fetch` para impedir descargas de objetos de clones parciales; Git sin ese flag se rechaza.
  No usa `status` (podría lanzar filtros `clean`), no recorre el worktree ni ejecuta código del proyecto. Los cambios
  locales no forman parte del inventario; T015 deberá exigir una base vigente antes de escribir.
- **Ámbito acotado.** Fuentes Python/JS/TS/Prisma/Go, manifiestos, configuración de herramientas, tests, CI y
  documentos raíz seleccionados. Se excluyen dependencias instaladas, cachés y builds aunque estén versionados.
  Límites: 50.000 entradas de árbol, 1 MiB por fuente, 32 MiB total; no se trunca. Enlaces/submódulos no se siguen;
  errores de lectura, formato o sintaxis dejan diagnóstico. El árbol sigue identificando la base completa.
- **Hechos con procedencia.** `core/project_onboarding.build_inventory` es puro, sin dependencias nuevas. Python
  con AST; manifiestos con JSON/TOML; JS/TS/Prisma con un subconjunto léxico explícito. Registra entidades/campos,
  relaciones, rutas locales, tests, CI y stack con fuentes. No evalúa expresiones ni resuelve imports, herencia entre
  módulos o montajes; lo dinámico queda señalado y los destinos desconocidos, a `null`. El inventario no garantiza
  completar el esquema runtime; la ingeniería inversa del revisor sigue pendiente de T014.
- **Formato recalculable.** `harness-local/onboarding-inventory/1`, con SHA-256 por fuente y `inventory_sha256`
  sobre árbol y hechos, independiente de raíz y commit. Sin SQLite, API, UI ni snapshots nuevos en T013. T014 lo
  congelará con la conversación; T015 confirmará perfil e incorporación.
- **Perfil propuesto.** Forma `local-config-4` con `[profiles.<nombre>]`, argv, cwd y evidencia de comandos,
  protección documental y paridad sobre modelos observados. Preparación vacía; no instala ni ejecuta nada, no
  escribe el TOML y siempre exige confirmación o edición. Si no detecta validaciones, `ready=false` y no inventa
  comandos para rellenarlas. Ejecutables, entorno y composición quedan para el operador. Los perfiles propuestos
  con comandos se validan en pruebas con el parser de D095.

Sin cambios de modelos, migraciones, dependencias, prompts, versiones congeladas ni API. Sin ejecución del harness
sobre este repositorio, proveedores reales, smokes, push o publicación.


## D102 — P008-T014: ingeniería inversa sobre HEAD y borradores privados

Estado: implementada el 2026-10-16; verificación offline y límites en el
[registro](archive/phase-008/P008-T014_INGENIERIA_INVERSA.md). Fase: P008. Aplica D088 punto 11 y D083, sobre D075 y D101.

- Conversación `onboarding` en las rutas de planificación existentes. Congela el inventario de T013, su HEAD y
  árbol en `planning_conversations.source` (0019), sin nuevas tablas ni columnas. Solo repositorios Git no vacíos
  y sin creación, fases o importación propia confirmada; STATE/NEXT_STEPS o `.harness/` versionados remiten al Flujo A.
  Los archivos raíz existentes, incluido README, son evidencia; no se sustituyen al conversar o aplicar borradores.
- Cada turno congela inventario, borradores, preguntas, ediciones y conversación, con límite conjunto de 2 MiB.
  Consulta el HEAD original incluso si el worktree o HEAD cambian después. T015 deberá comprobar la base vigente
  antes de escribir. Reutiliza la exportación privada de D083, sin `.git`, enlaces ni submódulos, con sus límites
  completos (20.000 archivos, 16 MiB por archivo y 128 MiB total), y Git con `--no-lazy-fetch` de D101. Se congela
  también el árbol completo, no solo las fuentes seleccionadas por el inventario. No se ejecuta código del proyecto.
- Rol de solo lectura `definition`, esquema existente y plantilla nueva por hash `onboard-project`. No inyecta
  AGENTS del disco: sus reglas se analizan como evidencia de la instantánea. Pide los once documentos D088 y
  flujos, diagrama desde modelos concretos, decisiones observadas marcadas «inferida del código», preguntas ante
  requisitos o planes no deducibles y confirmación de sustitución de README. Sin plantilla automática de diagrama
  «Sin persistencia» ni comandos de un perfil aún sin confirmar. Una respuesta inválida es FAILED sin fallback.
- Borradores en `onboarding-drafts/<id>/` junto a SQLite, con la CAS de la definición/importación. El harness solo
  los escribe tras aplicar una propuesta confirmada o una edición del usuario. El checkout no se escribe. Detecta
  cambios del área antes de invocar y modificaciones de la exportación o del área durante el turno; descarta la
  respuesta alterada. Preguntas abiertas y aplazamientos con motivo se conservan para la confirmación de T015.
- Conserva el carril de planificación de H6.5 y su lock por checkout; comparte con el chat la exportación, no su
  carril. Intención persistida antes de exportar; limpieza al terminar o al confirmar detenido el proceso tras
  caída. Una exportación fallida queda en recuperación, sin invocación ni reintento automático.
- `cli-12`: Codex recibe `--skip-git-repo-check` también para el rol `definition` si su raíz es una exportación,
  conservando sandbox de lectura y memoria desactivada. `document_layout = "d088-7"` deja jobs anteriores en
  cuarentena. Catálogos y snapshots anteriores siguen legibles; no se reescriben. La guardia de downgrade de 0019
  también impide perder un origen de onboarding, sin cambiar su upgrade ni la revisión SQLite.

Extensiones técnicas acotadas: supervisor para exportación/observación; flag/versionado del adaptador Codex;
`0019` solo en la guardia de downgrade; OpenAPI/tipos regenerados y etiqueta de propósito en dos archivos de UI.
El control y la recuperación siguen siendo cooperativos, sin aislamiento OS. Las pruebas usan revisores falsos:
comprueban contexto, contrato, CAS, diagrama sintético exacto y efectos, no la calidad de generación de un proveedor
real. UI específica, vista previa/commit, conservación de originales y confirmación del perfil pendientes de T015.


## D103 — P008-T015: incorporación confirmada del Flujo B

Estado: implementada el 2026-10-16; verificación offline y límites en el
[registro](archive/phase-008/P008-T015_INCORPORACION_CONFIRMADA.md). Fase: P008. Aplica D088 punto 11 sobre D037, D095,
D100 y D102.

- Vista previa sobre el HEAD original, checkout e índice limpios. Solo documentos de D088 y flujos; los once
  documentos deben existir en el origen o los borradores, sin fallback. STATE/NEXT_STEPS acuerdan P001 y ROADMAP
  aporta objetivo/criterios; se regeneran sus bloques e índice de decisiones antes de sellar la base adoptada.
  Preguntas bloqueantes sin responder ni aplazar, turno pendiente, borradores inválidos/ajenos, límites de líneas,
  deriva de HEAD/checkout o colisiones (también de mayúsculas y archivo/directorio) bloquean antes de escribir.
- El perfil propuesto por el inventario se muestra como referencia. La autoridad de efectos sigue siendo la
  composición local del operador (D049/D095): la vista previa muestra su perfil completo, incluidas validaciones,
  preparación, JUnit y rutas, y exige su `profile_sha256` además del hash de la vista previa, motivo e
  Idempotency-Key. Para modificarlo se edita el TOML local y se selecciona la composición en Ajustes; la API no
  admite comandos/ejecutables nuevos ni escribe el TOML. Confirmar la incorporación no ejecuta esos comandos.
- `archive/phase-000/INVENTORY.json` conserva el inventario congelado; `SUMMARY.md`, la conversación, preguntas,
  aplazamientos, pendientes y perfil. Todo original sustituido (README, instrucciones o documentación) se guarda
  por bytes en `onboarding-originals/<ruta original>`. README sin borrador se conserva en su sitio. Ningún archivo
  de código se sustituye ni se ejecuta; un destino de archivo ocupado bloquea, sin renumerar el historial.
- Se reutiliza `project_imports` (0020), `purpose = import_commit`, intención sellada, lock/lease y conciliación
  de D100. `preview.flow = onboarding` distingue la incorporación. Resultado, fase P001 ACTIVE y base documental
  se registran atómicamente al terminar el job. Al confirmar se cierran todos los borradores del checkout.
  Una caída conserva intención/run y exige confirmar detenido y reconfirmar para el mismo commit; una repetición
  completada devuelve cero cambios. Una composición distinta de la congelada impide conciliar.
- El escritor compartido de Git puede usar conversiones: antes de capturar o ejecutar la incorporación se
  rechazan filtros clean/process configurados, también mediante includes, y se contrastan los blobs del árbol
  propuesto con los bytes de la vista previa. Las conversiones internas que alteren bytes también bloquean.
  Los límites de exportación D083, documentos de 512 KiB y diff de 4 MiB se mantienen, sin truncar.
- API específica `…/onboarding` y UI `/projects/:p/onboarding[/:c/*borrador]`, sobre los componentes de importación;
  muestran perfil detectado, composición elegida, diff, conservación de originales, run y continuidad en P001.
  OpenAPI/tipos regenerados; `document_layout = "d088-8"` deja jobs anteriores en cuarentena sin reescribir
  historiales, catálogos, snapshots ni intenciones. Sin modelos estructurales, migraciones o dependencias nuevas.

La revisión del contenido inferido y la elección de la composición corresponden al usuario. Las pruebas offline
con revisores/comandos falsos verifican los efectos y la continuidad; no acreditan generación semántica ni CLI
reales. La exclusión y los permisos siguen siendo cooperativos. P008 sigue activa hasta su revisión y cierre.

## D104 — Revisión de salida de P008 con hallazgos en el Flujo A

Estado: revisión completada el 2026-10-17 sobre `f650851`; P008 sigue activa y no está lista para cerrar.
[Dictamen, evidencia y verificación](archive/phase-008/P008_REVISION_SALIDA.md). Fase: P008.

- Las quince entregas están implementadas y los recorridos sintéticos previstos existen. La revisión adicional
  reproduce tres incumplimientos del Flujo A: `git status` ejecuta un filtro local incluso con checkout limpio;
  `text eol=lf` cambia los bytes del blob y aun así la importación termina COMPLETED; un destino nuevo ignorado
  se acepta y deja documentos escritos con importación INTERRUPTED, sin commit ni fase adoptada.
- El requisito ya decidido sigue siendo lectura sin ejecución y commit del árbol documental exacto confirmado
  (D096/D100). El Flujo B tiene guardias para esos casos (D103). Se registra P008-T016 como siguiente tarea de
  corrección, sin iniciar su implementación en esta revisión y sin cambiar el diseño ni intenciones anteriores.
- Quedan referencias activas desactualizadas en especificación, arquitectura y ayudas de CLI/UI (H4), incluida
  la deuda de textos de `local-config-4` anotada en T008. Se sincronizarán antes de repetir la revisión de salida;
  las referencias históricas en decisiones, archivos o snapshots congelados se conservan.
- Esta sesión solo añade la revisión y sus reproducciones/evidencia sintéticas y actualiza el seguimiento.
  STATE compacta T003–T005 con enlaces al detalle existente para respetar el presupuesto. No hay cambios de
  producto, modelo, esquema, API, UI, dependencias ni versiones congeladas.

La revisión no autoriza ni ejecuta el cierre/archivo, registro de este repositorio, proveedores reales, smokes,
push o publicación. No se han lanzado subagentes ni cambiado la configuración global del usuario.

## D105 — P008-T016: frontera Git y bytes confirmados en las importaciones

Estado: implementada el 2026-10-17; verificación en el [registro](archive/phase-008/P008-T016_FRONTERA_GIT.md). Fase: P008.
Corrige H1–H3 de D104 bajo las garantías existentes de D096, D099, D100 y D103.

- **Antes de ejecutar Git con filtros.** El inventario A consulta `config --includes --get-regexp` y rechaza
  cualquier `filter.*.clean` o `filter.*.process` antes de `status`. La guardia se comparte con B y precede a
  captura/sellado y ejecución/reanudación. No ejecuta los filtros ni edita configuración. Las lecturas de los
  árboles propuestos mantienen `--no-lazy-fetch`, como B.
- **Árbol exacto.** Se leen los blobs del árbol propuesto y se contrasta el SHA-256 de cada documento resultante,
  incluidos los no modificados, originales archivados y binarios; las eliminaciones deben estar ausentes.
  Una conversión interna de atributos que altere bytes bloquea la vista previa antes de confirmar o escribir.
  El sellado final tiene que reproducir el árbol validado en la vista previa. El job contrasta el árbol sellado
  antes de llamar al escritor; este conserva la recaptura, el recálculo y la CAS anteriores, por lo que una deriva
  posterior de atributos tampoco autoriza escribir un árbol distinto.
- **Destinos ignorados.** `check-ignore` comprueba los documentos nuevos antes de confirmar y vuelve a hacerlo
  al ejecutar/reanudar. Un destino ignorado impide la escritura; no se fuerza su inclusión ni se cambia
  `.gitignore`. Los documentos ya versionados pueden seguir sujetos a sus reglas de exclusión habituales.
- **Continuidad.** Las guardias se aplican también a la vista previa de una importación interrumpida. Se mantiene
  la intención original, el mismo run/commit al conciliar, la CAS por bytes, D099 y la adopción atómica de fase.
  `document_layout = "d088-9"` congela estas reglas; una composición actual pone en cuarentena los jobs anteriores
  antes de efectos. No se reescriben intenciones ni snapshots; una intención antigua exige restaurar su composición
  compatible para continuar. No cambian esquema, API, prompts, adaptador CLI ni TOML.

Las regresiones usan exclusivamente repositorios/SQLite temporales, marcadores sintéticos y puertos falsos.
La configuración y exclusión siguen siendo cooperativas: las comprobaciones no añaden aislamiento del sistema
operativo ni una garantía frente a cambios concurrentes arbitrarios de configuración. H4 y la nueva revisión de
salida quedan para las tareas siguientes; esta corrección no cierra ni archiva P008.

## D106 — P008-T017: referencias vigentes sin cambiar contratos

Estado: implementada el 2026-10-17; verificación en el [registro](archive/phase-008/P008-T017_REFERENCIAS_VIGENTES.md). Fase: P008.
Resuelve H4 de D104 contrastando los textos con D093, D095, D102 y D105 y con el código vigente.

- SPECIFICATION refleja F11 y F18 implementados, conservando la confirmación pendiente del ejemplo Django sobre
  el proyecto del usuario. ARCHITECTURE presenta `cli-12`, `local-config-4` con lectura de 1–3, registro con 3/4
  y perfiles declarados; mantiene `document_layout = "d088-9"` de T016. Se aclaran las excepciones del rol
  `definition` a la inyección de instrucciones y la procedencia del control introducido en `cli-11`.
- Ayuda de `serve`, diagnóstico del registro y Home/Registry muestran los formatos admitidos. Prompts explica
  que `bootstrap-project` pertenece a la creación v1 retirada, `reconcile-phase` construye una tarea documental
  y `close-phase` revisa el check; el cierre tras READY exige su propia confirmación. Activar no inicia operaciones.
- Solo se corrigen textos y su selección en la UI: no cambian comportamiento operativo, contratos, versiones,
  prompts del motor, esquema, API ni dependencias. Las ADR anteriores, archivos y evidencias congeladas se conservan.

P008 sigue activa. La siguiente tarea es repetir la revisión de salida; el cierre y archivo son posteriores.

## D107 — Segunda revisión de salida de P008

Estado: revisión completada el 2026-10-17 sobre `a455ff9`, tras T016/T017; P008 sigue activa y no está lista
para cerrar por H5. [Dictamen y verificación](archive/phase-008/P008_REVISION_SALIDA_2.md). Fase: P008.

- H1–H3 de D104 se rechazan antes de efectos: filtros sin ejecución, conversiones de bytes y destinos ignorados
  sin escritura ni operación/commit/fase nuevos. Se conserva nueva evidencia sintética independiente y se
  comprueban las regresiones, recorridos válidos A/B, D099, recuperación y cuarentena por versiones.
- H4 está resuelto por T017. La revisión encuentra y corrige dos referencias adicionales de la prosa vigente
  en `flows/documents.md` y `flows/project-definition.md`: rutas/edición de instrucciones de T003 y flujos A/B
  de T009–T015 ya implementados. No cambia el diseño, los diagramas ni el código del producto.
- **H5, alta:** el lector A usa Git sin desactivar lazy-fetch. Un blob prometido ausente provoca que `ls-tree -l`
  ejecute el `upload-pack` configurado antes de confirmación o turno; reproducción offline con un marcador y
  transporte falso. B no lo ejecuta con `--no-lazy-fetch`. Se define P008-T018 para corregir esta frontera y los
  diagnósticos de objetos ausentes bajo las garantías existentes de D096; no cambia el diseño del producto.
- Se contrastan todos los criterios de ROADMAP, checks offline y paridad documental. STATE compacta el detalle
  de T006/T007 con enlaces a sus registros para conservar el presupuesto; entregas, ADR y evidencia anteriores
  permanecen intactas. No cambian modelos, esquema, API, dependencias ni contratos/versiones congelados.

Siguiente: T018 y nueva revisión de salida; el cierre y archivo son posteriores. Esta revisión no ejecuta
un check READY del producto sobre este repositorio, ni lo registra, cierra, archiva o etiqueta. ROADMAP no
define sucesora; no se inventa P009. No se amplían los consentimientos de proveedores, smokes, push o
publicación; se mantienen los límites de contención cooperativa y verificación visual.


## D108 — P008-T018: lecturas de importación sin lazy-fetch

Estado: implementada el 2026-10-17; verificación y límites en el
[registro](archive/phase-008/P008-T018_OBJETOS_LOCALES.md). Fase: P008. Corrige H5 de D107 bajo D096/D100/D101/D105.

- `adapters/local_git.py` extrae la frontera de B en `LocalGit`, sin depender de los inventarios. Cada comando
  exige `--no-lazy-fetch`; un Git antiguo falla desde el primer `rev-parse`, sin fallback por entorno. A la usa
  en `read_checkout`, por lo que también cubre inventario, origen de conversación, turnos, estado, vista previa
  y confirmación. B conserva su protección en inventario, exportación y lecturas de árboles sellados.
- El lector de tamaños compartido reconoce objetos/tamaños ausentes (`BAD`, o `-` en un blob) y da un diagnóstico
  con objeto y ruta; `-` en submódulos conserva su semántica anterior. Los lectores A/B y `HeadSnapshot` dejan
  de intentar `int('BAD')`. El lector batch común rechaza objetos ausentes, cabeceras sin tamaño válido y cuerpos
  incompletos; no entrega contenidos ni inventarios parciales. No se recuperan objetos ni ejecutan transportes.
- `document_layout = "d088-10"` congela las reglas corregidas; la composición pone en cuarentena jobs anteriores,
  incluido `d088-9`, antes de efectos. No cambia el formato de inventarios/mapas, prompts, codec, adaptador CLI,
  esquema, API ni dependencias. No se reescriben intenciones, snapshots ni evidencia histórica de H5; las
  transiciones antiguas selladas conservan su conciliación documentada.
- Se conservan las guardias de filtros y bytes confirmados, D099, CAS y recuperación del mismo commit. Solo
  Git/SQLite temporales y herramientas falsas en las regresiones, sin configurar el usuario ni ejecutar el
  harness sobre este repositorio. P008 sigue activa: después corresponde otra revisión de salida; cierre y
  archivo separados.

## D109 — Tercera revisión de salida de P008

Estado: revisión completada el 2026-10-17 sobre `0348b84`; P008 no lista para cerrar. Fase: P008.
Evidencia, comprobaciones y límites en el [registro](archive/phase-008/P008_REVISION_SALIDA_3.md).

- H1–H3 siguen rechazados antes de sus efectos y H4 conserva las referencias sincronizadas. H5 ya se rechaza
  en A/B con diagnóstico del objeto ausente, sin ejecutar el transporte falso, recuperar objetos ni cambiar
  bytes del checkout o de `.git`; todos los comandos observados llevan `--no-lazy-fetch`.
- H6 reproduce ejecución de un filtro `clean` de un submódulo durante `read_checkout`: la guardia solo consulta
  la configuración del repositorio principal, pero `status --ignore-submodules=none` inspecciona el submódulo.
  Con gitlink fuera de `docs/`, se acepta el inventario y se crea una conversación después de ejecutar el filtro;
  dentro de `docs/`, el bloqueo por submódulo llega después del efecto. Configuración directa y por include
  reproducidas con herramientas falsas; el inventario B no invoca el filtro en los mismos fixtures.
- Se define P008-T019 para impedir esa ejecución implícita antes de inventario/conversación/vista previa,
  conservando el rechazo de checkout sucio, las guardias D105/D108, D099, CAS y recuperación. Es una corrección
  de las garantías existentes de D096/D100, sin ampliar soporte de submódulos. Se evaluará su versión congelada.
- Esta revisión no cambia el producto, esquema, API ni versiones, ni reescribe evidencia histórica. El script
  nuevo y su JSON conservan H6; una ejecución correcta del script acredita el hallazgo, no su corrección.
  Cierre y archivo siguen separados. Sin registro ni check READY del producto sobre este repositorio;
  sin fase sucesora inventada, proveedores reales, smokes, push, publicación ni subagentes.

## D110 — P008-T019: gitlinks rechazados antes de inspeccionar el checkout

Estado: implementada el 2026-10-19; verificación en el [registro](archive/phase-008/P008-T019_SUBMODULOS.md). Fase: P008.
Corrige H6 de D109 bajo D096/D100/D103/D105/D108, sin ampliar soporte de submódulos.

- **Rechazo previo en todo el repositorio.** `check_submodules` consulta `ls-tree -r -z --full-tree HEAD` y
  `ls-files --stage -z` con `LocalGit`, sin abrir repositorios hijos. Un modo `160000` en cualquiera de las dos
  fuentes bloquea con ruta y origen antes de `status`, incluso fuera de `docs/`. Se cubren gitlinks recién
  añadidos o retirados del índice, hijos sin inicializar y gitdirs separados. No se ejecutan filtros de hijos,
  ni siquiera para comprobar su limpieza; no se cambia configuración ni se ignora suciedad.
- **Consumidores y escritor compartido.** Crear una conversación A, enviar turnos, observar antes/después y
  consultar estado/vista previa/confirmación heredan la guardia de `read_checkout`. `check_git` la repite
  antes de capturar/sellar y ejecutar/reanudar A/B, incluidas intenciones interrumpidas. El inventario estático
  B conserva su lectura sin seguir submódulos; la guardia posterior impide aprobar su escritura. El escritor
  general no cambia ni se amplía su soporte de submódulos.
- **Compatibilidad.** `document_layout = "d088-11"` congela el rechazo; la composición actual pone jobs anteriores
  en cuarentena antes de efectos. No se reescriben intenciones, snapshots, historiales ni la reproducción de H6.
  Tras retirar un gitlink añadido después de confirmar, la recuperación mantiene la intención, run y commit
  originales. Se conservan D099, CAS, filtros del padre/includes, objetos locales, hashes y destinos ignorados.
- **Alcance.** Solo Git/SQLite temporales, filtros marcador y agentes falsos. Sin esquema, API, UI, prompts,
  dependencias ni configuración global nuevos. Las comprobaciones mantienen la exclusión cooperativa de D105;
  no añaden aislamiento frente a cambios concurrentes arbitrarios del checkout/configuración.

P008 sigue activa. Después corresponde otra revisión de salida; cierre y archivo separados.

## D111 — Cuarta revisión de salida de P008

Estado: revisión completada el 2026-10-19 sobre `2815b5c`; P008 no lista para cerrar por H7. Fase: P008.
Evidencia, comprobaciones y límites en el [registro](archive/phase-008/P008_REVISION_SALIDA_4.md).

- H1–H5 mantienen sus resultados en las rutas revisadas. H6 queda resuelto: dieciocho escenarios nuevos con
  gitlinks dentro/fuera de `docs/` o solo en índice, filtros `clean`/`process` directos/por include y creación
  de conversación rechazan antes de `status`, sin filtros invocados ni cambios de bytes. Las 27 regresiones
  T019 también pasan, incluidos consumidores, observaciones y recuperación A/B.
- **H7, alta:** `GitWorkspace._git` usa `Git` sin `--no-lazy-fetch`. `_reachable` llama a `Git.code(cat-file -e)`
  sobre el commit esperado aún no escrito; su ausencia normal provoca lazy-fetch y ejecuta `upload-pack`.
  La guardia local previa no cubre ese comando posterior. Se reproduce con todos los objetos del origen
  disponibles en A/B, ejecución inicial y reanudación tras caída anterior al escritor. El transporte falso
  local deja marcador; las operaciones terminan COMPLETED con el commit sellado y sin nuevas invocaciones
  de agentes. No hubo red, objetos recuperados ni pérdida documental demostrada.
- Se define P008-T020 para impedir transportes implícitos del escritor A/B y su recuperación, manteniendo
  la ausencia normal del commit futuro, el rechazo de objetos necesarios ausentes, D099, CAS, hashes,
  guardias H1–H6 y conciliación de la misma intención/run/commit. Se evaluará su versión congelada.
- Esta revisión no cambia producto, esquema, API, prompts ni versiones; no reescribe evidencia histórica.
  El script y JSON nuevos exigen las guardias anteriores y acreditan el hallazgo H7, no su corrección.
  Cierre y archivo separados; sin registro ni check READY del producto sobre este repositorio, fase sucesora
  inventada, proveedores reales, smokes, push, publicación o subagentes.

## D112 — P008-T020: escritor de importaciones con objetos locales

Estado: implementada el 2026-10-19; verificación y límites en el
[registro](archive/phase-008/P008-T020_ESCRITOR_LOCAL.md). Fase: P008. Corrige H7 de D111 bajo D100/D103/D105/D108/D110.

- **Escritor vinculado a la frontera local.** `check_git` configura `GitWorkspace.local_objects_only` antes
  de captura/sellado y ejecución/reanudación A/B. Su fábrica interna entrega `LocalGit` para todas las llamadas
  `run`/`code`, incluidas comprobación del commit esperado, recaptura, escritura, conciliación y refresco del índice.
  Las demás instancias conservan su comportamiento por defecto. No depende de los objetos disponibles en
  el inventario ni de una variable de entorno que Git antiguo pueda ignorar.
- **Ausencia normal y soporte obligatorio.** El commit sellado aún ausente se consulta con
  `--no-lazy-fetch`: su ausencia permite crearlo localmente. `LocalGit.code` verifica primero el soporte
  mediante `run(--version)` con el mismo flag y ejecutable; Git sin soporte falla con diagnóstico, sin
  confundir el error con una respuesta booleana ni intentar otro modo.
- **Objetos necesarios.** Antes de capturar o escribir, la guardia comprueba los árboles completos de HEAD
  y de la vista previa/intención con `ls-tree` y `cat-file --batch-check`. Incluye árboles y blobs ajenos
  al ámbito documental; un objeto ausente o una respuesta incompleta bloquean con diagnóstico. No se
  ejecutan transportes, recuperan objetos ni modifican remotos/configuración para resolver la ausencia.
- **Compatibilidad.** `document_layout = "d088-12"` congela las reglas corregidas y pone composiciones
  anteriores, incluida `d088-11`, en cuarentena antes de efectos. No se reescriben intenciones, snapshots,
  historiales ni reproducciones/evidencia de H5/H7. Se conservan filtros del padre/includes, gitlinks,
  destinos ignorados, bytes exactos, D099, CAS, adopción atómica y la misma intención/run/commit al recuperar.
- **Alcance.** Regresiones con Git/SQLite temporales, agentes y transportes falsos, sin red ni proveedores
  reales. Sin esquema, API, UI, prompts o dependencias nuevos. Se mantiene la exclusión cooperativa:
  no añade aislamiento frente a cambios concurrentes arbitrarios del checkout o su configuración.

P008 sigue activa. Después corresponde otra revisión de salida; cierre y archivo separados.

## D113 — Quinta revisión de salida de P008

Estado: revisión completada el 2026-10-19 sobre `7568215`; criterios cumplidos offline. Fase: P008.
Evidencia, comprobaciones y límites en el [registro](archive/phase-008/P008_REVISION_SALIDA_5.md).

- H1–H6 conservan sus guardias. H7 queda resuelto en A/B: captura/sellado, ejecución y recuperación con
  puertos nuevos usan `--no-lazy-fetch` en ambas APIs Git. La ausencia normal del commit futuro permite
  crearlo localmente sin invocar el transporte falso; se mantienen la intención, run, commit y una sola
  fase adoptada. Los objetos necesarios ausentes bloquean sin alterar bytes; restituirlos permite continuar.
- Git sin soporte falla con diagnóstico en `run` y `code`, sin fallback. Las regresiones cubren además
  caídas parciales y posteriores al commit/antes de adopción, D099, CAS, originales/binarios y cuarentena.
  Los siete criterios de ROADMAP se cumplen en el alcance offline; no aparecen nuevos bloqueos.
- Esta revisión solo añade registro, script y JSON de evidencia y actualiza la continuidad documental.
  Los resúmenes activos de las revisiones primera/tercera se compactan con enlaces para respetar el
  presupuesto de STATE. ADR anteriores, snapshots, intenciones y evidencia histórica permanecen intactos.
- P008 sigue activa hasta el cierre y archivo documental en una tarea separada. No se registra ni ejecuta
  un check READY del producto sobre este repositorio; no se inventa sucesora, ni se amplían consentimientos
  de proveedores, smokes, push o publicación. Se conservan los límites de contención cooperativa y QA visual.

## D114 — Cierre documental manual de P008

Estado: cerrada y archivada el 2026-10-19 por la continuación solicitada por el usuario, tras D113. Fase: P008.
[Resumen](archive/phase-008/SUMMARY.md), [revisión](archive/phase-008/REVIEW.md) y
[registro de cierre](archive/phase-008/P008_CIERRE.md).

- Las veinte tareas de P008 y sus siete criterios de salida están cumplidos en el alcance offline de D113,
  sobre el código `7568215`; la revisión y sus evidencias quedaron en `9c88879`. No se amplían sus garantías
  a UI visual, generación semántica real, Django/ruff/mypy reales o recorridos con proveedores reales.
- El usuario pide continuar con la siguiente tarea y hacer commit, que STATE/NEXT_STEPS identifican como
  cierre y archivo documental. Se completa manualmente bajo D002/D088, sin registrar ni ejecutar el harness
  sobre este repositorio, check READY, SQLite, agentes o proveedores. No se crea tag de fase: este cierre
  manual se acredita con su commit y el HEAD de origen del manifiesto; no simula el protocolo gestionado.
- `archive/phase-008/` conserva STATE, NEXT_STEPS y los 33 artefactos originales de `docs/phase/` por bytes.
  El manifiesto recoge rutas de origen/destino, tamaños y SHA-256; REVIEW y SUMMARY nuevos identifican el
  dictamen y el alcance del cierre. Los enlaces y comandos internos de los originales conservan su contexto
  histórico; los scripts se reproducen en su commit de origen. No se reescriben snapshots, scripts ni JSON.
- Los enlaces vigentes de DECISIONS y README se actualizan al archivo, sin cambiar decisiones anteriores.
  ROADMAP conserva objetivo y criterios de P008 y enlaza su archivo. STATE incorpora la base de P008 y
  NEXT_STEPS queda sin tareas; `docs/phase/` vacía. Sin sucesora en ROADMAP, no se inventa P009.
- La próxima prioridad corresponde al usuario; las candidatas y límites quedan en ROADMAP. Se mantienen
  las restricciones de desarrollo manual y los consentimientos agotados de proveedores/smokes. Sin push,
  publicación, cambios de configuración global, esquema, API o código del producto.

## D115 — P009: Django desde cero, carpeta de proyectos y agentes por proyecto

Estado: fase planificada el 2026-10-19 por petición del usuario; pendiente de implementación y piloto. Fase: P009.
[Plan](archive/phase-009/P009_PLAN_DJANGO.md) y [tareas](archive/phase-009/NEXT_STEPS.md). Amplía D049/D078/D082; conserva la asignación de D052.

- Nueva sección de UI «Elegir carpeta de proyectos». La elección explícita del usuario concede al servicio la
  creación de proyectos hijos en esa raíz y se conserva entre reinicios; no la elige la IA, ni se deduce de HOME,
  del cwd, de otros proyectos o de un prompt. `$HOME/Documents/projects/` es el ejemplo del usuario;
  cada instalación puede elegir otra ubicación. La aplicación no modifica permisos del sistema operativo.
- Ese permiso de carpeta cubre nuevas creaciones dentro de su alcance, sin repetirlo para cada hijo. El usuario
  indica el nombre y ve el destino exacto antes de crear. No autoriza modificar proyectos hermanos, sobrescribir
  destinos, instalar dependencias, usar red o llamar proveedores fuera de la operación confirmada. El ejecutor
  solo recibe la raíz del proyecto hijo. La elección no implica confiar en repositorios ya existentes.
- La UI guardará la elección como configuración operativa local auditada, sin editar el TOML ni la configuración
  global del usuario. T001 concretará persistencia, contratos, convivencia con las raíces explícitas del TOML,
  revocación y recuperación; las autoridades antiguas no se amplían ni sustituyen silenciosamente.
- Creación desde cero mediante carpeta hija nueva, definición/documentos D088 y receta técnica Django confirmada.
  Se evita exigir un scaffold o entorno manual, y se conserva el bootstrap documental existente. Las operaciones
  de instalación y creación de archivos protegidos tienen alcance propio; no se abren al ejecutor de tareas.
- Proveedores seleccionables por proyecto desde presets autorizados del servicio, también al cambiar entre tareas.
  El usuario fija proveedor/modelo/esfuerzo del revisor y proveedor/catálogo admisible del ejecutor. El revisor
  elige modelo y esfuerzo concretos del ejecutor por tarea/revisión, con motivo. Se usa planificación por agente.
  El servidor sigue fijando ejecutables, entornos, credenciales y versiones admitidas; no los suministra el cliente.
- Piloto en un único proyecto Django pequeño: lista de tareas, SQLite y plantillas. Cuatro tareas incrementales
  COMMITTED, en orden revisor→ejecutor: Codex→Codex, Codex→Claude, Claude→Claude y Claude→Codex. Los cambios de
  selección son por proyecto, entre tareas terminadas; no alteran intentos anteriores ni jobs en curso.
- P009-T001–T005 preparan producto y ensayo offline; T006 fija ruta/nombre, modelos/esfuerzos del revisor,
  catálogos del ejecutor, comandos, versiones y límites de la operación real. T007–T012 ejecutarán el piloto
  solo tras ese consentimiento específico. La petición actual autoriza redactar la fase, no ejecutar proveedores,
  instalaciones, red, servicios o el harness sobre este repositorio. No cambia ningún archivo fuera del checkout.

Todo lo anterior está planificado. No se cambia en esta tarea código, esquema, configuración real, contratos o
versiones congeladas. Los modelos de datos y los flujos vigentes conservan sus diagramas; el flujo futuro se
identifica expresamente como diseño pendiente. P008 y su archivo permanecen intactos.

## D116 — P009-T001: autoridad de creación, presets por proyecto y preparación separada

Estado: diseño completado el 2026-10-19; implementación pendiente de P009-T002–T004. Fase: P009.
[Contrato, esquema propuesto, API y pruebas](archive/phase-009/P009-T001_CONTRATO_CREACION.md).
Concreta D115 tras contrastar D049/D051/D052/D078/D095 y los consumidores del registro, composición y bootstrap.

- Una selección de carpeta UI por instalación, inicialmente ausente, persistida en SQLite con revisión, identidad
  filesystem y eventos append-only. Es autoridad solo para hijos nuevos; no amplía `[registration].roots`, que
  conserva el alta de checkouts existentes. La carpeta UI puede estar fuera de esas raíces. Funciona en formatos
  registrables v3/v4 y futura v5; no eleva el techo de bootstrap del operador ni edita TOML/configuración global.
- Guardar/cambiar/retirar se confirma por preview/CAS y ruta exacta. Retirada invalida creaciones aún pendientes
  antes de nuevos efectos; no retira hijos ya registrados, borra archivos ni cambia sus hashes. Reelección de la
  misma ruta no revive intenciones antiguas. Reanudación requiere nueva autorización y propiedad acreditada.
- Cada creación reserva id/destino y sella intención antes de `mkdir`. Nombre de un componente y destino nuevo,
  incluso frente a carpetas vacías, con identidad/guardias de enlaces y conflictos. Alta D078, evento, procedencia
  y resultado de creación se confirman atómicamente. Repetir devuelve la misma operación; una caída entre mkdir
  y persistir identidad queda incierta, sin adoptar por vacío ni borrar a ciegas. Sin marcador nuevo en el hijo.
- Se reserva `local-config-5` para presets `[agent_presets.*]`, selección por proyecto y preparación. Las ramas
  v1–v4 conservan sus hashes y rechazan claves nuevas. Fila sin override conserva agentes globales; el registro
  v5 guarda selección en su fila/eventos existentes. Proyectos TOML siguen en consulta en UI. Presets contienen
  ejecutables/entornos/capacidades del operador; el cliente solo selecciona ids, modelo/esfuerzo del revisor y
  política/catálogos del ejecutor. `ports` compondrá ambos agentes por checkout, sin pareja global mutable.
- Cambio de roles confirmado por versión/hash y sin trabajo utilizable pendiente: jobs/locks, preparación,
  aceptación/commit o planificación anterior incompatible bloquean o se invalidan antes de efectos según el
  contrato. Catálogos/esfuerzos se validan por proveedor/preset, sin fallback. D052 conserva la decisión concreta
  y motivo del ejecutor en el revisor por tarea/revisión. Snapshots anteriores intactos.
- Orden: hijo → definición/commit documental → receta/commit técnico → tareas. V5 permite enlaces tipados a
  ejecutables del entorno aún no creado; definición y bootstrap no ejecutan checks irresolubles. Hasta preparar,
  se bloquean tareas/comandos/checks que los necesiten. El recibo de entorno habilita su resolución controlada.
- Receta Django empaquetada, con plan materializado confirmado de archivos/hashes, comandos exactos, versiones,
  entorno, red/cache y límites. Tiene escritor propio para configuración protegida, sin excepción para ejecutores
  ni borradores documentales. Intención/pasos/lease/lock y registro de procesos, conciliación de commit y adopción
  atómica; un efecto de instalación/red incierto no se reintenta implícitamente. Django sigue fuera del runtime.
  La preparación tendrá journal propio y propietario explícito en locks/procesos compartidos: las FK actuales a
  jobs/runs no se pueden reutilizar sin ampliación. Su binding `preparation-commands-1` será independiente del
  binding actual de `commands-1`. Admisión, recuperación y lectores/backup cubrirán ambos propietarios.
- Los contratos nuevos de creación/preparación se versionan por separado. V5 congela presets efectivos y recibo
  en la composición; no exige cambiar formas `cli-12`, `commands-1`, codec 7 o layout `d088-12`. Si la implementación
  necesitase cambiar alguna forma real, deberá versionarla. Tablas/migraciones/API/tipos se incorporan en T002–T004
  con paridad; el diagrama vigente conserva solo entidades implementadas.

T004 concretará versiones/lock/instalador; T006 recogerá selecciones y consentimiento real. Esta decisión no fija
modelos/esfuerzos, rutas operativas, permisos de red/instalación o llamadas de proveedor. Sin ejecución del piloto.


## D117 — P009-T002: carpeta persistente y creación con intención previa

Estado: implementado el 2026-10-19, verificación offline y QA con respuestas sintéticas. Fase: P009.
[Entrega y límites](archive/phase-009/P009-T002_CARPETA_PROYECTOS.md). Aplica D116 §§2–3/6–9; conserva D078/D095.

- Raíz UI singleton inicialmente ausente, revisiones y eventos persistentes; selección/retirada por preview,
  CAS, clave idempotente y ruta canónica exacta. Sin HOME/cwd/raíz predeterminada, exploración de disco, cambios
  de TOML, chmod o confianza global. Disponible con configuración registrable v3/v4 y `roots = []`; el techo
  `bootstrap_enabled` sigue vigente. Las raíces TOML conservan únicamente el alta existente.
- Creación síncrona de efectos cortos: intención y reservas antes de mkdir, fd del padre sin seguir enlaces,
  identidad y fsync antes del checkpoint; alta/evento/procedencia/resultado en una transacción. Lock reentrante
  compartido con registro y transacciones de escritura SQLite serializan contra la retirada, también entre
  instancias. Conflictos por ancestros/identidades físicos incluyen alias de mayúsculas y reservas sin carpeta,
  sin confiar solo en la comparación textual de rutas. No añade jobs, ejecutores ni Git a la creación. Tras REGISTERED enlaza a la definición existente.
- Las intenciones `project-creation-1` congelan autoridad, composición completa por hashes, versiones, perfil,
  política, roles efectivos y confianza exacta. Liga además el hash del perfil completo, también en v3,
  sin cambiar los hashes históricos del registro. La preview valida comandos/contexto sobre el padre existente
  y calcula hashes para el destino futuro; devuelve solo datos. La composición operativa sigue exigiendo directorio existente.
  Formatos/hashes previos, CLI, commands, codec y layout se conservan.
- Una carpeta sin identidad persistida queda incierta; reiniciar solo clasifica, nunca adopta por vacío,
  borra ni reintenta. Retirada bloquea efectos pendientes y conserva hijos registrados. Reanudar exige preview
  nueva, misma identidad, hijo vacío acreditado y composición original vigente; añade autoridad/evento sin
  reescribir la intención. Sin prueba de propiedad requiere resolución externa. Cancelar conserva bytes y
  reserva salvo ausencia acreditada; tras resolución externa, otra comprobación versionada de cancelación
  puede liberar la reserva sin reabrir efectos. El alta D078 tampoco puede adoptar una reserva incierta.
- Migración aditiva `0021_project_creation`: cuatro tablas y `registered_projects.creation_id` nullable con
  FK/índice único, fuera del JSON/hash de fila v3/v4. ALTER ADD COLUMN evita reconstruir la tabla referenciada
  por auditoría previa con foreign_keys activas. Downgrade rechaza pérdida de autoridad/historia nueva.
  Backup incluye estas tablas; restauración permanece de consulta.
- UI «Nuevo proyecto» con autoridades diferenciadas, destino absoluto, confianza del checkout, historial,
  reanudación y cancelación. Conserva sobre/clave de confirmación en sesión ante pérdida de respuesta o 401;
  tras recargar el reenvío es explícito. Entradas estrictas, sesión/CSRF/origen y OpenAPI/tipos actualizados.

No implementa presets v5, scaffold/entorno Django ni receta, ni ejecuta proveedores/piloto. T003 es la siguiente
entrega; T006 conserva la puerta de consentimiento real. Fixtures y QA no conceden una carpeta real al servicio.

## D118 — P009-T003: presets v5 y selección de agentes por proyecto

Estado: implementado y verificado offline el 2026-10-19. Fase: P009.
[Entrega y verificaciones](archive/phase-009/P009-T003_AGENTES_PROYECTO.md), [flujo](flows/project-agents.md).
Aplica D116 §4; conserva D049/D052/D078/D095 y la separación de preparación de T004.

- `local-config-5` optativa conserva claves v4 y admite `[agent_presets.<id>]`: CLI privada, proveedor/roles,
  catálogo local de modelos, esfuerzos del proveedor y permiso explícito de modo libre. Sin consulta remota
  ni procesos al cargar; validación de USER, herramientas de lectura fijas y versión caracterizada por rol.
  V1–v4 rechazan claves nuevas y mantienen sus hashes. Sin override se hereda la pareja/política actual.
- Registro y `[[projects]]` v5 admiten `agent_selection`: revisor con preset/modelo/esfuerzo; ejecutor solo preset.
  Catálogo/modo siguen en `policy`. UI editable solo para registros, en alta/creación/Ajustes; no preselecciona
  modelo/esfuerzo al cambiar preset. El catálogo público omite ejecutables y valores de entorno. Configuración
  ausente/incompatible se diagnostica sin fallback; no se escribe el TOML ni configuración global.
- Agentes efectivos guardados por checkout junto a comandos/artefactos; `ports` crea adaptadores por job con
  ellos, sin mutar los defaults ni otros proyectos. Vistas muestran los proveedores efectivos. Preflight
  explícito cubre la pareja heredada y todos los roles de los presets. El revisor decide modelo/esfuerzo/motivo
  del ejecutor por tarea/revisión y se valida antes de invocarlo; codec 7 y cli-12 sin cambios.
- JSON de fila/eventos D078, sin tablas/columnas ni migración. Preview/hash incluye selección y contenido de
  ambos presets; CAS/replay conserva una sola versión. V5 congela también id/hash de fila; historial anterior
  intacto. Deriva de capacidades mantiene cuarentena por composición; preset retirado deja fila no disponible.
- Cambios/bajas v5 exigen ausencia de jobs/locks, aceptación/commit pendiente, propuestas de chat sin resolver,
  definición/importación con turnos utilizables y operaciones documentales incompletas. Planes de fase PROPOSED
  se invalidan atómicamente como SUPERSEDED con decisión auditada, sin editar snapshots/contenido/hash. Requieren
  nueva planificación. Entidades y exclusión de preparación siguen pendientes de T004.
- Admisión, reanudación y commit comprueban la versión activa bajo la misma transacción SQLite que el cambio
  de registro. Un job anterior impide cambiar; petición posterior con contexto obsoleto se rechaza sin encolar.
  Los puertos congelados siguen comprobando la composición antes de efectos. La UI actualiza su lectura de
  agentes inmediatamente después de guardar.

Sin operación con proveedores reales ni consentimiento del piloto. Receta Django, enlaces diferidos al entorno,
preparación y su journal/locks siguen en T004; esta entrega no acepta aún esas claves de v5.


## D119 — P009-T004: receta Django confirmada y entorno acreditado

Estado: implementado el 2026-10-19, pruebas con herramientas sintéticas; herramientas Django reales en T005.
Fase: P009. [Entrega](archive/phase-009/P009-T004_RECETA_DJANGO.md), [flujo](flows/project-preparation.md). Aplica D116 §5–9,
sin ampliar el consentimiento de instalación/proveedores/piloto.

- V5 admite `[recipes.django]`, composición `recipe="django"`, perfil empaquetado `python-django-recipe` y
  enlaces exactos `project_venv` de python/pytest/ruff/mypy. Crear/definir/commit documental no exige `.venv`.
  Solo el hijo nuevo con procedencia de creación y commit raíz documental aceptado puede preparar esta receta.
  Perfiles Django declarados con rutas absolutas y v1–v4 conservan su comportamiento/hashes.
- Implementación empaquetada `django-recipe-1`; el hash de composición incluye configuración y bytes/manifest
  del productor. Preview de solo lectura: contenido/hashes íntegros, templates, lock, versiones, HEAD, identidad,
  ejecutables acreditados por hash, argv, entorno público, límites por paso, red/cache y commit previsto. Confirmar
  liga ese plan por CAS/hash/clave; ninguna entrada admite comandos o archivos libres.
- CPython 3.11–3.13 de patch explícito; uv del operador con versión exacta. Dependencias directas/transitivas
  fijadas con hashes de wheels publicados: Django 5.2.17, pytest 9.0.3, pytest-django 4.11.1, ruff 0.14.1,
  mypy 1.18.2, django-stubs/ext 5.2.7 y cierre completo del lock empaquetado. No entran en las dependencias
  del harness. La compatibilidad publicada guía esta selección; T005 acreditará su ejecución real.
- Ambos roles/presets efectivos deben declarar `PYTHONDONTWRITEBYTECODE=1` para que comandos Python de agentes
  no alteren incidentalmente el entorno acreditado. Se rechaza la incompatibilidad; no se reescribe su entorno
  ni la configuración global. Los validadores nativos llevan esa política dentro de la composición de receta.
- Venv sin pip, instalación uv con hashes, sin dependencias implícitas, builds, configuración descubierta,
  descargas de Python o retry HTTP. Offline usa wheelhouse opcional explícito o caché privada; vacío falla sin
  red. Network requiere techo del operador y aceptación del plan. HOME/cache/tmp quedan dentro del hijo.
- startproject/startapp usan templates propios en staging y su salida exacta se compara antes de publicar.
  Proyecto/app, templates/static, pytest/JUnit, ruff check/format, mypy estricto con stubs/plugin y checks Django;
  sin modelo Task. Secreto aleatorio y SQLite solo locales/ignorados, sin bytes secretos en el plan/commit.
  La receta escribe configuración protegida; un ejecutor normal sigue sin poder hacerlo.
- Migración `0022_project_preparation`, 42 tablas: operaciones/pasos/eventos y propietarios exclusivos
  job/preparación en locks/procesos compartidos. Migración conserva FK/datos/id de procesos previos, sin apagar
  FKs. Intención/reserva/lock se sellan antes de efectos; lease/propietario y grupo antes de GO. Binding nuevo
  `preparation-commands-1`; `commands-1`, CLI, codec y snapshots históricos conservan sus formas.
- El worker del carril escritor procesa preparaciones; consulta/polling no ejecutan herramientas. Caída/lease
  o error detienen, conservando evidencia. Cancelación usa handle propio y acredita muerte del grupo; recuperación
  nunca señala PIDs persistidos. Nueva intención enlazada confirma primer paso no acreditado; prefijo DONE
  conserva evidencia. Archivos iniciales parciales, entorno incierto o deriva frente al último prefijo bloquean;
  no hay borrado/recreación/reinstalación automática ni adopción de bytes ajenos.
- Commit técnico determinista con intención previa y blobs/árbol/HEAD exactos. Una caída antes de adopción
  concilia el mismo commit sin repetir herramientas. COMPLETED/recibo/liberación se adoptan juntos; jobs
  posteriores congelan `project_environment_sha256`. Identidad, entorno completo y archivos protegidos se
  verifican antes de tareas/checks y de cada comando. Cambios de roles conservan recibo compatible.
- Admisión/registro/preparación comparten exclusión SQLite; una reserva pendiente/incierta bloquea jobs,
  cambios de composición y baja. Lectores de procesos, backup/restauración de consulta y retención reconocen
  preparación; capturas/journal permanecen inline en SQLite. Sin runs ficticios ni otra cola de agentes.

No se instala Django ni se ejecutan sus herramientas reales en T004. Solo se consultan metadatos públicos de
versiones/hashes; paquetes, red de instalación y piloto mantienen su propuesta/consentimiento propios.

## D120 — P009-T005: ensayo temporal con CLI falsas y Django real

Estado: verificado el 2026-10-19. Fase: P009.
[Entrega, reproducción y límites](archive/phase-009/P009-T005_ENSAYO_DJANGO.md). Aplica D116/D119, sin cambiar sus contratos.

- Ensayo por la API con sesión real, Git/SQLite temporales y los adaptadores CLI de producto conectados solo
  a procesos falsos. Un único hijo recorre raíz → creación/registro → definición D088/commit → receta/commit →
  cuatro tareas COMMITTED (Codex→Codex, Codex→Claude, Claude→Claude, Claude→Codex) → check/cierre, tag y archivo.
  Incrementos sintéticos de plantilla; no se adelanta el CRUD ni se presenta como piloto con modelos.
- Reinicios y reenvíos conservan carpeta/id/intenciones/commits. Los cambios de roles preservan el recibo del
  entorno y todos los historiales/configuraciones anteriores. El revisor falso selecciona modelo/esfuerzo y
  motivo del ejecutor; los specs de los procesos acreditan la pareja usada y el cwd hijo.
- Fallo inyectado tras el commit técnico y antes de adoptar el recibo: reiniciar no repite herramientas. Una
  nueva intención confirmada enlaza la fallida y concilia el mismo hash, sin nuevos procesos de preparación;
  conserva plan/pasos originales y añade el evento de sucesión, sin reescribir esa evidencia.
- El usuario autoriza específicamente en esta sesión descargar de PyPI los 17 wheels fijados y verificarlos
  contra el lock, para entornos temporales con Python 3.13.13 y uv 0.12.19 ya instalados. La receta se ejecuta
  después offline, sin modificar configuraciones globales ni dependencias del harness. Versiones/hashes
  públicos en el [recibo saneado](archive/phase-009/P009-T005_WHEELS.json).
- La prueba tiene variante sintética ordinaria y variante real optativa: exige rutas explícitas de Python y
  wheelhouse; ausencia de ambas omite solo la variante real y no descarga nada. La receta intacta pasa pytest/JUnit,
  ruff check/format, mypy estricto con stubs/plugin, migrate, check y makemigrations --check.

La evidencia real corresponde a macOS arm64 y CPython 3.13.13; no certifica toda la matriz Python/plataformas.
T006 conserva propuesta y consentimiento del wheel operativo, servicios y proveedores. Este consentimiento
temporal de paquetes no inicia ni autoriza el piloto; los consentimientos históricos de proveedores siguen agotados.

## D121 — P009-T006: propuesta del piloto y caracterización previa de CLI

Estado: propuesta preparada y **autorizada por el usuario el 2026-10-20** («Autorizo la propuesta completa»);
sin ejecutar. Fase: P009. [Propuesta, selecciones, límites y parada](archive/phase-009/P009-T006_PROPUESTA_PILOTO.md).
Concreta D115 para la operación real; aplica D050/D051/D052/D119. No reutiliza consentimientos de D050/D071.

- Las CLI instaladas, Codex 0.163.0 y Claude 2.1.304, están fuera del baseline (`SUPPORTED`: Codex 0.161.0/0.162.1,
  escritura solo 0.162.1; Claude 2.1.295/2.1.296) y no queda ninguna versión caracterizada en disco. El usuario
  elige caracterizarlas en una tarea de producto previa, P009-T013, que se ejecuta antes de T007. No se instalan
  versiones antiguas ni se cambian enlaces globales. Se fijan el binario nativo de Codex y el binario versionado
  de Claude por ruta y SHA-256; cualquier cambio de hash detiene el piloto.
- T013 se numera tras T012 para no renumerar las referencias de D115–D120 y del plan; su orden de ejecución
  lo fija la dependencia de T007. El wheel operativo se construye después de T013, porque debe incluir el baseline
  nuevo; instalarlo en T006 habría dejado un paquete obsoleto.
- Selecciones del usuario: raíz `$HOME/Documents/projects/`, hijo `harness-django-pilot`, área persistente
  `$HOME/.local/share/harness-local/`, revisor Codex `gpt-6-luna`/`medium`, revisor Claude
  `claude-sonnet-5-5`/`medium`. Ejecutor en modo catálogo: Codex `gpt-6-luna` y Claude `claude-sonnet-5-5`/`claude-opus-5-5`,
  con esfuerzos {low, medium, high}. Wheelhouse offline previo con los 17 wheels del lock, `max_revision_cycles = 2`,
  timeouts de 1800/3600 s. El revisor sigue eligiendo modelo/esfuerzo y motivo del ejecutor (D052).
- Detalles reversibles fijados con criterio: subcarpetas del área, puertos 8031 (servicio) y 8032 (runserver de QA),
  `supervisor = true`, autor Git con la identidad del usuario y tags `lightweight`, timeout de la receta de 600 s.
- Techo de 60 invocaciones de proveedor (máximo previsto: 50; definición ≤20 turnos, 7 por tarea y 2 de cierre).
  Para al primer fallo, sin retry/fallback/cambio de proveedor; corregir no autoriza a repetir consumo. Red solo
  para PyPI (17 wheels) y el tráfico propio de las CLI. Si T013 necesitara invocar un modelo para caracterizar la
  escritura de Codex, se detiene y pide autorización aparte.

T006 no instala, crea ni ejecuta nada: solo lee versiones, enlaces, hashes, destino y puertos. Sin cambios de
código, esquema, API, versiones congeladas ni diagramas.

## D122 — P009-T013: Codex 0.163.0 y Claude 2.1.304 en el baseline `cli-12`

Estado: implementado y verificado offline el 2026-10-20. Fase: P009.
[Sondas, fuente, pruebas y límites](archive/phase-009/P009-T013_CARACTERIZACION_CLI.md). Dentro del consentimiento de D121 (§§1, 6).
Amplía D052/D068 sin cambiar argv, protocolo, salidas ni controles de D059/D066/D068 o cli-11.

- Sondas reales solo de `--version`, `exec --help`/`--help` sobre los binarios fijados por hash, con entorno
  explícito y cwd temporal; ninguna llamada a modelos. Versiones con el formato reconocido y todos los flags
  requeridos y usados presentes. Las ayudas de `exec` y de Claude quedan como fixtures públicas de regresión.
- Codex: `rust-v0.163.0` resuelve al commit `83086188…`, embebido en el nativo. La comparación con la fuente del pin
  anterior en lectura deja idénticos la guardia de confianza de `thread/start`, el parser de overrides, la CLI y los
  eventos JSONL de `exec`, `ReasoningEffort`, las estructuras de memoria/historial/sandbox y la carga de AGENTS.md.
  Los cambios del cargador y de permisos no afectan a las claves ni al modo de aprobación del transporte. Por eso
  0.163.0 se admite también como escritor, con la misma supresión de confianza.
- Claude: ayuda y literales de 2.1.304 conservan flags, semántica de `--restricted`, vocabulario de esfuerzo,
  controles de memoria/hooks y los terminales `result` del parser. La ayuda de 2.1.296 ya no está en disco para
  compararla byte a byte; queda como límite, junto a los eventos de cambio de modelo, visibles en `message_models`.
- Se mantiene `cli-12`: la forma de la invocación no cambia y la versión de cada CLI ya forma parte de la identidad
  congelada por rol. Versiones anteriores admitidas; las no caracterizadas (Claude 2.1.299–2.1.301 en disco, entre
  otras) se siguen rechazando. Ejemplo de configuración al día; scripts históricos de ejemplos sin tocar.

30 pruebas nuevas: baseline, vecinos rechazados, argv idéntico por rol/proveedor, preflight con las ayudas reales
y las cuatro parejas por el adaptador real. Suite offline completa: 1.577 tests y 121 subtests correctos, una omisión
esperada (variante Django real sin wheelhouse). Sin observación en ejecución: el piloto acreditará los efectos reales.

## D123 — P009-T007: detenida; Codex rechaza la definición en un hijo sin Git

Estado: observado el 2026-10-20 y piloto detenido. Fase: P009. Dentro del consentimiento de D121 (§§3–5).
[Evidencia saneada, causa y consumo](archive/phase-009/P009-T007_CREACION_DJANGO.md).

- Preparación correcta fuera de los checkouts: wheel de `21871a0`, venv offline por hashes, 17 wheels verificados
  contra el lock, TOML v5, preflight `version_help_match` en los seis roles/presets e `init-db`. Desde la UI:
  carpeta de proyectos guardada, hijo `harness-django-pilot` creado y registrado con revisor Codex
  `gpt-6-luna`/`medium` y ejecutor Codex en catálogo, brief y primer mensaje de la definición.
- El primer turno `definition` falla en 302 ms sin llegar al modelo: Codex 0.163.0 exige `--skip-git-repo-check`
  fuera de un repositorio, y `cli-12` solo lo pasa a raíces exportadas (D083/D102). Un hijo nuevo no tiene `.git`
  hasta el commit raíz. Las CLI falsas de T005 no reproducían esa comprobación. Es un defecto del producto, no del entorno.
- Parada según D121 §5: sin reintento, sin cambiar de proveedor ni tocar TOML/SQLite. Consumo: una invocación lanzada,
  cero tokens. Servicio detenido y sin procesos; área e hijo vacío conservados. P009-T014 corrige el transporte.
  Reanudar T007 exige wheel nuevo, propuesta al día si cambia el adaptador y autorización nueva del usuario.
- `check_distribution.py` conserva un tramo de bootstrap v1 retirado y falla con 405 después de verificar el contenido,
  el arranque y la sesión del wheel. El usuario decide continuar con esa verificación parcial y exige corregirlo
  antes de cerrar P009 (P009-T015).
- Detalles operativos fijados con criterio: `serve` con `TMPDIR` dentro del área, para que la clave de sesión no salga
  del área; sin `home-commands/`, porque la composición de la receta exige un entorno vacío (D119).

## D124 — P009-T014: `cli-13`, Codex define un proyecto nuevo fuera de Git

Estado: implementado y verificado offline el 2026-10-20. Fase: P009. Corrige el defecto de D123; amplía D083/D102.
[Criterio, versión, CLI falsa y verificación](archive/phase-009/P009-T014_DEFINICION_SIN_GIT.md).

- Codex recibe `--skip-git-repo-check` en el rol `definition` cuando el snapshot congelado del prompt es la
  plantilla `define-project`, es decir, la definición D088 de una carpeta nueva, además de las exportaciones
  de D083/D102. La condición sale de la petición congelada, no del disco al lanzar. Una definición D088 nunca
  apunta a Git: el turno se rechaza al encolar si el destino pertenece a un repositorio, y falla antes de invocar
  si aparece `.git` después. Importación sobre checkout vivo, demás roles, ejecutor y Claude conservan su argv.
- El flag solo salta la comprobación de arranque de Codex. Sandbox `read-only`, memoria desactivada,
  `project_doc_max_bytes=0` y la falta de override de confianza no cambian. La guardia de `thread/start` (D068/D122)
  solo persiste confianza con permisos que escriben el cwd, y el revisor no los tiene.
- Adaptador `cli-13`: el argv cambia para una clase de peticiones (regla de D052; precedente D102). Los jobs
  congelados con `cli-12` y aún no reclamados quedan en `RECOVERY_REQUIRED` antes del preflight, por la comparación
  de versiones existente. Runs, snapshots y métricas anteriores conservan `cli-12`. Sin cambios de esquema, API,
  codec, layout, `local-config` ni baseline de CLI.
- La CLI falsa de las pruebas rechaza siempre, como el pin, un `exec` fuera de cualquier repositorio sin el flag.
  Con `cli-12` falla el ensayo sintético de T005, que es el caso de T007. Otros 25 tests usaban checkouts sin Git;
  la fixture compartida pasa a ser un repositorio, sin tocar el adaptador.
- Una conversación de definición con un turno `FAILED` admite un turno nuevo (cada turno es su propio run y congela
  sus versiones). La reanudación de T007 reutiliza hijo, registro y conversación. La propuesta de T006 se actualiza
  (§8). Reanudar exige wheel nuevo y autorización nueva del usuario; Codex real con el flag queda para el piloto.

## D125 — P009-T016: suite pytest en paralelo y Git sin fork

Estado: implementado y verificado offline el 2026-10-20. Fase: P009. Autorizado por el usuario punto por punto.
[Diagnóstico, cambios, matrices recortadas y medidas](archive/phase-009/P009-T016_SUITE_RAPIDA.md).

- La suite pytest se ejecuta en paralelo por defecto con pytest-xdist 3.8.0 (`-n auto --dist worksteal` en
  `pyproject.toml`); `-n 0` la ejecuta en serie. El mismo comando de AGENTS.md sigue siendo el de referencia.
- Pruebas: en macOS la sesión evita el shim `xcrun` de `/usr/bin/git` con un prefijo temporal enlazado al Git real.
  `migrated_database` copia una plantilla migrada una vez por sesión. Los tests A/B montan solo el mundo de su flujo.
- Matrices: se elimina una combinación solo si cada eje sigue cubierto (producto completo en otra prueba más barata
  o cada valor presente al menos una vez), con el precedente del muestreo diagonal de filtros. Puntos de crash,
  orígenes, pasos de cierre y etapas no se recortan. 16 combinaciones menos.
- Adaptador Git, sin cambiar árboles, commits, errores ni mensajes: `_tree_with` lista el árbol una vez y agrupa
  `update-index` consecutivos (`hash-object` sigue por ruta por los atributos), `bootstrap._tree` hace un único
  `hash-object --no-filters --stdin-paths`, `capture` resuelve el índice una vez y `LocalGit.code()` comprueba
  `--no-lazy-fetch` una vez por instancia.
- `Git.run/code` lanzan `git -C <raíz>` con ruta absoluta y `close_fds=False` para que `subprocess` use
  `posix_spawn` en lugar de `fork`. Es seguro porque los descriptores del proceso no son heredables (PEP 446,
  `O_CLOEXEC` en SQLite). Un directorio inaccesible sigue siendo un `GitError` de lanzamiento, nunca un código de
  salida. Un ejecutable no resoluble a ruta absoluta usa el camino anterior. Si un cambio futuro marca descriptores
  como heredables, debe revisar esta decisión.
- Resultado en la máquina de desarrollo: de más de 25 minutos a unos 4:20 con 10 workers. Sin cambios de esquema,
  API, versiones congeladas ni contratos de agentes.

## D126 — P009-T015: el wheel se verifica con la definición D088

Estado: implementado y verificado offline el 2026-10-20. Fase: P009. Cierra el hallazgo §5 de
[T007](archive/phase-009/P009-T007_CREACION_DJANGO.md#5-verificación-del-wheel-incompleta) (D123);
[entrega](archive/phase-009/P009-T015_VERIFICACION_WHEEL.md).

- `scripts/check_distribution.py` sustituye el tramo de bootstrap v1 (retirado en D089/D093) por el recorrido HTTP
  vigente: conversación `definition`, un turno con agente sintético, aplicación confirmada de los borradores, vista
  previa lista, aceptación sin confirmar rechazada sin `.git`, aceptación con commit raíz e idempotencia tras reinicio.
  La primera tarea sale del `task_text` de esa vista previa. Se conservan contenido del wheel, sesión, UI/assets,
  simulación, reinicio, errores de configuración y esquema, backup y restauración de consulta sin el checkout.
- El fixture `tests/fixtures/e2e/installed_config.py` pasa a `offline-installed-v2`: contexto `documents = "v2"`,
  perfil sintético con validación `test-runner check` resuelta por `ScriptedCommandRunner` y un agente que responde
  a `definition`, `executor` y `reviewer`. Sigue siendo un módulo aislado, copiado junto al wheel, sin proveedores.
- El script lanza el servicio con `TMPDIR` dentro de su directorio temporal y comprueba que la clave de sesión queda
  allí. ARCHITECTURE §9 documenta que `serve` usa `TMPDIR` para la clave y los temporales de Git.
- Sin cambios de producto, esquema, API ni versiones congeladas. El fixture no tiene una prueba pytest propia: el
  script es su única comprobación y se ejecuta al construir un wheel (D051).

## D127 — P009-T007: completada; Django creado desde la UI con revisor Codex

Estado: completada el 2026-10-21. Fase: P009. Reanuda D123 con autorización nueva del usuario, dentro de D121 §§3–6
y de la propuesta §8. [Evidencia saneada](archive/phase-009/P009-T007_CREACION_DJANGO.md#7-reanudación-y-cierre-de-t007-2026-10-21).

- Wheel de `1f8aa7a` (`cli-13`), verificado entero con `check_distribution.py` (D126) e instalado offline en el
  venv del área; preflight correcto en los seis roles. Se reutilizan el área, la SQLite, el hijo y su conversación.
- La definición se completa en los turnos 2 y 3 con Codex `gpt-6-luna`/`medium`. Commit raíz `9b612ca` desde la UI,
  receta offline `django-recipe-1` y commit técnico `d762e77`; portada y estáticos responden en loopback. Consumo:
  3 de 20 invocaciones de T007, 3 de 60 del piloto. Sin edición manual del scaffold.
- Hallazgo: la plantilla `define-project` pide conservar los marcadores gestionados «donde los borradores los
  tienen», pero no dice que en una carpeta nueva son opcionales. Codex 0.163.0 respondió con una pregunta bloqueante en
  lugar de redactar. El usuario decidió contestarla en la conversación (turno 3), que es el uso previsto, en lugar de
  parar; queda como corrección propuesta para la plantilla, sin implementar.
- Hallazgo: el ROADMAP del revisor no declaraba `**Tag:**` y el cierre de P001 no habría creado tag pese a la
  configuración `lightweight`. El usuario decidió añadir `p001` como edición propia desde la UI antes de aceptar.
- El consentimiento de D121 cubre T008–T012 dentro de sus techos. T008 (Codex→Codex) es la siguiente; se lanza
  cuando el usuario lo pida.

## D128 — P009-T008: detenida; una ruta de directorio no cubre sus archivos

Estado: detenida el 2026-10-21. Fase: P009. Dentro de D121 y de la propuesta §§3–6, a petición del usuario.
[Evidencia saneada](archive/phase-009/P009-T008_PILOTO_CODEX_CODEX.md).

- P001-T001 del hijo (run `fc340afb`) se planifica, se ejecuta y pasa las seis validaciones del perfil con Codex
  `gpt-6-luna`/`medium` en los tres roles. La selección del ejecutor la decide el revisor con motivo propio y coincide
  con la invocación. El revisor bloquea: la política de rutas marca como infracción los seis archivos de `core/`.
- Causa: `check_paths` empareja con `fnmatchcase`, que no trata `core/` como prefijo de directorio, y
  `task_contract` acepta esa entrada sin avisar. El fallo llega después de ejecutar y revisar. La notación viene del
  NEXT_STEPS que redactó el revisor en la definición; el ensayo T005 usaba `templates/**` y no lo cubría.
- Se para por rechazo del revisor (propuesta §5): sin reintento, revalidación, concesiones ni commit. Consumo: 3 de
  las 7 invocaciones de T008, 6 de 60 del piloto. Los cambios del ejecutor se conservan sin confirmar en el hijo,
  por decisión del usuario.
- La corrección es una tarea de producto aparte, P009-T017. Reanudar T008 exige wheel nuevo verificado y
  autorización nueva del usuario; esta parada no autoriza más consumo.
- Antes de encolar, el recibo de preparación no coincidía: el `runserver` de QA de T007 escribió 366 `.pyc` en
  `.venv`, cuyo bytecode también acredita el recibo (D119). Por decisión del usuario se borraron exactamente esos
  archivos, sin tocar código, TOML ni SQLite. El QA de T012 lanzará `runserver` sin escribir bytecode.

## D129 — P009-T017: una ruta de directorio se congela como `dir/**`

Estado: implementada el 2026-10-21. Fase: P009. Corrige la causa de D128.
[Entrega](archive/phase-009/P009-T017_RUTAS_DIRECTORIO.md).

- `task_contract` congela como `dir/**` toda entrada de `allowed_paths` o `forbidden_paths` que termina en `/`.
  Ejecutor, revisor, política de rutas, concesiones de ficheros y comprobación de contradicciones leen así el mismo
  alcance. La contradicción con una prohibición se rechaza antes del escritor. Se descarta rechazar la notación:
  los NEXT_STEPS que redacta el revisor la usan, y el run pararía sin ejecutar.
- `matches` no cambia. Las rutas exactas, los globs, las entradas sin barra y los patrones de perfiles se leen igual.
  Los contratos ya congelados conservan bytes, hashes y lectura literal, así que no se versiona el motor ni el
  adaptador. `plan-task` y el esquema del planificador piden `dir/**`.
- Por decisión del usuario, el run `fc340afb` no se revalida: con su contrato literal volvería a parar. Queda
  BLOCKED como evidencia. Reanudar T008 exige retirar del hijo las ocho rutas de su diff y encolar P001-T001 de
  nuevo. Necesita al menos 3 de las 4 invocaciones que quedan, y un ciclo REVISE superaría el techo de 7.

## D130 — P009-T018: el recibo de preparación compara el inodo, no el dispositivo

Estado: implementada el 2026-10-21. Fase: P009. Desbloquea la segunda reanudación de T008.
[Entrega](archive/phase-009/P009-T018_RECIBO_TRAS_REINICIO.md).

- La segunda sesión de T008 se paró antes de encolar, sin consumir invocaciones. Tras reiniciar el Mac, macOS
  renumeró `st_dev` del hijo con el mismo inodo y los mismos bytes, y el recibo de D119 dejó de valer.
- Por decisión del usuario, `verify_receipt` compara el inodo del checkout y de `.venv`, y sigue verificando
  byte a byte los archivos protegidos y el entorno. Los recibos no se reescriben y conservan su hash. Admisión, UI y
  comandos nativos usan esa misma verificación.
- Las operaciones en curso (creación, preparación y carpeta de proyectos) siguen comparando `{device, inode}`.
  Tras un reinicio, crear otro proyecto exige volver a elegir la carpeta. Queda como límite, fuera del piloto.

## D131 — P009-T008: completada; Codex→Codex COMMITTED

Estado: completada el 2026-10-21. Fase: P009. Dentro de D121 y de la propuesta §§3–6 y §10.
[Evidencia saneada §8](archive/phase-009/P009-T008_PILOTO_CODEX_CODEX.md#8-reanudación-2026-10-21-sesión-3-committed).

- El run nuevo `7fbaf89c` de P001-T001 se planifica, se ejecuta, valida y revisa con Codex `gpt-6-luna`/`medium` en los
  tres roles. La selección del ejecutor la decide el revisor con motivo y coincide con la invocación. `core/` se congela
  como `core/**` (D129) y la política de rutas no marca nada. ACCEPT sin hallazgos.
- Commit `98f4611` confirmado desde la UI por decisión del usuario: P001-T001 COMMITTED, con contenido exacto
  acreditado. Es la primera tarea del piloto P009 que llega a COMMITTED, sobre un proyecto creado desde la UI.
- Consumo: T008 6 de 10, piloto 9 de 60. `fc340afb` sigue BLOCKED como evidencia.
- Antes hubo que corregir dos defectos que ningún ensayo había detectado: rutas de directorio (T017, D129) y recibo
  tras reinicio (T018, D130). Las observaciones de contenido (alta sin redirección y flujo recortado) no bloquean.
  Quedan registradas para las tareas siguientes del hijo.

## D132 — P009-T009: detenida; el ejecutor Claude no puede cumplir `ruff format`

Estado: detenida el 2026-10-21. Fase: P009. Dentro de D121 y de la propuesta §§3–6, a petición del usuario.
[Evidencia saneada](archive/phase-009/P009-T009_PILOTO_CODEX_CLAUDE.md).

- En Ajustes solo cambia el ejecutor, a Claude con el catálogo de D121 (registro v2, auditado). El run `bb29b133` de
  P001-T002 se planifica con revisor Codex `gpt-6-luna`/`medium`, que elige al ejecutor Claude `claude-sonnet-5-5`/`medium`
  con motivo. La invocación coincide con esa selección. Edición y borrado con 404, POST y CSRF; 11 tests JUnit verdes.
- Falla `ruff format --check .` por una línea de `core/tests.py`. El hijo usa `line-length = 100` y el ejecutor
  Claude, sin shell (D121), formatea a mano con 88 columnas. Dos REVISE con el mismo hallazgo, y el reintento no
  cambia nada. Ni el revisor ni el ejecutor ven qué línea cambiaría Ruff. El run acaba en `revision_limit`.
- `serve` murió por SIGBUS en el índice WAL durante el primer ciclo de corrección. Causa probable, no demostrada: los
  lectores `sqlite3` del sistema que el agente lanzaba sobre la SQLite viva. La SQLite está íntegra. La recuperación
  del producto funcionó: RECOVERY_REQUIRED sin reencolar, escritor confirmado, run INTERRUPTED y reintento explícito
  pedido por el usuario. Regla de operación: no se abre la SQLite viva con otra build de SQLite mientras corre `serve`.
- Consumo: T009 6 de 7, piloto 15 de 60. Sin commit; los cambios del ejecutor se conservan en el hijo.
- La corrección es una tarea de producto aparte, P009-T019. Reanudar T009 exige autorización nueva del usuario;
  esta parada no autoriza más consumo.

## D133 — P009-T019: el harness formatea con la herramienta del perfil tras cada turno del ejecutor

Estado: implementada el 2026-10-21. Fase: P009. Corrige la causa de D132.
[Entrega](archive/phase-009/P009-T019_FORMATEO_PERFIL.md).

- Por decisión del usuario, tras cada turno del ejecutor y antes de capturar la evidencia, el motor ejecuta el
  formateador del perfil (`formatter_argv` + rutas) sobre los `changed_paths` que casan con `formatter_paths` y que
  el contrato permite. Nunca al revalidar. Se descartan el diff de `ruff format --diff` para el ejecutor (cuesta un
  ciclo por error y depende del modelo) y una concesión `Bash(ruff format …)` (shell parcial, contra D121).
- El perfil `python-django-recipe` declara `ruff format --` y `*.py` en `local_config.py`, no en `recipes/django.py`:
  su texto es la huella que vincula los recibos de preparación (D119). La huella no cambia y el hijo del piloto sigue
  preparado. Un formateador exige argv terminado en `--` y `authorize_profile_commands = true`.
- El runner nativo autoriza ese argv solo con archivos regulares existentes del checkout (`formatter-paths`). Sin
  formateador, `command_config_sha256` no cambia y el adaptador sigue en `commands-1`.
- Un formateador que no se ejecuta para el run en la etapa `formatter` antes de revisar. Un código de salida distinto
  de cero llega a la validación y al revisor. El ciclo guarda `formatting_json`: el revisor lo recibe como
  `formatting`, la API lo expone y la UI lo muestra. El historial pasa a formato 8 solo si algún ciclo lo tiene, y
  lee 1–8. `PROFILE_INSTRUCTIONS` avisa al ejecutor de que el harness formatea.
- Por decisión del usuario, `bb29b133` queda en `revision_limit` como evidencia, igual que `fc340afb` (D129).
  Reanudar T009 exige un wheel reconstruido y verificado, retirar del hijo las 7 rutas de su diff con copia privada
  y una autorización nueva con techo: un run nuevo necesita al menos 3 invocaciones y queda 1 de 7.

## D134 — P009-T009: completada; Codex→Claude COMMITTED

Estado: completada el 2026-10-21. Fase: P009. Dentro de D121 y de la propuesta §§3–6 y §12.
[Evidencia saneada §7](archive/phase-009/P009-T009_PILOTO_CODEX_CLAUDE.md#7-reanudación-2026-10-21-sesión-2-committed).

- Autorización nueva del usuario: reanudar T009 con techo 13. Wheel de `494b929` (T019) verificado e instalado. Las 7
  rutas de `bb29b133` se retiran del hijo con copia privada. Una incidencia del script obligó a reconstruir dos
  archivos de esa copia desde la evidencia del producto, sin pérdida.
- Run `bf007561` de P001-T002: revisor Codex `gpt-6-luna`/`medium`, ejecutor Claude `claude-sonnet-5-5`/`medium`
  elegido por el revisor con motivo y observado en el stream. El formateo del harness (D133) reformatea 1 de 3
  archivos, pasan las seis validaciones y el revisor acepta a la primera, sin hallazgos.
- Commit `2f2b13f` confirmado desde la UI por decisión del usuario: P001-T002 COMMITTED. Consumo: T009 9 de 13,
  piloto 18 de 60. Es la primera tarea del piloto con un ejecutor sin shell que llega a COMMITTED.

## D135 — P009-T020: encolar desde los documentos, con notas adicionales

Estado: implementada el 2026-10-21. Fase: P009. A propuesta del usuario, antes de T010.
[Entrega](archive/phase-009/P009-T020_ENCOLAR_DESDE_DOCUMENTOS.md).

- `GET /projects/{id}/task-sources` ofrece las tareas del NEXT_STEPS vivo con su sección literal (precedida de las
  restricciones compartidas, si las hay) y su hash. El formulario elige fase y tarea con desplegables y muestra el
  contrato en solo lectura. El modo manual sigue disponible. En el hijo del piloto, los textos coinciden byte a byte
  con los que se pegaron a mano en T008 y T009.
- `POST /runs` acepta `source_sha256` (CAS: 409 `task_source_changed` si el documento vivo ya no da ese texto) y
  `notes`, hasta 4000 caracteres. Las notas van en la petición del job, sin columna ni migración. El motor las pasa
  al planificador, las congela en el contrato como `additional_notes` y las añade a las instrucciones del ejecutor.
- No basta con añadirlas al texto: el planificador solo lee la sección de la tarea y las restricciones compartidas.
  Solo el usuario aporta `additional_notes` (se retira la que invente el planificador) y nunca amplían rutas,
  comandos ni permisos. Sin notas, petición, entrada, contrato y prompts no cambian.

## D136 — P009-T010: completada; Claude→Claude COMMITTED

Estado: completada el 2026-10-21. Fase: P009. Petición del usuario de continuar, dentro de D121 y de la propuesta
§§3–6. [Evidencia saneada](archive/phase-009/P009-T010_PILOTO_CLAUDE_CLAUDE.md).

- Wheel de `5ba32f8` (T020) construido, verificado e instalado offline. Registro v3 al cambiar solo el revisor a
  Claude `claude-sonnet-5-5`/`medium` desde Ajustes; ejecutor Claude y catálogo intactos. Mismo proyecto e historial.
- Run `beaf4528`, P001-T003, encolado desde el selector documental sin notas. Claude Sonnet 5.5/medium en los tres
  roles; ejecutor elegido por el revisor con motivo y modelo observado en el stream. Completar/reabrir por POST,
  filtros por estado y vacíos legibles; flujo actualizado, sin cambios de modelo ni migraciones.
- Pasan los 22 tests y las seis validaciones; el formateador deja los tres archivos Python sin cambios. ACCEPT a la
  primera, sin hallazgos ni concesiones. Commit `882af9b` confirmado desde la UI; run COMMITTED y checkout limpio.
  T010 consume 3 de 7; piloto acumulado 21 de 60. La comprobación de fase previa `08f3532f` no tiene intentos de agentes.
- El mensaje automático del commit toma el título congelado en español. Consultado después de confirmarlo, el
  usuario elige conservar ese commit y su evidencia y aplicar el inglés al commit de esta sesión en `my_harness`.
  No se reescriben historiales. T011–T012 pendientes; el piloto todavía no está terminado.

## D137 — P009-T011: completada; Claude→Codex COMMITTED

Estado: completada el 2026-10-21. Fase: P009. Petición del usuario de continuar, dentro de D121 y de la propuesta
§§3–6. [Evidencia saneada](archive/phase-009/P009-T011_PILOTO_CLAUDE_CODEX.md).

- Mismo wheel instalado de T020. Desde Ajustes, registro v4 al cambiar solo el ejecutor a Codex con el catálogo
  D121; revisor Claude `claude-sonnet-5-5`/`medium` intacto. Proyecto, checkout e historial conservados.
- Run `6bb55757`, P001-T004, desde el selector documental. Notas del usuario exigen título inglés; el planificador
  congela `Search tasks by title`, del que deriva el mensaje de commit, sin modificar el documento ni ampliar
  permisos. El revisor elige `gpt-6-luna`/`medium` con motivo y el argv coincide. Claude reporta Sonnet en sus
  streams; Codex no reporta modelo independiente. El esfuerzo efectivo tampoco se mide independientemente.
- Búsqueda GET por título con ORM y escape, combinable con filtros, estado sin resultados y flujo documentado.
  Cinco tests nuevos; 27 tests y seis validaciones correctas. ACCEPT a la primera, sin hallazgos ni concesiones.
  Commit `a2de6ad` confirmado desde la UI, mensaje inglés; COMMITTED y checkout limpio. T011: 3 de 7; piloto: 24 de 60.
- Las cuatro parejas tienen tareas COMMITTED. QA funcional conjunto y check/cierre del hijo quedan para T012;
  no se presenta el piloto como terminado. Observación documental: nodo `R` duplicado en el Mermaid de búsqueda
  y estado del hijo; revisar en T012 sin reescribir evidencia ni editar el hijo fuera del producto.

## D138 — P009-T012: QA correcto y cierre detenido por REVISE documental

Estado: detenida el 2026-10-21. Fase: P009. Dentro de D121 y de la propuesta §§3–6, con reanudación HITL de §13.
[Informe y matriz](archive/phase-009/P009-T012_CIERRE_PILOTO.md), [corrección propuesta](archive/phase-009/P009-T012_CORRECCION_DOCUMENTAL.md).

- Primer acceso del QA devuelve 500: la migración aceptada `core.0001_initial` no está aplicada a la SQLite de uso.
  Las validaciones del perfil usan la base de tests y comprueban deriva de migraciones; no migran la base local.
  Se detienen ambos servicios sin consumo. El usuario autoriza copia privada, aplicación de la migración existente
  y reanudación, con el mismo techo de dos llamadas. Sin cambios de código/configuración ni SQLite del harness.
- QA conjunto en Chrome correcto con una tarea sintética, eliminada desde la UI: alta/listado, edición,
  estado/filtros, búsqueda combinada, escape y confirmación/cancelación/borrado. El check vuelve a pasar las seis
  validaciones con 27 tests y JUnit completo, sobre `a2de6ad` limpio.
- Check `82cc4650`/run `400d5d48`, Claude `claude-sonnet-5-5`/`medium`: REVISE por el nodo `R` duplicado y
  título incompleto de `tasks.md`. Pide también consolidar dos propuestas ADR y actualizar la prosa de STATE.
  Se respeta la parada, sin retry ni cierre. Corrección concreta lista para confirmar en el editor documental del
  producto, sin agentes de edición y conservando los cuatro commits y el check original; espera respuesta HITL.
- T012: 1 de 2; piloto: 25 de 60. Una llamada restante no autoriza reanudar tras REVISE sin respuesta del usuario.
  P001 sin READY, cierre, tag ni archivo; P009 tampoco se cierra. Servicios detenidos, cero locks y sin trabajos
  pendientes, SQLite íntegra. Las cuatro parejas COMMITTED están acreditadas, pero el piloto no está completado.

## D139 — P009-T012: completada; piloto Django con P001 cerrada y archivada

Estado: completada el 2026-10-21. Fase: P009. Continúa D138 tras autorización expresa «Autorizo» en el chat,
para corregir documentos desde el producto, gastar la llamada restante y cerrar solo si READY (propuesta §14).
[Informe y matriz](archive/phase-009/P009-T012_CIERRE_PILOTO.md), [ediciones confirmadas](archive/phase-009/P009-T012_CORRECCION_DOCUMENTAL.md).

- Editor documental con preview/diff/hash, motivo y confirmación en tres commits ingleses: `2f23d3d` corrige
  nodo y título del flujo; `0787bff` actualiza prosa de STATE; `47a0557` consolida D001/D002 del hijo desde las
  propuestas aceptadas de T003/T004 y regenera su índice. Sin agentes para editar ni cambios manuales en el hijo.
  Los cuatro commits anteriores y el primer check REVISE se conservan.
- Check `9f9bdb44`/run `21f607d3`, Claude `claude-sonnet-5-5`/`medium`, devuelve READY sobre `47a0557` limpio;
  los cinco criterios pasan, sin preguntas ni acciones, con 27 tests/JUnit y las seis validaciones correctas.
  Vínculo `d61549f4668a`. Modelo reportado Sonnet; esfuerzo efectivo sin medición independiente.
- Cierre confirmado desde UI sobre ese vínculo: `d2e45cf7`/run `99852943`, CLOSED, tag ligero `p001` sobre
  el HEAD evaluado y commit inglés `3d105c6` (`harness: archive P001`). STATE/NEXT_STEPS se archivan por bytes,
  con REVIEW y SUMMARY, en `docs/archive/phase-001/`. Documentos vivos renovados y ROADMAP actualizado;
  sin sucesora ni planificación posterior. Cierre sin invocaciones de proveedor ni duplicados.
- Se acredita el recorrido real Django desde creación UI hasta cuatro tareas COMMITTED con las cuatro parejas,
  QA conjunto y cierre/archivo del mismo proyecto. T012 consume 2 de 2; piloto 26 de 60. No autoriza más
  llamadas por el margen global restante ni permite comparar estadísticamente la calidad de los modelos.
- Hijo limpio, servicios detenidos, SQLite íntegra, cero locks y ningún job pendiente. P009 del harness no se
  cierra en esta tarea: su revisión y archivo documental son posteriores. Observaciones sin bloqueo en el informe.

## D140 — Cierre documental manual de P009

Estado: cerrada y archivada el 2026-10-21 por la continuación solicitada por el usuario, tras D139. Fase: P009.
[Resumen](archive/phase-009/SUMMARY.md), [revisión](archive/phase-009/REVIEW.md) y
[registro de cierre](archive/phase-009/P009_CIERRE.md). Precedente: D002/D088/D114.

- Las veinte tareas y siete criterios de ROADMAP están cumplidos en el alcance acreditado por T012/D139:
  creación UI, cuatro parejas sobre el mismo Django, QA conjunto, READY y cierre/archivo de P001 del hijo.
  El piloto consume 26 de 60; T012 agota sus dos llamadas. No demuestra portabilidad ni superioridad de modelos.
- La petición de continuar y hacer commit cubre la siguiente tarea identificada en STATE/NEXT_STEPS: revisar
  la salida y cerrar/archivar documentalmente P009. Se completa manualmente; el repositorio sigue sin
  registrarse ni ejecutarse en el harness. Sin check READY ni tag propios, SQLite operativa o proveedores.
- Se conservan STATE, NEXT_STEPS y los 26 artefactos originales de `docs/phase/` por bytes respecto de `4223571`.
  El manifiesto registra origen/destino, tamaño y SHA-256. SUMMARY y REVIEW sintetizan entregas, evidencia y
  límites; los originales conservan sus estados, enlaces y comandos históricos en su contexto de origen.
- STATE compacta la base de P009, NEXT_STEPS queda sin tareas y ROADMAP marca la fase completada con su archivo.
  Sin sucesora definida, el usuario elige la próxima prioridad. Las referencias vigentes se reubican;
  las fases anteriores y las decisiones históricas conservan su contenido.
- Las observaciones de alta sin redirección, marcadores de define-project y presentación de deriva de fase
  cerrada quedan como candidatas sin fase. No se corrigen en este cierre ni se añaden migraciones automáticas.
  No cambian código, esquema, API, flujos, configuración global o consentimientos. Sin push ni publicación.

## D141 — P010: consolidación de la primera versión local

Estado: propuesta aceptada por el usuario el 2026-10-21; fase planificada, sin implementación. Fase: P010.
El encargo es «Crea únicamente la documentación de la nueva fase. (Acepto tu propuesta)».
[Plan](archive/phase-010/P010_PLAN_CONSOLIDACION.md), [tareas](archive/phase-010/NEXT_STEPS.md) y [criterios](ROADMAP.md#p010--consolidación-de-la-primera-versión-local).

- Tras P001–P009, se acota una fase de consolidación: `package.json` inicial de `typescript-web`, lecturas de runs
  sin decodificación completa, marcadores opcionales de definición, presentación de deriva de fases cerradas,
  documentación de instalación/compatibilidad y contraste de los criterios globales de aceptación.
- Las correcciones técnicas se diseñan en T001; esta decisión fija resultados y restricciones, sin dar por elegidos
  una receta TypeScript, tablas, migraciones, índices, formatos o versiones nuevos. La paridad documental se hace
  al implementar, conservando snapshots, recuperación y protecciones de los manifiestos.
- Una matriz relacionará los trece criterios de SPECIFICATION §10 con evidencia y límites. El cierre de las fases
  anteriores no sustituye a esa revisión ni acredita por sí solo la primera versión. «Primera versión local»
  describe un alcance de producto; no cambia automáticamente `0.1.0`, crea un tag ni publica el paquete.
- La validación real complementaria de A/B y del perfil Python/Django declarativo se prepara como propuesta
  concreta en T008. Antes del cierre se decidirá explícitamente si se ejecuta o se mantiene como límite del
  alcance soportado; no se confunde la receta Django de P009 con el perfil de D095. Una operación real conserva
  consentimiento propio; aceptar el plan no lo concede. No se obliga a repetir la matriz de cuatro parejas.
- Se aplazan la hora de validaciones, KaTeX y el POST→redirect→GET del Django hijo; continúan fuera de alcance
  App Server/SDK, `project.yaml`, nube, multiusuario, aislamiento físico y publicación. P009 y sus snapshots
  permanecen intactos; no se inicia otra fase del hijo.
- Esta entrega cambia solo documentación. No autoriza implementar tareas, lanzar agentes/proveedores o smokes,
  instalar, levantar servicios, modificar configuración global, hacer commits, push o publicar. La siguiente
  tarea es P010-T001 cuando el usuario solicite ejecutar el plan; no se usa el harness sobre este repositorio.

## D142 — P010-T001: receta TypeScript, proyección de runs y tarea T011

Estado: diseño completado el 2026-10-22; implementación pendiente de P010-T002, T003 y T011. Fase: P010.
[Contrato, inventario y matriz inicial](archive/phase-010/P010-T001_CONTRATO_CONSOLIDACION.md). Concreta D141. Las cuatro
elecciones de diseño son del usuario (HITL del 2026-10-22). Conserva D029, D088, D095 y D116–D119.

- El `package.json` inicial de un `typescript-web` nuevo lo genera una segunda receta empaquetada,
  `typescript-web-recipe-1`, dentro del marco D119: `[recipes.typescript-web]` en `local-config-5` y una composición
  con `recipe = "typescript-web"` y el perfil integrado sin cambios. Mismo contrato `project-preparation-1`, binding,
  tablas, locks, recuperación y commit técnico; Django conserva sus planes, recibos y hashes. Solo hijos nuevos
  creados por el servicio, con commit documental raíz; las altas e importaciones no cambian.
- La receta escribe un manifiesto empaquetado (`typescript@5.9.3` con el lock del fixture y `engines` exactos),
  verifica `node`/`npm`, ejecuta `npm ci --ignore-scripts` (offline con la caché declarada; red solo con techo del
  operador y elección en la vista previa) y las validaciones del perfil antes del commit. El recibo fija el
  manifiesto protegido y los ejecutables, no `node_modules`. Un `npm ci` incierto sigue las reglas D119.
- Las vistas leen una proyección derivada `run-projection-1`. Se escribe en la misma transacción que
  `history_json`, que sigue siendo la autoridad, y la rellena una migración aditiva sin reescribir historiales.
  Las vistas no seleccionan `history_json` ni llaman a `load_history`; el backup comprueba la consistencia. El
  motor, la recuperación, los checks, el chat y los permisos siguen leyendo el historial.
- Se añade **P010-T011**, que lleva las métricas y la vista previa de exportación a esa proyección (SPECIFICATION §9).
  Depende de T003 y precede a T006. T003 cubre detalle, diff, JUnit y listados de runs.
- La matriz inicial de los trece criterios no reejecuta nada. Huecos: `typescript-web` nuevo (T002), A/B y perfil
  D095 sin evidencia real (T008), chat sin evidencia real localizada. Queda abierta para T007 la cuestión del SSE
  gestionado frente al sondeo con cursor de D029 en el criterio 13.

Solo documentación: sin código, esquema, API, flujos, configuración, instalaciones, servicios ni proveedores.

## D143 — P010-T002: receta `typescript-web-recipe-1` implementada

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega, pruebas y límites](archive/phase-010/P010-T002_ARRANQUE_TYPESCRIPT.md), [flujo](flows/project-preparation.md),
[ejemplo](../examples/typescript-web-recipe.example.toml). Implementa D142 y el contrato de P010-T001 §1;
conserva D088, D116 y D119.

- `local-config-5` admite `[recipes.typescript-web]` (node/npm absolutos sin shells y con versión exacta, `npm_cache`
  canónico fuera del estado y de los checkouts, timeout, salida y techo de red). Su composición nombra el perfil
  integrado `typescript-web` sin cambios, `node`/`npm` que resuelven a los mismos archivos y un entorno propio con
  `npm_config_cache` igual a la caché; no se reescribe. Formato, `[recipes.django]` y v1–v4 sin cambios.
- `recipes/django.py` permanece byte a byte: su texto entra en la huella de los recibos emitidos. Un registro en
  `recipes/__init__.py` asocia cada receta a su módulo y perfil; el servicio separa núcleo común y partes por receta,
  y el plan Django conserva claves y valores.
- Manifiesto empaquetado íntegro en la vista previa; pasos `files` → versiones exactas → `npm ci --ignore-scripts`
  (offline solo desde la caché) → `npm run check/test/build` con JUnit → commit técnico. HOME/TMPDIR y dos npmrc
  vacíos en el hijo, porque npm rechaza el mismo archivo como configuración de usuario y global.
- Recibo con identidad, manifiesto protegido según el glob del perfil y `node`/`npm` por hash; `node_modules` no se
  congela porque el perfil lo reinstala en cada tarea. Recuperación D119 sin relajar: con caché vacía npm falla sin
  crear `node_modules/` y el sucesor explícito es posible; bytes parciales o un `npm ci` sin checkpoint bloquean.
- Sin migración, tablas ni cambios de API. UI con textos por receta. Mensajes `preparation_required` genéricos.

Verificación con node/npm sintéticos y, opcionalmente, con node 24.15.0/npm 11.12.1 reales sobre una caché local ya
poblada, sin red. No acredita proveedores, otras plataformas ni dependencias añadidas tras preparar.

## D144 — P010-T003: proyección `run-projection-1` implementada

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega, medidas y límites](archive/phase-010/P010-T003_LECTURAS_RUNS.md), [diagrama](DDBB-DIAGRAM.md#proyección-de-runs-p010-t003),
[flujo](flows/task-run.md#lectura-del-run-d144). Implementa D142 y el contrato de P010-T001 §2 para las vistas de
runs; métricas y exportación quedan para T011.

- Migración aditiva `0023_run_projection` con seis tablas derivadas (resumen, paradas, ciclos, tramos de diff,
  reportes JUnit y casos), con FK a `managed_runs` y claves primarias compuestas que fijan el orden. Rellena cada
  historial existente con el codec vigente (formatos 1–8) sin modificar `history_json`; el downgrade solo las borra.
- `_queue_new_run` y `_history` escriben la proyección en la misma transacción que el historial; la actualización es
  incremental (paradas y ciclos añadidos, y la revisión de un ciclo previo, único cambio que `_history` admite).
- El diff revisado se guarda en tramos fijos de 64 KiB: una página lee solo los tramos que cubre más 4 bytes para
  completar una secuencia UTF-8. El tamaño del tramo forma parte de `run-projection-1`.
- API: `history.cycles` se sustituye por `history.cycle_count` y `history.latest_cycle`, y los ciclos se leen con
  `GET /runs/{id}/cycles` (10 por defecto, hasta 100). El resto del detalle conserva su forma; `stops` sigue completo
  porque crece con los jobs y sus filas son pequeñas. OpenAPI, tipos, página del run y chat actualizados.
- Las vistas cargan solo columnas declaradas de `managed_runs` (el resto lanza) y no importan el codec; los listados
  de tareas agregan en SQL. El backup recalcula la proyección de cada run y compara filas y recuentos; si difiere
  falla con diagnóstico. La restauración no reconstruye y la cuarentena no cambia.

Verificación con historiales sintéticos (formatos 1–8 tras la migración y uno de 26 MiB), motor y agentes falsos,
comparando con la implementación anterior. No se migra la instalación real en esta fase.

## D145 — P010-T011: métricas y vista previa de exportación sobre la proyección

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega, medidas y límites](archive/phase-010/P010-T011_METRICAS_SIN_HISTORIAL.md), [flujo](flows/documents.md#vista-previa-de-la-exportación-d145).
Implementa D142 y el contrato de P010-T001 §2 para las vistas que no son de runs, sobre la proyección de D144.

- Las métricas `summary`, `tasks` y `validations` y la vista previa de la exportación documental (formas D036 y v2)
  leen `run-projection-1` y `managed_attempts`; no llaman a `load_history` ni seleccionan `history_json`.
- La validación de cada ciclo se reconstruye sin casos en Python. SQL extrae de cada comando los campos que decide
  `CommandResult.passed`, evaluado con la misma clase del motor, y cuenta los casos JUnit por reporte y resultado.
  Solo un entero JSON es código de salida.
- Los intentos del historial son las filas `1..attempts` de `managed_attempts`, invariante que ya exige `_history`.
  Una fila posterior sin resultado es un intento en curso y no cuenta.
- La vista previa no es autoridad. El envío confirmado, la petición del job y la intención recalculan la instantánea
  desde el historial y exigen la revisada; si la proyección difiere, responden `Conflict` sin efecto. El commit de
  tarea, la transición y su vista previa, los checks, el chat y la recuperación siguen leyendo el historial.
- Un run sin proyección es una base inconsistente: las vistas fallan con diagnóstico y no reconstruyen.
- Sin migración, tablas, columnas ni cambios de API: las medidas no justifican una versión nueva de la proyección.

Verificación con historiales sintéticos (formatos 1–8 tras la migración, casos límite de validación y un ámbito de
35,4 MiB), motor y agentes falsos, comparando con la implementación anterior. No se migra la instalación real.

## D146 — P010-T004: marcadores opcionales en la definición

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega](archive/phase-010/P010-T004_MARCADORES_DEFINICION.md), [flujo](flows/project-definition.md).
Resuelve la observación de D127: ante una carpeta nueva, Codex preguntó como bloqueante por el contenido y los
marcadores gestionados que la plantilla pedía conservar.

- Los marcadores gestionados son opcionales en los borradores de definición. Es el comportamiento que ya tenía la
  aceptación (`replace_block` añade al final el bloque ausente); no cambia el motor, la API ni el esquema.
- La plantilla incorporada `define-project` lo dice expresamente: sin borradores en el contexto se redacta desde el
  brief sin pedir contenido previo; el revisor no necesita añadir marcadores, conserva las parejas que existan y no
  los pone en otros documentos. La definición solo crea documentos: el código figura como trabajo planificado.
- Versionado: la plantilla incorporada cambia de identidad (`builtin-1:` + hash). Los turnos anteriores conservan la
  plantilla congelada en su catálogo y su snapshot; las versiones activadas desde el editor de prompts no cambian.
- La UI de definición explica en una carpeta sin borradores que no hacen falta archivos previos, y el editor de
  borradores ya no pide no borrar los marcadores: indica que son opcionales y cómo se regeneran.
- `import-project` y `onboard-project` parten de un origen con contenido y no cambian.

## D147 — P010-T005: evidencia histórica de una fase cerrada

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega](archive/phase-010/P010-T005_FASES_CERRADAS.md), [flujo](flows/phase-lifecycle.md#consulta-de-una-fase-cerrada-p010-t005).
Resuelve la observación de P009 (REVIEW): la vista de P001 cerrada del hijo comparaba los documentos renovados por el
cierre con la base histórica y mostraba deriva.

- Solo cambia la presentación. `phase.documents`, el READY vinculado, el check y la adopción siguen igual; nada
  histórico se reescribe. Sin migración: todo sale de la operación `close` ya registrada.
- `PhaseRead.closure` (null en fases abiertas) muestra el cierre o abandono: check READY con su resultado, base
  (head, evidencia, documentos), tag, motivo, commit y archivo.
- Hashes esperados tras cerrar: base adoptada, más lo que escribió el cierre (`after_sha256` de su vista previa
  sellada), más las ediciones y exportaciones documentales COMMITTED posteriores de la fase, encadenadas por
  `before_sha256`. Su diferencia con la base es `renewed`: esperada, no un fallo del check.
- Deriva real: sin sucesora, documentos vivos distintos de los esperados (`changed`); con sucesora no se comparan,
  porque son suyos. Además, cada archivo del archivo se contrasta con el hash que escribió el cierre
  (`archive_altered`). Ninguno se oculta.
- La página de documentos usa los hashes esperados si la última fase está terminada. Las fases abiertas conservan
  deriva frente a la base adoptada, READY obsoleto y bloqueo del cierre.

## D148 — P010-T006: documentación de instalación y alcance soportado

Estado: completada el 2026-10-22. Fase: P010. [Entrega](archive/phase-010/P010-T006_DOCUMENTACION_VERSION.md).
Contrasta README, ARCHITECTURE y `examples/` con el código y la evidencia, sin cambiar código ni configuración.

- Versiones CLI por rol según `cli_agents.SUPPORTED`/`WRITE_SUPPORTED` y D122, con el uso real registrado de cada
  una; los usos anteriores a `cli-13` se presentan como históricos y Codex 0.161.0 figura sin uso real localizado.
- README separa lo verificado offline de lo probado con proveedores; A/B, perfil declarado de D095, receta TypeScript
  web, chat y backup no tienen uso real. «Primera versión local» no cambia la versión `0.1.0` ni implica publicación.
- Por decisión del usuario, la falta de actualizador de bases en el paquete instalado (D043) se documenta como límite
  vigente: una base en una revisión anterior, como `0022`, no arranca con el paquete en `0023`. P010-T007 valora si se
  acota como tarea de producto; no se documenta una vía manual sobre `storage/migrate.py`.
- La plantilla TOML sigue en `local-config-4` (la fija un test) y vale como v5 cambiando `format`; el fragmento Django
  se añade con otro nombre de composición si el TOML ya tiene `[compositions.django]`.

## D149 — P010-T007: matriz de aceptación, SSE por cursor y tarea T012

Estado: completada el 2026-10-22. Fase: P010. [Matriz](archive/phase-010/P010_MATRIZ_ACEPTACION.md).
Decisiones del usuario en el bucle HITL de T007 sobre las dos cuestiones abiertas de T001 y T006.

- **Criterio 13 de SPECIFICATION §10.** En la UI gestionada, el sondeo de eventos con cursor por secuencia de D029
  cumple la garantía «sin huecos ni duplicados» que el criterio pide al SSE; el SSE literal se acredita en la
  observación legacy. Es una interpretación explícita: la especificación no cambia y el SSE gestionado sigue sin
  implementarse. Un test nuevo lee eventos por páginas mientras el run avanza y continúa tras reiniciar el servicio.
- **Migraciones del paquete instalado.** La falta de una orden de migración en el paquete (D043, D148) incumple
  «migraciones explícitas con backup previo» de §9. Se añade **P010-T012**: `harness-local migrate` sobre
  `storage/migrate.py`, con instantánea previa y las mismas negativas, antes de T009.
- Matriz: los trece criterios cumplen en el alcance offline con tests reejecutados; dos tests nuevos cubren el
  recorrido completo del criterio 2 por la API y el cursor del 13. La evidencia real es histórica y la falta de uso
  real (chat, backup, A/B, perfil declarado, receta TypeScript) queda para T008. Sin cambios de producto.

## D150 — P010-T012: migración explícita de bases desde la CLI instalada

Estado: implementado y verificado offline el 2026-10-22. Fase: P010.
[Entrega y límites](archive/phase-010/P010-T012_MIGRACION_INSTALADA.md), [flujo](flows/database-migration.md). Implementa el
acuerdo de D149 para SPECIFICATION §9; amplía D053 a la CLI instalada y mantiene creación/arranque de D043.

- `harness-local migrate --database RUTA --snapshots DIRECTORIO --writers-stopped` reutiliza `storage/migrate.py`.
  Ambas rutas son absolutas; exige base existente y directorio de copias fuera de checkouts Git y raíces persistidas.
  Rechaza enlaces en componentes, base y auxiliares; no usa `HARNESS_DATABASE_URL` ni configuración global.
- Declaración explícita de servicio/observadores/escritores detenidos, igual que backup. La evidencia persistida
  comprueba propietarios de jobs y preparaciones, grupos CLI y validaciones, incluso antes de devolver `current`.
  Un servicio inactivo sin propietario persistido depende de esa declaración; no se añade descubrimiento global.
- Revisión anterior conocida: instantánea SQLite `premigration-1`, integridad, revisión, SHA-256 y fsync antes de
  Alembic; validación de esquema tras el éxito. Base al día: sin escritura ni copia. Rechaza revisiones desconocidas,
  restauraciones de consulta y bases sin Alembic. Fallos conservan base y copia, sin restauración automática.
- `scripts/dev` conserva creación y migración de su base y comparte las guardias ampliadas y la copia. Sin
  migraciones nuevas, modelos, API/tipos ni cambios de historiales/snapshots. README y ARCHITECTURE retiran el límite
  del actualizador ausente; el verificador del wheel incluye el recorrido, pendiente de ejecutar en T009.
- Evidencia offline sintética: `0022`→`0023` con formatos 1–8, proyección verificada e historiales/contextos/versiones
  intactos; revisiones antiguas; negativas y fallos. La prueba de `serve` supera su guardia sin arrancar un servicio.
  Sin instalación real migrada, proveedores, smokes ni operación del hijo de P009.

## D151 — P010-T008: validación real complementaria aplazada

Estado: completada el 2026-10-22. Fase: P010.
[Propuesta y alcance](archive/phase-010/P010-T008_PROPUESTA_VALIDACION_REAL.md). Decisión explícita del usuario en el bucle
HITL: «Aplazar y conservar los límites de validación real». Resuelve la elección pendiente de D141, D148 y D149.

- Se aplazan la validación real de importaciones A/B y la del perfil Python/Django declarado de D095. La propuesta
  concreta dos repositorios sintéticos, una pareja, una tarea B/D095 y un techo de 21 llamadas, sin ejecutarlos.
  Rutas, modelos y demás parámetros operativos quedan sin elegir; no se añade una tarea operativa ni autorización.
- Alcance anunciado: A/B y D095 implementados y verificados offline con agentes/herramientas falsos, sin uso real.
  La receta Django conserva su evidencia histórica D139 (macOS arm64/Python 3.13), sin extrapolarla al perfil
  declarado. Chat, backup/restauración y receta TypeScript conservan también su falta de uso real.
- T009 puede verificar el paquete y emitir el dictamen en ese alcance, conservando los límites; T010 sigue
  condicionado a un dictamen favorable. Aplazar no equivale a validar ni a declarar terminada la versión.
- Se sincronizan STATE, NEXT_STEPS, ROADMAP, seguimiento de la matriz y las dos filas de alcance de README.
  Sin cambios de producto, comandos operativos, proveedores, instalaciones, servicios, push o publicación;
  no se opera P009 ni se reutiliza su consentimiento. Una validación real futura exige tarea y consentimiento propios.

## D152 — P010-T009: paquete final verificado y dictamen favorable

Estado: completada el 2026-10-22. Fase: P010.
[Verificación final](archive/phase-010/P010-T009_VERIFICACION_FINAL.md), [revisión de salida](archive/phase-010/P010_REVIEW.md) y
[evidencia saneada](archive/phase-010/P010-T009_EVIDENCE.json). Base `d6a69c8`, producto sin cambios desde `dd7b958`.

- El usuario autoriza expresamente («Autorizo.») el alcance presentado en T009 §1: construcción e instalación
  offline del wheel en venv temporal, verificador con puertos falsos y servicios de loopback y QA con API sintética.
  No incluye proveedores reales ni la instalación operativa; D151 permanece vigente.
- Checks finales: 1682 pytest, 121 subtests, dos variantes opt-in omitidas; 12 unittest, 82 Node, tipos, build y
  Alembic temporal correctos. No reaparece el intermitente de T007; pasan las lecturas acotadas T003/T011.
- Wheel `0.1.0` con UI y migraciones verificado fuera del checkout: instalación por hashes, sesión/CSRF,
  `migrate` `0022`→`0023` con copia previa, definición D088, tarea/commit/reinicio idempotentes y backup/restauración
  de consulta. SHA-256: `94a6699e7c2e36cc42bcf45e1e2feb4d2028aa722756b47cb862087919792b17`.
- QA de escritorio con 102 assets idénticos a los del wheel y respuestas sintéticas: preparación TypeScript,
  marcadores, fases abierta/cerrada/sucesora/deriva, documentos, ciclos/diff/JUnit y métricas. Doce capturas saneadas;
  sin hallazgos de producto. No se anuncia integración navegador/backend ni validación real adicional por esta QA.
- Dictamen favorable para los siete criterios de ROADMAP en el alcance declarado. La matriz de trece criterios
  conserva evidencia y límites. T010 queda como siguiente tarea; T009 no cierra ni archiva P010, cambia versión,
  crea tag, publica u opera este repositorio con el harness. Sin cambios de código, esquema, API o flujos.
- Servicios y pestaña temporales detenidos/cerrada; doce SQLite sintéticas sin jobs pendientes ni locks. Wheel y
  logs locales conservados; entorno del verificador limpiado. Sin configuración global, P009/ReferenceProject o proveedores.

## D153 — Cierre documental de P010 y de la primera versión local

Estado: cerrada y archivada el 2026-10-22 por la continuación solicitada por el usuario, tras D152. Fase: P010.
[Resumen](archive/phase-010/SUMMARY.md), [revisión](archive/phase-010/REVIEW.md) y
[registro de cierre](archive/phase-010/P010_CIERRE.md). Precedentes: D002/D088/D114/D140.

- La petición de continuar la siguiente tarea y finalizar con un commit en inglés autoriza T010, identificada
  en STATE/NEXT_STEPS. T009 ya emite dictamen favorable para los siete criterios; la matriz global acredita
  los trece en su alcance y D151 resuelve explícitamente el aplazamiento real de A/B y del perfil D095.
  Las doce tareas quedan completadas; no hay tareas obligatorias pendientes del alcance declarado.
- Se completa la primera versión local con esos límites: paquete `0.1.0`, fuente de producto `dd7b958` y wheel
  verificado en T009, sin cambio de versión, tag ni publicación. La evidencia real sigue siendo histórica;
  el cierre documental no amplía garantías a recorridos con proveedores ni a otras plataformas.
- STATE, NEXT_STEPS y todos los artefactos originales de `docs/phase/` se conservan por bytes respecto de
  `2e46c71`; MANIFEST registra origen/destino, tamaño y SHA-256. SUMMARY/REVIEW/P010_CIERRE nuevos sintetizan
  entregas, paquete y límites. Los snapshots conservan sus estados y enlaces en el contexto original.
- STATE compacta la base, NEXT_STEPS queda sin tareas y ROADMAP enlaza P010 completada. Las referencias vigentes
  se reubican, sin reescribir P001–P009 ni el contenido de decisiones históricas. Sin sucesora definida,
  el usuario elige la próxima prioridad; las candidatas siguen en ROADMAP.
- Cierre manual del repositorio, separado del check READY del producto: sin registrarlo ni ejecutarlo con el
  harness, operar el Django hijo, agentes, proveedores, servicios o smokes. Sin cambios de producto, esquema,
  API, flujos, dependencias o configuración global; sin push, publicación ni ampliación de consentimientos.

## D154 — P011: preparación para apertura pública en GitHub

Estado: fase planificada el 2026-10-22 por encargo explícito del usuario; dieciocho tareas pendientes.
[Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md), [tareas](archive/phase-011/NEXT_STEPS.md) y
[criterios](ROADMAP.md#p011--preparación-para-apertura-pública-en-github). Precedentes: D051, D088, D119,
D122/D124, D143 y D151–D153.

- El usuario pide preparar el paquete para abrirlo en GitHub y encarga crear una fase con tareas, permitiendo
  añadir/modificar las propuestas: inglés de comentarios/código, elección en/es, CLI más compatibles, paridad
  semántica de diagramas y README completo. Esta entrega documenta el plan, sin ejecutar sus tareas.
- Se divide traducción por grupos (núcleo/perfiles, backend/recetas, cliente/herramientas y tests/fixtures), con
  inventario previo por archivo y revisión de identificadores españoles. No se presume que existan nombres que
  renombrar ni se traduce contenido arbitrario como si fuera comentario. Prompts originales ingleses y editables.
- Se planifica preferencia de UI independiente de lengua por proyecto, ambas en/es; inglés para nuevos usuarios/
  proyectos y conservación del español anterior donde corresponda por compatibilidad. La lengua efectiva se
  congela por intento; cambiarla no reescribe documentos, prompts personalizados, catálogos ni evidencias previas.
  La solución i18n React/Python, formatos y migraciones se concretan en T001 antes de implementar.
- La compatibilidad CLI se amplía mediante mínimos/familias/capacidades por proveedor/rol, distinguiendo
  verificadas/candidatas y preservando permisos, confianza, memoria y recuperación. T011 fija mínimos y
  comprobaciones con evidencia; no se promete aceptar cualquier CLI futura ni se retiran guardias por conveniencia.
- La traducción respeta huellas de recetas, protocolos y archivos históricos. T001 define el tratamiento compatible
  de fuentes ligadas a recibos; ADR e historia conservan el original y pueden tener una guía inglesa sin segundo
  registro de decisiones. La convención española actual no se presenta aún como cambiada en el producto.
- Se añaden licencia/titularidad, revisión de contenido e historial publicables, metadatos/versionado, CI sintética,
  primer uso desde clon limpio y QA del paquete exacto. Licencia y versión pública se deciden en sus tareas;
  no se eligen términos legales ni `1.0.0` por efecto de planificar. Un hallazgo histórico no autoriza reescritura.
- Nueve criterios de salida, dieciocho tareas y dictamen previo al archivo. D151 sigue vigente; nuevos proveedores,
  smokes, instalaciones/red/servicios o caracterizaciones reales requieren su alcance/autorización propios.
  No se opera este checkout con el harness ni el Django de P009, toca configuración global, hace commit/tag/push,
  cambia visibilidad o publica. El cierre prepara un expediente; la acción remota posterior exige instrucción explícita.

## D155 — P011: retirada del harness anterior y dos vías de alta

Estado: ampliación de planificación solicitada por el usuario el 2026-10-22; retirada pendiente de P011-T019.
[Tareas](archive/phase-011/NEXT_STEPS.md), [plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md) y
[criterios](ROADMAP.md#p011--preparación-para-apertura-pública-en-github). Amplía D154 y sustituye para el producto
público futuro el soporte al harness anterior de D012–D014/D027/D088; conserva su historia y evidencia.

- El usuario pide eliminar funcionalidades del harness anterior porque no estarán disponibles para usuarios de
  GitHub, manteniendo exactamente dos vías: crear desde cero o adaptar un repositorio existente para my_harness.
  Se planifica retirar visor/observación/importación legacy, activación desde el motor anterior y normalización A;
  el alta B desde código sin harness y la creación nueva permanecen, ambas con seguimiento gestionado.
- La retirada incluye UI/navegación/rutas, API, comandos `legacy-import`/`legacy-summary`, observadores y SSE/feeds
  legacy, configuración, prompts y módulos/tests/fixtures exclusivamente dedicados al soporte retirado. No basta
  ocultar enlaces ni dejar un flag que reactive la funcionalidad. Rutas antiguas se rechazan sin efectos.
- Registrar/reabrir proyectos ya gestionados es operación normal, no un tercer origen. Se mantiene compatibilidad
  de historiales propios/configuraciones/recibos donde siga siendo necesaria; no confundirla con visor legacy.
- B comparte `project_imports`, `purpose = import_commit`, repositorios y escritor Git con A. T001 inventaría
  dependencias y T019 conserva/reubica las necesarias: no se eliminan por nombre ni se destruyen datos, tablas,
  revisiones Alembic, archivos históricos o backups automáticamente. Jobs del modo retirado no se ejecutan ni
  se reinterpretan como B; se define su resolución y se conserva evidencia.
- Se añade T019 tras T002 y antes de T003, manteniendo numeración/enlaces anteriores; P011 queda con diecinueve
  tareas y diez criterios de salida. Traducción, idiomas, diagramas, README, paquete y QA excluyen soporte retirado
  y verifican cero/B y ausencia de entrypoints/observadores legacy. T017 depende también de T019.
- T019 actualizará SPECIFICATION F03/F05, modos/importación y criterios globales 1/11/13: idempotencia cero/B,
  incorporación existente conservada y observación gestionada por cursor, sin reescribir la matriz histórica P010.
  D151 mantiene pendiente validación real B/D095; A queda fuera del futuro alcance, sin considerarse validado.
- Esta entrega solo amplía documentos: no elimina código ni altera datos/modelos/flujos/contratos vigentes,
  no invoca proveedores, smokes o servicios, hace commit/tag/push ni publica. La base sigue describiendo lo
  implementado hasta que T019 complete su retirada y paridad en una entrega propia.

## D156 — Planificación de P011 finalizada y modo continuo aplazado a v0.2.0

Estado: decidido por el usuario el 2026-10-22; planificación finalizada, ejecución de P011 pendiente.
[Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md), [tareas](archive/phase-011/NEXT_STEPS.md) y
[horizonte v0.2.0](ROADMAP.md#después-de-la-apertura-en-github--v020). Precedentes: D034, D091 y D154/D155.

- Tras comprobar los límites actuales, el usuario aplaza a v0.2.0, después de subir/abrir el proyecto en GitHub,
  el modo continuo entre fases: tareas, commits, check, cierre/archivo, planificación y ejecución de la siguiente
  fase cuando no haya error ni HITL. Es una capacidad futura no implementada y fuera de P011.
- La automatización futura será opcional con autorización inicial acotada, alcance/presupuesto y parada por
  error, bloqueo, pregunta o límite; deberá conservar READY, aceptación por contenido e intención/recuperación.
  No se diseña ni habilita aquí, no se añade fase sucesora ni se cambia la versión del paquete `0.1.0`.
  T015 respetará la reserva de v0.2.0 para después de la apertura inicial.
- D034/D091 siguen vigentes: lote desatendido para tareas/commits, check explícito, cierre autorizado sobre READY,
  archivo y apertura mecánica de sucesora sin tareas, y confirmación propia del plan posterior. No se traslada
  código del comando legacy ni se reintroduce el soporte retirado por D155.
- El usuario pide un commit en inglés que cierre la planificación de «Publicar en GitHub». Autoriza el commit
  documental del plan P011 y sus ampliaciones, no completar/archivar la fase, ejecutar tareas o publicar.
  Se mantienen diecinueve tareas pendientes y diez criterios; siguiente P011-T001.
- Se conservan decisiones/archivos históricos; sin cambios de producto, modelos, flujos implementados,
  dependencias o configuración global, sin agentes/proveedores/smokes, servicios, tags, push, publicación o cambio
  de visibilidad. Checks documentales y revisión del diff antes del commit; las suites del producto no aplican.

## D157 — Repositorio público nuevo y continuidad del desarrollo

Estado: preferencia adoptada para la planificación por el usuario el 2026-10-22; sin exportación ni publicación.
[Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md), [tareas](archive/phase-011/NEXT_STEPS.md). Afina la frontera pública de D154/D156.

- El usuario prefiere el segundo modelo: conservar privado el historial/documentación anteriores y, desde la
  publicación, desarrollar código, documentación, decisiones y fases en el repositorio público, útiles para
  usuarios/forks y sus agentes. No congelar ni excluir permanentemente `docs/` de las versiones públicas.
- P011 preparará una instantánea inicial permitida/revisada con nueva raíz Git independiente y docs públicas
  nuevas suficientes para explicar estado, arquitectura, decisiones de partida y contribución. No copiar `.git`,
  objetos/refs/tags, historia privada, ADR/fases/evidencias internas ni referencias que exijan acceso a ellas.
  No reescribir ni borrar la historia de este checkout para lograrlo.
- Tras abrir, repositorio público como fuente principal de código/docs y cambios mediante commits/PR públicos;
  este checkout conserva historia/archivo privado. No mantener dos desarrollos activos con copias que sobrescriban
  contribuciones. La correspondencia entre origen privado y candidato se registra privadamente al preparar el corte.
- T001/T002 definen frontera/inventario; T014 redacta contexto público nuevo; T015/T016 preparan/verifican el árbol
  candidato y T017 revisa la transición. Solo publicar lo revisado con licencia/evidencia adecuadas; la decisión
  no crea repositorios, autoriza push/cambio de visibilidad ni ejecuta el harness sobre este checkout o su futura copia.
- Siguen diecinueve tareas y diez criterios; ninguna implementación iniciada. D156 y la reserva de automatización
  para v0.2.0 siguen vigentes. No se hace otro commit por esta ampliación sin nueva petición.

## D158 — Idioma visual global y trabajo inmutable por proyecto

Estado: requisitos afinados por el usuario el 2026-10-22; diseño/implementación pendientes en P011.
[Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md), [tareas](archive/phase-011/NEXT_STEPS.md). Sustituye el idioma mutable por proyecto
y la asociación de conversación al trabajo propuestas en D154; conserva prompts originales ingleses y snapshots.

- Dos ajustes/defaults globales del producto: `ui_language` y `default_work_language`, en/es e inicialmente en.
  Cambiar el default de trabajo afecta solo a futuras altas. Persistencia/precedencias/formato se concretan en T001;
  no se edita configuración global del equipo ni se presupone escribir TOML desde UI.
- Visual global, mutable, no un ajuste por proyecto: UI, mensajes y conversación con el agente, sus respuestas
  al usuario y preguntas HITL. La persona puede conversar en español mientras todo el trabajo técnico es inglés.
- Trabajo por proyecto elegido explícitamente al crear/incorporar a partir del default global, ligado a la
  confirmación de alta y después inmutable por UI/API/configuración. Rige documentación/planes/ADR y código/
  comentarios nuevos que lee/escribe el agente; proyecto público my_harness se establece en inglés. Proyectos
  previos preservan contratos/semántica, con migración explícita antes de futuras operaciones sin inferencias de idioma.
- No impedir leer fuentes previas en otro idioma ni traducir automáticamente archivos, datos de usuario o logs.
  No traducir keywords, nombres públicos, formatos, rutas canónicas, comandos o códigos técnicos por el locale;
  no impone idioma funcional a la aplicación hija ni una reducción fija de tokens.
- Congelar ambas lenguas al admitir cada job/turno, con directivas y procedencia en intentos/prompts: el cambio
  visual rige nuevas interacciones, no modifica una llamada activa, jobs pendientes/reintentos, aceptaciones o
  respuestas pasadas. La misma conversación puede tener nuevos turnos en otro visual sin cambiar trabajo.
- Prompts originales en inglés y personalización conservada. Directiva del motor tipada, conceptualmente
  `Respond to the user in {ui_language}. Write project documentation and code in {work_language}.`, por el canal
  de instrucciones disponible de Codex/Claude, sin asumir flags/system prompts comunes inexistentes ni ampliar permisos.
  Campos humanos en visual y borradores/código/contenido técnico en trabajo, incluso dentro de una misma respuesta.
- T001 y T007–T010 se ajustan: defaults globales, selector visual, alta de trabajo inmutable, rechazo de cambios,
  snapshot de ambos idiomas y pruebas de las cuatro combinaciones/concurrencia/compatibilidad. Modelos/flujos/API
  con paridad al implementar; hoy solo cambian documentos del plan, sin proveedores, servicios, instalaciones,
  código, esquema, nuevos commits o publicación.

## D159 — P011-T001: contrato de idiomas, fuentes y corte público

Estado: diseño documentado el 2026-10-22 al ejecutar T001 por petición del usuario; sin implementación de producto.
[Contrato](archive/phase-011/P011-T001_CONTRATO_APERTURA.md), [inventario](archive/phase-011/P011-T001_INVENTARIO.md).
Concreta D154–D158; conserva las guardias de D027, el layout D088 y las huellas/recuperación D119/D143.

- T001 inventaría los 688 archivos de `2730f54`: 469 filas individuales y 219 archivos históricos agrupados,
  con propietaria, idioma/candidatos, tratamiento y excepciones. No equivale a traducción, retirada legacy,
  auditoría de privacidad/derechos o validación pública. La petición actual autoriza su commit local en inglés.
- Preferencias globales por instalación/base SQLite: `ui_language` y `default_work_language`, en/es, iniciales
  en/en, mutables con CAS y auditoría; sin TOML global ni autoridad de navegador. Catálogos JSON por ámbito
  React/Python, claves/parámetros controlados, fallback inglés, Intl en cliente y datos técnicos estructurados;
  sin dependencias nuevas ni `.po`. API conserva códigos y evidencia original; override CLI explícito por invocación.
- Trabajo elegido al alta/confirmación por hash y asociado una vez a la identidad/raíz del proyecto, también
  para proyectos TOML. SQLite manda tras asociarlo; cambios por UI/API/TOML o baja/reapertura se rechazan.
  T008 añadirá `local-config-6`, conservando lectura/hashes 1–5. Proyectos previos sin valor requieren selección
  explícita antes de futuras operaciones; no inferirlo del idioma de archivos ni reescribirlos.
- `language-context-1` sella par/procedencia al admitir cada job/turno. Pendientes, intentos, revisiones y retries
  conservan su par; nuevo turno captura visual actual. El visual no cambia hashes de composición ni invalida
  aceptaciones. El contrato asigna campos humanos a visual y artefactos técnicos a trabajo, conservando
  literales/criterios originales. Directiva tipada del motor sellada en prompt por stdin de ambos proveedores,
  fuera de variables editables; sin flags nuevos ni cambios de permisos/confianza/memoria.
- Recetas v1 y recursos ligados a huellas permanecen por bytes/perfil como compatibilidad histórica. T004
  prepara v2 de Django/TypeScript con fuente inglesa; T008/T009 ligan nuevas altas y generación a trabajo.
  No sustituir v1 bajo su identidad, invalidar recibos por comentarios ni imponer idioma funcional a la app hija.
  Conservar lectores de historiales/catálogos antiguos y alias D088 en/es; nuevas formas se versionan, no rellenan
  snapshots antiguos con valores inventados. Conciliar una intención propia sellada conserva sus bytes.
- T019 retirará entradas A/legacy/observadores, extrayendo antes Git,
  escritor/adopción y guardias compartidas por B/preparación. `project_imports` y `purpose=import_commit` siguen
  compartidos; distinguir por origen/preview. Guardias mínimas de activaciones ACTIVE anteriores protegen
  solo trabajo gestionado, sin nuevas activaciones/reversiones ni visor/lector/indexador operativo. El esqueleto
  sintético propio H0 es independiente de legacy, no otra vía de alta, y no se elimina por D155.
- Datos/tablas/migraciones, historial propio y referencias de backup se conservan. Jobs A pendientes se
  rechazan/cuarentenan sin ejecutar intenciones; resolución explícita tras acreditar escritor detenido, sin
  reinterpretar como B ni borrar evidencia. PREPARING/REVERTING antiguos bloquean efectos y requieren resolución
  manual explícita. Restauraciones siguen de consulta, sin observadores ni reanudación del modo retirado.
- Corte público inicial por lista positiva de archivos exactos revisados: fuentes/recursos/tests sintéticos y
  herramientas vigentes, documentación pública nueva suficiente para usuarios/forks/agentes y nueva raíz Git.
  Excluir historia/ADR/fases/evidencias privadas y estado/cachés/credenciales; correspondencia privada por hashes.
  Desde la apertura, código/docs/decisiones/fases evolucionan en el repositorio público como fuente principal,
  sin dos desarrollos sincronizados por copias. No se crea/exporta/publica un candidato en T001.
- Diez criterios con tareas/evidencias pendientes; licencia/titularidad (T002), mínimos CLI (T011), versión
  candidata (T015) y ensayos (T016) siguen en sus tareas. Checks estáticos de inventario, fuentes, parsers,
  enlaces/presupuestos e integridad/diff; sin suites, servicios, proveedores, instalaciones o red.

## D160 — P011-T002: licencia MIT y frontera del contenido publicable

Estado: adoptada el 2026-10-22 al ejecutar T002 por petición del usuario; revisión estática del origen completada,
sin candidato ni dictamen de preparación pública. [Informe](archive/phase-011/P011-T002_CONTENIDO_PUBLICABLE.md),
[inventario privado](archive/phase-011/P011-T002_INVENTARIO.tsv) y [dependencias](archive/phase-011/P011-T002_DEPENDENCIAS.tsv).
Concreta D154/D157/D159; no autoriza publicación o reescritura de historia.

- El usuario delega explícitamente en esta sesión la elección de licencia/canal y confirma David Acosta como
  titular público. Se elige MIT (copyright 2026 David Acosta), por permitir reutilización/distribución con términos
  breves y conservación del aviso. La delegación resuelve la elección humana de T002 antes de redactar términos.
  LICENSE, metadatos de licencia/autor y guías CONTRIBUTING/SECURITY inglesas entregados, sin publicar el correo
  facilitado para la identidad ni inventar contactos, entidad, SLA, bounty o soporte de versiones.
- Canal elegido: reportes privados de vulnerabilidades de GitHub del futuro repositorio, con fallback de pedir
  canal privado por issue sin detalles. SECURITY no activa la función: el propietario debe habilitarla y verificarla
  antes de abrir; expediente remoto de T015/T017, sin operación de cuenta/repo ahora. Solo se consultaron fuentes
  oficiales de MIT/GitHub; escaneo local sin enviar contenidos, instalaciones, servicios o proveedores.
- Base de 690 archivos y 4.009 objetos alcanzables (145 commits, incluidos refs remotos/checkpoints locales)
  escaneada. No se identifican credenciales reales en los patrones usados; las coincidencias genéricas son
  centinelas sintéticos. Se constatan rutas/identidad/referencias/evidencia privadas; no se declara publicable el
  origen. D157 las resuelve mediante exclusión explícita del historial y nuevo árbol/Git revisados, sin borrar refs,
  reescribir commits/snapshots o confundir ignore con saneamiento. Reflogs/inalcanzables/estado ignorado y formatos
  de secreto no reconocidos quedan fuera de la garantía del escaneo finito.
- Inventario exacto privado por ruta/hash/disposición: 244 exclusiones privadas, 99 fixtures legacy a retirar
  tras contraste T019, siete archivos a sustituir y 340 candidatos a revisar, ninguno aprobado para copiar
  automáticamente. Ayudas reales de CLI se conservan privadas: T006/T012 deben reemplazar su cobertura pública
  con fixtures sintéticos, sin asumir licencia de redistribución por ser texto público. Docs/instrucciones nuevas
  en T014; fuente/recursos técnicos conservan la compatibilidad congelada de T001. Este informe/censo no se exporta.
- Avisos de terceros de las 123 entradas runtime frontend conservados en NOTICE-THIRD-PARTY: 129 textos de
  upstream, 69 contenidos distintos, lock/hash y procedencia por paquete. Khroma MIT acreditado por su archivo
  local aunque el lock omita licencia; fastdom/strictdom la contienen en README. Se preservan alternativas de
  DOMPurify y copyrights, sin relicenciar terceros bajo MIT del proyecto ni cambiar locks/dependencias.
- Censo de 247 entradas separa runtime, build y recetas externas. Hay 19 sin términos de versión exacta en
  evidencia local (colorama, 17 de receta Django y uv_build), no vendorizadas: ausencia declarada, sin atribuirles
  licencia de memoria. T015 debe acreditar/conservar términos de cualquier material que distribuya, verificar
  assets/fuentes incorporados y completar avisos/metadatos del paquete; los textos fuente no certifican un bundle.
- Los dos wheel/sdist locales antiguos son evidencia estática, sin ejecutar: contienen legacy, faltan avisos y el
  sdist conserva un `.orig`; excluidos del candidato, sin borrarlos. El staging actual no copia LICENSE/NOTICE;
  su integración explícita y comprobación del candidato pertenecen a T015/T016, antes de distribuir.
- Sin cambios de comportamiento, API/modelos/flujos, fuentes de recetas o configuración global; sin suites,
  builds, proveedores/agentes, smokes, servicios, nueva copia, tags/push/publicación. El usuario autoriza el commit
  local en inglés de esta tarea; siguiente T019, sin encadenar su ejecución.

## D161 — P011-T019: retirada legacy/A y compatibilidad no destructiva

Estado: implementada el 2026-10-22 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Precedentes: D155/D159 y [contrato T001 §6](archive/phase-011/P011-T001_CONTRATO_APERTURA.md#6-retirada-legacya-frontera-de-código-y-datos).
[Informe, dependencias y validación](archive/phase-011/P011-T019_RETIRADA_LEGACY.md).

- Se retiran los módulos exclusivos del visor/índice/observación/SSE, activación/reversión y Flujo A, sus rutas,
  comandos, conversaciones, plantilla, UI, estilos y fixtures/tests exclusivos. URL UI antigua → no encontrada;
  API ausente → 404 tras guardias; CLI antigua → error de argumentos antes de SQLite. Sin flags de reactivación.
- Se conservan dos accesos: creación desde cero e incorporación de código sin harness (B); registro/reapertura
  normal de proyectos ya gestionados. B conserva `project_imports`, `purpose=import_commit`, perfil confirmado,
  intención, CAS y adopción P001. Guardias Git/blobs, DTO de árbol y borradores privados extraídos a módulos comunes.
- Tablas, revisiones 0001–0023, campos y datos previos no cambian. `watch_enabled` queda inerte; arranque y
  restauración no construyen observadores ni escanean/indexan fuentes externas. Backup verifica referencias
  selladas de snapshots/exportaciones; restauración solo de consulta y revisión compatible.
- Antes de construir puertos/procesos o comprobar el checkout, trabajos A o importaciones con conversación,
  fuente, flujo o petición contradictorios quedan en cuarentena. ACTIVE con lease vencido sigue recuperación
  conservadora. Confirmar detenido el propietario exacto comprueba procesos/grupos, cierra el job, libera el
  lock y registra motivo/evento, sin ejecutar ni modificar intención, operación o conversación retiradas.
  Una intención retenida sin resolver sigue bloqueando otro escritor; su resolución manual está fuera del flujo retirado.
- Activaciones PREPARING/REVERTING no se completan, abandonan ni revierten: bloquean para resolución manual.
  ACTIVE propia solo admite trabajo gestionado con marcador/manifiesto y copia íntegros y sin deriva legacy;
  guardia extraída de solo lectura. Sus rutas de artefactos permanecen protegidas en registro/creación, sin servicio
  de migración activo. `import-project` se admite al leer catálogos congelados, nunca en el catálogo efectivo,
  edición, validación actual o render de invocación.
- SPECIFICATION F03/F05, modos, §8 y criterios 1/11/13, arquitectura, datos, flujos, README y OpenAPI/tipos al día.
  Sin cambios de modelos, migraciones, dependencias, recetas/recibos, configuración global o historia congelada.
  Checks sintéticos offline y manifiestos fuente en el informe; sin servicios de producto, navegador, proveedores,
  smokes, instalación operativa, push, publicación o consentimientos nuevos. T003 queda como siguiente tarea.

## D162 — P011-T003: núcleo y perfiles en inglés sin cambiar comportamiento

Estado: implementada el 2026-10-22 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Precedentes: D158/D159 y [contrato T001 §5](archive/phase-011/P011-T001_CONTRATO_APERTURA.md#5-fuentes-congeladas-recetas-documentos-y-compatibilidad).
[Inventario resuelto y validación](archive/phase-011/P011-T003_INGLES_NUCLEO.md).

- Los 35 archivos Python de `core/**` y `profiles/**` quedan con comentarios y docstrings en inglés (123 líneas
  de comentario, 121 docstrings), incluidos `tree.py`/`managed_mode.py` de T019 y el docstring restante de
  `import_commit.py`. Sin identificadores españoles que renombrar.
- Regla aplicada: T003 traduce solo comentarios/docstrings. Ningún literal cambia: mensajes visibles → T007/T010,
  prosa generada/prompts/esquemas → T009, alias del parsing bilingüe D088 y comandos de chat se conservan, y los
  valores de `ProjectProfile` permanecen porque `asdict(profile())` entra en la huella de recetas v1.
- Evidencia de comportamiento: AST idéntico por archivo antes/después con docstrings vaciados; suites existentes
  pertinentes. Sin tests nuevos que solo comprueben comentarios. T004 es la siguiente tarea.

## D163 — P011-T004: backend en inglés y recetas v2 sin cablear

Estado: implementada el 2026-10-22 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Precedentes: D159/D162 y [contrato T001 §5](archive/phase-011/P011-T001_CONTRATO_APERTURA.md#5-fuentes-congeladas-recetas-documentos-y-compatibilidad).
[Inventario resuelto y validación](archive/phase-011/P011-T004_INGLES_BACKEND.md).

- Los 94 archivos Python de `src/harness_local/**` fuera de `core/**`/`profiles/**` quedan con comentarios y docstrings
  en inglés (223 líneas de comentario, 318 docstrings), migraciones incluidas sin tocar ids/DDL. Las 84 descripciones
  `description=` de la API son técnicas: se traducen y `openapi.json`/`api.generated.ts` se regeneran (E3).
  Sin identificadores españoles que renombrar; AST idéntico con docstrings/descripciones vaciados.
- Literales sin cambios: 555 candidatos residuales inventariados por archivo, mensajes visibles → T010 (CLI también
  T011), prosa generada/prompts → T009, comandos bilingües D088 conservados. Fuentes v1 de receta (`django.py`,
  `typescript_web.py`, lock/paquetes) y perfil `typescript-web` conservan bytes y huellas, ahora fijadas por test.
- HITL del usuario: T004 añade `recipes/django_2.py` (`django-recipe-2`) y `recipes/typescript_web_2.py`
  (`typescript-web-recipe-2`) autónomos y en inglés, sin cablear: no figuran en `recipes.RECIPES`, `by_version` ni
  en la preparación hasta `local-config-6` (T008). Scaffold con prosa técnica según trabajo en/es (docstring del
  modelo Django; descripción del test TypeScript); con `es`/`en` respectivamente igualan los bytes v1.
- Los defaults funcionales del hijo (`LANGUAGE_CODE = "es"`, `<html lang="es">`, textos visibles) se conservan en v2
  por decisión del usuario conforme a §5; no derivan del idioma visual ni del de trabajo.
- Pasos v2 con efectos idénticos a v1, `id` estable y `label` humano en inglés; T008 debe despachar comprobaciones
  por `id`, no por etiqueta. Huella v2 = versión, trabajo, scaffold/manifiesto, closure Django, perfil efectivo y
  fuente del módulo; idioma inválido → `ValueError`. Perfil TypeScript v2 propio (etiqueta JUnit inglesa) para
  que cambios futuros del integrado no alteren su identidad; Django v2 solo cambia instrucciones del ejecutor.
- Sin cambios de modelos, migraciones, flujos, configuración, dependencias, recibos o historia congelada.
  Checks offline en el informe; sin agentes, proveedores, servicios, preparaciones reales ni red. T005 es la siguiente.

## D164 — P011-T005: cliente, scripts y ejemplos en inglés

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Precedentes: D159/D162/D163 y [inventario T001](archive/phase-011/P011-T001_INVENTARIO.md) (U, H, E3, E6, E8).
[Inventario resuelto y validación](archive/phase-011/P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md).

- Comentarios del frontend en inglés: 195 líneas en 27 archivos TS/TSX (JSDoc y `{/* */}` incluidos) y 17
  comentarios CSS. Flujo de tokens sin comentarios idéntico a `HEAD` en los 38 archivos y CSS sin comentarios
  idéntico; sin identificadores españoles. Cadenas visibles, ARIA, formatos es-ES y `<html lang="es">` quedan
  inventariados para T010 (1240 candidatos); comandos de chat bilingües conservados; OpenAPI/tipos y lock intactos.
- HITL del usuario: los mensajes propios de los scripts de mantenedor (`dev.py`, `toolchain.py`,
  `check_distribution.py`, ayudas argparse) se traducen ya, porque no tienen catálogo y T010 no incluye
  `scripts/**`. Se conservan, con comentario a su origen, las cadenas que casan con salida del producto
  (`clave de acceso en`, `módulo:atributo`, `Esquema SQLite`). Nota abierta: T010 debe actualizar esos scripts
  cuando traduzca los mensajes origen; su planificación ampliará rutas o hará los scripts independientes del idioma.
- HITL del usuario: descripción del paquete «Local application that orchestrates Codex and Claude Code agents to
  plan, implement, review and commit tasks in Git repositories»; versión y resto de metadatos siguen en T015.
- Ejemplos vigentes (`local_config`, fragmentos de receta, `managed_demo.py`) en inglés con placeholders sintéticos
  ingleses; datos TOML idénticos salvo esos placeholders y la etiqueta JUnit del perfil de ejemplo. Guiones
  históricos E6 (`first_use`, `provider_matrix`) conservan bytes, fuera del corte público y sin presentarse como
  instrucciones actuales. Referencias internas (Hx.y, DNNN) en comentarios se mantienen como en T003/T004 (T014).
- Sin cambios de modelos, migraciones, flujos, API, dependencias o configuración global. Checks offline en el
  informe; sin servicios, construcción/instalación del paquete, agentes, proveedores ni red. T006 es la siguiente.

## D165 — P011-T006: pruebas y fixtures en inglés sin tocar datos

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Precedentes: D159/D162–D164 y [inventario T001](archive/phase-011/P011-T001_INVENTARIO.md) (F, E2).
[Inventario resuelto y validación](archive/phase-011/P011-T006_INGLES_PRUEBAS.md).

- Comentarios y docstrings de las pruebas Python en inglés: 294 comentarios y 91 docstrings en 49 archivos, con
  AST idéntico (docstrings aparte). Comentarios y cinco nombres de test de `frontend/tests` en inglés. Único
  identificador español renombrado: `test_task_command_is_idempotent_proposal_without_snapshot_or_agent`; el
  comando `tarea` y sus expectativas se conservan.
- Se traducen también los textos propios de las pruebas que no son expectativas ni datos: un diagnóstico de
  `AssertionError`, dos excepciones sintéticas junto con su `match=` y dos motivos de `pytest.skip`.
- Se conservan expectativas de mensajes del producto (cambian con su origen en T009/T010), campos bilingües
  D088, comandos de chat, contenido sintético de usuario, sondas Unicode y los datos de fixtures: streams,
  manifest, ayudas reales de CLI y texto visible de la app hija `typescript_web`. Las referencias internas
  (Hx.y, DNNN, `docs/archive`) quedan para T014.
- HITL del usuario: los README de `tests/fixtures/{cli_help,streams,typescript_web}` se traducen; son descripción
  y no datos, aunque `streams/` sea E2, y ninguna prueba hashea sus bytes.
- Sin cambios de modelos, migraciones, flujos, API, dependencias ni configuración global. Suites offline en verde
  con los mismos totales que en T005; sin servicios, agentes, proveedores ni red. T007 es la siguiente.

## D166 — P011-T007: preferencias globales de idioma, catálogos y visual congelado por job

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D158/D159 (§2–§4 del [contrato T001](archive/phase-011/P011-T001_CONTRATO_APERTURA.md)).
[Entrega, alcance y validación](archive/phase-011/P011-T007_INFRAESTRUCTURA_IDIOMAS.md), [flujo](flows/language-preferences.md).

- HITL del usuario sobre el reparto T007/T008/T009: T007 congela **solo el visual** por job en
  `managed_jobs.language_context` (`ui-language-1`: idioma y versión de preferencias), en la transacción de admisión
  de las siete vías de alta de jobs. T008 añadirá trabajo y llevará el par `language-context-1` a intentos/prompts;
  T009, la directiva al agente. Hasta entonces el visual congelado es procedencia y los agentes no cambian de idioma.
- Nueva acción (tarea, turno, check, commit u otra sobre un resultado anterior) captura el visual vigente. Las
  continuaciones del mismo run (reintento del ejecutor, revalidación y reanudaciones de bootstrap, importación,
  exportación y edición documental) copian el valor del primer job del run, también null, sin recapturar.
- Migración `0024_product_preferences`: fila singleton `product-preferences-1` con CHECK en/es, sembrada en/en
  versión 1, y eventos con `Idempotency-Key` y cadena de hashes. Leer no crea ni repara; una fila inválida se lee
  como inglés con estado `invalid` y bloquea admisiones (409 `preferences_invalid`) hasta un guardado explícito.
  Downgrade rechazado solo si hay eventos: sin ellos toda captura es `en` de fábrica y no se pierde una elección.
- API `GET/PUT /api/managed/preferences` con CAS, idempotencia y códigos `preferences_conflict`/`idempotency_conflict`;
  los jobs exponen `language_context`. Diagnósticos propios de sesión y preferencias localizados con el visual
  guardado, sin cambiar códigos ni estados. OpenAPI/tipos regenerados.
- Catálogos JSON en/es sin dependencias: `harness_local/i18n` (Python, fallback inglés, campo ausente visible) y
  `frontend/src/i18n.ts` + `i18n/*.json` + `Language.tsx` (claves tipadas, interpolación como texto, `Intl` para
  números/fechas/plurales). La UI parte de una copia provisional en `localStorage` o inglés y relee el servicio en
  cada consulta de sesión y al recuperar el foco; la autoridad es SQLite.
- HITL del usuario: catálogos iniciales para shell, sesión y preferencias (navegación, migas, estado del supervisor,
  tema, página no encontrada y nueva página global `/preferences`); el resto, en T010.
- CLI `--ui-language en|es` por invocación; si no, preferencias de la base existente abierta en solo lectura, o `en`.
  Mensajes propios del lanzador/CLI localizados; `clave de acceso en`, `módulo:atributo` y `Esquema SQLite` siguen
  en español por su acoplamiento con los scripts (nota D164 para T010).
- Paridad: DDBB-DIAGRAM (50 tablas), flujo nuevo y notas en chat/tarea, ARCHITECTURE. Suites offline en verde; sin
  servicios, QA de navegador, agentes, proveedores ni red. T008 es la siguiente.

## D167 — P011-T008: idioma de trabajo inmutable por raíz y par congelado por job e intento

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D158/D159 (§2 y §4 del [contrato T001](archive/phase-011/P011-T001_CONTRATO_APERTURA.md)) sobre D166.
[Entrega, alcance y validación](archive/phase-011/P011-T008_IDIOMA_PROYECTO.md), [flujo](flows/project-work-language.md).

- HITL del usuario sobre el alcance: el cableado de las recetas v2 (`django-recipe-2`, `typescript-web-recipe-2`,
  despacho por `id`) sale de T008 a una tarea nueva, **T020**, antes de T009. Mientras tanto `local-config-6` no
  admite `[recipes]`: quien prepare con receta sigue en `local-config-5`, sin cambiar la semántica futura de v6.
- Migración `0025_project_work_languages`: tabla `project_work_languages` con una fila por raíz canónica
  (`work-language-1`: valor en/es, `project_id`, origen `registration|creation|toml|migration`, confirmación y hash),
  escrita una vez y nunca actualizada ni borrada; `managed_attempts.language_context` copia el par del job.
  Downgrade rechazado si hay alguna fila. Sin FK: la raíz sobrevive a bajas, cambios de id y proyectos TOML.
- Alta: `work_language` obligatorio en registro (B) y creación (`project-creation-2`), inicializado en la UI desde el
  default global. El hash de la vista previa sella solo el valor elegido y la asociación existente; el default y su
  versión son procedencia en `confirmation`, así que cambiarlo entre vista previa y confirmación no altera el valor.
  La fila se escribe en la misma transacción que registra el proyecto. Una raíz ya asociada solo admite su valor
  (la reapertura conserva la fila original). Cambios/bajas con `work_language` → 409 `work_language_immutable`.
- HITL del usuario: un TOML `local-config-6` con `[[projects]].work_language` se asocia **al arrancar el servicio**
  (`toml`, con el hash del TOML); la carga sigue sin efectos. Otro valor para una raíz ya asociada detiene el
  arranque. v6 sin la clave, v1–v5 y registros previos quedan sin valor hasta una confirmación explícita.
- Confirmación explícita (ausente → valor), por HITL con API y UI mínima en Ajustes: `POST …/work-language/preview`
  y `…/work-language` con hash, motivo obligatorio y sin trabajo sin terminar ni bloqueos de configuración. No
  traduce, renombra ni inspecciona archivos. El usuario indica que no existen proyectos previos (paquete sin uso real).
- Admisión: cada job nuevo sella `language-context-1` (visual actual, versión de preferencias, trabajo, origen y hash
  de la fila) en su transacción; sin fila → 409 `work_language_required` sin encolar nada. Las continuaciones copian
  el contexto del primer job del run (también `ui-language-1` o null), y cada intento copia el de su job.
  `ProjectContext.work_language` entra en `context_json` solo si existe (snapshots anteriores intactos); un
  contexto con otro valor se rechaza. El visual sigue fuera de hashes de composición.
- Pruebas: un fixture autouse de `tests/product/conftest.py` confirma `en` sintético (fila real) al instalar un
  proyecto o admitir el primer job, y retira solo esas filas antes de un downgrade de Alembic; las pruebas de la
  guardia lo desactivan con `@pytest.mark.unconfirmed_work_language`. Así las ~720 pruebas ajenas a idiomas no se
  reescriben y la guardia real se prueba aparte.
- Paridad: DDBB-DIAGRAM (51 tablas), flujo nuevo y nota en preferencias, ARCHITECTURE, SPECIFICATION (F23 parcial),
  OpenAPI/tipos regenerados, catálogos en/es de los mensajes y bloques nuevos. Sin directiva al agente (T009), sin
  traducción del resto de la UI (T010), sin servicios, QA de navegador, agentes, proveedores ni red. T020 es la siguiente.

## D168 — P011-T020: recetas v2 en local-config-6 con el idioma de trabajo sellado en plan y recibo

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D163 (módulos v2) y D167 (idioma de trabajo por raíz; T020 desglosada por HITL).
[Entrega, alcance y validación](archive/phase-011/P011-T020_RECETAS_V2.md), [flujo](flows/project-preparation.md#recetas-v2-por-idioma-de-trabajo-p011-t020-d168).

- Generaciones por formato: `[recipes.django]`/`[recipes.typescript-web]` con las mismas claves y validaciones
  seleccionan v1 en `local-config-5` y v2 en `local-config-6` (`recipes.GENERATIONS`); sin elección de versión en el
  TOML ni migración de v1 a v2. `by_version` resuelve ambas, de modo que planes/recibos v1 y v2 se leen y concilian
  con la clase de su versión sellada, sin recalcular ni reinstalar.
- Identidades: la composición no conoce el idioma de trabajo (en proyectos registrados lo fija SQLite, D167), así que
  `recipe_config_sha256` liga la configuración del operador y la huella v2 de **ambos** idiomas
  (`implementation_sha256_by_work_language`). El idioma concreto se sella donde se prepara: el plan lleva
  `work_language`, el hash de la fila y `recipe_sha256 = fingerprint(work_language)`, y el recibo los copia, así que
  `project_environment_sha256` de los jobs posteriores también los liga. v1 conserva `implementation_sha256`.
- Guardia: la vista previa v2 lee la fila de la raíz en su sesión y, sin ella, responde 409
  `work_language_required` antes de comprobar el checkout; antes de cada paso se compara de nuevo valor y hash con
  el plan. Un sucesor conserva los valores del plan original. Nada se infiere del contenido ni del default.
- Perfiles: una composición v6 con receta usa el perfil de su módulo v2 (Django con el formateador de D133;
  TypeScript con su copia propia), y el `typescript-web` integrado sigue para composiciones sin receta.
- Despacho por `id` estable (`python-version`, `installer-version`, `installed-versions`, `node-version`,
  `npm-version`, `create-environment`, `generate-*`, `migrate`, `validate-*`); v1 sigue por sus etiquetas
  congeladas mediante un mapa equivalente. La UI nombra los pasos v2 desde los catálogos en/es por `id` (visual)
  sin mutar el plan; los planes v1 muestran su etiqueta congelada. `PreparationPlanRead` añade `work_language` y
  `recipe_sha256` opcionales (OpenAPI/tipos regenerados).
- El idioma funcional del hijo (`LANGUAGE_CODE`, `<html lang>`, textos visibles) no deriva del visual ni del de
  trabajo (contrato T001 §5). Sin cambios de modelos/migraciones (DDBB-DIAGRAM intacto); flujo de preparación,
  ejemplos, ARCHITECTURE y catálogos actualizados. Sin servicios, QA de navegador, herramientas reales ni red.
  T009 es la siguiente.

## D169 — P011-T009: directiva de idioma sellada y documentos generados en el idioma de trabajo

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D158/D159 (contrato T001 §4/§5), D166 y D167 (par congelado por job/intento).
[Entrega, alcance y validación](archive/phase-011/P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md),
[flujo](flows/project-work-language.md#directiva-y-documentos-generados-p011-t009-d169).

- HITL: toda la generación documental entra en T009 (sin desglose) y los mensajes de commit y trailers son técnicos
  (T), sin cambios para ambos idiomas; solo el título de la tarea, escrito por el planificador, sigue W.
- Directiva `language-directive-1`: texto del motor (`core/engine/language.py`) que `render_attempt` añade tras la
  plantilla editable y antes del esquema, con la frase del criterio, el mapa V/W/T del rol (T001 §4), lectura de
  fuentes mixtas sin traducir y las etiquetas D088 del idioma de trabajo; declara su precedencia. El par sale solo del
  `language_context` del job reclamado; ninguna variable de plantilla lo sustituye. Ambos proveedores la reciben en el
  prompt de stdin ya usado, sin flags, system prompt ni cambios de permisos.
- Identidad: el snapshot del intento añade `language` (`directive`, par y SHA-256 del texto); `rendered_sha256`
  la cubre. Un formato desconocido, valores fuera de en/es o un trabajo distinto del contexto congelado detienen el
  intento en `prompts` antes de invocar. Jobs sin par (null o `ui-language-1`) se renderizan como antes, sin clave
  nueva; no se inventa un par. No se versiona `language-context-1`: el texto de la directiva es del motor, como el
  esquema, y cambiarlo exige un identificador nuevo.
- Plantillas inglesas sin ejemplos de marcadores españoles; ids nuevos por contenido y catálogos congelados o
  personalizados legibles. Las respuestas siguen el mapa por campo: una misma salida combina V y W.
- Documentos: el vocabulario en/es (`core/engine/document_text.py`) cubre bloques, plantilla D088 con AGENTS y
  envoltorios, REVIEW/SUMMARY, transición, DEFINITION.md, SUMMARY de B, texto de tarea desde chat y etiquetas del
  contrato de reconciliación, con el `work_language` del contexto congelado. Sin él (contextos previos a D167) se
  conservan los bytes españoles (y el inglés histórico del texto de chat): la salida española es idéntica byte a byte.
  Sin cambiar `document_layout`: el idioma ya forma parte del contexto congelado y solo cambia la salida inglesa,
  inexistente antes de D167; intenciones de commit selladas no regeneran prosa.
- Sin cambios de esquema, API, rutas, marcadores, códigos, parsers, presupuestos ni del idioma funcional del hijo.
  Mensajes visibles y avisos de vista previa → T010. Pruebas con agentes falsos: no acreditan calidad lingüística
  de proveedores reales ni ahorro de tokens. T010 es la siguiente.

## D170 — P011-T010: interfaz en/es por catálogos tipados y diagnósticos HTTP propios en el visual guardado

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D159 (contrato T001 §3) sobre la infraestructura D166.
[Entrega, alcance y validación](archive/phase-011/P011-T010_TRADUCCION_PRODUCTO.md),
[flujo](flows/language-preferences.md).

- HITL: T010 se desglosa. T010 = toda la interfaz React y los diagnósticos HTTP propios de `api/*` (sesión, guardia,
  router); la nueva T021 cubre diagnósticos de servicio/CLI y ayuda argparse. La QA visual en/es, claro/oscuro y
  escritorio/móvil se hace una vez tras T021 con autorización propia. La línea `Harness Local: access key at <ruta>`
  es salida técnica fija en inglés que leen `scripts/dev.py` y `scripts/check_distribution.py` (actualizados aquí);
  `módulo:atributo` y `Esquema SQLite` siguen con sus módulos en T021.
- Catálogos: 1417 claves React en/es tipadas desde el inglés; una clave terminada en `.one` es siempre plural.
  Frases con elementos (`rich`) parten la plantilla antes de insertar valores; las etiquetas de enlace traducibles son
  frases propias, nunca fragmentos. Errores fuera de React como `LocalizedError(clave)`; `ManagedError` conserva el
  `diagnostic` del servicio y, sin él, la interfaz añade su frase. Formatos de estadísticas, fechas, bytes y coste
  por idioma (`Intl`), sin `es-ES` fijo. Recetas desconocidas usan frases genéricas, no un fragmento.
- Visor Markdown: el HTML renderizado no lleva texto propio; códigos `data-blocked`/`data-alt` y párrafos vacíos que
  el visor rellena con `textContent`/`title`. `splitBlocks` devuelve `{code, name}`.
- Servidor: 24 claves nuevas del catálogo Python para `api/managed.py`, `api/app.py` y `api/security.py`, emitidas en
  el visual guardado (inglés si no se lee); códigos, estados y claves JSON intactos. Textos que la API reenvía desde
  servicios/storage, del agente, de terceros y la evidencia se muestran tal cual.
- Excepciones: nombres de comandos de chat (protocolo español), estados/códigos, rutas, hashes, comandos y el
  endónimo `Español`. La UI aún compara dos textos ingleses del servicio (`managed blocks are generated`,
  `changed since`); T021 los conserva o pasa a códigos. Sin cambios de esquema, API/OpenAPI, rutas ni persistencia.
- Validación: Node 93/93, `check`/`build` (aviso >500 kB previo), pytest 1608 passed, 2 skipped, 29 subtests
  (una expectativa española antigua de `test_managed_api.py` pasa a leer el catálogo) y unittest 8 OK. Sin esquema
  nuevo (sin Alembic), servicios, navegador, agentes, proveedores, red ni `scripts/dev`. T021 es la siguiente.

## D171 — P011-T021: textos propios del servicio y la CLI en el visual de cada emisión

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D159 (contrato T001 §3) sobre D166/D170.
[Entrega, alcance y validación](archive/phase-011/P011-T021_TRADUCCION_SERVICIO_CLI.md),
[flujo](flows/language-preferences.md).

- HITL sobre el alcance: T021 lleva a catálogo todo texto propio del servicio/CLI que estaba en español y la ayuda
  argparse; los ~960 textos de servicio ya ingleses quedan como texto técnico inglés y se desglosan en la nueva
  **T022**. Los dos textos que compara la UI siguen en inglés sin cambios.
- Emisión: `i18n.emission()` fija el visual en un `ContextVar` (código o resolutor evaluado una vez) y `tr()` lo usa;
  sin emisión, inglés. Petición HTTP → preferencias guardadas (middleware); job reclamado → visual congelado en su
  `language_context` (HITL), o el guardado si se admitió sin él; preparación → guardado; CLI → `--ui-language`, base o
  `en` (la ayuda, `--ui-language` o `en`). Lo persistido queda en la lengua emitida, sin retraducción posterior.
- `tr()` devuelve `Localized`, un `str` que recuerda clave y campos para volver a renderizarse; copias/pickle/JSON
  conservan solo el texto. La vista previa de retención sella cada diagnóstico propio en inglés, así que su hash no
  depende del idioma (las previas calculadas sobre el texto español dejan de coincidir y se revisan de nuevo). Las
  vistas previas de registro/creación incluyen la declaración mostrada; el registro de confianza guarda la confirmada.
- HITL sobre el aislamiento del núcleo: `core/` puede importar `harness_local.i18n` como única hoja externa (solo
  stdlib); test y ARCHITECTURE lo recogen.
- 471 claves del servicio en/es (+425): configuración local, registro, creación, preparación (prefijo
  `preparation_required:` conservado), backup, retención, migración, runtime/lanzador, modo gestionado, vistas,
  métricas, CLI y correcciones de diagnóstico; un resto de T010 en `api/managed.py`. `scripts/check_distribution.py`
  pasa a `--ui-language en` y a los textos ingleses (`module:attribute`, `SQLite schema`).
- Excepciones verificadas por test: vocabulario documental y alias de parsers (D169), recetas v1 y perfil con huella
  (D163), tokens del protocolo de chat, mensaje técnico de commit y textos de terceros. Sin cambios de esquema,
  API/OpenAPI, rutas, cliente ni dependencias.
- Validación: pytest 1615 passed, 2 skipped, 29 subtests; unittest 8 OK; Node 93/93. QA visual conjunta no
  autorizada (HITL), registrada como no realizada; sin servicios, navegador, agentes, proveedores, red ni scripts
  de distribución. T022 es la siguiente.

## D172 — P011-T022: textos de servicio ya ingleses en en/es y rechazos por código

Estado: implementada el 2026-10-23 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D159 (contrato T001 §3) sobre D166/D170/D171.
[Entrega, alcance y validación](archive/phase-011/P011-T022_TRADUCCION_SERVICIO_INGLES.md),
[flujo](flows/language-preferences.md).

- HITL sobre el criterio: casi todo `raise` llega a la API como `diagnostic`, así que lo visible se decide por
  naturaleza. Pasa a `tr()` lo que el operador causa o resuelve (entradas, conflictos de estado, ids desconocidos,
  checkout/Git/entorno, resultados de agentes, razones de parada/aceptación/bloqueo y diagnósticos registrados).
  Queda como texto técnico inglés lo que solo falla por un error de programación o datos persistidos corruptos y lo
  que entra en la entrada de un agente (validación, JUnit, rechazos por comando del runner, inventario de
  incorporación), por D169. La lista, con categoría (`invariant`, `agent-input`, `technical`), vive en
  `tests/fixtures/service_texts/english.json` y un test exige que todo texto propio en posición de diagnóstico sea
  `tr()` o figure en ella.
- 724 claves nuevas en/es (1195 en total) en 56 módulos de `core/`, `adapters/`, `storage/` y `services/`. El inglés
  de cada mensaje convertido es idéntico al literal que sustituye; una frase condicional son dos claves y nunca se
  insertan fragmentos. El literal español del chequeo de esquema que T021 no detectó es ahora `database.not_prepared`.
- HITL sobre la UI: los dos textos que comparaba pasan a códigos. `ManagedBlocksEdited` y `DraftChanged` (subclases
  de `ValueError`/`DraftConflict`) son la causa del `Conflict` y `call()` emite `managed_blocks_generated` y
  `draft_changed`; `Docs.tsx` y `Planning.tsx` comparan `ManagedError.code`. `code` es texto libre: sin cambio de
  OpenAPI ni tipos.
- HITL sobre métricas: las razones de parada se persisten en la lengua emitida (D171) y las métricas siguen
  agrupando por etapa y texto, así que una misma causa en en y es son dos grupos; aceptado y documentado.
- Huellas: ninguna cubre un texto nuevo salvo vistas previas que ya llevaban avisos localizados (precedente D171);
  los bloqueos de una vista previa de definición impiden confirmarla. READY, intenciones de commit y proyecciones no
  guardan razones. Nada persistido se retraduce.
- HITL: QA visual conjunta T010+T021+T022 no autorizada; registrada como no realizada. Sin cambios de esquema,
  API/OpenAPI, rutas ni dependencias.
- Validación: pytest 1619 passed, 2 skipped, 29 subtests; unittest 8 OK; Node 93/93; `check`/`build` del cliente
  (aviso >500 kB previo). Sin esquema nuevo (sin Alembic), regeneración OpenAPI, servicios, navegador, agentes,
  proveedores, red ni scripts de distribución. T011 es la siguiente.

## D173 — P011-T011: detección automática de CLI, mínimos y contrato por capacidades

Estado: diseño completado el 2026-10-23 por petición del usuario, con commit local en inglés; implementación
pendiente en T012. Fase: P011. Concreta D154/D159 y sustituye para el trabajo nuevo la política de admisión por
listas exactas de D052/D122; no reescribe sus evidencias ni cambia todavía `cli-13`.
[Contrato, fuentes, matriz y validación](archive/phase-011/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md).

- HITL: el usuario quiere que quien descargue el proyecto de GitHub no especifique la versión de Codex o Claude
  Code: el sistema reconoce los clientes/versiones y funciona desde un mínimo estable; si es inferior, indica
  actualizar. Resuelve las dos preguntas de la sesión: sin aceptación explícita de candidatas y sin excepción de
  nueva admisión para un lector antiguo bajo mínimos. Tampoco se exige importar evidencia o mantener una lista
  por binario al usuario final.
- Mínimos nuevos comunes a lectura/escritura: Codex **0.163.0**, Claude Code **2.1.304**, por ser la pareja más
  reciente caracterizada en D122 y usada por el piloto, con la corrección de transporte D124. No se afirman
  mínimos de introducción de funciones ni estabilidad semántica pre-1.0. Versiones anteriores, incluida 0.161.0
  con memoria solo probada sintéticamente (D066), conservan lectura de historia/configuración/hashes; nuevos
  intentos bajo mínimos se bloquean con indicación de actualizar.
- Descubrimiento de los proveedores elegidos por PATH explícito del servicio, ruta opcional para instalaciones
  no estándar, observación acotada de `--version`/help y perfiles de capacidades incluidos en la aplicación.
  Sin shell, búsqueda general del disco, auth/login/status, autoactualización ni cambiar proveedor/modelo.
  Parsear TOML no ejecuta CLI; resolución controlada antes de admitir trabajo congela la versión real, nunca
  `auto`. Formato automático nuevo versionado en T012; formatos/pins anteriores legibles con sus hashes y
  mismatch explícito, ejemplos públicos nuevos sin pins.
- Una release posterior estable numéricamente elegible, incluso de otro minor/major, se admite automáticamente
  si cumple el perfil aplicable; no existe techo numérico ni allowlist exclusiva por patch. Candidata conserva su
  procedencia técnica, sin confirmación humana adicional. Matriz por proveedor/rol de flags/valores, sandbox,
  confianza, memoria, instrucciones, permisos/grants, esquema/streams y cancelación. Guardias esenciales sin
  acreditar bloquean antes de invocar; help/exit 0 por sí solos no prueban semántica. La aplicación mantiene
  perfiles/justificación y diagnostica incompatibilidades; no traslada la investigación al usuario.
- Contrato de interfaz aplicado a candidatas es compatibilidad condicionada, no observación real de sus efectos
  ocultos. La supresión de confianza Codex requiere una justificación semántica aplicable, conservando D068/D122;
  no se infiere de flags o número superior. Sin evidencia nueva de binarios posteriores en T011; si hace falta
  para ampliar soporte acreditado, propuesta operativa separada y autorización propia antes de ejecutarla.
- Versión observada, identidad local del lanzamiento, capacidades/procedencia y hash de política/perfil quedan
  ligados al job/intento. Revalidación por intento y antes de GO; cambio de binario/versión/composición no reutiliza
  observaciones ni cambia trabajos ya encolados: cuarentena conservadora, sin retry/fallback ni mutar congelados.
  Nuevo trabajo puede redetectar el cliente actualizado sin pedir al usuario su versión.
- D160 sigue excluyendo ayudas reales del corte público: T012 sustituye su dependencia en tests por fixtures
  sintéticos y conserva originales privados. T011 solo diseña: sin código, esquema, flujo implementado, paquete,
  CLI/proveedores reales, suites, servicios, smoke, instalación o publicación. Checks documentales y fuentes
  oficiales; exceso previo del presupuesto de NEXT_STEPS registrado. Siguiente tarea: T012.

## D174 — P011-T012: clientes automáticos y compatibilidad condicionada

Estado: adoptada por HITL el 2026-10-23 y aplicada en T012 por la continuación y commit local en inglés pedidos
por el usuario. Fase: P011. Concreta D173 y sustituye su exigencia de acreditar por artefacto la supresión interna
de confianza antes de admitir cada nuevo escritor: la evidencia de D068/D122 conserva su alcance histórico.
[Entrega, matriz, checks y límites](archive/phase-011/P011-T012_COMPATIBILIDAD_CLI.md),
[flujo](flows/cli-compatibility.md), [datos JSON](DDBB-DIAGRAM.md#ejecución-gestionada-p003).

- HITL de implementación: no hay sonda pública sin inferencia que pruebe la condición interna de Codex que
  suprime escrituras globales de confianza para cada release posterior. El usuario elige admitir las posteriores
  automáticamente bajo el contrato conocido, con **compatibilidad condicionada** y sin afirmar efectos internos
  verificados. No se pide pin, aceptación de candidatas, archivo de evidencia ni investigación por patch al usuario.
  No se relajan sandbox, memoria, confianza o permisos: controles ausentes/alterados o incompatibilidad observable
  bloquean; help y pruebas falsas no se presentan como observación de los efectos reales.
- `local-config-7` extiende v6: ejecutable y `cli_version` opcionales por agente/preset; entorno, timeout y selección
  de proveedor/modelo/esfuerzo siguen explícitos. Solo los proveedores elegidos se resuelven por su PATH absoluto
  explícito o ruta opcional. Cargar sigue sin procesos; la resolución es un paso separado de arranque/composición
  y admisión. Cada mutación API resuelve el proyecto una vez en esa petición; lecturas GET/HEAD pasivas.
  `check-config --preflight` sigue siendo diagnóstico explícito de defaults y todos los roles de presets.
- Mínimos estables comunes de trabajo nuevo: Codex 0.163.0 y Claude Code 2.1.304 (D122/D124). Inferior → actualizar;
  ausente → instalar/ruta; formato ambiguo/prerelease → diagnóstico. Posteriores compatibles, incluso otro
  minor/major, no necesitan estar en una lista. Las listas previas quedan como evidencia; formatos 1–6/pins/hashes
  se leen sin reinterpretarse. Un pin explícito que difiere se diagnostica y se guía al formato automático.
  Los mínimos también se aplican al trabajo nuevo de configuraciones antiguas. V7 usa recetas v2 con las mismas
  claves y sin tocar fuentes/recibos/huellas v1/v2.
- `cli-14` y política empaquetada `cli-capabilities-1`, ligada por hash a su contenido y a fuentes de transporte/
  diagnóstico. Preflight de cada intento, sin caché de veredictos del job, con versión observada, flags emitidos
  completos, alias de config y valores requeridos cuando help declara choices. El perfil guarda procedencia de
  referencia/candidata y `internal_effects_verified=false`; no inventa evidencia de permisos efectivos, memoria,
  persistencia, dependencias transitivas, auth o inferencia. Validación local independiente del argv protege las
  guardias antes del target; terminales, grants, cancelación y ausencia de fallback/retry se conservan.
- Job congela versión real, identidad de lanzamiento y política; v7 añade procedencia de versión y descubrimiento.
  Hashes de ejecutable/script/intérprete explícitos y resolución de enlaces, con caché de contenido validada por
  inode/tamaño/mtime/ctime; no se confunden argumentos de datos mutables con código. Comprobación alrededor de
  sondas y antes de GO tras journal de identidad. Cambios → parada/cuarentena del trabajo congelado, nunca adoptar
  otro cliente; el trabajo nuevo redetecta. No se afirma aislamiento del SO o identidad de dependencias opacas.
- Rechazos de bind conservan informes seguros en eventos; los de intento dejan intención rechazada sin ejecutar
  target, o parada observada del grupo propio si ya esperaba GO. Se amplían JSON propios, no tablas/migraciones,
  y no se rellenan campos históricos ausentes. API usa códigos/correcciones en/es, sin exponer ayuda cruda,
  valores de entorno, credenciales o rutas de ejecutables. Contratos OpenAPI/tipos sin cambio de forma.
- D160: cobertura pública sustituida por ayudas sintéticas independientes, originales reales privados intactos.
  Fixtures dinámicos de operación se actualizan al mínimo o a candidatas sintéticas, conservando escenarios de
  historia, rechazo y recuperación; no se reescriben streams/snapshots congelados. README/ejemplos corrigen la
  guía de soporte y quitan pins nuevos; traducción/primer uso público completo sigue en T014.
- Sin CLI/proveedores reales, auth/configuración global, nuevos smokes, servicios en puertos, navegador, red,
  instalaciones o publicación. La evidencia nueva es sintética/offline y sus checks quedan en la entrega.
  No acredita uso real nuevo ni cambia los aplazamientos B/D095 o consentimientos agotados. Siguiente: T013.

## D175 — P011-T013: diagramas contrastados con el código sin cambiar el producto

Estado: aplicada el 2026-10-23 en T013 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Cumple el criterio 5 del contrato T001 (D159) para los flujos vigentes, el modelo de datos y la
arquitectura textual. [Matriz, hallazgos, checks y límites](archive/phase-011/P011-T013_MATRIZ_DIAGRAMAS.md).

- La autoridad es el código con sus pruebas: cada discrepancia se resolvió corrigiendo el dibujo o su prosa, sin
  alterar comportamiento para que encaje. Catorce hallazgos documentales (F01–F14), ninguno de diseño pendiente:
  estados de run y fase, ramas de chat, máquina de creación, `local-config-6/7`, resolución CLI separada,
  idioma de trabajo en B y restos de A/observadores. Dos transiciones dibujadas sin prueba a nivel de run
  reciben regresión (`RECOVERY_REQUIRED → COMMITTED` y rechazo en el reclamo); ambas pasan con el código intacto.
- Un diagrama que no puede expresar una regla en una flecha (vuelta al estado previo de una fase) la declara en la
  prosa contigua. El piloto P009 se separa del flujo de producto como evidencia histórica enlazada; el archivo no se
  edita. Los flujos conservan su idioma actual: la línea base pública inglesa sigue en T014.
- Comprobación reproducible en `docs/phase/`: paridad ER ↔ metadata (tablas, columnas, tipos, PK/FK/UK, nulos,
  relaciones y unicidades listadas), parser Mermaid local 11.17.2 con DOMPurify inerte (solo sintaxis, sin DOM ni
  render) y enlaces/anclas. Pasar el parser no acredita paridad semántica; la acredita la matriz.
- Resto fuera de rutas permitidas y sin efecto: la ayuda `cli.help.writers_stopped` aún menciona «observers»;
  queda para T014/T017. Sin proveedores, CLI reales, servicios, navegador ni red. Siguiente: T014.

## D176 — P011-T014: baseline pública en `docs/public/` y README inglés de primer uso

Estado: aplicada el 2026-10-23 en T014 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D157/D159 (contrato T001 §8) para la documentación pública inicial.
[Entrega, mapa del candidato, checks y pendientes](archive/phase-011/P011-T014_DOCUMENTACION_PUBLICA.md).

- HITL de ubicación: la baseline pública se prepara en el árbol autocontenido `docs/public/`, que replica la raíz del
  candidato (instrucciones de agentes y `docs/`); T015 lo copia sustituyendo AGENTS/CLAUDE/GEMINI y todo `docs/`.
  Los documentos privados en español siguen vivos. `README.md` raíz pasa a ser el README inglés público y
  `README.es.md` la entrada española, solo en la raíz.
- HITL de alcance: especificación, arquitectura, modelo de datos y flujos públicos en inglés pasan a la nueva
  **T023**, antes de T015. T014 entrega README de primer uso, entrada española, instrucciones públicas, ejemplo
  mínimo `local-config-7` de un proveedor, DECISIONS de partida y ROADMAP/STATE/NEXT_STEPS públicos (P001 = modo
  continuo opcional de D156, sin tareas).
- HITL de numeración: DECISIONS pública conserva los números que cita el código, reescritos en inglés de forma
  autocontenida y en su estado vigente, sin contenido privado; huecos esperados, baseline < D200 y nuevas decisiones
  públicas desde D200. No se cambia código para renumerar. El comprobador exige entrada pública para todo DNNN
  citado por el código del candidato.
- El README describe solo capacidades entregadas, separa desarrollo y uso instalado, declara macOS ARM64 como única
  plataforma probada y el primer uso como no ensayado hasta T016. Comprobación estática del candidato modelado,
  carga del ejemplo con rutas sintéticas y `--help` de la CLI; sin suites, builds, servicios, proveedores ni red.
  Siguiente: T023.

## D177 — P011-T023: documentación técnica pública autocontenida en inglés

Estado: aplicada el 2026-10-23 en T023 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Completa el desglose HITL de D176 sin cambiar el producto.
[Entrega, criterios y checks](archive/phase-011/P011-T023_DOCUMENTACION_TECNICA_PUBLICA.md).

- `docs/public/docs/` añade SPECIFICATION, ARCHITECTURE, DDBB-DIAGRAM y los 14 flujos vigentes, reescritos en inglés
  desde los documentos vivos y el código: comportamiento actual sin historia de fases, enlaces al archivo ni piloto.
  El flujo privado `legacy-migration.md` se publica como `legacy-compatibility.md`.
- Solo se citan DNNN con entrada pública; el resto se describe sin número. Requisitos públicos renumerados F01–F22
  sin los retirados (ninguna referencia en código). Columnas ER idénticas; comentarios traducidos.
- El comprobador de T014 exige también entrada pública para los DNNN de los documentos, normaliza `..` y limita el
  patrón de archivo privado a enlaces y fases privadas. README y README.es enlazan los documentos nuevos.
- Nota para T015/T017: el módulo `profiles/reference_project.py` del candidato lleva un nombre privado; la arquitectura
  pública no lo nombra. Siguiente: T015.

## D178 — P011-T015: paquete candidato 0.1.0, CI sintética e instantánea pública

Estado: aplicada el 2026-10-23 en T015 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D156/D157/D160 y el contrato T001 §8 para el paquete y el corte inicial.
[Entrega, hashes, procedimiento manual y checks](archive/phase-011/P011-T015_PAQUETE_PUBLICO.md).

- HITL de versión: el candidato de la primera apertura pública es `0.1.0` (el `0.1.0` local de P010 no se publicó y
  su `dist/` queda excluido); `0.2.0` sigue reservada (D156). CHANGELOG fija la política: una versión para paquete,
  API y UI; 0.x con notas de cambio; datos legibles entre versiones y esquema solo con `migrate`; Release manual en
  GitHub con wheel, sdist, `requirements.txt` y `SHA256SUMS`, sin PyPI.
- Paquete: README y licencias en staging (`license-files`), carpeta de salida nueva o vacía, `requirements.txt` sin
  cabecera (registraba la ruta absoluta) y `SHA256SUMS`. `check_distribution.py` verifica miembros exactos,
  metadatos, licencias, versión única, ausencia de componentes retirados y el `pyproject.toml.orig` de uv_build.
  El journey instalado se repara declarando el idioma de trabajo del fixture (roto desde D167). Avisos: los 58
  paquetes del bundle tienen aviso; las 19 entradas externas sin términos locales no se redistribuyen.
- CI sintética en GitHub Actions (`macos-15`, `contents: read`, acciones fijadas por commit, sin secretos,
  proveedores ni publicación); escrita y no ejecutada en remoto.
- HITL de nombre privado: ReferenceProject es un proyecto privado que se incorporará con el flujo de repositorio existente;
  se elimina `profiles/reference_project.py` y toda referencia en código y tests, ampliando las rutas de la tarea. Los
  documentos y archivos históricos privados no se reescriben.
- HITL de instantánea: herramienta privada por lista positiva que materializa el candidato en
  `.local/public-candidate/` sin Git, con manifiesto privado origen → candidato y otro publicable; código idéntico al
  origen. Crear el repositorio, activar el reporte privado, commit, push, tag o Release siguen pendientes de
  autorización propia (procedimiento en la entrega). Siguiente: T016.

## D179 — P011-T016: primer uso ensayado, pylock y validación de tarea igual al perfil

Estado: aplicada el 2026-10-23 en T016 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Sustituye el punto de `requirements.txt` de D178. Concreta D157/D178 para el ensayo del candidato.
[Entrega, matriz, hallazgos y hashes](archive/phase-011/P011-T016_PRIMER_USO_QA.md).

- HITL de alcance: red solo para el primer llenado de cachés vacías (PyPI, registry de npm) y repetición offline;
  ensayo en el scratchpad de la sesión desde la instantánea con un `git clone` local sin remoto; servicio instalado en
  loopback recorrido por HTTP con CLI falsas. La QA de navegador pasa a la nueva **T024**, con autorización propia.
- HITL de formato: el paquete publica `pylock.toml` (PEP 751, exportado por uv del lock, URL y hash de cada wheel) en
  lugar de `requirements.txt`, porque este no se instala offline desde la caché que deja el primer paso documentado.
  README, `check_distribution.py`, CHANGELOG, ARCHITECTURE y la D043 pública lo reflejan; uv verifica los hashes.
- HITL de producto: un comando de validación de la tarea con el argv de una validación del perfil que se ejecuta en la
  raíz sin entorno propio es esa validación (su timeout) y se ejecuta una vez; antes la autorización exacta lo rechazaba
  por el timeout por defecto y paraba la primera tarea del ejemplo mínimo. Validaciones con `cwd` o entorno propios no
  se adoptan. Regresión nueva; la autorización sigue siendo por comando completo.
- Un test de TypeScript dependía de metadatos npm de la caché privada y ahora admite `ENOTCACHED`; la sonda falsa crea
  directorios. Resultado: suites, build y check desde el clon limpio, build idéntico byte a byte al del checkout y
  primer uso instalado con ambos accesos hasta COMMITTED, cierre de fase, cuatro pares de idioma, reinicio, `migrate` y
  backup en verde. Sin CLI reales, inferencia, navegador, CI remota ni publicación. Siguiente: T024.

## D180 — P011-T024: QA de navegador del candidato y tres correcciones de presentación

Estado: aplicada el 2026-10-24 en T024 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D179 (QA de navegador desglosada de T016) y cierra la QA visual conjunta de T010/T021/T022.
[Entrega, matriz, capturas y hashes](archive/phase-011/P011-T024_QA_NAVEGADOR.md).

- HITL de alcance: build/instalación offline del candidato en el scratchpad, datos sintéticos con la CLI falsa del
  driver T016, servicio en loopback y Claude in Chrome en una pestaña nueva solo sobre esa URL; matriz completa
  (14 pantallas × en/es × claro/oscuro × escritorio/móvil) con capturas representativas saneadas.
- Móvil: ventana mínima de Chrome (500 px) más maquetación de 390 px emulada con `zoom`; el embebido en iframe queda
  descartado porque el servicio lo prohíbe. La navegación de la extensión llega como `cross-site` y la guardia anti-CSRF
  la rechaza, como debe; la QA recarga desde la propia página.
- Correcciones de cliente (todas las combinaciones): duración de validación con formato `Intl` del idioma, fecha de
  cierre de fase con `when()` y rol/estado de los intentos traducidos (`ROLES` y cinco estados de intento nuevos en
  `Status`, claves en/es). Dos regresiones Node; tipos/build y `check_distribution` del candidato corregido en verde.
- HITL de producto: acciones de job, etapas del motor, veredictos y campos de huella se mantienen como códigos técnicos
  visibles y se documentan como excepción; los motivos persistidos siguen en su idioma de emisión (T022).
- Resultado: sin claves crudas, desbordes de página, controles sin nombre, textos bajo AA ni errores de consola; foco
  visible en ambos temas. Sin otros navegadores, lectores de pantalla, CLI reales, proveedores, red ni publicación.
  Siguiente: T017.

## D181 — P011-T017: dictamen favorable y expediente de apertura pública

Estado: aplicada el 2026-10-24 en T017 por la continuación y commit local en inglés pedidos por el usuario.
Fase: P011. Concreta D154/D155/D157/D158 y el procedimiento de D178.
[Revisión de salida](archive/phase-011/P011_REVIEW.md) y [expediente](archive/phase-011/P011_EXPEDIENTE_APERTURA.md).

- Dictamen favorable en el alcance declarado: los diez criterios de ROADMAP y los trece globales de SPECIFICATION
  §10 (1/11/13 en su redacción de D161) cumplen con evidencia trazable; la matriz histórica de P010 no se reescribe.
  Sin tareas obligatorias, licencia ni hallazgos de privacidad o paridad pendientes. Habilita T018.
- HITL: las rutas de T017 se amplían para cerrar el residuo de la retirada legacy (ayuda de `--writers-stopped`,
  diagnóstico de `migrate` y un docstring decían «observers»; ahora «service and writers») y para que README,
  README.es y el STATE público citen la QA de navegador de T024. Sin cambio de flags, códigos ni comportamiento.
- Candidato final: instantánea de 387 archivos con manifiesto `74cc9141…ea71` (13 rutas distintas de T016, todas
  explicadas); wheel `46d29c20…d9d6`, sdist `79e256de…42c5` y `pylock.toml` sin cambios, con dos builds idénticos y
  `check_distribution` en verde. Suites completas en verde tras el cambio de catálogos.
- Expediente con acciones remotas exactas sobre `<owner>/<repo>` (HITL: placeholders; visibilidad al autorizar):
  regenerar y comparar el manifiesto, repositorio vacío, commit raíz único, CI verde, visibilidad, reporte privado
  de vulnerabilidades antes de anunciar y Release opcional sin PyPI. Ninguna se ha ejecutado; cada una requiere
  autorización propia. Límites conservados: solo macOS ARM64, CI remota sin ejecutar, CLI y proveedores reales sin
  uso en P011, B/D095 aplazados (D151) y QA solo en Chrome.

## D182 — Cierre documental de P011 y preparación pública archivada

Estado: cerrada y archivada el 2026-10-24 por la continuación solicitada por el usuario, tras D181. Fase: P011.
[Resumen](archive/phase-011/SUMMARY.md), [revisión](archive/phase-011/REVIEW.md) y
[registro de cierre](archive/phase-011/P011_CIERRE.md). Precedentes: D002/D088/D114/D140/D153.

- La petición de continuar la siguiente tarea y finalizar con un commit en inglés autoriza T018, identificada en
  STATE/NEXT_STEPS. T017 emite dictamen favorable de los diez criterios y los trece globales (D181); las veinticuatro
  tareas quedan completadas, sin tareas obligatorias, licencia ni hallazgos de privacidad o paridad pendientes.
- STATE, NEXT_STEPS y los 61 artefactos originales de `docs/phase/` se conservan por bytes respecto de `4eeda84`;
  MANIFEST registra origen/destino, tamaño y SHA-256. SUMMARY/REVIEW/P011_CIERRE nuevos sintetizan entregas,
  candidato y límites. Los snapshots conservan estados, enlaces y comandos en su contexto original.
- El cierre solo cambia `docs/` privada, excluida del candidato: manifiesto público `74cc9141…ea71`, wheel, sdist y
  `pylock.toml` de T017 siguen vigentes. El paso 1 del expediente, que cita el script en `docs/phase/`, se reproduce
  desde un worktree temporal del commit de T017 sin adaptar los originales; comprobado con el mismo manifiesto.
- STATE compacta la base, NEXT_STEPS queda sin tareas y ROADMAP enlaza P011 completada. Las referencias vigentes se
  reubican, sin reescribir P001–P010 ni el contenido de decisiones históricas. Sin sucesora definida: el usuario
  elige entre autorizar la apertura sobre el expediente o una candidata de ROADMAP; v0.2.0 sigue tras la apertura.
- Cierre manual del repositorio, separado del check READY del producto: sin registrarlo ni ejecutarlo con el harness,
  agentes, proveedores, servicios o smokes. Sin cambios de producto, esquema, API, flujos, dependencias, paquete o
  configuración global; sin tag, push, creación de repositorio, cambio de visibilidad, Release ni publicación.

## D183 — P012: validación real previa a la apertura pública

Estado: fase planificada el 2026-10-24 por encargo explícito del usuario; siete tareas pendientes.
[Tareas](archive/phase-012/NEXT_STEPS.md) y [criterios](ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública).
Precedentes: D095, D139, D151, D155, D157, D173, D174, D181 y D182.

- Tras regenerar el candidato de P011 en `my_harness_dist` (paso 1 del expediente, manifiesto `74cc9141…ea71`), el
  usuario decide no abrir el repositorio sin validar con proveedores reales lo que el README anuncia sin uso real,
  porque quiere publicar un producto que funcione y que va a usar personalmente. Se toma la candidata de D151
  (B y D095) y se amplía a chat, backup/restauración y receta TypeScript web v2 con trabajo en español.
- Las ejecuciones reales anteriores (D050, D071, D139) precedieron a `cli-14`, la detección por capacidades, la
  directiva de idioma y las recetas v2. El primer tramo real acredita también el flujo básico con la versión actual
  y con Claude Code 2.1.310, posterior al mínimo, en compatibilidad condicionada (D174).
- Pareja elegida por el usuario: revisor Claude Code y ejecutor Codex, ambos con modelos ligeros; la cuota de
  Claude es limitada. No se repiten las cuatro combinaciones: su fila conserva la evidencia anterior a `cli-14`.
- La fase se desarrolla en este repositorio privado porque la apertura (D157) aún no se ha ejecutado: la evidencia
  real queda en la historia privada y el repositorio público nace con el alcance corregido. El candidato de P011
  deja de ser el publicable cuando cambien README o `docs/public/`; T005 prepara el sustituto y T006 el expediente.
- Planificar no autoriza operaciones: T001 es documental y cada tramo real (T002–T004) exige confirmación de la
  propuesta y autorización propia. Fixtures sintéticos, área privada fuera de checkouts, sin configuración global,
  sin operar este repositorio con el harness ni el Django de P009, sin acciones remotas ni publicación.

## D184 — P012-T001: propuesta operativa y Codex 0.164.0

Estado: completada documentalmente el 2026-10-24; propuesta confirmada por el usuario, sin autorizar tramos.
[Propuesta, parámetros y controles](archive/phase-012/P012-T001_PROPUESTA_OPERATIVA.md). Fase: P012. Concreta D183 sobre
D095/D119/D143/D151/D168/D173/D174, sin ampliar autorizaciones operativas.

- La inspección `--version` encuentra Codex **0.164.0**, frente a 0.163.0 previsto en D183. El usuario responde
  expresamente «Usar 0.164.0 instalada, con compatibilidad condicionada de D174». Se actualizan los criterios
  vivos de P012, sin reescribir D183 ni evidencias anteriores. Claude observado 2.1.310. No se instala otra CLI.
- Propuesta: área nueva `$HOME/Documents/harness-validation/p012-20261024`, puertos 8024/8025, autor
  sintético, trabajo/visual es, Claude `sonnet`/low y catálogo único Codex `gpt-6-luna`/low; este nombre procede
  del catálogo local leído sin red, y la ayuda Claude documenta el alias/esfuerzo. Parámetros confirmados por el
  usuario; no se atribuye disponibilidad de cuenta ni inferencia a una lectura de catálogo/help.
- Python **3.14.4** para construir/instalar el harness, exigido por sus metadatos; **3.13.13** solo para el fixture B.
  `local-config-7` íntegro propuesto con Django declarado del ejemplo (sin receta/formateador) y TypeScript v2.
  Política agent/catalog, cero correcciones automáticas para parar en el primer fallo, sin fallback.
- Techos propuestos Claude/Codex: T002 12/3 (4 h), T003 3/0 (2 h), T004 12/3 (4 h), total 27/6; una ejecución
  normal por tarea, sobrante sin permiso de relanzamiento. Cada tramo conserva su autorización separada.
- Base de paquete `c5cfc9b4586dbdb64075624e268e2f187749d430`; hashes de CLI, intérprete y locks observados.
  Wheel/sdist/pylock de P012 aún no construidos, cachés/fixtures sin acreditar y preflight no ejecutado:
  son punto de control obligatorio de preparación offline de T002 antes de proveedores. Se usa pylock PEP 751,
  no el requirements histórico. El usuario acepta este punto de control diferido en su confirmación; T001 cierra
  documentalmente sin presentar sus comprobaciones operativas como ejecutadas o acreditadas.
- HITL: «Confirmar T001 con estos parámetros; sin autorizar tramos». Quedan elegidos área, puertos, modelos,
  esfuerzos, autor, fixtures, TOML, política, presupuestos, paradas y guion. Siguiente tarea T002, pendiente de su
  autorización explícita; T003/T004 conservan las suyas. No se pide ni se presume permiso operativo adicional.
- Solo cambios `docs/**`, versiones/help/hashes locales y comprobaciones documentales. Sin build, instalación,
  fixtures operativos, servicios, agentes/proveedores, smokes, configuración global, commits, push ni publicación.
  Se conservan los límites anunciados y el expediente archivado de P011.

## D185 — P012-T002: autorizada y detenida por caché Django incompleta

Estado: T002 iniciada y detenida el 2026-10-24 en preparación offline; no completada, sin llamadas a modelos.
[Registro y hashes](archive/phase-012/P012-T002_INCORPORACION_REAL.md),
[doce pins y hashes faltantes](archive/phase-012/P012-T002_WHEELS_FALTANTES.lock). Fase: P012. Aplica D183/D184.

- El usuario pide «Haz commit y comienza con la siguiente tarea». Se hace commit de T001 (`dc5edd4`) y se inicia
  T002 con la propuesta confirmada; la instrucción autoriza ese tramo, sin extenderse a T003/T004 ni a descargas.
- Área privada nueva elegida en T001, TOML 0600 y toolchain revalidada. Build offline correcto de la base
  `c5cfc9b4586dbdb64075624e268e2f187749d430`, sin cambios de fuentes; wheel SHA-256
  `46d29c209f90a8f67c02e4295753688ec0c646c5c0f0259575fed5910117d9d6`, checksums de artefactos correctos.
- Inventario de cachés locales: 5 de 17 wheels originales compatibles encontrados; faltan 12 del lock Django.
  Se aplica la parada de T001 antes de verificador, instalación, preflight, fixture, servicio/UI o proveedores.
  Consumo Claude/Codex **0/0** frente a **12/3**. Sin SQLite, jobs, locks ni procesos propios activos; área conservada.
- No se acredita incorporación B, perfil declarado con herramientas reales, flujo básico cli-14 ni COMMITTED.
  Es falta de prerrequisito operativo, no defecto demostrado del producto: no se abre tarea de corrección.
- Reanudar requiere consentimiento nuevo tras la parada. Resolver con wheelhouse local permitido o consentimiento
  separado para metadatos PyPI y hasta doce wheels de los pins/hashes adjuntos, sin ampliar dependencias, modelos,
  permisos ni presupuesto. No hay descarga o relanzamiento implícito. T003/T004 siguen sin autorización.
- Solo documentación del producto; sin cambios de código/datos/flujos/configuración global, suites, push o publicación.
  T001 y archivos históricos no se reescriben. Los cambios del registro T002 quedan sin commit.

## D186 — P012-T002: descargas autorizadas y falso rechazo de choices multilínea

Estado: T002 reanudada y detenida de nuevo el 2026-10-24; defecto acotado, sin llamadas a modelos.
[Registro y evidencia saneada](archive/phase-012/P012-T002_INCORPORACION_REAL.md#7-reanudación-autorizada-y-wheelhouse-resuelto),
[manifiesto wheels](archive/phase-012/P012-T002_WHEELS_VERIFICADOS.sha256). Fase: P012. Conserva D185 como primera parada.

- HITL: «Autorizar esas descargas y reanudar T002», sobre lista de doce pins/hashes de D185. Se consultan sus doce
  metadatos PyPI y descargan doce wheels compatibles de files.pythonhosted.org, verificando tamaño y hash;
  cinco originales se copian de cachés locales revalidadas. Wheelhouse propio de 17 wheels completo.
- Verificador de distribución exit 0 con CLI falsas; harness instalado offline en Python 3.14.4 y fixture B en
  3.13.13 con hashes/sin builds. Dos preparaciones y seis validaciones del perfil declarado correctas: pytest
  2 passed con JUnit y mypy 10 fuentes. Fixture original con 15 archivos y commit sintético `f6a2d9d`.
- Preflight instalado exit 1: Claude 2.1.310 rechazado por `unsupported_values` de `--permission-mode dontAsk`,
  aunque aparece en una continuación de la lista de su ayuda. Codex 0.164.0 pasa en compatibilidad condicionada.
  Lectura del código y reproducción pura con ayuda sintética confirman que el lector de choices excluye saltos
  de línea: mismos valores en una sola línea pasan. Sin volver a ejecutar preflight o cambiar guardias/configuración.
- Se aplica la parada de D184: sin init-db, servicio operativo, UI, registro/incorporación, tarea ni COMMITTED.
  Consumo Claude/Codex 0/0; sin SQLite, jobs, locks o procesos propios activos. Área y evidencia conservadas.
- Defecto acotado en **P012-T008**, siguiente tarea de corrección offline con tests sintéticos; T002 sigue parcial.
  Corregir no autoriza relanzarla: hace falta propuesta/base y wheel nuevos, verificar hashes/preflight bajo
  consentimiento de reanudación nuevo. Sin debilitar permisos, actualizar CLI, fallback o ampliar presupuesto.
  T003/T004 siguen sin autorización. Sin suites del producto o cambios de código en T002, sin push/publicación.

## D187 — P012-T008: listas multilínea en el preflight CLI

Estado: implementada y verificada offline el 2026-10-24 por la continuación pedida por el usuario.
El commit solicitado conserva T002 (`2abf278`); los cambios de T008 quedan sin commit.
[Corrección, pruebas y propuesta de continuación](archive/phase-012/P012-T008_CORRECCION_PREFLIGHT.md),
[flujo CLI](flows/cli-compatibility.md). Fase: P012. Corrige el defecto de D186 sin reanudar T002.

- `unsupported_values` lee listas de valores separados por comas dentro de la sección de su opción, incluidas
  continuaciones LF/CRLF, valores con guiones y comillas simples/dobles. Ya no corta en el primer salto de línea
  ni acepta menciones de prosa posterior como valores. Otra opción, un cierre o prosa ajena no aportan el valor
  requerido. Una lista que lo excluye sigue bloqueada; no anunciar lista no inventa observaciones.
- Sin cambiar valores/flags requeridos, mínimos, permisos, argv, modelos, API, esquema o versiones de transporte.
  `cli-14`/`cli-capabilities-1` conservan sus nombres; huella de política derivada automáticamente nueva
  `1156d0c9c8ad969c6762653eadadb5626c3d8f203d6e7ce821611d6286cc79d5`. Nada reescribe evidencia congelada.
- Veinticinco regresiones nuevas, ayudas/ejecutables exclusivamente sintéticos. Antes del cambio, 15 fallos en
  la selección de 24 casos reproducen el defecto y una falsa aceptación de prosa. Tras corregir, 25/25 y los
  cinco módulos de diagnóstico/capacidades/descubrimiento/transporte/memoria pasan: 229 tests, sin CLI reales.
- T002 sigue parcial y detenida; la entrega propone un commit base nuevo y `dist-t008`/`venv-t008` bajo el área
  ya elegida, conservando los originales. Construcción/verificación/instalación y preflight real requieren
  consentimiento nuevo de reanudación antes de ejecutarse, con 12/3 llamadas de techo y 0/0 consumidas.
  No se confunde corrección sintética con validación real. T003/T004 siguen sin autorización.
- Sin cambios de modelos/migraciones, dependencias, UI o contrato API. Flujo actualizado en la misma tarea;
  diagrama de datos intacto. Sin build operativo, servicios, navegador, smokes, red, CLI/proveedores reales,
  área operativa, configuración global, push o publicación. T001/T002 y archivos históricos conservados.

## D188 — P012-T002: preflight corregido aprobado y parada en la apertura de Chrome

Estado: T002 reanudada y detenida el 2026-10-24; preparación corregida acreditada, sin llamadas a modelos.
[Registro, hashes y continuación propuesta](archive/phase-012/P012-T002_INCORPORACION_REAL.md#10-continuación-autorizada-con-el-paquete-corregido).
Fase: P012. Conserva D185/D186 y aplica la propuesta de D187.

- El usuario pide continuar la siguiente tarea y finalizar con commit. Con el precedente D185, se interpreta como
  autorización nueva para T002 sobre T008 §5 y se comunica antes de operar: base `6efbd82`, destinos nuevos
  `dist-t008`/`venv-t008`, mismo fixture/configuración/modelos, techo 12 Claude/3 Codex y parada al primer fallo.
- Checkout limpio, identidades/versiones/hashes, TOML íntegro y 17 wheels revalidados. Build y verificador offline
  correctos, instalación en Python 3.14.4 y política nueva de T008 comprobada. Wheel SHA-256
  `5df9e000dd9f1bb9056103b519439a8352f48c4ba57c4173c2482f5ddca15e0b`.
- Preflight real **exit 0**: Claude 2.1.310 y Codex 0.164.0, sin valores ausentes y con compatibilidad condicionada,
  sin acreditar auth/inferencia. Dos preparaciones y seis validaciones del fixture en verde (pytest 2 tests).
  SQLite nueva inicializada, servicio arrancado fuera del checkout en 8024.
- Primera apertura automatizada en Chrome rechazada con `origin_rejected` / «Request from a foreign site.».
  Ese diagnóstico corresponde a `Sec-Fetch-Site: cross-site`; no se observan los headers ni se acredita defecto
  del producto. Se aplica la parada de permisos, sin repetir navegación ni cambiar protecciones.
- Servicio detenido normalmente; puerto cerrado, 0 jobs/runs/conversaciones/incorporaciones/locks. Llamadas a
  modelos 0/0. Originales `dist`, configuración y bytes/modos del fixture conservados; venv anterior intacto.
  UI autenticada, registro, B y COMMITTED siguen pendientes; T002 no completa.
- Continuación concreta pendiente de HITL: usar los nuevos artefactos y misma SQLite, reiniciar tras revalidar y
  abrir mediante la barra de direcciones de Chrome, sin cambiar Host/Origin/CSRF ni cabeceras. Parar si se rechaza.
  Mantener 12/3 llamadas y parámetros de T001. Sin reconstrucción, init-db, descargas ni autorización de T003/T004.
- Solo documentación en este repositorio; sin cambios de diseño/código/esquema/flujos ni corrección nueva sin defecto
  demostrado. Sin suites del producto adicionales, configuración global, tags, push o publicación.

## D189 — P012-T002: rechazo cross-site también desde la barra de Chrome

Estado: continuación autorizada y detenida el 2026-10-24; T002 parcial, sin llamadas a modelos.
[Evidencia y siguiente punto HITL](archive/phase-012/P012-T002_INCORPORACION_REAL.md#15-hitl-recibido-y-navegación-desde-la-barra-de-chrome).
Fase: P012. Conserva D188 sin alterar su resultado ni su propuesta histórica.

- HITL recibido tras `e69d1d1`: «Autorizar esa continuación de T002», referido a la propuesta concreta de D188:
  mismo wheel/venv corregidos y SQLite, reinicio en 8024, URL desde la barra de Chrome y guardias intactas,
  B/tarea solo si abre, límites 12/3 y sin T003/T004 o descargas. No se repiten build/instalación/init-db.
- Hashes, conservación, base sin jobs/locks y puerto revalidados; servicio reiniciado. Campo de dirección enfocado
  explícitamente por accesibilidad nativa, URL escrita y Return; vuelve a mostrar `origin_rejected` / «Request from
  a foreign site.». Sin capturar cabeceras ni atribuir defecto al producto/navegador. La navegación manual del
  usuario aún no está comprobada. No se repite otra navegación ni se cambian protecciones.
- Nueva parada conforme a T001 §6: servicio detenido normalmente, puerto cerrado, clave temporal eliminada;
  0 jobs/runs/conversaciones/incorporaciones/locks, 0/0 llamadas. Originales y fixture conservados por bytes/modos.
  UI autenticada, registro, B y tarea siguen pendientes; el preflight real aprobado de D188 sigue acreditado.
- Siguiente propuesta para HITL: diagnóstico local sin modelos, con reinicio y apertura manual por el usuario,
  observando solo cabeceras de navegación/estado en Network y excluyendo cookies/credenciales. Sin modificar ni
  interceptar tráfico, cambios de guardias, login, registro o proveedores; detener tras recoger evidencia.
  No hay autorización para otro relanzamiento todavía. T003/T004 siguen sin autorización.
- Solo documentación en el checkout; sin suites adicionales, cambios del producto, configuración global o remotos.

## D190 — P012-T002: acceso manual al login y diagnóstico local sin cabeceras

Estado: diagnóstico local autorizado y terminado el 2026-10-24; T002 parcial, servicio detenido y sin modelos.
[Evidencia y continuación propuesta](archive/phase-012/P012-T002_INCORPORACION_REAL.md#18-diagnóstico-autorizado-y-acceso-manual-observado).
Fase: P012. Conserva D188/D189; no cambia el contrato de seguridad.

- «Continúa» autoriza la propuesta concreta de D189: reiniciar para diagnóstico con apertura manual y observar
  cabeceras, sin login/registro/modelos ni cambios de protección. Mismo wheel/venv y SQLite; guardias revalidadas.
- Network preparado en una pestaña vacía controlada por Codex. El usuario informa que esa pestaña sigue cargando,
  pero otra pestaña normal muestra el acceso. Accesibilidad confirma **Harness Local / Sign in / Local key** vacío
  en la URL 8024; vincular esa pestaña ya cargada permite observarla sin otra navegación.
- La pestaña controlada sigue en `about:blank`, con indicadores Network `200`/0 B y pendiente. No se consigue leer
  cabeceras ni se captura el HTTP de la pestaña normal. Diagnóstico parcial de causa, acceso manual al login
  acreditado; sin defecto del producto demostrado ni motivo para debilitar Host/Origin/CSRF.
- Servicio detenido normalmente al terminar, puerto cerrado y clave eliminada; 0 jobs/runs/conversaciones/
  incorporaciones/locks y 0/0 modelos. Originales/fixture conservados. Sin login, registro, B o tarea.
- Propuesta para nuevo HITL: reanudar T002 con la pantalla cargada manualmente antes de vincularla a la herramienta,
  autenticar y continuar B/tarea desde UI con parámetros 12/3 intactos. Si requiere navegación, apertura manual;
  si falla la interacción, parar sin cambiar a API. El diagnóstico no autoriza ese nuevo tramo. T003/T004 excluidas.
- Solo documentación, conservación y parada; sin suites adicionales, cambios del producto o configuración global.

## D191 — P012-T002: incorporación B confirmada y parada del escritor Codex

Estado: reanudación autorizada el 2026-10-24; B COMMITTED, tarea en REVISION_LIMIT; T002 parcial y servicio detenido.
[Registro, evidencia y siguiente diagnóstico](archive/phase-012/P012-T002_INCORPORACION_REAL.md#21-reanudación-autorizada-sesión-y-registro).
Fase: P012. Conserva D188–D190 y sus límites.

- «Autorizo» cubre la propuesta D190/§20: mismo wheel/venv/SQLite, login cargado manualmente, B/tarea desde UI,
  modelos/esfuerzos y 12/3 llamadas, cero correcciones. Login y preferencias es/es correctos; registro `p012-b`
  con composición django, perfil declarado python-django y política confirmada, sin modificar TOML.
- Dos turnos Claude válidos con doce borradores revisados y aplicados por hash. HITL adicional: conversión habitual
  `int` para `limit` (espacios, +5, 05 aceptados; 5.0 rechazado); 400 JSON con clave `error`, sin texto exacto, ausencia
  conserva 5. D005 del hijo distingue la decisión del usuario de las cuatro decisiones inferidas del código.
- Incorporación documental COMMITTED en `976b1d1fb9fad40da73aef19e0d6896578999cff`, P001 ACTIVE con una tarea;
  código original conservado por bytes/modos, README archivado con mismo blob/modo Git. Perfil SHA `8585911d…`.
  El usuario autoriza aparte solo comprobar idempotencia por API local (UI sin botón tras completar): una repetición
  con mismos hashes/datos/clave devuelve 202 y el mismo job, sin duplicar efectos ni llamadas. B/tarea siguen por UI.
- Tarea `b94eedef…`: plan Claude correcto, ejecución Codex con resultado que declara no haber completado el trabajo.
  Tres rutas permitidas quedan vacías (60 líneas borradas); errores reportados de heredocs, parche y `python`
  ausente. Pytest exit 5/0 casos/JUnit partial, mypy y comandos Django exit 1; Ruff pasa. Revisor REVISE; cero
  correcciones → REVISION_LIMIT, sin reintento, aceptación o commit de tarea. No se repara el resultado a mano.
- Consumo Claude 4/12, Codex 1/3. Claude reporta `claude-sonnet-5-5` bajo alias sonnet/low; Codex gpt-6-luna/low.
  CLI 2.1.310/0.164.0 y política corregida congeladas, compatibilidad condicionada. El transporte exit 0 no acredita
  éxito funcional. Servicio detenido, 0 jobs activos/encolados/locks, cinco procesos de agentes STOPPED.
- Intención del ejecutor sin TMPDIR, `/tmp` excluido por D059 y PATH sin venv del fixture, distinto del validador.
  Son indicios de un prerrequisito operativo, sin causa raíz o defecto del producto demostrados. Siguiente tarea
  **P012-T009**, diagnóstico documental/offline y propuesta concreta sin cambiar el TOML operativo, fuentes o
  resultado fallido. Si acredita defecto, acotar corrección sintética antes de relanzar. Nuevo tramo real requiere
  consentimiento; no reutilizar congelados con configuración distinta. T003/T004 siguen sin autorización.
- Solo documentación del producto; sin suites nuevas, cambios de seguridad/configuración global o acciones remotas.

## D192 — P012-T009: entorno del escritor y continuidad con fixture limpio

Estado: diagnóstico offline completado el 2026-10-24; propuesta elegida por HITL, operación real sin autorizar.
Fase: P012. [Diagnóstico, delta exacto, consentimiento posterior y comprobaciones](archive/phase-012/P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md).

- Intención congelada y TOML coinciden: ejecutor sin TMPDIR ni Python en PATH; el validador tiene entorno y mapa
  de ejecutables propios. El stream acredita `python` ausente y errores de caché Git/xcrun en `/tmp`; el rechazo
  de heredoc se conoce por el reporte del ejecutor, sin comando exacto conservado. No se demuestra la causa
  del truncamiento ni un defecto del harness; no se abre corrección de código ni se afirma eficacia de la propuesta.
- D059/D068/D174 conservados: checkout canónico, `/tmp` excluido, red false, approval never y confianza untrusted.
  TMPDIR explícito propuesto dentro del checkout, en `.local/codex-tmp` ignorado y 0700, sin añadir raíces externas.
  PATH propuesto incluye el venv Django. No se atribuyen efectos internos nuevos a Codex 0.164.0 ni se cambia modelo/esfuerzo.
- El run viejo agotó 0 correcciones: retry no invoca al ejecutor; revalidar no repara. Otro run rechaza el checkout
  sucio; cambiar composición no habilita reutilizar jobs congelados. No se restaura el diff ni se edita SQLite,
  TOML original, historial o presupuesto para desbloquearlo.
- HITL: el usuario elige **«Preparar la continuación con otro fixture limpio (recomendado)»**, tras aclarar que
  solo elige la propuesta y no inicia operaciones reales. Se propone B2 `projects/onboarding-b-t009` desde el
  commit inicial sintético `f6a2d9d`, preservando B íntegro; repetir incorporación B y una tarea por UI en registro
  nuevo. Copia `config/harness-local-t009.toml`, presets nuevos de la misma pareja y composición `django-t009`;
  defaults/composición del proyecto original intactos. Mismo wheel T008 y misma base operativa mediante API,
  sin reconstrucción, copia de resultados fallidos, reset del original o reescritura de registros previos.
- Consumo intacto Claude 4/12, Codex 1/3; saldo 8/2. Guion nuevo previsto hasta 4 Claude + 1 Codex, cero correcciones,
  mismos techos temporales y parada al primer fallo. La siguiente acción es pedir consentimiento explícito sobre
  los efectos/rutas de la propuesta; no está concedido por este HITL. T002 parcial, T003/T004 sin autorización.
- Once tests dirigidos correctos y check puro v7 sin procesos; copia SQLite/WAL/SHM para consulta, originales
  conservados. Solo documentación y comprobador documental sintético; sin CLI/proveedores reales, servicio,
  navegador, red, pruebas del fixture fallido, suites completas, cambios globales o acciones remotas.

## D193 — P012-T002: fixture limpio incorporado y rechazo por Ruff

Estado: continuación T009 autorizada y ejecutada el 2026-10-24; nueva parada, T002 sigue parcial.
Fase: P012. [Autorización, comprobaciones, resultados y conservación](archive/phase-012/P012-T002_CONTINUACION_T009.md).
Conserva D191/D192 sin atribuir al nuevo intento la resolución de la causa del truncamiento anterior.

- HITL: **«Autorizar esta continuación de T002»**, sobre la propuesta concreta T009 §5: B2 desde `f6a2d9d`,
  venv offline, copia TOML/presets/composición propios, preflight, servicio/UI, incorporación y una tarea nuevas
  en la misma SQLite; hasta 4 Claude + 1 Codex adicionales, cero correcciones. El usuario pide introducir la
  clave local directamente; no se imprime ni se documenta. T003/T004 quedan fuera del consentimiento.
- Mismo wheel/venv corregido `6efbd82`, distribuciones/CLI/wheels verificados por hashes, sin build o descarga.
  `onboarding-b-t009` limpio desde el árbol inicial, sin remotos/enlaces/alternates, Python 3.13.13 y TMPDIR
  privado 0700 dentro del checkout. `harness-local-t009.toml` 0600 añade solo los presets y composición acordados;
  huellas del proyecto original idénticas, cambio efectivo del escritor nuevo limitado a PATH/TMPDIR.
- Preflight real exit 0, CLI 2.1.310/0.164.0 con compatibilidad condicionada y ocho checks iniciales correctos.
  Registro `p012-b-t009` por UI en es/es, un turno Claude, doce propuestas revisadas y APPLIED por CAS;
  **incorporación COMMITTED `9808fd9`**, 15 originales intactos por bytes/permisos, README idéntico en su ruta.
  P001 ACTIVE y una tarea; no se repite el reenvío idempotente ya acreditado en D191.
- Tarea `f98b16d9…`: plan Claude, ejecución Codex gpt-6-luna/low y revisión Claude sonnet/low, procesos completos.
  El escritor usa Python/TMPDIR explícitos y conserva contenido en las tres rutas autorizadas; implementa
  validación de limit y once casos adicionales. Motor: **13 tests JUnit aprobados**, mypy y Django correctos;
  **Ruff E501 en dos líneas y formato fallan**. Revisor REVISE, **REVISION_LIMIT**, sin aceptación ni commit de
  tarea. La propuesta del revisor no se aplica: no se repara, formatea, revalida o reintenta el resultado.
- Consumo nuevo **3 Claude/1 Codex**, acumulado **7/12 y 2/3**; las tres Claude reportan claude-sonnet-5-5.
  Servicio detenido normalmente, puerto cerrado y clave eliminada; **7 jobs DONE, 9 procesos STOPPED, 0 locks**.
  **8186 filas previas intactas** en contraste de copias SQLite/WAL/SHM; B/diff anterior, TOML original,
  distribuciones e historiales conservados. B2 conserva HEAD documental y sus tres cambios sin commit.
- El fallo acreditado pertenece a la salida del ejecutor, sin defecto del producto demostrado. T002 continúa
  parcial y no acredita aún el flujo básico exitoso completo. Siguiente acción: concretar offline una propuesta
  de continuidad y someterla a HITL; la parada agota este consentimiento, sin permiso implícito por el saldo 5/1.
  Sin reutilizar el run bajo otra política, reparar manualmente, crear otro fixture o consumir modelos sin una
  autorización nueva. Sin nuevas tareas de producto por un defecto no demostrado, ni ampliación a T003/T004.
- Solo documentos de este repositorio; sin cambios de producto, modelos/migraciones, flujos, baseline pública,
  configuración global, smokes adicionales, tag, push o publicación. Checks documentales y diff al cerrar;
  suites completas y pruebas de los fixtures detenidos no se repiten.

## D194 — P012-T010: formateador declarativo optativo en local-config-8

Estado: implementada y verificada offline el 2026-10-24, tras elección HITL explícita; sin reanudar T002.
Fase: P012. [Alternativas y elección](archive/phase-012/P012-T002_PROPUESTA_CONTINUIDAD_RUFF.md),
[contrato, pruebas y guion posterior](archive/phase-012/P012-T010_FORMATEADOR_DECLARATIVO.md). Amplía D095 apoyándose en D133.

- La investigación confirma que el run agotado no admite otra política, revalidar no ejecuta/formatea y un
  nuevo run no admite el checkout sucio. No hay defecto del motor acreditado: validaciones y revisor rechazaron
  correctamente Ruff. Una nueva raíz desde el commit documental limpio de B2 puede registrarse como proyecto
  ya gestionado, sin repetir B; no se crea u opera en esta tarea.
- HITL: **«Implementar formateador declarativo offline (recomendado)»**. Se elige habilitar la capacidad D133
  al operador del perfil declarado, con tests sintéticos. No se elige ampliar Codex a 4 llamadas ni autorizar
  un ciclo de corrección. Tampoco se autoriza reconstruir/instalar, editar configuración privada o relanzar.
- Se introduce **local-config-8**, conservando el contrato y las huellas de v1–v7. Solo v8 admite el par opcional
  `formatter_argv`/`formatter_paths` en perfiles declarados: presentes van juntos y no vacíos; argv sin shell
  terminado en `--`, patrones relativos únicos, ejecutable mapeado y `authorize_profile_commands = true`.
  Omitir ambos conserva el perfil sin formateador. El ejemplo lo muestra comentado; `check-config` expone el
  par únicamente cuando está declarado. Se reutilizan diagnósticos y validaciones existentes.
- Sin cambiar motor/runner: D133 selecciona solo archivos cambiados, existentes, coincidentes y permitidos por
  el contrato, y formatea antes de validar/revisar. Registro nativo `formatter-paths`, timeout 120 s y formato 8
  de historial existentes. Revalidar no formatea. Aceptación y commit ligados a los bytes formateados.
  El ejecutor no gana shell, red o rutas; se mantienen las seis validaciones y las guardias del runner.
- V8 conserva detección CLI, presets, idiomas y recetas v2 de v7. V7 mantiene el descubrimiento automático al
  separarlo del identificador de última versión. Registro y mapa de generaciones reconocen v8, sin modificar
  módulos de recetas ligados a recibos. Los perfiles sin formateador conservan las huellas efectivas; cambiar
  formato/argv/patrones no adopta jobs anteriores: cuarentena antes de efectos, snapshots intactos.
- **28 regresiones nuevas**, además de **177 y 106 checks dirigidos**; **8 unittest correctos**. Recorrido nativo
  con CLI/herramientas falsas hasta commit, precedencia del formateador, evidencia del revisor y bytes del commit;
  carga sin procesos, errores, huellas/cuarentena, detección/parejas/idiomas, registro v8 y recetas v1/v2.
  No se presenta esta evidencia sintética como solución probada del intento real ni causa del truncamiento anterior.
- T002 conserva sus dos fallos y consumo **Claude 7/12, Codex 2/3**, servicio detenido. El guion posterior propone
  wheel/venv nuevos, clon limpio de `9808fd9` sin otra B, perfil/composición/presets propios, cero correcciones y
  una tarea. Previsión 2 Claude/1 Codex, sin permiso de consumo por esta elección. Falta concretar/revisar el
  tramo operativo y pedir consentimiento nuevo. T003/T004 y acciones remotas permanecen fuera.
- Flujos, especificación, arquitectura y documentos vivos actualizados; sin modelos/migraciones, API, UI,
  dependencias, códec o configuración global. Sin proveedores reales, servicio, build operativo, modificación
  de fixtures/TOML/SQLite privados, smokes, tag, push o publicación; baseline pública pendiente de T005.

## D195 — P012-T002: continuación con formateador y preparación operativa

Estado: autorizada y ejecutada hasta parada antes del alta el 2026-10-24; T002 sigue parcial.
Fase: P012. Concreta D194, sin reescribir D184/D191/D193.
[Propuesta, delta exacto y registro de ejecución](archive/phase-012/P012-T002_PROPUESTA_T010.md).

- HITL: **«Autorizar esta continuación de T002»**. Nuevo máximo 2 Claude/1 Codex, cero correcciones; incluye
  build/verificador/instalación offline, clon documental B2, TOML v8, preflight/checks, servicio/UI, alta/P001,
  dos commits documentales preparatorios y una tarea. Sin repetir B ni autorizar T003/T004.
- Se fija base `a7d8b33`, destinos dist-t010/venv-t010/managed-b-t010 y copia TOML privada. Transformador puro
  comprueba fuente/hash, conserva tablas previas y añade perfil/presets/composición propios; propuesta y archivo
  materializado de hash `e0e95abb…fbb6db`. Mismos modelos/esfuerzos/permisos; formateador solo en el perfil nuevo.
- Build correcto y clon independiente de `9808fd9`, 28 blobs intactos. Una comprobación del operador confunde
  modo Git 100644 con permisos de disco y provoca parada preventiva: 15 originales B2 en 0600, 13 documentos
  en 0644 frente a los 28 en 0600 del clon por umask. HITL preciso **«Igualar los 13 documentos y continuar T002»**:
  se ajustan únicamente esos trece modos y se comprueban los 28 contra commit/manifiesto, sin tocar B/B2.
- Verificador del wheel correcto con CLI falsas, instalación aislada y hash wheel `ead1b58b…b4710`; Python
  3.14.4 del harness y 3.13.13 del clon con 17 wheels por hash. Carga pura con procesos bloqueados acredita
  el perfil con formateador y cero correcciones. Preflight real exit 0, CLI 2.1.310/0.164.0 y política `1156d0c9…`;
  ocho checks iniciales verdes, pytest 2 casos/JUnit. `migrate` no-op conserva bytes SQLite.
- Servicio/login correctos. La UI v8 **oculta el selector de presets** porque su lista termina en v7. Impide
  seleccionar los presets autorizados; parada antes de preview/alta, sin usar defaults ni una API alternativa.
  Es un defecto del producto, a diferencia de los fallos anteriores del ejecutor. Se acota en T011 (D196).
- Servicio detenido normalmente, puerto sin listener/clave eliminada, **7 jobs DONE, 9 procesos STOPPED, 0 locks**.
  **13.785 filas anteriores idénticas** en las copias de todas las tablas SQLite salvo sqlite_*; B/B2/diffs,
  configuraciones y distribuciones previas conservan bytes/modos. No hubo registro/fase/run/commit nuevo del hijo.
- Consumo adicional **0/0**, acumulado **Claude 7/12, Codex 2/3**. No acredita formateador real, tarea COMMITTED
  ni T002 completa. La parada agota el consentimiento; conservar clon/TOML/wheel y evidencias, sin relanzar.
  La corrección offline posterior requiere propuesta y consentimiento nuevos antes de construir/operar otro wheel.

## D196 — P012-T011: paridad del selector de presets UI con local-config-8

Estado: implementada y verificada offline el 2026-10-24; sin otra operación real.
Fase: P012. Corrección del defecto observado en D195 conforme al contrato D194.
[Entrega, checks y próximo paso](archive/phase-012/P012-T011_PRESETS_UI_V8.md).

- El formulario compartido de registro/creación/actualización reconoce `local-config-8` como formato con
  selección de agentes por proyecto, igual que el backend. Se añade v8 a PRESET_FORMATS y al aviso en/es.
  Formatos antiguos/desconocidos mantienen su comportamiento; no se modifica API, permisos, política o TOML.
- Se exporta DraftFields para renderizar el componente real en tests con React/ReactDOM y el proveedor de
  idioma. Helper de pruebas con el TypeScript existente, sin dependencias nuevas. Ocho regresiones cubren las
  tres operaciones en en/es, presets filtrados por rol, modelo/esfuerzo seleccionados, v5–v7, fallback anterior/
  desconocido y ausencia de presets. Render sin efectos/HTTP, sin copiar fixtures o datos privados.
- **103 tests Node correctos**, incluidos los ocho nuevos; tipos y build Vite correctos. No se repiten suites
  backend/Alembic al no cambiar Python/esquema. No se atribuye al wheel T010 la corrección del checkout:
  no se construye/instala otro wheel ni se arranca servicio, navegador de QA, proveedores o modelos tras corregir.
- T002 sigue parcial y detenida, consumo 7/2 y resultados conservados. Próximo paso: concretar/revisar propuesta
  con dist-t011/venv-t011 nuevos y conservar clon/TOML preparados solo si coinciden sus manifiestos y no están
  registrados. Mismos límites, máximo nuevo previsto 2 Claude/1 Codex, cero correcciones; consentimiento antes
  de cualquier nueva preparación/operación, sin reponer llamadas, repetir B o extender a T003/T004.
- Documentos vivos/evidencia actualizados; sin cambio de diseño, modelos/migraciones, flujo implementado,
  baseline pública, dependencias, configuración global, tags, push o publicación. Cuerpos D001–D194 conservados.

## D197 — P012-T002: propuesta de continuación tras T011

Estado: propuesta concretada y revisada offline el 2026-10-24; consentimiento operativo pendiente.
Fase: P012. Concreta el siguiente paso de D196, sin reabrir el consentimiento agotado de D195.
[Propuesta completa, comandos futuros y petición HITL](archive/phase-012/P012-T002_PROPUESTA_T011.md).

- Base del producto `500a783`, con selector v8 corregido. Destinos nuevos dist-t011/venv-t011; conservar
  managed-b-t010 y harness-local-t010.toml, sin otra B, clon o transformación de configuración. Mismos id,
  perfil/composición/presets, puerto, modelos/esfuerzos, permisos, contrato y dos commits documentales por UI.
- Lecturas locales: 28 archivos iguales a blobs/manifiesto, 15 originales 0600 y 13 documentos 0644, clon limpio
  sin remoto/alternates; TOML 0600 de hash `e0e95abb…fbb6db`; destinos nuevos ausentes. SQLite íntegra en 0025,
  13.785 filas, 7 jobs DONE, 9 procesos STOPPED, 0 locks; clon sin registro/fase/run. Repetir guardias antes de operar.
- Propuesta: build/verificador/instalación offline, preflight/ocho checks, servicio/UI, registro/P001,
  preparación documental y una tarea. Máximo nuevo 2 Claude/1 Codex, acumulado máximo 9/12 y 3/3, cero
  correcciones y parada al primer fallo; cuatro horas y conservación de resultados anteriores. Hashes del
  paquete futuro pendientes, sin atribuirle los anteriores. Sin autorización de descargas o T003/T004.
- La petición de continuar/commitear autoriza esta preparación documental; AGENTS, T001 §7 y D196 requieren
  consentimiento específico para sus efectos operativos. No se construye/instala, ejecutan CLI reales o
  checks del fixture, inicia servicio, opera datos privados o consume modelos al concretarla.
- STATE/NEXT_STEPS/ROADMAP al día. Sin cambio de producto, esquema, API, flujo, configuración global,
  documentación pública o historia congelada; sin tag, push o publicación. T002 permanece parcial.

## D198 — P012-T002: tarea real COMMITTED con perfil declarado v8

Estado: T002 completada con evidencia acumulada; operación 2026-10-24 y cierre documental 2026-10-25.
Fase: P012. [Propuesta/consentimiento](archive/phase-012/P012-T002_PROPUESTA_T011.md) y
[resultado, matriz y límites](archive/phase-012/P012-T002_RESULTADO_T011.md). Concreta D197, sin reescribir D184–D197.

- HITL **«Autorizo.»** a la propuesta del commit `cc2ef5d`: producto `500a783`, dist-t011/venv-t011 nuevos,
  clon/TOML t010 conservados, máximo nuevo 2 Claude/1 Codex y cero correcciones. Sin repetir B, reparar resultados
  o autorizar T003/T004. Guardias de fuentes, ocho hashes, 17 wheels/lock, checkout/configuración y base correctas.
- Wheel `f22521ff…acd3201` construido/verificado/instalado offline fuera del checkout. Preflight CLI
  2.1.310/0.164.0 y ocho checks del clon correctos; migrate no-op en 0025, SQLite idéntica antes del servicio.
  Selector UI v8 permite claude-t010/codex-t010, perfil declarado python-django-t010 y composición django-t010.
  Registro p012-b-t010 es/es, bootstrap false, P001 ACTIVE desde los siete criterios literales del ROADMAP.
- Dos commits documentales UI/CAS `60246d5` y `f4a35ba` confirman AGENTS y D006 del operador, sin aprobar
  retroactivamente D001–D005. Originales intactos, checkout limpio y hashes adoptados antes de encolar por CAS.
  Run **`e3fa4ae6…` COMMITTED `6f021211b307`**: plan Claude, única ejecución Codex, formateador D133 sobre
  dos rutas Python permitidas (exit 0, sin cambios), seis validaciones/13 casos JUnit correctos y revisión ACCEPT.
- Diff de tres rutas idéntico al aceptado, ligado al commit sellado; regeneración mecánica de STATE/NEXT_STEPS
  del hijo. Hallazgo low de una referencia de línea en el flujo conservado; sin corrección manual/revalidación.
  Claude informa claude-sonnet-5-5 para el alias sonnet; Codex no informa modelo en los metadatos observados,
  selección gpt-6-luna/low congelada. Compatibilidad condicionada cli-14, sin extrapolar efectos internos.
- Evidencia acumulada satisface los cuatro criterios T002: B/idempotencia conservan procedencia D191/D193;
  esta continuación acredita el perfil/formateador v8 y la tarea actual, sin declarar una tercera incorporación.
  Los dos resultados REVISION_LIMIT siguen intactos; el éxito no demuestra la causa del truncamiento inicial.
- Nuevo **2 Claude/1 Codex**, total T002 **9/12 y 3/3**, cero correcciones; operación dentro de cuatro horas.
  Servicio detenido normalmente, puerto cerrado/clave eliminada, **11 jobs DONE, 12 procesos STOPPED, 0 locks**.
  **13.785 filas previas idénticas** por todas sus columnas; 1.136 filas nuevas normales y 14.921 finales.
  B/B2, diffs, TOML/distribuciones anteriores conservan hashes/modos; evidencia completa solo en el área privada.
- Siguiente T003: concretar/revisar propuesta propia de chat y backup/restauración sobre p012-b-t010 y pedir
  consentimiento antes del servicio/proveedores; T003/T004 sin autorización. Sin cerrar P001 del clon ni P012,
  operar este repositorio con el harness, cambios globales, tags, push o publicación. Baseline pública en T005.
- Documentos vivos al día, sin cambio de producto, modelos/migraciones, API o flujo implementado. Comprobaciones
  del tramo y documentales pertinentes; sin repetir suites completas. Historial y D001–D197 conservados.

## D199 — P012-T003: confirmación en cola con supervisor detenido

Estado: diseño operativo elegido por HITL el 2026-10-25; propuesta preparada, sin consentimiento de ejecución.
Fase: P012. [Propuesta, comprobaciones y consentimiento pendiente](archive/phase-012/P012-T003_PROPUESTA_CHAT_BACKUP.md).
Precedentes: D035/D040/D083/D174/D184/D198. Sin cambio de producto ni reescritura de T001.

- Al concretar T003 se contrasta una discrepancia del guion: aceptar la propuesta por hash/versión crea un run/job
  QUEUED `action=start`; el TOML conservado tiene supervisor=true. La aceptación notifica al supervisor y puede
  iniciar preparación/plan/ejecución, incompatible con «sin ejecutarla». Código y pruebas acreditan que es el
  comportamiento existente, no un defecto demostrado. No hay pausa HTTP ni aceptación diferida sin cola.
- Se consultan dos vías: supervisor desactivado y cola conservada, o definir una mejora de aceptación diferida.
  HITL: **«Usar supervisor=false y conservar la tarea en cola; revisar T004 antes de reactivar esa base.»**
  Detener el servicio tras el chat, crear una copia TOML nueva 0600 con único delta semántico supervisor=false,
  comprobar huellas/política y arrancar para aceptar por UI. Original intacto, sin editar SQLite ni jobs congelados.
- Tarea confirmada P001-T002 prevista QUEUED, cero intentos/preparaciones/comandos/locks; no describirla como
  terminada o inexistente. Conservarla y no reactivar el supervisor sobre esa base. T004 debe revisar su arranque
  explícitamente antes de operar; su futuro consentimiento no autoriza ejecutar la tarea de chat.
- Se conserva la instalación T011/base 500a783, proyecto p012-b-t010/HEAD 6f02121 y puertos 8024/8025.
  Techo propio T003 3 Claude/0 Codex y dos horas, sin saldo transferido de T002. Backup del producto con escritores
  detenidos y raíz state; restauración nueva marcada de consulta, sin configuración/supervisor, con lecturas y
  rechazo 409 de mutaciones. Resultados fallidos y resto de evidencias previas intactos.
- Comprobaciones preparatorias de solo lectura: 14.921 filas, 11 jobs DONE, 12 procesos STOPPED, cero locks/chat;
  clon limpio de 28 archivos; hashes wheel/toolchain conservados y referencias actuales bajo state. Comparación
  pura de ambos TOML en memoria: mismo proyecto, composición, política, agentes y versiones. Tres pruebas
  sintéticas de aceptación, comandos y backup/consulta correctas. Sin operación real ni llamadas nuevas.
- La elección del diseño no es consentimiento para servicio/proveedores, copia TOML o backup. Solicitar autorización
  específica sobre el guion revisado conforme a T001 §7. T003 sigue pendiente y T004 sin autorización; sin build,
  instalación, migración, cambios globales, ejecución del fixture, tags, push o publicación. Documentos vivos al día.

## D200 — P012-T003: chat real y backup restaurado con límite de UI

Estado: operación autorizada, ejecutada y detenida el 2026-10-25; dictamen de alcance UI pendiente de HITL.
Fase: P012. [Propuesta y consentimientos](archive/phase-012/P012-T003_PROPUESTA_CHAT_BACKUP.md) y
[resultado, evidencia y límites](archive/phase-012/P012-T003_CHAT_BACKUP_REAL.md). Concreta D199/D040/D083/D198.

- El usuario responde «Continúa.» tras el commit bcbf977 y la solicitud específica de consentimiento T003:
  guion 8024/8025, instalación T011 conservada, máximo 3 Claude/0 Codex y dos horas, sin T004. Guardias y
  preflight correctos; primer arranque detenido por origin_rejected de navegación automatizada, cero llamadas.
  HITL «Autorizo esa reanudación por la barra nativa, con los mismos límites.» Mismo producto/base/configuración,
  sin cambiar Host/Origin/CSRF o reponer presupuesto; incidencia y parada conservadas sin causa inventada.
- Dos turnos Claude sonnet/low, CLI 2.1.310/cli-14, modelo reportado claude-sonnet-5-5: ANSWERED sobre HEAD
  6f02121, evidencia antes/después intacta, siete documentos y run T002, cero locks. Respuesta coherente con
  comportamiento/tests; algunas referencias imprecisas y corrección espontánea en el segundo turno conservadas.
  `/estado` muestra P001 ACTIVE y tarea COMMITTED sin modelo; una única propuesta documental del revisor.
- Servicio del chat detenido antes de confirmar. Copia TOML 0600 supervisor=false, único delta semántico y
  huellas/política iguales; original intacto. UI verifica Supervisor detenido y acepta propuesta e294ae30…
  por hash/versión: P001-T002/run d235e9d5… QUEUED, job 14 sin owner ni intentos/preparaciones/ciclos/locks.
  Checkout, 28 archivos y HEAD intactos; no hay ejecución/commit de esa tarea. Guardia de T004 D199 conservada.
- Backup/verificación/restauración/verificación del producto correctos: 42 artefactos/13 runs, destinos nuevos,
  raíz state, marca query_only y execution_authorized=false. HTTP de run/diff/JUnit/métricas coincide, incluidos
  ambos REVISION_LIMIT de T002; POST inerte rechazado 409 restored_read_only. Sin reconstruir o reparar evidencia.
- UI restaurada /runs/id no ofrece página con project_id=null. RunRedirect lo declara explícitamente; el
  registro persistido se conserva, pero en consulta no se componen proyectos operativos. D040/entrega H5.2
  definen consulta API por id; el guion T003 añadió UI. Se consulta si cerrar T003 con evidencia API y límite UI,
  o mantenerla parcial y planificar una vista de consulta aparte. Dictamen pendiente, sin decidir diseño o
  cambiar criterios unilateralmente; no se atribuye a la UI lo solo comprobado por HTTP.
- Consumo T003 2/3 Claude y 0/0 Codex, dentro de dos horas originales. Servicios detenidos normalmente, ambos
  puertos cerrados/claves retiradas, 13 DONE/1 QUEUED/14 STOPPED/0 locks y grupos muertos. Las 14.921 filas
  anteriores idénticas; 1.877 nuevas normales, 16.798 finales iguales en fuente/bundle/restauración. Base operativa
  con SHA-256 idéntico tras backup/consulta; fixtures/diffs/configuraciones/distribuciones/herramientas intactos.
- Documentos vivos al día, producto/API/modelos/migraciones/flujos implementados sin cambios. No se repiten
  suites válidas ni validaciones del fixture. Evidencia completa privada, resultados anteriores conservados.
  Siguiente: resolver HITL de alcance. T004 sin autorización ni arranque sobre esa base, sin relanzar T003,
  nuevas llamadas, cambios globales, tags, push o publicación. P012 sigue abierta.

## D201 — P012-T012: vista UI de consulta planificada

Estado: alcance elegido por HITL y tarea planificada el 2026-10-25; implementación pendiente.
Fase: P012. [Plan, criterios y secuencia](archive/phase-012/P012-T012_PLAN_VISTA_CONSULTA.md).
Precedentes: D040/D144/D145/D199/D200. Los informes T003 y D001–D200 se conservan sin reescribirlos.

- Ante las alternativas de cerrar T003 solo con evidencia API o mantenerla parcial y planificar UI independiente,
  el usuario elige **«Planificar vista UI Aparte»**. T003 permanece parcial con chat/confirmación/backup/API
  acreditados; se añade T012 a P012 (doce tareas). Su implementación offline será el siguiente trabajo.
- El contrato planificado añade `read_only_archive` a SupervisorRead desde la marca D040, sin inferir copia de
  project_id=null, ausencia de agentes o supervisor=false. OpenAPI/tipos regenerados, sin migración, codec,
  formato de bundle o retirada de guardias. Modo ordinario conserva sus rutas y comportamiento.
- UI de copia en `/runs/:id`, entrada por id desde inicio y contexto permanente de consulta; sin proyecto
  ficticio o ProjectWorkspace. Evidencia/diff/JUnit/jobs/intentos/eventos existentes por id; consumo por run_id
  con procedencia y páginas. Reutilizar presentación y endpoints; sin inventario global, búsqueda o métricas
  nuevas, checkout/historial completo, backfill o reinterpretación de estados guardados.
- En copia no se montan controles de permisos/recuperación/ejecución/commit, formularios operativos o reenvíos
  pendientes; rutas directas operativas muestran contexto de consulta. La autoridad sigue siendo query_only,
  supervisor/puertos ausentes y rechazo 409. Pruebas sintéticas backend/router/React en en/es, incluso sin
  checkout, con estados incompletos/pendientes, acciones anunciadas y solicitudes guardadas sin producir efectos.
- Al implementar, paridad de flujo/arquitectura/especificación y Node/tipos/build/pytest dirigidos. Esta sesión
  solo planifica y verifica documentos: ninguna capacidad nueva implementada, fuentes de producto o baseline
  pública modificadas, operación privada, servicios, agentes/proveedores o llamadas nuevas.
- Tras T012, propuesta concreta y consentimiento nuevos para continuar T003 **solo con consulta UI** del wheel
  corregido, cero llamadas de modelos y sin repetir chat/aceptación/backup o cambiar resultados anteriores.
  T003 solo cerrará al observar su evidencia por UI y verificar conservación/parada. T004 no se autoriza y
  conserva la guardia D199 del job QUEUED; T005 depende también de T012 y de completar T003. Sin tags/push/publicación.

## D202 — P012-T012: vista UI de consulta implementada

Estado: implementado y verificado offline el 2026-10-25. Fase: P012. Implementa el contrato D201.
[Entrega, pruebas y propuesta posterior](archive/phase-012/P012-T012_VISTA_CONSULTA.md),
[flujo](flows/backup-consultation.md). D001–D201 e informes reales anteriores conservados por bytes.

- `SupervisorRead.read_only_archive` procede de la marca D040; OpenAPI/tipos regenerados. No cambia esquema,
  migraciones, bundle, codec, puertos, guardias query_only/409 o composición de proyectos en copias.
- La UI espera la señal antes de montar páginas operativas. Copia: inicio por id, `/runs/:id` independiente,
  contexto permanente, navegación de consulta y bloqueo de rutas operativas directas sin `ProjectWorkspace`.
  No accede ni reenvía solicitudes pendientes, ni monta permisos/recuperación/ejecución/commit aunque se anuncien.
- Presentación de evidencia extraída y compartida con el modo normal: estado/commit, ciclos/diff con hash,
  validaciones/JUnit, jobs/intentos/eventos y logs bajo demanda. Consumo paginado por `run_id` con procedencia,
  ausencias distintas de cero y modelos solicitados/reportados conservados. Eventos por cursores exactos.
- Lecturas iniciales, páginas y recarga explícita, sin polling de ejecución de estados históricos. Estadísticas
  globales de copia también sin polling ni sugerencias de backfill. Sesión/autenticación conserva su contrato.
  Sin marca se conservan la redirección canónica, ausencia de proyecto, controles y CAS operativos.
- Regresiones sintéticas backend y React/router en en/es, sin checkout y con acciones/peticiones guardadas;
  mismas lecturas/hash sin decodificar historial. No hay operación privada, proveedores o wheel operativo nuevo.
  T012 completa offline; T003 sigue parcial hasta QA UI real con consentimiento nuevo, cero llamadas de modelos
  y sin repetir chat/aceptación/backup. T004 conserva D199 y su autorización separada; T005 sigue pendiente.

## D203 — P012-T003: parada previa al build por identidad histórica del host

Estado: continuación UI autorizada y detenida antes del build el 2026-10-26; HITL pendiente.
Fase: P012. [Evidencia saneada y propuesta de reanudación](archive/phase-012/P012-T003_UI_T012.md).
Precedentes: D040/D199–D202; guion §4 de la entrega T012. Registros anteriores conservados.

- El usuario responde **«Autorizo.»** a la petición específica: build/instalación offline en destinos nuevos,
  consulta de restored/t003 en 8025, una hora y cero modelos. No autoriza T004 ni la base operativa.
- Antes del build coinciden los cinco hashes previstos de bases/manifiestos, las 16.798 filas en fuente/bundle/
  restauración, integridad/FK/esquema/marcas, hashes de herramientas y artefactos comprobados. Puertos cerrados,
  13 DONE/1 QUEUED/14 STOPPED/0 locks, destinos previstos ausentes. WAL existentes vacíos, sin immutable=1.
- La guardia `liveness(identity, group=True) == dead` falla con **unknown** en los 14 procesos históricos.
  Nombre de equipo y plataforma coinciden, pero difiere el componente uuid.getnode() de la identidad del host.
  Los 14 grupos locales están ausentes; esto no acredita muerte de identidades del host anterior. Sin causa
  atribuida al cambio de identificador, defecto de producto demostrado o modificación de identidades/guardias.
- Parada conforme al guion, sin construir/instalar/servir ni llamadas nuevas. No se completan comprobaciones
  posteriores de fixtures/preparaciones, QA UI o conservación final como si se hubiera recorrido todo el tramo.
  T003 sigue parcial, evidencia privada nueva y registro saneado; producto/API/modelos/flujos sin cambios.
- HITL: continuar solo la copia de consulta aceptando explícitamente la incertidumbre histórica, con límites
  originales y sin alterar SQLite/código, o conservar la parada. Pendiente respuesta; sin reanudar por inferencia.
  La evidencia de consulta nunca certifica muerte de escritores. T004 conserva D199 y su consentimiento separado.

## D204 — P012-T003: consulta UI restaurada verificada con salvedad autorizada

Estado: ejecutada, detenida y T003 completada con evidencia acumulada el 2026-10-26.
Fase: P012. [Resultado saneado, pruebas y límites](archive/phase-012/P012-T003_UI_RESULTADO_T012.md).
Precedentes: D040/D199–D203. La parada D203, su informe y los resultados anteriores se conservan por bytes.

- El usuario responde **«Autorizo»** tras el commit 92e800d y la pregunta específica: reanudar solo la copia
  de consulta aceptando `unknown` histórico, sin modificar identidades, SQLite, código o guardias. Se conservan
  hora original desde 07:23 UTC, cero modelos y base operativa detenida. No autoriza T004.
- Fuentes de producto f948429 y 24 hashes T012 correctos, checkout limpio en 92e800d, guardias de conservación
  repetidas. Build/verificador/instalación offline en dist-t012/venv-t012 nuevos: wheel **730891f8…f41520**,
  miembros exactos/recorrido sintético del verificador correctos y 259 archivos instalados iguales al wheel.
  Sin migración, inicialización real, preflight CLI o validaciones/formateador del fixture.
- Única consulta real de restored/t003 en 8025, sin agentes/supervisor/escritor de commits. Señal
  read_only_archive=true; UI Chrome es con contexto permanente, entrada por id/recarga, COMMITTED/6f02121,
  diff, seis validaciones/13 casos JUnit, enlace al original y métricas con procedencia. Dos REVISION_LIMIT
  sin commit y QUEUED sin intentos conservados; ruta operativa directa bloqueada sin workspace o acciones.
  Original/diff contrastados puntualmente por HTTP; no se repite la matriz API, mutación 409 o chat/backup.
- Recuperación del control nativo de Chrome y descarte del autocompletado Bitwarden, sin guardar credenciales
  o cambiar ajustes/guardias. QA UI observado y capturas/AX privadas; sin atribuir al producto los bloqueos
  de automatización. No se usa evidencia HTTP como sustituto del QA UI.
- Parada normal 07:42:13 UTC y conservación 07:43:02 UTC, dentro de la hora original: puertos cerrados/clave
  retirada; cinco hashes esperados y 16.798 filas por todas sus columnas iguales. 254 archivos privados previos,
  42 artefactos, tres fixtures/HEAD/diffs/modos y ocho herramientas intactos. 13 DONE/1 QUEUED/14 STOPPED/0 locks;
  tarea pendiente sin owner/intentos/preparaciones/ciclos. Cero llamadas nuevas, acumulado T003 2/3 Claude y 0/0 Codex.
- Las 39 referencias de identidad histórica siguen unknown y sus grupos locales ausentes; consulta no certifica
  muerte de escritores ni reinterpreta esas identidades. El nuevo servicio se detiene por su identidad viva.
  T003 cumple con chat/confirmación/backup/API de D200 más UI/conservación/parada de este tramo y esa salvedad.
- Sin cambio de producto/API/modelos/migraciones/flujos o baseline pública; sin repetir suites de producto
  válidas. T004 necesita propuesta que respete D199 y consentimiento separado antes de efectos; P012 sigue
  abierta, P001 del clon ACTIVE. Sin tags en este repositorio, push, publicación o operación del Django P009.

## D205 — P012-T004: propuesta con base independiente y sucesora vacía

Estado: alcance de sucesora elegido por HITL el 2026-10-26; propuesta preparada offline, operación sin autorizar.
Fase: P012. [Guion, TOML completo, hashes, comprobaciones y consentimiento](archive/phase-012/P012-T004_PROPUESTA_TYPESCRIPT.md).
Precedentes: D059/D091/D143/D168/D184/D192/D199/D204. Sin cambio de producto ni reescritura de T001.

- D199 conserva P001-T002/run d235e9d5… QUEUED y prohíbe reactivar su base. Se propone init-db exclusivo
  en state-t004/harness.sqlite3, state_dir propio y TOML nuevo, sin copiar filas ni registros. El supervisor
  solo consume la cola nueva. Omitir proyectos en TOML no se usa como aislamiento de la cola anterior.
- T004/T001 hablaban de planificación confirmada posterior «sin tareas». El cierre D091 crea la sucesora
  vacía desde ROADMAP; el plan posterior exige tareas. HITL: **«Confirmar P002 en ROADMAP durante la
  definición y terminar con P002 ACTIVE vacía tras el cierre (recomendado).»** Se aclara el criterio vivo T004;
  objetivo/criterios de P002 se confirman en bootstrap, sin conversación/plan P002 posterior al archivo.
- Conservar venv-t012/wheel 730891f8…f41520: 259 archivos instalados iguales y fuentes coincidentes. Siete
  hashes de herramientas pertinentes iguales a T001; versiones previstas 2.1.310/0.164.0, sin ejecutar CLI.
  Base anterior íntegra en 0025, 16.798 filas, 13 DONE/1 QUEUED/0 locks; hashes de tres bases y dos TOML
  coincidentes. Identidades históricas unknown/14 STOPPED conservan procedencia D204, sin certificar muerte
  ni extender la salvedad de consulta a ejecutar en esa base. Puertos 8024/8025 sin listener.
- Caché privada original vacía; objeto typescript@5.9.3 de 4.377.468 bytes en la caché local del checkout,
  integridad SHA-512 del lock exacta y SHA-256 10e108c9…87a1d3. Proponer copia exclusiva del objeto por digest
  a npm-cache-t004 nueva, sin red/credenciales/índices ni poblar otras cachés. npm ci real aún no acreditado.
- TOML/entornos nuevos acotados a TypeScript: defaults Claude sonnet/low y Codex gpt-6-luna/low por catálogo,
  TMPDIR del escritor dentro del hijo ignorado tras preparar, perfil/receta v2 sin cambios, es/es y cero
  correcciones. Creación por UI de p012-typescript-es, definición CAS, receta offline, una tarea sobre main.ts
  y flujo, READY/cierre/tag p001 solo del hijo y P002 vacía. Sin modelos, migraciones o dependencias nuevos.
- Techo propio 12 Claude/3 Codex, una ejecución normal, cero reintentos, cuatro horas desde preparación;
  parada al primer fallo y conservación final. Sin transferir saldos T002/T003 o ejecutar el job de chat.
  La elección HITL solo aclara alcance: T001 §7 y AGENTS exigen consentimiento específico antes de efectos.
- Cinco tests existentes sintéticos correctos: instalaciones independientes, receta v2 es, selección v1/v2
  v5–v8 y cierre con sucesora vacía. TOML contrastado sintáctica/semánticamente con rutas sintéticas;
  parsers/enlaces/presupuestos/historia/diff verificados. Sin build/instalación, npm, CLI/proveedores reales,
  servicio o escritura operativa. STATE/NEXT_STEPS/ROADMAP actualizados; T004 pendiente y P012 abierta.
  Sin cambios de producto/API/datos/flujos, baseline pública, archivos congelados, configuración global,
  tags en my_harness, push o publicación.

## D206 — P012-T004: receta completada y parada por preparation_required

Estado: ejecutada y detenida el 2026-10-26; T004 parcial, T013 offline añadida.
Fase: P012. [Resultado, matriz, parada y conservación](archive/phase-012/P012-T004_TYPESCRIPT_REAL.md).
Precedentes: D119/D168/D174/D199/D204/D205; propuesta e informes previos conservados por bytes.

- Consentimiento **«autorizo»** al guion 9aefae3: base/state/TOML/caché propios, instalación T012 conservada,
  máximo 12 Claude/3 Codex, una ejecución normal, cero correcciones/reintentos y cuatro horas desde 08:00:10 UTC.
  Guardias de fuentes/259 archivos, ocho herramientas, hashes y 16.798 filas previas correctas; sin build nuevo.
- Copia exclusiva del objeto TypeScript 5.9.3, preflight cli-14 2.1.310/0.164.0 e init-db 0025 correctos;
  nueva base sin proyectos/jobs anteriores. UI Chrome es/es crea p012-typescript-es bajo el padre confirmado.
  Tres turnos Claude ANSWERED y 16 propuestas CAS: documentos iniciales, aclaración de campos/criterios y tag.
  Bootstrap COMPLETED, commit raíz dbc2d74; única tarea P001-T001, P001 ACTIVE y tag previsto p001.
- Receta typescript-web-recipe-2/es COMPLETED, ocho pasos DONE: npm ci offline y tres validaciones exit 0,
  un caso JUnit passed de título normal/vacío y commit técnico bcf59d8. Idioma/hash/receta sellados e iguales
  en plan/recibo. TMPDIR ignorado del escritor creado tras preparar; checkout/recibo intactos y verificados.
- Una petición UI para encolar devuelve **409 preparation_required** pese a prepared=true/recibo válido.
  Cero runs de tarea o llamadas Codex; sin plan de tarea, reintento, READY, tag o cierre/P002 activa. Se conserva
  el rechazo y se para, sin otra API o reinicio para sortearlo. Consumo real T004 **3/12 Claude, 0/3 Codex**.
- Parada normal 08:15:59 UTC, puertos 8024/8025 cerrados/clave retirada. Conservación 08:25:50 UTC:
  base nueva íntegra con 4.623 filas, 4 DONE/9 STOPPED/0 locks; grupos propios muertos. 23 archivos/HEAD técnico
  iguales; 16.798 filas previas por todas sus columnas, 254 archivos/42 artefactos/tres fixtures/ocho herramientas
  intactos. Job de chat anterior QUEUED conservado; unknown histórico no se interpreta como dead.
- La traza estática localiza que frozen_versions fuerza resolve_project; refresh v7/v8 recompone sin
  project_environment_sha256 y resolve_project lo instala sin bind. La guardia admit exige el vínculo del recibo,
  correctamente; read de preparación consulta SQLite/archivos y puede mostrar prepared=true. Añadir **T013**
  para reproducir/corregir offline la pérdida con regresiones sintéticas, sin debilitar guardias o recetas.
- **«continúa.»** tras el rechazo conduce a conservación y corrección offline, no a reanudar el tramo real.
  T004 parcial, P012 abierta con trece tareas; T005 depende de T013 y del cierre real pendiente T004.
  Reanudación con propuesta/consentimiento nuevos, sin volver a definir/preparar o reparar el hijo a mano.
  En esta entrega no cambia producto, API, datos o flujo; sin suites completas repetidas, servicio nuevo,
  CLI/proveedores nuevos, instalación/build, cambios globales, tag en my_harness, push o publicación.

## D207 — P012-T013: vínculo del recibo tras resolución CLI

Estado: implementado y verificado offline el 2026-10-26. Fase: P012.
[Entrega, reproducción, pruebas y continuación propuesta](archive/phase-012/P012-T013_VINCULO_RECIBO.md).
Precedentes: D119/D168/D174/D206; el resultado real T004 se conserva por bytes.

- Regresión HTTP sintética reproduce el rechazo de T004: antes de preparar, 409 legítimo; después de receta
  COMPLETED/prepared=true, 409 preparation_required en vez de 202. Causa: refresh forzado v7/v8 recompone
  versiones base y resolve_project instalaba sin volver a ligar la huella derivada del recibo persistido.
- Tras refresh se llama al bind existente de preparación, antes de instalar/congelar versiones. Solo el recibo
  COMPLETED con recipe_config compatible aporta project_environment_sha256 exacto; el idioma se liga en la
  instalación normal. Sin copiar una huella anterior a una composición distinta o tocar snapshots/recibos/jobs.
- admit/verify_receipt no cambian: tareas/checks/cierres verifican vínculo/configuración/archivos/herramientas.
  Proyectos sin receta y formatos anteriores conservados. Sin cambios de receta/perfil/runner/motor, esquema,
  API, configuración global, dependencias o huellas de implementación congeladas.
- Catorce variantes nuevas: ocho HTTP para Django/TypeScript en/es v7/v8 y seis de config/archivo/herramienta
  alterados en ambas recetas v8/es. 24 tests del módulo y 226 relacionados correctos, un opt-in real omitido,
  ocho unittest correctos; aviso existente de Starlette/httpx. Arquitectura/flujo y documentos vivos actualizados.
- Sin build/wheel/instalación, servicio, CLI/proveedores reales o validaciones del fixture nuevos. Hijo/recibo/
  HEAD técnico bcf59d8 y parada D206 intactos, nuevo consumo 0/0; T004 sigue parcial en 3/12 Claude y 0/3 Codex.
- Propuesta posterior: dist-t013/venv-t013 nuevos con esta corrección, conservar state-t004/TOML/hijo, preflight,
  migrate no-op y servicio/UI 8024; una tarea, READY y cierre/tag p001 solo del hijo, P002 ACTIVE vacía.
  Máximo nuevo 3 Claude/1 Codex, acumulado máximo 6/12 y 1/3, cero correcciones y deadline original
  2026-10-26 12:00:10 UTC; si venció, revisar ventana explícitamente. Sin repetir definición/receta o usar otra
  base para sortear el resultado. T001 §7/parada exigen consentimiento nuevo antes de esos efectos reales.
- T013 completa y P012 abierta con trece tareas; T005 pendiente de T004. Sin tags en my_harness, push o publicación.


## D208 — P012-T004: tarea COMMITTED y check sin READY

Estado: continuación autorizada/ejecutada y detenida el 2026-10-26; T004 parcial.
Fase: P012. [Resultado, consentimientos y propuesta documental](archive/phase-012/P012-T004_CONTINUACION_T013.md).
Precedentes: D091/D168/D174/D199/D205–D207; informes anteriores conservados por bytes.

- Usuario autoriza build/instalación T013, única tarea y cierre del hijo, máximo nuevo 3 Claude/1 Codex.
  Ventana original vigente hasta 12:00:10 UTC. Base exacta 9a9fa5d938236d6dd72d72561647c006c73e42f6;
  fuentes y guardias de bases/fixtures/recibo/23 archivos/herramientas correctas antes de operar.
- dist-t013/venv-t013 nuevos: build/verificador aislado/instalación offline y 259 archivos del paquete correctos;
  wheel 70ee6883…6cc1bb. Preflight CLI 2.1.310/0.164.0 correcto, migrate current/0025 sin snapshot ni cambio
  SQLite. Misma base state-t004/TOML/recibo/hijo; sin repetir creación, receta o validaciones iniciales.
- Primera parada origin_rejected al navegar con extensión desde el login correcto; cero llamadas nuevas.
  Parada/conservación 08:53 UTC, 16.798 filas anteriores y 4.623 T004 iguales. HITL explícito autoriza
  reanudar por barra nativa; mismo wheel/base y límites, sin debilitar guardias. Acceso/login y enlaces Enter
  correctos. Una sola petición de tarea desde creación, con NEXT_STEPS contrastado.
- d1e35d32… COMMITTED en ae86967ba54a2e881ec876e1db6f6b332abfd770: versiones congeladas contienen el
  digest exacto del recibo, receta v2 y contexto es. Plan Claude, única ejecución gpt-6-luna/low y revisión
  ACCEPT sin hallazgos/permisos/correcciones; Claude sonnet/low reporta claude-sonnet-5-5. Tres validaciones
  correctas y XML original/un caso passed; la suite no acredita espacios interiores. Diff inspeccionado
  limitado a main.ts y flujo español, API/defecto/sufijo/h1 conservados; documentos mecánicos adoptados.
- Check c3a99262…/operación 8deeaafd… FAILED: proveedor termina exit 0, cinco criterios passed y verdict
  READY con required_action de refrescar prosa STATE obsoleta. El contrato exige acciones/preguntas vacías;
  se rechaza correctamente. Conservar payload/check/commit, sin convertirlo en READY o cerrar/taggear P001.
- Parada normal 09:00:45 UTC, puertos cerrados/clave retirada; 7 DONE/13 STOPPED/0 locks. Base previa 16.798
  filas intactas, 254 archivos/42 artefactos/tres fixtures/diffs/ocho herramientas conservados. T004: 6.012
  filas (1.389 nuevas; una fila de fase actualizada normalmente), recibo y checkout limpio en ae86967.
  Nuevo 3 Claude/1 Codex; acumulado T004 6/12 y 1/3. P001 ACTIVE, sin p001 o P002 activa.
- [Diff propuesto](archive/phase-012/P012-T004_PROPUESTA_ACTUALIZAR_STATE.diff) preparado sin editar el hijo: prosa STATE
  con hechos/commits actuales y check fallido, bloque gestionado conservado. HITL pendiente para edición
  documental por UI/CAS/hash/commit, un Claude adicional para check nuevo y cierre solo si READY. Máximo
  nuevo revisado 4/1, acumulado máximo 7/12 y 1/3; deadline original, sin reejecución de tarea. No se usa
  el saldo global como consentimiento. Sin cambios de producto/guardias/esquema, tags en my_harness o remotos.


## D209 — P012-T004: estado documental confirmado y cierre real del hijo

Estado: T004 completada con evidencia acumulada el 2026-10-26, tras HITL sucesivos.
Fase: P012. [Resultado, matriz, checks y conservación](archive/phase-012/P012-T004_CONTINUACION_T013.md).
Precedentes: D091/D168/D174/D199/D205–D208; D208 y los resultados fallidos se conservan.

- HITL **«Autorizar edición documental y 1 Claude adicional»**: actualizar exclusivamente prosa STATE
  mediante el editor del producto, conservando bloque gestionado, tarea COMMITTED y check fallido. Preview
  CAS a7396c355b6e… y diff concreto confirmados; document_edit e83c08fd… COMMITTED en
  **c58712eed9ff1bc57bc0521ada957ab7fce73222**, solo docs/STATE.md. Archivo igual a propuesta, bloque
  gestionado igual por bytes y hashes adoptados. Sin agentes en la edición ni otra ejecución Codex.
- Segundo check 4357e769… FAILED: exit 0, READY con cinco criterios passed y acciones/preguntas vacías,
  pero parafrasea el segundo criterion. La directiva existente exige copia literal y la guardia rechaza
  correctamente. No normalizar payload, redefinir criterio o debilitar contrato. Parada 09:13:45 UTC;
  6.757 filas T004/9 DONE/14 STOPPED/0 locks, recibo válido y HEAD limpio, sin tag/cierre.
- HITL **«Autorizar un check más con 1 Claude»**: un nuevo check sin cambios de producto/documentos/modelo/
  guardias/respuestas. Techo final nuevo **5 Claude/1 Codex**, acumulado T004 **8/12 y 1/3**, deadline
  original 12:00:10 UTC. Consentimientos individuales conservados; saldo global no autoriza otros efectos.
- Tercer check dd0d3be3…/b4189e44… **READY** válido sobre c58712e, evidencia 9b0e4f67fedf…: criterios
  exactos/passed, sin acciones/preguntas. Payload persistido comprobado con validate_phase_result; UI lista
  para cerrar, sin jobs pendientes o locks. Confirmación de motivo/checkbox autoriza solo el cierre previsto.
- **P001 CLOSED**, tag ligero **p001 del hijo sobre c58712e**, commit de archivo
  **ecbc47f1ea9142e8e141a90eaa2d963857dbd39a**. STATE/NEXT_STEPS archivados por bytes, SUMMARY/REVIEW
  generados; cuatro archivos íntegros. docs/phase no tenía artefactos: no atribuirle un traslado adicional.
  ROADMAP/documentos vivos renovados y **P002 ACTIVE sin tareas/runs/plan posterior**, conforme a D205.
- Parada final **09:19:04 UTC**, conservación **09:20:23 UTC**: 11 DONE/15 STOPPED/0 locks, 36 identidades
  propias de procesos/comandos dead, puertos cerrados y claves de las cuatro aperturas retiradas. T004 íntegra
  en 0025: **7.460 filas**, 2.837 nuevas frente a 4.623; 4.622 originales intactas, una fila de fase
  actualizada normalmente con definición conservada. Nueve intentos COMPLETE, una única ejecución/tarea.
- **16.798 filas anteriores iguales por todas sus columnas**, 254 archivos/42 artefactos/tres fixtures/diffs/
  ocho herramientas intactos; job anterior QUEUED y salvedad unknown de T003 conservados. Instalaciones T012
  y T013 verificadas contra sus wheels, TOML/recibo/archivos protegidos iguales, hijo limpio. Sin operar
  la base anterior o certificar sus escritores históricos.
- T004 cumple con la evidencia D206/D208/D209: creación/receta es, tarea/flujo/validaciones y cierre real.
  Un único JUnit existente passed; espacios interiores acreditados por inspección, sin ampliar cobertura.
  Dos checks inválidos y tres paradas conservados, sin reparar respuestas ni reejecutar tarea. Siguiente T005;
  P012 abierta. Sin cambios de producto/datos/flujos en my_harness, tag propio, push, publicación o configuración global.


## D210 — P012-T005: alcance público y candidato verificados

Estado: completada el 2026-10-26 por la continuación y commit local en inglés pedidos por el usuario. Fase: P012.
[Entrega, matriz, hashes, checks y sustitución](archive/phase-012/P012-T005_CANDIDATO.md). Concreta D157/D176/D183 sobre
D198/D200/D202/D204/D207/D209; no modifica los resultados o consentimientos reales anteriores.

- README/README.es por fila, CHANGELOG y baseline pública reflejan la pareja Claude 2.1.310 revisor/Codex 0.164.0
  ejecutor con cli-14; cuatro parejas y receta Django previas conservan su procedencia. B/perfil declarado v8,
  TypeScript v2/es hasta cierre, chat y consulta de backup acreditados solo en su alcance sintético/macOS ARM64.
  No se atribuye creación Django v2, matriz completa de idiomas, producción o reparación automática de formato.
- Docs públicas autocontenidas en inglés: v8, consulta independiente sin checkout/autoridad de ejecución y vínculo
  del recibo tras resolver CLI; flujos y prosa del diagrama de datos en paridad, sin cambios de ER/esquema o API.
  D194 pública equivale al contrato técnico (< D200); las decisiones operativas privadas no se publican.
  D151 histórica se conserva, superada solo en ese alcance por la nueva entrada. P001 pública sigue sin tareas.
- Candidato por lista positiva copiada de T015, **401 archivos/5.480.755 bytes**, manifiesto
  **cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a**. Diff contra P011: 14 añadidos,
  38 modificados, cero eliminados y 349 idénticos; sin Git/historia privada, datos operativos, cachés o symlinks.
  Wheel nuevo **eef56a29…4504ab**, sdist/pylock/checksums registrados; versión candidata 0.1.0 conservada.
- Validación offline sobre copia pública: **1760 pytest/29 subtests**, dos opt-in omitidas, **8 unittest/119 Node**,
  tipos/build, Alembic en SQLite nueva, check_distribution con agentes falsos, 31 Markdown/260 enlaces y 36
  diagramas sin fallos. Logs y error de los primeros envoltorios zsh documentados, sin fallo de suite o producto.
- Sustitución separada por HITL tras preparar candidato/checks: **«Sí, sustituir y conservar P011»**. Renombrado
  `my_harness_dist` a `my_harness_dist_p011_74cc9141` y copia nueva al destino original; 401 hashes/modos nuevos
  y 387 hashes de P011 verificados. Conservación autorizada, sin borrar el árbol anterior ni inicializar Git.
- T005 completada; siguiente T006 (revisión/expediente), P012 abierta. Sin proveedores/CLI reales, fixtures o bases
  operativos, red, CI remota, QA visual nueva, tag, push o publicación; este repositorio no se opera con el harness.

## D211 — P012-T006: dictamen favorable y expediente actualizado

Estado: completada el 2026-10-26 por la petición del usuario de continuar la siguiente tarea. Fase: P012.
[Revisión de salida](archive/phase-012/P012_REVIEW.md), [expediente nuevo](archive/phase-012/P012_EXPEDIENTE_APERTURA.md) y
[contraste estático](archive/phase-012/P012-T006_COMPROBACION.json). Concreta D183/D210 y conserva D157/D181/D182.

- Dictamen favorable de los siete criterios de salida en el alcance declarado, con evidencia acumulada y
  procedencia de cada tramo; no quedan correcciones obligatorias pendientes. Habilita T007, que no se ejecuta
  en T006. P012 sigue abierta; cierre documental y posterior aprobación explícita de publicación pendientes.
- B/idempotencia originales, tarea con perfil/formateador v8, chat/propuesta QUEUED, consulta API/UI restaurada
  y TypeScript v2/es hasta cierre acreditados en sus respectivos informes. Dos REVISION_LIMIT, dos checks
  rechazados e identidad histórica unknown conservados, sin reparar resultados o certificar muerte de escritores.
  T004 usa base aislada; saldos y consentimientos anteriores no habilitan nuevas operaciones.
- Candidato T005 conservado: 401 archivos/5.480.755 bytes, manifiesto cf191a40…9362a, wheel eef56a29…4504ab.
  Reproducción del manifiesto desde 99b1b995, fuentes públicas actuales, hashes/modos del destino, 387 hashes P011
  y paquete/checksums contrastados. No se regenera/sustituye el destino o paquete ni se repiten suites válidas.
- Expediente nuevo con fuente reproducible exacta, manifiesto y hashes completos; sustituye para operar al de
  P011 sin reescribirlo. Pasos remotos propuestos con owner/repo, identidad pública y visibilidad por concretar
  al autorizar: repositorio vacío, Git independiente/push, CI del commit exacto, visibilidad, reporte privado de
  vulnerabilidades y Release opcional. Referencias oficiales GitHub/CLI leídas sin operar cuentas o remotos.
- Solo documentación privada: parsers/enlaces/presupuestos, cuerpos D001–D210 y originales phase/archive
  conservados. Sin cambios de producto, datos, API o flujos; sin servicios, builds, instalaciones, CLI/proveedores
  reales, fixtures, smokes, commits/tags, push o publicación. Tras abrir, fuente principal pública según D157.

## D212 — Cierre documental de P012 y validación real archivada

Estado: cerrada y archivada el 2026-10-26 por la continuación solicitada por el usuario, tras D211. Fase: P012.
[Resumen](archive/phase-012/SUMMARY.md), [revisión](archive/phase-012/REVIEW.md) y
[registro de cierre](archive/phase-012/P012_CIERRE.md). Precedentes: D002/D088/D114/D140/D153/D182.

- La petición de commitear la tarea anterior, continuar la siguiente y finalizar con commit en inglés autoriza
  T007, señalada en STATE/NEXT_STEPS tras el dictamen favorable de T006. Trece tareas y siete criterios
  completados en el alcance declarado; no quedan correcciones obligatorias pendientes. Sin sucesora definida.
- STATE/NEXT_STEPS y todos los artefactos originales de docs/phase se conservan por bytes respecto del commit
  T006 ce4b5d2. MANIFEST registra origen/destino, tamaño y SHA-256. SUMMARY/REVIEW/P012_CIERRE y comprobación
  nuevos explican el cierre; los snapshots mantienen sus estados, enlaces y comandos en el contexto original.
  Archivo previo P000–P011 intacto; decisiones D001–D211 solo cambian enlaces de navegación al nuevo archivo.
- STATE compacta la base, NEXT_STEPS queda sin tareas y ROADMAP enlaza el cierre. Referencias vigentes de
  arquitectura, especificación y flujo de consulta reubicadas sin cambiar contratos, diagramas o comportamiento.
  README, README.es y docs/public permanecen iguales; candidato/paquete T005 y P011 conservados sin regenerar.
- El candidato mantiene 401 archivos/5.480.755 bytes y manifiesto cf191a40…9362a; wheel eef56a29…4504ab.
  Expediente P012 vigente, P011 histórico. Scripts con raíz derivada se reproducen desde los commits de origen
  o se inspeccionan con su ruta original simulada, sin modificar snapshots ni moverlos de vuelta.
- Evidencia real acumulada y límites de D211 conservados: pareja actual única, fixtures sintéticos/macOS ARM64/
  Chrome, dos REVISION_LIMIT, dos checks rechazados, propuesta QUEUED e identidad histórica unknown. No se
  certifica muerte de escritores ni se autoriza reactivar bases, ejecutar colas o consumir saldos anteriores.
- Cierre manual, separado del READY del producto y del cierre del hijo T004; sin registrar/ejecutar este
  repositorio con el harness, servicios, agentes, proveedores o smokes. Sin cambios de producto, datos, API,
  flujos, dependencias, instalaciones o configuración global; sin tag, push, CI remota o publicación.
  La apertura requiere instrucciones explícitas sobre el expediente y sus parámetros. Tras el primer push,
  repositorio público como fuente principal (D157); modo continuo v0.2.0 posterior, sin tareas (D156).

## D213 — Mantenimiento Git desactivado en fixtures de incorporación

Estado: aplicado el 2026-10-26 por petición de corrección y commit del usuario, sin fase nueva.
[Informe](phase/2026-10-26_CORRECCION_CI_ARCHIVO.md). Precedentes: D105/D110/D112, D125 y D212.

- El fallo de CI comunicado en `my-harness-archive` compara todo el checkout y `.git` antes/después de rechazar
  Git sin `--no-lazy-fetch`. El único delta es la desaparición de `.git/objects/maintenance.lock`; el método
  Git del inventario está sustituido desde su primera llamada y no llega a ejecutar un proceso.
- El helper de `tests/product/test_project_onboarding.py` invocaba Git real para crear/commitear los fixtures
  sin desactivar su mantenimiento automático. Trace2 reproduce de forma determinista el lanzamiento de
  `git maintenance run --auto --quiet --detach` durante ese commit en el entorno local.
- Las llamadas de ese helper pasan `-c gc.auto=0 -c maintenance.auto=false`, igual que el adaptador de
  producción ya hacía. Solo afectan al proceso de Git del fixture; no se cambia configuración global ni local
  persistente. Se mantienen las comprobaciones de bytes completas, sin ignorar locks ni añadir esperas/reintentos.
- Una regresión observa los procesos hijos reales de Git con Trace2: falla antes de la corrección y pasa
  después. El informe registra las comprobaciones locales y sus límites; CI remota sin ejecutar en esta tarea.
- La tabla vigente de ROADMAP marca P012 completada el 2026-10-26 y enlaza su resumen archivado, conforme a
  D212. No se reescriben snapshots/expedientes congelados ni se regenera el candidato público.
- La subida del archivo a GitHub comunicada por el usuario no se confunde con la apertura independiente de
  P012. Sin push, acciones remotas, proveedores, smokes ni ejecución del harness sobre este repositorio.

## D214 — Candidato público actualizado tras la corrección de CI

Estado: actualización local autorizada y completada el 2026-10-26, sin fase nueva.
[Suplemento de apertura](phase/2026-10-26_ACTUALIZACION_CANDIDATO.md). Precedentes: D157, D210–D213.

- El usuario pide actualizar `my_harness_dist` tras comprobar que conservaba el helper anterior a D213.
  Se exporta la revisión exacta `08f27bc` con la lista positiva congelada de P012, sin modificar el exportador
  archivado ni mezclar documentación/historia privadas con el árbol público.
- Se conserva el original P012 íntegro como `my_harness_dist_p012_cf191a40`; P011 y los snapshots/evidencias
  archivados permanecen intactos. El árbol corregido conserva 401 archivos, con 400 idénticos y solo
  `tests/product/test_project_onboarding.py` modificado; sin añadidos/eliminados ni cambios de modos.
- Nuevo árbol de 5.481.629 bytes, manifiesto `5ef17ff3…4d4c55`. El suplemento y sus manifiestos actualizan la
  referencia operativa de apertura; no se presenta la identidad nueva como la que verificó T005/T006.
- Pruebas sobre una copia aislada del árbol exportado, con dependencias desde caché offline. Sin entornos,
  cachés o resultados en el candidato final. El suplemento registra resultados y sustitución verificada.
- La corrección solo afecta a pruebas, fuera de las entradas de construcción del wheel/sdist; se conservan
  los artefactos originales, sin reconstrucción ni nueva evidencia de proveedores. Sin acciones remotas,
  publicación, servicios, smokes o configuración global en esta tarea.
- El usuario solicita después un commit: se registran en inglés la actualización documental, el adaptador
  reproducible y sus manifiestos/evidencias, sin volver a modificar el candidato ni hacer push.


## D215 — P013: instalación guiada y configuración desde la UI

Estado: fase abierta y planificada el 2026-10-26 por petición explícita del usuario; implementación pendiente.
[Plan](phase/P013_PLAN.md), [tareas](NEXT_STEPS.md) y [flujo planificado](flows/configuration-setup.md).
Precedentes: D049/D051/D078/D095/D118/D150/D156/D157/D161/D174/D194/D212–D214.

- El usuario aprueba las propuestas de simplificación discutidas antes de publicar y pide una fase nueva.
  P013 recoge instalación/arranque automatizados, asistente inicial y gestión de configuración global y por
  proyecto desde UI. Quince tareas pendientes; siguiente T001, contrato previo a implementación.
- Entradas propuestas `scripts/install` y `scripts/start`: venv/directorios creados por herramientas, opciones
  de rutas/caché, primera preparación con red y repetición offline. `.local/` no es requisito del equipo.
  Mantener locks, comprobación del paquete y uso real del wheel fuera del checkout; `scripts/dev` para desarrollo.
- Asistente global determinista antes de configurar agentes; detección y formularios para datos mecánicos,
  elección de proveedor/modelo, identidad Git, almacenamiento y raíces. No invocar modelos para configurarlos.
  Archivo TOML generado/editable desde UI, validación y confirmación de la versión exacta antes de activar.
- Perfil propio por proyecto tras concretar documentación y arquitectura; incorporar usa también inventario
  del HEAD sellado. Conversar no exige composición de stack previa. Revisor propone, ejecutor prepara/comprueba
  lo autorizado y harness recoge validaciones/evidencia; usuario confirma activación. Ejemplos Django/TypeScript
  y recetas actuales quedan como ayudas opcionales, sin limitar stacks a sus plantillas.
- Edición manual o asistida global/por proyecto desde UI, con diff e impacto visibles. Ayuda IA global solo
  tras configurar clientes. Revisor conserva solo lectura; ejecutor sin escritura general del TOML global;
  aplicación valida y guarda archivos. No equivale a modificar configuración global de Git/CLI/uv/npm/shell.
- T001 fija autoridad y localización fuera de checkouts de archivos globales/por proyecto, vínculo con SQLite,
  versiones, activación/reinicio, guardado atómico/CAS, recuperación, backup y compatibilidad de formatos 1–8.
  No se inventan ahora tablas, revisiones o un número de formato nuevo. Jobs, recibos e historiales congelados
  conservan su procedencia; una propuesta de perfil no acredita herramientas instaladas ni validaciones pasadas.
- Publicación aplazada hasta el cierre satisfactorio de P013, con candidato/paquete, evidencia y expediente
  nuevos. Sustituye la ausencia de sucesora y apertura como siguiente paso que reflejaban D212/D214, sin reabrir P012 ni
  reescribir sus snapshots, dictámenes, expedientes o candidatos originales. D157 sigue rigiendo tras el primer push;
  modo continuo D156 continúa reservado para después de la apertura en v0.2.0.
- Abrir la fase solo autoriza esta planificación documental. No ejecuta sus tareas de producto ni autoriza
  harness sobre este repositorio, agentes/proveedores/smokes, configuración global del equipo, reactivación de
  bases/fixtures anteriores, commits no solicitados ni acciones remotas. Cerrar P013 dejará pendiente la
  autorización concreta de apertura con owner/repo, identidad pública y visibilidad.

## D216 — P013-T001: instalación aislada y arranque sin configuración

Estado: diseño concretado el 2026-10-26; implementación pendiente T002–T006. Fase: P013.
[Contrato §2–§3](phase/P013-T001_CONTRATO.md#2-instalación-y-actualización),
[flujo](flows/configuration-setup.md). Concreta D215 conservando D051/D150/D157.

- Instalación desde clon construye/verifica con locks; desde paquete recibe material de verificación
  autocontenido, sin Node ni checkout como requisito. Venv y generación propios fuera de checkouts,
  cachés/rutas/Python/uv elegibles; offline por defecto y red explícita, sin descargar herramientas ni cambiar
  ajustes globales. Repetición verifica recibo `installation-1`; actualización explícita conserva generaciones/datos.
- `scripts/start` usa el venv instalado y parámetros explícitos de DB/configuración/puerto/temporal privado,
  no instala ni migra al arrancar. Solo base ausente se inicializa exclusivamente. Base existente pasa por
  validación; esquema antiguo exige parada/instantánea/migración D150 aparte, sin rollback automático.
- Arranque sin configuración admite asistente autenticado y determinista sin supervisor consumidor/modelos;
  archivo inválido bloquea ejecución y conserva evidencia. Sesión/Host/Origin/CSRF también en primer uso.
  Consulta D040 tiene prioridad y no carga agentes/configuración operativa. Configuración no decide su propia
  ruta de arranque ni traslada datos desde la UI.
- El verificador actual depende de fuentes/frontend y fixtures del checkout: T002 debe extraer/reutilizar su
  verificación para la entrada desde paquete; checksums solos no sustituyen D051. T012/T013 acreditarán los
  recorridos, sin atribuirles evidencia previa. No se ejecutan instalaciones, servicios ni smokes en T001.

## D217 — P013-T001: archivos versionados y activación de configuración

Estado: diseño concretado el 2026-10-26; implementación pendiente T004–T006/T010–T011. Fase: P013.
[Contrato §4–§6](phase/P013-T001_CONTRATO.md#4-archivos-formatos-y-autoridad),
[backup §10](phase/P013-T001_CONTRATO.md#10-backup-y-fallos-de-frontera).
Concreta D215; conserva D049/D078/D118/D174/D194 y formatos históricos.

- Reservar `local-config-9`, `project-config-1` y `configuration-operation-1`. Global sin composición obligatoria;
  registro/idiomas/confianza siguen en SQLite. Perfil/composición propios en archivo por proyecto, con referencias
  selladas a global. Ejemplos copiados con procedencia, sin referencia mutable compartida. Sin secretos ni nuevos
  permisos implícitos; límites TOML 64 KiB, directorios/archivos nuevos 0700/0600 fuera de checkouts.
- TOML inmutable por versión es autoridad del contenido; referencia activa en SQLite es autoridad de activación.
  Copias `global.toml` y `projects/<id>/project.toml` son editables, no hot reload. Intención previa, CAS de
  versiones/hashes, publicación atómica por archivo y fsync; ninguna activación parcial entre archivos/SQLite.
  Conflicto/caída conserva base/candidato y exige conciliación verificable, sin última escritura gana.
- Guardar no activa. Toda global confirmada requiere reinicio con admisión cerrada hasta promoción validada;
  perfil de proyecto se activa sin reinicio bajo barrera transaccional de admisión/commit. Rechazar activación
  con trabajo pendiente según D118, sin cancelarlo ni reescribirlo; planes PROPOSED pasan a SUPERSEDED.
  Cambios globales muestran impacto y revisiones derivadas exactas de proyectos afectados.
- Cambio externo de copia editable bloquea nuevas operaciones del ámbito hasta importación/descarte por CAS;
  no inyecta valores en jobs activos. Deriva de versión inmutable bloquea efectos/cuarentena. Jobs/snapshots/
  recibos previos intactos. Asistencia usa pareja activa congelada, nunca la candidata en la misma sesión.
- Lectura/operación 1–8 conserva hashes y reglas; conversión al editor explícita por conjunto, originales intactos.
  Backup nuevo incluye TOML/versiones/intenciones por bytes y hashes; restore sigue solo consulta sin originales,
  clientes ni autoridad de reparación/ejecución. Sin modelos, migraciones, API ni formatos implementados en T001.

## D218 — P013-T001: perfil tras contexto y preparación antes de activar

Estado: diseño concretado el 2026-10-26; implementación pendiente T007–T011. Fase: P013.
[Contrato §7–§9](phase/P013-T001_CONTRATO.md#7-dos-entradas-commits-y-perfil-preparado),
[flujo](flows/configuration-setup.md). Concreta D215 y amplía el recorrido actual D095/D119/D161.

- Alta nueva/B con agentes/Git/raíz/idiomas y capacidad documental, sin composición de stack ficticia ni
  capacidad de tareas. Documentación/arquitectura o inventario/HEAD preceden a la propuesta estructurada del
  revisor. Propuesta separada de borradores D088; preguntas/evidencia por comando, herramientas diferidas y
  validaciones significativas antes de aceptar documentos. Ejemplos Django/TypeScript opcionales.
- Conservar commit documental raíz/B y adopción P001 antes de preparar; TOML privado fuera del checkout.
  Después confirmar plan técnico, preparar/comprobar y conciliar commit técnico si cambia contenido versionado.
  Activación propia posterior exige recibo/evidencia compatible y confirmación exacta; P001 ACTIVE no equivale
  a perfil operativo. Un fallo conserva documentos/operación y puerta de tareas cerrada.
- Reservar `project-profile-preparation-1` para preparación genérica, sin renumerar recetas/recibos v1/v2.
  Ejecutor acotado, harness ejecuta argv exactos y recoge evidencias; red/dependencias/archivos/límites visibles,
  journal/locks/procesos y recuperación conservadores. Ningún agente escribe configuración global general.
- Perfil/comandos/herramientas/locks cambiados requieren comprobación nueva; cambios solo de agentes/global
  pueden conservar evidencia de entorno tras verificar igualdad técnica, sin modificar el recibo original.
  Proyectos 1–8 sin receta conservan admisión hasta importación explícita. Activar no repite alta ni commits.
- UI/API separan propuesta, guardado, preparación y activación, en/es y con CAS/replay. Detalles de tablas/DTO
  quedan para sus entregas con paridad de diagrama/OpenAPI/tipos; no son funcionalidades existentes en T001.

## D219 — P013-T002: instalador por generaciones y paquete autocontenido

Estado: implementado el 2026-10-26; validación de orquestación sintética, recorrido instalado pendiente
T012/T013. Fase: P013. Concreta D216 sin alterar D051/D150.
[Entrega](phase/P013-T002_INSTALACION.md), [flujo](flows/configuration-setup.md).

- `scripts/install` selecciona clon o paquete local `--dist`, Python/uv locales y destinos/cachés explícitos.
  Offline por defecto, red solo con `--allow-network` y plan visible; no descarga herramientas, modifica
  ajustes globales ni requiere `.local/` o venv de desarrollo. Desde paquete no exige Node/npm ni fuentes/tests.
- Nuevo material `distribution-1`: manifiesto de miembros/hash de wheel/sdist, metadatos esperados, wrappers,
  verificador y fixture sintético, todos incluidos en SHA256SUMS. Build conserva primero la comparación exacta
  contra las fuentes/UI/locks y componentes retirados; verificación común sin checkout rechaza miembros
  ambiguos/enlaces, hashes alterados y dependencias sin pins/hashes. Conserva el recorrido instalado D051.
  Los hashes detectan alteración respecto al material entregado; no son una firma del distribuidor.
- Generaciones definitivas sin mover venv; intención/recibo privado `installation-1`, checks y hashes de
  paquete/locks/herramientas/venv. Exclusión de instaladores, fsync y referencia atómica `current.json` solo
  tras éxito. Repetición verifica bytes/recibo, sin reinstalar; otro contenido requiere actualización explícita
  y declaración `--writers-stopped`. Fallo conserva generación/diagnóstico y referencia anterior.
- Destinos privados fuera de checkouts y no solapados; ocupados sin recibo válido bloquean. Nueva instalación
  exige datos/configuración vacíos; actualización conserva sus rutas/contenido y generaciones previas.
  No crea DB/TOML, migra/restaura, borra ni cambia permisos ajenos. D150 sigue siendo una acción separada;
  declarar parada no descubre procesos ni acredita muerte de escritores.
- Caché elegida con subdirectorios uv/npm; build/verificador reciben ejecutables/cachés sin activar entorno.
  Build independiente conserva cachés históricas por defecto. Dependencias se sincronizan por pylock/hashes,
  solo wheels y copia en venv; verificación instalada siempre offline con ámbito sintético aislado.
- T002 prueba orquestación con ejecutables falsos y archivos temporales. Sin instalación/servicio/smoke real,
  proveedor, harness sobre este repositorio, cambio de esquema/API/UI/TOML, candidato anterior o acción remota.
  T003 implementará arranque; T012/T013 acreditarán primer uso/paquete nuevo bajo autorización correspondiente.

## D220 — P013-T003: arranque instalado y exclusión de instancia

Estado: implementado el 2026-10-26; validación sintética de orquestación/señales, recorrido instalado
pendiente T012/T013. Fase: P013. Concreta D216 conservando D051/D150/D219.
[Entrega](phase/P013-T003_ARRANQUE.md), [flujo](flows/configuration-setup.md).

- `scripts/start` resuelve/verifica `current.json`, recibo `installation-1`, paquete y venv. Ejecuta su Python
  con `-I -B`, módulo CLI instalado y cwd en datos, sin uv/Node/Vite/checkout como runtime. Los wrappers se
  entregan con `distribution-1` y SHA256SUMS en los paquetes nuevos; candidatos anteriores intactos.
- Rutas fijadas antes de leer TOML: DB bajo datos del recibo y configuración bajo su directorio propio,
  sin adoptar otra instalación por nombres coincidentes. Defaults `harness.sqlite3`, `global.toml` si existe,
  puerto 8013 y temporal `data/tmp`; opciones absolutas, sin enlaces/checkouts, temporal privado 0700.
  No recrea raíces ausentes ni cambia permisos ajenos; variables de runtime/configuración/Git del operador
  filtradas. Usa intérprete ya instalado: no instala, descarga ni toca ajustes globales del equipo.
- Preflight en el paquete instalado valida esquema por SQLite de solo lectura antes de servir, sin cambiar
  WAL de bases antiguas. Solo DB ausente y sin auxiliares pasa por `init-db` exclusivo. Puerto ocupado,
  TOML explícito ausente/inválido, referencia alterada o esquema incompatible bloquean; D150 exige acción
  separada con parada declarada, instantánea y migración, nunca dentro de `serve`/reinicio.
- Consulta D040 tiene prioridad y omite TOML operativo. Sin TOML, T003 usa la UI protegida de consulta ya
  existente, sin consumidor gestionado: no anuncia implementado el asistente T005/T006 ni la autoridad T004.
  No modifica contratos TOML 1–8, API/UI/modelos/migraciones ni jobs/snapshots/recibos históricos.
- Locks de instancia y de instalación retenidos por wrapper e hijo excluyen otro servicio y la actualización
  cooperativa aun tras SIGKILL del wrapper. SIGINT/SIGTERM se reenvían al grupo del hijo y se espera su salida;
  conserva códigos, datos y archivos de diagnóstico. No limpia guardias persistidas de jobs ni interpreta
  un lock liberado como prueba de que hayan muerto escritores o proveedores.
- Pruebas con intérprete/procesos sintéticos y DB temporal, incluido wrapper separado del checkout, señales,
  caída del wrapper, exclusión, reinicio y errores. Sin instalación/servicio/smoke/proveedor real, harness sobre
  este repositorio, cambios globales o acciones remotas. Siguiente tarea T004.


## D221 — P013-T004: journal y referencias de configuración

Estado: implementada y verificada con archivos/SQLite sintéticos el 2026-10-26; integración API/runtime y
recibos pendiente T005–T011. Fase: P013. Concreta D217, sin alterar parsers/hashes 1–8, D118 ni snapshots.
[Entrega](phase/P013-T004_CONFIGURACION.md), [datos](DDBB-DIAGRAM.md#configuración-versionada-p013-t004),
[flujo](flows/configuration-setup.md).

- Parser de editor separado: global `local-config-9` sin proyectos ni composición obligatoria reutiliza
  validaciones v8; proyecto `project-config-1` declara perfil completo, comandos/entorno/política/agentes
  efectivos e identidad/referencia global exactas. Borrador incompleto no activa; claves desconocidas,
  credenciales reconocibles y tamaños inválidos se rechazan. No se detectan/invocan clientes al parsear.
- Tres tablas aditivas en `0026_configuration`: ámbitos con CAS y referencias guardada/activa/pendiente,
  revisiones inmutables y operaciones `configuration-operation-1` con clave única/request hash/journal/actor.
  Contenido autorizado solo en TOML inmutable; SQLite no es otra configuración editable. El downgrade con
  operaciones existentes bloquea para no perder historia.
- Preview liga candidato/diff, validación, base/hash activo, motivo y directorios. Intención comprometida antes
  de publicar; exclusión flock más barrera SQLite, temporales exclusivos, replace/fsync y finalización del
  conjunto verificado. Caída conserva intención; recuperación requiere declaración de parada, lock efectivo y
  preview exacta de bytes base/candidatos. RECOVER audita la confirmación; replay no repite publicaciones.
  Rutas privadas 0700/0600, UID, límite 64 KiB, sin enlaces/hardlinks/especiales ni solapamiento con checkouts.
- Guardar no activa. Global agenda un conjunto por id de activación y promueve tras reinicio declarado y
  revalidación; fallo conserva anterior y pendiente. Borradores pueden guardarse mientras espera. Proyecto
  activa sin reinicio solo con verificador de preparación del servicio, obligatorio y sin fallback. T008/T009
  aportarán binding de recibos/HEAD y recomposición, no un booleano de una petición o de IA.
- Activación revalida bajo barrera de admisión/commit: trabajos, locks, preparación, aceptación/commit,
  propuestas/borradores y operaciones documentales pendientes bloquean; planes PROPOSED se superseden.
  Global exige revisiones exactas compatibles de todos los perfiles activos afectados; editar uno no cambia otro.
  Cambios externos se importan o descartan por CAS, sin hot reload ni reparación silenciosa de inmutables.
- El almacenamiento se entrega sin endpoints/UI, consumidor v9 ni promoción automática en arranque; quedan
  para sus tareas. Importación/conversión integral de legacy y bundle con los TOML en T011. Hasta entonces
  backup actual rechaza bases con operaciones nuevas, en/es, para no acreditar una copia sin sus archivos;
  consulta restaurada conserva prioridad y no toca originales.
- Sin instalaciones/servicios reales, harness sobre este checkout, agentes/proveedores/smokes, configuración
  global del equipo, CI remota, tag, push o publicación. Commit local solicitado por el usuario; P011/P012/D214
  y sus candidatos/artefactos conservados.

## D222 — P013-T005: asistente API y arranque con autoridad global versionada

Estado: implementada y verificada con API/archivos/SQLite y clientes sintéticos el 2026-10-26. Fase: P013.
Concreta D216/D217/D221 y conserva D040/D150/D174.
[Entrega y checks](phase/P013-T005_ASISTENTE_API.md), [flujo](flows/configuration-setup.md).

- `serve` selecciona directorios de configuración/estado antes de leer TOML; `scripts/start` transmite los
  del recibo. El preflight conserva esquema/consulta, pero deja el TOML ausente/inválido al asistente protegido.
  No hay migración silenciosa ni sustitución de archivos. Consulta D040 prevalece sin leer rutas originales.
- API autenticada `/api/managed/configuration`: estado/referencias, detección determinista por PATH explícito,
  formulario JSON o TOML, preview/diff, guardado CAS idempotente, activación separada para reinicio, cancelación
  y consulta/conciliación de intenciones. Directorio de estado fijado por arranque; no se trasladan datos desde UI.
  Comprobación explícita version/help reutiliza D174, sin inferencia/login ni credenciales automatizadas.
- Parsear, GET, preview, guardar y activar no lanzan clientes. Solo `/check-clients` ejecuta preflight con entorno
  explícito. Detectar no hereda PATH, no recorre home ni lee identidad Git/configuración global; los valores
  manuales siguen sujetos a los validadores existentes. Diagnósticos propios en/es sin contenido crudo.
- Guardar no activa; arranque promueve el conjunto pendiente por la primitiva T004 antes de componer consumidores.
  Error conserva referencias y bloqueo. Solo bytes inmutables autorizados componen la global v9; copia editable
  y cambios externos no recargan configuración. La promoción no certifica muerte de escritores ajenos.
- HTTP cierra mutaciones gestionadas cuando falta autoridad válida; la misma puerta se revalida dentro de la
  barrera SQLite de escritura para cubrir carreras con activación. Configuración y preferencias usan carriles
  propios: permiten resolver setup/idioma sin habilitar trabajo. No se reconcilian altas/preparaciones al arrancar
  sin autoridad ni se inicia supervisor en ese estado.
- Loader/formas/hashes 1–8 intactos. Consumo v9 exclusivo desde referencia activa del editor; global READY no
  concede todavía registro/admisión por el carril legacy de composiciones. Altas/perfiles/recibos propios se
  conectarán en T007–T009. Editar/importar autoridad legacy o una base con registro previo queda bloqueado hasta
  T011; no se adopta silenciosamente. La UI del asistente y ajustes se entrega en T006.
- Sin modelos/migraciones nuevos, instalaciones/servicios reales, agentes/proveedores/smokes, configuración
  global del equipo ni acciones remotas. Pruebas TestClient y herramientas falsas; no uso real nuevo.
  Commit local en inglés solicitado. Candidatos/artefactos y snapshots P001–P012/D214 intactos.

## D223 — P013-T006: asistente y editor global con confirmaciones exactas

Estado: implementada y verificada con UI/HTTP sintéticos el 2026-10-26; QA visual integrada pendiente T012. Fase: P013.
[Entrega](phase/P013-T006_ASISTENTE_UI.md), [flujo](flows/configuration-setup.md).
Concreta D216/D217/D222 sin anticipar importación T011 ni perfiles/asistencia T007–T010.

- `/setup` y `/settings/configuration` comparten editor determinista en/es. Resolver consulta antes de
  montar editor/workspace; modo global bloqueado conduce al asistente, preferencias conservadas. Supervisor
  solo publica el modo adicional; TOML/formulario/entornos completos quedan en el editor autenticado.
- Formulario mínimo sin stack ni TOML manual. Detección sugiere rutas/cuenta por PATH explícito y se aplica
  por acción separada; preflight version/help solo al comprobar. Modelo/esfuerzo del revisor explícitos;
  modelos del ejecutor se seleccionan por proyecto. Almacenamiento fijado al arrancar, sin traslado en UI.
- Conversión formulario/TOML por parser servidor en `/configuration/form`, sin dependencias TOML de navegador,
  procesos, guardado ni activación. Campos avanzados conservados; parser/guardias finales T004/T005 intactos.
  Diff/TOML/hash revisados antes de guardar; activación de la guardada validada exige otro preview/confirmación.
- Borrador con base CAS y sobre idempotente en almacenamiento de sesión de la pestaña. Sondeo/conflicto
  no reemplaza candidato ni actualiza base; adoptar base actual es explícito y exige nueva preview. Recarga
  no reenvía confirmaciones: usuario revisa/reintenta exactamente el mismo contenido/clave tras perder respuesta.
- Activa/guardada/pendiente y reinicio visibles; no endpoint de reinicio. Cancelación fija id/versión vistos;
  recuperación inspecciona hashes y exige declarar escritores detenidos. Ningún timeout acredita esa parada.
  Legacy informa que requiere importación explícita T011; originales y contratos 1–8 conservados.
- Sin esquema/migraciones nuevos. Pruebas de componentes/contrato con transporte falso y TestClient; sin
  servicio instalado, navegador, proveedores, smokes ni publicación. T012/T013 acreditarán lo visual/instalado.
