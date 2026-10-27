#!/bin/sh
# Una combinación de la matriz D052 (D057): preflight, init-db, serve, recorrido y TERM.
# Uso: sh run_pairing.sh BASE PAR   (PAR = <revisor>-<ejecutor>; BASE preparado con prepare.sh,
# con BASE/venv instalado desde el wheel, D051). Lanza agentes: solo con consentimiento explícito.
# Sin reintentos: cualquier fallo termina la combinación y conserva su evidencia en BASE/PAR.
set -u
B="$1"
P="$2"
A="$B/$P"
HERE=$(cd "$(dirname "$0")" && pwd)
H="$B/venv/bin/my-harness"
PY="$B/venv/bin/python"
cd "$B"
"$H" check-config "$A/operator/my-harness.toml" --preflight > "$A/preflight-run.json" || { echo PREFLIGHT-FAILED; exit 3; }
"$PY" -I -c 'import json, sys
checks = json.load(open(sys.argv[1]))["preflight"]
sys.exit(any(c["status"] != "version_help_match" or c["missing_flags"] for c in checks.values()))' \
  "$A/preflight-run.json" || { echo PREFLIGHT-MISMATCH; exit 3; }
"$H" init-db --database "$A/state/harness.sqlite3" || { echo INIT-DB-FAILED; exit 4; }
"$H" serve --database "$A/state/harness.sqlite3" --config "$A/operator/my-harness.toml" > "$A/serve.log" 2>&1 &
S=$!
echo "$S" > "$A/serve.pid"
KEY=""
for _ in $(seq 60); do
  KEY=$(sed -n 's/.*clave de acceso en //p' "$A/serve.log")
  [ -n "$KEY" ] && break
  sleep 1
done
if [ -z "$KEY" ]; then
  echo SERVE-NOT-READY
  kill -TERM "$S"
  wait "$S"
  exit 5
fi
"$PY" -I "$HERE/drive.py" "$A" "$P" "$KEY"
D=$?
echo "driver-exit $D"
kill -TERM "$S"
wait "$S"
echo "serve-exit $?"
echo ORCHESTRATION-END
exit "$D"
