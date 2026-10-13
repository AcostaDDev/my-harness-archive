# Siguiente tarea — H4.1: chat contextual por turnos nuevos de la CLI Codex

H3.4 completado offline el 2026-10-13 (D034). Incluye la guardia H0/H1, el lote
desatendido con commits, la enmienda y el abandono de fases, los tags anotados y
la reconciliación con agente. Ver el
[informe](discovery/H3.4_PHASE_ADJUSTMENTS.md).

Estado verificado:

- migración `0011_phase_amendments`;
- 408 pruebas pytest (18 de H3.4) y 121 subtests;
- 12 checks ligeros y 4 pruebas Node;
- OpenAPI, tipos, TypeScript y build;
- recorrido en Chrome sobre la demo sintética.

No se usaron proveedores ni se migró la SQLite de trabajo.

El orden de D033 sigue siendo: H4.1 → exportación mecánica de STATE/NEXT_STEPS →
H4.2. **H4.1 no está iniciado.** Los consentimientos de smokes anteriores siguen
agotados.

## Objetivo y alcance (D033 punto 2, backlog H4.1)

1. Conversación separada del flujo de ejecución. Cada turno es una invocación nueva
   de la CLI de Codex en solo lectura, con contexto explícito: proyecto, fase,
   documentos y evidencias seleccionadas. La salida es estructurada y tiene un
   esquema fijo. No se reanudan sesiones del proveedor. App Server/SDK quedan para
   un incremento posterior.
2. Persistencia en SQLite de conversaciones, turnos y peticiones congeladas antes
   del efecto (prompt, contexto, versiones y hashes). Una caída deja el turno con
   resultado desconocido y no se reintenta solo.
3. Herramientas solo de lectura y propuestas estructuradas. Una propuesta del tipo
   «Ajusta X» se convierte, con confirmación explícita, en una tarea vinculada que
   ejecuta el motor normal (contrato, revisión, commit). El chat nunca modifica la
   aplicación por una ruta lateral ni concede permisos.
4. API y UI bajo la guardia local, con versiones, confirmaciones e idempotencia.
5. Caracterización offline con fakes y SQLite/Git temporales, más los checks
   pertinentes. Antes de terminar: revisión del diff y actualización de
   STATE/NEXT_STEPS, DECISIONS e informe.

## Criterios de aceptación

- Un turno usa una invocación nueva de solo lectura, con contexto y petición
  congelados antes de invocar. Una salida inválida se detiene sin fallback.
- Una propuesta confirmada genera una tarea vinculada que ejecuta y revisa el
  motor. Sin confirmación no se encola nada.
- El chat no escribe en el checkout ni amplía permisos o contratos.
- Pasan las pruebas offline y los checks de API, tipos, TypeScript y build
  pertinentes.

## Fuera de alcance

- Proveedores reales o smokes: requieren autorización específica. Según D033
  punto 8, habrá un único recorrido completo futuro.
- App Server/SDK.
- Exportación mecánica de STATE/NEXT_STEPS y bootstrap H4.2.
- Sesión local, SSE gestionado y guardia de lecturas H0/H1.
- Push y publicación: los hace el usuario.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
