# Diagnóstico del escritor Codex y raíces explícitas (`cli-7`, D059)

Completado offline el 2026-10-13. Tarea activa de NEXT_STEPS: explicar la
negativa del escritor en la combinación 2 de D057, leyendo Codex 0.162.1 sin
lanzar sesiones, y aplicar una medida acotada con regresión y cuarentena.
Git limpio al empezar. No se ejecutó el harness para desarrollar este repositorio.

## Conclusión y grado de certeza

**La causa inmediata observada es una interpretación incorrecta del modelo
sobre el alcance de escritura, antes de usar herramientas.** D057 no muestra
un error de escritura ni una denegación del sandbox. El modelo sostuvo que
`src/estimate.ts` no era escribible aunque estaba dentro de la raíz
`/private/tmp` que él mismo mencionaba. No hizo lecturas, comandos ni ediciones.

**La descripción de raíces temporales es una hipótesis de origen, no una causa
interna demostrada.** El binario contiene la plantilla de permisos que permite
editar `cwd` y `writable_roots`, además de vías para obtener raíces desde cwd,
`/tmp` y `TMPDIR`. En este Mac `/tmp` resuelve a `/private/tmp`, padre del
checkout. Esto es consistente con que el modelo mencionase `/private/tmp` y
`cli-tmp`. No conservamos el mensaje de permisos que Codex generó internamente
para aquella sesión: `prompt.txt` es solo la entrada del harness. Las cadenas y
los símbolos no prueban qué lista exacta se renderizó ni cómo se redujeron las
raíces redundantes. Tampoco prueban que una escritura real habría funcionado.

## Lectura local del binario

El wrapper npm instalado resuelve el ejecutable nativo:

```text
$HOME/.nvm/versions/node/v24.15.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex
```

- Tamaño: 246642624 bytes.
- SHA-256: `74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0`.
- `--version`: `codex-cli 0.162.1`.
- `exec --help`: `workspace-write`, `-c` con valores TOML, `--cd` (working
  root) y `--add-dir` (directorios adicionales escribibles).
- Ambos comandos terminaron con exit 0. El sandbox de desarrollo advirtió que
  no podía crear aliases PATH; no hubo sesión, autenticación ni inferencia.

Lectura de bytes, offsets de archivo decimales:

| Offset | Cadena relevante | Implicación |
|---:|---|---|
| 190135896 | Plantilla `workspace-write`: permite editar archivos en `cwd` y `writable_roots` | El checkout no requiere estar fuera de `/tmp` para ser escribible según la plantilla |
| 185940751 | `The writable roots are` | Hay una lista de raíces añadida a la descripción |
| 185943746 | `Ignoring invalid TMPDIR value` (junto a mensajes para cwd y `/tmp`) | Existen vías distintas de incorporación de raíces temporales y cwd |
| 186944906 | `writable_roots`, `network_access`, `exclude_tmpdir_env_var`, `exclude_slash_tmp` | Las opciones están presentes en la estructura de permisos |
| 186981005 | Rechazo de overrides `sandbox_workspace_write.writable_roots` con `--remote` | El override existe; el harness usa ejecución local sin `--remote` |

`nm -nm` y desensamblado selectivo de `objdump` también identificaron
`PermissionsInstructions::from_permission_profile`,
`SandboxPolicy::get_writable_roots_with_cwd` y
`FileSystemSandboxPolicy::has_configured_writable_roots_with_cwd`.
Solo se leyeron bytes y símbolos. No se invocaron esas funciones ni se
certificó su flujo completo por desensamblado.

Para repetir la lectura sin sesiones: localizar el nativo desde `bin/codex.js`,
calcular su SHA-256, buscar esas cadenas en sus bytes y consultar únicamente
`--version` / `exec --help`. No usar `exec` con un prompt ni comandos sandbox
que arranquen un agente para probar permisos.

## Contraste con D057 y `cli-6`

Evidencia conservada, leída sin modificar SQLite ni sus artefactos:

- BASE: `/private/tmp/harness-provider-matrix-2`.
- Checkout/cwd/`--cd`: `codex-codex/web`.
- Intento ejecutor: `a50e1ddb-8a57-4d25-a02c-e944c7cbaa7b`.
- `state/artifacts/matrix-codex-codex/<intento>/prompt.txt`: 2832 bytes,
  SHA-256 `704daa4004730125e93cc1d228eff23b12c23cc3a42e4ff6ef3e04603611b4d1`.
- `stdout.bin`: 594 bytes,
  SHA-256 `92b96cf0925ec4dd06e78924de7758de23ff2a7fe3c4d8b24b5ce114b1228349`.
- `stderr.bin`: vacío (SHA-256 del contenido vacío).
- `evidence/events.json`: intención de proceso con `cli-5`, modelo
  `gpt-6-luna`, esfuerzo `low`, `workspace-write`,
  `sandbox_workspace_write.network_access=false`, `approval_policy="never"`,
  búsqueda desactivada, `--ignore-user-config`, `--ignore-rules` y `--ephemeral`.
