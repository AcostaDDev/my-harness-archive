# Siguiente tarea — H4.1: chat contextual

H3.3 completado offline el 2026-10-13 (D032):
[fases, preguntas, cierre y tags](discovery/H3.3_PHASES.md).
Fases en SQLite con definición congelada y base documental por hash; check y
cierre como jobs bajo el lock del checkout; READY ligado a HEAD/fingerprint,
documentos, commits de tareas y preguntas; cierre que reobserva y solo crea un
tag ligero por CAS; autorizaciones de lote y de cierre distintas y auditadas.
Migración `0010_phases`. 390 pruebas pytest (29 H3.3), 121 subtests, 12 checks
ligeros, 3 pruebas Node, OpenAPI/tipos/TypeScript/build y recorrido Chrome
sintético verificados. Sin proveedores ni migración de la SQLite de trabajo.

**H4.1 no iniciado.** Los consentimientos de smokes anteriores siguen agotados.

## Objetivo y alcance siguiente

Completar H4.1 del backlog en una entrega acotada, sin iniciar H4.2:

1. Revisar especificación §6 (chat y permisos interactivos), §12 («Ajusta X»),
   §13 (`/chat/messages`, `/proposals/{id}/accept`), backlog H4.1 y contratos
   H2/H3. Señalar contradicciones materiales antes de cambiar el diseño.
2. Decidir el transporte: App Server/SDK solo tras comprobar compatibilidad y
   autenticación en lectura (D007–D009); si no es viable, turnos nuevos con
   contexto explícito por la CLI existente. No consumir proveedores sin
   autorización explícita del usuario para un smoke concreto.
3. Persistir conversación, mensajes y propuestas estructuradas en SQLite, separadas
   del flujo de ejecución; herramientas de solo lectura con referencias exactas.
4. Aceptar una propuesta crea o actualiza una tarea mediante decisión explícita,
   con `Idempotency-Key`, versión y auditoría; la ejecución sigue pasando por el
   motor (contrato, revisión, commit H2.4) y por las fases H3.3.
5. Exponer API/UI con guardias locales, tipos generados y confirmaciones.
6. Caracterizar offline con fakes: propuesta duplicada, aceptación concurrente,
   reinicio, rechazo y ausencia de rutas laterales que modifiquen la aplicación.
7. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS,
   DECISIONS e informe antes de completar la tarea.

## Criterios de aceptación

- «Ajusta X» genera una propuesta vinculada; aceptarla crea una tarea que ejecuta
  el motor y su resultado queda enlazado al mensaje de origen.
- El chat no modifica archivos, documentos, permisos ni fases por una ruta lateral.
- Una propuesta se acepta una sola vez; reinicios y reenvíos no duplican tareas.
- Conversación y propuestas sobreviven al reinicio sin reescribir históricos.
- Pruebas offline, API/tipos/TypeScript/build pertinentes pasan.

## Fuera de alcance

Proveedores reales o smokes sin autorización explícita, login/refresh, secretos,
recuperación de D020/D022, permisos vivos, bootstrap H4.2, segundo perfil H4.3,
integración de rama, push/publicación y distribución. No lanzar colaboración
automática ni usar el harness para desarrollar el repo. Pendientes sin ampliación
implícita: sesión local, guardia H0/H1, SSE gestionado, políticas editables,
registro de proyectos por HTTP, exportación mecánica de STATE/NEXT_STEPS,
reconciliación documental con agente, edición de definiciones de fase y
encadenado automático del lote.
