# Siguiente acción — H2.3: corregir configuración Codex offline

H0, H1, H2.1 y H2.2 completados. H2.3 implementado y caracterizado offline;
smoke autorizado ejecutado el 2026-10-11 y detenido al primer error.
[Resultado y evidencias](discovery/H2.3_SMOKE.md): Codex 0.162.1 rechaza los
overrides `model_providers.openai` porque `openai` es un proveedor integrado
reservado. No se lanzaron Claude ni el revisor, ni se relanzó el planificador.
H2.4 no iniciado.

## Objetivo pendiente

Corregir y caracterizar offline la configuración del adaptador Codex antes
de proponer otra verificación real. El preflight de versión/help y los fakes
no detectaron el rechazo semántico de la configuración; no acreditan acceso
a modelos, cuota, autenticación ni comportamiento frente a proveedores.

## Acción acotada

1. Revisar el stderr conservado, el argv congelado y la configuración admitida
   por Codex 0.162.1. Resolver cómo solicitar cero retries HTTP/stream sin
   sobrescribir IDs reservados ni cambiar silenciosamente de proveedor.
2. Añadir una regresión offline que cubra el rechazo observado; ajustar los
   procesos sintéticos para no aceptar indiscriminadamente ese argv inválido.
   Mantener versión, sesión nueva, selección explícita y ausencia de fallback.
3. Ejecutar checks offline pertinentes, revisar diff y actualizar
   STATE/NEXT_STEPS/DECISIONS. No lanzar proveedores durante esta corrección.
4. Preparar una nueva propuesta concreta de smoke solo después de los checks.
   La autorización D018 se aplicó a una ejecución detenida al primer error;
   no habilita relanzamientos automáticos tras corregir el adaptador.

## Criterios de aceptación

- Configuración Codex compatible y caracterizada sin overrides reservados,
  con límites de retries explícitos y sin inferir garantías no comprobadas.
- Regresión que detecte el fallo real observado y conserve las garantías H2.3
  de captura, cancelación, persistencia y parada sin fallback.
- Evidencias del smoke fallido conservadas; resultado real separado de fakes.
- Sin nuevas invocaciones reales ni avance a H2.4 en esta corrección.

## Fuera de alcance

H2.4 worktrees/captura Git completa/commit de producto, H2.5 migración de
proyectos, entradas gestionadas API/CLI/UI, permisos vivos, chat, SDKs, cierre
de fase y distribución. No ejecutar el harness para desarrollar, lanzar otros
agentes automáticamente, usar runs de usuario, extraer credenciales, modificar
configuración global ni ejecutar tests/instalaciones en ReferenceProject.
