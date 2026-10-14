# Siguiente paso — verificar la condición de persistencia de confianza del pin Codex

Estado al 2026-10-14:

- **D067 preparación completada con incompatibilidad.**
  [Dictamen y borrador acotado](discovery/CODEX_STARTUP_PREPARATION.md),
  [controlador solo sintético](discovery/CODEX_STARTUP_PREPARATION.py) y
  [comandos proyectados/hashes/evidencia](discovery/CODEX_STARTUP_PREPARATION.json).
- **Candidata no apta para CLI real:** la denegación por defecto que restringe
  lecturas globales y no concede red/Mach no permite un arranque útil del fake
  Python mínimo; SIGABRT antes del marcador, sin diagnóstico de causa interna.
  No se amplían permisos para pasar ni se solicita ejecutarla.
- Dos variantes de argv están proyectadas, con pin/hash, memoria cli-8,
  HOME/CODEX_HOME/auth ficticios, sin/con override de confianza y límites de
  procesos/tiempo/capturas. Ninguna ejecutada; el controlador no acepta CLI real.
- 12 casos finales (diez de controlador independiente y dos OS), once grupos
  observados ausentes. Originales ficticios protegidos conservados; dos configs
  sacrificiales cambiadas intencionadamente. Auth antes del marcador es
  inconclusa, no prueba de ausencia de persistencia. 14 pytest focales correctos.
- D066 conserva controles de memoria automática en todos los roles, 215 pytest
  pertinentes correctos y 941 recolectados. Ausencia de persistencia externa,
  fuente auth, refresh y contexto exclusivamente documental sin certificar.
- D064/D065 y D067 no califican un backend de contención para producto. cli-8/
  local-config-2, núcleo, permisos/modelos, jobs/locks e historiales intactos.
- Flujos reales: Codex→Claude D057 y Codex→Codex D061 COMMITTED; cambio global
  en la segunda provoca parada. Claude→Claude con D058 pendiente de prueba
  real; Claude→Codex nunca lanzada. La fase de comprobaciones sigue abierta.

## Tarea concreta propuesta, no iniciada

**Verificar en fuente identificable de Codex 0.162.1 qué condición activa la
persistencia de confianza y si un override de transporte evita escribir.**

1. Localizar fuente verificable correspondiente al nativo/pin o evidencia
   estática suficiente para enlazar campos/condiciones; registrar versión/hash
   y procedencia. Documentación actual, símbolos o tests falsos no bastan para
   atribuir semántica exacta a ese binario.
2. Delimitar la ruta ya localizada: permiso de escritura del cwd, estado de
   confianza, overrides, destino config y efectos de thread/start. Separar lo
   acreditado de inferencias y ramas no reconstruidas.
3. Emitir dictamen: supresión específica acreditada, o límite preciso si no
   puede demostrarse con esa evidencia. No cambiar el transporte por un supuesto
   ni volver a preparar una ejecución con el perfil no apto de D067.
4. Solo si hay evidencia suficiente, concretar como tarea posterior una
   corrección acotada y regresión por versiones/congelados. Mantener separado
   no generar/inyectar memorias de no escribir configuración global.

Criterios: trazabilidad de fuente/pin y condición exacta o límite registrado,
ninguna CLI real/version/help/inferencia, auth/secretos/configuración global,
cambio de baseline/modelos/permisos/historiales o integración de otro sandbox.
La consulta de fuente pública, si se necesita, debe ser solo lectura; no
instalar/actualizar CLI ni ejecutar código externo. Actualizar STATE/NEXT_STEPS/
DECISIONS antes de dar la tarea por terminada.

Una prueba real posterior requiere propuesta suficiente y autorización nueva.
D067 no está pendiente de consentimiento para ejecución: está descartada como
candidata actual. D050/D055/D057/D060 siguen agotados. No otra matriz, recuperación
o liberación de locks, publicación/push, archivado documental o H6.2 aquí.
