# P010-T008 — Propuesta de validación real complementaria

Fecha: 2026-10-22. Base de producto: `dd7b958` (T012). **Estado: completada; validación real aplazada por el usuario.**
Decisión: [D151](../DECISIONS.md#d151--p010-t008-validación-real-complementaria-aplazada).
Tarea exclusivamente documental: no se ha construido ni instalado un wheel, creado fixtures operativos,
consultado el área de P009, lanzado CLI, proveedores, servicios o smokes. Este documento no concede autoridad
operativa. [Contrato de tarea](../NEXT_STEPS.md#p010-t008--propuesta-de-validación-real-complementaria-y-alcance).

## 1. Qué falta y qué ya está acreditado

| Capacidad | Evidencia disponible | Afirmación que añadiría este recorrido |
|---|---|---|
| Flujo A: normalizar un harness anterior | P008, D100/D105/D108/D110/D112 y quinta revisión D113: originales por bytes, commit conciliable, fase adoptada, CAS y fronteras Git con agentes falsos | Un revisor real produce documentación revisable sobre un origen sintético anterior; la confirmación conserva originales y permite continuar bajo D088 |
| Flujo B: incorporar código sin harness | P008, D101–D103/D113: inventario estático, conversación, perfil confirmado, commit documental y continuidad sintéticos | El revisor contrasta entidades/rutas contra código Django sintético, propone documentos correctos y el producto los confirma sin modificar código |
| Perfil Python/Django declarado, D095 | `test_declared_profiles.py`: TOML, identidad congelada, cuarentena, dos preparaciones, seis validaciones y JUnit con herramientas falsas | Una tarea con herramientas Python reales y agentes reales llega a COMMITTED usando exclusivamente el perfil declarado en TOML, sin cambios del núcleo |
| Receta Django, D119 | P009, D139: creación, preparación, cuatro tareas, cuatro parejas, QA y cierre real | Ya acreditada. No se repite ni se usa como prueba del perfil declarado |

Referencias: [entrega D095](../archive/phase-008/P008-T008_PERFILES_DECLARATIVOS.md),
[revisión P008](../archive/phase-008/REVIEW.md), [piloto P009](../archive/phase-009/P009-T012_CIERRE_PILOTO.md),
[matriz P010](P010_MATRIZ_ACEPTACION.md). Los tests citados son evidencia ya registrada, no reejecutada en T008.

La propuesta reduce el coste a **dos repositorios sintéticos, una pareja de agentes y una tarea**. B y D095 se
comprueban en el mismo proyecto; no hace falta repetir la matriz de cuatro parejas. No certifica todos los
orígenes A ni proyectos Django arbitrarios, otras plataformas, aislamiento físico o calidad comparativa de modelos.
Chat, backup/restauración y receta TypeScript conservan su evidencia offline; no se incorporan implícitamente
a este recorrido. El wheel final y su verificación sintética siguen correspondiendo a T009.

## 2. Fixtures y resultados observables propuestos

**A — `import-a`.** Repositorio nuevo generado a mano con contenido ficticio tipo harness anterior: `PROJECT.md`,
`REQUIREMENTS.md`, `DECISSONS.md`, instrucciones breves, documentación/archivo de una fase anterior y una fase activa.
Sin `.harness/` operativo, runs, credenciales, remotos, submódulos, filtros ni datos de ReferenceProject. Inventario de
rutas/modos/SHA-256 y HEAD inicial antes de registrar. El revisor solo conversa sobre su exportación de HEAD;
se revisan los borradores, preguntas y mapa de conservación antes de confirmar el diff exacto. Resultado exigido:
documentos D088 coherentes, originales archivados por bytes, un único commit documental, fase activa adoptada y
reenvío de la misma confirmación sin segundo commit. No se ejecuta una tarea en A ni se ensaya la migración de runs
legacy D027/D099; ese límite se conserva expresamente.

**B — `onboarding-b`.** Repositorio nuevo Django mínimo, escrito con datos ficticios antes del inventario:
`manage.py`, `config/`, una aplicación con un modelo y su migración, una ruta/vista, tests pytest-django,
README y configuración de ruff/mypy/django-stubs. Sin documentos de harness, `.harness/`, remotos ni bases versionadas.
`.venv/`, `.local/`, bytecode y SQLite ignorados. Las seis validaciones deben pasar antes de registrar el proyecto;
se guardan HEAD y hashes de todo el código. No se clona, copia ni opera el hijo de P009, ni se activa una receta.

El inventario B debe citar el modelo, relación si existe, ruta y tests con procedencia; se revisan sus límites
estáticos. El revisor redacta los once documentos D088 y los flujos observados. Las decisiones inferidas se marcan
como tales; preguntas no deducibles pasan por HITL. El operador declara el perfil D095 en un TOML privado antes de
confirmar sus hashes y los documentos. Resultado exigido: un commit documental, código intacto por bytes y modos,
originales sustituidos conservados y P001 ACTIVE. Reenviar la confirmación no duplica efectos.

**Continuidad B/D095.** P001 contiene una única tarea acotada: añadir validación de entrada a la vista existente y
tests correspondientes, sin cambiar dependencias, herramientas, modelos ni migraciones. Su contrato congela las
rutas concretas al preparar el fixture. Planificación `agent`, revisión y COMMITTED mediante UI. Se contrastan las
dos preparaciones, seis validaciones, JUnit, diff aceptado y commit único. El perfil es
`[profiles.python-django]` del [ejemplo vigente](../../examples/local_config.example.toml), no el perfil construido
por la receta. No se añade formateador automático: el ejemplo solo autoriza `ruff format --check .`.
No se cierra la fase ni se planifica una sucesora; estos efectos no son necesarios para las tres afirmaciones.

## 3. Área, versiones y elecciones por confirmar si se ejecuta

Las rutas entre `<…>` son parámetros pendientes, no destinos elegidos. Nada se crea hasta resolverlos.

| Elemento | Propuesta concreta | Elección o comprobación pendiente |
|---|---|---|
| Área operativa | `<AREA>` nueva, privada y fuera de cualquier checkout; `dist/`, `venv/`, `config/`, `state/`, `tmp/`, `home-commands/` y `wheels/` | Ruta absoluta elegida por el usuario, inexistente y sin enlaces; no reutilizar el área de P009 |
| Repositorios | `<RAIZ>/import-a` y `<RAIZ>/onboarding-b`, nuevos y sin remotos | Raíz elegida por el usuario; destinos inexistentes; única raíz de registro |
| Distribución | Wheel desde un commit identificado con T012, assets y migraciones `0023`; instalarlo en `<AREA>/venv` | Commit final, SHA-256 de wheel/requirements y resultado de verificación; nunca importar producto desde el checkout |
| Construcción harness | Toolchain local fijada en el repositorio: Python 3.14.4, uv 0.12.19, Node 24.15.0 y npm 11.12.1 | Comprobar disponibilidad antes de ejecutar; una falta de caché no autoriza descarga |
| Django del fixture B | Propuesta: Python 3.13.13 y los 17 pins/hashes del lock empaquetado `django-requirements.lock`: Django 5.2.17, pytest 9.0.3, pytest-django 4.11.1, ruff 0.14.1, mypy 1.18.2, django-stubs 5.2.7 | Confirmar Python/uv, lock completo y wheelhouse propio; reutilizar los pins no activa la receta ni acredita su preparación |
| CLI y adaptador | `cli-13`; Codex lectura 0.161.0/0.162.1/0.163.0, escritura 0.162.1/0.163.0; Claude 2.1.295/2.1.296/2.1.304 en ambos roles | Usuario elige una pareja, rutas versionadas, modelo/esfuerzo del revisor y catálogo/esfuerzos del ejecutor; registrar hashes nuevos sin lanzar CLI en T008 |
| Política | `planning_mode = agent`, `executor_mode = catalog`, `max_revision_cycles = 2`; revisor 1800 s, ejecutor 3600 s | Confirmar pareja y catálogo; sin fallback ni actualización de CLI; versión no admitida obliga a tarea previa separada |
| Servicio | Un `serve` en `127.0.0.1:<PUERTO>`, `supervisor = true`; `TMPDIR=<AREA>/tmp` privado | Puerto concreto elegido y comprobado libre; no usar 8013/5173 ni puertos/servicios de P009 |
| Configuración | `local-config-5` privado, chmod 600; solo composición declarada Django y proyectos nuevos; `bootstrap_enabled = false` | Revisar TOML completo, ejecutables absolutos, entorno, autor Git e identidad congelada antes de encolar |

Las versiones de esta tabla son pins locales y baseline del producto, no una consulta de versiones actuales del
mercado ni una comprobación de lo instalado. Los modelos no se eligen por extrapolación del consentimiento de P009.
Agentes con el HOME de autenticación y USER verificado por UID según D119; memoria automática desactivada,
revisores de solo lectura y escritor contenido por su CLI. Comandos del perfil con HOME privado y
`PYTHONDONTWRITEBYTECODE=1`; Django solo usa bases de tests temporales. No hace falta `runserver` ni migrar una base
de uso. No se toca configuración global ni se concede Bash al escritor Claude.

## 4. Comandos, instalaciones y red propuestos

Guion revisable para una futura tarea; no ejecutado. Los comandos del perfil son argv sin shell y requieren
la composición confirmada. Rutas, entornos y hashes se completan antes de autorizar la operación.

1. Construir desde el checkout, sin operar el harness sobre él:
   `uv run --frozen --offline python scripts/build_distribution.py --out-dir <AREA>/dist` y
   `uv run --frozen --offline python scripts/check_distribution.py --dist <AREA>/dist`, con
   `UV_CACHE_DIR=.local/uv-cache`. El verificador levanta servicios temporales de loopback con CLI falsas;
   necesita autorización propia en la tarea operativa, o evidencia aplicable de T009 sobre idéntico wheel.
2. Crear `<AREA>/venv` con `uv venv --offline --no-python-downloads`; instalar `requirements.txt` mediante
   `uv pip sync --offline --require-hashes --python <AREA>/venv/bin/python …`, y el wheel mediante
   `uv pip install --offline --no-deps --python <AREA>/venv/bin/python <WHEEL>`.
3. Preparar B con venv Python 3.13 y `uv pip install --offline --no-index --find-links <AREA>/wheels --require-hashes
   --python <B>/.venv/bin/python -r <LOCK>`. Wheelhouse nuevo verificado contra el lock; no leer ni modificar el de P009.
   Si faltan wheels, parar: PyPI o cualquier instalación con red requieren una autorización adicional con lista/hash.
4. Generar fixtures y commits iniciales con Git local y autor confirmado. Ejecutar previamente en B los argv de
   D095 de la tabla siguiente. Guardar manifiesto de fuentes/hashes; no instalar desde scripts del proyecto.
5. Desde fuera del checkout, con la CLI instalada: `harness-local check-config <TOML> --preflight` (version/help,
   sin invocación de modelo), `harness-local init-db --database <AREA>/state/harness.sqlite3` y
   `harness-local serve --database <AREA>/state/harness.sqlite3 --config <TOML> --port <PUERTO>`.
6. Registrar A/B, conversar, revisar borradores y confirmar importación/perfil desde UI con CAS/hash y motivos.
   En B encolar solo la tarea descrita en §2; aceptar y confirmar su commit desde la UI. No editar SQLite/TOML
   para desbloquear, ni corregir a mano el resultado de los agentes durante el recorrido.

| Tipo | argv del perfil declarado | Timeout |
|---|---|---|
| Preparación | `python --version`; `python -m django --version` | 30 s cada uno |
| Validación/JUnit | `pytest --junitxml=.local/junit.xml -q` | 900 s |
| Validación | `ruff check .`; `ruff format --check .` | 120 s cada uno |
| Validación | `mypy .` | 600 s |
| Validación | `python manage.py check` | 120 s |
| Validación | `python manage.py makemigrations --check --dry-run --noinput` | 120 s |

`authorize_profile_commands = true` solo cubre esos comandos exactos; instalaciones y generación del fixture son
operaciones separadas del operador. Red propuesta: únicamente tráfico de las CLI elegidas con sus proveedores.
Sin red en preparación, validadores, Git, construcción o instalación; caché incompleta obliga a parar. No hay
push, publicación, cambio de versión, actualización global, navegación remota ni nuevos proyectos fuera de §3.

## 5. Consumo, parada, recuperación y evidencia

| Tramo | Máximo propuesto de invocaciones a modelos |
|---|---|
| A: conversación de importación | 6 turnos de revisor |
| B: conversación de incorporación | 8 turnos de revisor |
| Tarea B | 7: 1 plan + 3 ejecuciones + 3 revisiones |
| Total | **21**, sin reserva ni relanzamientos |

El límite cuenta llamadas fallidas y las de selección si el recorrido concreto las requiere; antes de operar se
contrasta ese presupuesto con la política congelada. No se realizan llamadas adicionales al agotarlo. Techo de
sesión propuesto: 4 horas de pared; al alcanzarlo no se inicia otra llamada y se solicita parada del trabajo activo.
El producto no impone un presupuesto monetario/token estricto sobre el proveedor; si el usuario necesita uno se
debe fijar y verificar el mecanismo antes de autorizar. Los retries internos de la CLI no son invocaciones
adicionales observables por el harness y no se promete controlarlos (D019).

Parada al primer fallo de proveedor/esquema/timeout, validación, permisos, revisión REVISE o bloqueo de entorno,
CAS, hashes, base, destinos o cuarentena. El techo de dos correcciones es defensivo: no concede relanzar tras esta
parada. Preguntas normales de definición se resuelven por HITL dentro de sus turnos; un defecto del producto se
acota aparte antes de continuar. Sin fallback de modelo, actualización de CLI, privilegios o ampliación de rutas.

Tras caída: conservar intención, streams, HEAD y diff; confirmar procesos/grupos detenidos desde los mecanismos
del producto. Conciliar solo un commit ya sellado si no requiere invocar de nuevo y mantiene la autorización;
una recuperación que repita llamadas o cambie composición exige consentimiento nuevo. No restaurar automáticamente,
editar historiales o retirar cambios del fixture para aparentar éxito. No forzar caídas en esta validación real:
sus garantías ya están cubiertas sintéticamente.

Al terminar o parar: detener servicio y grupos, comprobar ausencia de locks/jobs activos con el servicio parado;
conservar fixtures y área privados para revisión. Solo borrar exportaciones/temporales propios cuya limpieza haga
el producto. Borrar repositorios, venv o área persistente exige una petición posterior; no hay limpieza destructiva
implícita. La inspección de SQLite se hace con servicio detenido o sobre copia, no concurrentemente con `serve`.

Evidencia pública en `docs/phase`: commit de producto, hashes de wheel/lock/TOML sin valores de entorno, versiones
y hashes CLI, plataforma, fuentes sintéticas y manifiestos, ids abreviados, número de llamadas, comandos/resultados,
JUnit resumido, hashes de originales conservados y código B, commits de importación/tarea y resultado de parada.
Streams, tokens de sesión, credenciales, prompts completos y SQLite permanecen privados fuera del repositorio.
Un resultado parcial identifica qué afirmación se acreditó y cuál sigue pendiente; nunca se resume como aprobado total.

## 6. Decisión HITL y alcance anunciado

El 2026-10-22 el usuario elige expresamente **«Aplazar y conservar los límites de validación real»**, conforme a
D141 y al contrato T008. Se aplazan A, B y la comprobación real del perfil declarado D095. T008 queda completa;
T009 es la siguiente tarea, con dictamen aún pendiente. No se añade T013 ni se autoriza la operación de §§2–5.

Las alternativas presentadas fueron:

- **Aplazar los tres recorridos.** T008 queda completa con esta propuesta; T009 puede revisar el paquete en el
  alcance offline. A/B y perfil declarado se anuncian como implementados y verificados con datos/agentes sintéticos,
  sin uso real; la receta Django conserva exclusivamente su evidencia histórica. Chat, backup y receta TypeScript
  siguen con los límites de §1. No se añade tarea operativa ni se presume autorización futura.
- **Ejecutar posteriormente A + B/D095.** Completar en HITL las elecciones de §3 y confirmar §§2–5; añadir una
  P010-T013 operativa, acotada y autorizada, previa al dictamen T009, sin ejecutar el recorrido en T008. Su resultado
  conserva evidencias parciales y límites. Elegir ejecutar sin completar parámetros no autoriza iniciar efectos.

El alcance que puede anunciarse conserva A/B y D095 como implementados y verificados offline con agentes y
herramientas falsos, sin validación real. La receta Django conserva la evidencia histórica de D139, limitada a
macOS arm64/Python 3.13. Chat, backup/restauración y receta TypeScript siguen sin uso real. Esta decisión no
convierte la evidencia sintética en evidencia real ni anticipa el dictamen final de T009 o el cierre T010.
Los parámetros de §3 quedan sin elegir porque no se ejecutará el recorrido; una operación futura requerirá
otra tarea y consentimiento específico. No se reutilizan los consentimientos agotados de P009.

## 7. Comprobaciones de T008

| Comprobación | Resultado |
|---|---|
| Contraste estático de propuesta, D095/D119/D139, contratos A/B y matriz | Evidencia real, sintética y propuesta diferenciadas; decisión HITL registrada en D151 |
| Parsers puros `parse_roadmap`, `plan_tasks`, `decision_index` | 10 fases, 7 criterios de P010, 12 tareas y 151 decisiones |
| Enlaces/anclas relativos de los siete documentos tocados | 452 comprobados, sin rotos |
| Presupuestos | STATE 11.521/24.576 bytes, base acumulada 5.801/12.288 y NEXT_STEPS 23.743/49.152 |
| Conservación respecto a `dd7b958` | Cuerpos D001–D150, ROADMAP P001–P009, dictamen original de la matriz y archivos de fases cerradas intactos |
| Diff documental y `git diff --check` | Revisados, sin errores de espacios |

No se ejecutan pytest, unittest, Node, tipos/build o Alembic: solo cambian documentos, sin código, esquema, API,
flujos ni UI. No se ejecutan los comandos de §§2–5 ni se inspecciona la instalación operativa.
