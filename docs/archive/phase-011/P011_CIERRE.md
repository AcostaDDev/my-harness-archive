# P011 — Cierre documental de la preparación pública

Fecha: 2026-10-24. Origen: `4eeda84a586240a4ac51e8ad78eed2c13a7e34ad` (T017 completada, D181).
Decisión: [D182](../../DECISIONS.md#d182--cierre-documental-de-p011-y-preparación-pública-archivada).

## Resultado y autorización

El usuario pide continuar con la siguiente tarea y finalizar con un commit en inglés. STATE/NEXT_STEPS señalan
P011-T018, después del dictamen favorable de T017. Se contrastan ROADMAP, plan, entregas, revisión y expediente:
veinticuatro tareas y diez criterios de salida cumplidos en el alcance declarado; [dictamen de cierre](REVIEW.md).
D114/D140/D153 resuelven el precedente del cierre manual, sin una nueva elección de diseño; no hay ambigüedad que
requiera HITL. [Resumen de entregas, candidato y límites](SUMMARY.md).

Se trasladan los 61 artefactos originales de `docs/phase/` (incluidas 18 capturas de T024, scripts y manifiestos) y
se copian STATE/NEXT_STEPS por bytes. El [manifiesto](MANIFEST.json) fija los 63 originales respecto del commit de
origen. Este registro, SUMMARY y REVIEW son nuevos y sintetizan el resultado sin reescribir la revisión de T017. Los
snapshots conservan estados, enlaces relativos y comandos en su contexto original. La carpeta de trabajo queda vacía
(se elimina además su `__pycache__` ignorado); P000–P010 permanecen intactas.

STATE compacta la base acumulada, NEXT_STEPS queda sin tareas y ROADMAP marca P011 completada con su archivo. Las
referencias vigentes de DECISIONS (D154–D181), ARCHITECTURE, SPECIFICATION y dos flujos se reubican al archivo; las
decisiones históricas solo cambian referencias de navegación y D182 registra el cierre. README, README.es y
`docs/public/` no cambian: forman parte del candidato aprobado en T017. Sin fase sucesora definida.

Cierre manual separado del check READY del producto: no se registra ni ejecuta este repositorio en el harness, ni se
opera el Django hijo o el área de P009. No cambian producto, esquema, API, contratos, flujos, dependencias, paquete,
configuración global ni consentimientos. Sin tag, cambio de versión, creación de repositorio, push, cambio de
visibilidad, Release ni publicación. El commit de cierre lo autoriza expresamente el usuario en esta sesión.

## Verificación

- Integridad: los 63 originales coinciden por bytes con sus blobs del commit de origen, tamaños y SHA-256 del
  manifiesto; los 219 archivos de fases archivadas anteriores permanecen intactos. `docs/phase/` vacía. El diff solo
  toca `docs/`, sin cambios en `docs/public/`.
- Enlaces (`P011-T013_links.py`): 26 Markdown vigentes/nuevos (incluidos README y README.es) con 738 enlaces
  relativos/anclas válidos; 28 snapshots Markdown con 194 válidos en su contexto original, desde un worktree del
  commit de origen. Sin referencias vigentes a `docs/phase/P011*`.
- Parsers del producto: once fases, diez criterios de P011, 182 decisiones únicas, consecutivas y con estado, con
  índice de 182 filas en orden; cero tareas activas y veinticuatro en el plan archivado. Sin bloques gestionados;
  STATE 10.687/24.576 bytes, base acumulada 8.718/12.288 y NEXT_STEPS 1.047/49.152, dentro de sus presupuestos
  (resuelve H3 de T017).
- Los 70 bloques Mermaid de los 45 documentos vigentes, incluidos los públicos, coinciden por bytes con los del commit
  de origen; no se repite su parseo. JSON del manifiesto legible; `git diff --check` correcto.
- Candidato: la instantánea regenerada desde el commit de origen (procedimiento de abajo) y desde el árbol final de
  este cierre da 387 archivos, 5.402.952 bytes, sin problemas y manifiesto idéntico al archivado
  (`74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71`). El comprobador de la documentación pública
  (`P011-T014_public_docs_check.py`) sigue en verde: 30 Markdown, 249 enlaces, 79 decisiones públicas.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 8 checks correctos.

Las últimas suites completas y el paquete son los de T017/D181: pytest 1671 y 29 subtests, dos opt-in omitidas,
unittest 8, Node 95, dos builds idénticos y `check_distribution` correctos. No se repiten pytest, Node, tipos/build,
Alembic, build del paquete, ensayo desde clon limpio ni QA de navegador en este cierre sin cambios de producto. No se
ejecutan instalaciones, servicios, agentes, CLI reales, proveedores, CI remota, operaciones de P009/ReferenceProject, push
ni publicación. Los dos scripts con raíz fija (`P011-T014`, `P011-T015`) se ejecutan sobre sus bytes archivados con
una ruta de origen simulada, sin copiarlos de vuelta a `docs/phase/`.

## Reproducir el candidato

El paso 1 del [expediente](P011_EXPEDIENTE_APERTURA.md) cita el script en su ruta de origen, que deriva la raíz del
repositorio de su propia ubicación. Archivado, se ejecuta desde un worktree temporal del commit de T017; usa solo la
biblioteca estándar (comprobado con Python 3.14.4) y no modifica este checkout más allá del registro del worktree:

```sh
git worktree add --detach <tmp>/wt-t017 4eeda84a586240a4ac51e8ad78eed2c13a7e34ad
python3 <tmp>/wt-t017/docs/phase/P011-T015_public_candidate.py \
  --revision 4eeda84a586240a4ac51e8ad78eed2c13a7e34ad --out <dir> \
  --private-manifest <tmp>/priv.tsv --public-manifest <tmp>/pub.sha256
git worktree remove <tmp>/wt-t017
```

`public_manifest_sha256` debe ser `74cc9141…ea71`; si no, parar. El commit de este cierre produce el mismo árbol,
porque solo cambia `docs/` privada. El resto del expediente no depende de rutas de `docs/phase/`.

## Comprobación de bytes

Desde la raíz, solo biblioteca estándar y Git local de lectura:

```sh
python3 - <<'CHECK'
from hashlib import sha256
from pathlib import Path
import json, subprocess

manifest = json.loads(Path('docs/archive/phase-011/MANIFEST.json').read_text())
for item in manifest['files']:
    archived = Path(item['target']).read_bytes()
    original = subprocess.check_output([
        'git', '--no-lazy-fetch', 'cat-file', 'blob',
        manifest['source_commit'] + ':' + item['source'],
    ])
    assert archived == original
    assert len(archived) == item['size_bytes']
    assert sha256(archived).hexdigest() == item['sha256']
print(len(manifest['files']), 'originales intactos')
CHECK
```

MANIFEST no incluye los cuatro archivos nuevos REVIEW, SUMMARY, P011_CIERRE y el propio manifiesto. La revisión de
cierre no concede autoridad para reproducir comandos históricos con proveedores o servicios ni para ejecutar ningún
paso remoto del expediente.
