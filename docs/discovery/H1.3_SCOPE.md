# Siguiente tarea — H1.3 (pendiente)

H1.2 completado el 2026-10-11. [Alcance y criterios originales](discovery/H1.2_SCOPE.md)
conservados para revisión; [entrega y verificaciones](discovery/H1.2_NAVIGATION.md).
Esta entrega no inicia H1.3.

## Objetivo

Añadir actualización incremental de observación: watcher con relectura controlada,
reconciliación al iniciar y eventos SSE persistidos con reconexión por cursor.
Cerrar y abrir el navegador debe recuperar actividad sin pérdidas ni duplicados,
sin presentar un archivo parcial como fallo del agente.

## Alcance de la siguiente sesión

1. Revisar H1.3 del backlog, observación/persistencia de la especificación y
   D012/D013. Usar fixtures/copias sintéticas; conservar autoridad del origen,
   importación explícita H1.1 y navegación H1.2, sin iniciar motor ni agentes.
2. Implementar observación local controlada por proyecto, agrupación de cambios y
   relectura de evidencias. Reconciliar al iniciar y preservar identidad/idempotencia,
   ausencias y archivos parciales pendientes de relectura. Cambios no convierten
   review/validación en intentos ni ACCEPT/READY en aceptación/commit/cierre.
3. Persistir eventos de actualización del índice y servir SSE con cursor estable.
   Resolver consistencia entre transacción del índice/evento, reconexión, orden,
   duplicación y recuperación tras reinicio; no implementar event sourcing del motor.
4. Actualizar listas/detalles de la UI por eventos, manteniendo selección coherente,
   procedencia y hashes. Un tramo previamente abierto no se mezcla con contenido
   de un hash nuevo; separar error local de lectura y evidencia de fallo del agente.
5. Generar contratos/tipos y comprobar offline los cinco escenarios, escrituras
   parciales que se completan, cambios/desapariciones, reconexión y reinicio.
   Mantener H0.3/H1.1/H1.2, actualizar STATE/NEXT_STEPS y registrar decisiones.

## Criterios de aceptación

- Cambios sintéticos se reflejan tras relectura controlada, sin duplicar runs ni
  perder historial/evidencia disponible; archivos parciales permanecen pendientes.
- Reiniciar el servicio reconcilia el origen; cerrar/abrir el navegador o reconectar
  por cursor recupera actividad sin pérdidas ni duplicados.
- UI conserva identidades/procedencia, muestra cambios/ausencias y evita mezclar
  bytes de versiones diferentes. Diagnósticos de lectura no declaran fallo de agente.
- Contratos/tipos, checks offline y build pasan; H0.3/H1.1/H1.2 siguen funcionando.

## Fuera de alcance

H2 motor/supervisor/cola/bloqueo escritor, modo gestionado, adaptadores reales,
chat, permisos interactivos, SDKs y distribución. No ejecutar harness/agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global. No usar runs
reales; cualquier smoke con proveedores exige autorización explícita de consumo
en una tarea posterior.
