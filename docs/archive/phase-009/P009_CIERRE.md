# P009 — Cierre y archivo documental

Fecha: 2026-10-21. Origen: `422357145d4120a9d55a65783864054ee3e96378` (T012 completada, D139).
Decisión: [D140](../../DECISIONS.md#d140--cierre-documental-manual-de-p009).

## Resultado y autorización

El usuario pide continuar la siguiente tarea y finalizar con un commit en inglés. STATE/NEXT_STEPS señalan
revisar el informe de salida y cerrar/archivar P009 en una tarea separada de T012. Se contrasta la salida con
ROADMAP y las entregas: veinte tareas completadas, siete criterios cumplidos; [dictamen](REVIEW.md).
El precedente D114 resuelve el cierre manual de este repositorio sin registrarlo en el producto.

Se mueven los 26 artefactos de `docs/phase/` y se copian STATE/NEXT_STEPS a `archive/phase-009/`, por bytes.
El [manifiesto](MANIFEST.json) fija los 28 originales respecto del HEAD de origen. REVIEW/SUMMARY sintetizan
resultado y límites; este registro deja la verificación reproducible. La carpeta de trabajo queda vacía.

STATE compacta la base acumulada, NEXT_STEPS queda sin tareas y ROADMAP enlaza P009 completada. Las referencias
vigentes se reubican al archivo, incluidas las de SPECIFICATION, ARCHITECTURE, diagramas y ayudas CLI. README
y la prosa de project-creation/project-definition dejan de presentar la fase y el piloto como pendientes;
los diagramas y el comportamiento operativo no cambian. Las ADR históricas solo cambian sus referencias de navegación; D140 registra
el cierre. Las fases archivadas anteriores conservan todos sus bytes. Sin sucesora, el usuario elige prioridad.

Las observaciones del piloto quedan en ROADMAP como candidatas sin fase. El cierre no toca el Django hijo
ni su área operativa, ni ejecuta el harness sobre este repositorio, ni crea check READY/tag propios. Tampoco cambian
código, esquema, API, dependencias, configuración global, contratos, flujos o consentimientos.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Integridad: los 28 originales coinciden por bytes con sus blobs en el commit de origen, y sus tamaños y
  SHA-256 coinciden con MANIFEST. Los 155 archivos de fases archivadas anteriores permanecen intactos.
- Enlaces: 25 Markdown vigentes/nuevos con 452 enlaces relativos/anclas válidos; 24 snapshots Markdown con
  143 enlaces relativos/anclas válidos en su contexto original. No quedan referencias vigentes a las rutas
  retiradas de `docs/phase/`.
- Parsers del producto: nueve fases, siete criterios de P009, 140 decisiones únicas y ordenadas con estado,
  cero tareas activas y las veinte tareas del plan archivado. Instrucciones y bloques correctos; STATE 6172
  bytes, base 5061 y NEXT_STEPS 810, dentro de sus presupuestos.
- Todos los bloques Mermaid vigentes coinciden por bytes con los del HEAD de origen; no se repite su parseo
  o renderizado. Diff limitado a documentación y movimientos de artefactos; revisado, con
  `git diff --check` correcto.

La última suite completa es la de T020: 1597 pytest correctos y uno omitido, 81 Node, tipos/build y OpenAPI
correctos. No se repiten pytest completo, Node, tipos/build, Alembic ni wheel en este cierre documental.
No se ejecutan servicios, Django/ruff/mypy reales, agentes, proveedores, smokes, push o publicación.

## Comprobación de bytes

Desde la raíz, solo biblioteca estándar y Git de lectura local:

```sh
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
import json, subprocess

manifest = json.loads(Path('docs/archive/phase-009/MANIFEST.json').read_text())
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
PY
```

Los enlaces de snapshots se verifican en el contexto de origen del manifiesto, traduciendo las rutas archivadas
por ese mapa; los vigentes y las tres páginas nuevas se comprueban desde su ruta actual. Los originales no se
reescriben para adaptar sus enlaces o estados históricos. MANIFEST no incluye los cuatro archivos nuevos
REVIEW, SUMMARY, P009_CIERRE y el propio manifiesto.
