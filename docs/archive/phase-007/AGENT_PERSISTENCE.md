# Persistencia de proyecto y memoria automática de las CLI (D066)

2026-10-14, sobre `7cd3503`, Git inicialmente limpio. El usuario exige contexto
duradero de trabajo en Markdown organizado bajo `docs/`, historial por fase y
STATE/NEXT_STEPS frescos; después pide continuar con la persistencia de las CLI.
[Inventario estático reproducible](AGENT_PERSISTENCE_INVENTORY.py),
[procedencia y verificaciones](AGENT_PERSISTENCE.json).

## Resultado

**Desactivación explícita de memoria automática implementada en el transporte
`cli-8` y verificada offline. Ausencia total de persistencia externa aún no
certificada.** La escritura de confianza de Codex D061/D062 sigue sin resolver.
No se presenta una configuración de memoria como contención del proceso CLI,
ni se integra el sandbox D063–D065, que conserva su dictamen desfavorable.

El trabajo elegido concreta la opción de capacidades soportadas de D065 y
mantiene la prohibición de cambios globales. No se acepta una relajación del
aislamiento ni un cambio de autenticación. SQLite conserva la autoridad
operativa del harness; los documentos conservan contexto y decisiones del
proyecto. El archivado automático por fase y la continuidad documental real
permanecen como alcances separados, sin implementar en esta entrega.

## Inventario y fuentes

Lectura estática de los binarios existentes: Codex 0.162.1 con el mismo hash
de D059/D062; Claude 2.1.295 y 2.1.296 con hashes y offsets en el manifiesto.
No se ejecutaron, ni version/help. No se abrieron auth.json, config.toml,
settings personales, llavero ni directorios de memoria reales.

```sh
python3 docs/discovery/AGENT_PERSISTENCE_INVENTORY.py
```

La sonda solo lee ejecutables públicos fijados por hash y emite metadatos y
offsets de literales. Su presencia no acredita precedencia, selección efectiva
o efectos en ejecución. Codex incluye MemoriesToml, generate_memories,
use_memories, HistoryPersistence y una vía separada de trust_level. Claude
incluye autoMemoryEnabled, el override ambiental y diagnósticos de desactivación.
El binario Codex 0.161.0 no estaba disponible para esta lectura; ese lector
conserva su baseline y solo se prueba con procesos sintéticos en esta entrega.
No se certifican los controles nuevos en esa versión real.

Se contrastó la semántica con documentación oficial consultada el 2026-10-14.
Hubo **consulta documental web**, sin llamadas de proveedor ni consumo de
modelos. Las comprobaciones y pruebas de código fueron offline:

