# Primer uso real D050 — ejecución autorizada

Ejecutado el 2026-10-13 (14:42–14:50 UTC) sobre `0e39364`, Git limpio en
`main`. [Propuesta](FIRST_USE_PROPOSAL.md), D050/D051. El usuario escribió
«Autorizo ejecutar la propuesta D050 una vez». Una sola ejecución. Recorrido
completo tarea → commit → check → cierre, con **tres** invocaciones de
proveedor, todas `complete`. Sin reintentos, relanzamientos ni login.

## Desviación en el paso 3 y decisión

`harness-local serve` desde la instalación editable de desarrollo terminó con
exit 1 antes de servir: «Assets web ausentes; instalar el paquete construido
con scripts/build_distribution.py». La UI solo existe en el wheel (D043). El
wheel de `dist/` era anterior a D049 (sin `local_config.py`). Fue un fallo
previo al consumo: ningún proceso de proveedor, ningún job y checkout intacto.

Se consultó al usuario, que pidió la opción más mantenible, modular y
reutilizable, sin prisas. Se usó la vía de distribución documentada, sin
cambios (D051):

1. `build_distribution.py --out-dir BASE/package`. Construye el wheel/sdist
   actual con la UI, offline; `dist/` no se toca.
2. `check_distribution.py --dist BASE/package`: wheel aislado correcto (UI,
   API, sesión, bootstrap/tarea/commit/reinicio y evidencia restaurada; fakes).
3. Venv nuevo `BASE/venv`, instalación offline con `--require-hashes` y wheel
   `--no-deps`. `check-config` desde el venv instalado: versiones congeladas
   idénticas a las del preflight.
4. `BASE/venv/bin/harness-local serve --config` con cwd en el área, sin
   `PYTHONPATH` ni `HARNESS_MANAGED_CONFIG`.

El resto de pasos, el TOML (sin cambios desde la preparación), los límites y los
criterios se siguieron tal como estaban escritos. La SQLite se creó con
`init-db` del entorno de desarrollo antes del fallo; el esquema es el mismo y el
servicio instalado lo aceptó.

## Configuración congelada

Área `/private/tmp/harness-first-use`. TOML idéntico al de la propuesta (diff
comprobado), SHA-256 `f803557225cad8f046987b11360fd67667b638db8559c835081dea538930afdd`.
Preflight `version_help_match` en ambas CLI: `codex-cli 0.162.1` (help
`df0d864c…`) y `2.1.295 (Claude Code)` (help `550db4f8…`), sin flags ausentes.

| Versión congelada | Valor |
|---|---|
| `engine` / `local_config` / `profile` | `harness-local-0.1.0` / `local-config-1` / `typescript-web` |
| `local_config_sha256` | `69a9ff6c54ce6a11cadaecb8e80aa556ed770e16870f64e92acf41f9f6386bd5` |
| `agent_adapter`, CLI | `cli-4`, Codex 0.162.1, Claude 2.1.295 |
| `cli_config_sha256` | `0330e073fbadf22e7cb646a8c2395b88d5dbf62527c1ea30674b45eef7ede512` |
| `commands`, `command_config_sha256` | `commands-1`, `7641276af3e5b4be7504bd75fec963c7962d8925ba06a4441e508a4fadbe00c7` |

## Recorrido y resultados

| Paso | Resultado |
|---|---|
| Fase P001 | `ACTIVE`, id `6bd40ca4-b30c-4081-a108-a2613910f313` |
| Run P001-T001 | `abcc508f-3f6c-4354-a5b8-9a5744648ff1`, job 1 → `ACCEPTANCE_READY` |
| Commit (job 2) | `COMMITTED`, `8999af8` sobre `6b02d9d`, autor `Harness First Use`, solo `src/estimate.ts` |
| Check (job 3, run `3b27500d-…`) | `READY_TO_CLOSE`, binding `ed4124966451dc2c…29689225` |
| Cierre (job 4) | `CLOSED`, tag ligero `first-use-p001` → `8999af8` (HEAD READY) |

Diff aceptado: `return tasks * 45;` → `return tasks * 30;`. Review ACCEPT sin
hallazgos, preguntas ni concesiones. Aceptación elegible con
`changed_paths = ["src/estimate.ts"]`. La evaluación de fase marcó los tres
criterios como superados, con evidencia citada (commit en HEAD, tres
validaciones con exit 0 y 3/0 tests, documentos sin cambios).

