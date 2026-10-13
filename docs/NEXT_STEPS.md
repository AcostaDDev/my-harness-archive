# Siguiente paso — diagnóstico offline del cambio de configuración global

Estado al 2026-10-13:

- **D060 ejecutada una vez y cerrada con parada preventiva (D061).**
  [Resultado y límites](discovery/PROVIDER_MATRIX_CLI7_RUN.md),
  [manifiesto de resultado/verificaciones](discovery/PROVIDER_MATRIX_CLI7_RESULT.json).
  Autorización específica del usuario recibida; consentimiento agotado.
- Combinación 2 Codex→Codex `COMMITTED` (`585a35c`): tres intentos completos,
  edición real solo de `src/estimate.ts`, check/test/build correctos, JUnit
  con tres casos aprobados, ACCEPT y commit por contenido exacto. Jobs DONE,
  propietarios cerrados, procesos muertos, cero locks y servicio detenido.
- La comprobación entre combinaciones detectó un cambio de hash en
  `~/.codex/config.toml`. mtime coincide con el inicio del escritor y se
  observa una entrada `trust_level = "trusted"` para el checkout de la 2.
  La línea base solo conserva hashes: delta exacto y atribución a la CLI
  siguen sin demostrarse. Configuración global conservada sin restaurar.
- Combinaciones 3 Claude→Claude y 4 Claude→Codex **no lanzadas**: parada por
  condición global de D060. Sus áreas siguen vacías y limpias, sin SQLite,
  jobs ni intentos. Tres invocaciones Codex y cero Claude; sin retries.
- Paquete/scripts/TOML coinciden con D060. D059 acredita escritura real en
  este ensayo; Claude real con esquema tipado D058 sigue pendiente. D057
  conserva su combinación 1 COMMITTED y el resto de su evidencia anterior.

## Tarea concreta propuesta, no iniciada

**Diagnosticar offline el cambio observado en la configuración global de
Codex antes de preparar otra ejecución.** Sin inferencia ni consumo.

1. Leer D061, línea base, resultado, specs y originales conservados en
   `/private/tmp/harness-provider-matrix-3`. Separar el cambio de hash
   observado de la hipótesis sobre el escritor; no deducir el delta completo
   desde el estado posterior ni inventar una copia previa.
2. Inspeccionar en lectura el comportamiento de la CLI fijada 0.162.1 y
   las rutas de configuración/confianza usadas con `--ignore-user-config`,
   `--ignore-rules`, `--strict-config` y `--ephemeral`. Comprobar qué puede
   acreditarse sin lanzar sesiones ni tocar el HOME real.
3. Si se identifica una corrección compatible, documentar el alcance y
   probarla offline con HOME/fixtures sintéticos y sin credenciales. Conservar
   autenticación D024, permisos, contratos y versiones congeladas; un cambio
   de transporte exige versión y cuarentena correspondientes. Si implica
   una contradicción material de diseño o no puede verificarse offline,
   registrar el límite antes de implementar.
4. Verificar el diff y los checks pertinentes, actualizar STATE/NEXT_STEPS
   y DECISIONS con causa acreditada, hipótesis pendientes y siguiente paso.
   No restaurar ni borrar configuración global o evidencias previas.

Criterios de aceptación: diagnóstico trazable que distingue observado,
inferido y ausente; efectos globales y aislamiento efectivo descritos;
corrección solo si está justificada y verificable offline, sin reescribir
historiales ni silencios de fallback. Esta tarea no incluye otra matriz,
preflight real, login, nuevas invocaciones, recuperación o liberación de
locks. Una ejecución futura de 3/4 necesita propuesta/consentimiento nuevos.

Después, y aparte: hito de interfaz de producto (D054, H6.2). Alternativas
pendientes: `forbidden_paths` frente a prosa; instalación de operación
reutilizable (D051); `memory/` vacío de Claude; endurecimientos de D048.
Ninguna iniciada en D061. Sin publicación, push ni uso del harness para
desarrollar este repositorio. D050, D055, D057 y D060 están agotados.
