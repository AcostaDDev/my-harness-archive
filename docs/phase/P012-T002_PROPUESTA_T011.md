# P012-T002 — Continuación propuesta tras corregir los presets UI v8

Fecha: 2026-10-24. **Estado: propuesta revisada offline; consentimiento operativo pendiente.**
Base del producto: **`500a783c90e2f3ae581ba3c0fd483d1e7a2b1808`**, corrección T011 incluida.
Decisión: [D197](../DECISIONS.md#d197--p012-t002-propuesta-de-continuación-tras-t011).
Precedentes: [T011 §4](P012-T011_PRESETS_UI_V8.md#4-próximo-paso-todavía-sin-autorizar),
[propuesta anterior](P012-T002_PROPUESTA_T010.md) y D194–D196. No se reanuda el consentimiento agotado de D195.

## 1. Delta y destinos exactos

Se propone construir/verificar/instalar el producto corregido en **dist-t011/venv-t011 nuevos**, conservando el
clon documental y la configuración que quedaron preparados antes del alta. No hace falta otra incorporación B:
los dos B ya están COMMITTED; falta acreditar una tarea COMMITTED con el perfil declarado y el formateador.

`AREA=$HOME/Documents/harness-validation/p012-20261024`.

| Destino bajo AREA | Efecto propuesto |
|---|---|
| `dist-t011/`, `venv-t011/` | Distribución nueva y harness instalado con Python 3.14.4 |
| `projects/managed-b-t010/` | Conservar clon, venv Django 3.13.13 y `.local/codex-tmp`; registro/documentos/tarea por UI |
| `config/harness-local-t010.toml` | Leer el TOML v8 existente, sin modificarlo ni regenerarlo |
| `state/operator/t011-*`, `tmp/t011-*` | Evidencia privada, manifiestos y copias de consulta nuevas |
| `state/harness.sqlite3` y artefactos normales del producto | Misma base; escrituras exclusivamente por el producto |

El cambio respecto de la propuesta anterior se limita a base del producto, dist/venv nuevos y prefijos de
evidencia. Se conservan puerto **8024**, raíz, id **p012-b-t010**, perfil **python-django-t010**, composición
**django-t010**, presets **claude-t010/codex-t010**, entorno, permisos, modelos y contrato de tarea.
No crear otro clon, ajustar modos o cambiar destinos/configuración automáticamente ante una discrepancia.

## 2. Puerta de conservación antes de cualquier operación

Comprobación de solo lectura realizada al preparar esta propuesta:

- Clon en **`9808fd97d349c6eeacb766be8ff5e5603b6e974c`**, limpio, sin remoto ni alternates. Los **28 archivos**
  versionados coinciden por SHA-256 tanto con sus blobs de HEAD como con `state/operator/t010-clone-manifest.json`.
  Modos de disco exactos: **15 originales 0600 y 13 documentos 0644**; no se confunden con modos Git.
- TOML modo **0600**, SHA-256 **`e0e95abb9055f1c9f985c82285bc3c7b551f6503ff6bddb5aff7ddf282fbb6db`**.
  `dist-t011` y `venv-t011` ausentes. Área, raíz y TOML sin componentes simbólicos.
- SQLite leída con `mode=ro&immutable=1`, sin WAL pendiente: integridad **ok**, esquema
  **0025_project_work_languages**, **13.785 filas** en tablas no `sqlite_*`, **7 jobs DONE**, **9 procesos STOPPED**,
  **0 locks**. Sin registro por raíz/id, fase o run del clon. No se abre el harness ni se escriben datos operativos.

Repetir todo tras consentimiento y antes de operar. Además: comprobar área fuera de checkouts, destinos nuevos
ausentes y sin enlaces, puerto libre, servicio/escritores detenidos, sin grupos vivos ni trabajo utilizable
pendiente. `umask 077`, directorios privados 0700. Verificar destinos resueltos de enlaces propios de venv/toolchain.

Contrastar los ocho hashes de toolchain de [T001 §2](P012-T001_PROPUESTA_OPERATIVA.md#2-toolchain-observada-y-modelos-propuestos),
los 17 wheels del [manifiesto aprobado](P012-T002_WHEELS_VERIFICADOS.sha256) y el lock Django
`0f2ce9af…313c1b`. Acreditar venv Django y TMPDIR existente/ignorado sin reinstalarlos por defecto. Conservar
manifiestos SHA-256/modos de B/B2/diffs/configuraciones/distribuciones y copias SQLite/WAL/SHM con escritores
detenidos. Al acabar, contrastar las filas previas y declarar las escrituras normales nuevas del producto.
Si aparece WAL, usar copias consistentes de consulta; no ignorarlo para afirmar integridad o igualdad.

## 3. Construcción, instalación y arranque propuestos

**Comandos futuros; no ejecutados.** Desde
`REPO=$HOME/Documents/projects/my_harness`, verificar que fuentes, scripts, locks y entradas del paquete
coinciden con la base `500a783`; este documento privado no entra en el paquete. Usar PATH explícito de T001
(Node/npm 24.15.0/11.12.1 y uv 0.12.19), sin configuración ambiental heredada.

```sh
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist-t011"
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist-t011"
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3 "$AREA/venv-t011"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip sync --offline --python "$AREA/venv-t011/bin/python" "$AREA/dist-t011/pylock.toml"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip install --offline --no-deps --python "$AREA/venv-t011/bin/python" "$AREA/dist-t011/harness_local-0.1.0-py3-none-any.whl"
```

Ejecutar por etapas con guardias, nunca como bloque sin controles. Antes de instalar, contrastar SHA256SUMS y
registrar hashes completos de wheel/sdist/pylock: **aún no existen**, no se reutilizan los de T010. El verificador
incluye CLI falsas, venv temporal y servicios efímeros de loopback. El build recompone frontend/dist y usa las
cachés locales existentes; cualquier dependencia ausente obliga a parar, sin descarga implícita.

Desde AREA, con HOME `command-home`, TMPDIR `tmp`, PATH explícito venv-t011/Node/uv, PYTHONNOUSERSITE=1,
PYTHONDONTWRITEBYTECODE=1 y LANG=C.UTF-8, sin PYTHONPATH/config ambiental:

```sh
"$AREA/venv-t011/bin/harness-local" check-config "$AREA/config/harness-local-t010.toml" --preflight
"$AREA/venv-t011/bin/harness-local" migrate --database "$AREA/state/harness.sqlite3" --snapshots "$AREA/state/operator/t011-premigration" --writers-stopped
"$AREA/venv-t011/bin/harness-local" serve --database "$AREA/state/harness.sqlite3" --config "$AREA/config/harness-local-t010.toml" --port 8024
```

Entre preflight y servicio, ejecutar en **managed-b-t010**, con argv/entorno exactos de django-t010, las dos
preparaciones y seis validaciones/JUnit: ocho checks correctos y los 28 archivos versionados intactos por
bytes/modos. No aplicar formateador ni tests a B/B2. `migrate` debe ser no-op sin instantánea ni cambio SQLite;
esquema inesperado → parada. No init-db sobre la base existente ni scripts/dev. Operación desde el wheel
instalado fuera del checkout; no se ejecuta este repositorio con el harness.

## 4. Recorrido autorizado solo tras respuesta HITL

Login en la pestaña local de 127.0.0.1:8024, clave privada directa al formulario sin imprimirla. Si reaparece
el rechazo cross-site, parar y pasar por HITL; conservar Host/Origin/CSRF. En el formulario corregido comprobar
presets v8 visibles y elegir los dos t010 explícitamente; no sustituirlos por la pareja heredada.

Se conserva íntegro [el recorrido anterior §4](P012-T002_PROPUESTA_T010.md#4-registro-documentación-y-única-tarea):
registro p012-b-t010, es/es, bootstrap false, composición/perfil/presets de §1, confianza explícita en fixture
sintético; P001 ACTIVE desde ROADMAP con sus siete criterios y P001-T001 desde NEXT_STEPS. Sin otra B ni
conversación/inventario/propuestas de incorporación.

Dos commits documentales secuenciales mediante editor UI, vista previa/CAS/confirmación del producto:
AGENTS.md acredita el perfil/composición/formateador y checks; docs/DECISIONS.md conserva D001–D005 y añade
D006 con la elección del operador y el índice regenerado. Textos exactos en el §4 citado, bloques gestionados
conservados; adopción por hash si se requiere y checkout/documentos confirmados antes de encolar. No escribir
archivos del hijo manualmente ni usar una API alternativa. No editar herramientas, código o NEXT_STEPS al preparar.

Política: **Claude sonnet/low**, timeout 1800 s; **Codex gpt-6-luna/low**, timeout 3600 s; planning_mode **agent**,
executor_mode **catalog** con ese único modelo/esfuerzo, **max_revision_cycles = 0**. CLI previstas
**2.1.310/0.164.0**, compatibilidad condicionada cli-14; identidad comprobada por intento/antes de GO.

Una tarea seleccionada del NEXT_STEPS por CAS: entrada `int`, rango 1–20, defecto 5; HTTP 400 JSON con `error`
descriptivo para vacío/texto/0/21/5.0; aceptar espacios, `%2B5` y `05`, probar extremos/límite efectivo y conservar
casos originales. Solo **catalog/views.py**, **catalog/tests/test_views.py**, **docs/flows/items-listado.md**.
Sin dependencias, modelos, migraciones, configuración ni rutas nuevas.

Plan Claude → una ejecución Codex → formateador nativo D133 `ruff format --` sobre Python cambiado/permitido
→ seis validaciones/JUnit → revisión Claude → aceptación exacta y commit del producto si corresponde.
Guardar formatting_json, argv/rutas/exit, diff, JUnit, identidad/modelos reportados y commit. Una aceptación válida
de esos bytes; no next_prompt, correcciones o revalidaciones después de un fallo. No cerrar P001 ni iniciar chat,
backup/restauración de producto, T003/T004 o prueba idempotente adicional.

## 5. Presupuesto, parada y decisión solicitada

Consumo anterior **Claude 7/12, Codex 2/3**. Máximo nuevo **2 Claude y 1 Codex**, acumulado máximo **9/12 y 3/3**.
Las dos llamadas Claude son plan/revisión; no hay turno de incorporación. Cero correcciones, sin fallback,
ampliación o reposición de saldo. Máximo **4 horas** desde la preparación operativa.

Parar al primer fallo de identidad/proveedor/auth/esquema/timeout, formato/validación, permisos, CAS/hash,
destino/cache, REVISE/BLOCKED, pregunta no deducible o cuarentena. El motor puede sellar la validación/revisión
ya en marcha como en D193; nunca iniciar otro ciclo. HITL antes de un paso dependiente de una respuesta.
No reparar resultados a mano, editar TOML/SQLite para desbloquear o reutilizar un run agotado con otra política.

Al terminar o parar, detener servicio/grupos propios, acreditar puerto cerrado, clave retirada, jobs terminales,
procesos STOPPED y cero locks. Conservar área/evidencias y comparar manifiestos/copias de consulta. Datos privados,
tokens, prompts y streams completos permanecen fuera del repositorio. Una parada agota este consentimiento:
no habilita otro intento. T002 solo se completa al acreditar sus criterios, incluida la tarea COMMITTED.

**HITL pendiente:** «Autorizar la continuación de T002 según P012-T002_PROPUESTA_T011: build/verificador e
instalación offline en dist-t011/venv-t011 nuevos, conservar y comprobar clon/TOML t010, preflight/ocho checks,
servicio/UI 8024, registro/P001, dos commits documentales y una tarea; máximo nuevo 2 Claude/1 Codex, cero
correcciones y parada al primer fallo».

La petición genérica de continuar y hacer commit autoriza preparar esta propuesta y su commit de documentación.
AGENTS, T001 §7 y D196 exigen respuesta operativa específica antes del build, servicio o proveedores. Sin
descargas, cambio global, operación de B/B2 fallidos, otro clon/B, T003/T004, tags, push o publicación.

## 6. Validación de la propuesta

Contraste con SPECIFICATION §§6/8/9/11, ARCHITECTURE §§6/9, D194–D196, T001 y propuesta T010. Comprobación
local de solo lectura de §2, sin invocar CLI reales, modelos, servicio, build operativo o checks del fixture.
No cambia producto, esquema, API o flujo implementado; diagrama/flujos y baseline pública permanecen iguales.
Checks correctos: parsers del producto (**12 fases, 7 criterios P012, 11 tareas, 197 decisiones**), **606
enlaces/anclas relativos** en los cinco Markdown de esta entrega y presupuestos STATE/base/NEXT_STEPS
**14.198/24.576**, **8.914/12.288**, **26.903/49.152 bytes**. Cuerpos D001–D196 conservados por bytes;
diff revisado y `git diff --check` correcto. Sin cambios en archivo histórico, baseline pública o código.
No se repiten suites Python/Node, tipos/build o Alembic: entrega documental sin cambio de producto/datos.
Los ocho checks del clon y la verificación del wheel nuevo siguen pendientes del consentimiento operativo.
