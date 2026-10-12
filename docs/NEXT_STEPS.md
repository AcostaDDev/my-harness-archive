# Siguiente tarea — H2.3: corrección offline del entorno explícito del smoke

Diagnóstico de autenticación Claude completado en lectura el 2026-10-12,
D023. Fuera del sandbox, Claude Code 2.1.295 reconoce sesión `claude.ai` con
USER presente; el entorno mínimo HOME/PATH/TMPDIR/LANG no la reconoce.
Añadir solo USER la restaura, retirarlo del entorno de la sesión la impide;
LOGNAME no basta. Sin login, inferencia ni corrección. Status no admite los
flags de fuentes aisladas; transporte completo sigue pendiente.
[Informe y reproducción](discovery/H2.3_AUTH_DIAGNOSIS.md),
[alcance completado](discovery/H2.3_AUTH_DIAGNOSIS_SCOPE.md).
Doce checks ligeros correctos; D020/D022 conservan capturas/hash, resultados,
24/31 eventos y locks. D018 ya ausente según informes anteriores. H2.4 no iniciado.

## Objetivo

Corregir offline la construcción del entorno explícito del smoke para que
Claude reciba USER correspondiente al usuario local, conservando autenticación
propia de las CLI, fuentes/tools/MCP aislados y configuración congelada.
No modificar el adaptador para heredar automáticamente el entorno del supervisor.

## Alcance acotado

1. Revisar D008/D017/D022/D023, script del smoke y contrato de CLIConfig.
   Conservar resultados/specs/historial/locks anteriores sin recuperación.
2. Incluir USER explícito y comprobado contra el usuario local en la construcción
   del entorno del smoke; resolver ausencia/discrepancia antes de consumo con
   diagnóstico concreto. No copiar variables de credenciales ni ampliar fuentes.
3. Añadir regresión offline independiente con proceso sintético que distinga
   USER ausente/presente, pruebe entorno completo sin herencia silenciosa y
   conservación de HOME/PATH/TMPDIR/LANG y permisos/selecciones existentes.
   No usar status real ni inferencia como test automatizado.
4. Congelar la configuración nueva con hash distinto. Probar que un job con
   configuración anterior no se ejecuta silenciosamente con la nueva, sin
   reescribir historia/resultados. Si cambia el comportamiento del adaptador,
   elevar su versión; no versionarlo por mera edición documental.
5. Ejecutar checks offline pertinentes y actualizar STATE/NEXT_STEPS/DECISIONS
   e informe. Preparar por separado una propuesta de verificación real con
   sus límites, sin ejecutar otro smoke dentro de esta corrección.

## Criterios de aceptación

- USER válido transmitido explícitamente y sin credenciales heredadas; ausencia
  o discrepancia resuelta antes de cualquier llamada a proveedor.
- Regresión sintética demuestra el defecto previo y el comportamiento corregido,
  sin requerir sesión real, secretos ni red.
- Configuración/hash nuevos congelados y selección de modelos/esfuerzos conservada;
  jobs antiguos bloqueados ante incompatibilidad, sin sustituir specs/resultados.
- Fuentes/settings/hooks, herramientas/MCP vacíos, sesiones frescas y ausencia
  de fallback/reinvocación automática conservados.
- Evidencias disponibles D020/D022 y lock anterior preservados; históricos
  documentales D018/D020/D022 intactos, sin reconstruir el área D018 ausente.
- Checks/diff/documentación revisados; no presentar pruebas offline o status
  como éxito real completo ni como prueba de acceso al modelo, inferencia o cuota.

## Fuera de alcance

La autorización D022 terminó al fallo. Diagnóstico D023 y su commit no autorizan
consumo. Sin otro smoke, login/logout/refresh, lectura de secretos/keychain,
API keys, cambios globales, fallback, recuperación/liberación automática,
SDK/MCP/herramientas activos, H2.4/H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat, publicación o push.
