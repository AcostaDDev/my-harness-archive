# Propuesta de matriz D052, combinaciones 2–4 con `cli-7` (D060)

Preparada y ensayada offline el 2026-10-13 sobre `5db4da2` (D059), con Git
inicialmente limpio en `main`. **No ejecutada con proveedores ni autorizada.**
La tarea de esta entrega termina con la preparación; ejecutar es una tarea
separada y exige consentimiento específico nuevo. D050, D055 y D057 están
agotados. [Manifiesto de preparación y evidencia sintética](PROVIDER_MATRIX_CLI7_PREPARATION.json).

## Alcance y selecciones propuestas

Se conservan las selecciones y el recorrido de
[D055](PROVIDER_MATRIX_PROPOSAL.md) / [D057](PROVIDER_MATRIX_RERUN_PROPOSAL.md),
reduciendo la ejecución a las combinaciones pendientes de comprobación. La 1
(Codex→Claude) ya llegó a `COMMITTED` en D057 y no se repite.

| # | Par y área bajo BASE | Revisor y planificador | Ejecutor del catálogo | Máximo de invocaciones |
|---|---|---|---|---:|
| 2 | `codex-codex` | Codex 0.162.1 `gpt-6-luna` / `medium` | Codex 0.162.1 `gpt-6-luna` / `low` | 3 |
| 3 | `claude-claude` | Claude 2.1.296 `claude-sonnet-4-6` / `medium` | Claude 2.1.296 `claude-sonnet-4-6` / `low` | 3 |
| 4 | `claude-codex` | Claude 2.1.296 `claude-sonnet-4-6` / `medium` | Codex 0.162.1 `gpt-6-luna` / `low` | 3 |

Cada combinación crea una fase `P001`, planifica `P001-T001`, edita, valida y
revisa; solo con `ACCEPTANCE_READY` confirma el commit H2.4 por versión exacta.
Sin check ni cierre de fase, tag, lote, chat o bootstrap. La tarea restaura
`tasks * 30` desde la regresión `tasks * 45` de la fixture TypeScript web.
Única ruta permitida: `src/estimate.ts`. Tests, scripts, configuración, lock y
documentos de fase permanecen intactos. Entradas inválidas conservan su
`RangeError`; las validaciones del perfil acreditan los resultados 90 y 0.

`planning_mode = "agent"`, `executor_mode = "catalog"`, un modelo y esfuerzo
por catálogo, `max_revision_cycles = 0`. No correcciones automáticas. Una
invocación nueva por rol; ningún resume de conversación.

## Cambios respecto a D057

- **Área nueva preparada:** `BASE=/private/tmp/harness-provider-matrix-3`.
  Las áreas `/private/tmp/harness-provider-matrix` y
  `/private/tmp/harness-provider-matrix-2` se conservan. Ningún run antiguo se
  reanuda ni adopta con versiones nuevas.
- **Wheel actual, adaptador `cli-7`.** Incluye D056, el
  [esquema tipado de Claude lector](TYPED_JSON_SCHEMA.md) (D058) y las
  [raíces explícitas de Codex escritor](CODEX_WRITER_ROOTS.md) (D059).
- Claude lector recibe en `--json-schema` el esquema del motor congelado en
  el prompt del intento, con tipos de propiedades/elementos y
  `additionalProperties: true`. No se convierten cadenas JSON en listas ni
  objetos.
- Codex escritor solicita `writable_roots=["<checkout canónico>"]` y
  `exclude_slash_tmp=true`, junto a `workspace-write` y red desactivada. La
  entrada de transporte aclara que los descendientes del checkout están
  incluidos en el acceso solicitado; el contrato y las denegaciones reales
  siguen delimitando los efectos. El TMPDIR explícito permanece como raíz
  temporal predeterminada de la CLI.
- `prepare.sh BASE [PAR ...]` permite preparar solo 2–4. Sin pares conserva
  las cuatro combinaciones originales. Un par desconocido se rechaza antes
  de crear el área. No cambian los TOML generados, salvo las rutas de BASE.
