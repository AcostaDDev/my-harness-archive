# P008-T008 — Perfiles declarativos en el TOML local

Fecha: 2026-10-16. Base: D088 punto 11, D049 y D078. Decisión: [D095](../DECISIONS.md#d095--p008-t008-perfiles-declarados-en-local-config-4).

## Entrega

- `services/local_config.py`: formato `local-config-4`, que admite `[profiles.<nombre>]` además de lo que ya
  admitía `local-config-3`. `_profile` convierte la tabla en un `ProjectProfile` sin ejecutar nada. `_command` es el
  parser común de comandos exactos y lo usan también las autorizaciones extra. `_shell_free` aplica la regla de argv
  sin shell, y `_patterns` comprueba que los patrones sean relativos al checkout. El compositor guarda el mapa
  nombre → perfil y añade a la autoridad congelada `asdict(profile)` en v4. `summary` incluye `profiles` y
  `registrable` acepta v3 y v4.
- `examples/local_config.example.toml`: pasa a `local-config-4`, con `[profiles.python-django]` y
  `[compositions.django]` junto a la composición `web`, que no cambia.
- `tests/product/test_declared_profiles.py` (27 casos) y el modo `django` de `cli_process_probe.py`.
- `docs/ARCHITECTURE.md` §6: TOML v4 y perfiles.

Sin cambios en `profiles/` ni en `core/engine/context.py`: `ProjectProfile` ya tenía todos los campos que se
necesitaban, y `restore_context` reconstruye el perfil desde el snapshot, así que un perfil declarado se restaura
igual que uno integrado.

## Formato

```toml
[profiles.python-django]
preparation = [{ argv = ["python", "--version"], timeout_seconds = 30 }]
validations = [
  { argv = ["pytest", "--junitxml=.local/junit.xml", "-q"], timeout_seconds = 900,
    junit = { path = ".local/junit.xml", coverage = "Tests pytest del proyecto; no cobertura de código" } },
  { argv = ["ruff", "check", "."], timeout_seconds = 120 },
]
allowed_command_prefixes = [["pytest"], ["ruff", "check"]]
protected_paths = ["docs/STATE.md", "..."]
sensitive_paths = [".env", "..."]
data_model_paths = ["**/models.py", "**/migrations/**"]
executor_instructions = "..."

[compositions.django]
profile = "python-django"
authorize_profile_commands = true
executables = { python = "/abs/.venv/bin/python", pytest = "/abs/.venv/bin/pytest", ruff = "/abs/.venv/bin/ruff" }
environment = { PATH = "/abs/.venv/bin:/usr/bin:/bin", HOME = "/abs/home", LANG = "C.UTF-8" }
```

La composición sigue autorizando exactamente la preparación y las validaciones del perfil. Si un `argv[0]` no está
en `executables`, la composición se rechaza al cargar.

## Verificación

- 12 checks ligeros (`unittest`) correctos.
- Pytest completo: 1.218 OK, 121 subtests y 1 fallo, con el aviso conocido de Starlette/httpx. El fallo era
  `test_example_template_documents_the_local_config_3_keys`, que fijaba el formato del ejemplo a v3. Se renombró a
  `..._local_config_4_keys`, ahora espera `[profiles]`, y `test_previous_formats_keep_their_frozen_identity` comprueba
  además el hash congelado de `local-config-3`. Re-ejecutados `test_project_registry.py`,
  `test_declared_profiles.py` y `test_local_config.py`: 74 OK.
- Casos nuevos:
  - El perfil `python-django` del ejemplo compone sin lanzar procesos.
  - `check-config` lo valida y rechaza un argv con `bash -c`.
  - 22 rechazos sin efectos, cada uno comprobado por su mensaje: claves desconocidas o ausentes, shell, operadores,
    sustitución, rutas, prefijos, ejecutable que apunta a `/bin/sh`, duplicados, JUnit fuera del checkout, nombre
    integrado, perfil no declarado y `[profiles]` en v3.
  - Un cambio del perfil cambia `local_config_sha256` y deja en cuarentena el job admitido antes.
  - Recorrido sintético Django: agentes falsos y herramientas falsas que comprueban el código del checkout. Pasa por
    las 2 preparaciones y las 6 validaciones en orden exacto, con JUnit `complete`/`created`, y termina en un commit
    COMMITTED con el checkout limpio.
  - `typescript-web` en v3 y v4: mismo contexto y comandos; solo cambian el formato y el hash.
- 241 enlaces y anclas de los cinco Markdown editados, todos válidos.
- No se ejecutaron `alembic check`, las pruebas Node ni el build, porque no cambian modelos, migraciones, UI ni
  OpenAPI. Tampoco proveedores reales, smokes ni herramientas Python reales.

## Fuera de alcance y pendientes

- `cli.py` (ayuda de `serve --config`), `services/project_registry.py` (diagnóstico «requiere local-config-3») y la
  UI (Home y Registry) siguen citando `local-config-3` como requisito del registro. Siguen siendo ciertos para v3,
  pero no mencionan v4. Esos archivos están fuera de las rutas permitidas.
- El ejemplo `python-django` no se ha ensayado con un proyecto ni con herramientas reales. `mypy .` sobre Django
  puede requerir `django-stubs`, y `pytest` requiere `pytest-django` configurado en el proyecto: lo confirma el
  usuario al adoptarlo.
- La propuesta de perfil a partir del inventario es del Flujo B (P008-T013) y usa este formato.
