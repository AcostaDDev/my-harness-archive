# Instrucción inicial para desarrollar Harness Local

Este texto puede copiarse como primer mensaje en Codex o Claude Code, dentro del repositorio nuevo del producto y junto a los otros dos documentos. Es deliberadamente neutral respecto al agente que lo ejecute.

---

Quiero desarrollar una aplicación local para configurar, ejecutar y observar un harness modular de desarrollo asistido por agentes.

Lee primero:

- `docs/01-especificacion-harness-local.md`.
- `docs/02-backlog-y-plan-de-desarrollo.md`.
- Las instrucciones aplicables del repositorio nuevo.

La referencia existente está en `$HOME/Documents/projects/reference_project/.harness`. Úsala solo como referencia de lectura: no modifiques ReferenceProject ni ejecutes su harness, agentes, instalaciones o validaciones. No copies sus históricos ni secretos al repositorio nuevo.

Este producto se desarrollará manualmente con ayuda de Codex y Claude Code. No uses el harness para coordinar su propio desarrollo. No lances otros agentes ni sesiones de proveedores automáticamente. Las integraciones reales se probarán después en un repositorio desechable, con autorización de consumo.

Objetivo de esta primera sesión: completar solo H0.1 según `docs/NEXT_STEPS.md`. Los puntos de arquitectura y compatibilidad siguientes son referencias para sesiones posteriores H0.2/H0.3; no se ejecutan en esta primera entrega.

1. Inspecciona la referencia necesaria y registra commit base y cambios locales relevantes.
2. Distingue invariantes reutilizables de lógica específica de ReferenceProject.
3. Documenta formatos de contratos, resultados, revisiones, validaciones y eventos.
4. Crea fixtures sintéticos pequeños para aceptación, revisión, bloqueo, interrupción y cierre.
5. Propón una estructura de módulos Python con núcleo independiente, API FastAPI, SQLite y frontend React/TypeScript.
6. Documenta capacidades y dudas de los adaptadores CLI, App Server y Agent SDK, verificando documentación oficial antes de asumir contratos externos.
7. Conserva un registro de decisiones y un estado de desarrollo que distinga propuesta de implementación real.
8. Ejecuta únicamente verificaciones offline apropiadas a lo creado.

Invariantes que deben conservarse:

- Codex planifica/revisa y Claude ejecuta en el flujo del producto, pero esta sesión de desarrollo es manual.
- Los agentes no deciden por sí solos estados mecánicos ni omiten validaciones.
- Cada intento tiene contexto explícito y versiones registradas.
- Reanudar trabajo no implica recuperar una conversación.
- No hay dos escritores del motor sobre el mismo checkout.
- Una aprobación está vinculada a acción, alcance e intento.
- Revisiones y validaciones corresponden a una versión exacta del contenido.
- No hay fallback de modelo o consumo adicional silencioso.
- El historial distingue datos observados, solicitados, estimados y ausentes.
- El núcleo no incluye reglas Django, PostgreSQL ni comandos propios de ReferenceProject.

Al terminar, entrega cambios concretos, comprobaciones realizadas, decisiones pendientes y la siguiente tarea acotada. No declares implementada ninguna capacidad que solo esté documentada.
