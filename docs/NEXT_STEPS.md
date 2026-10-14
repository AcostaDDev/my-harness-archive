# Siguiente paso — elegir alcance tras el dictamen de contención

Estado al 2026-10-14:

- **Diagnóstico offline y frontera revisada D065 completados.**
  [Dictamen y criterios verificables](discovery/CODEX_CONTAINMENT_REVISION.md),
  [evidencia](discovery/CODEX_CONTAINMENT_REVISION.json) y
  [sonda reproducible](discovery/CODEX_CONTAINMENT_REVISION.py).
- **Candidata sin calificación para integrar.** Perfiles sintéticos iguales
  componen manteniendo ambas capas y prohibición de escritura global; los pares
  ensayados con restricciones distintas se rechazan en la segunda aplicación.
  Comentarios/reordenación/deny redundante no causan el rechazo. No se prueba
  el perfil exacto de Codex ni se atribuye una causa interna sin evidencia.
- Cerrar fd/pipe corta las vías heredadas ensayadas; stdout capturado como
  bytes no delega. Hardlink introducido después de admisión/readiness modifica
  un sacrificial exterior. Prechecks/lock cooperativo no certifican ausencia
  de carreras. IPC general, auxiliares/auth reales y refresh siguen pendientes.
- 32 escenarios finales completos (22 anidados, doce rechazos esperados),
  14 pytest focales correctos. Auth/config ficticios conservados. Solo tres
  sacrificiales explícitos cambian; errores sin fallback. Sin CLI real, red
  externa, integración en producto ni cambios globales.
- cli-7/local-config-2, núcleo, TOML operativo, jobs, modelos/permisos D024/D059
  y congelados conservados. D063/D064 permanecen como evidencia histórica.
- D060 cerrada con parada preventiva D061: 2 Codex→Codex COMMITTED (`585a35c`),
  3/4 no lanzadas. La 1 D057 ya completa; Claude real con esquema tipado D058
  sigue pendiente. D062 acreditó el delta de confianza de 93 bytes.

## Siguiente tarea pendiente de elección, no iniciada

**Elegir con el usuario un alcance después de la incompatibilidad D065.**

Opciones delimitadas en el dictamen:

1. Investigar una capacidad soportada de separación de estado/auth o una
   frontera externa distinta que conserve ambas capas y excluya aliases/IPC
   con autoridad exterior. Requiere alcance acotado y evidencia nueva; no se
   presume disponible para Codex 0.162.1 ni se inicia automáticamente.
2. Mantener suspendida esa integración y el consumo pendiente con Codex.
3. Revisar explícitamente el modelo de aislamiento/auth/efectos aceptados.
   Garantía cooperativa frente a terceros del mismo UID, cambio de cuenta/
   almacén o aceptación de refresh remoto serían cambios materiales pendientes
   del usuario, no decisiones tomadas por esta entrega.

La elección deberá concretar objetivo, amenaza cubierta, efectos admitidos y
criterios antes de implementar. No basta cerrar fd y escanear enlaces. Ninguna
opción autoriza copiar/enlazar credenciales, eliminar sandbox interno, ampliar
raíces, escribir ajustes globales o restaurarlos después.

Una integración será otra tarea tras una calificación suficiente. Comprobación
real requiere propuesta/consentimiento específicos nuevos con el límite de
refresh resuelto. No iniciar otro smoke/matriz, CLI real (ni version/help),
jobs, recuperación/liberación de locks, publicación, push o H6.2.
D050/D055/D057/D060 siguen agotados. No se ha avanzado a esta tarea siguiente.

Después, y aparte: interfaz de producto D054/H6.2. Alternativas pendientes:
`forbidden_paths` frente a prosa, instalación de operación reutilizable D051,
`memory/` vacío de Claude y endurecimientos D048. Ninguna iniciada en D065.
