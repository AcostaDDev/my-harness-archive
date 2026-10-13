# Siguiente paso — calificación offline de la contención candidata

Estado al 2026-10-13:

- **Propuesta de contención del proceso Codex completada (D063).**
  [Opciones, alcance y criterios](discovery/CODEX_PROCESS_CONTAINMENT_PROPOSAL.md),
  [evidencia](discovery/CODEX_PROCESS_CONTAINMENT_EVIDENCE.json) y
  [sonda independiente](discovery/CODEX_PROCESS_CONTAINMENT_PROBE.py).
- Candidata: frontera externa de escritura macOS conservando HOME/USER y auth
  en origen. Ensayo con credenciales ficticias: lectura correcta, ocho
  denegaciones de escritura, hijo contenido y originales intactos. Primera
  aplicación dentro del sandbox de desarrollo falló; ensayo fuera autorizado.
- **No implementada en producto ni auth real certificada.** CODEX_HOME privado
  no tiene separación de auth acreditada. Refresh remoto puede tener efectos
  aunque se deniegue save local; sandbox anidado, IPC y auxiliares pendientes.
  cli-7, local-config-2, permisos D024/D059 e historiales conservados.
- D062 acreditó la adición exacta de confianza de 93 bytes por hash inverso;
  atribución al proceso original sigue inferida. Configuración global conservada.
- D060 cerrada con parada preventiva (D061): 2 Codex→Codex COMMITTED
  (`585a35c`), 3/4 no lanzadas. Consentimiento agotado. La 1 D057 ya completa;
  Claude real con esquema tipado D058 sigue pendiente.

## Tarea concreta propuesta, no iniciada

**Calificar offline el contenedor macOS candidato con procesos y credenciales
exclusivamente sintéticos, antes de integrar el transporte de producto.**

1. Partir de la sonda D063 y su matriz pendiente. Delimitar y ensayar perfil
   lector/escritor, raíces canónicas y rechazo de solapamientos con HOME,
   estado/artefactos; rutas especiales, symlinks/hardlinks y escapes.
2. Ensayar estado auxiliar (config temporal/rename, caché, SQLite y locks),
   auth ausente/ilegible y refresh ficticio con escritura denegada. Originales
   inmutables, diagnóstico explícito, un lanzamiento y ningún fallback.
3. Comprobar descendientes, descriptores heredados y sandbox interno sintético
   equivalente a las restricciones D059. Investigar IPC/delegación solo contra
   servicios sintéticos propios: no tocar llavero, launch services ni auth real.
   Registrar exactamente qué vías quedan fuera de la frontera.
4. Verificar launcher/perfil ausente o inválido antes del proceso objetivo,
   timeout/cancelación y protocolo de identidad/gate mediante fakes. Sin
   invocar ni siquiera version/help de CLI reales o arrancar el harness.
5. Emitir dictamen de viabilidad y alcance de integración posterior, o límite
   preciso si no es viable. Actualizar STATE/NEXT_STEPS/DECISIONS. No conectar
   el prototipo al adaptador, TOML operativo ni jobs reales en esta tarea.

Criterios: resultados reproducibles con HOME/auth ficticios y conservación de
originales; denegaciones y escrituras permitidas diferenciadas; ningún bypass
si el SO no soporta el perfil; limitaciones de IPC/auth/red explícitas. No
presentar fakes como certificación de login, refresh remoto o CLI real. Sin
cambios de baseline/modelos/permisos, credenciales reales copiadas/enlazadas,
configuración global o historiales. El núcleo permanece independiente del SO.

La integración en producto será otra tarea tras el dictamen. Una comprobación
real requiere propuesta y consentimiento específicos nuevos, incluyendo la
resolución del límite de refresh descrito en D063; no está autorizada aquí.
No iniciar otro smoke/matriz, preflight real, jobs, recuperación, liberación
de locks, publicación, push o H6.2. D050/D055/D057/D060 siguen agotados.

Después, y aparte: hito de interfaz de producto (D054, H6.2). Alternativas
pendientes: `forbidden_paths` frente a prosa; instalación de operación
reutilizable (D051); `memory/` vacío de Claude; endurecimientos de D048.
Ninguna iniciada en D063.
