# P013 — Matriz de aceptación

Actualizada en T014 (2026-10-27). Fuente: ocho criterios de [ROADMAP](../ROADMAP.md#p013--instalación-guiada-y-configuración-desde-la-ui).
[Revisión de salida favorable](P013_REVIEW.md) en el alcance declarado y [expediente preparado](P013_EXPEDIENTE_APERTURA.md).
Candidato cualificado; cierre/archivo T015 pendiente, publicación todavía aplazada.

| Criterio | Evidencia | Dictamen y límites |
|---|---|---|
| 1. Contrato previo de configuración/autoridad/compatibilidad | [T001](P013-T001_CONTRATO.md), D216–D218; [T004](P013-T004_CONFIGURACION.md) | Cumplido: contrato anterior a implementación; no confundir su diseño con código de aquella entrega. |
| 2. Instalación/arranque, venv, rutas/cachés, red/offline, aislamiento de paquete | [T002](P013-T002_INSTALACION.md), [T003](P013-T003_ARRANQUE.md), [T012](P013-T012_PRIMER_USO.md#instalación-y-repetición) | Cumplido en macOS ARM64: copia de clon, caché inicialmente vacía, descargas de dependencias autorizadas; instalación final offline, paquete/actualización/replay sin Node y caché incompleta rechazada. Fallos originales conservados. |
| 3. Setup autenticado sin TOML/modelos, editor/diff/confirmación | [T005](P013-T005_ASISTENTE_API.md), [T006](P013-T006_ASISTENTE_UI.md), [QA T012](P013-T012_PRIMER_USO.md#qa-visual) | Cumplido: formulario real Chrome, sondas falsas explícitas, guardar/activar/reiniciar independientes, modos protegidos. No login ni inferencia de proveedores reales. |
| 4. Dos altas contextuales sin stack obligatorio | [T007](P013-T007_PROPUESTA_PERFIL.md), [T009](P013-T009_ALTA_UI.md), [recorrido instalado](P013-T012_PRIMER_USO.md#altas-y-tareas) | Cumplido con Go sintético; documentos/inventario antes de propuesta, adopción y commit documental/P001. V9 sin composición. Operaciones de proyecto por HTTP protegido; formularios de alta revisados aparte en navegador. |
| 5. Preparación acotada, recibo, activación antes de tareas | [T008](P013-T008_PREPARACION.md), [T009](P013-T009_ALTA_UI.md), [resultados T012](P013-T012_RESULTS.json) | Cumplido sintético: intento prematuro 409, Go/ejecutor falsos, JUnit/recibo y activación separados; tarea COMMITTED en ambas altas. No certifica compilador Go ni instalación de dependencias de un stack real. |
| 6. Edición manual/asistida, impacto, recuperación y contratos congelados | [T010](P013-T010_EDICION_ASISTIDA.md), [T011](P013-T011_COMPATIBILIDAD.md), [T012](P013-T012_PRIMER_USO.md) | Cumplido por suites sintéticas; formulario/TOML y contexto documental de edición comprobados instalados. Asistencia y matriz de conflictos/caídas no se repiten íntegramente en el navegador. |
| 7. Compatibilidad/backup/consulta, fallos, ambos accesos, en/es/QA | [T011](P013-T011_COMPATIBILIDAD.md), [T012](P013-T012_PRIMER_USO.md#backup-y-consulta), [capturas](P013-T012_QA/es-light-desktop-restored-run.jpg) | Cumplido en el alcance: backup formato 2, restore sin configuración/herramientas/checkouts originales; revisiones TOML/runs legibles, mutación 409 y cero jobs pendientes. Chrome, temas y anchos muestreados; no auditoría completa de accesibilidad. |
| 8. Guías públicas, candidato/paquete nuevos, revisión/expediente y cierre | README en/es y docs/public actualizados; [candidato T013](P013-T013_CANDIDATO.md), [revisión T014](P013_REVIEW.md), [expediente](P013_EXPEDIENTE_APERTURA.md) y [contraste](P013-T014_COMPROBACION.json) | Cumplido para dictaminar y pasar a T015: documentación/candidato/paquete exactos verificados; 2048 pytest/29 subtests, 8 unittest y 155 Node, tipos/build/Alembic/distribución correctos. Originales intactos. Cierre/archivo pendiente y obligatorio antes de publicar; fase todavía abierta. |

## Criterios propios de T012

| Criterio de NEXT_STEPS | Resultado |
|---|---|
| Primer uso limpio hasta global UI y altas/perfiles/tarea con stack distinto | Cumplido, con la distinción explícita navegador/HTTP y ensayo sintético de Go. |
| Caché/repetición/fallos, espacios, reinicio/edición/consulta y QA en/es | Cumplido con límites registrados en la entrega y once capturas. |
| README usuario/desarrollo, uv/venv/scripts/red/offline, opcionales/edición y baseline autocontenida | Cumplido; checker público comprueba enlaces, presupuestos, decisiones y ausencia de referencias privadas. |
| Autorización operativa acotada y separación respecto de proveedores/P012 | Cumplido: encargo/autorización del usuario aplicado al ensayo aislado; ninguna llamada a proveedores o cambio global. |
