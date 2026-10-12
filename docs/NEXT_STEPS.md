# Siguiente tarea — H2.3: corregir configuración MCP de Claude offline

El nuevo smoke autorizado con `cli-2` terminó el 2026-10-12: Codex planificador
COMPLETE (exit 0, terminal y uso reportado); Claude FAILED (exit 1) por
configuración MCP inválida. Revisor no lanzado, sin fallback ni relanzamiento.
[Resultado y evidencias](discovery/H2.3_SMOKE_RETRY.md), D020. El primer
[smoke D018](discovery/H2.3_SMOKE.md) queda separado e intacto.
209 pruebas y 121 subtests, 12 checks ligeros correctos. H2.4 no iniciado.

## Objetivo

Corregir exclusivamente el argumento MCP vacío de Claude Code 2.1.295 sin
activar servidores/configuración del usuario, manteniendo herramientas vacías,
sesiones nuevas, selección explícita y denegación dontAsk. La spec real conserva
`--strict-mcp-config --mcp-config '{}'`; la CLI exige el campo `mcpServers`.
Comprobar el formato válido con help/documentación o validación local sin
inferencia. No presentar preflight/fakes como éxito real del proveedor.

## Alcance acotado

1. Leer D020 y el informe real. Conservar sus evidencias y resultados anteriores.
2. Confirmar el contrato de `--mcp-config` para la versión fijada y sustituir el
   argumento inválido por una configuración explícita de cero servidores.
   No eliminar el modo estricto ni heredar fuentes de configuración del usuario.
3. Añadir una regresión sintética que rechace el formato observado antes de
   simular inferencia, independientemente del código del adaptador. Caracterizar
   que versión/help pueden pasar aunque el argumento sea inválido.
4. Verificar argv corregido, herramientas vacías, prompts/hooks/configuración
   aislados, captura de fallo y parada sin revisor ni llamadas adicionales.
5. Versionar el cambio del adaptador/configuración; jobs congelados `cli-2` no
   deben ejecutar silenciosamente un argv diferente. Preservar historial previo.
6. Ejecutar checks offline pertinentes, revisar diff, actualizar STATE/NEXT_STEPS/
   DECISIONS y preparar la siguiente propuesta real sin ejecutarla.

## Criterios de aceptación

- Configuración MCP vacía válida para Claude 2.1.295, sin servidores heredados.
- Regresión independiente reproduce el rechazo antiguo y permite el argv
  corregido; preflight no se presenta como validación semántica completa.
- Herramientas/autenticación/selecciones/permisos y demás garantías H2.3
  conservados; ausencia/null/cero y resultados anteriores preservados.
- Versiones congeladas impiden sustitución silenciosa del comportamiento.
- Checks offline pasan, evidencia real separada y límites pendientes explícitos.
- Ninguna nueva inferencia, fallback, relanzamiento ni avance a H2.4.

## Fuera de alcance

La autorización D020 concluyó al primer fallo. Corrección, tests, commit o
continuación no autorizan otro smoke: requerirá propuesta y consentimiento
específicos. No consumir proveedores, extraer credenciales, alterar configuración
global, activar SDK/MCP/herramientas ni lanzar agentes de colaboración.
H2.4 Git/worktrees/commit de producto, H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat y distribución quedan fuera de esta tarea.
