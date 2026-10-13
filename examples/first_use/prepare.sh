#!/bin/sh
# Preparación del primer uso real (D033.8). Sin proveedores ni red.
# Uso: sh prepare.sh BASE   (BASE no debe existir; ruta absoluta canónica)
set -eu
BASE="$1"
REPO=$HOME/Documents/projects/my_harness
NODE_BIN=$HOME/.nvm/versions/node/v24.15.0/bin
CLAUDE=$HOME/.local/share/claude/versions/2.1.295
GIT=/usr/bin/git
umask 077
mkdir "$BASE"
mkdir "$BASE/operator" "$BASE/state" "$BASE/cli-tmp" "$BASE/command-home"
: > "$BASE/command-home/user.npmrc"
: > "$BASE/command-home/global.npmrc"
cp -R "$REPO/.local/npm-cache" "$BASE/npm-cache"
test -x "$CLAUDE" && test -x "$NODE_BIN/codex" && test -x "$NODE_BIN/node" && test -x "$NODE_BIN/npm"

# Checkout desechable: fixture TypeScript web + documentos de fase + regresión deliberada.
umask 022
mkdir "$BASE/web"
cp -R "$REPO/tests/fixtures/typescript_web/." "$BASE/web"
rm -rf "$BASE/web/node_modules" "$BASE/web/.build" "$BASE/web/dist" "$BASE/web/.local"
mkdir "$BASE/web/docs"
cat > "$BASE/web/docs/STATE.md" <<'EOF'
# Estado

Checkout desechable del primer uso real de Harness Local (D033.8). Base: fixture
`typescript_web` con una regresión deliberada de 45 minutos por tarea.
EOF
cat > "$BASE/web/docs/NEXT_STEPS.md" <<'EOF'
# Primer uso real — plan del checkout desechable

## P001-T001 — Restaurar treinta minutos por tarea
**Objective:** `estimateMinutes` debe volver a calcular treinta minutos por tarea; ahora calcula cuarenta y cinco.
**Allowed paths:** `src/estimate.ts`
**Acceptance criteria:**
- `estimateMinutes(3)` devuelve 90 y `estimateMinutes(0)` devuelve 0.
- Las entradas no enteras, no seguras o negativas siguen lanzando `RangeError` con el mensaje actual.
- `npm run check`, `npm run test` y `npm run build` pasan sin cambiar tests, scripts, configuración ni lock.
**Out of scope:** Cualquier archivo distinto de `src/estimate.ts`, dependencias, red y configuración.
**Executor:** claude-sonnet-4-6 / low — Selección explícita del usuario para el primer uso real
EOF
G="$GIT -C $BASE/web -c user.name=Harness-First-Use -c user.email=first-use@example.invalid -c commit.gpgsign=false"
$G init -q -b main
$G add -A
$G commit -q -m "first use: baseline"
sed -i '' 's/tasks \* 30/tasks * 45/' "$BASE/web/src/estimate.ts"
grep -q 'tasks \* 45' "$BASE/web/src/estimate.ts"
$G commit -q -am "first use: deliberate 45-minute regression"

cat > "$BASE/operator/harness-local.toml" <<EOF
# Primer uso real (D033.8). Archivo del operador; sin secretos.
format = "local-config-1"

[service]
state_dir = "$BASE/state"
supervisor = true

[git]
executable = "$GIT"
author_name = "Harness First Use"
author_email = "first-use@example.invalid"

[providers.codex]
executable = ["$NODE_BIN/codex"]
cli_version = "0.162.1"
timeout_seconds = 600
environment = { HOME = "$HOME", USER = "acosta", PATH = "$NODE_BIN:/usr/bin:/bin", TMPDIR = "$BASE/cli-tmp", LANG = "C.UTF-8" }

[providers.claude]
executable = ["$CLAUDE"]
cli_version = "2.1.295"
timeout_seconds = 900
environment = { HOME = "$HOME", USER = "acosta", PATH = "/usr/bin:/bin", TMPDIR = "$BASE/cli-tmp", LANG = "C.UTF-8", DISABLE_AUTOUPDATER = "1" }
tools = ["Read", "Edit", "Write", "Glob", "Grep"]
allowed_tools = ["Read", "Edit", "Write", "Glob", "Grep"]

[[projects]]
id = "first-use-web"
root = "$BASE/web"
repository_trusted = true
profile = "typescript-web"
tag_kind = "lightweight"

[projects.policy]
executor_models = ["claude-sonnet-4-6"]
executor_efforts = ["low"]
planner_model = "gpt-6-luna"
planner_effort = "low"
reviewer_model = "gpt-6-luna"
reviewer_effort = "medium"
max_revision_cycles = 0
planning_mode = "deterministic"

[projects.commands]
authorize_profile_commands = true
executables = { node = "$NODE_BIN/node", npm = "$NODE_BIN/npm" }
environment = { PATH = "$NODE_BIN:/usr/bin:/bin", HOME = "$BASE/command-home", TMPDIR = "$BASE/command-home", LANG = "C.UTF-8", CI = "true", npm_config_cache = "$BASE/npm-cache", npm_config_userconfig = "$BASE/command-home/user.npmrc", npm_config_globalconfig = "$BASE/command-home/global.npmrc", npm_config_update_notifier = "false" }
max_timeout_seconds = 300
max_output_bytes = 65536
EOF
chmod 600 "$BASE/operator/harness-local.toml"
echo "Preparado: $BASE"