- El entorno del preparador fija `TMPDIR=BASE/codex-codex/cli-tmp`, hermano
  del checkout, y no define `writable_roots` ni excluye `/tmp`.
- Stdout contiene thread/turn, un único `agent_message` de negativa y terminal
  completo. No hay `command_execution`, `file_change` ni evento de error.
- El prompt ordena editar únicamente `src/estimate.ts`; no afirma que el
  checkout esté fuera del sandbox. La prosa de `forbidden_paths` ya registrada
  en D057 queda como tarea aparte; la negativa observada menciona permisos
  físicos, no ese glob.

`cli-6` conserva exactamente el argv Codex de `cli-5`. D058 solo cambió el
esquema de Claude lector. Por tanto, aquel incremento no mitigaba esta negativa.
No se copian runs reales a fixtures: todas las pruebas nuevas son sintéticas.

## Medidas elegidas e implementación

**`cli-7`**, solo para Codex ejecutor:

```text
--sandbox workspace-write
-c sandbox_workspace_write.network_access=false
-c sandbox_workspace_write.writable_roots=["<checkout canónico>"]
-c sandbox_workspace_write.exclude_slash_tmp=true
```

`--cd` y el cwd de proceso usan el mismo `ProjectContext.root`, ya canónico.
El array se codifica como un único argumento TOML sin shell, con escapes y
Unicode comprobados. No se añade otro checkout. Se conserva la incorporación
predeterminada del `TMPDIR` del entorno explícito para los temporales de la CLI;
no se habilita red ni aprobación ni se modifica la configuración global.
Excluir `/tmp` elimina el permiso automático sobre todos sus descendientes;
si el operador fija TMPDIR allí o en otro padre amplio, esa vía sigue vigente.
No se promete una única raíz efectiva para cualquier entorno del operador.

La entrada de transporte del escritor añade una aclaración con el checkout
canónico: el acceso solicitado incluye sus subdirectorios, las rutas del
contrato son relativas al checkout y siguen limitando qué se puede editar.
La aclaración distingue configuración solicitada de denegaciones reales, que
se deben respetar y reportar. Se guarda y hashea en el `prompt.txt` de la
intención, sin alterar `AgentRequest`, el catálogo o snapshots de prompts,
contratos ni permisos congelados. Los lectores y Claude conservan su argv y
entrada de transporte anteriores.

Se eligen las dos medidas porque son complementarias: nombrar el checkout
explica el acceso, y excluir la raíz temporal amplia reduce una posible fuente
de ambigüedad. **Añadir solo `writable_roots` podría dejar `/private/tmp` como
raíz padre en la descripción.** No se cambia la ubicación del smoke: sería
solo una medida del ensayo y no resolvería el uso del producto en checkouts
bajo `/tmp`. No se prepara ni ejecuta una nueva matriz en esta tarea.

## Compatibilidad

`agent_adapter=cli-7` diferencia el comportamiento aunque el hash de CLIConfig
no cambie. La comparación existente de versiones congela el adaptador y pone
jobs anteriores, incluidos `cli-6`, en `RECOVERY_REQUIRED` antes del preflight
y los efectos. No se adoptan trabajos pendientes con el comportamiento nuevo.
Las versiones e historias anteriores permanecen legibles e intactas.
Sin cambios de esquema `0013_bootstrap`, codec 7, `local-config-2`, OpenAPI,
UI, dependencias ni flags requeridas del preflight.

## Verificación offline

- `test_codex_workspace_write.py`: 10 pruebas nuevas, repetidas con
  `--basetemp /private/tmp/harness-cli7-roots-20261013`, todas correctas.
  Comprueban raíces canónicas y escapes TOML (comillas, barra inversa, Unicode
  y salto de línea), lectores sin nuevas raíces, rechazo sintético de argv
  `cli-6` y raíces amplias, ambos recorridos con Codex escritor hasta
  `ACCEPTANCE_READY`, texto de transporte/hash y cuarentena sin reescritura.
- La CLI sintética exige raíz del checkout y exclusión de `/tmp` antes de
  editar. Esto comprueba el contrato de transporte, no emula la interpretación
  del modelo ni reproduce una denegación física que D057 no observó.
- Suite completa: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`:
  **921 pruebas y 121 subtests correctos**, 345,54 s. Un aviso de deprecación
  de Starlette/httpx; ninguna dependencia cambiada.
- Checks ligeros `unittest`: **12 correctos**. Cliente gestionado Node:
  **6 correctos**. Diff revisado y `git diff --check` limpio.
- Sin cambios de UI/esquema: no se repitieron build/tsc, regeneración
  OpenAPI/tipos ni QA visual en esta entrega.

No probado: nueva sesión de Codex real, su mensaje interno de permisos, una
escritura real por su sandbox ni Claude real con D058. Requiere consentimiento
nuevo y específico para otro smoke. No hubo proveedores, login, red, push,
instalaciones, ReferenceProject ni modificaciones de áreas de D057.

Siguiente tarea separada: preparar una nueva ejecución de las combinaciones
2–4 con `cli-7`, límites y consentimiento nuevos; no iniciada aquí.
