# P012-T004 — Propuesta de creación TypeScript v2 con base independiente

Fecha: **2026-10-26**. **Estado: preparada y contrastada offline; ejecución sin autorizar.**
Base documental: **`7450c0f`**. Producto conservado: **`f94842980235d1801e6a99505bffd329f63e1f85`**,
instalado y verificado en T003/UI como T012. Decisión: [D205](../DECISIONS.md#d205--p012-t004-propuesta-con-base-independiente-y-sucesora-vacía).
Precedentes: [T001 §§5–7](P012-T001_PROPUESTA_OPERATIVA.md#5-fixtures-y-recorridos-observables),
[resultado T003/UI](P012-T003_UI_RESULTADO_T012.md), D059/D091/D143/D168/D192/D199/D204.

## 1. Aislamiento del arranque y alcance elegido por HITL

D199 exige conservar la tarea de chat P001-T002/run `d235e9d5…` **QUEUED**, sin ejecutarla. El supervisor
consume la cola de la base que se le entrega; ni omitir el proyecto del TOML ni cambiar de puerto garantiza
preservar ese job. Se propone una **base nueva**, inicializada por `init-db`, con su propio `state_dir` y sin
registros importados. La base anterior y sus copias no se abren con el servicio ni se migran, cancelan o clonan.
El supervisor de T004 solo tendrá los jobs del nuevo hijo. Es una operación soportada, sin cambiar el diseño
del producto: `launcher.initialize`, `ManagedRuntime` y el test de dos instalaciones independientes.

Se detecta otra ambigüedad: T004 pedía «planificación confirmada de la siguiente fase sin tareas».
SPECIFICATION §7 y el flujo de fase separan la creación automática de la sucesora vacía del plan posterior,
que exige al menos una tarea (`definition.validate_plan`, `PhasePlanRepository.preview`). Consultado el usuario,
elige: **«Confirmar P002 en ROADMAP durante la definición y terminar con P002 ACTIVE vacía tras el cierre
(recomendado).»** Se confirma su objetivo y criterios en el ROADMAP del bootstrap; el cierre crea P002 con
NEXT_STEPS pendiente de planificación. No se solicita después una conversación ni confirmación de plan P002.
La elección aclara el alcance; **no autoriza servicio, instalación, preparación o proveedores**.

## 2. Entradas conservadas y comprobaciones de solo lectura

`AREA=$HOME/Documents/harness-validation/p012-20261024`.

| Entrada bajo AREA | SHA-256 comprobado |
|---|---|
| `dist-t012/harness_local-0.1.0-py3-none-any.whl` | `730891f8de5b68b9279e6d8a96a7066a3dd3e1ba9c5b64c5336e2f4814f41520` |
| `dist-t012/SHA256SUMS` | `c5d0194a052f8f9d92c2cd8674238c5513a9f9e6aa932811b7fa81a09bcb43be` |
| `state/harness.sqlite3` | `187614a9ea361e1f96a45f55240f55a20e4b3138dab2bdd47a1e3fe280675cfc` |
| `backups/t003/state.sqlite3` | `b35c4114734da72e25c12a57e01f0f350d6676608eac84c1b4a3d768072e7d15` |
| `restored/t003/state.sqlite3` | `1a1506ff90c2f451ef0bb467a8b520149265c8e516ca6e42088d256300d4b4b8` |
| `config/harness-local-t010.toml` | `e0e95abb9055f1c9f985c82285bc3c7b551f6503ff6bddb5aff7ddf282fbb6db` |
| `config/harness-local-t003-paused.toml` | `d41f9375e47baf87bd45d77269d5d583c46b6933b2d5004bd8737408d8becd08` |

Los **259 archivos instalados** de `venv-t012` coinciden por bytes con el wheel; sus fuentes locales coinciden.
Los siete hashes pertinentes de T001 (Python 3.14, uv, Node, npm, Claude, lanzador y nativo Codex) coinciden
sin ejecutar las herramientas. Se mantienen las versiones previstas **Claude 2.1.310 / Codex 0.164.0**,
Python **3.14.4**, uv **0.12.19**, Node **24.15.0** y npm **11.12.1**; el preflight real queda pendiente.

La base anterior, abierta en solo lectura sin `immutable=1`, pasa integridad/FK y conserva esquema
**0025_project_work_languages**, **52 tablas con alembic_version**, **16.798 filas**, **13 jobs DONE/1 QUEUED**
y **cero locks**. WAL observado vacío y SHM existente; no se borran ni se ignoran para comparar datos.
Los **14 procesos STOPPED** y la identidad histórica **unknown** mantienen la procedencia D204: aquí no se
repite su certificación ni se extiende la excepción de consulta a ejecutar sobre esa base.
Puertos **8024/8025 sin listener**; área y padres comprobados canónicos y fuera de checkouts.

La caché privada `npm-cache/` está vacía. El objeto exacto de **typescript@5.9.3** existe en
`REPO/.local/npm-cache/_cacache/content-v2/sha512/`, donde
`REPO=$HOME/Documents/projects/my_harness`. Leídos **4.377.468 bytes**, integridad SHA-512 idéntica al
lock de `recipes/typescript_web_2.py`:

```text
sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==
```

SHA-256 **`10e108c9cf7d5f2879053dff18515fb405abf2ccef63eaaf017d9c571687a1d3`**. Bajo consentimiento se
copiará **solo ese objeto**, en la misma ruta relativa por digest, a `npm-cache-t004/` nuevo. Sin índices,
metadatos, npmrc, tokens o cachés de otros paquetes. El lock ya sella URL e integridad; la comprobación de bytes
no acredita todavía que `npm ci --offline` vaya a pasar: eso lo prueba la preparación real. Si pide cualquier
objeto adicional, parar y listar faltantes, sin descargar ni completar la caché de forma implícita.

## 3. Destinos y configuración exacta propuesta

| Destino nuevo bajo AREA | Efecto autorizado solo tras consentimiento |
|---|---|
| `state-t004/harness.sqlite3` | Base independiente, vacía de jobs anteriores; inicialización exclusiva |
| `state-t004/` | Artefactos del producto y evidencia privada `operator/` propia |
| `config/harness-local-t004.toml` | TOML nuevo 0600, contenido literal siguiente |
| `config/t004-user.npmrc`, `config/t004-global.npmrc` | Dos archivos nuevos, distintos y vacíos, 0600 |
| `npm-cache-t004/` | Caché nueva con el único objeto acreditado; escrituras normales de npm en T004 |
| `command-home-t004/`, `tmp/t004/` | HOME de comandos y temporales/evidencia del servicio, 0700 |
| `projects/typescript-es/` | Hijo nuevo, creado exclusivamente por UI; id `p012-typescript-es` |

Se ha comprobado ausencia de state-t004, TOML, hijo, HOME, caché y tmp/t004; antes de operar se repite además
la ausencia de ambos npmrc y de auxiliares de la base. No se sustituyen destinos existentes. Conservar instalación
T012: **sin build, verificador del paquete, instalación o migración nuevos**. El puerto operativo sigue siendo
**127.0.0.1:8024**, con 8025 cerrado; no cambiarlo automáticamente si está ocupado.

TOML completo; no hay variables por expandir en su contenido. Mantiene los defaults Claude/Codex y la receta de
T001, con catálogo limitado en la política del hijo; no incorpora los perfiles/presets/composiciones Django.
`state_dir`, caché y entorno de comandos son propios. El ejecutor recibe Node en PATH y TMPDIR dentro del hijo,
según el precedente D192; no necesita el venv Django. Ese temporal se crea **después** de la preparación y
**antes** de encolar la tarea, bajo `.local/` ya ignorada, sin editar archivos versionados o ampliar writable_roots.
El revisor conserva el entorno de T001; las recetas fijan su propio HOME/TMPDIR bajo `.harness-preparation`.

```toml
format = "local-config-8"

[service]
state_dir = "$HOME/Documents/harness-validation/p012-20261024/state-t004"
supervisor = true

[git]
executable = "/usr/bin/git"
author_name = "P012 Synthetic Operator"
author_email = "p012@example.invalid"

[agents.reviewer]
provider = "claude"
model = "sonnet"
effort = "low"
executable = ["$HOME/.local/bin/claude"]
timeout_seconds = 1800
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.local/bin:$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", LANG = "C.UTF-8", PYTHONDONTWRITEBYTECODE = "1" }

[agents.executor]
provider = "codex"
executable = ["$HOME/.nvm/versions/node/v24.15.0/bin/codex"]
timeout_seconds = 3600
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", TMPDIR = "$HOME/Documents/harness-validation/p012-20261024/projects/typescript-es/.local/codex-tmp", LANG = "C.UTF-8", PYTHONDONTWRITEBYTECODE = "1" }

[registration]
roots = ["$HOME/Documents/harness-validation/p012-20261024/projects"]
bootstrap_enabled = true

[recipes.typescript-web]
node_executable = "$HOME/.nvm/versions/node/v24.15.0/bin/node"
node_version = "24.15.0"
npm_executable = "$HOME/.nvm/versions/node/v24.15.0/bin/npm"
npm_version = "11.12.1"
npm_cache = "$HOME/Documents/harness-validation/p012-20261024/npm-cache-t004"
allow_network = false
timeout_seconds = 120
max_output_bytes = 65536

[compositions.typescript]
profile = "typescript-web"
recipe = "typescript-web"
authorize_profile_commands = true
executables = { node = "$HOME/.nvm/versions/node/v24.15.0/bin/node", npm = "$HOME/.nvm/versions/node/v24.15.0/bin/npm" }
environment = { HOME = "$HOME/Documents/harness-validation/p012-20261024/command-home-t004", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", TMPDIR = "$HOME/Documents/harness-validation/p012-20261024/tmp/t004", LANG = "C.UTF-8", CI = "true", npm_config_cache = "$HOME/Documents/harness-validation/p012-20261024/npm-cache-t004", npm_config_userconfig = "$HOME/Documents/harness-validation/p012-20261024/config/t004-user.npmrc", npm_config_globalconfig = "$HOME/Documents/harness-validation/p012-20261024/config/t004-global.npmrc", npm_config_update_notifier = "false" }
```

Guardar el bloque literalmente con salto final, revisar parseo/semántica y registrar su SHA-256 antes de usarlo.
SHA-256 del bloque UTF-8 con salto final:
**`3b9f433d2c3f27a34bfd8cb02c5e29a800224a0498721a99e3bd2a2ad46a8d95`**.
No sobrescribir ni transformar los TOML anteriores. `check-config --preflight` debe acreditar solo esta pareja,
sin los presets de otros tramos. No requiere crear de antemano el hijo o el TMPDIR del escritor; si una CLI los
exigiera para version/help, parar antes de proveedores, sin crearlos fuera de la secuencia de creación.

## 4. Preparación y servicio propuestos, todavía sin ejecutar

Repetir hashes de §2, coincidencia de 259 archivos instalados, fuentes T012 y toolchain; comprobar destinos,
ancestros sin enlaces/checkouts y puertos. Conservar manifiestos por bytes/modos de B/B2/clon, diffs,
configuraciones/distribuciones y bases/artefactos anteriores. Guardar evidencia nueva solo en state-t004/operator
y tmp/t004. Las lecturas anteriores de bases se comparan sin convertir `unknown` en `dead` ni señalar procesos
históricos; una actividad local inesperada, WAL con datos nuevos o deriva obliga a parar.

Crear exclusivamente los directorios/archivos de §3 con `umask 077`, modos 0700/0600 y creación exclusiva;
copiar el objeto npm por digest, contrastar integridad y hash. Nunca crear el hijo manualmente. Desde AREA,
con PATH explícito de venv-t012/Node/uv y `/usr/bin:/bin`, HOME command-home-t004, TMPDIR tmp/t004,
PYTHONNOUSERSITE=1, PYTHONDONTWRITEBYTECODE=1 y LANG=C.UTF-8, sin PYTHONPATH o configuración ambiental:

```sh
"$AREA/venv-t012/bin/harness-local" check-config "$AREA/config/harness-local-t004.toml" --preflight
"$AREA/venv-t012/bin/harness-local" init-db --database "$AREA/state-t004/harness.sqlite3"
"$AREA/venv-t012/bin/harness-local" serve --database "$AREA/state-t004/harness.sqlite3" --config "$AREA/config/harness-local-t004.toml" --port 8024
```

Ejecutar por etapas: antes de `serve`, comprobar esquema 0025, base operativa sin marca de consulta y cero
jobs/procesos/locks/proyectos. No copiar tablas ni datos de T003. No ejecutar scripts/dev, migrate o init-db sobre
una base existente. CLI version/help no son llamadas de modelos. Las guardias por intento/antes de GO se conservan.

## 5. Recorrido UI y evidencia de aceptación

Login en Chrome mediante la barra nativa, clave privada directa al formulario sin imprimir ni guardar.
Idioma visual **es** y trabajo **es**. Si aparece origin_rejected u otro fallo de guardia, parar, sin cambiar
Host/Origin/CSRF. Verificar que el servicio usa la nueva base, sin proyectos previos.

1. Elegir padre **AREA/projects** desde UI y confirmar su preview/hash/versión. Crear carpeta **typescript-es**,
   id **p012-typescript-es**, composición **typescript**, bootstrap habilitado y confianza explícita en el fixture
   sintético. Heredar exactamente los defaults declarados, sin presets Django. Política: planning_mode **agent**,
   executor_mode **catalog**, único **gpt-6-luna/low**, **max_revision_cycles=0**; revisor **sonnet/low**.
2. Conversación de definición real con Claude; hasta seis turnos normales dentro del techo. Brief: página estática
   del scaffold empaquetado, función `heading`, sin servicios, dependencias nuevas o datos privados. Proponer los
   documentos D088 en español, flujo **docs/flows/titulo.md**, P001 con una única **P001-T001** y P002 en ROADMAP.
   P001 acredita normalización, conservación de API/defecto/sufijo, validaciones y paridad del flujo; el cierre se
   comprueba después de READY, sin usarlo como criterio circular. P002 reserva la evolución posterior con objetivo
   y criterios, sin tareas ni compromiso de ejecutarlos en este tramo. Resolver preguntas no deducibles por HITL.
   Aplicar borradores CAS, revisar contenido completo, límites AGENTS/CLAUDE/GEMINI, índice de decisiones y
   separación de datos frente a flujo; confirmar el hash de la definición y el commit documental raíz por UI.
3. Preparación: preview/confirmación **offline**, **typescript-web-recipe-2**, trabajo **es** y hash de idioma/receta
   sellados. Revisar los nueve archivos del manifiesto y pasos/argv. `npm ci --offline --ignore-scripts --no-audit
   --no-fund`, versiones exactas, check/test/build y JUnit; commit técnico separado y recibo COMPLETED con esos
   hashes. No atribuir red al mero campo resolved del lock. Parar ante falta de caché o cualquier fallo.
4. Crear únicamente el temporal ignorado **.local/codex-tmp/** del escritor, modo 0700; comprobar su resolución,
   ignorado y limpieza Git, sin modificar manifest/recibo. Seleccionar **P001-T001** del NEXT_STEPS por CAS:
   normalizar secuencias de espacios interiores a uno en `heading`, conservando trim exterior, API exportada,
   defecto `Proyecto` y sufijo ` preparado`. Solo **src/main.ts** y **docs/flows/titulo.md**. Sin editar tests,
   scripts, configuración o dependencias; la suite existente prueba título normal/vacío, sin presentarla como
   cobertura nueva de espacios interiores. Contrastar el diff exacto de la transformación y la explicación del flujo.
   Plan Claude → **una ejecución Codex** → tres validaciones/JUnit → revisión Claude → aceptación exacta/COMMITTED.
   El perfil v2 no declara formateador. No añadirlo ni traducir API/protocolos; comentarios/documentos nuevos en es.
5. Con tarea COMMITTED, checkout limpio y sin trabajo pendiente, solicitar check de P001: validación de base y
   evaluación Claude. Solo **READY** vigente permite confirmar el cierre con su hash/vínculo y motivo por UI.
   Autorizar **solo el tag p001 del hijo** sobre el HEAD evaluado y el commit de archivo: SUMMARY/REVIEW,
   STATE/NEXT_STEPS y docs/phase originales por bytes, ROADMAP actualizado. Comprobar **P001 CLOSED** y
   **P002 ACTIVE con cero tareas**, conforme al HITL de §1; no pulsar planificación, lote o ejecución de P002.
6. Registrar ids abreviados, versión/CLI/modelo reportado frente a solicitado, hashes de definición/plan/recibo,
   diff aceptado, commit documental/técnico/tarea/archivo, tag, JUnit, READY y consumos por proveedor.
   Estado funcional y resultados acreditados solo cuando existan. Detener y conservar según §6.

## 6. Presupuesto, parada y consentimiento solicitado

Techo propio T004: **12 Claude / 3 Codex**, **cuatro horas** desde la preparación operativa. Solo **una ejecución
normal Codex**, cero correcciones/reintentos: la reserva restante no permite otra ejecución tras fallo.
Previsión Claude: hasta seis turnos de definición, plan y revisión, READY y hasta tres aclaraciones dentro del
mismo recorrido. No se consume una llamada para planificar P002. Registrar contadores antes/después; no
traspasar los saldos T002 (**9/12 y 3/3**) o T003 (**2/3 y 0/0**), ni reponer tiempo tras una parada.

Primer fallo de proveedor/auth/esquema/timeout, validación/REVISE/BLOCKED, permisos, CAS/hash, caché,
cuarentena o destino → parar, conservar evidencia y pedir consentimiento nuevo antes de reanudar. El motor puede
sellar evidencia de la validación/revisión ya iniciada; no se abre otro ciclo ni se repara a mano. Sin fallback,
cambios globales, red de paquetes, edición SQLite, concesión de /tmp o ampliación de modelos/permisos.
La única red contemplada es la de las CLI con sus proveedores bajo el consentimiento solicitado.

Al terminar o parar: detener servicio y grupos propios por identidad viva, puerto cerrado/clave retirada,
jobs/preparaciones terminales, procesos STOPPED y cero locks, o declarar reservas inciertas. Verificar conservación
de las bases/filas/artefactos/TOML/distribuciones y tres fixtures anteriores, con el job de chat QUEUED sin cambios.
La incertidumbre histórica D204 se conserva; no certificar muerte ni reactivar su base. Mantener el hijo/base
nuevos y el área para revisión. Evidencia completa privada; informe saneado futuro en
**docs/phase/P012-T004_TYPESCRIPT_REAL.md**.

**Consentimiento pendiente:** autorizar este guion completo: base/state/TOML/caché/entornos nuevos, copia local
del único objeto npm, reutilización de venv-t012, preflight/init-db exclusivo/servicio/UI en 8024, creación,
definición, receta offline, una tarea, READY y cierre/tag/archivo **del hijo**, final con P002 ACTIVE vacía;
máximo **12 Claude/3 Codex**, una ejecución normal, cero correcciones, cuatro horas y parada al primer fallo.
La petición genérica de continuar y hacer commit autoriza esta preparación documental. **AGENTS** prohíbe
«lanzar agentes, proveedores, smokes […] sin autorización explícita» y **T001 §7** exige «T003 y T004 requieren
su propia autorización posterior». Por eso se solicita respuesta específica antes de efectos reales.
Sin build/instalación nuevos, operación de la base anterior, T005, tags en my_harness, push o publicación.

## 7. Validación de esta propuesta

Contraste con SPECIFICATION §§5–7, ARCHITECTURE §9, diagrama de datos y flujos de creación, definición,
preparación y fase; lectura del código de configuración, inicialización, runtime, receta y planificación.
Solo datos sintéticos en las pruebas; las lecturas privadas de §2 no se incorporan como fixtures.

**Cinco tests existentes correctos** (pytest offline, `-n 0`): instalaciones con autoridad independiente;
preparación v2 TypeScript/es con recibo y commit; elección v1/v2 en v5–v8 para ambas recetas; cierre exacto
con tag/archivo y sucesora sin plan. Un aviso ya existente de Starlette/httpx. No se escriben tests nuevos ni
se repiten suites completas, frontend/build o Alembic: no cambia producto, API, modelos, migraciones o flujos.
La carga semántica del TOML se contrasta con rutas equivalentes sintéticas, sin escribirlo en el área operativa.
Comando de los cinco tests (incluye las dos parametrizaciones de selección de receta):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0 \
  tests/product/test_project_creation.py::test_two_installations_keep_independent_root_selection \
  'tests/product/test_recipe_v2_preparation.py::test_v6_child_prepares_with_its_work_language_and_commits_the_v2_manifest[typescript-es]' \
  tests/product/test_recipe_v2_preparation.py::test_v5_keeps_v1_and_successors_select_v2_from_the_same_recipe_keys \
  tests/product/test_phase_closure.py::test_unified_closure_exact_archive_and_successor_without_plan
```

Parsers puros: **12 fases, 7 criterios P012, 12 tareas y 205 decisiones**. **649 enlaces/anclas** relativos
correctos en los cinco Markdown de esta entrega. Presupuestos STATE/base/NEXT_STEPS:
**19.246/24.576**, **9.171/12.288**, **36.098/49.152 bytes**. Cuerpos D001–D204, informes congelados,
producto y baseline pública intactos; tres hashes SQLite conservados después de las lecturas.
Diff revisado y `git diff --check` correcto.
Sin construir/instalar, ejecutar CLI/proveedores reales, servicio, npm, validadores del hijo o escritura operativa.
T004 permanece pendiente hasta autorización y evidencia real; esta propuesta no acredita sus criterios.
