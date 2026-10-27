#!/bin/sh
# Preparación del smoke de la matriz D052 (local-config-2; transporte del wheel instalado). Sin proveedores ni red.
# Uso: sh prepare.sh BASE [PAR ...]   (BASE no debe existir; ruta absoluta canónica)
# Sin PAR prepara las cuatro combinaciones; D060 selecciona solo las 2–4.
# Crea BASE/<revisor>-<ejecutor> para las combinaciones seleccionadas, cada una con su
# checkout desechable, su TOML 0600, su estado y sus áreas privadas.
set -eu
BASE="${1:?Uso: prepare.sh BASE [PAR ...]}"
shift
if [ "$#" -eq 0 ]; then
  set -- codex-claude codex-codex claude-claude claude-codex
fi
for pair in "$@"; do
  case "$pair" in
    codex-claude|codex-codex|claude-claude|claude-codex) ;;
    *) echo "Combinación desconocida: $pair" >&2; exit 2 ;;
  esac
done
REPO=$HOME/Documents/projects/my_harness
NODE_BIN=$HOME/.nvm/versions/node/v24.15.0/bin
CODEX="$NODE_BIN/codex"
CLAUDE=$HOME/.local/share/claude/versions/2.1.296
GIT=/usr/bin/git
HOME_DIR=$HOME
USER_NAME=acosta
test -x "$CLAUDE" && test -x "$CODEX" && test -x "$NODE_BIN/node" && test -x "$NODE_BIN/npm"
umask 077
mkdir "$BASE"

# Selecciones del usuario (D055): modelos de D050, revisor medium, catálogo del ejecutor low.
model() { case "$1" in codex) echo gpt-6-luna ;; claude) echo claude-sonnet-4-6 ;; esac; }

# agent ROL PROVEEDOR ÁREA: tabla [agents.ROL] del TOML.
agent() {
  echo "[agents.$1]"
  echo "provider = \"$2\""
  if [ "$1" = reviewer ]; then
    echo "model = \"$(model "$2")\""
    echo 'effort = "medium"'
    timeout=600
  else
    timeout=900
  fi
  if [ "$2" = codex ]; then
    echo "executable = [\"$CODEX\"]"
    echo 'cli_version = "0.162.1"'
    echo "timeout_seconds = $timeout"
    echo "environment = { HOME = \"$HOME_DIR\", USER = \"$USER_NAME\", PATH = \"$NODE_BIN:/usr/bin:/bin\", TMPDIR = \"$3/cli-tmp\", LANG = \"C.UTF-8\" }"
  else
    echo "executable = [\"$CLAUDE\"]"
    echo 'cli_version = "2.1.296"'
    echo "timeout_seconds = $timeout"
    echo "environment = { HOME = \"$HOME_DIR\", USER = \"$USER_NAME\", PATH = \"/usr/bin:/bin\", TMPDIR = \"$3/cli-tmp\", LANG = \"C.UTF-8\", DISABLE_AUTOUPDATER = \"1\" }"
    if [ "$1" = executor ]; then
      echo 'tools = ["Read", "Edit", "Write", "Glob", "Grep"]'
      echo 'allowed_tools = ["Read", "Edit", "Write", "Glob", "Grep"]'
    fi
  fi
  echo
}

