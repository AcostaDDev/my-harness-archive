# my_harness — Harness Local

Aplicación local para configurar, ejecutar y observar un harness de desarrollo con agentes. Planifica, ejecuta,
valida, revisa y hace commit de tareas acotadas sobre tus repositorios, organizadas en fases, con chat, métricas,
tests y documentación por proyecto. Todo corre en tu máquina: el servicio solo escucha en `127.0.0.1` y los modelos se
usan a través de las CLI de Codex y Claude Code con tu propia suscripción.

## Estado

Fases P001–P008 completadas, incluido el contrato documental unificado, cierre de fase e importación de proyectos.
Sin fase activa; la próxima prioridad está por definir. Detalle en [ROADMAP](docs/ROADMAP.md) y
[STATE](docs/STATE.md). Verificación offline con datos sintéticos; el uso con proveedores reales se ha comprobado
en ejecuciones puntuales autorizadas.

## Requisitos

- macOS (probado en ARM64) con Python 3.14.4 y uv 0.12.19.
- Node 24.15.0 y npm 11.12.1 solo para desarrollar o construir la UI.
- Para uso real: CLI `codex` (0.162.1 para escribir) y/o `claude` (2.1.295 o 2.1.296) ya autenticadas.

## Instalación para uso real

El uso real se opera desde el paquete construido, nunca desde este checkout (D051):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/build_distribution.py --out-dir /ruta/paquete
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/check_distribution.py --dist /ruta/paquete
uv venv --python 3.14.4 --no-python-downloads /ruta/venv
uv pip sync --python /ruta/venv/bin/python --require-hashes /ruta/paquete/requirements.txt
uv pip install --python /ruta/venv/bin/python --no-deps /ruta/paquete/harness_local-0.1.0-py3-none-any.whl
```

Configuración: copia [la plantilla TOML](examples/local_config.example.toml) fuera de todo checkout, `chmod 600`, y
ajusta agentes, Git, composiciones y raíces de registro. Después:

```sh
/ruta/venv/bin/harness-local check-config /ruta/harness-local.toml --preflight
/ruta/venv/bin/harness-local init-db --database /ruta/state/harness.sqlite3
/ruta/venv/bin/harness-local serve --database /ruta/state/harness.sqlite3 --config /ruta/harness-local.toml
```

Abre `http://127.0.0.1:8013` y pega la clave de sesión del archivo privado que anuncia el arranque (válida ocho horas).
Con el supervisor activo, el servicio invoca las CLI configuradas y consume tu suscripción.

## Desarrollo

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
scripts/dev
```

`scripts/dev` comprueba versiones, migra la SQLite local (`.local/harness.sqlite3`) con un backup previo y arranca la
API en `:8013` y Vite en `http://127.0.0.1:5173`. Admite `--database` y `--config`.

## Tests

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
node --test frontend/tests/*.test.mjs
npm --prefix frontend run build
```

Las pruebas usan Git, SQLite y procesos temporales con agentes falsos; no consumen proveedores ni red.

## Estructura

- `src/harness_local/`: núcleo y motor (`core/`), adaptadores, persistencia, servicios, API y migraciones.
- `frontend/`: UI React/TypeScript; `frontend/src/api.generated.ts` se genera desde OpenAPI.
- `tests/`: pruebas y fixtures sintéticos. `scripts/`: desarrollo y distribución. `examples/`: demos y plantilla TOML.

## Documentación

- [Especificación](docs/SPECIFICATION.md): requisitos y reglas de negocio.
- [Arquitectura](docs/ARCHITECTURE.md): stack, módulos, patrones, comandos y límites.
- [Roadmap](docs/ROADMAP.md), [estado](docs/STATE.md) y [siguientes pasos](docs/NEXT_STEPS.md).
- [Decisiones](docs/DECISIONS.md), [diagrama de datos](docs/DDBB-DIAGRAM.md) y [flujos](docs/flows/task-run.md).
- [Archivo de fases](docs/archive/phase-008/SUMMARY.md): entregas, revisión y evidencia de la última fase cerrada.
- Instrucciones para agentes: [AGENTS.md](AGENTS.md), con [CLAUDE.md](CLAUDE.md) y [GEMINI.md](GEMINI.md) como envoltorios.
