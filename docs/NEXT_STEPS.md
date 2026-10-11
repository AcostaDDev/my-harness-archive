# Siguiente tarea — H2.2 (pendiente)

H0, H1 y H2.1 completados el 2026-10-11. [Alcance original de H2.1](discovery/H2.1_SCOPE.md)
y [entrega/verificaciones](discovery/H2.1_ENGINE.md) conservados para revisión.
Esta entrega no inicia H2.2.

## Objetivo

Añadir persistencia gestionada, cola local y exclusión por checkout al motor
extraído, con estados/eventos atómicos, jobs idempotentes y snapshots congelados
por intento. Mantener la autoridad de observación separada.

## Alcance de la siguiente sesión

1. Revisar H2.2 del backlog, estados/persistencia/seguridad de la especificación
   y D003/D010/D012–D015. Delimitar entidades gestionadas y su autoridad antes
   de añadir migraciones; no convertir simulaciones o evidencia legacy en intentos.
2. Persistir runs/intentos, estados, resultados y eventos mediante transacciones
   cortas. Congelar contrato, contexto, políticas, prompts y versiones por intento;
   conservar los anteriores y el presupuesto de correcciones al recuperar.
3. Implementar jobs locales idempotentes y cola, con lease/heartbeat y exclusión
   por raíz canónica del checkout. No mantener una transacción SQLite abierta
   mientras un trabajo se ejecuta. Recuperar paradas/reinicios sin llamadas ocultas.
4. Comprobar concurrencia, claves repetidas y fallos entre transiciones con
   adaptadores falsos y repositorios/bases sintéticos. Un solo escritor por checkout;
   checkouts distintos pueden progresar según la política explícita de cola.
5. Mantener H0/H1/H2.1, ejecutar checks pertinentes, revisar diff, actualizar
   STATE/NEXT_STEPS y registrar decisiones duraderas. Documentar límites de la
   recuperación/exclusión sin presentar adaptadores falsos como ejecución real.

## Criterios de aceptación

- Estados, resultados y eventos gestionados se guardan atómicamente; historial,
  snapshots y presupuesto persisten tras reiniciar.
- Doble solicitud y solicitudes concurrentes para el mismo trabajo lanzan una
  sola ejecución falsa; raíces equivalentes comparten el bloqueo escritor.
- Cola/lease/exclusión no dependen de transacciones largas; fallos y recuperación
  tienen semántica explícita y no duplican ejecuciones silenciosamente.
- Observación legacy y simulaciones conservan su autoridad/contratos; regresión,
  migraciones, checks de contratos y build pasan.

## Fuera de alcance

H2.3 adaptadores CLI reales/smoke, H2.4 worktrees/captura Git completa/commit,
H2.5 migración de proyectos a gestionado, chat, permisos interactivos, SDKs,
cierre de fase y distribución. No ejecutar harness/agentes, tests/instalaciones
en ReferenceProject ni modificar configuración global. No usar runs reales; cualquier
smoke con proveedores requiere autorización explícita de consumo posterior.
