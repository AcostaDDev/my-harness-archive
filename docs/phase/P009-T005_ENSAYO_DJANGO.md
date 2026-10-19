# P009-T005 — Ensayo de creación Django y cuatro parejas sin proveedores

Fecha: 2026-10-19. Decisión [D120](../DECISIONS.md#d120--p009-t005-ensayo-temporal-con-cli-falsas-y-django-real).
Base: producto de T002–T004, sin cambios en sus contratos, receta, versiones, API ni esquema.

## Resultado y motivo

Se añade un ensayo completo porque las pruebas previas cubrían creación, roles y preparación por separado;
T004 solo había contrastado las herramientas Django mediante procesos sintéticos.
[Prueba reproducible](../../tests/product/test_django_journey.py) por la API con sesión local real, Git/SQLite
temporales y adaptadores CLI de producto conectados a procesos falsos. Dos variantes: herramientas sintéticas
para la suite offline ordinaria y Django/pytest/ruff/mypy reales con un wheelhouse explícito.

| Tramo | Comprobación |
|---|---|
| Elegir raíz y crear hijo | Raíz temporal explícita fuera de roots TOML; solo un hijo, registro e intención aunque se reenvíe la petición y se reinicie. |
| Definición D088 | Conversación con CLI falsa, propuestas aplicadas/confirmadas; commit documental raíz y fase con cuatro tareas. |
| Preparación | Plan offline confirmado; herramientas/lock intactos, generación por templates propios, validadores y commit técnico separado. |
| Recuperación | Fallo simulado después del commit técnico; reinicio sin replay y sucesora confirmada que concilia el mismo hash sin procesos nuevos. Plan/pasos previos conservados. |
| Cuatro parejas | Codex→Codex, Codex→Claude, Claude→Claude, Claude→Codex, en ese orden y mismo id/checkout/historial. |
| Selección e historia | Revisor falso elige ejecutor/modelo/esfuerzo/motivo; intentos planner/executor/reviewer y specs de procesos coinciden. Cambios de roles/reinicio conservan recibo y runs previos. |
| Cierre | Check READY_TO_CLOSE, cierre CLOSED/COMMITTED, tag al HEAD anterior y archivo exacto de STATE/NEXT_STEPS. Reenvío no duplica cierre. |

Cada variante deja siete commits: definición, preparación, cuatro incrementos sintéticos y cierre; catorce
intentos de agente con prompt: definición, doce de tareas y revisión de fase, además de sondeos falsos de versión/ayuda.
Las cuatro tareas añaden marcas a la
plantilla y mantienen el test de la portada. No implementan Task/CRUD ni sustituyen las tareas del piloto.
Entorno, secreto local, SQLite, caches y JUnit permanecen ignorados. No se escribe en el padre ni en hermanos
durante las tareas; los specs de agentes señalan únicamente el cwd del hijo.

Se amplía [cli_process_probe.py](../../tests/product/cli_process_probe.py) con respuestas de ensayo explícitas
desde un archivo privado de la fixture fuera del hijo. Conserva las guardias existentes de CLI, memoria,
restricciones de lectura y sandbox de escritura. No llama a Codex ni Claude reales.

## Herramientas reales y autorización

El usuario autoriza en esta sesión la descarga de los 17 wheels del lock, verificación de hashes y uso en
entornos temporales con Python 3.13.13 y uv 0.12.19 ya instalados, sin cambios globales ni proveedores.
Se descargan **34.425.869 bytes de wheels**, sin sdists/builds ni resolver un cierre distinto; se elige el wheel
compatible con macOS arm64/CPython 3.13 de cada versión. Todos los SHA-256 están en el lock empaquetado.
[Recibo público saneado](P009-T005_WHEELS.json), sin rutas privadas, secretos, logs ni runs operativos.

La prueba no descarga paquetes. Usa el wheelhouse preparado en directorio temporal; la propia receta crea
el venv del hijo sin pip e instala offline con hashes, `--no-deps`, `--only-binary`, copias y caché privada.
No hay cambios de scaffold, límites o configuración para hacer pasar las herramientas.

Comandos reales de preparación y del perfil comprobados:

```sh
python -m django startproject config .harness-preparation/output --template .harness-preparation/templates/project
python -m django startapp core .harness-preparation/output/core --template .harness-preparation/templates/app
python manage.py migrate --noinput
pytest --junitxml=reports/pytest.xml
ruff check .
ruff format --check .
mypy config core manage.py
python manage.py check
python manage.py makemigrations --check --dry-run --noinput
```

Los ejecutables reales son los absolutos de la preview: Python base/uv del operador y herramientas de `.venv`.
pytest produce un caso correcto de portada y JUnit consistente; ruff comprueba lint y formato, mypy usa modo
estricto con django-stubs/plugin; Django aplica sus migraciones base, pasa check y no propone migraciones nuevas.
Los seis validadores del perfil se repiten por cada tarea; check de fase usa las validaciones del producto.

Para repetir con paquetes ya preparados y autorizados, sin descargar:

```sh
HARNESS_TEST_DJANGO_PYTHON=/ruta/absoluta/python3.13 \
HARNESS_TEST_DJANGO_WHEELHOUSE=/ruta/absoluta/wheels \
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_django_journey.py
```

Sin ambas variables, la suite ordinaria ejecuta la variante sintética y omite la real con motivo explícito;
si solo se proporciona una, falla la configuración. No instala paquetes automáticamente fuera del hijo ni
consulta caches globales de paquetes para deducir un permiso de red.

## Verificación y fronteras

- Recorrido final, con comprobación de proveedor/modelo/esfuerzo en los argv reales de las CLI falsas:
  **dos variantes correctas**, sintética y Django real, en 3 min 49 s. La segunda se ejecuta completamente
  offline con el wheelhouse autorizado. Sin variables, **una omisión explícita** de la variante real comprobada.
- Suite offline completa: **1.548 tests y 121 subtests correctos, sin fallos ni omisiones**, repartidos en
  tres particiones disjuntas de 516 casos (`uv run --frozen --offline pytest -q @...`), que cubren exactamente
  la colección. Resultados por partición: 516; 516 + 24 subtests; 516 + 97 subtests. Duración máxima: 12 min 27 s.
  Las variables explícitas de toolchain real están presentes también en la partición que contiene esa variante.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **12 checks** correctos.
- `node --test frontend/tests/*.test.mjs`: **79 tests** correctos. `npm --prefix frontend run check`
  y `npm --prefix frontend run build`: correctos.
- Alembic upgrade/check sobre SQLite temporal: sin diferencias de metadata. No se usa la base local del usuario.
  Exportación OpenAPI idéntica a `create_app().openapi()`; no hay contrato/tipos nuevos que regenerar.
- **23 Markdown activos, 381 enlaces/anclas relativos**, 120 decisiones, nueve fases y doce tareas P009
  correctos por enlaces/parsers; presupuestos de STATE/base/NEXT_STEPS correctos. Diagramas sin cambios.
- Diff revisado y `git diff --check` correcto. Avisos existentes: deprecación Starlette/httpx y chunk Vite
  superior a 500 kB; no afectan al resultado.

El wheelhouse descargado se elimina tras las verificaciones; solo se conserva su recibo público saneado.
Los entornos y SQLite del ensayo usan los directorios temporales de pytest y su retención ordinaria.

Casos de frontera existentes incluidos en la regresión: destinos ocupados/incluso vacíos, escapes/enlaces,
raíz retirada y permisos obsoletos, deriva de identidad/configuración/archivos/entorno, instalación fallida,
cancelación antes de efectos y de proceso vivo, leases vencidos, JUnit incoherente y fallos de commit/adopción.
La nueva prueba integra recuperación y continuidad en el mismo recorrido; no reemplaza esas pruebas dirigidas.

No cambia producto, migraciones/modelos, dependencias del harness, OpenAPI/tipos, versiones congeladas ni
diagramas de datos. Los flujos vigentes enlazan la nueva evidencia y corrigen una referencia pendiente de T004
en la exclusión de cambios de roles. STATE/NEXT_STEPS, ROADMAP, SPECIFICATION y ARCHITECTURE reflejan T005.
Los registros históricos de T001–T004 permanecen intactos.

QA funcional de API y portada a través del cliente de Django/pytest. No cambia UI; no se repite QA visual ni
se arranca un servidor/navegador del Django, el wheel operativo, smokes o proveedores. Evidencia limitada a
macOS arm64 y Python 3.13.13; no se han ensayado Python 3.11/3.12, otras plataformas ni instalación de receta
en modo network. El piloto y sus selecciones/consentimientos siguen pendientes en T006.
