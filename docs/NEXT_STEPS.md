# Siguiente tarea — Exportación mecánica de STATE/NEXT_STEPS

H4.1 completado offline el 2026-10-13 (D035). Cada mensaje del chat es un turno
nuevo de solo lectura con el contexto congelado al encolarlo, salida de esquema
fijo y sin reintentos. Las propuestas solo se convierten en una tarea normal tras
una confirmación explícita. Ver el [informe](discovery/H4.1_CHAT.md).

Estado verificado:

- migración `0012_chat`;
- 430 pruebas pytest (21 de H4.1) y 121 subtests;
- 12 checks ligeros y 4 pruebas Node;
- OpenAPI, tipos, TypeScript, build y `alembic check`;
- recorrido en Chrome sobre la demo sintética.

No se usaron proveedores ni se migró la SQLite de trabajo.

El orden de D033 sigue siendo: H4.1 → exportación mecánica de STATE/NEXT_STEPS →
H4.2. **La exportación no está iniciada.** Los consentimientos de smokes
anteriores siguen agotados.

## Objetivo y alcance (D033 punto 1, especificación §7)

1. El motor exporta, a partir de la autoridad SQLite, la parte mecánica de
   `STATE.md` y `NEXT_STEPS.md` del proyecto gestionado: fase vigente, estado,
   tareas con aceptación y commit, preguntas abiertas, últimos checks y lotes. La
   prosa escrita por personas no se toca: el bloque mecánico va delimitado por
   marcadores.
2. Exportar es determinista: el mismo estado produce los mismos bytes. Se previsualiza
   como diff antes de aplicarse.
3. Antes de escribir se comparan los hashes de los documentos con la base adoptada
   (H3.3). Un cambio externo se presenta como propuesta de importación o de
   reconciliación, nunca se mezcla en silencio.
4. Escribir los documentos es un cambio del checkout: se hace como tarea o commit
   revisado por contenido exacto (H2.4), con intención previa y conciliación tras
   una caída. Después, la base documental de la fase se adopta por hash. Hay que
   decidir y registrar en DECISIONS si el cierre de fase (D032) invoca la
   exportación o sigue siendo una acción separada.
5. API y UI bajo la guardia local, con versiones, confirmaciones e idempotencia.
   Caracterización offline con Git y SQLite temporales.

## Criterios de aceptación

- La exportación es determinista y solo modifica el bloque mecánico delimitado.
- Un documento cambiado externamente nunca se sobrescribe: se detiene o propone
  una reconciliación.
- El efecto en Git es revisable y conciliable, sin duplicar commits.
- Pasan las pruebas offline y los checks de API, tipos, TypeScript y build
  pertinentes.

## Fuera de alcance

- Bootstrap H4.2.
- Proveedores reales o smokes: requieren autorización específica (D033 punto 8).
- App Server/SDK para el chat.
- Sesión local y SSE gestionado.
- Push y publicación: los hace el usuario.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
