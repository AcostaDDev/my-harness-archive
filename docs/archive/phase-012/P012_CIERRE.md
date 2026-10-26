# P012 — Cierre documental de la validación real

Fecha: **2026-10-26**. Origen: `ce4b5d2f8ed1a1ac1af9cec00316b10b1d95a814` (T006/D211).
Decisión: [D212](../../DECISIONS.md#d212--cierre-documental-de-p012-y-validación-real-archivada).

## Resultado y autorización

El usuario pide commitear la tarea anterior, continuar con la siguiente y finalizar con commit en inglés.
Se verifica y commitea T006 como `ce4b5d2`; STATE/NEXT_STEPS señalan T007. La revisión T006 acredita siete
criterios con dictamen favorable y sin correcciones obligatorias. D182 y los cierres anteriores resuelven el
procedimiento manual sin una elección de diseño pendiente: no se necesita HITL para archivar.

**T007 completada:** [resumen](SUMMARY.md), [revisión de cierre](REVIEW.md), archivo por bytes y documentos vivos.
Se trasladan 40 artefactos de docs/phase y se copian STATE/NEXT_STEPS exactos de T006. El
[manifiesto](MANIFEST.json) fija los 42 originales con origen/destino, tamaño y SHA-256.
Se retira el __pycache__ ignorado de los comprobadores, sin incorporar temporales al archivo.
P000–P011 permanecen intactas. No se reescriben snapshots para cambiar estados, enlaces o comandos.

SUMMARY, REVIEW, este registro, MANIFEST y comprobador/resultado son nuevos. El snapshot de NEXT_STEPS y el
expediente dicen «T007 pendiente» porque conservan el estado anterior; el cierre se acredita aquí y en D212.
STATE compacta la base y queda sin fase activa; NEXT_STEPS sin tareas ni sucesora; ROADMAP marca P012 completada.
DECISIONS, ARCHITECTURE, SPECIFICATION y el flujo de consulta solo reubican enlaces a los originales archivados.
README, README.es y docs/public permanecen idénticos; candidato y paquete T005 sin regeneración o sustitución.

Cierre manual separado del check READY del producto y del cierre real del hijo TypeScript de T004.
Sin registrar/ejecutar este repositorio con el harness, servicios, CLI reales, agentes, proveedores o smokes.
Sin cambios de producto, datos, API, flujos, dependencias, configuración global, versión, tag, push o publicación.
El siguiente paso corresponde al usuario sobre el [expediente P012](P012_EXPEDIENTE_APERTURA.md), con owner/repo,
visibilidad e identidad pública pendientes. Los consentimientos operativos anteriores no se renuevan.

## Verificación

Comprobador nuevo de lectura local, sin servicios ni red:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/archive/phase-012/P012-T007_check.py
git diff --check
```

El [resultado](P012-T007_COMPROBACION.json) registra:

- Los 42 originales coinciden con sus blobs en T006, tamaños y SHA-256. Los 286 archivos anteriores
  de archive permanecen intactos; docs/phase queda vacía.
- Doce fases con siete criterios P012 conservados, 212 decisiones consecutivas con estado e índice,
  cero tareas activas y trece en el plan archivado. STATE/base/NEXT_STEPS dentro de sus presupuestos.
- 35 documentos vigentes/nuevos con 957 enlaces/anclas válidos; 26 snapshots con 269 enlaces comprobados
  en sus rutas y commit originales. Decisiones D001–D211 idénticas salvo enlaces de navegación;
  35 diagramas vigentes iguales por bytes. STATE 12.147/24.576 bytes, base 10.577/12.288 y
  NEXT_STEPS 1.346/49.152.
- Exportación en memoria del commit T005 y de las fuentes finales idénticas al manifiesto público aprobado:
  401 archivos/5.480.755 bytes. Destino local con lista/hashes/modos iguales, sin Git/symlinks; 387 hashes P011,
  wheel/sdist/pylock/SHA256SUMS conservados. Documentación pública sobre el candidato correcta.
- Diff exclusivamente documental privado y sin cambios en docs/public; JSON legible y diff revisado.

Las últimas suites completas siguen siendo T005: 1760 pytest/29 subtests, dos opt-in omitidas, 8 unittest,
119 Node, tipos/build, Alembic temporal, distribución instalada sintética y 36 diagramas públicos verificados.
No se repiten suites, builds, instalaciones, QA de navegador, pruebas de fixtures o consultas operativas.
No se ejecutan CI remota, autenticación GitHub, push, publicación ni comandos históricos del archivo.

## Reproducción y contexto histórico

El expediente T006 ya fija el commit T005 `99b1b9954d543259a84956940ea8543035551077` y un worktree temporal
para reproducir el candidato con el script en docs/phase; el archivo no cambia ese procedimiento.
Manifiesto esperado: `cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a`.
Los scripts originales derivan la raíz desde su ruta: no ejecutarlos directamente desde archive.
El comprobador T007 carga solo utilidades estáticas con su ruta original simulada, sin modificar snapshots.
La reproducción materializada y cualquier acción posterior se revisarán bajo la instrucción de apertura;
T007 solo contrasta bytes en memoria y conserva los árboles externos.

El comprobador T007 puede ejecutarse desde su ruta archivada. Los demás comandos/propuestas congelados
se interpretan desde sus rutas de origen y commits identificados; conservarlos no autoriza ejecutarlos.
