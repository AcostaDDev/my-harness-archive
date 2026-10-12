# Siguiente tarea — H2.3: propuesta de nuevo smoke real con cli-3

Corrección MCP offline completada el 2026-10-12 como `cli-3`: configuración
Claude explícita `{"mcpServers":{}}` con modo estricto, sin servidores ni
herramientas heredados por esas opciones. Jobs congelados `cli-2`/`cli-1`
bloqueados antes de efectos; historial anterior conservado. D021,
[entrega y límites](discovery/H2.3_MCP_FIX.md),
[alcance completado](discovery/H2.3_MCP_FIX_SCOPE.md).
211 pruebas y 121 subtests, 12 checks ligeros correctos. H2.4 no iniciado.

## Propuesta concreta pendiente de consentimiento

Una ejecución nueva de `scripts/smoke_cli.py`, hasta tres invocaciones de 60 s
cada una, en un checkout sintético nuevo bajo `/private/tmp`, con SQLite y
artefactos externos. No reanudar D018/D020 ni reutilizar sus jobs/configuraciones.

| Rol | CLI fijada | Modelo solicitado | Esfuerzo |
|---|---|---|---|
| Planificador | Codex 0.162.1 | `gpt-6-luna` | `low` |
| Ejecutor | Claude Code 2.1.295 | `claude-sonnet-4-6` | `low` |
| Revisor | Codex 0.162.1 | `gpt-6-luna` | `low` |

Adaptador `cli-3`, selección/configuración congeladas antes de lanzar.
Codex read-only/approval never; Claude dontAsk/prompts none, tools/allowedTools
vacíos, MCP vacío/estricto, fuentes de settings vacías y hooks desactivados.
Sesiones nuevas; entorno explícito `HOME`, `PATH`, `TMPDIR`, `LANG`, sin API keys
ni extracción de credenciales. Suscripciones/auth propias de las CLI.
Red e inferencia pueden consumir cuota; `uv --offline` solo limita uv.
Retries internos de ambas CLI siguen desconocidos, sin garantía de una única
inferencia por invocación. No se certifica aislamiento total con estos flags.

Parar al primer error, timeout, salida inválida/parcial o ausencia de terminal:
preservar bytes, eventos, spec y resultados; no ejecutar roles restantes,
cambiar selecciones/proveedores ni relanzar. La autorización D020 concluyó con
su fallo; esta propuesta, la corrección offline y su commit no autorizan consumo.

## Orden de trabajo tras autorización específica

1. Revisar Git, D021, informe de corrección y script. Confirmar versión/help
   locales y selecciones exactas; incompatibilidad bloquea sin consumo.
   Preflight no certifica semántica completa de argumentos ni acceso/auth/cuota.
2. Ejecutar una sola vez el script con guardia de consumo, selecciones de la
   tabla y output nuevo. No usar el harness para desarrollar ni lanzar agentes
   de colaboración. Si no hay autorización específica, no ejecutar este paso.
3. Comprobar terminal/exit code, JSON, captura/hash/rangos y persistencia para
   cada rol efectivamente lanzado; separar selección solicitada de metadatos
   reportados y ausencia/null/cero. No inferir aceptación de tarea del transporte.
4. Al fallar, conservar RECOVERY_REQUIRED/lock y comprobar propietario cerrado
   y liveness conservadora de grupos, sin recuperación automática. No corregir
   ni relanzar dentro de esta tarea; documentar el diagnóstico y próxima tarea.
5. Revisar diff, actualizar STATE/NEXT_STEPS/DECISIONS e informe independiente
   con hashes/procedencia/límites; no copiar evidencia privada a fixtures.

## Criterios de aceptación

- Evidencia de las CLI/argv/selecciones congeladas `cli-3`, MCP explícitamente
  vacío, permisos conservados, checkout sintético intacto y artefactos externos.
- Rama de éxito: tres transportes completos con terminal/exit 0/JSON y
  resultados persistidos; sin afirmar aceptación/commit de producto.
- Rama de error: parada al primer fallo con evidencia exacta y resultados
  persistidos, roles restantes no lanzados y ninguna llamada adicional/fallback.
- Datos observados y ausentes diferenciados; no deducir factura/cuota o retries
  efectivos a partir de telemetría incompleta.
- Historial D018/D020 separado; no corrección, relanzamiento ni avance a H2.4.

## Fuera de alcance

Consumo sin consentimiento específico, cambios globales/auth, SDK/MCP/herramientas
activos, producto Git/worktrees/commit H2.4, H2.5, entradas gestionadas API/CLI/UI,
permisos vivos, chat, distribución, publicación y push.
