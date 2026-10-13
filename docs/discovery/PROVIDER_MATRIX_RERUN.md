# Nueva ejecución de la matriz D052 (D057): resultado

Ejecutada el 2026-10-13 (16:43–16:47 UTC) sobre `2c375bc`, con Git limpio en
`main`. [Propuesta](PROVIDER_MATRIX_RERUN_PROPOSAL.md), D057. El usuario pidió
«comienza la preparación» y lanzó con `!` la orden de cada combinación. Siete
invocaciones de proveedor, sin reintentos, relanzamientos ni login.
Consentimiento agotado.

**Resultado:**

- Combinación 1 completa.
- Combinaciones 2 y 3 fallidas por dos defectos distintos.
- Combinación 4 no lanzada, por decisión del usuario: repetiría con casi total
  seguridad el fallo de la 3.

## Preparación (Claude Code, sin agentes)

- `prepare.sh` sobre `BASE=/private/tmp/harness-provider-matrix-2`: cuatro
  checkouts limpios. Los TOML son idénticos a los de la propuesta salvo en `BASE`.
- Wheel con D056 en `BASE/package` (SHA-256 `fec3333e…`, contiene «never argv
  arrays»), `check_distribution.py` correcto y venv `BASE/venv` offline por hashes.
- `check-config --preflight`: `version_help_match` en los ocho agentes (Codex
  0.162.1, Claude 2.1.296), sin flags ausentes.

## Resultados

| # | Combinación | Run | Resultado | Invocaciones |
|---|---|---|---|---:|
| 1 | Codex → Claude | `2f5a8d89-5d39-4a9f-b56e-4a3e7ad30681` | **`COMMITTED`**, commit `79853bf` | 3 |
| 2 | Codex → Codex | `660cf82d-5b15-4593-858a-1e6c2acf174b` | **`REVISION_LIMIT`**: el escritor no editó | 3 |
| 3 | Claude → Claude | `230f36f3-8f41-4e8d-8511-a0fde8431696` | **`STOPPED`** en `planner`: `Invalid task allowed_paths` | 1 |
| 4 | Claude → Codex | — | **No lanzada**: repetiría el planificador de la 3 | 0 |

En todas las lanzadas: jobs `DONE` con propietario cerrado, procesos `STOPPED`,
sin locks, servicio detenido con TERM y apagado limpio, y checkout limpio. Sin
procesos residuales. Todos los intentos terminaron con exit 0 y stderr vacío.

### 1. Codex → Claude: completa

| Rol | Intento | Pared | Uso reportado |
|---|---|---:|---|
| Planificador Codex `gpt-6-luna`/`medium` (`read-only`) | `9a7a9288-…` | 18,4 s | 23 922 in (10 752 en caché) / 550 out / 240 reasoning |
| Ejecutor Claude 2.1.296 `claude-sonnet-4-6`/`low` | `16ebe526-…` | 7,4 s | modelo reportado `claude-sonnet-4-6`; 292 out; `total_cost_usd` 0,0775 |
| Revisor Codex `gpt-6-luna`/`medium` | `a2b71952-…` | 3,6 s | 14 212 in (8 960 en caché) / 40 out |

- **Plan y selección.** El planificador devolvió `validation_commands: []`, una
  lista de cadenas, así que no hizo falta normalizar. Eligió
  `claude-sonnet-4-6`/`low` del catálogo y lo justificó.
- **Validaciones.** El ejecutor solo cambió `src/estimate.ts` (`tasks * 45` →
  `tasks * 30`). Check, test y build dieron exit 0.
- **Revisión, aceptación y commit.** Review ACCEPT sin hallazgos. Aceptación
  elegible con `changed_paths = ["src/estimate.ts"]`. Commit `79853bf`, autor
  `Harness Provider Matrix`. 218 eventos.
- **Primer uso real de Claude 2.1.296** como escritor.

### 2. Codex → Codex: el escritor Codex no editó

- **Planificador** (10,1 s): contrato válido, `validation_commands: []`,
  selección `gpt-6-luna`/`low` del catálogo.
- **Ejecutor Codex** (`workspace-write`, `network_access=false`,
  `approval_policy="never"`, `low`, 4,8 s, 63 tokens de salida y 0 de
  razonamiento). No intentó editar ni ejecutó comandos. Su respuesta completa:

  > «No implementé el cambio: las instrucciones disponibles solo permiten
  > escribir en /private/tmp y en cli-tmp, pero el archivo src/estimate.ts está
  > bajo /private/tmp/harness-provider-matrix-2/codex-codex/web. No edité
  > ningún archivo.»

  El razonamiento es contradictorio, porque el archivo está bajo `/private/tmp`.
  El sandbox no lo bloqueó: no hubo intento de escritura ni stderr.
- **Validaciones.** Check 0, **test 1** (el código seguía en 45) y build 0.
- **Revisor** (6,5 s): REVISE correcto, con un hallazgo de corrección en
  `src/estimate.ts` y una selección válida. Como `max_revision_cycles = 0`, el
  run terminó en `REVISION_LIMIT` sin corrección automática. 95 eventos.
