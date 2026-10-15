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
(migración documental de este repositorio) implementada el mismo día**; P008-T002 implementada (D089); P008-T003–T015
pendientes. Fase: P008.
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
