# P013-T002 — Instalación automatizada y cachés configurables

Fecha: 2026-10-26. Base: `f24ade9`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local
en inglés. **Implementada; validación de orquestación sintética. Primer uso instalado pendiente T012/T013.**
[D219](../DECISIONS.md#d219--p013-t002-instalador-por-generaciones-y-paquete-autocontenido),
[contrato T001 §2](P013-T001_CONTRATO.md#2-instalación-y-actualización),
[flujo actualizado](../flows/configuration-setup.md).

## Resultado y motivo

Sin incongruencias pendientes de HITL tras contrastar T001/D216, D051/D150 y el código de distribución;
las elecciones reversibles de recibo/directorios concretan ese contrato.

`scripts/install` sustituye la composición manual de build/verificación/venv/pip. Acepta un clon o un paquete
local nuevo autocontenido, conserva locks/hashes y la comprobación instalada D051. Separa cachés, instalación,
datos y configuración, sin exigir `.local/`, entorno activado o cambios de configuración global del equipo.
No implementa arranque ni asistente: T003/T005 siguen pendientes, y la CLI actual requiere TOML completo.

Dos entradas excluyentes: `--clone /ruta/clon` (por defecto el checkout del script) y `--dist /ruta/paquete`.
Desde paquete se entregan también `scripts/install` y sus módulos; no requiere Node/npm, fuentes ni tests del
checkout. Los paquetes anteriores P011/P012 no tienen el material nuevo y se rechazan con diagnóstico;
se conservan intactos. No cambia la versión `0.1.0` ni se construye un candidato en esta tarea.

Ejemplos de uso futuro, **no ejecutados en esta sesión**:

```sh
scripts/install --help
scripts/install --clone /ruta/clon --python /ruta/python3.14 --uv /ruta/uv \
  --install-dir '/ruta/Harness Local/installation' --data-dir '/ruta/Harness Local/data' \
  --config-dir '/ruta/Harness Local/configuration' --cache-dir '/ruta/Harness Cache' --allow-network
/ruta/paquete/scripts/install --dist /ruta/paquete --python /ruta/python3.14 --offline
scripts/install --dist /ruta/paquete-nuevo --upgrade --writers-stopped
```

Los ejemplos segundo y tercero usan valores sugeridos para las rutas omitidas: deben elegirse explícitamente
si se continúa una instalación personalizada. `--upgrade --writers-stopped` declara servicio y escritores
parados; no descubre procesos ni certifica su muerte. No migra DB: D150 sigue como operación separada.

## Opciones, herramientas y caché

- `--install-dir`, `--data-dir`, `--config-dir`: rutas absolutas, privadas y del UID actual, sin componentes
  enlazados, fuera de checkouts/entrada y sin solaparse. Sugeridas bajo
  `~/Library/Application Support/Harness Local/{installation,data,configuration}`. Se crean faltantes con
  0700; existentes ajenas no se recorren ni reciben chmod. Nueva instalación exige datos/configuración vacíos.
- `--cache-dir`: raíz con `uv/` y `npm/`, sugerida `~/Library/Caches/Harness Local/`. Puede compartirse de
  forma explícita, separada de instalación/datos/configuración. No necesita `.local/` preexistente.
- `--python`: ejecutable local Python `>=3.14,<3.15`; el wrapper también lo usa para bootstrap. Sin opción,
  prefiere `python3.14` local o comprueba `python3`. El bootstrap de ayuda exige Python >=3.11; un Python
  anterior indica seleccionar el 3.14 local. `--uv`: ejecutable local uv 0.12.19. No descarga herramientas.
- Clon exige además Node v24.15.0/npm 11.12.1; paquete solo Python/uv y Git para verificación sintética.
  Requisitos se comprueban antes de crear instalación. Rutas con espacios se pasan en argv, sin shell/eval.
- `--offline` es el modo por defecto y no tiene fallback a red. `--allow-network` habilita únicamente la
  preparación fijada por locks/pylock; plan de rutas, efectos y red visible antes de escribir. Variables
  UV/PIP/PYTHON/HARNESS del operador se filtran en los procesos de instalación; uv sin configuración externa
  y npm sin configuración de usuario/global. No se automatizan credenciales ni configuración de clientes.
- Build usa `npm ci --ignore-scripts --no-audit --no-fund`, UI y uv_build fijados; exporta pylock con `--frozen`.
  Caché de build parametrizada; su uso independiente sin `--cache-dir` conserva `UV_CACHE_DIR` o
  `.local/uv-cache` y `.local/npm-cache`. No modifica locks. Dependencias instaladas por pylock con hashes,
  solo wheels y copia al venv; wheel propio sin resolver dependencias nuevas. Verificación instalada offline.

## Paquete autocontenido y paridad con D051

`build_distribution.py` conserva primero la verificación exacta contra fuentes, UI, licencias, metadatos,
versiones únicas, locks y componentes retirados de `check_checkout_artifacts`. Solo entonces entrega:

| Archivo/material | Función |
|---|---|
| Wheel, sdist, `pylock.toml` | Producto/UI/migraciones y dependencias fijadas con hashes. |
| `distribution-1.json` | Formato `distribution-1`, metadatos de proyecto y mapas de miembros/hash exactos de wheel y sdist. |
| `scripts/install`, `install.py`, `toolchain.py`, `distribution_artifacts.py` | Entrada y módulos de instalación sin dependencias de desarrollo. |
| `scripts/check_distribution.py`, `installed_config.py` | Verificación instalada y fixture sintético autocontenidos. |
| `SHA256SUMS` | Todos los archivos anteriores, incluidos scripts/manifiesto, por ruta relativa segura. |

`distribution_artifacts.py` no importa el checkout ni dependencias externas. Verifica conjunto exacto de
archivos, hashes, miembros y metadatos; rechaza duplicados, rutas ambiguas, enlaces/especiales de los archivos
comprimidos y dependencias sin pins/hashes/HTTPS. Lee archivos comprimidos sin extraerlos. Sin Python `-O`.
El manifiesto se crea después del contraste con fuentes; no reemplaza esa comparación. SHA256SUMS es control
de integridad respecto a la entrega, sin firma ni acreditación criptográfica de autoría del distribuidor.

`check_distribution.py` recibe Python/uv/caché, verifica el material y conserva el recorrido aislado de D051:
UI/assets/API, sesión, migración D150 sintética, definición D088, tarea/commit/reinicio, errores y consulta de
backup, con agentes falsos y directorios propios. Copia el fixture del paquete; no necesita checkout, Node,
TOML, bases o proveedores del operador. T002 **no ejecutó ese recorrido**, solo conserva su código y prueba
su independencia de importación/orquestación; su ejecución corresponde a T012/T013 con autorización propia.

## Generaciones, replay y actualización

| Ruta bajo `--install-dir` | Contrato |
|---|---|
| `.install.lock` | Exclusión no bloqueante entre instaladores; archivo privado, sin borrar un lock de otro proceso. |
| `generations/gen-<id>/venv/` | Venv creado directamente en ruta definitiva; no se mueve y conserva shebangs absolutos. |
| `generations/gen-<id>/distribution/` | Paquete construido/copias verificadas; nunca se mezclan dos generaciones. |
| `generations/gen-<id>/tmp/` | Temporal privado de construcción/verificación; no reutiliza áreas del operador. |
| `generations/gen-<id>/installation.json` | Intención/recibo privado `installation-1`, PREPARING → READY o FAILED. |
| `current.json` | Referencia `installation-1` con generación y hash del recibo READY, publicada por reemplazo atómico. |

Recibo: petición normalizada (origen/tipo/hash de fuentes o SHA256SUMS, destinos, Python/uv y hashes de sus
binarios), modo de red, referencia anterior, checks terminados, versión, hash de distribución/locks y mapa del
venv (bytes/modos y destinos de enlaces; excluye bytecode derivado). Archivos nuevos 0600. Se sincronizan
archivos/directorios de generación y recibo antes de publicar/sincronizar referencia. No hay tablas SQLite nuevas.

Repetición idéntica verifica referencia/recibo, distribución y venv, y devuelve el resultado sin reinstalar;
puede pasar de preparación con red a repetición offline. Otra entrada/contenido requiere `--upgrade` y parada
declarada; conserva rutas/datos/configuración y generaciones previas. Las fuentes se comprueban también tras
build y la copia del paquete debe conservar identidad. Deriva de venv/recibo/paquete bloquea, sin repararla.

Fallo de herramienta, caché incompleta, verificación o interrupción deja diagnóstico/bytes y referencia
anterior intacta. Caída abrupta puede dejar PREPARING; sin referencia no es instalación lista. Destino ocupado
sin recibo compatible se rechaza: inspeccionar/conservar o elegir destino nuevo, sin borrado/reintento automático.
La publicación final tiene recibo READY duradero: una pérdida de respuesta se concilia repitiendo. No hay
rollback automático de binarios/datos, adopción de DB ajena ni migración/restauración en el instalador.

## Validación y límites

- **119 pytest correctos** en los módulos de instalación, diagnósticos API, desarrollo, launcher, migración
  instalada y documentos; tras la revisión final, **31 pruebas del instalador correctas** (122 pruebas distintas
  entre ambas pasadas). Incluyen **31 pruebas nuevas** de herramientas falsas/archivos sintéticos: clon y
  paquete, rutas con espacios, caché elegida, offline/red explícita, requisitos/destinos inválidos, replay,
  deriva, exclusión, interrupción y actualización fallida/exitosa con preservación de datos/generaciones.
  Verificación de alteraciones, miembros duplicados/enlaces/archivos especiales inseguros, alias de mayúsculas
  en macOS, pins y ayuda importable sin checkout. Warning esperado del ZIP duplicado y deprecación previa
  de FastAPI/TestClient, sin fallos.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**.
- Ayudas del wrapper/build/verificador, compilación Python y `sh -n scripts/install` correctos. Parsers:
  13 fases, ocho criterios P013, quince tareas únicas y 219 decisiones consecutivas con estado.
  **737 enlaces locales/anchors en nueve documentos**, fences y presupuestos correctos (STATE 16.250 bytes,
  NEXT_STEPS 21.213); cuerpos D001–D218 y base acumulada STATE conservados.
- Mermaid: **tres flowcharts y una secuencia**, cero fallos, con el checker archivado P011-T013; solo parseo,
  sin acreditar renderizado/QA visual. `git diff --check` correcto y diff revisado antes del commit.

No instala paquetes, descarga, levanta servicios, ejecuta verificador/smoke operativo, llama proveedores/agentes
reales ni opera el harness sobre este checkout. Tests de orquestación no acreditan primer uso instalado, red
real ni calidad de modelos. Sin suite pytest completa, Node/tipos/build, Alembic operativo, navegador o CI
remota: no cambian producto runtime, esquema, API/OpenAPI, UI ni dependencias. No modifica configuración
global del equipo, snapshots/historiales ni árboles/paquetes D214/P011/P012. Un commit local en inglés, sin
push/tag/publicación. Siguiente: **P013-T003**.
