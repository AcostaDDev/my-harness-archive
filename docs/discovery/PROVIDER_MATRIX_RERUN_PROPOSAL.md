# Propuesta de nueva ejecución de la matriz D052 (D057)

Preparada el 2026-10-13 sobre `7d00240` (D056), con Git limpio salvo los dos
scripts nuevos de esta propuesta. **Ejecutada y cerrada el mismo día; ver [resultado](PROVIDER_MATRIX_RERUN.md).**
Cuando se preparó, no estaba ejecutada ni autorizada. Ejecutarla
exigía un consentimiento específico y explícito del usuario. D055 y los
consentimientos anteriores están agotados y no se trasladan.

Repite la [propuesta D055](PROVIDER_MATRIX_PROPOSAL.md) después de la
corrección D056 ([entrega](CONTRACT_SHAPES.md)). La primera ejecución
([resultado](PROVIDER_MATRIX_RUN.md)) se detuvo en el planificador de la
combinación 1.

## Qué se conserva de D055

Siguen vigentes sin cambios:

- **Selecciones del usuario:** las cuatro combinaciones en el orden 1 → 4.
- **Recorrido:** el revisor planifica, el ejecutor edita y el revisor revisa;
  después, commit sin proveedor.
- **Modelos:** Codex `gpt-6-luna` y Claude `claude-sonnet-4-6`. Revisor
  `medium`; catálogo del ejecutor `low`.
- **Fallos:** un fallo detiene solo su combinación.
- **Ajustes:** modo catálogo, `max_revision_cycles = 0`, Claude 2.1.296
  versionado y timeouts de 600 y 900 s. También se mantienen las variantes
  autorizadas de 1800 s.
- **Preparación:** `examples/provider_matrix/prepare.sh` sin cambios (SHA-256
  `94db751b…`). Sus TOML solo difieren de D055 en `BASE`.
- **Validación:** lo que confirma cada combinación y los límites (3
  invocaciones por combinación, 12 en total, 30 min por combinación y 2 h la
  matriz).
- **Criterios:** los de éxito, los de fallo y parada, y lo que no se certifica.

## Qué cambia

- **Área nueva:** `BASE=/private/tmp/harness-provider-matrix-2`. El área de
  D055 conserva su evidencia y no se reutiliza.
- **Paquete con D056.** Se construye en `BASE/package` desde el HEAD de la
  ejecución y se registra su SHA-256.
  - Esquema tipado.
  - `plan-task` pide cadenas.
  - El argv se normaliza.
- **Scripts versionados** en lugar del script ad hoc de D055:
  - [`run_pairing.sh`](../../examples/provider_matrix/run_pairing.sh) (SHA-256
    `b38bed4b…`), para una combinación: preflight comprobado
    (`version_help_match` y sin flags ausentes en ambos agentes), `init-db`,
    `serve` en segundo plano, recorrido y TERM. Sale con 3/4/5 si falla antes
    del recorrido.
  - [`drive.py`](../../examples/provider_matrix/drive.py) (SHA-256
    `c85f73fc…`): sesión, fase `P001`, run y, solo con `ACCEPTANCE_READY`,
    commit.
    - Espera hasta `finished_at` o `RECOVERY_REQUIRED`, porque `ACTIVE` no es
      terminal (fallo de D055).
    - Límite propio de 28 min por combinación.
    - Instantánea por API completa en `BASE/<par>/evidence`: proyecto, fase,
      run, intentos y eventos paginados, jobs, logs, supervisor y
      `outcome.json`.
    - Sale con 0 solo si el run queda `COMMITTED`.
- **Reparto de la ejecución.** El clasificador de permisos de Claude Code
  bloquea las órdenes que lanzan agentes, así que se reparte así:
  - **Claude Code:** preparación, wheel y verificación, venv, `check-config
    --preflight` de las cuatro, revisión de la evidencia entre combinaciones y
    decisión según los criterios de parada.
  - **Usuario, con `!`:** una orden por combinación, solo cuando Claude Code
    indique que procede:

    ```
    ! cd $HOME/Documents/projects/my_harness && nohup sh examples/provider_matrix/run_pairing.sh /private/tmp/harness-provider-matrix-2 <par> > /private/tmp/harness-provider-matrix-2/<par>/orchestration.log 2>&1 &
    ```

    `<par>` va, en orden, `codex-claude`, `codex-codex`, `claude-claude` y
    `claude-codex`.