- **Acredita:** argv del escritor Codex, sandbox solicitado, `low` y `medium`
  aceptados por `gpt-6-luna`, y transporte completo.
- **No acredita:** que Codex escriba de verdad en un checkout.
- **Hipótesis para el diagnóstico, sin verificar:** con el checkout bajo
  `/private/tmp`, la lista de raíces escribibles que Codex describe al modelo
  (cwd, `/tmp`, `TMPDIR`) se presenta de forma que el modelo no reconoce el
  checkout como escribible.

### 3. Claude → Claude: listas serializadas como texto

- **Planificador Claude.** Argv `--tools Read,Glob,Grep`, `--allowedTools
  Read,Glob,Grep`, `--restricted` y `--json-schema`. Terminó `complete`: 9,2 s,
  3 turnos, `permission_denials` vacío, modelo reportado `claude-sonnet-4-6` y
  `total_cost_usd` 0,0574.
- **Herramientas.** Usó `Read` sobre `src/estimate.ts` y la herramienta
  `StructuredOutput`. Ninguna entrada nueva en `~/.claude/projects`.
- **Salida.** `structured_output` estaba presente, pero **listas y objetos
  llegaron como cadenas JSON**: `"allowed_paths": "[\"src/estimate.ts\"]"`, y lo
  mismo en `forbidden_paths`, `acceptance_criteria`, `validation_commands` y
  `executor_selection`. El contenido era correcto. El motor paró con `Invalid
  task allowed_paths`. 273 eventos.
- **Causa.** `cli-5` pasa a Claude lector un `--json-schema` mínimo:
  `{"type":"object","required":[…]}`, sin tipos de propiedades. Sin tipos, la
  CLI trata cada campo como texto. D056 tipó el esquema que va dentro del
  prompt, pero no el del argv, para no cambiar `cli-5`.
- **Acredita:** el transporte del lector Claude con herramientas de solo
  lectura, `--restricted` y salida estructurada.
- **No acredita:** contratos válidos de un lector Claude.

### 4. Claude → Codex: no lanzada

Su planificador es el mismo lector Claude con el mismo `--json-schema`, y su
escritor es Codex con la misma configuración que falló en la 2. El usuario
decidió no lanzarla. El área sigue preparada con estado vacío y no se
reutiliza.

## Observaciones

- **Prosa en las rutas prohibidas.** El planificador Codex escribió
  `forbidden_paths` como `"**/* (except src/estimate.ts)"`, que no es un glob
  útil. No tuvo efecto, porque la aceptación compara las rutas cambiadas con
  las permitidas y las protegidas del perfil. Conviene endurecerlo aparte.
- **Carpeta de Claude.** La CLI de Claude, como escritora, volvió a crear
  `~/.claude/projects/-private-tmp-harness-provider-matrix-2-codex-claude-web`
  (como en D050). No se toca.
- **Repositorio, fixture y configuración global** sin cambios.

## Evidencia

| Combinación | Rol | stdout bytes | stdout SHA-256 (16) | prompt SHA-256 (16) |
|---|---|---:|---|---|
| 1 | planificador | 2 160 | `52d89856d59ce5d2` | `360021185e350c55` |
| 1 | ejecutor | 31 507 | `9dd55afc5d0ce3d1` | `837c5183eef6aacd` |
| 1 | revisor | 504 | `afe775c9fbaf386b` | `c14411da5e71d171` |
| 2 | planificador | 1 631 | `4b668e4f6c7b1ac0` | `f4084c92b2dbae4f` |
| 2 | ejecutor | 594 | `92b96cf0925ec4dd` | `704daa4004730125` |
| 2 | revisor | 1 579 | `c14c7ab831386aee` | `d27e1e9486b825a8` |
| 3 | planificador | 51 964 | `0a5c52249555aaeb` | `360021185e350c55` |

Instantáneas de la API en `BASE/<par>/evidence/`. SQLite y artefactos en
`BASE/<par>/state/`.

## Qué acredita la matriz hasta ahora

| Punto de D052 | Estado |
|---|---|
| Composición `cli-5`/`local-config-2` real, preflight y reparto por agente | ✓ |
| Planificación por el revisor y elección del ejecutor dentro del catálogo | ✓ con Codex; con Claude, el contrato es inválido |
| Codex lector (`read-only`) | ✓ |
| Codex escritor (`workspace-write` sin red) | argv y sandbox ✓; **sin edición real** |
| Claude lector con `--json-schema`, `--tools Read,Glob,Grep` y `--restricted` | transporte ✓; **contrato inválido** |
| Claude 2.1.296 escritor | ✓ |
| Esfuerzos Codex `medium` y `low` con `gpt-6-luna` | ✓ aceptados (los demás siguen inferidos) |
| Ciclo completo con commit | ✓ solo en Codex → Claude |
