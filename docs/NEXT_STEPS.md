# Siguiente tarea — H3.4: ajustes de fases, lote desatendido y guardia H0/H1

H3.3 completado offline el 2026-10-13 (D032):
[fases, preguntas, cierre y tags](discovery/H3.3_PHASES.md).
Migración `0010_phases`. 390 pruebas pytest (29 H3.3), 121 subtests, 12 checks
ligeros, 3 pruebas Node, OpenAPI/tipos/TypeScript/build y recorrido Chrome
sintético verificados. Sin proveedores ni migración de la SQLite de trabajo.

El usuario fijó el orden y el alcance en **D033**: H3.4 → H4.1 (chat por CLI,
turnos nuevos) → exportación mecánica de STATE/NEXT_STEPS → H4.2.

**H3.4 no iniciado.** Los consentimientos de smokes anteriores siguen agotados.

## Objetivo y alcance

Una entrega acotada con los puntos 3–7 de D033, sin iniciar H4.1:

1. **Guardia H0/H1:** aplicar Host de loopback, Origin y `X-Harness-Local` a las
   mutaciones de simulaciones y observación legacy; actualizar cliente y pruebas.
   La sesión local queda para el hito 5.
2. **Lote desatendido con commit:** la autorización de lote congela tareas, texto
   del plan y el alcance explícito «encadenar y confirmar commits». El supervisor
   encola el commit de cada aceptación elegible y la siguiente tarea tras
   COMMITTED; se detiene en el primer bloqueo, pregunta, caducidad, revocación o
   evidencia invalidada. Nunca comprueba ni cierra la fase. Caídas: recuperación
   H2 explícita, sin repetir efectos inciertos.
3. **Enmienda y abandono de fase:** nueva versión de definición con motivo y
   confirmación, conservando la anterior e invalidando READY y lotes; abandono
   explícito con estado terminal y auditoría.
4. **Tags configurables:** tipo por proyecto, ligero por defecto. Anotado con
   mensaje, identidad y fecha fijados en la intención, id determinista y
   conciliación sin mover ni sobrescribir.
5. **Reconciliación con agente:** acción que genera una tarea con contrato
   determinista limitado a los documentos de la fase (plantilla `reconcile-phase`),
   ejecutada, revisada y confirmada por el flujo normal; la base se adopta después
   por hash.
6. Exponer API/UI con versiones, confirmaciones y acciones del servidor.
7. Caracterizar offline con fakes y Git/SQLite temporales; checks pertinentes,
   revisión del diff y actualización de STATE/NEXT_STEPS, DECISIONS e informe.

## Criterios de aceptación

- Las mutaciones H0/H1 rechazan Host/Origin ajenos y peticiones sin cabecera.
- Un lote autorizado recorre tarea → aceptación → commit → siguiente tarea sin
  intervención y se detiene en el primer bloqueo; nunca comprueba ni cierra.
- Enmendar una definición invalida READY y lotes y conserva la versión anterior.
- Tags ligeros y anotados se crean una vez, se concilian tras caída y no se mueven.
- La reconciliación con agente no escribe fuera de los documentos de la fase y
  pasa por revisión y commit de contenido exacto.
- Pruebas offline, API/tipos/TypeScript/build pertinentes pasan.

## Fuera de alcance

Proveedores reales o smokes (D033 punto 8: solo un recorrido completo futuro y
autorizado), chat H4.1, exportación mecánica de STATE/NEXT_STEPS, bootstrap H4.2,
segundo perfil H4.3, sesión local, SSE gestionado, políticas editables, registro de
proyectos por HTTP, integración de rama, push/publicación (lo hace el usuario) y
distribución. No lanzar colaboración automática ni usar el harness para
desarrollar el repo.
