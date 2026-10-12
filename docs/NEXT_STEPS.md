# Siguiente tarea — H2.3: diagnóstico de autenticación Claude en lectura

Smoke `cli-3` autorizado y ejecutado el 2026-10-12 sobre `039a01e`: Codex
planificador COMPLETE (exit 0, terminal/JSON); Claude FAILED (exit 1, terminal
de error) por `authentication_failed` y «Not logged in · Please run /login».
MCP vacío aceptado; herramientas y servidores vacíos observados. Revisor no
lanzado, sin corrección, login ni relanzamiento. D022,
[resultado y evidencias](discovery/H2.3_SMOKE_CLI3.md),
[alcance completado](discovery/H2.3_SMOKE_CLI3_SCOPE.md).
211 pruebas/121 subtests y 12 checks ligeros correctos en preparación;
persistencia, 31 eventos/hashes/rangos, grupos muertos y checkout intacto
comprobados después. H2.4 no iniciado.

## Objetivo

Determinar por qué Claude Code 2.1.295 no dispone de autenticación en el entorno
explícito del smoke, conservando las suscripciones/auth propias de las CLI.
El fallo acredita este contexto, no ausencia de login en todo el Mac. Separar
diagnóstico observado, hipótesis y causa comprobada. No extraer credenciales ni
usar inferencia para probar autenticación.

## Alcance acotado

1. Revisar D008/D017/D022, informe y spec del smoke. Conservar resultados,
   capturas y bloqueo anteriores sin reanudar ni recuperar automáticamente.
2. Consultar help/documentación oficial y mecanismos locales de estado de auth
   en lectura, sin ejecutar print/agentes/modelos. Filtrar la salida en memoria:
   solo estado/método de auth y diagnósticos necesarios, sin correo, IDs de cuenta,
   tokens, cookies, contenido de almacenes de credenciales ni dumps del entorno.
3. Comparar el contexto explícito `HOME`, `PATH`, `TMPDIR`, `LANG`, ejecutable,
   fuentes de settings aisladas y restricciones del proceso con la sesión propia
   del usuario. Inspeccionar solo metadatos/configuración no secreta pertinentes;
   no ampliar el entorno ni heredar variables de credenciales automáticamente.
4. Si el diagnóstico exige login o intervención del usuario, documentar el
   paso concreto para su sesión sin hacerlo automáticamente. Si revela un cambio
   necesario del adaptador, proponer una tarea offline separada con regresión y
   versión congelada; no mezclar esa implementación con el diagnóstico.
5. Actualizar STATE/NEXT_STEPS/DECISIONS e informe con evidencia saneada y límites.
   No ejecutar otro smoke ni iniciar H2.4.

## Criterios de aceptación

- Diagnóstico en lectura reproducible y limitado al contexto observado, o
  incertidumbre pendiente explícita con la comprobación/intervención necesaria.
- Estado de auth observado separado de acceso al modelo, inferencia y cuota;
  no deducirlos de help/status o de los ceros reportados en el fallo.
- Sin extracción/exposición de secretos ni modificación global/login automática.
- Modelo/proveedor/suscripción, aislamiento de herramientas/MCP y configuración
  congelada conservados; no sustitución por API keys ni ampliación silenciosa.
- Resultados/capturas de D018/D020/D022 y lock anterior preservados;
  documentación/checks proporcionales revisados, sin nuevas invocaciones de agente.

## Fuera de alcance

La autorización D022 terminó al primer fallo. Otro smoke requiere propuesta
y consentimiento específicos; este diagnóstico o su commit no autorizan consumo.
Sin login/logout/refresh, lectura de secretos/keychain, fallback, relanzamiento,
corrección del adaptador, SDK/MCP/herramientas activos, cambios globales,
H2.4/H2.5, entradas gestionadas API/CLI/UI, permisos vivos, chat, publicación o push.
