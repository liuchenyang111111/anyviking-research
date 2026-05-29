#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="config/ov.conf"
HOST_NAME="127.0.0.1"
PORT="1933"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --config)
      CONFIG_PATH="${2:?Missing value for --config}"
      shift
      ;;
    --host)
      HOST_NAME="${2:?Missing value for --host}"
      shift
      ;;
    --port)
      PORT="${2:?Missing value for --port}"
      shift
      ;;
    -h|--help)
      echo "Usage: scripts/start_openviking.sh [--config config/ov.conf] [--host 127.0.0.1] [--port 1933]"
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
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
CONFIG="$PROJECT_ROOT/$CONFIG_PATH"
BASE_URL="http://$HOST_NAME:$PORT"
LOG_DIR="$PROJECT_ROOT/workspace/logs"
PID_FILE="$PROJECT_ROOT/workspace/openviking-server.pid"

health_check() {
  "$PROJECT_ROOT/.venv/bin/python" - "$BASE_URL" <<'PY' >/dev/null 2>&1
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

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python not found in virtual environment: $PYTHON_BIN. Run install.sh first." >&2
  exit 2
fi

if [ ! -f "$CONFIG" ]; then
  echo "OpenViking config not found: $CONFIG" >&2
  exit 2
fi

if health_check; then
  echo "OpenViking is already running at $BASE_URL."
  exit 0
fi

mkdir -p "$LOG_DIR"

PYTHONIOENCODING=utf-8 PYTHONUTF8=1 nohup "$PYTHON_BIN" -m openviking_cli.server_bootstrap \
  --config "$CONFIG" \
  --host "$HOST_NAME" \
  --port "$PORT" \
  > "$LOG_DIR/openviking-server.log" 2>&1 &

PID="$!"
mkdir -p "$(dirname "$PID_FILE")"
echo "$PID" > "$PID_FILE"

sleep 8

if health_check; then
  echo "OpenViking started."
  echo "PID: $PID"
  echo "Log: $LOG_DIR/openviking-server.log"
else
  echo "OpenViking process started but health check failed. PID: $PID" >&2
  echo "Log: $LOG_DIR/openviking-server.log" >&2
  exit 2
fi
