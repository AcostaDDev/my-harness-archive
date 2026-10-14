# Siguiente paso: H6.5, creación y planificación conversacionales

Estado al 2026-10-14:

- **H6.4 implementado offline (D074).** [Catálogo, entrega y límites](discovery/H6.4_METRICS.md),
  [caracterización de D071](discovery/H6.4_STREAM_CATALOG.json).
- Migración `0014_attempt_metrics`: una fila por intento resuelto, escrita en la transacción del resultado,
  con procedencia por campo y null distinto de cero. Captura `terminal-2` (turnos, duración de API y
  contadores derivados) sin cambiar el adaptador `cli-9`.
- Relleno explícito e idempotente: `harness-local metrics-backfill --database RUTA [--artifact-root RAÍZ]`.
- Agregados de solo lectura en `/api/managed/metrics/*` (resumen, intentos, grupos, modelos, tareas) y
  tokens/turnos en el SUMMARY de las fases que se archiven. Sin UI ni proveedores.
- H6.3 (D072/D073) commiteado por separado antes de H6.4.

## Tarea concreta propuesta, no iniciada

**H6.5 — Creación y planificación conversacionales, offline (D072 §5.1, §11; D073 puntos 4 y 7).**

1. Conversación `definition` sobre la infraestructura de chat (D035): turnos nuevos del revisor en solo
   lectura con contexto congelado (brief Markdown con hash, máximo 256 KiB; borradores actuales con su
   hash; turnos anteriores). Salida estructurada: respuesta, preguntas abiertas, propuestas de borrador por
   documento (contenido completo y motivo) y pendientes para aceptar. Salida inválida detiene el turno.
2. Borradores en la carpeta destino, sin commit: aplicar una propuesta escribe con CAS sobre el hash
   anterior; una edición del usuario entre medias es conflicto y no se sobrescribe. El turno siguiente
   detecta por hash las ediciones del usuario. Solo rutas de la plantilla v2 (`skeleton`),
   `architecture/*.md` y `decisions/*.md`; cualquier otro archivo bloquea la aceptación. El agente nunca
   escribe.
3. Aceptación con vista previa determinista: archivos íntegros, `archive/phase-000/{BRIEF,DEFINITION}.md`,
   bloques, definición de P001 derivada del ROADMAP, perfil, política y comandos. Bloqueos: documentos
   obligatorios ausentes, ROADMAP sin fases, P001 sin objetivo/criterios, NEXT_STEPS sin una tarea
   P001-TNNN válida o preguntas bloqueantes abiertas. La confirmación lanza el bootstrap D037 con la
   plantilla v2 (`documents = "v2"`), commit raíz con esos bytes y P001 ACTIVE adoptada.
4. Conversación `phase_planning` con el mismo mecanismo para proponer el plan de la fase siguiente que
   hoy aporta el usuario en `phase_transition`.

Criterios: de una carpeta vacía, con conversación sintética y ediciones en disco y por API, se llega al
commit raíz con P001 y `phase-000`; las ediciones concurrentes se detectan; no se admite ningún archivo
ajeno; el agente no escribe; bootstrap v1 y proyectos existentes siguen igual. Sin proveedores ni UI.
Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

Después: UI H6.2 como tarea completamente distinta (D073), con métricas y estadísticas sobre los
endpoints de H6.4.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
