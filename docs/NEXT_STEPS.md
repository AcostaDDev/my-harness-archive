# Siguiente paso: H6.2, UI de producto (tarea aparte, D073)

Estado al 2026-10-14:

- **H6.5 implementado offline (D075).** [Entrega, API y límites](discovery/H6.5_CONVERSATIONAL_CREATION.md).
- Migración `0015_planning`: conversaciones `definition` y `phase_planning`, turnos congelados y propuestas
  (borradores por documento o plan de la fase siguiente). Roles aditivos `definition` y `planning` en `cli-9`
  y plantillas versionadas `define-project` y `plan-phase`.
- Borradores en la carpeta destino escritos solo por el harness al aplicar una propuesta confirmada, con CAS;
  ediciones del usuario en disco o por API detectadas por hash; archivos ajenos bloquean la aceptación.
- Aceptación → bootstrap D037 con plantilla v2: commit raíz, `archive/phase-000/{BRIEF,DEFINITION}.md`,
  bloques regenerados y P001 ACTIVE adoptada. La transición acepta `plan_proposal`.
- API bajo `/api/managed/projects/{id}/planning`; OpenAPI y tipos regenerados. Sin UI ni proveedores.

## Tarea concreta propuesta, no iniciada

**H6.2 — UI de producto (D054, D072 §6–§9, D073 punto 6).** Tarea completamente distinta de las anteriores,
con su plugin de diseño. Construye la interfaz una sola vez sobre los contratos ya estables (H6.3–H6.5).

Antes de implementar, fijar el alcance con el usuario y dividirlo en entregas verificables, por ejemplo:

1. Shell con enrutado por URL (§7: proyectos, fases `PNNN`, tareas `PNNN-TNNN`, runs) y carga limitada por
   recurso; el servidor del wheel sirve `index.html` en rutas que no son de API.
2. Documentación y chat: árbol y editor Markdown seguro con diff confirmado (`document_edit`), deriva y
   bloques bloqueados; chat contextual existente.
3. Creación: asistente sobre `/planning` (brief, turnos, aplicar/descartar borradores, edición con CAS,
   aplazar preguntas, vista previa de aceptación con bloqueos) y planificación de fase → transición con
   `plan_proposal`.
4. Estadísticas: métricas por tarea, tests OK/KO y agregados globales y por proyecto (`/metrics/*`).

Decisiones pendientes para el alcance: registro de proyectos desde la UI (D054, convivencia con el TOML
`local-config`, que hoy no expone `bootstrap_enabled`), enrutador propio sin dependencia nueva y carga
diferida de Mermaid. QA visual con navegador sobre `scripts/dev` y datos sintéticos.

Criterios orientativos: cada URL se abre por enlace directo y recarga; ninguna acción repite efectos al
reintentar; las confirmaciones se ligan a hash y versión; recorrido sintético completo de creación →
primera tarea → cierre → transición con plan propuesto. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
