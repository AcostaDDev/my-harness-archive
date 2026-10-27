# P013-T012 — Primer uso integrado, QA y documentación de usuario

2026-10-26. Base `4e420738fc8b2e97b89651089a63761ad8ffa726`, checkout limpio al empezar.
**Completada con evidencia instalada sintética y QA Chrome; candidato final pendiente T013.**
[D229](../DECISIONS.md#d229--p013-t012-primer-uso-instalado-y-documentación-pública),
[matriz](P013_MATRIZ_ACEPTACION.md), [resultados saneados](P013-T012_RESULTS.json),
[guion reproducible](P013-T012_REHEARSAL.py).

## Alcance, autorización y resultado

El usuario encargó la siguiente tarea, commit en inglés y HITL para ambigüedades no resolubles, añadiendo:
«Tienes autorización para cualquier duda que implique la misma». Se aplicó a instalación/descargas fijadas,
servicios locales, ejecutables falsos y QA en un área temporal propia fuera del repositorio. Se comunicó el
alcance antes de operar. No se encontraron contradicciones de diseño que requirieran cambiar D216–D228.

La prueba usa una copia Git local sin archivos operativos/cachés, a partir de la base citada, con los parches
acotados de scripts indicados abajo. El harness corre solo desde wheels instalados sobre proyectos sintéticos;
nunca sobre este checkout. Python 3.14.4, uv 0.12.19 de Homebrew, Node 24.15.0/npm 11.12.1 para construir;
macOS ARM64 y Chrome del equipo. Sin CLI/proveedores reales, login de cuentas, credenciales, cambios en
configuración global de Git/CLI/uv/npm/shell, bases o fixtures P012 ni acciones remotas.

## Instalación y repetición

Área nueva con rutas `clean clone`, `Harness Local verified/{installation,data,configuration}`, `Chosen Cache`
y `Synthetic projects`; todos los datos locales fuera del checkout. Caché inicialmente vacía, red explícita
solo para dependencias fijadas por los locks. No se instaló Python/uv/Node globalmente. El primer recorrido
identificó fallos reales; se conservaron generaciones fallidas y se eligieron destinos nuevos para continuar.

Después de corregir scripts, la instalación desde la copia del clon se completó offline usando la caché
preparada: build/UI, miembros/metadatos/checksums, venv y verificador aislado del wheel, luego recibo READY y
current.json. El verificador ejecutó su recorrido sintético D051 de definición/tarea/commit/reinicio/migración/
backup/consulta sin Node ni checkout en runtime. El instalador no inicializó ni migró la base del operador.

Tras el hallazgo visual se construyó **otro paquete de ensayo**, con la corrección UI y scripts actuales,
y se actualizó la instalación desde `--dist --offline --upgrade --writers-stopped`, con PATH `/usr/bin:/bin`
y Python/uv por ruta absoluta: sin Node/npm. Conservó generación/datos/configuración previos. Repetición
idéntica desde paquete verificó/reutilizó READY sin reinstalar. Entrada desde paquete con caché vacía falló
con diagnóstico de caché incompleta y **sin current.json**; generación FAILED conservada.

El [JSON](P013-T012_RESULTS.json) registra hashes de ese segundo paquete: wheel `a4c483af…171bfb`, sdist
`746cb6d1…68080e`, pylock `20a327c3…f2cf9` y SHA256SUMS `54e39854…3f258`. Son identidades del ensayo, anteriores
a los últimos cambios documentales. No son el candidato exacto de T013 ni sustituyen los hashes D214/P011/P012.

## Correcciones acotadas

| Hallazgo observado | Corrección y comprobación |
|---|---|
| Pin uv rechazaba sufijo Homebrew al pasar ruta absoluta | `toolchain.py` normaliza según nombre lógico uv, conservando el pin exacto. Regresión con nombre/ruta y versión válida/inválida. |
| npm rechazaba cargar /dev/null como user y global config | `install.py` usa /dev/null para usuario y archivo vacío privado de generación para global; filtra overrides npm en ambas capitalizaciones. Prueba con npm real sin red y configuración sintética ajena intacta. |
| uv build generaba .gitignore adicional y rompía el conjunto exacto | `build_distribution.py` pasa --no-create-gitignore. Verificador completo de miembros/checksums posterior correcto. |
| Verificador esperaba salida ante configuración inválida | `check_distribution.py` verifica sesión/asistente INVALID, sin autoridad, supervisor deshabilitado, admisión 409 y cero nuevas invocaciones. Conserva diagnóstico de esquema viejo. |
| Reinicio inmediato rechazaba puerto sin listener por TIME_WAIT | `start.py` usa SO_REUSEADDR en precheck; regresión abre/cierra una conexión real y conserva rechazo con listener. Bind final de uvicorn sigue autoritativo. Mensaje ya anuncia asistente entregado. |
| Alternar creación/registro duplicaba selector de padre | Dos hermanos React compartían la clave de revisión. `Registry.tsx` distingue root-/new-. Regresión roja antes/verde después; instrumentación de JSX detecta claves explícitas duplicadas. Navegador actualizado alterna tres veces y mantiene un selector. |
| Probe sintético esperaba esquema de lector en preparación | `cli_process_probe.py` lee esquema solo en rol lector; preparación escritora sin ese bloque funciona. Ningún cambio en adaptadores/productores/permisos reales. |

Las rutas de producto ampliadas se acotaron a esos scripts y dos claves de Registry; no hay cambio de diseño,
modelo/migración/API/OpenAPI/tipos, TOML o dependencias. La documentación vigente/pública conserva paridad de flujo.

## Altas y tareas

`P013-T012_REHEARSAL.py` es stdlib y copia solo el probe falso al área de ensayo. El servicio es el paquete
instalado con supervisor; todas las peticiones usan sesión local, CSRF y previews/confirmaciones exactas.

1. Primer `scripts/start` crea DB ausente sin TOML y sirve `/setup`. Desde **formulario real en Chrome**, se
   completan identidad Git y clientes Claude falsos en PATH explícito, usuario/home privados, modelo/esfuerzo
   del revisor, raíces y supervisor. Preflight version/help sin inferencia; diff y confirmación de guardado,
   preview/confirmación separada de activación. Reiniciar carga la misma global activa.
2. Creación sin composición bajo padre confirmado e incorporación B sobre HEAD Git sintético. B parte de
   `original.txt`; el inventario no ejecuta código. Conversación falsa devuelve documentos/arquitectura Go,
   propuesta con evidencia por validación/prefijo y plan técnico sin dependencias/red.
3. Se aplican borradores, adopta perfil y confirma commit documental/P001; aplicación guarda project-config-1
   privado con ejecutable Go falso y entorno .prepare. Intentar tarea antes de activar devuelve 409.
4. Preparación confirmada hace escribir solo app/main.go, go.mod y .gitignore al ejecutor falso; comando Go
   falso produce JUnit (no es un compilador). Se comprueban ámbito/archivos, commit técnico y recibo, después
   activación independiente. Nueva tarea cambia app/main.go, valida, recibe ACCEPT falso y confirma commit.
5. `created-final` y `existing-final` terminan **COMMITTED**, con IDs y preparaciones en el JSON. El original B
   sigue idéntico. El nuevo paquete carga esos proyectos tras actualizar/reiniciar sin repetir trabajo.

El recorrido de proyectos es **HTTP protegido**, no una automatización de todos sus clics. Los formularios y
editores se revisan separadamente en Chrome. El revisor/ejecutor falsos y Go falso ejercitan orquestación,
contratos/recibos/validación/JUnit; no acreditan modelos ni compilación/instalación real de Go.

Los intentos previos no se borraron: preparación FAILED por el probe incompleto, tarea STOPPED por prefijo
no autorizado, propuesta STOPPED por faltar evidencia del prefijo y preview B 409 por diagrama ausente.
Se corrigieron los fixtures en nuevas altas, conservando resultados/operaciones. Inventario final: 4 runs
COMMITTED, 10 COMPLETED, 2 STOPPED; preparaciones 4 COMPLETED/1 FAILED; **cero jobs pendientes/activos**.
No se presenta cada ejecución parcial como un recorrido completo adicional.

## Backup y consulta

Con servicio/escritores propios parados, CLI instalada crea/verifica backup formato 2 con roots explícitos de
datos/configuración y restaura en destino nuevo. Se conservan originales renombrando configuración, herramientas
y checkouts a ubicaciones no disponibles para el servicio; no se borran ni se reparan intenciones históricas.

`scripts/start --database …/data/restored/state.sqlite3` abre consulta, sin TOML original/agentes. HTTP lee los
dos runs COMMITTED y los TOML de global/proyectos por revisión desde bundle; check-clients rechaza con 409.
UI muestra Archivo de consulta, run B, commit, validación/JUnit/diff y métricas, sin controles operativos.
Los fallos históricos siguen en el bundle. Consulta no acredita muerte de escritores ni autoriza reactivar la DB.
Al acabar se detienen todos los servicios propios y se comprueba que el puerto ya no escucha.

## QA visual

Once capturas JPEG originales en [P013-T012_QA](P013-T012_QA/es-light-desktop-restored-run.jpg). Solo contienen
datos sintéticos/rutas de ensayo; nunca claves de sesión ni credenciales. Escenarios:

| Vista | Idioma/tema/ancho | Evidencia |
|---|---|---|
| Confirmación global | en/oscuro/1470 | [activación](P013-T012_QA/en-dark-global-activation.jpg) |
| Global activa/asistencia | en/claro/1280 y 320; es/claro/390 | [escritorio](P013-T012_QA/en-light-desktop-global.jpg), [320](P013-T012_QA/en-light-320-global.jpg), [es móvil](P013-T012_QA/es-light-mobile-global.jpg) |
| Perfil propio activo | es/oscuro/1280 y 390 | [escritorio](P013-T012_QA/es-dark-desktop-profile.jpg), [móvil](P013-T012_QA/es-dark-mobile-profile.jpg) |
| Creación e incorporación | es/oscuro/1280; en/claro/390 | [creación](P013-T012_QA/es-dark-desktop-creation.jpg), [alternancia corregida](P013-T012_QA/es-dark-desktop-onboarding-fixed.jpg), [creación móvil](P013-T012_QA/en-light-mobile-creation-fixed.jpg), [registro móvil](P013-T012_QA/en-light-mobile-onboarding-fixed.jpg) |
| Consulta restaurada | es/claro/1470 | [run COMMITTED](P013-T012_QA/es-light-desktop-restored-run.jpg) |

Formulario/TOML global convertido en ambos sentidos, descarte/carga de versión por confirmación explícita,
borrador conservado tras reinicio, contexto de edición del perfil activo y editor TOML comprobados. Se usaron
Tab (autor → correo, id → carpeta) y Enter para cambiar de entrada; foco visible y orden coherente en esos
puntos. No overflow global observado en los anchos móviles comprobados; texto/hash se ajustan. Tema y preferencias
se cambiaron solo en el navegador/DB de ensayo; viewport temporal restaurado.

Chrome con extensiones del operador: se observaron errores de autofill de Bitwarden ajenos a la app y navegación
iniciada por la extensión rechazada por sec-fetch-site; se usó barra de direcciones nativa para entrada directa,
sin relajar seguridad ni cambiar extensiones. No se probaron otros navegadores/lectores de pantalla, auditoría
completa de teclado/contraste, todas las combinaciones ni dispositivos físicos. Capturas son muestras, no prueba
de accesibilidad completa. La clave desaparece al parar; ninguna sesión queda abierta en un servicio vivo.

## Documentación, checks y límites

README en/es separa instalar/usar de desarrollo; explica uv/venv/cachés, opciones, clon/paquete, red/offline,
setup/perfiles, edición/importación, actualización y backup. `docs/public/` incorpora contrato vigente en inglés,
D216–D228, esquema 0027/54 tablas y flujo; sigue siendo autocontenida sin informes privados. Los diagramas
anteriores de composición/recetas se identifican como carril legacy y enlazan los nuevos gates v9.

- **2048 pytest y 29 subtests correctos**, dos opt-in omitidas, cuatro workers (261,61 s). Incluye nuevas
  regresiones de uv/npm/puerto y probe actualizado. Avisos conocidos FastAPI/TestClient y ZIP negativo duplicado.
- **155 Node y 8 unittest correctos**. Regresión de Registry falla antes por claves duplicadas y pasa después;
  Node completo repetido tras la corrección. Build/tipos correctos; aviso conocido de chunks grandes.
- Dos builds/instalaciones verificadas y actualización/replay desde paquete sin Node; fallo de caché incompleta
  controlado. Verificador instalado completo, backup y consulta HTTP/Chrome correctos. Sin repetir smoke de
  proveedores ni usar el harness sobre este checkout.
- [Checker vigente](P013-T012_CHECK_DOCS.py) y [público](P013-T012_CHECK_PUBLIC.py): parsers/enlaces/presupuestos,
  decisiones congeladas, referencias de código y ausencia de referencias privadas: 13 fases, 15 tareas,
  229 decisiones, 944 enlaces/anclas vigentes; 32 documentos públicos, 271 enlaces, 93 decisiones públicas.
  Otras 49 pruebas documentales/paridad correctas. Mermaid: cinco flowcharts, dos secuencias y trece ER,
  cero fallos con el checker citado en T001 (solo parseo/stub DOMPurify, sin acreditar renderizado). Diff revisado y `git diff --check` correcto. No hay cambios de esquema: no se repite Alembic check
  operativo; la suite valida migraciones sobre SQLite temporal y el verificador instalado ejercita migración.

Artefactos operativos/logs completos permanecen en el área temporal local indicada por `.local/p013-t012-area`
(ignorada por Git); solo se versionan guion, resultados saneados, capturas, matriz y checks. Se conservan candidatos,
paquetes/snapshots P011/P012/D214 por bytes. No tag, push, CI remota ni publicación. T013 verificará el árbol/paquete
finales con sus hashes propios; esta tarea no los da por entregados.
