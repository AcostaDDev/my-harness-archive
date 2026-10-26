# P013-T001 — Validación y límites

Fecha: 2026-10-26. Base: `2e682b1`; checkout limpio al comenzar. Encargo: continuar siguiente tarea y
finalizar con commit local en inglés. [Contrato](P013-T001_CONTRATO.md),
[D216–D218](../DECISIONS.md#d216--p013-t001-instalación-aislada-y-arranque-sin-configuración).

## Resultado y revisión de alcance

T001 completa el contrato documental, sin implementar producto. Define instalación/actualización y arranque,
autoridad/versiones/CAS/recuperación, modos sin configuración/consulta, reinicios/activación/trabajo congelado,
dos altas con commits documentales previos a preparación, perfil propio/evidencia y API/UI/matriz de fallos.
SPECIFICATION/ARCHITECTURE y flujos distinguen diseño de comportamiento actual. DDBB-DIAGRAM solo enlaza el
trabajo futuro: continúa en revisión `0025`, 51 tablas. STATE/NEXT_STEPS/ROADMAP/plan señalan T002 siguiente.

Contraste de D049/D051/D078/D095/D118/D150/D157/D161/D174/D194/D215 con consumidores documentados en
el contrato §1. D119/D168/D207 precisan recetas y vínculo de recibos. Sin contradicciones pendientes de HITL;
las elecciones de T001 están dentro del diseño delegado por D215. No se toman rutas, proveedores/modelos o
consentimientos históricos como valores operativos nuevos del usuario.

## Checks

- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**, sin procesos de producto.
- Parsers puros `parse_roadmap`, `plan_tasks`, `decision_index` y `phase_data`/`phase_definition`:
  13 fases, ocho criterios P013, quince tareas únicas (T001 completada como diseño y catorce pendientes),
  218 decisiones consecutivas con estado; dependencias y campos de tareas correctos.
- **780 enlaces locales/anchors en 17 documentos** tocados, con destinos referenciados comprobados;
  fences equilibrados. Presupuestos correctos: STATE 15.302 bytes, NEXT_STEPS 21.093 y base 10.578.
  No se recorre ni modifica el archivo histórico fuera de los destinos citados.
- Mermaid: checker sintáctico existente de P011 sobre `configuration-setup.md`;
  `node docs/archive/phase-011/P011-T013_mermaid_check.mjs frontend docs/flows/configuration-setup.md`.
  **Tres flowcharts y una secuencia correctos, cero fallos** tras corregir separadores de texto de la secuencia.
  Solo parseo: stub DOMPurify del checker archivado, sin afirmar renderizado/sanitización ni QA visual.
- Cuerpos D001–D215 contra HEAD intactos (salvo separación final); índice solo añade D216–D218.
  Base acumulada STATE intacta. `docs/archive/` y `docs/public/` sin cambios; ninguna ruta fuera de `docs/**`.
- `git diff --check` correcto y diff revisado antes del commit.

## Omisiones deliberadas

No se ejecutan pytest completo, Alembic, tipos/build, instalaciones, verificador de distribución, servicios,
proveedores, agentes del producto, smokes, harness sobre este repositorio, navegador, red o CI remota.
No cambian código, modelos, migraciones, formatos admitidos, API/OpenAPI, UI, dependencias, versión,
configuración global del equipo, snapshots, bases/fixtures privados ni candidatos/paquetes D214/P011/P012.
Esos recorridos se implementan/verifican en sus tareas y con el alcance operativo autorizado que corresponda.
El commit solicitado es local; no hay push, tag ni publicación. Siguiente: **P013-T002**.