- Máximo **nueve invocaciones**: cinco Codex y cuatro Claude si se completa
  todo. Se propone un límite operativo total de 90 minutos (tres
  combinaciones de 30 minutos), en lugar de las dos horas de la matriz completa.

## Herramientas, entorno y límites

Sin cambios respecto a D055 salvo BASE y transporte D058/D059:

- Codex: `$HOME/.nvm/versions/node/v24.15.0/bin/codex`, versión
  exigida 0.162.1. Lectores `read-only`; escritor `workspace-write`,
  `sandbox_workspace_write.network_access=false`, `approval_policy="never"`,
  búsqueda desactivada, configuración/reglas de usuario omitidas y sesión
  efímera. No se conceden herramientas adicionales de Codex; sus comandos
  nativos, si se observan, se registran.
- Claude: `$HOME/.local/share/claude/versions/2.1.296`, versión
  exigida 2.1.296, `DISABLE_AUTOUPDATER=1`. Lector con
  `Read,Glob,Grep`, `--restricted` y esquema tipado; escritor con
  `Read,Edit,Write,Glob,Grep`, sin Bash. `dontAsk`, prompts desactivados,
  MCP explícito vacío, settings/fuentes/hooks aislados y sesión nueva.
- Entorno CLI explícito: `HOME=$HOME`, `USER=acosta` validado contra
  UID, `LANG=C.UTF-8`, `TMPDIR=BASE/<par>/cli-tmp`. PATH Codex incluye el
  Node fijado más `/usr/bin:/bin`; PATH Claude es `/usr/bin:/bin`. Sin
  credenciales ni variables adicionales heredadas.
- Node 24.15.0 y npm 11.12.1 por ruta absoluta. Comandos con HOME/TMPDIR
  propios (`command-home`), npmrc vacíos, caché copiada por combinación,
  `CI=true` y actualización desactivada. `npm ci --offline` prepara; check,
  test y build del perfil validan con captura `commands-1` (64 KiB por stream)
  y JUnit. Las únicas variantes adicionales autorizadas son
  `npm run check|test|build` con timeout exacto de 1800 s.
- Timeout de cada invocación: revisor/planificador 600 s y ejecutor 900 s.
  Comandos del perfil: 30/120 s. El driver observa un plazo de 28 minutos
  desde su inicio y después pide parada del servicio con TERM. Los 30/90
  minutos son límites operativos supervisados por el operador: no hay un
  watchdog global que garantice matar un proceso al segundo exacto.
- Suscripciones y autenticación existentes de cada CLI. No login, refresh,
  API keys ni cambio a API de pago. Retries internos de proveedores
  desconocidos; nueve invocaciones CLI no garantizan nueve solicitudes ni
  ausencia de consumo ante un fallo.

No se autorizan `retry_executor`, `revalidate`, nuevos runs, concesiones,
modo libre, otro modelo/esfuerzo/CLI, relanzamientos, publicación o push.
Cambiar selecciones, herramientas, límites o entorno exige revisar la
propuesta antes de consentir. Si BASE se pierde o queda ocupado por una
ejecución, se elige otra área nueva y se registran sus hashes; no se reutiliza
una SQLite de ensayo.

## Paquete instalado y configuración preparada

El paquete se construyó offline con `build_distribution.py`, se verificó con
`check_distribution.py --dist BASE/package` y se instaló en `BASE/venv`:
venv nuevo, 18 dependencias de producción por pins/hashes y wheel `--no-deps`,
sin instalación con red. Recursos contrastados contra este checkout. Se
ejecuta desde BASE y el paquete instalado, conforme a D051.

Wheel: `BASE/package/harness_local-0.1.0-py3-none-any.whl`.
SHA-256: `79ac961dfc90f82c4b0a1437df222d93b33f1fb343e6e3f22e4437862dabe9e0`.
El manifiesto registra también sdist, requirements y scripts. No se
reconstruye silenciosamente el paquete antes de ejecutar esta propuesta.

