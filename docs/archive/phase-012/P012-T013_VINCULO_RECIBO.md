# P012-T013 — Vínculo de preparación tras resolver las CLI

Fecha: **2026-10-26**. **Estado: implementada y verificada offline.**
Base: **54b44bb**, que conserva [la parada real T004](P012-T004_TYPESCRIPT_REAL.md) (D206).
Decisión: [D207](../DECISIONS.md#d207--p012-t013-vínculo-del-recibo-tras-resolución-cli).
Fuentes exactas de esta entrega: [manifiesto](P012-T013_CODE.sha256).

## Problema, reproducción y corrección

T004 completó una receta v2/es y su commit técnico, pero la petición de primera tarea devolvió 409
preparation_required. La reproducción HTTP nueva usa únicamente clientes/herramientas/datos sintéticos:
antes de preparar rechaza correctamente; después de receta COMPLETED y GET de preparación prepared=true,
POST de tarea sigue devolviendo **409 en vez de 202** sobre el código anterior. No se emplean los runs,
datos, recibos o instalaciones privadas como fixtures.

La admisión HTTP llama `frozen_versions` → `ManagedRuntime.resolve_project` → `LocalComposer.refresh(force=True)`.
V7/v8 recompone las versiones para observar las CLI; ese resultado no contiene la huella derivada del recibo.
La instalación del proyecto renovaba el idioma desde SQLite, pero no el vínculo de preparación. Por ello
`storage.preparation.admit` rechazaba correctamente versiones sin project_environment_sha256, aunque
`ProjectPreparation.read` acreditara el recibo en SQLite/checkout.

Tras refresh se vuelve a llamar **ProjectPreparation.bind** y se instala el proyecto resultante. Se usa la misma
autoridad existente que en arranque, carga de registro y final de preparación: receta/config compatibles →
digest exacto del recibo; configuración distinta o recibo ausente → sin nuevo vínculo. El idioma se vuelve a
ligar por la instalación normal. Los proyectos sin receta conservan su comportamiento.

La guardia admit y verify_receipt siguen intactas: tareas, checks y cierres exigen el vínculo exacto y rechazan
deriva protegida/de herramientas. No se copia la huella anterior a una composición nueva ni se modifica el
recibo, historial, job o configuración para desbloquear. Sin nuevo formato/esquema/API, cambios de motor,
runner, perfil, implementación/huellas de receta o dependencias.

## Validación offline

**14 regresiones parametrizadas nuevas**:

- Ocho secuencias HTTP: Django/TypeScript, en/es y v7/v8. Rechazo antes de preparar, receta completa,
  prepared=true y tarea 202/QUEUED sin intentos tras resolver las CLI; versiones CLI observadas, digest del
  recibo/config e idioma congelado correctos. Admisión compartida de task/phase_check/phase_close válida.
- Seis casos Django/TypeScript v8/es: cambio de recipe_config, archivo protegido o ejecutable preparado.
  Los tres propósitos se siguen rechazando; configuración distinta no liga huella ni conserva recibo en la
  caché del compositor. El recibo persistido no cambia y no se encola trabajo.

Reproducción roja observada en la variante TypeScript/es/v8 antes de editar el producto: 409 preparation_required
después de preparar. Tras el cambio, **24 tests del módulo** y **226 tests relacionados** pasan; **un opt-in
omitido** porque exige caché real explícita. También **8 unittest** correctos. Aviso existente de Starlette/httpx.

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 tests/product/test_recipe_v2_preparation.py
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_cli_discovery.py tests/product/test_local_config.py tests/product/test_managed_api.py tests/product/test_project_preparation.py tests/product/test_typescript_preparation.py tests/product/test_recipe_versions.py tests/product/test_phase_closure.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Cobertura dirigida de resolución CLI, configuración/formatos anteriores, API, recetas v1/v2, rechazo por deriva,
recuperación y cierre. Sin repetir suites completas, Node/tipos/build/Alembic: no cambia frontend, API o datos.
No se operan los fixtures reales, construye/instala wheel, lanza servicio o CLI/proveedores reales. Los grupos
de pruebas pertenecen a fixtures temporales con clientes falsos, no al tramo T004. Nuevo consumo real **0/0**.
Producto anterior instalado, hijo/recibo/HEAD técnico y parada T004 se conservan; la corrección aún no acredita
una tarea real, READY o cierre de ese hijo.

Checks documentales correctos: **12 fases, 13 tareas y 207 decisiones**, **706 enlaces/anclas** relativos en
los siete Markdown de la entrega; presupuestos STATE/base/NEXT_STEPS **21.109/24.576**, **9.171/12.288** y
**40.175/49.152 bytes**. D001–D206, informe/propuesta T004, recetas, storage, baseline pública y frontend
conservados; manifiesto de fuentes y diff comprobados. Siete hashes de entradas operativas, TOML T004 y
puertos cerrados vuelven a coincidir tras los tests. Sin nueva operación del área privada.

## Propuesta de continuación T004, sin autorizar

AREA sigue siendo `$HOME/Documents/harness-validation/p012-20261024`. Destinos nuevos **dist-t013/** y
**venv-t013/**, comprobados ausentes al cerrar la tarea. Base del producto: commit de esta entrega con las dos
fuentes del manifiesto; el commit documental posterior no cambia esos hashes. Registrar el id completo antes
de construir. Los hashes de wheel/sdist/pylock **aún no existen** y no se sustituyen por los de T012.

Conservar **state-t004/harness.sqlite3**, **config/harness-local-t004.toml** (3b9f433d…46a8d95), caché/entornos
y **projects/typescript-es** en HEAD **bcf59d8e20299c39df33a9aeea44845fc0409186**. No repetir creación,
conversación, bootstrap, receta, pruebas iniciales de preparación o el envío fallido. Es una petición nueva de
tarea tras corregir el producto, aún con cero intentos anteriores, y no recuperación de un run inexistente.

Antes de operar, contrastar el manifiesto de fuentes, instalación anterior conservada, ocho hashes de herramientas,
TOML, recibo y sus sellos de idioma/receta, nueve archivos del commit técnico y los 23 archivos versionados/modos
del hijo. Cero task runs, 4 DONE/9 STOPPED/0 locks; grupos propios acreditados detenidos con identidad actual.
Si hay identidad incierta, deriva, trabajo pendiente o destino ocupado, parar y revisar sin heredar excepciones.
Conservar también los siete hashes, las 16.798 filas y artefactos/fixtures de la base anterior (D199), que no se
abre con servicio. Clave previa ausente y puertos 8024/8025 cerrados; nuevo servicio solo en 8024.

Comandos futuros por etapas, desde REPO con Node/npm/uv y TMPDIR **AREA/tmp/t004** explícitos, `umask 077`:

```sh
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp/t004" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist-t013"
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp/t004" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist-t013"
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3 "$AREA/venv-t013"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip sync --offline --python "$AREA/venv-t013/bin/python" "$AREA/dist-t013/pylock.toml"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip install --offline --no-deps --python "$AREA/venv-t013/bin/python" "$AREA/dist-t013/harness_local-0.1.0-py3-none-any.whl"
```

Revisar hashes/miembros/SHA256SUMS y registrar artefactos antes de instalar. Verificador con CLI falsas y
servicios temporales de loopback; sin usarlo como evidencia del recorrido real. Caché incompleta → parada,
sin descargas implícitas. Desde AREA y entorno del servicio de la propuesta original, cambiando solo PATH al
venv-t013 y conservando HOME command-home-t004/TMPDIR tmp/t004, sin PYTHONPATH/config heredada:

```sh
"$AREA/venv-t013/bin/harness-local" check-config "$AREA/config/harness-local-t004.toml" --preflight
"$AREA/venv-t013/bin/harness-local" migrate --database "$AREA/state-t004/harness.sqlite3" --snapshots "$AREA/state-t004/operator/t013-premigration" --writers-stopped
"$AREA/venv-t013/bin/harness-local" serve --database "$AREA/state-t004/harness.sqlite3" --config "$AREA/config/harness-local-t004.toml" --port 8024
```

Migrate debe ser **no-op en 0025**, sin instantánea o cambios SQLite; nunca init-db sobre esta base ni tocar la
anterior. Guardar evidencia nueva con prefijo t013, sin sobrescribir resultados o logs de la parada. Verificar
que el proyecto arranca con idioma es y project_environment_sha256 igual al digest del recibo conservado.

UI Chrome por barra nativa, login privado sin guardar clave/ajustes. Comprobar preparado y misma P001/tarea,
documentos adoptados, HEAD limpio y TMPDIR ignorado 0700. Desde la creación, usar **una vez** «Encolar primera
tarea» con el texto congelado de P001-T001, contrastado con el NEXT_STEPS actual; sin edición de tarea o nuevo
brief. Plan Claude → única ejecución Codex → check/test/build/JUnit → revisión Claude → COMMITTED. Conservar
el límite a src/main.ts y docs/flows/titulo.md, normalización U+0020, API/defecto/sufijo y restricciones del guion.
No atribuir al caso JUnit existente cobertura nueva de espacios interiores.

Después, check P001 con Claude; solo READY vigente habilita la confirmación de cierre/tag **p001 del hijo**,
archivo y P002 ACTIVE con cero tareas. No plan posterior. Detener y acreditar puerto/clave/procesos/locks,
conservar estado anterior y nuevo, contrastar filas/manifiestos y registrar resultado separado sin reescribir D206.

**Presupuesto propuesto:** máximo nuevo **3 Claude/1 Codex** (plan/revisión/READY y única ejecución normal),
acumulado máximo T004 **6/12 Claude y 1/3 Codex**, cero correcciones/reintentos. Se conserva la ventana original
hasta **2026-10-26 12:00:10 UTC**, sin reponer tiempo. Si ya venció al recibir la autorización, no empezar:
revisar explícitamente la ventana con el usuario. Parada al primer fallo conforme al guion original.

**Consentimiento pendiente:** autorizar build/verificador/instalación offline en destinos nuevos, preflight,
migrate no-op/servicio/UI solo sobre state-t004, una petición nueva de tarea con producto corregido, READY y
cierre/tag/archivo del hijo, mismos archivos/modelos/permisos, nuevo máximo 3 Claude/1 Codex y deadline original.
T001 §7 y la parada del guion exigen ese consentimiento separado antes de efectos reales. El «continúa.» recibido
durante el diagnóstico no lo sustituye. Sin más conversación/receta, red de paquetes, base anterior, tags en
my_harness, push, publicación o cambios globales. T004 permanece parcial hasta aportar esa evidencia.