- [OpenAI, configuración](https://learn.chatgpt.com/docs/config-file/config-reference):
  `features.memories` controla la función; `memories.generate_memories=false`
  excluye nuevos threads de los inputs de generación; `memories.use_memories=false`
  evita inyectar memorias existentes; `history.persistence="none"` desactiva
  el historial indicado. La documentación actual no certifica el comportamiento
  exacto del pin ni prohíbe otras escrituras de la CLI.
- [Claude, memoria](https://code.claude.com/docs/en/memory):
  `autoMemoryEnabled=false` desactiva memoria automática; su ubicación habitual
  es `~/.claude/projects/<proyecto>/memory`. Se usa un setting inline por
  invocación, sin editar settings personales ni redirigirla a otra memoria.
- [Claude, entorno](https://code.claude.com/docs/en/env-vars):
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=0` puede forzar activación pese al setting;
  `1` desactiva creación/carga de archivos de memoria automática.

No se adopta una API/SDK ni se cambia proveedor/modelo/esfuerzo o versión
instalada. Tampoco se usa una documentación de auth para asumir que redirigir
CODEX_HOME/CLAUDE_CONFIG_DIR conserve la sesión existente.

## Cambios aplicados

Todos los roles —planner, executor, reviewer, phase, chat y bootstrap— reciben
los controles pertinentes del proveedor, sin alterar solicitudes congeladas:

| Proveedor | Controles añadidos | Controles conservados |
|---|---|---|
| Codex | `-c features.memories=false`, `-c memories.generate_memories=false`, `-c memories.use_memories=false`, `-c history.persistence="none"` | `--ephemeral`, sesiones nuevas, fuentes/reglas omitidas, sandbox por rol, permisos y raíces D059. |
| Claude | `--settings '{"disableAllHooks":true,"autoMemoryEnabled":false}'` | `--no-session-persistence`, UUID nuevo, fuentes vacías, hooks/MCP aislados, tools y esquema tipado D058. |

CLIConfig rechaza antes de efectos un override Claude
`CLAUDE_CODE_DISABLE_AUTO_MEMORY` distinto de `1`, si se declara. Ausente se
usa el setting inline; explícitamente `1` se conserva. Se evita que un TOML
del operador reactive esa memoria. No se heredan variables ni se añaden o
reescriben HOME/USER/PATH/TMPDIR/LANG. Tampoco se copian/enlazan credenciales,
cambia almacén, consulta login o se borran directorios existentes.

El cambio de argv exige **`cli-8`**. Esa versión identifica estos controles,
no el backend de contención hipotético de D063. Los jobs `cli-7` u otras
versiones anteriores se ponen en cuarentena antes del preflight/efectos por
la comparación existente. Configuración y resultados previos no se reescriben.
El TOML permanece local-config-2 (y lectura local-config-1); no hay nuevos
campos, esquema, codec, API/UI, dependencias, permisos o cambios de motor.
El argv efectivo queda en la intención de proceso existente antes del GO.

## Persistencias diferenciadas y límites

| Efecto | Qué resuelve esta entrega | Pendiente |
|---|---|---|
| Memoria automática generada o inyectada | Desactivación solicitada explícitamente en cada invocación, con guardia contra override conocido Claude. | Comprobación dinámica del pin; ninguna ausencia de archivo real se afirma aquí. |
| Conversación/historial de CLI | Flags efímeros conservados, historial Codex desactivado explícitamente. | No constituye prohibición de toda persistencia o estado auxiliar. |
| Carpeta memory/ de Claude observada vacía | Control específico que faltaba en D050/D057. | Verificar con CLI real que no se cree/cargue memoria; otros directorios de proyecto pueden tener finalidades distintas. |
| Configuración de confianza Codex | Se mantiene el delta acreditado y la prohibición global. | No hay supresión demostrada; estos controles de memoria no son un remedio para D061. |
| Logs, cachés, SQLite/WAL/locks y estado auxiliar | Rutas/configuración del harness conservadas; sin redirección especulativa. | Inventario/efectos reales y supresión o destino compatible con autenticación. |
| Auth y refresh | HOME/USER y autenticación original no intervenidos. | Fuente efectiva, rotación remota y continuidad de sesión sin certificar. |

También permanecen las limitaciones de instrucciones estáticas cargadas por
las CLI, lectura general, servicios externos y herramientas de escritura.
Apagar auto memory no certifica que todo contexto provenga únicamente del
snapshot del harness, ni que herramientas/infraestructura no puedan modificar
otros archivos. No se confunde esto con los ensayos de contención de D065.
No se borra memoria anterior del usuario ni se cambia su comportamiento fuera
de las invocaciones de Harness Local.

La lectura adicional acotada de D062 confirma una llamada a
`FileSystemSandboxPolicy::can_write_local_path_with_cwd` antes de la rama que
llama a `set_project_trust_level` (direcciones `0x1018769c0` y `0x101876bb8`).
Es consistente con el efecto observado al entrar el escritor. No se mapeó
todo el layout ni se probó que un override de confianza evite persistir.
No se introduce ese override ni se elimina workspace-write para sortearlo.

## Verificación

20 casos nuevos: controles por rol/proveedor, rechazo de overrides conflictivos,
ausencia de un control con fallo único/captura original, y cuarentena `cli-7`
sin preflight/procesos o reescritura de historial. La matriz sintética existente
de cuatro combinaciones exige ahora esos controles antes de simular inferencia.
No se modelan sus efectos internos como si fuesen resultados de la CLI real.

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_cli_memory.py tests/product/test_cli_agents.py tests/product/test_agent_roles.py tests/product/test_codex_workspace_write.py tests/product/test_typed_json_schema.py tests/product/test_local_config.py tests/product/test_smoke_environment.py tests/product/test_cli_diagnostics.py
```

**215 passed en 54,67 s**, sin proveedores; 941 tests recolectados en total.
El primer pase tuvo 212 passed, dos fallos por `/bin/ps` bloqueado en el
sandbox y una fixture `web` ausente en el test nuevo. Fixture corregida y
repetición exterior autorizada mediante permisos de herramienta; no se
modificó el diagnóstico del producto para ocultar la denegación del entorno.
También inventario por hashes, sintaxis, enlaces, JSON y diff/whitespace.
No suite completa, build, Node separado o QA visual: UI/API no cambian y los
recorridos pertinentes ya incluyen Git/SQLite/Node con agentes sintéticos.

Los temporales originales de D062 y la matriz D061 no estaban disponibles
en esta sesión. Se usan informes/manifiestos versionados y el binario fijado,
sin reconstruir runs, atribuir nuevas observaciones o modificar su evidencia.

## Siguiente trabajo concreto separado

**Preparar un diagnóstico del arranque Codex, sin inferencia, con HOME/auth
ficticios y red denegada, para comprobar su persistencia de confianza.**
Debe fijar controles que impidan lectura de credenciales/configuración reales,
ejecutable/hash, argv, aislamiento, número de procesos/timeouts, capturas y
condiciones de parada. Comparar, si procede, confianza de transporte solo en
memoria y ausencia de override sobre un HOME sacrificial; un fallo previo a
thread/start no demostraría ausencia de persistencia en esa ruta. No reutilizar
el perfil D063 como si hubiese quedado calificado ni prometer auth compatible.

Preparación y ejecución son tareas separadas. La CLI real, aunque no genere
inferencia, requiere una propuesta concreta y autorización nueva para ese
diagnóstico; no se ejecutó ni quedó autorizada por D066. Matriz 3/4, continuidad
documental/archivado y H6.2 no se inician. No se declara cerrada la fase de
comprobación de flujos; D050/D055/D057/D060 siguen agotados.
