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
