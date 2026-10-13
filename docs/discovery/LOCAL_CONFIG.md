# Composición de uso real por configuración local TOML

Incremento elegido por el usuario el 2026-10-13 tras D048. [Alcance previo y
criterios](LOCAL_CONFIG_SCOPE.md). D049. Formato `local-config-1`, perfil
`typescript-web`. Verificado offline; no se ha ejecutado ningún proveedor.

## Uso

1. Copiar [la plantilla](../../examples/local_config.example.toml) **fuera** de
   cualquier checkout, rellenar rutas absolutas canónicas y `chmod 600`.
2. `harness-local check-config /ruta/harness-local.toml` valida y muestra ids,
   raíces, política y versiones congeladas, sin valores de entorno ni procesos.
   `--preflight` añade solo version/help de ambas CLI (D042): no autentica, no
   consume ni certifica cuota, modelos o permisos.
3. `harness-local init-db --database /ruta/harness.sqlite3` (base nueva) y
   `harness-local serve --database /ruta/harness.sqlite3 --config /ruta/harness-local.toml`.
   `--config` es incompatible con `HARNESS_MANAGED_CONFIG`. En desarrollo:
   `HARNESS_MANAGED_CONFIG=harness_local.services.local_config:from_environment`
   con `HARNESS_LOCAL_CONFIG=/ruta/harness-local.toml`.

Con `supervisor = false` los jobs quedan en cola; con `true`, el servicio los
ejecuta, y eso **sí** invoca las CLI configuradas y consume la suscripción. El
primer uso debe ser sobre un checkout desechable, con modelos y esfuerzos
elegidos por el usuario y la propuesta/autorización de D033.8.

## Archivo y esquema

Autoridad local del operador: archivo regular sin enlaces, `st_nlink == 1`,
propietario el UID del servicio, sin escritura de grupo/otros, ≤ 64 KiB, UTF-8,
ruta absoluta canónica y fuera de todos los checkouts. Se analiza con `tomllib`;
claves desconocidas o ausentes, tipos erróneos, números no finitos y valores no
textuales en entornos se rechazan con la ruta de la clave. Cargarlo no lanza
procesos, no crea directorios ni lee los repositorios gestionados. No debe
contener secretos: la autenticación sigue en cada CLI. `.harness/project.yaml`
(configuración portable del repositorio) queda para otra tarea.

- `[service]`: `state_dir` (artefactos CLI en `artifacts/<id>` y migraciones),
  `supervisor` explícito, `lease_seconds`/`poll_seconds` opcionales.
- `[git]`: ejecutable absoluto e identidad de commit explícita.
- `[providers.codex]`, `[providers.claude]`: argv con ejecutable absoluto,
  versión del baseline `cli-4`, timeout, entorno completo y herramientas de
  Claude. `USER` obligatorio e igual a la cuenta del UID local (D024).
- `[[projects]]`: id, raíz canónica, `repository_trusted = true`, perfil
  `typescript-web`, política de modelos/esfuerzos sin valores por defecto,
  `tag_kind` y techo de permisos H3.2 opcionales (validación existente).
  Bootstrap desactivado.
- `[projects.commands]`: ejecutables absolutos por nombre (sin PATH), entorno
  completo, límites D047 y `authorize_profile_commands`. Todos los comandos del
  perfil deben quedar autorizados exactamente; `[[projects.commands.authorized]]`
  añade variantes exactas (p. ej. una orden del contrato con timeout por
  defecto), nunca prefijos ni sustituciones.

Los ejecutables deben existir y ser ejecutables; los de CLI/comandos pueden ser
enlaces versionados elegidos por el operador. Las raíces y `state_dir` no pueden
ser enlaces. Versiones de binarios no se verifican por contenido.

## Composición y congelación

Por proyecto: `CLIProcessAdapter` (cli-4), `ManagedCommandRunner` (commands-1,
D047) y `GitWorkspace` con el Git configurado, **nuevos en cada job**. Versiones
congeladas: `engine` (`harness-local-<versión del paquete>`), `evidence=git-1`,
`local_config=local-config-1`, perfil, hashes del adaptador CLI y de comandos, y
`local_config_sha256` de la tabla del proyecto, proveedores, Git y `state_dir`.

Al ejecutar o hacer commit, la composición vigente debe coincidir con la
congelada en el job. Si se edita el TOML y se reinicia con jobs pendientes, el
job se aborta antes de lanzar CLI, comandos o Git: cuarentena
`RECOVERY_REQUIRED` y confirmación explícita existente, sin reescribir versiones.
Terminar o detener los jobs antes de cambiar la composición. D048 sigue
impidiendo usar otro runner con una configuración nativa congelada.

`ManagedRuntime` conserva sus comprobaciones: base SQLite y migraciones fuera de
checkouts; ids/raíces únicos; restauraciones de consulta ignoran la composición.
La validación de proyectos sin base se ha separado como `validate_projects`
para reutilizarla desde `check-config`, sin cambiar su contenido.

## Verificación offline

`tests/product/test_local_config.py`, 35 casos, con CLI falsas
(`cli_process_probe.py`, modo `web`) por el adaptador CLI real, Node/npm/tsc
reales con la caché local, Git/worktree/SQLite temporales:

- composición válida, puertos nuevos por job, rutas de artefactos y Git, sin
  procesos ni directorios al cargar; plantilla con las mismas claves;
- 22 rechazos de esquema con su motivo comprobado (claves, formato, rutas,
  confianza, perfil, modelos, USER, versión CLI, ejecutables, estado dentro del
  checkout, autorización incompleta, duplicados, id con escape, entorno, inf,
  tag, techo de permisos) y 7 del archivo (enlace, escritura de grupo, dentro
  del checkout, tamaño, UTF-8, ruta relativa, TOML inválido);
- variante exacta adicional autorizada sin sustituir las del perfil;
- cambio de composición tras admitir: cuarentena sin lanzamientos ni comandos;
- recorrido completo: runtime registra el proyecto, ejecutor/revisor CLI con
  sesiones nuevas, preparación/tipos/tests/build reales con JUnit, aceptación,
  commit con la identidad configurada y historial idéntico tras reabrir SQLite;
- `check-config` sin valores de entorno, con preflight de version/help y error
  explicado; `serve --config` rechaza `HARNESS_MANAGED_CONFIG`; `from_environment`.

Pendientes: piloto/smoke con proveedores (D033.8, autorización nueva), QA
visual, otros perfiles, `.harness/project.yaml`, UI de configuración, recarga
en caliente, bootstrap por configuración y verificación del wheel instalado con
`--config`.
