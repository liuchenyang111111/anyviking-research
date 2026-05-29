#!/usr/bin/env bash
set -euo pipefail

PORT="1933"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --port)
      PORT="${2:?Missing value for --port}"
      shift
      ;;
    -h|--help)
      echo "Usage: scripts/stop_openviking.sh [--port 1933]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/workspace/openviking-server.pid"

health_check() {
  "$PROJECT_ROOT/.venv/bin/python" - "http://127.0.0.1:$PORT" <<'PY' >/dev/null 2>&1
import json
import sys
import urllib.request

url = sys.argv[1].rstrip("/") + "/health"
with urllib.request.urlopen(url, timeout=3) as response:
    data = json.loads(response.read().decode("utf-8"))
healthy = bool(data.get("healthy") or data.get("status") == "ok")
raise SystemExit(0 if healthy else 1)
PY
}

STOPPED=0

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE")"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo "Stopping openviking-server, PID: $PID"
    kill "$PID"
    STOPPED=1
  fi
  rm -f "$PID_FILE"
fi

if [ "$STOPPED" -eq 0 ] && command -v pkill >/dev/null 2>&1; then
  if pgrep -f "openviking_cli.server_bootstrap|openviking-server" >/dev/null 2>&1; then
    echo "Stopping OpenViking server processes found by name."
    pkill -f "openviking_cli.server_bootstrap|openviking-server"
    STOPPED=1
  fi
fi

if [ "$STOPPED" -eq 0 ]; then
  echo "No openviking-server process found."
  exit 0
fi

sleep 2

if health_check; then
  echo "Warning: port $PORT still responds."
else
  echo "OpenViking stopped."
fi