- **Confirmación adicional en cada combinación:** qué forma devuelve el
  planificador real para `validation_commands` (cadenas, o argv normalizado
  con su original conservado en el intento) y que el contrato congelado use
  cadenas.

## Ensayo offline realizado

Hecho en el scratchpad, sin proveedores:

1. **Preparación y paquete.** `prepare.sh` completo en un área nueva. Wheel
   con D056 construido y verificado (`check_distribution.py`); su
   `plan-task.md` contiene «never argv arrays». Venv nuevo offline por hashes.
2. **CLI sintética.** En los cuatro TOML del ensayo se sustituyeron los
   ejecutables por la CLI sintética de las pruebas
   (`tests/product/cli_process_probe.py`). Versión de cada proveedor, selección
   del catálogo y un planificador que devuelve
   `validation_commands = [["npm","run","test"]]`, la forma observada en D055.
   El preflight dio `version_help_match` en los ocho agentes.
3. **Las cuatro combinaciones con `run_pairing.sh`**, servicio real del wheel en
   127.0.0.1:8013:

   | Combinación | Run | Intentos | Commit |
   |---|---|---|---|
   | `codex-claude` | `COMMITTED` | planner, executor y reviewer `COMPLETE` | `2849feae`, solo `src/estimate.ts` |
   | `codex-codex` | `COMMITTED` | planner, executor y reviewer `COMPLETE` | `b7216f1b` |
   | `claude-claude` | `COMMITTED` | planner, executor y reviewer `COMPLETE` | `debe8da4` |
   | `claude-codex` | `COMMITTED` | planner, executor y reviewer `COMPLETE` | `43fdb9ef` |

   Selección del ejecutor igual al catálogo y del revisor en `medium`. Contrato
   congelado `["npm run test"]`. Validaciones: `npm run test` de 1800 s más
   check, test y build de 120 s, todas con exit 0. Argv por proceso: lector
   Codex `read-only`; escritor Codex `workspace-write` con
   `network_access=false`; lector Claude con `--restricted` y `--json-schema`.
   Autor `Harness Provider Matrix`, entre 105 y 106 eventos, servicio detenido
   con TERM.
4. **Rama de fallo.** Con un planificador que devuelve `[[]]`, el run quedó
   `STOPPED` en `planner` con `Invalid task validation_commands`. Hubo un solo
   intento y ningún commit; la instantánea y `outcome.json` se guardaron, el
   script salió con 1 y el servicio se detuvo.

Las áreas del ensayo quedan en el scratchpad. La ejecución real prepara la suya.

## Ejecución propuesta (solo con consentimiento específico)

1. **Claude Code:**
   - `prepare.sh /private/tmp/harness-provider-matrix-2`; si la ruta existe, se
     elige otra nueva y se registra.
   - `build_distribution.py --out-dir BASE/package` y `check_distribution.py`.
   - Venv `BASE/venv` offline por hashes.
   - `check-config --preflight` de las cuatro: `version_help_match` en los
     ocho agentes.
2. **Para cada combinación en orden:**
   - El usuario lanza la orden con `!`.
   - Claude Code sigue `orchestration.log` hasta `ORCHESTRATION-END` y revisa
     `outcome.json`, la SQLite (solo lectura) y los artefactos.
   - Según los criterios de D055: la siguiente combinación procede, se omite
     (fallo de autenticación, cuota o preflight de un proveedor que usa) o se
     para la matriz.
3. **Registro** en `docs/discovery/PROVIDER_MATRIX_RERUN.md` y en D057. Los
   ids, hashes, uso y modelos reportados se separan de los solicitados.

No hay reintentos, relanzamientos, login ni acciones fuera del recorrido. Los
casos ambiguos (por ejemplo, un fallo nuevo que probablemente se repita en las
combinaciones pendientes) se consultan al usuario antes de seguir, como en D055.
