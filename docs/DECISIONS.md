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

Estado: seleccionado y resuelto el 2026-10-11; instalación del subconjunto usado
comprobada en H0.3 (D011).

Usar CPython 3.14.4 estándar, uv 0.12.19, Node 24.15.0 y npm 11.12.1 en el
Mac actual. Pins directos y fuentes en
[H0.2_COMPATIBILITY.md](discovery/H0.2_COMPATIBILITY.md); restricciones y
resolución conjunta en [snapshot](discovery/h0.2-version-metadata.json).
TypeScript queda en 5.9.3 porque openapi-typescript 7.13.0 requiere `^5.x`.
Codex 0.161.0 y Claude Code 2.1.295 son el baseline observado; versiones nuevas
exigirán comprobar capacidades, no trasladar flags legacy por suposición.

La resolución temporal sin instalación de H0.2 comprueba disponibilidad y
restricciones, no ejecución del stack. H0.3 creó locks y verificó instalación,
arranque y build al introducir el esqueleto; [evidencias](discovery/H0.3_SKELETON.md).
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
no preparados. [Alcance y evidencia](discovery/H0.3_SKELETON.md).

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
gestionado. [Entrega y verificaciones](discovery/H1.1_IMPORT.md).

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
[Entrega y verificaciones](discovery/H1.2_NAVIGATION.md).

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
[H1.3_OBSERVATION.md](discovery/H1.3_OBSERVATION.md).

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
real. [Entrega, trazabilidad y límites](discovery/H2.1_ENGINE.md).

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
[Entrega y pruebas](discovery/H2.2_PERSISTENCE.md).

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
Ver [entrega, fuentes y límites](discovery/H2.3_CLI.md).

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
Resultado, procedencia y límites en [H2.3_SMOKE.md](discovery/H2.3_SMOKE.md).
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
ejecutarla dentro de la corrección offline. [Entrega](discovery/H2.3_CONFIG_FIX.md).

## D020 — Nuevo smoke autorizado y parada ante configuración MCP de Claude

Estado: verificación real ejecutada el 2026-10-12; fallo conservado sin corregir
ni relanzar. [Resultado y evidencias](discovery/H2.3_SMOKE_RETRY.md).

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
dentro de esta entrega. [Contrato, fuentes y límites](discovery/H2.3_MCP_FIX.md).

## D022 — Smoke cli-3 autorizado y fallo de autenticación Claude

Estado: verificación real ejecutada el 2026-10-12; rama de error concluida,
sin login, corrección ni relanzamiento. [Informe](discovery/H2.3_SMOKE_CLI3.md).

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
[Informe y reproducción](discovery/H2.3_AUTH_DIAGNOSIS.md).

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
[Informe y alcance](discovery/H2.3_ENV_FIX.md).

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
[Propuesta posterior separada](discovery/H2.3_ENV_SMOKE_PROPOSAL.md) pendiente
de consentimiento específico; no ejecutar por la corrección o su commit.
H2.4 no iniciado.

## D025 — Smoke autorizado con USER: tres transportes completos

Estado: verificación real completada el 2026-10-12.
[Resultado y evidencias](discovery/H2.3_ENV_SMOKE.md).

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
[Entrega, protocolo y límites](discovery/H2.4_GIT.md).

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
[Entrega, protocolo y límites](discovery/H2.5_MIGRATION.md).

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
[Entrega, contratos y límites](discovery/H2_EXIT_API.md).

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
[Entrega y reproducción](discovery/H2_EXIT_UI.md).

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
[Entrega, procedencia y límites](discovery/H3.1_PROMPTS.md).

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
[Entrega y límites](discovery/H3.2_PERMISSIONS.md).

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
[Entrega y límites](discovery/H3.3_PHASES.md).

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
[Entrega y límites](discovery/H3.4_PHASE_ADJUSTMENTS.md).

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
[Entrega y límites](discovery/H4.1_CHAT.md).

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
[Entrega y límites](discovery/STATE_EXPORT.md).

El cierre sigue siendo D032: CLOSED + tag, sin invocar la exportación. Exportar es
una acción propia, también disponible para la última fase cerrada o abandonada,
hasta crear otra fase. Así el tag conserva el HEAD evaluado; exportar después no
lo mueve. Una exportación previa a cerrar vuelve obsoleto el vínculo READY por
sus documentos/HEAD: se exige un check nuevo. La evaluación histórica se conserva.

