# Composición de uso real por configuración local — alcance previo

Elegido por el usuario el 2026-10-13 tras D048, sobre `5e0c374`, Git limpio.
Decisiones del usuario: archivo **TOML fuera del checkout** leído con `tomllib`
(sin dependencias nuevas) y perfil **TypeScript web** como primera composición.
No autoriza ejecutar proveedores, smokes ni piloto.

## Diseño acotado

- Módulo `services/local_config.py` (`local-config-1`) que convierte un TOML del
  operador en `ManagedConfig`: servicio, Git, CLI Codex/Claude y proyectos.
  Sin valores implícitos para ejecutables, entorno, confianza, modelos ni
  esfuerzos. Claves desconocidas, tipos erróneos o rutas relativas se rechazan.
- El archivo es autoridad local: regular, sin enlaces, del UID del servicio, sin
  escritura de grupo/otros, ≤ 64 KiB, UTF-8 y fuera de todo checkout. No se lee
  nada del repositorio gestionado ni `.harness/project.yaml` (portable, futuro).
  No debe contener secretos: la autenticación sigue en cada CLI.
- Proyectos: id, raíz canónica existente, `repository_trusted = true` explícito,
  perfil `typescript-web` (único admitido), política de modelos/esfuerzos y
  `tag_kind` opcional; techo de permisos H3.2 opcional con la validación
  existente. Bootstrap desactivado.
- Composición por job, siempre nueva: `CLIProcessAdapter` (artefactos en
  `state_dir/artifacts/<id>`), `ManagedCommandRunner` (D047) con ejecutables
  absolutos, entorno explícito y autorización exacta de los comandos del perfil
  solo si `authorize_profile_commands = true`, más variantes declaradas, y
  `GitWorkspace` con Git absoluto e identidad explícita.
- Versiones congeladas por proyecto: adaptadores CLI y comandos con sus hashes,
  versión del paquete, `local-config-1` y hash de la composición del proyecto.
  Si al ejecutar difieren de las vigentes, el job se aborta antes de efectos
  con la cuarentena existente; no se reinterpreta ni se reescribe.
- Entorno CLI: `USER` obligatorio y comprobado contra el UID local (D024).
- Entrada: `harness-local serve --config RUTA` (incompatible con
  `HARNESS_MANAGED_CONFIG`), `harness-local check-config RUTA [--preflight]`
  (resumen sin valores de entorno; preflight solo version/help D042) y
  `local_config:from_environment` con `HARNESS_LOCAL_CONFIG` para desarrollo.
  Cargar la configuración nunca lanza procesos. Supervisor explícito.

## Criterios de aceptación

1. Configuración válida produce proyecto, contexto, versiones y puertos nuevos
   por job sin lanzar procesos; ejemplo documentado coherente con el esquema.
2. Rechazo sin efectos de: claves desconocidas, rutas relativas o inexistentes,
   archivo enlazado/compartible/grande/dentro de un checkout, estado dentro de
   un checkout, confianza ausente, perfil no admitido, modelos ausentes, USER
   distinto, CLI no soportada, ids/raíces duplicados.
3. Cambio de composición tras admitir un job: cuarentena antes de CLI/comandos.
4. Recorrido offline con el TOML: CLI falsas por el adaptador real, Node/npm/tsc
   reales, Git/SQLite temporales hasta aceptación y commit exacto; runtime del
   servicio registra el proyecto. `check-config` sin secretos y con preflight.
5. Regresión offline, diff revisado, STATE/NEXT_STEPS/DECISIONS/README/AGENTS.

Fuera: proveedores reales, login, smokes, otros perfiles, `.harness/project.yaml`,
UI de configuración, recarga en caliente, bootstrap, red e instalación online,
publicación/push, configuración global, ReferenceProject y harness de desarrollo.
Sin contradicción material: la especificación ubica la configuración local en el
directorio de la aplicación y reserva el YAML del repositorio para datos portables.
