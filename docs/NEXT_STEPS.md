# Siguiente paso — Elegir el incremento posterior al hito 5

H5.7 recorridos E2E offline completado el 2026-10-13 (D045).
Ver [entrega, matriz y reproducción](discovery/H5.7_E2E.md) y
[alcance original](discovery/H5.7_SCOPE.md).

- Crear, importar, ejecutar, bloquear, denegar, reintentar y recuperar comprobados
  con sesión real, API, Git/SQLite temporales y puertos falsos.
- Reinicio, idempotencia, evidencia exacta, confirmaciones y commit verificados;
  ninguna denegación, pérdida de sesión o recuperación reenvía acciones por sí sola.
- Wheel instalado aislado: bootstrap → primera tarea → commit → reinicio →
  backup/restauración de consulta, sin depender del checkout de desarrollo.
- 771 pruebas pytest y 121 subtests, 12 checks ligeros, 6 pruebas Node,
  TypeScript/build y verificador del paquete correctos.
- Chrome bloqueó el acceso con `ERR_BLOCKED_BY_CLIENT`: QA visual de H5.7
  pendiente de un navegador que permita acceder. HTTP no equivale a QA visual.

Esquema `0013_bootstrap`, codec 6, adaptador `cli-4` y locks conservados.
Revisión de cierre offline completada: [dictamen y brechas](discovery/H5_CLOSURE_REVIEW.md).
No hay siguiente incremento de implementación acordado ni iniciado.

## Propuesta concreta, pendiente de elección del usuario

Preparar el alcance de un ejecutor de comandos de validación de producto,
con pruebas offline. Hoy existe `CommandRunner` como protocolo y un runner real
solo en tests; la demo del servicio usa validadores falsos. Antes de un piloto
real hay que resolver ejecución, captura acotada, propiedad/recuperación de
procesos y configuración congelada, preservando el lock y la evidencia exacta.
Los criterios propuestos están en la revisión de cierre; no están implementados.

Se consultó al usuario la prioridad entre este incremento (recomendado), retomar
QA visual o preparar una propuesta de smoke sin ejecutarlo. **Elección pendiente**;
no interpretar la ausencia de respuesta como selección ni iniciar una de ellas
por defecto. La QA visual exige un navegador que permita acceder a loopback.

Los recorridos con proveedores siguen sin verificar. Un eventual smoke completo
(tarea → commit → check → cierre, D033.8) requiere propuesta y autorización
específica, checkout desechable y modelos/esfuerzos fijados por el usuario.
Los consentimientos previos están agotados. Sin push, publicación, colaboración
automática ni uso del harness para desarrollar este repositorio.
