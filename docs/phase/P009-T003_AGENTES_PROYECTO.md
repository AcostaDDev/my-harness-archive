# P009-T003 — Agentes configurables por proyecto

Fecha: 2026-10-19. Contrato: [D116 §4](P009-T001_CONTRATO_CREACION.md#4-presets-y-composición-por-proyecto-t003).
Decisión: [D118](../DECISIONS.md#d118--p009-t003-presets-v5-y-selección-de-agentes-por-proyecto).

## Resultado y motivo

El mismo proyecto registrado puede cambiar las cuatro parejas Codex/Claude sin editar el TOML entre tareas,
recrear su registro ni cambiar su checkout. `local-config-5` permite declarar presets del servicio, elegirlos
desde alta/creación/Ajustes y fijar explícitamente modelo/esfuerzo del revisor. El ejecutor conserva la selección
con motivo por tarea/revisión a cargo del revisor; Ajustes solo define proveedor y política admisible.

La composición efectiva guarda los dos CLIConfig por checkout y crea adaptadores nuevos para cada job.
`ports`, writer, `agents_view` y preflight emplean esa autoridad. No cambia `cli-12`, codec 7 ni layout D088.
V1–v4 conservan sus hashes; v5 sin selección conserva la pareja/política heredada, sin persistir overrides.

## Configuración y API

El operador migra expresamente su TOML privado a `format = "local-config-5"`. Conserva las claves v4 y añade
`[agent_presets.<id>]` opcionales. No se modifica ningún TOML ni configuración global del usuario en esta entrega.
La receta y los enlaces diferidos al entorno se implementarán en T004; esta versión aún los rechaza.

| Campos de cada preset | Contrato |
|---|---|
| `provider`, `roles` | Codex/Claude; reviewer y/o executor, únicos. CLI caracterizada para ese rol. |
| `executable`, `cli_version`, `timeout_seconds`, `environment` | Las reglas CLI actuales; argv absoluto existente y USER del UID. Cargar no ejecuta nada. |
| `tools`, `allowed_tools`, `grantable_tools` | Solo Claude; un preset utilizable como revisor no declara herramientas, pues su inventario de lectura es fijo. |
| `models`, `efforts` | Listas no vacías y únicas; modelos con forma del contrato y esfuerzos del vocabulario del proveedor. Catálogo local, sin afirmar disponibilidad remota. |
| `allow_open_executor` | Booleano explícito. `open` mantiene el esfuerzo dentro del subconjunto del preset; catálogo de modelos como referencia. |

Ejemplo de selección sintética de fila o `[[projects]]` v5, con presets previamente declarados por el operador:

```toml
agent_selection = { reviewer = { preset_id = "claude-reviewer", model = "reviewer-demo", effort = "high" }, executor = { preset_id = "codex-executor" } }
```

La política del ejecutor sigue exclusivamente en `policy`; la selección no acepta un modelo fijo del ejecutor,
ejecutables, herramientas, entorno o credenciales. Proyectos TOML siguen en consulta en UI. El formulario
identifica la pareja heredada y ofrece elegir por proyecto; cambiar de preset vacía modelo/esfuerzo del revisor
y los catálogos del ejecutor afectados. No escoge una alternativa si falta un preset compatible.

Se amplían `RegistryChangeInput` y `CreationInput` con la selección tipada; `RegistryRead` ofrece solo el catálogo
público (id/proveedor/roles/modelos/esfuerzos/modo libre), sin rutas CLI ni valores de entorno. Lectura/preview
añaden `configuration_blockers`. OpenAPI y tipos generados actualizados; se reutilizan sesión, CSRF y endpoints
del registro, sin rutas nuevas. `check-config --preflight` explícito incluye pareja heredada y cada rol admitido
de los presets; cargar y consultar no lo ejecutan.

## Persistencia, concurrencia y recuperación

Sin migración: selección en JSON `registered_projects.row` y sus eventos existentes, versión/hash de D078.
Preview liga selección y contenido completo de los presets elegidos. Confirmación incrementa una vez;
repetir la misma preview aplicada devuelve la versión original. V5 congela también id/hash de fila además de
su versión. Cambiar un preset del TOML conserva cuarentena; uno ausente vuelve no disponible la fila al reiniciar.

Además de jobs/locks, cambios v5 y bajas bloquean aceptación/commit pendientes, propuestas de chat sin resolver,
definición/importación con turnos utilizables y operaciones documentales incompletas. Se comprueba tanto en
preview como dentro de la transacción que actualiza el registro. Los planes de fase todavía PROPOSED pasan
a SUPERSEDED en esa transacción con actor/fecha/versión, sin tocar contenido/hash ni request/result del turno.
Un nuevo turno produce otro plan; no se reutiliza la propuesta anterior. Id, raíz e historial permanecen.

La admisión de nuevos runs, reanudaciones y commits comprueba la fila activa en la misma exclusión SQLite:
un job anterior al cambio lo bloquea; un envío posterior con la versión vieja se rechaza antes de encolar.
Los jobs congelados que derivan por TOML siguen en RECOVERY_REQUIRED antes de efectos. La exclusión de una
preparación futura corresponde a T004, junto a sus tablas/locks; no se simula con ids ficticios.

Flujo vigente en [project-agents](../flows/project-agents.md), paridad del JSON en
[DDBB-DIAGRAM](../DDBB-DIAGRAM.md#métricas-y-registro-de-proyectos-p007).

## Verificación

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: 1.506 tests y 121 subtests
  correctos (16 min 47 s). El caso de creación con presets añadido después de iniciar esa colección pasa
  por separado: cobertura actual de 1.507 casos. La matriz dirigida final vuelve a verificar los cuatro
  commits y el cambio posterior sobre los historiales conservados.
- 33 casos nuevos dirigidos correctos: cuatro parejas con CLI falsas por el adaptador real, commits y cambio
  posterior con historial intacto, cambios sucesivos sobre un mismo id/checkout, otro proyecto intacto, replay,
  reinicio, ausencia/deriva de presets, catálogos/modo libre sin fallback, aceptación pendiente, conversaciones,
  obsolescencia sin reescribir snapshots, carreras de admisión y creación de hijo con presets.
- Regresión dirigida previa: 142 tests de configuración, registro, roles, perfiles y creación correctos.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- `node --test frontend/tests/*.test.mjs`: 77 tests correctos. Tipos y build Vite correctos.
- Alembic upgrade/check sobre SQLite temporal: sin diferencias de metadata. No se modifica la SQLite local.
- OpenAPI exportado coincide con `create_app().openapi()`; tipos generados actualizados.
- Documentación activa: 20 Markdown en `docs/`, 348 enlaces/anclas relativos válidos; 118 decisiones consecutivas,
  nueve fases y doce tareas P009 por los parsers del producto. STATE/base/NEXT_STEPS dentro de presupuestos.
  Dos flowcharts modificados con sintaxis Mermaid correcta, sin render DOM. Diff revisado y whitespace correcto.
- Avisos existentes: deprecación Starlette/httpx en pytest y chunk Mermaid superior a 500 kB en Vite.
  Sin dependencias añadidas ni checks debilitados.

QA visual de assets compilados en Chrome con HTTP sintético en loopback: selección sin preseleccionar
modelo/esfuerzo, catálogos, preview/confirmación y actualización inmediata de agentes y versión del mismo
proyecto. El servidor simulado no ejecuta el harness ni crea carpetas de producto; pestaña/servidor retirados.
[Captura del resultado sintético](P009-T003_QA.jpg).

Sin proveedores reales, smokes, instalaciones/red, piloto, push o publicación. T004 es la siguiente tarea.