Los TOML 0600 están en `BASE/<par>/operator/harness-local.toml`. Los tres
`check-config` del binario instalado, **sin `--preflight`**, son válidos y
congelan `cli-7`, `local-config-2`, `commands-1` y el reparto de la tabla.
Hashes de composición (`local_config_sha256`):

| Par | SHA-256 |
|---|---|
| `codex-codex` | `f276340e96fe49f3946ee91dabbc40299f903fc50b46992f752e45986d7daa7e` |
| `claude-claude` | `9575bfc42e77092b8493d840e9037994f635b62fd5ce22aadfc38eabf87c0192` |
| `claude-codex` | `c6f0a748e4962fec02da1f12d932b5028c925f23c8504f619a9f3129a7acc673` |

El manifiesto añade hashes de archivos TOML y de los adaptadores. Checkouts
limpios con dos commits (base y regresión), estado y cli-tmp vacíos: no hay
SQLite, jobs, intentos, servicio ni consumo en esta área. **No se invocaron
las CLI reales, ni siquiera version/help.** El preflight real queda para la
tarea de ejecución y debe pasar antes de cualquier intento.

## Ensayo offline realizado

Área independiente: `/private/tmp/harness-provider-matrix-cli7-offline-20261013`.
Se prepararon las mismas tres combinaciones, sustituyendo únicamente en ese
ensayo los ejecutables por una copia de `tests/product/cli_process_probe.py`
y el entorno por HOME sintético/variables de la sonda. El intérprete y el
servicio usan el wheel instalado en BASE; no importan el producto desde el
checkout. npm, TypeScript, Git y SQLite son reales y locales.

Se usaron `run_pairing.sh` y `drive.py` sin cambios, por HTTP en 127.0.0.1:8013.
La sonda verifica raíz canónica/exclusión de `/tmp` antes de editar con Codex
y propiedades tipadas antes de responder como lector Claude. El planificador
devuelve argv `[["npm","run","test"]]` para comprobar también D056.

| Par | Resultado sintético | Intentos | Commit acotado | Eventos |
|---|---|---|---|---:|
| `codex-codex` | `COMMITTED` | tres `COMPLETE` | `afbc4b69` | 105 |
| `claude-claude` | `COMMITTED` | tres `COMPLETE` | `e969b748` | 106 |
| `claude-codex` | `COMMITTED` | tres `COMPLETE` | `b4e7edc1` | 105 |

En las tres: contrato congelado `["npm run test"]`, selección del catálogo,
test adicional de 1800 s y check/test/build de 120 s con exit 0, JUnit
`complete`, review ACCEPT y aceptación ligada a la misma huella. Un solo
commit nuevo, únicamente `src/estimate.ts`, documentos intactos y Git limpio.
SQLite reabierta en lectura: integridad/FK correctas, jobs DONE, propietarios
cerrados, procesos STOPPED y cero locks. Prompts/specs con hashes y `cli-7`
verificados; se guardaron instantáneas API, historial SQLite y specs.

Rama inválida en otra área:
`/private/tmp/harness-provider-matrix-cli7-invalid-20261013/codex-codex`.
Con `validation_commands=[[]]`: `STOPPED` en planner, un solo intento,
`Invalid task validation_commands`, sin ejecutor/revisor/commit y salida 1
del script. Evidencia conservada y servicio detenido.

Todos los servicios se cerraron con TERM, log `Application shutdown complete`,
clave retirada y puerto disponible. Uvicorn devuelve 143 al propagar TERM;
no se interpreta como fallo de tarea. El verificador local se ajustó para
admitir ese cierre y sockets en TIME_WAIT, sin relanzar combinaciones ya
terminadas. Bind requirió permiso fuera del sandbox. La sonda y el script de
verificación retenido `/private/tmp/h60_rehearsal.py` no ejecutan proveedores.

Checks adicionales: **82 pytest** (agentes, configuración local, D058, D059),
**12 checks ligeros**, sintaxis shell y rechazo de par desconocido sin crear
BASE. Build TypeScript/Vite correcto dentro del empaquetado. La verificación
de distribución cubre sesión, assets/API, bootstrap/tarea/commit/reinicio y
restauración de consulta con agentes falsos. Sin nueva QA visual ni suite
pytest completa: no cambia código de producto, UI, esquema, codec o locks.
Capturas del escritor D057 conservan sus hashes documentados.

