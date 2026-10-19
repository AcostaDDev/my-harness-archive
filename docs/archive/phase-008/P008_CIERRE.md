# P008 — Cierre y archivo documental

Fecha: 2026-10-19. Origen: `9c8887989332028a906349351e5554b4e2ad7a80` (quinta revisión de salida).
Decisión: [D114](../../DECISIONS.md#d114--cierre-documental-manual-de-p008).

## Resultado y autorización

El usuario pide continuar con la siguiente tarea y hacer commit, después de D113. STATE y NEXT_STEPS señalan
el cierre y archivo documental de P008. Se cierra la fase en ese alcance, con sus veinte tareas completadas
y siete criterios de salida cumplidos offline según [REVIEW](REVIEW.md).

Este repositorio se desarrolla manualmente y sigue sin registrarse en el producto. No se ejecuta el harness,
un check READY, SQLite, agentes, proveedores o smokes; no se crea tag de fase ni se simula una operación
gestionada. La autorización de continuación cubre el cierre documental y su commit. ROADMAP no define
sucesora: STATE y NEXT_STEPS quedan sin fase activa ni tareas, a la espera de la próxima prioridad del usuario.

## Cambios

- Los 33 archivos versionados de `docs/phase/` se mueven al archivo, con sus bytes intactos. También se copian
  por bytes STATE y NEXT_STEPS anteriores a esta tarea. El [manifiesto](MANIFEST.json) acredita los 35 originales
  respecto del HEAD de origen. La carpeta de trabajo queda vacía; solo se retiran sus cachés Python derivados.
- REVIEW sintetiza D113 y sus límites; SUMMARY resume la fase, enlaza las entregas y explica cómo consultar
  snapshots y reproducir scripts en su contexto original. Los originales no se editan para actualizar enlaces,
  estados o comandos históricos; tampoco cambian scripts/JSON ni los hashes cruzados de las revisiones.
- STATE incorpora la base de P008; NEXT_STEPS queda sin tareas. ROADMAP marca P008 completada y enlaza su
  archivo, conservando objetivo y criterios. Se añade D114; los enlaces vigentes de las ADR anteriores y
  README se reubican sin cambiar sus decisiones. Las fases P000–P007 archivadas permanecen intactas.
- No cambian modelos, flujos de producto, contratos, esquema, API, frontend, dependencias, prompts o versiones
  congeladas. SPECIFICATION, ARCHITECTURE, DDBB-DIAGRAM y los diagramas de flujos no requieren cambios.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Integridad: los 35 originales son idénticos a sus blobs en el commit de origen, con rutas completas,
  tamaños y SHA-256 correctos. Todos los hashes cruzados de las cinco revisiones coinciden. Los 33 movimientos
  de artefactos aparecen en Git con similitud del 100 %; STATE y NEXT_STEPS originales también están intactos.
  Los cinco commits de reproducción indicados en SUMMARY contienen exactamente sus scripts archivados.
- Documentación: 46 Markdown activos y del nuevo archivo, con 506 enlaces relativos/anclas válidos;
  161 enlaces de snapshots comprobados desde su contexto original. Los enlaces activos se comprueban en
  su ubicación actual. No quedan referencias activas a las rutas retiradas de `docs/phase/`.
- Los parsers reconocen 114 decisiones, ocho fases, cero tareas activas y las veinte tareas del plan archivado.
  Instrucciones, bloques y presupuestos de STATE/base/NEXT_STEPS correctos; fases anteriores intactas.
- Veinte diagramas Mermaid aceptados: siete ER y tres secuencias con `mermaid.parse`, siete flowcharts con
  su parser sin sanitización de etiquetas y tres estados con su gramática sin extracción dependiente del DOM.
  Verificación de sintaxis, sin renderizado. Diff revisado y `git diff --check` correcto.

La suite completa de 1.436 pytest y 121 subtests, 75 Node, tipos/build, Alembic temporal y OpenAPI pasa en D113.
No se repite aquí: este cierre modifica documentación y mueve evidencia preservada. No se ejecutan UI visual,
renderizado DOM, Django/ruff/mypy reales, proveedores reales, smokes, push o publicación; no hay datos privados
ni cambios de configuración global.

## Comprobación de bytes

Desde la raíz del repositorio, solo biblioteca estándar y Git de lectura local:

```sh
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
import json, subprocess

manifest = json.loads(Path('docs/archive/phase-008/MANIFEST.json').read_text())
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

Las verificaciones de enlaces de los snapshots usan la ruta original del manifiesto como base y traducen los
destinos archivados por ese mismo mapa. Los enlaces activos y de REVIEW/SUMMARY/este registro se validan desde
su ruta actual. Así se acredita su contexto sin reescribir el historial. El manifiesto no incluye las cuatro
páginas/artefactos nuevos de este cierre: REVIEW, SUMMARY, este registro y el propio MANIFEST.