| Rol | Intento | Solicitado | Reportado | Pared | Uso reportado |
|---|---|---|---|---:|---|
| Ejecutor | `5f75a3d3-dd87-4657-94c6-04994834ed98` | `claude-sonnet-4-6`/`low` | `claude-sonnet-4-6`; 3 turnos; Read + Edit | 8,1 s | 5 in / 270 out / 21 thinking; caché 11 018 creación y 21 410 lectura; `total_cost_usd` 0,0766 (`costBasis: list`) |
| Revisor | `3f551d11-c146-49aa-ba88-c21457419933` | `gpt-6-luna`/`medium` | sin modelo reportado | 9,2 s | 14 131 in (8 960 en caché) / 90 out / 48 reasoning |
| Fase | `d5fa6390-969c-4435-b7d5-3c5fb0d15225` | `gpt-6-luna`/`medium` | sin modelo reportado | 13,7 s | 27 710 in (22 016 en caché) / 673 out / 271 reasoning |

Exit 0, terminal observado, stderr vacío y grupo `dead` en los tres. Ejecutor
sin `permission_denials`. Codex no reporta el modelo: el «solicitado» no se
confunde con el «observado». El coste es el que informa la CLI con base de
lista; no certifica facturación ni cuota de la suscripción.

| Evidencia | Bytes | SHA-256 |
|---|---:|---|
| stdout ejecutor | 30 321 | `95c2c910d317e97a53f84e813249ea3e2f22acc1f90836c688c4f7ef246b4424` |
| stdout revisor | 505 | `2e7ea6df56c8aa780d75e57bdb63df498b0f5c7fe35bc6d5b6bdf070e1956c7e` |
| stdout fase | 4 054 | `4fab4aa5988b0ebb2ab388b45f8deeeb25865ebba4199e0685217d684b2277bd` |
| prompt ejecutor | — | `4205b80c63ba7e001c99802ac2589e4e8f90c71ccfe36a3e8a5b505ba534fb63` |
| prompt revisor | — | `653f0c5f62408376ca502999b7764a387e2c1a24881b26707c1e53485cf27774` |
| prompt fase | — | `8682cc3754c33ed4b98fd9acaa2ebe2fe4a1fb59bf75f03871ff6e7fdcaff84e` |

Comandos `commands-1`, todos con la configuración congelada, exit 0, sin
timeout ni error. Tarea: `node --version`, `npm --version`, `npm ci --offline`,
`check`, `test` (JUnit `complete`) y `build`. Check de fase: `check`, `test` y
`build`. 258 eventos en total; cuatro jobs `DONE` con propietario cerrado,
procesos de agente `STOPPED` y sin locks retenidos.

## Comprobaciones posteriores

- Servicio detenido con TERM: «Application shutdown complete». La clave de
  sesión y su directorio se retiraron. El envoltorio en segundo plano informó
  exit 144 tras la señal.
- SQLite reabierta desde el paquete instalado: run `COMMITTED`, versión 200,
  dos intentos. `history` y `versions` idénticos a la instantánea de la API
  tomada antes de detener el servicio.
- Checkout `BASE/web` limpio, tres commits y tag. Repositorio `my_harness` y
  fixture sin cambios; `dist/` intacto.
- Claude no persistió la sesión, pero creó un directorio vacío
  `~/.claude/projects/-private-tmp-harness-first-use-web/memory`. Se deja sin
  tocar (configuración global del usuario) y se registra como efecto observado
  de la CLI.
- El enlace `~/.local/bin/claude` sigue en 2.1.296. El binario 2.1.295 se usó
  por ruta explícita.

## Qué acredita y qué no

Acredita, para esta composición y este checkout, el primer recorrido completo
del motor con proveedores reales: contrato determinista, ejecutor con
herramientas limitadas, validaciones nativas con JUnit, review ACCEPT ligada al
contenido, commit H2.4, check READY ligado por hash, autorización de cierre y
tag por CAS, con historial reproducible tras reabrir SQLite.

No acredita: facturación/cuota, esfuerzo efectivo, retries internos de las CLI,
el modelo efectivo de Codex, aislamiento físico, ramas REVISE/BLOCKED/recuperación
con proveedores, otros modelos, perfiles o proyectos, la UI con navegador (se
usó HTTP), integración de ramas, push ni publicación. El consentimiento D050 se
ha agotado con esta ejecución.
