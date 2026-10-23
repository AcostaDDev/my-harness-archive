# P011-T016 — Primer uso reproducible y QA del paquete candidato

Fecha: 2026-10-23. Decisión: [D179](../DECISIONS.md#d179--p011-t016-primer-uso-ensayado-pylock-y-validación-de-tarea-igual-al-perfil).
Base: `2bd4a84`. Tarea de [NEXT_STEPS](../NEXT_STEPS.md#p011-t016--primer-uso-reproducible-y-qa-del-paquete-candidato);
candidato de [T015](P011-T015_PAQUETE_PUBLICO.md).

## 1. Alcance autorizado (HITL)

Propuesta presentada antes de ejecutar y aprobada por el usuario:

| Punto | Decisión |
|---|---|
| Red | Primer llenado de **cachés vacías** desde PyPI (uv) y registry.npmjs.org (npm) y repetición offline; Python 3.14.4 local, sin descarga |
| Carpeta | Scratchpad de la sesión, fuera del checkout: instantánea, repositorio local desechable sin remoto, `git clone`, venv, servicio y datos sintéticos. Se borra al terminar salvo la evidencia saneada de este directorio |
| Servicio/QA | Servicio instalado en loopback con puerto aleatorio y recorrido HTTP con CLI falsas. La **QA de navegador** (en/es, claro/oscuro, escritorio/móvil, junto con la pendiente de T010/T021/T022) pasa a la nueva **T024**, con autorización propia |

Configuración personal desactivada en todo el ensayo sin modificarla: `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, `UV_NO_CONFIG=1` y archivos npmrc vacíos propios. Sin credenciales, CLI reales ni proveedores.

Dos HITL más durante el ensayo (§3): `pylock.toml` sustituye a `requirements.txt` y se corrige el producto para que
una validación de la tarea igual a la del perfil no se rechace.

## 2. Recorrido

1. **Instantánea.** `P011-T015_public_candidate.py --revision 2bd4a84` → 387 archivos, manifiesto idéntico al de T015.
   Repositorio local con un commit sintético (identidad `Rehearsal`) y `git clone` (Git 2.50.1).
2. **Primer paso del README con red**, cachés vacías: `uv sync --frozen --no-python-downloads` (29 paquetes, ~5,7 s)
   y `npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache` (175 paquetes). npm requiere ficheros de
   configuración distintos para usuario y global (con `/dev/null` en ambos se niega); solo afecta al aislamiento del ensayo.
3. **Repetición offline**: borrar `.venv`/`node_modules` y reinstalar con `--offline` desde las cachés nuevas. Clon limpio
   (`git status` vacío).
4. **Suites desde el clon** (comandos de AGENTS): unittest, pytest, Alembic en BD temporal, Node y tipos.
5. **Paquete**: `build_distribution.py` y `check_distribution.py` desde el clon.
6. **Instalación del README** fuera del clon con los comandos ya corregidos (`uv venv`, `uv pip sync … pylock.toml`,
   `uv pip install --no-deps … .whl`), todos `--offline` con la caché del clon.
7. **Primer uso instalado** con [`P011-T016_rehearsal.py`](P011-T016_rehearsal.py) (solo stdlib, cliente externo):
   ejemplo mínimo del README con sus marcadores sustituidos, `claude` falso en el PATH explícito del rol (sonda pública
   en modo `recipe`), `check-config --preflight`, `init-db`, `serve --config` con supervisor y API con sesión/CSRF.
8. Tras cada corrección, el clon se sincronizó con el árbol nuevo y se repitió todo lo afectado; el **pase final**
   (§5) se hizo con el árbol definitivo.

## 3. Hallazgos y correcciones

| # | Hallazgo | Corrección |
|---|---|---|
| 1 | `test_incompatible_lock_or_runtime_stops_preparation[lock-mismatch]` esperaba `EUSAGE`; con una caché llenada solo por `npm ci` (sin metadatos del registro) npm responde `ENOTCACHED`. La caché privada los tenía por operaciones antiguas. El producto se comportaba bien en ambos casos (para en preparación, sin agentes ni cambios) y la CI habría fallado igual | El test admite ambos códigos con el motivo explicado |
| 2 | Desde un clon limpio, `uv pip sync --offline requirements.txt` falla: `uv sync --frozen` cachea los wheels pero no los metadatos del índice que necesita un requirements. Rompía `check_distribution`, la CI y el «todo offline tras el primer paso» del README (cuyos comandos de instalación, además, usaban la caché y red globales) | HITL: `pylock.toml` (PEP 751, URL y hash de cada wheel, exportado por uv del mismo lock) sustituye a `requirements.txt` en build, check, README, CHANGELOG, ARCHITECTURE y D043 pública. uv rechaza un hash alterado (comprobado). Instalación del README con `UV_CACHE_DIR=.local/uv-cache … --offline` |
| 3 | **Defecto de producto.** Con el ejemplo mínimo, una tarea que declara la validación del perfil (`python3 -m unittest discover -s tests -t .`, como invita la plantilla de NEXT_STEPS) se detenía: el comando de la tarea llevaba el timeout por defecto (1800 s), el perfil lo autoriza con 600 s y la autorización exacta lo rechazaba. Un revisor real lo haría en la primera tarea | HITL: en `core/engine/validation.py`, un comando de la tarea con el argv de una validación del perfil que se ejecuta en la raíz sin entorno propio **es** esa validación (su timeout) y se ejecuta una vez. Validaciones con `cwd`/entorno propios no se adoptan. Regresión nueva en `test_engine.py`; `test_contract_shapes` ajusta su aserción (antes ejecutaba el mismo `npm run test` dos veces). ARCHITECTURE privada y pública |
| 4 | La sonda falsa no creaba directorios al escribir archivos nuevos (limitación del doble, no del producto) | `cli_process_probe.py` crea los padres |
| 5 | README, README.es y STATE públicos decían «no ensayado» | Actualizados: ensayado desde clon limpio con CLI falsas, sin inicio de sesión ni inferencia real |

Observaciones del driver corregidas en él mismo (no del producto): preferencias exigen `Idempotency-Key`; la
incorporación debe proponer AGENTS/CLAUDE/GEMINI (la creación los toma de la plantilla; el 409 llegó en español al estar
el visual en es); un replay con la misma clave y otro cuerpo devuelve 409, como debe.

## 4. Matriz de criterios

| Criterio T016 | Evidencia |
|---|---|
| Propuesta previa de carpetas/comandos/red/servicios/limpieza y ejecución tras autorización | §1 |
| Clon sin cachés privadas, primera descarga explícita y repetición offline | §2.2–2.3; build del clon **idéntico byte a byte** al build del checkout privado |
| Instalar fuera del checkout; assets/catálogos/sesión; recorrido hasta COMMITTED/cierre en/es con agentes falsos | `check_distribution` (journey instalado) y driver: `alpha` creada desde cero → definición → tarea → **COMMITTED** → READY → **CLOSED** con tag `p001` y archivo; `beta` incorporada → tarea → **COMMITTED**; UI servida, rutas de assets, sesión y CSRF |
| Cambio de idioma sin mutar evidencia; CLI falsas posteriores/negativas; reinicio/migración/backup de consulta | `frozen_pair_unchanged` (es/es se mantiene tras cambiar preferencias); `later_client_admitted` (2.1.305, compatibilidad condicionada con efectos no verificados listados), `older_client_refused` (2.1.200 → mínimo 2.1.304 y «Update that client…»), preflight sin llamadas a modelo; reinicio con mismo run, replay idempotente y sin llamadas nuevas; `migrate` → `current`; backup create/verify/restore y servicio restaurado de solo lectura que rechaza mutar (409) |
| Cuatro combinaciones visual/trabajo, defaults que no cambian proyectos, rechazo a cambiar el trabajo, cambio visual entre turnos | Directiva sellada leída en los prompts grabados: en/es (definición `alpha`), es/es (planner/ejecutor/revisor de `alpha`), es/en (incorporación `beta`), en/en (definición `gamma`); AGENTS.md de `alpha` en español; defaults cambiados y proyectos intactos; cambiar el idioma en el registro → 409 `work_language_immutable` (diagnóstico en español con el visual es). Llamadas activas/pendientes y continuaciones congeladas: suites (`test_preferences`, `test_work_language`, `test_language_directive`), ejecutadas en el clon |
| Fuentes B mixtas legibles | `test_language_directive::test_onboarding_documents_and_prompt_follow_the_frozen_pair` en el clon; `beta` incorpora código y README existentes en inglés |
| Ensayo desde la instantánea permitida, sin historia/docs privados, código equivalente al aprobado, build autónomo | §2.1; 387 archivos; manifiesto público final [`P011-T016_MANIFIESTO_PUBLICO.sha256`](P011-T016_MANIFIESTO_PUBLICO.sha256) (mismas rutas que T015; 13 archivos cambiados por §3) |
| Ambos accesos; legacy/A ausente o rechazado sin efectos ni observadores | Driver: `/api/legacy/*`, `import`, `migration` → 404; `legacy-import`/`legacy-summary` → error de argparse. Arranque y respaldo de instalación anterior sin observadores: `test_legacy_retirement` en el clon |
| Base/versión/hashes, comandos/resultados/skips y servicios detenidos | §5; [`P011-T016_RESULTADOS.json`](P011-T016_RESULTADOS.json) saneado (30 entradas); ningún `harness-local serve` vivo al terminar |

## 5. Pase final (árbol definitivo)

| Paso | Resultado |
|---|---|
| Instantánea del árbol final | 387 archivos, manifiesto público `71fdc2250adc8610a39395589514e9c30b6a3f804b72a08d1e8252bdaaccf410`, sin problemas |
| Reinstalación offline en el clon | Correcta |
| unittest / pytest / Alembic temporal / Node / tsc (en el clon) | 8 OK / 1671 passed, 2 skipped / sin operaciones nuevas / 93/93 / correcto |
| Mismas suites en el checkout privado | Iguales (1671 passed, 2 skipped) |
| `build_distribution.py` + `check_distribution.py` (clon) | Correctos |
| Instalación del README fuera del clon + driver | 30/30 comprobaciones |
| Build desde el checkout privado | `SHA256SUMS` idéntico al del clon |

Paquete candidato:

| Artefacto | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `537b32fd97ddfb6093a1d0e26f3f8f758c009b33db768706e9983e0548f89c99` |
| `harness_local-0.1.0.tar.gz` | `c4a21e3836108d9a85fd5cc6bc9bf38d44efa8cc354f336ad07c25c828c7fd87` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |

Omisiones: QA de navegador (→ T024), CI remota, plataformas distintas de macOS ARM64, inicio de sesión, inferencia y
calidad lingüística o semántica de CLI reales (los dobles no las acreditan), recetas Django/TypeScript con
herramientas reales (sus skips opt-in siguen igual), red fuera del primer llenado. Sin push, tag, Release ni repositorio.

## 6. Notas para T024/T017

- T024 puede reutilizar el driver para preparar datos sintéticos y abrir la UI del servicio instalado.
- T017: el texto «observers» de la ayuda de la CLI sigue pendiente (nota de T014).
