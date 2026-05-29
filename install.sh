#!/usr/bin/env bash
set -euo pipefail

WITH_OPENVIKING=1
DEV=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --no-openviking)
      WITH_OPENVIKING=0
      ;;
    --dev)
      DEV=1
      ;;
    -h|--help)
      echo "Usage: ./install.sh [--no-openviking] [--dev]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ -n "${PYTHON:-}" ]; then
  PYTHON_BIN="$PYTHON"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Python 3.12 was not found. Install Python 3.12 first." >&2
  exit 2
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [ "$PYTHON_VERSION" != "3.12" ]; then
  echo "Python 3.12 is required, found $PYTHON_VERSION from $PYTHON_BIN." >&2
  exit 2
fi

echo "Creating virtual environment: .venv"
"$PYTHON_BIN" -m venv .venv

VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
echo "Upgrading packaging tools"
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

EXTRAS=()
if [ "$WITH_OPENVIKING" -eq 1 ]; then
  EXTRAS+=("openviking")
fi
if [ "$DEV" -eq 1 ]; then
  EXTRAS+=("dev")
fi

INSTALL_TARGET="."
if [ "${#EXTRAS[@]}" -gt 0 ]; then
  IFS=,
  INSTALL_TARGET=".[${EXTRAS[*]}]"
  unset IFS
fi

echo "Installing AnyViking Research: $INSTALL_TARGET"
"$VENV_PYTHON" -m pip install -e "$INSTALL_TARGET" --no-build-isolation

if [ -f config/ov.conf.example ] && [ ! -f config/ov.conf ]; then
  cp config/ov.conf.example config/ov.conf
  echo "Created config/ov.conf"
fi

if [ -f config/ovcli.conf.example ] && [ ! -f config/ovcli.conf ]; then
  cp config/ovcli.conf.example config/ovcli.conf
  echo "Created config/ovcli.conf"
fi

echo ""
echo "Install complete."
echo "Activate: source .venv/bin/activate"
echo "Check:    .venv/bin/anyviking doctor"