STATE y NEXT_STEPS usan las rutas del contexto del servidor, distintas y presentes
en la base documental adoptada. Los documentos regulares UTF-8 se acotan a 512 KiB.
Se añade o reemplaza únicamente el bloque entre
`<!-- harness-local:managed-state:start -->` y
`<!-- harness-local:managed-state:end -->`. La prosa exterior y sus terminaciones
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
[Entrega, uso y límites](discovery/H4.2_BOOTSTRAP.md).

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
[Entrega, comandos y límites](discovery/H4.3_TYPESCRIPT_PROFILE.md).

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
[Entrega y límites](discovery/H5.1_JUNIT.md).

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
[Procedimiento y límites](discovery/H5.2_BACKUP.md).

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
[Procedimiento y límites](discovery/H5.3_RETENTION.md).

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
[Uso, verificaciones y límites](discovery/H5.4_DIAGNOSTICS.md).

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
[Construcción, instalación y límites](discovery/H5.5_DISTRIBUTION.md).

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
[Operación, amenazas, pruebas y límites](discovery/H5.6_SESSION.md).

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
[Recorridos, matriz de cobertura y límites](discovery/H5.7_E2E.md).

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
pendiente de elección del usuario en esa revisión. [Dictamen](discovery/H5_CLOSURE_REVIEW.md).
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
[Entrega y límites](discovery/COMMAND_RUNNER.md), según el
[alcance escrito antes de implementar](discovery/COMMAND_RUNNER_SCOPE.md).
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
[Dictamen](discovery/COMMAND_RUNNER_REVIEW.md) sobre D047, pedido por el usuario
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
[Entrega y operación](discovery/LOCAL_CONFIG.md), según el
[alcance escrito antes de implementar](discovery/LOCAL_CONFIG_SCOPE.md).
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
con autorización del usuario el mismo día** y completa ([resultado](discovery/FIRST_USE_RUN.md),
D051). Consentimiento agotado. [Propuesta](discovery/FIRST_USE_PROPOSAL.md). Concreta D033.8.

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
[Resultado](discovery/FIRST_USE_RUN.md).

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
el mismo día como `cli-5` / `local-config-2` ([entrega](discovery/AGENT_ROLES.md)).
[Alcance](discovery/AGENT_ROLES_SCOPE.md). Sustituye la asignación fija
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
[Entrega](discovery/DEV_COMMAND.md). Decisiones del usuario: modo desarrollo
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

Estado: decidido por el usuario el 2026-10-13; **no implementado**. Backlog,
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
([resultado](discovery/PROVIDER_MATRIX_RUN.md)). La combinación 1 falló en el
planificador por un contrato ambiguo de `validation_commands`; el usuario
decidió parar y corregir, así que 2–4 no se lanzaron. Una sola invocación de
proveedor. Consentimiento agotado. [Propuesta](discovery/PROVIDER_MATRIX_PROPOSAL.md).

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
[Entrega](discovery/CONTRACT_SHAPES.md). Origen: el smoke D055 se detuvo porque
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
mismo día y cerrada** ([resultado](discovery/PROVIDER_MATRIX_RERUN.md)):

- 1 (Codex→Claude) `COMMITTED`.
- 2 (Codex→Codex) `REVISION_LIMIT`, porque el escritor Codex no editó.
- 3 (Claude→Claude) `STOPPED` en `planner`: el `--json-schema` sin tipos hizo
  que Claude serializara listas como texto.
- 4 no lanzada por decisión del usuario.

Siete invocaciones de proveedor. Consentimiento agotado.
[Propuesta](discovery/PROVIDER_MATRIX_RERUN_PROPOSAL.md).

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
[Entrega](discovery/TYPED_JSON_SCHEMA.md). Origen: en la combinación 3 de D057,
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
[Evidencia, medidas y límites](discovery/CODEX_WRITER_ROOTS.md). Petición del
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
[Resultado](discovery/PROVIDER_MATRIX_CLI7_RUN.md).
[Propuesta y órdenes](discovery/PROVIDER_MATRIX_CLI7_PROPOSAL.md),
[manifiesto de paquete/configuración y ensayo sintético](discovery/PROVIDER_MATRIX_CLI7_PREPARATION.json).
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
[Resultado y límites](discovery/PROVIDER_MATRIX_CLI7_RUN.md),
[manifiesto](discovery/PROVIDER_MATRIX_CLI7_RESULT.json). El usuario autorizó
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
transporte implementada**. [Evidencia y opciones](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
[manifiesto](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.json). Petición del
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
**sin implementación en producto**. [Alcance, alternativas y criterios](discovery/CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
[evidencia](discovery/CODEX_PROCESS_CONTAINMENT_EVIDENCE.json).

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
integración tal como está**, sin cambios de producto. [Dictamen y reproducción](discovery/CODEX_CONTAINMENT_QUALIFICATION.md),
[evidencia](discovery/CODEX_CONTAINMENT_QUALIFICATION.json).

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
integración en producto**. [Resultados y criterios](discovery/CODEX_CONTAINMENT_REVISION.md),
[evidencia](discovery/CODEX_CONTAINMENT_REVISION.json) y
[sonda sintética](discovery/CODEX_CONTAINMENT_REVISION.py).
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
[Entrega, inventario y límites](discovery/AGENT_PERSISTENCE.md),
[evidencia](discovery/AGENT_PERSISTENCE.json).

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
