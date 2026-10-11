# Decisiones

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

Estado: seleccionado y resuelto el 2026-10-11; instalación pendiente de H0.3.

Usar CPython 3.14.4 estándar, uv 0.12.19, Node 24.15.0 y npm 11.12.1 en el
Mac actual. Pins directos y fuentes en
[H0.2_COMPATIBILITY.md](discovery/H0.2_COMPATIBILITY.md); restricciones y
resolución conjunta en [snapshot](discovery/h0.2-version-metadata.json).
TypeScript queda en 5.9.3 porque openapi-typescript 7.13.0 requiere `^5.x`.
Codex 0.161.0 y Claude Code 2.1.295 son el baseline observado; versiones nuevas
exigirán comprobar capacidades, no trasladar flags legacy por suposición.

La resolución temporal sin instalación comprueba disponibilidad y restricciones,
no ejecución del stack. Crear locks y verificar instalación/arranque/build al
introducir el esqueleto. Los parsers H0.2 siguen usando biblioteca estándar.

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
