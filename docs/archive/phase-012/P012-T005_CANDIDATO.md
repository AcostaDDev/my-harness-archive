# P012-T005 — Alcance público y candidato actualizados

Fecha: 2026-10-26. Base: `b3c4bbe494b137d6bb91c721b209fe71a8851f16`, checkout inicialmente limpio.
Tarea: [T005](../NEXT_STEPS.md#p012-t005--alcance-público-y-candidato-actualizados).
Decisión: [D210](../DECISIONS.md#d210--p012-t005-alcance-público-y-candidato-verificados).

## 1. Alcance y procedencia

Actualización documental y preparación offline: README/README.es, CHANGELOG y baseline pública autocontenida,
con límites privados al día. Sin cambios de producto, modelos, migraciones, API, dependencias o versiones.
La versión sigue siendo candidata `0.1.0`; v0.2.0 sigue reservada al modo continuo, con P001 pública sin tareas.
No se reescriben originales de fases anteriores ni resultados reales. Cero llamadas nuevas a proveedores.

| Fila pública | Evidencia privada que sustenta la redacción y límite |
|---|---|
| Motor/fases/cierre | [T002](P012-T002_RESULTADO_T011.md), [T004](P012-T004_CONTINUACION_T013.md): tareas COMMITTED con cli-14; READY/cierre/archivo TypeScript acreditados tras HITL |
| Cuatro parejas | Evidencia histórica D071/D139 anterior a cli-14; P012 solo revisor Claude 2.1.310 → ejecutor Codex 0.164.0. Sin trasladar las cuatro a las versiones actuales |
| Receta Django | Creación/tareas/cierre históricos D139, macOS ARM64/Python 3.13. P012 usa Django existente/perfil declarado; no acredita creación con receta Django v2 |
| TypeScript nuevo | [Preparación](P012-T004_TYPESCRIPT_REAL.md) y [continuación](P012-T004_CONTINUACION_T013.md): v2/es, caché local, tarea y cierre; sin extender cobertura de la suite a espacios interiores |
| Recetas/idiomas | Solo TypeScript v2/es real. Django v2 y matriz completa de idiomas siguen con evidencia offline |
| B/perfil declarado | [B](P012-T002_INCORPORACION_REAL.md), [B2](P012-T002_CONTINUACION_T009.md) y [clon](P012-T002_RESULTADO_T011.md): originales intactos, idempotencia de B, tarea con v8/seis validaciones/13 JUnit. Formateador ejecutado sobre dos archivos sin cambios, sin afirmar reparación automática |
| Chat/backup/restauración | [Chat/API](P012-T003_CHAT_BACKUP_REAL.md) y [UI](P012-T003_UI_RESULTADO_T012.md): dos respuestas, comando sin modelo, confirmación QUEUED sin ejecución; consulta restaurada con hashes/filas iguales, guardia 409 e identidad histórica incierta conservada |
| Runs/métricas/exportación | Lecturas reales restauradas acreditadas; historiales grandes y vista previa de exportación solo sintéticos |

README y README.es tienen tablas equivalentes. STATE público recoge límites y fallos conservados; ROADMAP retira
el recorrido B/D095 de los huecos pendientes, conservando la cobertura más amplia sin acreditar. ARCHITECTURE y
SPECIFICATION describen v8, consulta y vínculo del recibo. Se añade la decisión pública D194 equivalente técnica
(< D200, manteniendo la numeración de partida y sin copiar decisiones operativas privadas); D151 queda conservada
con su aplazamiento histórico, superado solo en el alcance que declara D194.

Los flujos públicos incorporan consulta de backups y actualizan recibo/resolución, capabilities y compatibilidad v8
(presets/idioma incluidos). El diagrama de datos solo cambia dos menciones de formatos en la prosa: ER/esquema
sin cambios. No se alteran fuentes de recetas congeladas.

## 2. Candidato y frontera pública

Copia de la herramienta T015 en [P012-T005_public_candidate.py](P012-T005_public_candidate.py), con salidas T005.
Lista positiva y exclusiones conservadas: sin `.git`, historia privada, docs privadas, evidencia real, credenciales,
estado, cachés o symlinks. Los 25 archivos de `docs/public/` sustituyen las instrucciones/docs privadas.

- Árbol final nuevo: `.local/p012-t005/candidate-final/`, **401 archivos, 5.480.755 bytes**.
- [Manifiesto publicable](P012-T005_MANIFIESTO_PUBLICO.sha256):
  **`cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a`**.
- [Correspondencia privada](P012-T005_MANIFIESTO_PRIVADO.tsv): origen, destino, hash, modo y motivo.
  Sus hashes de rutas excluidas reflejan la exportación del árbol de trabajo, no una congelación de los documentos
  privados que registran después este resultado.
- [Diff de lista frente a P011](P012-T005_DIFF_PUBLICO.json): **14 añadidos, 38 modificados, 0 eliminados,
  349 idénticos**. Los añadidos son consulta/componentes/tests de T012, regresiones/presets de T010/T011 y el
  flujo público. Los modificados corresponden a T008/T010–T013 y la documentación de esta tarea.
- Manifiesto P011 conservado: `74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71`, 387 archivos.
  `my_harness_dist` se leyó y coincide exactamente con él; sin Git ni symlinks.

La validación se hace sobre `.local/p012-t005/validation/`, copia del candidato con cachés locales explícitas,
venv/build generados y BD Alembic nueva. El árbol final queda limpio de esos auxiliares. Los últimos ajustes solo
cambian prosa/diagramas públicos y se reflejan en la copia validada; código, tests, README y paquete son iguales.

## 3. Paquete nuevo

Build offline desde la copia pública en `.local/p012-t005/package/`; no se reutiliza `dist/` ni una instalación
operativa. [Checksums conservados](P012-T005_PAQUETE.sha256):

| Artefacto | SHA-256 |
|---|---|
| `harness_local-0.1.0-py3-none-any.whl` | `eef56a29c268839487f23e53493fd728361e31589ce0535a1f3f01e50b4504ab` |
| `harness_local-0.1.0.tar.gz` | `0f290f05d1a93f5117d0eac01f1b6b175bad61ad1e88613580441cce3072a384` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |

`check_distribution.py` confirma miembros exactos/metadatos/licencias/SHA256SUMS y el wheel instalado en venv
temporal, con agentes falsos y proyectos sintéticos: UI/assets/API/sesión, D088/definición/tarea/commit/restart,
errores y evidencia restaurada correctos. Sin operar fixtures reales ni este repositorio con el harness.

## 4. Validación

Desde la copia del candidato salvo los comprobadores privados; todo offline, sin descargas:

| Comando/check | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 8 OK |
| `UV_CACHE_DIR=<caché local> uv run --frozen --offline pytest -q` | **1760 passed, 2 skipped (opt-in), 29 subtests passed**, 164,49 s; 10 avisos de deprecación Starlette/httpx |
| Alembic `upgrade head` + `check`, `HARNESS_DATABASE_URL` sobre SQLite nueva de T005 | 0025; sin operaciones nuevas |
| `node --test frontend/tests/*.test.mjs` | **119/119** |
| `npm --prefix frontend run check` | TypeScript correcto |
| `… python scripts/build_distribution.py --out-dir ../package` | Build Vite/sdist/wheel/pylock correcto; aviso habitual de tamaño de bundle |
| `… python scripts/check_distribution.py --dist ../package` | Correcto, incluido recorrido instalado sintético y parada del servicio temporal |
| [Comprobador público](P012-T005_public_docs_check.py) sobre overlay y con `--candidate` | **31 Markdown/260 enlaces**, 80 decisiones, 61 referencias DNNN de código y 63 de documentos; sin referencias privadas o enlaces rotos |
| Mermaid local sobre 15 flujos y DDBB públicos | 36 diagramas parseados, cero fallos; solo sintaxis, sin QA visual nueva |

Los primeros envoltorios zsh de unittest/build/pytest usaron por error la variable reservada `status` y acabaron
con error del envoltorio después de ejecutar los comandos; los logs conservan sus resultados completos correctos.
No fue fallo de suite/build ni se repitieron suites para ocultarlo. Logs locales en `.local/p012-t005/logs/`.

Comandos para regenerar y contrastar el árbol tras el commit (salidas nuevas, fuera de las ya revisadas):

```sh
python3 docs/phase/P012-T005_public_candidate.py --revision HEAD --out .local/p012-t005/reproduced \
  --private-manifest .local/p012-t005/reproduced.tsv --public-manifest .local/p012-t005/reproduced.sha256
cmp docs/phase/P012-T005_MANIFIESTO_PUBLICO.sha256 .local/p012-t005/reproduced.sha256
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P012-T005_public_docs_check.py \
  --candidate .local/p012-t005/reproduced
```

## 5. Sustitución autorizada y siguiente tarea

HITL sobre candidato/paquete/checks ya revisables: **«Sí, sustituir y conservar P011»**. T005 exigía autorización
expresa para sustituir `my_harness_dist`; no se interpretó la continuación genérica como permiso para sobrescribirla.
Tras revalidar lista/hashes de P011 y del árbol final, y la ausencia del destino de conservación:

1. Renombrado `../my_harness_dist` → `../my_harness_dist_p011_74cc9141`.
2. Copia del candidato final → `../my_harness_dist`.
3. Verificados **401 hashes y modos** nuevos, **387 hashes** conservados de P011, listas exactas, ausencia de
   symlinks/Git y bytes idénticos de los 401 archivos revisados en la copia de validación.

[Registro de sustitución](P012-T005_SUSTITUCION.json). Sin repositorio Git público, push o publicación.
**T005 completada.** Siguiente: **T006**, revisión de salida y expediente de apertura nuevo; P012 continúa abierta.
No ejecutado: proveedores/CLI reales, fixtures/SQLite operativos, `scripts/dev`, red, CI remota, otras plataformas,
QA de navegador o accesibilidad nueva, repetición de los recorridos P012, tag de my_harness, push o publicación.

## 6. Revisión final del checkout

Parsers: **12 fases, 13 tareas y 210 decisiones**. Presupuestos privados STATE/base/NEXT_STEPS:
**23.514/24.576**, **9.171/12.288** y **41.317/49.152 bytes**. **728 enlaces/anclas privados** correctos;
D001–D209 conservadas por cuerpos, snapshots archivados intactos y `git diff --check` correcto.
El comprobador público también pasa sobre el destino externo sustituido. Diff revisado dentro de las rutas de T005;
los únicos efectos fuera son candidato/paquete/checks sintéticos y la sustitución autorizada, sin operación real.