**Estas pruebas no acreditan escritura de Codex real ni listas/objetos de
Claude real con D058.** Tampoco prueban su mensaje interno de permisos,
aislamiento físico, ausencia de red, cuota, factura, esfuerzo efectivo,
retries internos o modelo efectivo de Codex.

## Órdenes revisables para la tarea separada de ejecución

Solo después de consentimiento explícito para **D060 una vez**, con un
máximo de nueve invocaciones, en orden 2 → 3 → 4. Antes de cada orden:
comprobar los hashes del manifiesto, que el estado de ese par siga vacío y que
:8013 esté libre. No detener otro servicio para ocuparlo.

```sh
sh examples/provider_matrix/run_pairing.sh /private/tmp/harness-provider-matrix-3 codex-codex > /private/tmp/harness-provider-matrix-3/codex-codex/orchestration.log 2>&1
```

Revisar su evidencia y los criterios de parada antes de la siguiente:

```sh
sh examples/provider_matrix/run_pairing.sh /private/tmp/harness-provider-matrix-3 claude-claude > /private/tmp/harness-provider-matrix-3/claude-claude/orchestration.log 2>&1
```

Después de revisar la 3, si procede:

```sh
sh examples/provider_matrix/run_pairing.sh /private/tmp/harness-provider-matrix-3 claude-codex > /private/tmp/harness-provider-matrix-3/claude-codex/orchestration.log 2>&1
```

Órdenes desde la raíz del repositorio; el script pasa a BASE antes de operar.
El usuario puede lanzarlas manualmente (con `!` en Claude Code, como en D057).
No lanzar las tres en paralelo ni automáticamente sin revisar entre ellas.
Cada orden comprueba preflight `version_help_match` de ambos agentes, sin
flags ausentes y con las versiones fijadas; después crea una SQLite nueva,
arranca `serve`, obtiene sesión y conduce el recorrido. No reconstruir,
cambiar TOML ni sustituir una versión ante un fallo de preflight.

## Criterios de la futura ejecución y parada

Éxito por combinación exige tres intentos completos/exit 0 en el orden
planner→executor→reviewer, proveedores y selecciones de la tabla; contrato
con listas/objetos válidos, validaciones y JUnit correctos, ACCEPT y aceptación
elegible por contenido exacto; un commit nuevo del autor
`Harness Provider Matrix`, solo `src/estimate.ts` con `tasks * 30`. Jobs DONE,
propietarios cerrados, procesos detenidos, cero locks y documentos intactos.

En 2/4, registrar las herramientas/eventos de edición efectivos de Codex,
árbol antes/después, argv con raíces D059 y hash del prompt de transporte;
una mera afirmación de éxito sin cambios no satisface el criterio. En 3/4,
comparar `--json-schema` con el esquema congelado y comprobar listas como
listas y `executor_selection` como objeto en el original de Claude planner;
review con `findings` tipado si está presente. Lectores sin cambios Git y
sin denegaciones que impidan leer. Originales y contratos conservados.

Cualquier fallo, salida inválida, REVISE, bloqueo, denegación, timeout,
aceptación inelegible o commit incierto termina su combinación sin retry ni
fallback. TERM y conservar SQLite/artefactos/checkout/locks; no confirmar
recuperación ni liberar exclusión. Las restantes continúan, salvo fallos de
auth/cuota/preflight: se omiten los pares pendientes que usen ese proveedor.
Un fallo nuevo probablemente común se consulta antes de seguir.

Parada total ante efectos fuera de BASE (incluida configuración global),
servicio que no se deja detener o límite operativo total de 90 minutos.
No ampliar sandbox, red, permisos, modelos o versiones para superar el fallo.
Registrar completas, fallidas con etapa o no lanzadas con motivo; hashes, ids,
duraciones y datos reportados separados de los solicitados. El diagnóstico
posterior y H6.2 quedan fuera de esta propuesta.
