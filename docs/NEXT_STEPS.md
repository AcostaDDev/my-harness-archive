# Siguiente tarea — H3.3: fases

H3.2 completado offline el 2026-10-13 (D031):
[permisos y recuperación](discovery/H3.2_PERMISSIONS.md).
Ledger por categoría, huella/caducidad/versiones, conceder/denegar/sustituir,
identidad local del servicio y auditoría; snapshots y consumo por intento,
CLI `cli-4`, API/UI y acciones habilitadas en el servidor. Revalidar ante REVISE
se detiene para exigir reintento explícito, sin repetir el ejecutor.
Migración `0009_permissions`, codec 5 compatible con formatos 1–4.
361 pruebas pytest (30 H3.2), 121 subtests, 12 checks ligeros, 3 pruebas Node,
OpenAPI/tipos/TypeScript/build y recorrido Chrome sintético verificados.
No se han usado proveedores ni migrado la SQLite de trabajo del usuario.

**H3.3 no iniciado.** Los consentimientos de smokes anteriores siguen agotados.

## Objetivo y alcance siguiente

Completar H3.3 del backlog en una entrega acotada, sin iniciar H4:

1. Revisar especificación de fases (§8), backlog H3.3 y contratos H2/H3.1/H3.2.
   Definir autoridad y evidencia de fase sobre SQLite; señalar contradicciones
   materiales antes de cambiar diseño. COMMITTED sigue siendo checkpoint, sin
   integración automática en la rama de destino.
2. Implementar checks y reconciliación documental, con preguntas bloqueantes,
   evidencias/versiones y estados ACTIVE/CHECKING/READY_TO_CLOSE/CLOSED,
   NEEDS_RECONCILIATION/BLOCKED según alcance aceptado.
3. Vincular READY y autorización de cierre al contenido exacto y tareas aceptadas;
   invalidar evidencia obsoleta. Separar autorización de ejecución por lote y
   cierre de fase; las concesiones operativas no deciden producto ni cierre.
4. Exponer las acciones pertinentes por API/UI con versiones, confirmaciones,
   auditoría y guardias locales. Documentar semántica de cierre/tags y recuperación
   conservadora antes de efectos Git; no inventar cierre a partir del legacy.
5. Caracterizar offline preguntas pendientes, deriva documental, READY obsoleto,
   reinicio, concurrencia e historial mediante fakes y Git/SQLite temporales.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS,
   DECISIONS e informe antes de completar la tarea.

## Criterios de aceptación

- Una revisión READY obsoleta no permite cerrar la fase.
- Preguntas bloqueantes pendientes impiden avanzar/cerrar.
- Lote y cierre exigen autorizaciones distintas, explícitas y auditadas.
- Checks/reconciliación y evidencias sobreviven al reinicio sin borrar históricos
  ni repetir efectos inciertos automáticamente.
- Exclusión de checkout, contratos/snapshots y aceptación por contenido exacto
  se conservan. Pruebas offline, API/tipos/TypeScript/build pertinentes pasan.

## Fuera de alcance

Proveedores reales, smokes, login/refresh, secretos, recuperación de D020/D022,
SDK/permisos vivos, integración de rama, push/publicación, chat/bootstrap H4 y
distribución. No lanzar colaboración automática ni usar el harness para desarrollar
el repo. Sesión local, guardia H0/H1, SSE gestionado, políticas editables y registro
de proyectos por HTTP permanecen pendientes, sin ampliación implícita.
