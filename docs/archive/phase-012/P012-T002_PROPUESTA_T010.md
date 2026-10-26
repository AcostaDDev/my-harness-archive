# P012-T002 — Continuación operativa tras el formateador declarativo

Fecha: 2026-10-24. Base del producto: **`a7d8b33d1db10ba290a097cc9c9ecce73b63ef63`**.
**Estado actual: autorizada; preparación completada, tramo detenido antes del alta por un defecto de UI.**
Los §§1–6 conservan la propuesta sometida a consentimiento; ejecución y paradas en §§7–8.
Desarrolla el [guion de T010](P012-T010_FORMATEADOR_DECLARATIVO.md#5-continuación-operativa-propuesta-todavía-sin-autorizar)
y [D194](../DECISIONS.md#d194--p012-t010-formateador-declarativo-optativo-en-local-config-8).
No sustituye ni reescribe las evidencias o los consentimientos agotados de T001/T002/T009.

## 1. Efectos y puerta de control

Una continuación de T002, conservando los resultados B/B2. Construir y verificar el producto de la base indicada;
instalarlo en un venv nuevo; clonar el commit documental limpio de B2; preparar su venv offline; materializar
una copia v8 del TOML; preflight y ocho checks iniciales; servicio/UI, registro de proyecto ya documentado,
alta de P001, preparación documental y una tarea nueva. No repetir la incorporación B ni su conversación.

Área: `$HOME/Documents/harness-validation/p012-20261024` (`AREA` en los comandos).
Destinos **nuevos**, comprobados ausentes al preparar esta propuesta:

| Destino bajo AREA | Efecto propuesto |
|---|---|
| `dist-t010/`, `venv-t010/` | Distribución verificada y harness instalado, Python 3.14.4 |
| `projects/managed-b-t010/` | Clon independiente, venv Python 3.13.13 y temporal del escritor |
| `config/harness-local-t010.toml` | Copia v8, modo 0600, perfil/presets/composición nuevos |
| `state/operator/t010-*` | Evidencia privada, manifiestos y copias de consulta |
| `state/harness.sqlite3` y artefactos normales del servicio | Misma base, solo escrituras por el producto |

Repetir guardias antes de operar: destinos ausentes, sin enlaces en sus componentes, área fuera de checkouts,
puerto **8024** libre, servicio/escritores detenidos, sin jobs activos/pendientes ni locks. `umask 077`, directorios
privados 0700. Los enlaces propios de venv/lanzadores se acreditan por destino resuelto. Ante cualquier deriva,
parar sin sobrescribir o escoger otro destino automáticamente.

Antes de operar, guardar manifiestos SHA-256/modos de B/B2 (incluidos sus diffs), configuraciones y distribuciones
previas; copias SQLite/WAL/SHM de consulta con escritores detenidos. Al terminar contrastar filas previas de
historial/intenciones, y declarar cualquier cambio operativo normal del registro; no prometer igualdad de toda
SQLite mientras el producto trabaja. No leer tokens, prompts o streams completos para la evidencia pública.

## 2. Configuración exacta revisable

Fuente: `config/harness-local-t009.toml`, SHA-256
**`b11cce3d02fa3138127243e5cb4f634a45b75c4d836ca7b324afebded47e3cc9`**, comprobado por lectura.
El [transformador puro](P012-T002_CONFIG_T010.py) devuelve el texto completo propuesto sin escribirlo ni lanzar
procesos. Exige ese hash y contrasta el árbol TOML completo con el delta esperado:

- `format`: `local-config-7` → **`local-config-8`**.
- Mantener todas las tablas anteriores (defaults, perfiles, recetas, presets y composiciones).
- Añadir `profiles.python-django-t010`: copia exacta de `python-django`, más
  `formatter_argv = ["ruff", "format", "--"]` y `formatter_paths = ["*.py"]`.
- Añadir `agent_presets.claude-t010`: copia exacta de `claude-t009`.
- Añadir `agent_presets.codex-t010`: copia de `codex-t009`, sustituyendo únicamente la raíz
  `AREA/projects/onboarding-b-t009` por `AREA/projects/managed-b-t010` en PATH y TMPDIR.
  TMPDIR queda en `.local/codex-tmp` dentro del nuevo checkout, ignorado y 0700.
- Añadir `compositions.django-t010`: copia de `django-t009`, perfil `python-django-t010`, misma sustitución
  de raíz en los cuatro ejecutables y PATH. HOME/TMPDIR de validación conservan su entorno separado;
  `authorize_profile_commands = true`, mismas dos preparaciones y seis validaciones/JUnit.

SHA-256 del **texto propuesto**, calculado en memoria, todavía sin archivo operativo:
**`e0e95abb9055f1c9f985c82285bc3c7b551f6503ff6bddb5aff7ddf282fbb6db`**.
Revisar y verificar íntegro el TOML materializado antes del preflight. Ningún perfil antiguo adquiere formateador.
V8 cambia el identificador vivo de composición; no se afirma igualdad de versiones v7/v8 ni se adopta un job previo.
Los jobs agotados no se operan. Si el arranque exige recuperación o pone trabajo pendiente en cuarentena, parar.

Pareja/política invariables: Claude **sonnet/low** (1800 s), Codex **gpt-6-luna/low** (3600 s), plan **agent**,
ejecutor **catalog** con ese único modelo/esfuerzo y **max_revision_cycles = 0**. CLI previstas **2.1.310/0.164.0**,
compatibilidad condicionada `cli-14`; rutas/hashes de toolchain de [T001 §2](P012-T001_PROPUESTA_OPERATIVA.md#2-toolchain-observada-y-modelos-propuestos).
Recomprobar identidades; no actualizar clientes, permisos, confianza, modelo o configuración global.

## 3. Construcción y clon limpio, solo tras consentimiento

Desde `REPO=$HOME/Documents/projects/my_harness`, herramientas por PATH explícito de T001.
Comprobar que fuentes, scripts, locks y entradas del paquete coinciden con la base `a7d8b33`; los documentos
privados de esta propuesta quedan fuera del paquete. Comandos futuros:

```sh
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist-t010"
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist-t010"
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3 "$AREA/venv-t010"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip sync --offline --python "$AREA/venv-t010/bin/python" "$AREA/dist-t010/pylock.toml"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip install --offline --no-deps --python "$AREA/venv-t010/bin/python" "$AREA/dist-t010/harness_local-0.1.0-py3-none-any.whl"
git --no-lazy-fetch clone --no-local --no-hardlinks --no-checkout "$AREA/projects/onboarding-b-t009" "$AREA/projects/managed-b-t010"
git -C "$AREA/projects/managed-b-t010" remote remove origin
git --no-lazy-fetch -C "$AREA/projects/managed-b-t010" checkout --detach 9808fd97d349c6eeacb766be8ff5e5603b6e974c
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3.13 "$AREA/projects/managed-b-t010/.venv"
UV_CACHE_DIR="$AREA/uv-cache" uv pip install --offline --no-index --no-deps --no-build --require-hashes --find-links "$AREA/wheels" --python "$AREA/projects/managed-b-t010/.venv/bin/python" -r "$AREA/config/django-requirements.lock"
```

No ejecutar el bloque sin sus guardias intermedias. Antes de instalar, verificar SHA256SUMS y guardar hashes
completos de wheel/sdist/pylock; todavía **no existen** y no heredan hashes de T008. El verificador incluye CLI
falsas y servicios de loopback efímeros; el build recompone `frontend/dist`/dependencias desde cachés del checkout.
Antes de preparar Django, verificar los **17 wheels** contra el [manifiesto aprobado](P012-T002_WHEELS_VERIFICADOS.sha256)
y el lock contra el empaquetado (`0f2ce9af…313c1b`). Sin descargas/builds de dependencias; falta de caché → parada.

Clon: sin remoto, alternates, enlaces de objetos o gitlinks/filtros ejecutables. Contrastarlo contra el árbol
sellado de `9808fd97…`, con bytes y modos de sus **28 archivos**, incluidos los **15 originales** del fixture.
No copiar working tree, `.git/config`, ignorados, venv o SQLite de B2. El commit fuente está disponible localmente;
su lectura no valida de nuevo el resultado fallido. Crear `.local/codex-tmp` 0700 y acreditar exclusión Git.

Materializar únicamente el texto devuelto por el transformador de §2 en el destino nuevo, modo 0600.
Desde AREA, usando el entorno explícito T001 (HOME `command-home`, TMPDIR `tmp`, PATH nuevo venv/Node/uv,
PYTHONNOUSERSITE=1, PYTHONDONTWRITEBYTECODE=1, LANG=C.UTF-8; sin PYTHONPATH/config ambiental):

```sh
"$AREA/venv-t010/bin/harness-local" check-config "$AREA/config/harness-local-t010.toml" --preflight
"$AREA/venv-t010/bin/harness-local" migrate --database "$AREA/state/harness.sqlite3" --snapshots "$AREA/state/operator/t010-premigration" --writers-stopped
"$AREA/venv-t010/bin/harness-local" serve --database "$AREA/state/harness.sqlite3" --config "$AREA/config/harness-local-t010.toml" --port 8024
```

Entre preflight y servicio: ejecutar las dos preparaciones y seis validaciones del perfil sobre el **clon nuevo**,
con argv/entorno exactos de la composición, JUnit y checkout versionado intacto. Deben pasar los ocho checks;
no formatear ni ejecutar tests en B/B2. La base ya está en `0025_project_work_languages`: `migrate` debe ser
no-op, sin nueva revisión ni instantánea; un cambio de esquema inesperado detiene el tramo antes de servir.
No `init-db` sobre una base existente ni `scripts/dev`. Cargar el wheel desde el venv nuevo, fuera del checkout.

## 4. Registro, documentación y única tarea

Login en la pestaña local existente de **127.0.0.1:8024**, sin eludir Host/Origin/CSRF; clave efímera directa al
formulario sin imprimirla. Si la navegación encuentra otra vez el rechazo cross-site, parar y recurrir a HITL,
conservando las guardias. Registro **p012-b-t010**, raíz del clon nuevo, es/es, bootstrap false, composición
**django-t010**, perfil **python-django-t010**, presets **claude-t010/codex-t010**, política de §2 y confianza
explícita del fixture sintético. No abrir B ni repetir inventario/conversación/propuestas de incorporación.

Crear P001 desde UI: código/objetivo/siete criterios literales de su ROADMAP y tarea **P001-T001** de NEXT_STEPS;
documentos por defecto del layout D088, sin tag ni llamada de modelo. Comprobar fase ACTIVE y definición exacta.
El alta trabaja por raíz nueva, no adopta las fases SQLite ni los runs de B2.

Preparación documental por UI, vista previa/CAS/confirmación y commit del producto. El editor de contenido de
la UI envía **un archivo por operación** (`pages/Docs.tsx`): concretamos **dos commits documentales secuenciales**,
en lugar del único commit genérico del guion T010; sin escribir archivos manualmente ni usar una API alternativa.

1. `AGENTS.md`: cambiar el perfil/composición a `python-django-t010`/`django-t010`; sustituir «sin receta ni
   formateador automático» por «sin receta; formateador del harness `ruff format --` sobre archivos Python
   cambiados y permitidos por el contrato, antes de validar/revisar; revalidar no formatea». Con los ocho checks
   ya acreditados, retirar «propuesta del operador»/«propuesta, pendiente de confirmar» de sus dos títulos.
   Mantener preparaciones, seis validaciones, pareja, cero correcciones y resto de reglas; ≤60 líneas/32 KiB.
2. `docs/DECISIONS.md`: conservar D001–D005 y añadir **D006 — Formateador del perfil declarado elegido por el
   operador**, `Estado: aprobada por el operador para esta continuación.` Describir perfil/composición/presets
   de §2, D133, cero correcciones, checkout nuevo y conservación de resultados previos. La aprobación cubre esta
   elección, sin aprobar retroactivamente las cinco decisiones inferidas. Índice regenerado por el producto.

Conservar bloques gestionados en las propuestas; adoptar por hash si el producto lo requiere y comprobar
checkout limpio/documentos confirmados antes de encolar. NEXT_STEPS ya tiene política y tres rutas correctas;
no necesita otro cambio. No alterar archivos históricos, SPECIFICATION, herramientas ni código en esta preparación.

Seleccionar **P001-T001** desde el NEXT_STEPS vivo por CAS. Contrato funcional ya elegido: `int`, rango 1–20,
defecto 5, HTTP 400 JSON con `error` descriptivo para vacío/texto/0/21/5.0; aceptar espacios, `%2B5` y `05`,
probar extremos/límite efectivo y conservar casos originales. Solo `catalog/views.py`, `catalog/tests/test_views.py`,
`docs/flows/items-listado.md`; sin dependencias, modelos, migraciones, configuración o rutas nuevas.

Plan Claude → **una ejecución Codex** → formateador nativo D133 sobre archivos Python cambiados del contrato
→ seis validaciones/JUnit → revisión Claude → aceptación exacta y commit del producto si corresponde.
Guardar `formatting_json`, argv/rutas/exit, diff, JUnit, CLI/modelos reportados y commit. Confirmar únicamente una
aceptación válida de esos bytes; no aplicar next_prompt ni autorizar corrección o revalidación tras un fallo.
No cerrar P001, repetir la prueba idempotente, hacer chat o iniciar T003/T004.

## 5. Presupuesto, parada y consentimiento solicitado

Consumido: **Claude 7/12, Codex 2/3**. Se solicita como máximo nuevo **2 Claude + 1 Codex** (plan/revisión;
ejecución), acumulado máximo **9/12 y 3/3**. El saldo Claude restante no habilita turnos adicionales.
Sin correcciones, fallback ni ampliación de techo. Tiempo máximo de esta continuación: **4 horas** desde su
preparación operativa; al agotarlo no iniciar llamadas y detener el trabajo propio por las vías del producto.

Parar al primer fallo de identidad/proveedor/auth/esquema/timeout, formato/validación, permisos, CAS/hash,
destino/cache, REVISE/BLOCKED/pregunta no deducible o cuarentena. El motor puede completar la validación/revisión
ya en marcha para sellar su resultado como en D193; no iniciar un ciclo adicional. Una pregunta normal exige HITL
antes del paso dependiente. No reparar el resultado a mano ni editar TOML/SQLite para desbloquearlo.

Al terminar/parar: detener servicio y grupos propios, verificar puerto cerrado/clave retirada, jobs terminales,
procesos STOPPED y cero locks; conservar área y evidencias. Si hay incertidumbre, declararla y usar recuperación
explícita sin relanzar ni señalar un PID histórico. Comparar manifiestos previos y copias de consulta de SQLite;
publicar solo evidencia saneada. T002 se marca completa únicamente si acredita la tarea COMMITTED y todos sus
criterios; una propuesta o una preparación offline no lo demuestran.

**HITL solicitado:** «Autorizar esta continuación de T002 según P012-T002_PROPUESTA_T010: preparación offline,
wheel/venv nuevos, clon limpio de B2, TOML v8, preflight, servicio/UI y registro/P001, dos commits documentales
preparatorios y una tarea; máximo nuevo 2 Claude/1 Codex, cero correcciones y parada al primer fallo».
La petición de continuar/commitear el repositorio no equivale a este consentimiento operativo separado,
exigido por AGENTS, T001 §7, las restricciones T002 y D194. Respuesta todavía pendiente.

## 6. Comprobación de esta propuesta

Lecturas locales del TOML aprobado y blobs Git del commit documental B2; destinos nuevos ausentes. Transformación
TOML en memoria con conservación de tablas previas y hash exacto; sin archivos operativos ni procesos de proveedor.
Contraste con SPECIFICATION §8, ARCHITECTURE §§6/9 y flujos de documentos, fase y tarea: se usan vías existentes.
No cambia producto, esquema o flujo implementado; diagrama y flujos permanecen iguales. Checks documentales y diff
se registrarán al cerrar. Sin build/instalación operativa, preflight real, servicios, validaciones del hijo ni
nuevas llamadas todavía. Los hashes futuros se acreditan en la puerta offline, nunca se inventan aquí.

## 7. Consentimiento y primera preparación

El usuario responde **«Autorizar esta continuación de T002»** a la propuesta íntegra de §§1–6. Comprobados
ocho hashes de toolchain, 17 wheels, fuentes base, destinos ausentes y puerto libre; copias de consulta y
manifiestos privados conservados. Estado inicial: 7 jobs DONE, 9 procesos STOPPED, 0 locks; integridad SQLite
correcta, esquema 0025. No se consumen modelos en esta preparación.

Build offline terminado, wheel SHA-256 `ead1b58b265d63b0f909ef5291769b7f3e18aa81afe8327e666607bfd17b4710`;
todavía sin verificar/instalar al detenerse. Clon independiente creado en el commit documental esperado,
28 blobs coincidentes, sin remoto/alternates/enlaces y checkout Git limpio. Una comprobación del operador
exige erróneamente 0644 a todos los archivos y falla en `.gitignore`: confunde modo Git 100644 con permisos
de disco, afectados por umask 077. Lectura posterior: B2 tiene **15 originales 0600 y 13 documentos 0644**;
el clon tiene todos en 0600. El desfase real se limita a esos trece documentos, no a los originales.

Parada preventiva antes de verificador/instalación/venv/TOML/preflight/servicio y modelos. HITL propuesto:
igualar únicamente los trece documentos a 0644, mantener originales 0600 y repetir el contraste exacto contra
el manifiesto de B2 antes de continuar el mismo tramo. La primera pregunta decía 28 archivos 0644; se corrige
expresamente con una segunda pregunta que fija 15/13. No se normalizan modos ni se continúa sin su respuesta.

El usuario confirma ambas preguntas, incluida la precisión **«Igualar los 13 documentos y continuar T002»**.
Se ajustan solo esos trece documentos y se comprueban los 28 blobs contra el commit limpio y los modos contra
el manifiesto de B2: 15 originales 0600, 13 documentos 0644. Se conserva la distinción entre modos Git y disco.
La parada inicial y los dos enunciados quedan documentados; no se presenta como defecto del producto.

## 8. Preparación aprobada y parada por selector de presets v8

- `check_distribution.py` correcto: miembros/metadatos/licencias/checksums exactos y recorrido instalado con
  CLI falsas (UI/API/sesión/definición/tarea/commit/reinicio/restauración). Wheel instalado en `venv-t010`,
  dependencias por `pylock.toml` con hashes; Django en venv nuevo con los 17 wheels, sin red o builds.
- Hashes completos: wheel **`ead1b58b265d63b0f909ef5291769b7f3e18aa81afe8327e666607bfd17b4710`**;
  sdist **`fcc1cd92a7314ee9b4564dc5f9375a1bd54ca7eb68a17cb329f65bd8489d7e11`**;
  pylock **`20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9`**;
  SHA256SUMS **`b7f5663670d1cb161d38197ceb1075c4fbb1c46f72ad014340e42d633b97c0a4`**.
- TOML materializado, modo 0600 y hash exacto de §2. Carga/composición pura con creación de procesos bloqueada:
  formateador `ruff format --`, patrones `*.py`, cero correcciones y TMPDIR del ejecutor dentro del clon.
- Preflight real exit 0: Claude **2.1.310**, Codex **0.164.0**, política **`1156d0c9…`**, sin flags/valores
  ausentes; compatibilidad condicionada. No consume modelos ni acredita inferencia.
- Ocho checks iniciales aprobados: Python/Django version, pytest **2 passed** con JUnit, Ruff check/formato,
  mypy, Django check y makemigrations sin cambios. Los 28 archivos versionados conservan bytes/modos después.
- `migrate` no-op en 0025: bytes SQLite idénticos. Servicio instalado arrancado en 8024, login por clave privada
  directo al formulario, es/es conservado. Se abre «Registrar carpeta existente», sin enviar preview ni alta.
- **Defecto del producto:** el formulario muestra el aviso de que la configuración conserva la pareja del
  servicio y oculta los presets. `frontend/src/pages/Registry.tsx` limita `PRESET_FORMATS` a v5/v6/v7;
  el backend sí acepta v8 y ofrece sus presets. Así no se puede seleccionar claude-t010/codex-t010 por UI.
  No se registra con defaults ni se usa una API alternativa. Dos localizadores iniciales confundieron los
  botones de «Tipo de alta» con radio/checkbox: no enviaron acciones y se resolvieron leyendo el DOM.
- Servicio detenido con SIGINT al PID propio comprobado, salida 0; puerto sin listener y clave eliminada.
  Una prueba inicial de bind encontró TIME_WAIT; la conexión posterior es rechazada, sin servicio activo.
  **7 jobs DONE, 9 procesos STOPPED, 0 locks**. Ningún job/run/proyecto nuevo: **13.785 filas previas
  íntegras e idénticas**, comparación de todas las tablas de las copias SQLite/WAL/SHM (excepto sqlite_*).
  B/B2, sus diffs, TOML/distribuciones anteriores conservan SHA-256 y modos.

Consumo nuevo **0 Claude/0 Codex**; acumulado **7/12 y 2/3**. No hubo alta, fase nueva, commits documentales
del hijo, tarea, formateo nativo o validación/revisión real nuevos. T002 sigue parcial; este wheel contiene aún
el defecto de UI y se conserva como evidencia. El consentimiento se agota con la parada, sin relanzar.

Evidencia privada `state/operator/t010-*`: logs, manifiestos, copias de consulta en `tmp/t010-{before,after}-db`,
resumen final y captura `t010-registry-stop.png`; sin copiar tokens, SQLite o streams al repositorio.
Se abre la corrección acotada **[T011](P012-T011_PRESETS_UI_V8.md)**, verificada offline en esta sesión;
su producto corregido no se reconstruye/instala ni se opera sin otra propuesta y consentimiento.
