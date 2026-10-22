# P010-T002 — Arranque confirmado de un proyecto TypeScript web

Fecha: 2026-10-22. Base: `9550000`. Decisión:
[D143](../DECISIONS.md#d143--p010-t002-receta-typescript-web-recipe-1-implementada).
**Estado: implementado y verificado offline** con node/npm sintéticos y, como variante opcional, con node 24.15.0 y
npm 11.12.1 reales sobre la caché local ya poblada `.local/npm-cache`, sin red. Implementa el
[contrato de T001 §1](P010-T001_CONTRATO_CONSOLIDACION.md#1-arranque-de-un-proyecto-typescript-web-nuevo-t002)
dentro del marco D119 (D142). Sin proveedores, smokes, servicios ni instalaciones globales.

## 1. Qué se entrega

Un hijo `typescript-web` creado por el servicio obtiene, tras su commit documental D088, un manifiesto inicial
utilizable mediante una segunda receta empaquetada, `typescript-web-recipe-1`. La primera tarea se ejecuta con
las validaciones del perfil `typescript-web` sin que el ejecutor normal escriba archivos protegidos.

| Pieza | Cambio |
|---|---|
| `recipes/typescript_web.py` (nuevo) | Manifiesto, pasos y huella. `package.json` con el id del proyecto como nombre, `private`, `"type": "module"`, `engines` exactos de la receta, scripts `check`/`test`/`build` y `typescript@5.9.3`; lock v3 con la entrada de TypeScript del fixture (`resolved` e `integrity`), `tsconfig.json`, `.gitignore`, `scripts/test.mjs` (JUnit en `.local/junit.xml`), `scripts/build.mjs`, `index.html`, `src/main.ts` y `tests/main.test.mjs`. |
| `recipes/__init__.py` | Registro nombre → módulo y perfil exigido. `recipes/django.py` no cambia: su texto forma parte de la huella de los recibos emitidos. |
| `services/local_config.py` | `[recipes.typescript-web]` en `local-config-5` (ejecutables absolutos sin shells, versiones exactas, `npm_cache` canónico fuera del estado, timeout 120–1800, salida 1024–1048576, `allow_network`). La composición con `recipe = "typescript-web"` exige el perfil integrado, `node`/`npm` que resuelvan a los archivos de la receta y `npm_config_cache` igual a `npm_cache` en su entorno, que no se reescribe; la caché debe quedar fuera del checkout. `project_recipe` y `recipe_config_sha256` por receta. |
| `services/project_preparation.py` | Núcleo común (CAS, intención, pasos, lease, journal, commit, recuperación) y una clase por receta: manifiesto, destinos, plan específico, reglas de enlaces y fuente, comprobación de salida, JUnit del perfil y recibo. El plan Django conserva claves y valores. |
| `adapters/preparation.py`, `storage/preparation.py` | El recibo TypeScript verifica identidad, archivos protegidos y `node`/`npm` por hash; no congela `node_modules`. Mensajes `preparation_required` genéricos. |
| UI (`preparation.ts`, `Preparation.tsx`, `shared.tsx`, `Planning.tsx`) | Títulos, estados, modos y avisos según la receta congelada; misma vista previa, confirmación y journal. |
| `examples/typescript-web-recipe.example.toml` (nuevo) | Fragmento v5 de receta y composición, con test de claves. |
| `docs/flows/project-preparation.md` | Flujo con ambas recetas. |

Sin migración ni tablas nuevas (`0022` intacta, DDBB-DIAGRAM sin cambios). Sin cambios de API: `PreparationPlanRead`
ya admitía planes por receta (`extra='allow'`), por lo que no se regeneran OpenAPI ni tipos.

## 2. Pasos, red y recibo

1. `files`: crea `.harness-preparation/{home,tmp}`, dos npmrc vacíos y escribe el manifiesto completo.
2. `node --version` = `v<node_version>`; 3. `npm --version` = `<npm_version>`.
4. `npm ci --ignore-scripts --no-audit --no-fund`, más `--offline` en modo offline.
5–7. `npm run check`, `npm run test` (JUnit completo, con casos correctos y sin fallos) y `npm run build`.
8. Commit «harness: prepare TypeScript web (typescript-web-recipe-1)» con exactamente el manifiesto.

Entorno de los pasos: `HOME`/`TMPDIR` dentro de `.harness-preparation/`, `PATH` con el directorio de `node`,
`npm_config_cache`, `engine-strict`, registro `https://registry.npmjs.org/`, `fetch-retries=0` y
`npm_config_userconfig`/`npm_config_globalconfig` en dos archivos vacíos del hijo. **Hallazgo:** npm 11.12.1 rechaza
el mismo archivo para ambos («double-loading config … as "global", previously loaded as "user"»), así que el
contrato de «una configuración de usuario vacía» se concreta en dos archivos vacíos.

Offline usa solo la caché declarada y un fallo no cambia a red. Network exige `allow_network` y elegirlo en la vista
previa, que muestra registro, caché y el aviso de que la red escribe en ella. Confirmar documentos no concede
instalar: la preparación tiene su propia vista previa y confirmación (D116).

Recibo: contrato, receta, identidad, `recipe_config_sha256`, configuración, hash del lock, commit, operación,
`tools` (`node`/`npm` resueltos con hash) y los archivos del manifiesto que casan con `protected_paths` del perfil
con la misma semántica glob (`package.json`, `package-lock.json`, `tsconfig.json`, `.gitignore`, `scripts/**`,
`tests/**`). `index.html` y `src/main.ts` quedan para el ejecutor. `PreparedCommandRunner` y `admit` verifican el
recibo antes de tareas, checks y cada comando.

## 3. Recuperación

Se aplican sin excepciones las reglas D119. **Comprobado con npm real:** con caché vacía, `npm ci --offline` falla
con `ENOTCACHED` sin crear `node_modules/`, así que un fallo offline corriente admite una nueva intención enlazada
desde el mismo paso y no hizo falta relajar la regla (contrato §1.5). Bytes parciales en `node_modules/` o un
`npm ci` ejecutado sin checkpoint bloquean con `recovery_required` y no se borran. Un fallo del primer paso solo se
reintenta si el checkout sigue igual que el inicial. Una caída tras el commit concilia el mismo hash sin repetir
comandos. Destinos existentes, enlaces, destinos ignorados, archivos ajenos y deriva bloquean con diagnóstico.

## 4. Verificación

`tests/product/test_typescript_preparation.py` (40 casos) y `typescript_preparation_probe.py` (node/npm sintéticos con
caché sintética y marcadores de fallo):

- Vista previa exacta, idempotente y de solo lectura; lock idéntico al del fixture; red rechazada sin techo.
- Commit técnico, recibo (sin entorno congelado), reinicio, borrado de `node_modules` admitido y deriva del
  manifiesto o de `npm` que bloquea recibo, admisión y comandos nativos.
- Caché vacía offline: fallo sin red ni `node_modules`, sucesor explícito que completa sin repetir pasos.
- Instalación parcial y `npm ci` sin checkpoint: sin reintento ni borrado. Interrupción antes de cada comando
  (seis casos) y del paso de archivos; escritura parcial no adoptada; conciliación del commit tras la caída.
- Código ajeno antes de los comandos y JUnit con fallo tras salida 0: sin commit.
- Destinos existentes o enlazados (cinco), destino ignorado, hijo sin procedencia de creación, red con techo y
  elección, API estricta con la receta expuesta, diez configuraciones inválidas, caché dentro del checkout,
  coexistencia de ambas recetas con la huella Django fijada y fragmento de ejemplo.
- Recorrido por la API con CLI falsas: carpeta → creación → definición → tarea rechazada por `preparation_required` →
  preparación → P001-T001 con `node`/`npm --version`, `npm ci --offline` y `npm run check/test/build` del perfil →
  ACCEPTANCE_READY → COMMITTED. El commit de la tarea solo cambia `src/main.ts` y los bloques D088.
  Variante real opt-in (`HARNESS_TEST_TYPESCRIPT_NPM_CACHE`), ejecutada en esta tarea con `.local/npm-cache`:
  `tsc`, tests Node con JUnit y build reales, offline.

Regresiones y comprobaciones: ver §6.

## 5. Límites y observaciones

- El manifiesto queda fijo tras preparar (D119): añadir dependencias requiere un flujo confirmado futuro, fuera de
  P010; T006 lo documenta. `tests/**` sigue protegido por el perfil frente al ejecutor (P007); T007 lo registra.
- Cambiar TypeScript o el contenido empaquetado exige una receta nueva y deja en cuarentena jobs previos por
  `recipe_config_sha256`.
- La variante real depende de la caché local preexistente y de node/npm de este equipo (macOS arm64); no es
  evidencia con proveedores ni de otras plataformas. La caché puede recibir los registros (`_logs`) de npm.
- Las altas e importaciones A/B no son elegibles y conservan su comportamiento.

## 6. Comprobaciones ejecutadas

Sobre el árbol de trabajo de esta tarea (base `9550000`), el 2026-10-22:

- `pytest -q` completa (xdist): 1636 passed, 2 skipped (las variantes reales opt-in de Django y TypeScript),
  121 subtests passed. Incluye las regresiones Django (`test_project_preparation.py`, `test_django_journey.py`,
  `test_local_config.py`) sin cambios en sus tests.
- `test_typescript_preparation.py` con `HARNESS_TEST_TYPESCRIPT_NPM_CACHE=.local/npm-cache`: 40 passed, incluida
  la variante real, repetida tras el último ajuste del validador de composición (admitir ejecutables adicionales).
- `python3 -m unittest discover`: 12 tests OK. `alembic check`: sin operaciones nuevas.
- `node --test frontend/tests/*.test.mjs`: 82 pass. `npm --prefix frontend run check` y `run build`: correctos
  (solo el aviso conocido de tamaño de chunk).
- Enlaces y anclas de los documentos modificados comprobados con un script local.
- Experimento previo en un directorio temporal: `npm ci --offline` real con caché vacía (ENOTCACHED, sin
  `node_modules/`) y con `.local/npm-cache` (instala `typescript@5.9.3` y enlaza `.bin/tsc`).

No se ejecutaron proveedores, smokes, servicios, el wheel ni descargas; no se tocó configuración global ni el hijo
Django de P009. No se regeneraron OpenAPI/tipos porque la API no cambia.
