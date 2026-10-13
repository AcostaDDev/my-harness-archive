# Siguiente paso — propuesta de contención del proceso Codex

Estado al 2026-10-13:

- **Diagnóstico offline del cambio global completado (D062).**
  [Evidencia, conclusión y opciones](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md),
  [manifiesto de verificaciones](discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.json).
- Delta D061 acreditado: una sección de confianza de 93 bytes para el
  checkout Codex→Codex. Quitarla solo en memoria reproduce el SHA-256 previo;
  entrada añadida y ningún otro cambio de bytes entre los hashes registrados.
  Configuración global conservada, sin copiarla o restaurarla.
- La CLI 0.162.1 contiene una ruta interna de persistencia de confianza en
  config.toml. Flags de omisión de carga/reglas y sesión efímera no establecen
  contención del proceso. La atribución al arranque de Codex es muy probable,
  pero sigue inferida sin auditoría del proceso original.
- **Corrección de transporte no implementada:** override de trust sin garantía
  de supresión; CODEX_HOME privado desplaza auth también. HOME/USER, almacén,
  credenciales y `cli-7` conservados. Cinco casos sintéticos y hashes correctos;
  cero CLI de proveedores, sesiones, preflight o inferencia en D062.
- D060 cerrada con parada preventiva (D061): 2 Codex→Codex COMMITTED
  (`585a35c`), 3/4 no lanzadas con estado vacío. Consentimiento agotado.
  Claude real con esquema tipado D058 continúa pendiente. Evidencias D057/D061
  conservadas; la 1 D057 ya completa no necesita repetirse.

## Tarea concreta propuesta, no iniciada

**Concretar una propuesta de contención del proceso CLI de Codex que preserve
la autenticación existente, con alcance y criterios antes de implementar.**

1. Leer D062, D024/D049 y las fronteras actuales: entorno congelado,
   sandbox de herramientas, configuración privada y autenticación de la CLI.
   Separar qué protege al modelo de qué puede escribir el propio proceso.
2. Comparar las opciones viables para la versión fijada: contención externa
   del proceso y separación de estado/auth si la CLI la admite. Concretar
   fuentes de auth, efectos auxiliares/refresh, errores observables,
   portabilidad y límites. No suponer que una raíz privada mantenga login.
3. Preparar alcance y verificaciones con HOME, credenciales ficticias y
   procesos sintéticos. Deben acreditar lectura de auth ficticia sin alterar
   originales, contención de configuración/temporales y fallo explícito sin
   retries/fallback. Estas pruebas no certifican una sesión del proveedor.
4. Documentar la opción sustentada o el límite, el impacto en permisos,
   versiones/cuarentena y el consentimiento que exigiría una comprobación
   real. Señalar contradicciones materiales antes de cambiar diseño.
   Actualizar STATE/NEXT_STEPS/DECISIONS; dejar la implementación separada.

Criterios de aceptación: propuesta concreta y revisable que identifica auth y
estado, evidencia offline, efectos permitidos/impedidos y límites; conserva
contratos/historiales, D024/D059 y configuración global. Sin copiar/enlazar
credenciales reales, hacer login/refresh, invocar CLI de proveedores o alterar
baseline/modelos/permisos. Si no hay opción verificable, registrar exactamente
qué falta en vez de declarar aislamiento implementado.

No iniciar otro smoke/matriz, preflight real, jobs, recuperación, liberación
de locks o H6.2. Una comprobación real futura y las combinaciones pendientes
requieren propuesta y consentimiento específicos nuevos. D050, D055, D057 y
D060 siguen agotados. Sin publicación, push ni harness de desarrollo.

Después, y aparte: hito de interfaz de producto (D054, H6.2). Alternativas
pendientes: `forbidden_paths` frente a prosa; instalación de operación
reutilizable (D051); `memory/` vacío de Claude; endurecimientos de D048.
Ninguna iniciada en D062.
