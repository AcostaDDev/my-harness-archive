# P011-T015 — Paquete público, metadatos y checks reproducibles en GitHub

Fecha: 2026-10-23. Decisión: [D178](../DECISIONS.md#d178--p011-t015-paquete-candidato-010-ci-sintética-e-instantánea-pública).
Base: `f25baf5`. Tarea de [NEXT_STEPS](../NEXT_STEPS.md#p011-t015--paquete-público-metadatos-y-checks-reproducibles-en-github);
contrato [T001 §8](P011-T001_CONTRATO_APERTURA.md#8-lista-permitida-del-corte-inicial-y-continuidad) y
[T002](P011-T002_CONTENIDO_PUBLICABLE.md).

## 1. Decisiones HITL de esta sesión

1. **Versión candidata `0.1.0`.** Primera versión pública; el `0.1.0` local de P010 nunca se publicó y su `dist/`
   queda excluido. Se respeta la reserva de `0.2.0` (D156) y no se asume `1.0.0`. No hace falta tocar `api/app.py`.
2. **Ejecución autorizada.** Build offline con las cachés de `.local/`, inspección de wheel/sdist,
   `check_distribution.py` (venv temporal y servicio loopback con agentes falsos), suites y consulta web de solo
   lectura para fijar las versiones de las GitHub Actions.
3. **Instantánea pública materializada** en `.local/public-candidate/` (ignorado), sin `git init` ni commit.
4. **ReferenceProject fuera del código.** El usuario indica que ReferenceProject es un proyecto privado que incorporará más tarde
   con el flujo de incorporar un repositorio existente, y que toda referencia en el código debe desaparecer. Se
   amplían las rutas de T015 a ese módulo y a sus tests: se elimina `profiles/reference_project.py` (solo biblioteca, sin
   uso desde el TOML ni datos persistidos que lo nombren) y las cinco menciones de tests; la prueba de reglas de stack
   declarativas usa ahora un perfil sintético Django/Docker. Los documentos privados históricos no se reescriben.

## 2. Entregables

| Archivo | Cambio |
|---|---|
| `pyproject.toml` | `readme`, `license-files` (LICENSE, NOTICE.md, NOTICE-THIRD-PARTY.md), `keywords`, `classifiers`; sin cambio de versión ni dependencias (`uv lock --check` correcto) |
| `CHANGELOG.md` (nuevo) | Política de versiones (versión única paquete/API/UI, 0.x, reserva 0.2.0, Release manual sin PyPI) y notas de `0.1.0` como material de release |
| `scripts/build_distribution.py` | Carpeta de salida nueva o vacía; staging con README y archivos de licencia; fuentes de `src/` por sufijo permitido (aborta ante otros, ocultos o symlinks); `requirements.txt` con `--no-header` (antes registraba la ruta absoluta de salida); `SHA256SUMS` |
| `scripts/check_distribution.py` | Antes de instalar: `SHA256SUMS`, miembros exactos de wheel y sdist, bytes de fuentes/assets/licencias, METADATA (nombre, versión, `License-Expression`, `License-File`, `Requires-Dist`, `Requires-Python`, descripción = README), `pyproject.toml.orig` = pyproject del repo, ausencia de 20 componentes retirados, versión única pyproject/package.json/lock/API y `requirements.txt` sin cabecera ni rutas. Versión leída del pyproject |
| `tests/fixtures/e2e/installed_config.py` | Declara `work_language='en'`: el journey instalado estaba roto desde T008 (409 `work_language_required`); ninguna tarea posterior ejecutó el script |
| `.github/workflows/ci.yml` (nuevo) | CI sintética en `macos-15`: `permissions: contents: read`, acciones fijadas por commit, sin secretos/proveedores/publicación; cachés llenadas en un paso explícito y el resto offline: unittest, pytest, Alembic en BD temporal, Node, tipos, build y `check_distribution` |
| Retirada de `profiles/reference_project.py` | Tests `test_engine`, `test_typescript_profile`, `test_local_config`, `test_managed_api`, `test_prompts` |
| `tests/fixtures/cli_capabilities/README.md`, `tests/fixtures/typescript_web/README.md`, `examples/managed_demo.py` | Sin referencias a evidencia privada (`../cli_help/`, enlace al archivo privado) ni ruta local de ejemplo |
| README, README.es, `docs/public/docs/{STATE,ARCHITECTURE}.md` | Versión candidata con enlace al CHANGELOG; build/check/CI descritos; perfil privado retirado de la arquitectura pública |
| `docs/ARCHITECTURE.md`, `docs/STATE.md` | Paridad privada del perfil retirado y del build |
| [`P011-T015_public_candidate.py`](P011-T015_public_candidate.py) | Herramienta privada de la instantánea por lista positiva (§5) |
| [`P011-T015_bundle_notices.py`](P011-T015_bundle_notices.py) | Evidencia privada: paquetes del bundle frente a NOTICE-THIRD-PARTY (§4) |
| [`P011-T015_MANIFIESTO_PRIVADO.tsv`](P011-T015_MANIFIESTO_PRIVADO.tsv), [`P011-T015_MANIFIESTO_PUBLICO.sha256`](P011-T015_MANIFIESTO_PUBLICO.sha256) | Correspondencia origen → candidato (privada) y `sha256  ruta` publicable |
| `docs/phase/P011-T014_public_docs_check.py` | Incluye CHANGELOG y `.github/` en la vista del candidato |

## 3. Paquete candidato

Build final (`.local/p011-t015/package/`, árbol de trabajo sobre `f25baf5`; un segundo build del mismo árbol da
`SHA256SUMS` idéntico, reproducible en esta máquina):

| Artefacto | SHA-256 | Contenido |
|---|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `fc6c4ae0e47b037c09a4706aa8814755108e5895e63976ada7f7f8337f678910` | 158 fuentes + 101 assets UI + 4 dist-info + 3 licencias (266 archivos) |
| `harness_local-0.1.0.tar.gz` | `978fc627ccba24dceebd728269cbf95ab8170d37bb7b9bcff661116e894d65bf` | Mismas fuentes/assets, PKG-INFO, pyproject (+`.orig`), README y licencias |
| `requirements.txt` | `9e4a1377eca10a30da92daa63e9fb3b303a8a26202e420aa1c2579ef72fa222c` | Dependencias de servicio con hashes, sin cabecera |

`pyproject.toml.orig` lo genera uv_build al normalizar el pyproject del sdist (T002 lo había señalado como resto):
es el pyproject del repositorio byte a byte y el check lo exige así. Los artefactos de P010 en `dist/` no se
reutilizan ni se borran. Estos hashes corresponden a este árbol; el candidato que se publique se reconstruye en T016
desde la instantánea y fija sus propios hashes.

## 4. Avisos de terceros y 19 entradas externas

- Build temporal con sourcemaps: 58 paquetes/versiones llegan al bundle (incluidas copias anidadas como `cose-base`
  1.0.3/2.2.0, `d3-array` 2/3, `d3-path` 1/3, `layout-base` 1/2), todos con fila exacta en NOTICE-THIRD-PARTY; el
  hash del lock coincide. Sin fuentes ni imágenes emitidas (KaTeX llega solo como JS, sin CSS/fuentes). Sin rutas
  personales ni el nombre privado en `frontend/dist`.
- Las 19 entradas sin términos de versión exacta en evidencia local (colorama, 17 de la receta Django y uv_build)
  **no se redistribuyen**: ni wheel ni sdist ni `requirements.txt` las contienen (colorama no aparece en la exportación
  para esta plataforma; la receta las descarga en el proyecto hijo; uv_build es herramienta de build). Sin avisos
  adicionales que conservar en los artefactos.
- Las dependencias Python del servicio se instalan aparte desde `requirements.txt` con sus propios archivos de licencia.

## 5. Instantánea pública inicial

`python3 docs/phase/P011-T015_public_candidate.py --out .local/public-candidate` clasifica cada archivo rastreado (y
los no ignorados del árbol de trabajo): copiado, mapeado desde `docs/public/` o excluido con motivo; una ruta sin
clasificar detiene la exportación. Resultado final antes del commit:

| Disposición | Archivos |
|---|---|
| Copiados (`src/`, `frontend/`, `tests/`, `scripts/`, `.github/workflows/`, raíz y cinco ejemplos permitidos) | 363 |
| Baseline pública `docs/public/**` → raíz | 24 |
| Excluidos: documentación/fases/decisiones/evidencia privadas | `docs/**` restante |
| Excluidos: AGENTS/CLAUDE/GEMINI privados (sustituidos), ayudas reales de CLI (3), guiones históricos (4) | 10 |

Candidato: **387 archivos, 5.397.810 bytes**, manifiesto público SHA-256 `f80c07bce2817465d14b8338d9f493ddb0b69e385be2a99275057276ac37d045`.
Comprobaciones sobre el árbol materializado: sin symlinks; ocultos solo `.gitattributes`, `.gitignore`,
`.python-version`, `.github/`, `frontend/.npmrc` y el `.gitignore` del fixture TypeScript; sin rutas personales,
correo, nombre del proyecto privado ni enlaces a `docs/archive|phase` de este repositorio. Los códigos `PNNN-TNNN`
de comentarios del código se aceptan porque el preámbulo de la DECISIONS pública los explica (D176); `P001-T001`
es además dato del producto. El manifiesto privado registra origen, destino, hash, modo y disposición; el público,
solo `sha256  ruta`. Los archivos copiados son idénticos por construcción al origen (mismo hash en ambos manifiestos).

## 6. Procedimiento manual en GitHub (expediente para T017; nada ejecutado)

Requiere la autorización propia de apertura. Ninguno de estos pasos se ha hecho.

1. Regenerar la instantánea desde el commit aprobado (`--revision <commit>`) y comparar su manifiesto público con
   el revisado en T016/T017.
2. Crear el repositorio vacío en GitHub (sin README/licencia generados), con la visibilidad que decida el usuario.
3. Activar **Private vulnerability reporting** (Settings → Code security) y verificarlo antes de abrir; SECURITY.md
   no lo activa (D160).
4. En una copia de la instantánea fuera de este checkout: `git init`, identidad pública elegida, commit raíz único,
   remoto y push de `main`. Ningún objeto, ref o tag de este repositorio.
5. Comprobar que CI se ejecuta y pasa en `macos-15`; añadir `[project.urls]` con la URL real en una entrega posterior.
6. Release opcional `v0.1.0`: tag sobre el commit verde, adjuntar wheel, sdist, `requirements.txt` y `SHA256SUMS`
   construidos por CI o localmente con hashes comparados; notas desde la sección `0.1.0` del CHANGELOG. Sin PyPI.
7. Desde ese momento el repositorio público es la fuente principal (D157); este checkout no se sincroniza por copias.

## 7. Criterios de aceptación

| Criterio | Resultado |
|---|---|
| Versión/política sin asumir 1.0.0, reserva 0.2.0; coherencia Python/UI/locks/licencia; sin `.local`, runs, credenciales ni cachés; recursos completos | Cumplido: `0.1.0` (HITL), CHANGELOG, versión única verificada por check, miembros exactos |
| LICENSE/NOTICE en staging; metadatos, avisos de bundles/fuentes; 19 entradas externas; sin reutilizar `dist/` | Cumplido (§3–§4) |
| Sin componentes legacy/A ni privados en el paquete; sin tercer modo | Cumplido: 20 componentes retirados ausentes por check; perfil privado eliminado (HITL) |
| Build desde clon limpio con cachés explícitas; requisitos build/servicio/hijo; CI sintética sin secretos ni publicación | Workflow escrito; build local verificado. CI remota **no ejecutada**; el clon limpio se ensaya en T016 |
| Notas, hashes/manifiesto y procedimiento manual; activación del reporte privado | Cumplido (§3, §5, §6); nada remoto ejecutado |
| Instantánea saneada con docs públicas y sin Git/historia privada; correspondencia privada | Cumplido (§5); sin `git init`, commit público ni repositorio |

## 8. Validación

| Comando / check | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 8 OK |
| `uv run … pytest -q` | 1670 passed, 2 skipped (opt-in), 29 subtests |
| `alembic upgrade head` + `alembic check` con `HARNESS_DATABASE_URL` temporal | Sin operaciones nuevas. El `alembic check` por defecto apunta a `.local/harness.sqlite3` de desarrollo, en una revisión anterior, y falla por eso; la CI usa una BD temporal |
| `node --test frontend/tests/*.test.mjs`; `npm --prefix frontend run check` | 93/93; tsc correcto |
| `build_distribution.py` ×3 (uno antes del README final) y `check_distribution.py` | Build final y repetición con `SHA256SUMS` idéntico; check completo en verde (artefactos + journey instalado) |
| `uv lock --check --offline`; YAML del workflow con Ruby | Correctos; 10 pasos |
| `P011-T015_bundle_notices.py` | 58 paquetes cubiertos, sin assets binarios, sin patrones privados |
| `P011-T015_public_candidate.py` | 387 archivos, sin problemas |
| `P011-T014_public_docs_check.py` | 30 Markdown, 249 enlaces; layout y DNNN correctos |
| Consulta web de solo lectura (API de GitHub) | Releases y `action.yml` de checkout v7.0.1, setup-node v7.1.0 y setup-uv v10.3.2 en sus commits |

No ejecutado: CI remota, build en Linux u otra plataforma, ensayo desde la instantánea o clon limpio (T016), QA
visual, CLI/proveedores reales, red fuera de la consulta descrita, `git init`/commit/push/tag/Release/PyPI.

## 9. Notas para T016/T017

- Ensayar desde `.local/public-candidate` (o su regeneración con `--revision`) en una copia fuera del checkout; la
  primera ejecución de CI revelará requisitos del runner (identidad Git, versión de Git) no comprobables aquí.
- El texto «observers» en la ayuda de la CLI sigue pendiente (nota T014 → T017).
- `docs/archive/phase-010/SUMMARY.md` y otras evidencias privadas siguen nombrando el perfil retirado; son
  históricas y no entran en el candidato.
