# P012-T012 — Vista UI de runs en copias de consulta

Fecha: **2026-10-25**. **Estado: implementada y verificada offline; sin operación privada.**
Base de desarrollo: **`472ad89`**, checkout inicialmente limpio. Contrato: [plan D201 conservado](P012-T012_PLAN_VISTA_CONSULTA.md).
Decisión: [D202](../DECISIONS.md#d202--p012-t012-vista-ui-de-consulta-implementada).
T003 permanece parcial: su evidencia HTTP anterior no se presenta como verificación de esta UI.

## 1. Resultado y motivo

D040 conservaba evidencia consultable por API, pero la UI exigía un proyecto compuesto incluso para un run
restaurado. Ahora `SupervisorRead.read_only_archive` procede de la marca persistente D040. La UI espera esa
señal antes de montar páginas operativas; una instalación ordinaria sin agentes o con supervisor=false no
se convierte en copia. OpenAPI y tipos regenerados; sin migración, codec, formato de bundle o cambio de guardias.

La copia ofrece entrada por id en inicio y `/runs/:id` directa/recargable. Identifica su carácter de consulta,
conserva raíz/fase/tarea como texto histórico y presenta estado/commit, ciclos/diff con hash, validaciones/JUnit,
jobs/intentos/eventos y métricas paginadas por `run_id`. No necesita registro ni checkout. Las rutas operativas
directas muestran mensaje de consulta y vuelta al inicio. La navegación ofrece archivo y estadísticas;
los enlaces de run apuntan a `/runs/:id`.

`RunEvidence` comparte la presentación con `RunPage`; las decisiones, permisos y recuperación solo se suministran
desde el modo operativo. `AttemptMetrics` comparte la tabla y los formatos/procedencia de Stats, con ámbito por
run. Null sigue distinto de cero, modelo solicitado distinto de reportado; una lectura fallida muestra error,
no un éxito vacío. Los detalles pesados se abren bajo demanda: diff paginado y ligado a hash, casos/original
JUnit y estado de streams. Los eventos navegan con los cursores exactos del servidor, incluso con saltos.

En copias no se monta `ProjectWorkspace`, no se leen solicitudes guardadas ni se ofrecen permisos, recuperación,
ejecución, commit, chat o configuración aunque el payload anuncie acciones. Los estados históricos activos no
producen polling de ejecución: lectura inicial, páginas y recarga explícita. Stats tampoco sondea ni sugiere
backfill en copia. La comprobación de sesión/autenticación mantiene su contrato independiente. Sin marca se
conservan redirección canónica, estado sin proyecto, controles operativos y CAS; la paginación compartida de
ciclos retrocede diez posiciones, igual que el tamaño de página que ya sirve la API.

## 2. Verificación

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_backup.py tests/product/test_managed_api.py tests/product/test_run_projection.py tests/product/test_metrics_projection.py tests/product/test_metrics.py
node --test frontend/tests/*.test.mjs
npm --prefix frontend run check
npm --prefix frontend run build
```

- **102 tests Python dirigidos correctos**, incluidos tres casos nuevos. Backup y restauración sintéticos con
  run COMMITTED y otro QUEUED: respuestas iguales al origen, diff/JUnit/métricas incluidos, después de borrar
  exclusivamente el checkout temporal del test. Señal true en ambas copias y false en servicio ordinario con
  puertos configurados y supervisor=false. Configuración ambiental inválida ignorada, cero invocaciones,
  `query_only=1`, mutaciones 409, todas las filas conservadas. Probe SQL/codec confirma cero selección o
  decodificación de `history_json` en las lecturas HTTP después de verificar el bundle al arrancar.
- **16 regresiones React/router**, dentro de **119 tests Node correctos**. En/es, estados COMMITTED/QUEUED/ACTIVE/
  RECOVERY_REQUIRED/REVISION_LIMIT, datos ausentes e incompletos, acciones anunciadas y solicitud pendiente
  sintética guardada. Lecturas GET por id, diff con hash, casos/original JUnit, logs purgados, consumo por run,
  páginas de métricas y cursores de eventos con salto 0→101→0. Sin acceso a pendientes, escrituras o timers de
  ejecución. Entrada codificada, rutas directas bloqueadas, 404 y modo aún sin resolver. Modo normal conserva
  redirección con proyecto, estado sin proyecto y controles de decisiones/permisos/recuperación/sondeo.
- React/ReactDOM reales para el render; el helper TSX existente admite un host de hooks solo en esos tests.
  Conduce estado, efectos y peticiones sintéticas de forma determinista sin DOM, servicio o dependencias nuevas.
  No acredita comportamiento visual ni ciclo de vida real del navegador; esa comprobación queda para T003.
- **TypeScript y build Vite correctos**, con aviso existente de chunks mayores de 500 kB. El build frontend es
  un check local: no es un wheel ni instalación operativa. Aviso de deprecación Starlette/httpx en pytest.

No se ejecutan suites Python completas/unittest o Alembic: el cambio backend es el campo de lectura, cubierto
por runtime/API/backup/proyecciones/métricas; no hay modelos SQL ni migraciones. No se repiten validaciones de
fixtures reales, smokes, CLI/proveedores, wheel/verificador de distribución o QA de navegador. Sin servicios
operativos o procesos de modelos. Las pruebas de producto usan Git/SQLite temporales y herramientas falsas.

## 3. Paridad, conservación e identidad de código

[Flujo nuevo](../flows/backup-consultation.md), referencia desde lectura de run, ARCHITECTURE §7 y SPECIFICATION
F06/F16 actualizados. STATE/NEXT_STEPS/ROADMAP y D202 reflejan la entrega. El diagrama SQL no cambia porque no
cambian modelos persistidos ni migraciones. README y baseline pública siguen pendientes de T005.

El [manifiesto de 24 archivos de código/API/tests](P012-T012_CODE.sha256) fija la corrección revisable.
SHA-256 del manifiesto: **`c89f85cc4b49b0045ab0bdb979e6a17f6862d10304da676bb8ac48c09f60784c`**.
El commit de entrega se resuelve sin ambigüedad con `git log -1 --format=%H -- docs/phase/P012-T012_CODE.sha256`;
antes de operar debe coincidir con el commit entregado al usuario y sus 24 hashes. Un cambio de producto exige
revisar la propuesta, no incorporarlo silenciosamente a la continuación.

D001–D201, plan D201, ambos informes T003, archivo histórico y baseline pública conservados por bytes frente a
472ad89. No se abre el área privada, SQLite, fixtures, TOML, distribuciones, diffs o evidencias reales. Los hashes
y recuentos de §4 proceden del informe T003 fechado; no se presentan como guardias repetidas hoy.

Checks documentales correctos: **12 fases, 7 criterios P012, 12 tareas y 202 decisiones**, **698 enlaces/anclas**
relativos válidos en los nueve Markdown de la entrega. Presupuestos STATE/base/NEXT_STEPS:
**17.212/24.576**, **9.171/12.288**, **33.693/49.152 bytes**. Manifiesto de código verificado, conservación
histórica contrastada por bytes, diff revisado y `git diff --check` correcto.

## 4. Propuesta de continuación T003 solo UI, sin autorizar

**Esta propuesta no concede permiso para construir/instalar/servir ni completa T003.** Tras revisar el commit
de entrega, pedir consentimiento nuevo para el guion siguiente, con **máximo una hora y cero llamadas Claude/
Codex**. No usa el saldo de T003; no repite chat, `/estado`, aceptación, backup o restauración anteriores. T004
no forma parte del tramo y conserva la guardia D199 del job QUEUED.

Área conservada: `AREA=$HOME/Documents/harness-validation/p012-20261024`.
Repositorio de build: `REPO=$HOME/Documents/projects/my_harness`.

| Ruta bajo AREA | Efecto propuesto |
|---|---|
| `dist-t012/`, `venv-t012/` | Destinos nuevos para build/verificación e instalación offline de la corrección |
| `restored/t003/` | Consulta de la restauración existente; sin configuración de agentes |
| `state/operator/t003-ui-t012-*` | Evidencia privada nueva de hashes/filas/QA/parada; sin sobrescribir la anterior |
| `tmp/t003-ui-t012-*` | Temporales nuevos; descarga JUnit si se necesita comprobar sus bytes |
| `command-home/`, `tmp/`, cachés existentes | Entorno de proceso explícito; sin cambios globales o descargas |

Antes de efectos: checkout limpio en el commit de esta entrega, manifiesto anterior intacto, destinos nuevos
sin enlaces/ocupantes, puerto **8025** libre y **8024** cerrado. Confirmar por lectura y hashes que la base
operativa sigue detenida y que bundle/restauración no han cambiado desde T003. No arrancar 8024 ni pasarle esta
base al supervisor. Esquema 0025, marca 0x483532 e integridad/FK de la copia correctos; **16.798 filas** finales,
**13 DONE/1 QUEUED/14 STOPPED/0 locks** conservados. Comparar todas las columnas mediante lecturas de consulta.
No usar `immutable=1` sobre WAL pendiente; ante WAL inesperado, proceso vivo, hash/recuento distinto o ruta
ocupada, parar y revisar por HITL sin reparar, retirar marca o crear destinos alternativos.

| Referencia fechada de T003 | SHA-256 esperado antes y después |
|---|---|
| Base operativa | `187614a9ea361e1f96a45f55240f55a20e4b3138dab2bdd47a1e3fe280675cfc` |
| Manifiesto backup | `7ff59485ae62c7371a580184cfd4b17071b67cf6f0d8f448e0b41f069362b7b5` |
| SQLite backup | `b35c4114734da72e25c12a57e01f0f350d6676608eac84c1b4a3d768072e7d15` |
| Manifiesto restauración | `f5152c80f0de9ae4da6728ac1cedacee10f0442e80c2ecb8d539d82ecd4651e7` |
| SQLite restauración | `1a1506ff90c2f451ef0bb467a8b520149265c8e516ca6e42088d256300d4b4b8` |

Después de consentimiento, con `umask 077`, ejecutar desde REPO los comandos offline siguientes. Mantener el
Python instalado `/opt/homebrew/bin/python3` (T011: 3.14.4); verificar su identidad conservada sin invocar CLI de
agentes. El verificador de distribución incluye pruebas sintéticas/CLI falsas y servicios efímeros propios;
no confundirlos con la consulta de la copia real. Si falta caché, parar sin red. No migrar ni inicializar nada.

```sh
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist-t012"
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist-t012"
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3 "$AREA/venv-t012"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip sync --offline --python "$AREA/venv-t012/bin/python" "$AREA/dist-t012/pylock.toml"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip install --offline --no-deps --python "$AREA/venv-t012/bin/python" "$AREA/dist-t012/harness_local-0.1.0-py3-none-any.whl"
```

Registrar SHA256SUMS, wheel/paquete/pylock e instalación y contrastar miembros exactos con fuentes del commit.
Los hashes de esos artefactos nuevos se calcularán al construirlos; no se inventan antes. Conservar todos los
dist/venv anteriores. Ningún `check-config --preflight`, CLI real, validador/formateador del fixture o modelo.

Arranque desde AREA, entorno explícito HOME=command-home, TMPDIR=tmp, PATH de venv-t012/Node/uv,
PYTHONNOUSERSITE=1, PYTHONDONTWRITEBYTECODE=1 y LANG=C.UTF-8, sin PYTHONPATH ni HARNESS_MANAGED_CONFIG.
`HOME` solo se pasa al proceso por el contrato operativo existente; no se cambia globalmente ni se reutiliza
como variable auxiliar de script. Único servicio real propuesto:

```sh
"$AREA/venv-t012/bin/harness-local" serve --database "$AREA/restored/t003/state.sqlite3" --port 8025
```

Login por barra nativa/pestaña nueva en `http://127.0.0.1:8025`, clave efímera directamente al formulario sin
imprimir/guardar credenciales. Verificar señal `read_only_archive=true`, ausencia de puertos/supervisor y
contexto permanente. Desde inicio introducir **`e3fa4ae6-5183-4bf9-a406-011b90370302`**; recargar su URL,
observar COMMITTED/commit **6f02121**, abrir ciclo/diff, validaciones, **13 casos JUnit**, original y métricas
con procedencia. Comparar diff SHA-256 **`db6fa9b245b8d7d9f9c10c534bf611ccbc526434673e35f46030e73ed892b3c0`**
y original JUnit **`7e51116eeec2b61fac2b2f4281a63852934a5b63bb1223e15e27a34a68ad4e63`** con T003.
No cambiar preferencias en la copia; revisar idioma actual y las rutas directas bloqueadas.

Consultar por id de manifiesto los dos REVISION_LIMIT y P001-T002 QUEUED; conservar sus estados y cero intentos/
preparaciones/lock de la tarea pendiente. Sin acciones de tarea, permisos, recuperación, registro o configuración.
Capturas saneadas privadas de detalle/commit, diff, casos/original/métricas y contexto de consulta. No repetir
lecturas HTTP ya acreditadas salvo las que consume la propia UI o el contraste puntual de hashes necesario.

Al primer error de origen/auth/hash/esquema/cache/ruta/UI, pregunta no deducible o efecto inesperado, detener
normalmente, conservar evidencia y pasar por HITL; no cambiar guardias ni reintentar con el saldo anterior.
Al acabar, servicio detenido, puerto cerrado/clave retirada, hashes y todas las filas conservados; comprobar
además B/B2/clon, TOML/distribuciones y evidencias previas contra sus manifiestos. Resultado saneado nuevo,
sin reescribir informes anteriores. Solo entonces dictaminar el criterio UI de T003; T004 sigue separado.
