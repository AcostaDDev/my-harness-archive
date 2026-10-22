# P010 — Cierre documental de la primera versión local

Fecha: 2026-10-22. Origen: `2e46c7143ea497774e813f092e36f10e7d662187` (T009 completada, D152).
Decisión: [D153](../../DECISIONS.md#d153--cierre-documental-de-p010-y-de-la-primera-versión-local).

## Resultado y autorización

El usuario pide continuar la siguiente tarea y finalizar con un commit en inglés. STATE/NEXT_STEPS señalan
P010-T010, después del dictamen favorable de T009 y de la decisión HITL D151. Se contrastan ROADMAP, plan,
matriz, entregas y revisión: doce tareas y siete criterios de salida cumplidos en el alcance declarado;
[dictamen de cierre](REVIEW.md). D114/D140 resuelven el precedente del cierre manual, sin una nueva elección de diseño.

Se completa la primera versión local con los límites de D151: A/B y D095 solo offline, validación real aplazada.
El paquete verificado por T009 sigue en `0.1.0`, fuente de producto `dd7b958`; no se construye ni instala otro wheel.
No hay tareas obligatorias pendientes del alcance declarado ni se atribuye uso real a la evidencia sintética.
[Resumen de entregas, paquete y límites](SUMMARY.md).

Se trasladan los 26 artefactos originales de `docs/phase/` y se copian STATE/NEXT_STEPS por bytes.
El [manifiesto](MANIFEST.json) fija los 28 originales respecto del HEAD de origen. Este registro se redacta
como artefacto T010 en `docs/phase/` y se archiva al cerrar; SUMMARY/REVIEW nuevos sintetizan el resultado sin
reescribir la revisión de T009. Los snapshots conservan estados y enlaces relativos en su contexto original.
La carpeta de trabajo queda vacía; P000–P009 permanecen intactas.

STATE compacta la base acumulada, NEXT_STEPS queda sin tareas y ROADMAP marca P010 completada con su archivo.
README anuncia la primera versión terminada dentro de su alcance; las referencias vigentes de DECISIONS,
ARCHITECTURE y flujos se reubican. Las decisiones históricas solo cambian referencias de navegación; D153
registra el cierre. Sin fase sucesora definida, el usuario elige la próxima prioridad entre las candidatas de ROADMAP.

Cierre manual separado del check READY del producto: no se registra ni ejecuta este repositorio en el harness,
ni se opera el Django hijo o el área de P009. No cambian producto, esquema, API, contratos, flujos, dependencias,
configuración global ni consentimientos. Sin tag, cambio de versión, push o publicación. El commit de cierre
lo autoriza expresamente el usuario en esta sesión.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Integridad: los 28 originales coinciden por bytes con sus blobs del commit de origen, tamaños y SHA-256
  del manifiesto; los 187 archivos de fases archivadas anteriores permanecen intactos. `docs/phase/` vacía.
- Enlaces: 25 Markdown vigentes/nuevos con 528 enlaces relativos/anclas válidos; 15 snapshots Markdown con
  119 enlaces relativos/anclas válidos en su contexto original. Sin referencias vigentes a las rutas retiradas.
- Parsers del producto: diez fases, siete criterios de P010, 153 decisiones únicas, ordenadas y con estado,
  cero tareas activas y doce en el plan archivado. Instrucciones y bloques correctos; STATE 7953 bytes,
  base acumulada 6548 y NEXT_STEPS 856, dentro de sus presupuestos.
- Los 29 bloques Mermaid vigentes coinciden por bytes con los del HEAD de origen; no se repite su parseo
  ni renderizado. Las decisiones históricas conservan el contenido salvo sus referencias de navegación.
  JSON del manifiesto y de la evidencia legibles; diff documental y movimientos revisados, `git diff --check` correcto.

La última suite completa y el paquete son los de T009/D152: pytest 1682 y 121 subtests, dos opt-in omitidas,
unittest 12, Node 82, tipos/build, Alembic temporal y verificador del wheel correctos. No se repiten pytest,
Node, tipos/build, Alembic, wheel o QA visual en este cierre sin cambios de producto. No se ejecutan instalaciones,
servicios, agentes, proveedores, smokes, operaciones de P009/ReferenceProject, push o publicación.

## Comprobación de bytes

Desde la raíz, solo biblioteca estándar y Git local de lectura:

```sh
python3 - <<'CHECK'
from hashlib import sha256
from pathlib import Path
import json, subprocess

manifest = json.loads(Path('docs/archive/phase-010/MANIFEST.json').read_text())
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

Los enlaces de snapshots se verifican en su contexto de origen, resolviendo primero en el commit del manifiesto;
los vigentes y las tres páginas nuevas se comprueban desde su ruta actual. MANIFEST no incluye los cuatro archivos
nuevos REVIEW, SUMMARY, P010_CIERRE y el propio manifiesto. La revisión de cierre no concede autoridad para
reproducir comandos históricos con proveedores o servicios.
