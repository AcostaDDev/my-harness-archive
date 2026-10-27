# P013 — Cierre documental de la instalación guiada

Fecha: **2026-10-27**. Origen: `ff5109df44d65665db1e33a6f3f99f241d3928a0` (T014/D231).
Decisión: [D232](../../DECISIONS.md#d232--cierre-documental-de-p013-e-instalación-guiada-archivada).

## Resultado y autorización

El usuario pide continuar con la siguiente tarea y finalizar con un commit en inglés. STATE/NEXT_STEPS señalan
T015 tras la revisión favorable de T014, que acredita ocho criterios sin correcciones obligatorias. D182/D212
y el contrato documental de SPECIFICATION resuelven el procedimiento manual sin elección de diseño pendiente:
no se necesita HITL para archivar. Los suplementos 2026-10-26 (D213/D214, sin fase) estaban en docs/phase y
el cierre la vacía por contrato; se archivan aquí, con su procedencia en el manifiesto.

**T015 completada:** [resumen](SUMMARY.md), [revisión de cierre](REVIEW.md), archivo por bytes y documentos vivos.
Se trasladan los 72 artefactos versionados de docs/phase, con sus subdirectorios de capturas QA y logs T013,
y se copian STATE/NEXT_STEPS exactos de T014. El [manifiesto](MANIFEST.json) fija los 74 originales
(1.498.064 bytes) con origen/destino, tamaño y SHA-256. Se retiran los __pycache__ ignorados que dejaron los
comprobadores en docs/phase y en el archivo P012, sin incorporar temporales. P000–P012 permanecen intactas.
No se reescriben snapshots para cambiar estados, enlaces o comandos.

SUMMARY, REVIEW, este registro, MANIFEST y comprobador/resultado son nuevos. El snapshot de NEXT_STEPS y el
expediente dicen «T015 pendiente» porque conservan el estado anterior; el cierre se acredita aquí y en D232.
STATE compacta la base y queda sin fase activa; NEXT_STEPS sin tareas ni sucesora; ROADMAP marca P013 completada.
DECISIONS, DDBB-DIAGRAM y siete flujos solo reubican enlaces a los originales archivados; SPECIFICATION y
ARCHITECTURE además actualizan sus frases de estado de cierre, sin cambiar contratos ni diagramas.
README, README.es y docs/public permanecen idénticos; candidato y paquete T013 sin regeneración o sustitución.

Cierre manual separado del check READY del producto. Sin registrar/ejecutar este repositorio con el harness,
servicios, CLI reales, agentes, proveedores o smokes. Sin cambios de producto, datos, API, dependencias,
instalaciones, configuración global, versión, tag, push o publicación. El siguiente paso corresponde al
usuario sobre el [expediente P013](P013_EXPEDIENTE_APERTURA.md), con owner/repo, visibilidad, identidad pública
y permisos pendientes. Los consentimientos operativos anteriores no se renuevan.

## Verificación

Comprobador nuevo de lectura local, sin servicios, builds, instalaciones ni red:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -B docs/archive/phase-013/P013-T015_check.py
git diff --check
```

El [resultado](P013-T015_COMPROBACION.json) registra:

- Los 74 originales coinciden con sus blobs en T014, tamaños y SHA-256; el archivo contiene solo ellos y los
  seis documentos nuevos. Los 334 archivos anteriores de archive permanecen intactos; docs/phase queda vacía.
- Trece fases con contratos sin cambios y ocho criterios P013, 232 decisiones consecutivas con estado e índice,
  cero tareas activas y quince en el plan archivado. Cuerpos D001–D231 idénticos salvo enlaces de navegación.
  STATE 12.409/24.576 bytes, base 10.782/12.288 y NEXT_STEPS 1.397/49.152.
- 36 documentos vigentes/nuevos con 1.158 enlaces/anclas válidos; 27 vigentes idénticos a T014 salvo
  enlaces reubicados; 23 snapshots con 245 enlaces comprobados en sus rutas y commit originales;
  42 diagramas Mermaid vigentes iguales por bytes.
- Fuente `984c287` reexportada en memoria igual al manifiesto `ea0f74e9…00c428` y a las fuentes públicas actuales.
  `my_harness_dist_p013` con 445 archivos/6.389.580 bytes, rutas/directorios/hashes/modos exactos y sin Git;
  documentación pública del candidato correcta (50 documentos/403 enlaces). Candidatos D214/P012/P011, siete
  inventarios protegidos de T013 y los 13 archivos del paquete distribution-1 conservados por hash.
- Diff exclusivamente documental privado, sin cambios en docs/public ni README; JSON legible y diff revisado.

Las últimas suites completas siguen siendo T013: 2048 pytest/29 subtests, dos opt-in omitidas, 8 unittest,
155 Node, tipos/build, Alembic temporal y distribución instalada sintética. No se repiten suites, builds,
instalaciones, QA de navegador, fixtures o servicios. No se ejecutan CI remota, autenticación GitHub, push,
publicación ni comandos históricos del archivo.

## Reproducción y contexto histórico

El expediente T014 fija el commit T013 `a0cab9e51f6440b827825d5491313f0542e4197e` y un worktree temporal para
reproducir el candidato con el adaptador en docs/phase de ese commit; el archivo no cambia ese procedimiento.
Los scripts archivados derivan la raíz desde su ruta: no ejecutarlos directamente desde archive. El comprobador
T015 carga los auxiliares T013/T014 con su ruta original simulada, sin modificar snapshots, y puede ejecutarse
desde su ruta archivada. Conservar los comandos congelados no autoriza ejecutarlos.