prepare() {
  REVIEWER="$1"
  EXECUTOR="$2"
  PAIR="$REVIEWER-$EXECUTOR"
  C="$BASE/$PAIR"
  umask 077
  mkdir "$C" "$C/operator" "$C/state" "$C/cli-tmp" "$C/command-home"
  : > "$C/command-home/user.npmrc"
  : > "$C/command-home/global.npmrc"
  cp -R "$REPO/.local/npm-cache" "$C/npm-cache"

  # Checkout desechable: fixture TypeScript web + documentos de fase + regresión deliberada.
  umask 022
  mkdir "$C/web"
  cp -R "$REPO/tests/fixtures/typescript_web/." "$C/web"
  rm -rf "$C/web/node_modules" "$C/web/.build" "$C/web/dist" "$C/web/.local"
  mkdir "$C/web/docs"
  cat > "$C/web/docs/STATE.md" <<EOF
# Estado

Checkout desechable del smoke de la matriz D052, combinación revisor $REVIEWER →
ejecutor $EXECUTOR. Base: fixture \`typescript_web\` con una regresión deliberada de
45 minutos por tarea.
EOF
  cat > "$C/web/docs/NEXT_STEPS.md" <<EOF
# Smoke de la matriz D052 — plan del checkout desechable

## P001-T001 — Restaurar treinta minutos por tarea
**Objective:** \`estimateMinutes\` debe volver a calcular treinta minutos por tarea; ahora calcula cuarenta y cinco.
**Allowed paths:** \`src/estimate.ts\`
**Acceptance criteria:**
- \`estimateMinutes(3)\` devuelve 90 y \`estimateMinutes(0)\` devuelve 0.
- Las entradas no enteras, no seguras o negativas siguen lanzando \`RangeError\` con el mensaje actual.
- \`npm run check\`, \`npm run test\` y \`npm run build\` pasan sin cambiar tests, scripts, configuración ni lock.
**Validation commands:** ninguno adicional; el perfil ejecuta siempre check, test y build.
**Out of scope:** Cualquier archivo distinto de \`src/estimate.ts\`, dependencias, red y configuración.
**Executor:** $(model "$EXECUTOR") / low — Catálogo del usuario para el smoke de la matriz D052
EOF
  G="$GIT -C $C/web -c user.name=Harness-Provider-Matrix -c user.email=matrix@example.invalid -c commit.gpgsign=false"
  $G init -q -b main
  $G add -A
  $G commit -q -m "provider matrix: baseline"
  sed -i '' 's/tasks \* 30/tasks * 45/' "$C/web/src/estimate.ts"
  grep -q 'tasks \* 45' "$C/web/src/estimate.ts"
  $G commit -q -am "provider matrix: deliberate 45-minute regression"

  umask 077
  {
    echo "# Smoke de la matriz D052: revisor $REVIEWER → ejecutor $EXECUTOR. Archivo del operador; sin secretos."
    echo 'format = "local-config-2"'
    echo
    echo '[service]'
    echo "state_dir = \"$C/state\""
    echo 'supervisor = true'
    echo
    echo '[git]'
    echo "executable = \"$GIT\""
    echo 'author_name = "Harness Provider Matrix"'
    echo 'author_email = "matrix@example.invalid"'
    echo
    agent reviewer "$REVIEWER" "$C"
    agent executor "$EXECUTOR" "$C"
    cat <<EOF
[[projects]]
id = "matrix-$PAIR"
root = "$C/web"
repository_trusted = true
profile = "typescript-web"
tag_kind = "lightweight"

[projects.policy]
planning_mode = "agent"
executor_mode = "catalog"
executor_models = ["$(model "$EXECUTOR")"]
executor_efforts = ["low"]
max_revision_cycles = 0

[projects.commands]
authorize_profile_commands = true
executables = { node = "$NODE_BIN/node", npm = "$NODE_BIN/npm" }
environment = { PATH = "$NODE_BIN:/usr/bin:/bin", HOME = "$C/command-home", TMPDIR = "$C/command-home", LANG = "C.UTF-8", CI = "true", npm_config_cache = "$C/npm-cache", npm_config_userconfig = "$C/command-home/user.npmrc", npm_config_globalconfig = "$C/command-home/global.npmrc", npm_config_update_notifier = "false" }
max_timeout_seconds = 1800
max_output_bytes = 65536

# Variantes exactas que el planificador puede proponer como validation_commands
# (argv sin timeout → 1800 s por defecto). Otro argv no está autorizado: su validación falla.
EOF
    for script in check test build; do
      echo
      echo '[[projects.commands.authorized]]'
      echo "argv = [\"npm\", \"run\", \"$script\"]"
      echo 'timeout_seconds = 1800'
    done
  } > "$C/operator/my-harness.toml"
  chmod 600 "$C/operator/my-harness.toml"
  echo "Preparado: $C"
}

# Orden de novedad creciente: planificador Codex, escritor Codex, lector Claude, ambos.
for pair in "$@"; do
  prepare "${pair%-*}" "${pair#*-}"
done
