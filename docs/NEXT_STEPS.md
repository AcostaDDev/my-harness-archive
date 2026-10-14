# Siguiente paso — concretar continuidad documental por fase

Estado al 2026-10-14:

- **Comprobación funcional de flujos de modelos cerrada (D071).**
  [Cuatro combinaciones reales](discovery/PROVIDER_MATRIX_CLI9_RUN.md),
  [manifiesto y hashes](discovery/PROVIDER_MATRIX_CLI9_RESULT.json).
- Codex→Codex, Codex→Claude, Claude→Claude y Claude→Codex completan
  planificación, edición real, validaciones/JUnit, ACCEPT y commit exacto.
  Doce invocaciones completas. El ejecutor no hace commit: acepta el revisor
  y lo realiza mecánicamente el harness. Procesos/owners/servicios cerrados,
  cero locks, claves retiradas y muestras de config/memorias intactas.
- cli-9 suprime específicamente confianza persistida por el escritor Codex,
  con projects inline untrusted acreditado en fuente del pin y prueba real;
  mantiene workspace-write/raíces/auth. [D068](discovery/CODEX_TRUST_SUPPRESSION.md).
  Controles de auto memory D066 conservados. Jobs anteriores en cuarentena
  antes de preflight, sin reescribir historiales.
- [D069/D070 conservados](discovery/PROVIDER_MATRIX_CLI9_STOPS.md): contrato
  contradictorio y timeouts. Prompt/contrato corregidos para parar antes de
  editar ante contradicciones. Errores de stream siguen rechazándose aunque
  después exista terminal/exit 0. No retries/fallback silenciosos.
- 948 pytest + 121 subtests y 12 checks estándar aprobados; builds y wheel
  instalado offline verificados. Git/documentos/diff/hashes revisados.
- El éxito funcional no certifica aislamiento físico, ausencia de auxiliares
  de CLI/logs/cachés/SQLite/auth refresh, cuota o retries internos. Tampoco
  acredita archivado ni continuidad documental por fase: docs del fixture
  se preservaron, no se ejecutó ese recorrido. No se integra D063/D067.

## Tarea concreta propuesta, no iniciada

**Concretar la organización de Markdown por fase y la continuidad de trabajo
con STATE/NEXT_STEPS frescos, antes de implementar el archivado.**

1. Revisar el contrato existente de exportación documental y la referencia
   ReferenceProject solo en lectura, sin sus runs/datos privados. Identificar qué
   ya existe y qué exige la organización por fase pedida por el usuario.
2. Proponer rutas, documentos activos/históricos, índice de entrada y reglas
   de cierre/archivo. Mantener SQLite como autoridad operativa del harness;
   Markdown como contexto duradero del proyecto, sin doble autoridad.
3. Definir actualización/reconciliación por contenido exacto y quién escribe
   cada documento. El ejecutor deja cambios para revisión; el commit sigue
   condicionado a aceptación y validación. No diseñar memoria global del modelo.
4. Delimitar una implementación posterior y criterios verificables con fixtures
   sintéticos: nueva sesión reconstruye la tarea desde docs, archivo de fase
   conserva historia y fase activa mantiene STATE/NEXT_STEPS actuales.

Criterios de esta tarea de diseño: contrato concreto, diferencias frente a lo
implementado explícitas, trazabilidad de decisiones y alcance posterior acotado.
No marcar como implementado/probado lo que solo está definido. No modificar
ReferenceProject, mover historias reales automáticamente, consumir proveedores ni
iniciar UI H6.2/otra implementación aquí. Actualizar STATE/NEXT_STEPS/DECISIONS.

D071 satisfecha y agotada; D069/D070 y consentimientos anteriores también.
Otra prueba real requiere propuesta y consentimiento nuevos. No quedan runs
activos de esta matriz que recuperar. Sin push/publicación, relanzamiento o
liberación manual de locks. La siguiente tarea no se inicia en la entrega actual.
