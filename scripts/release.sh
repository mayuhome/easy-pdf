#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RELEASE_VENV="${ROOT_DIR}/.release-venv"
SMOKE_VENV="${ROOT_DIR}/.release-smoke-venv"
RUN_TESTS=1

usage() {
  cat <<'EOF'
Usage: ./scripts/release.sh [--skip-tests]

Options:
  --skip-tests    Skip pytest before build.
  -h, --help      Show this help message.

Environment:
  PYTHON_BIN      Python executable to use (default: python3)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-tests)
      RUN_TESTS=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[release] unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

printf "[release] project root: %s\n" "$ROOT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[release] error: python executable not found: $PYTHON_BIN" >&2
  exit 1
fi

cd "$ROOT_DIR"

if [[ ! -d "$RELEASE_VENV" ]]; then
  printf "[release] creating release venv: %s\n" "$RELEASE_VENV"
  "$PYTHON_BIN" -m venv "$RELEASE_VENV"
fi

# shellcheck disable=SC1091
source "$RELEASE_VENV/bin/activate"

printf "[release] installing release tooling...\n"
python -m pip install --upgrade pip setuptools wheel build
python -m pip install -e ".[dev,pdf,gui]"

if [[ "$RUN_TESTS" -eq 1 ]]; then
  printf "[release] running tests...\n"
  pytest
else
  printf "[release] skipping tests (--skip-tests).\n"
fi

printf "[release] building artifacts...\n"
./scripts/build.sh

WHEEL_PATH="$(ls -1t "$ROOT_DIR"/dist/*.whl | head -n 1)"
if [[ -z "$WHEEL_PATH" ]]; then
  echo "[release] error: wheel artifact not found in dist/" >&2
  exit 1
fi
printf "[release] wheel artifact: %s\n" "$WHEEL_PATH"

if [[ -d "$SMOKE_VENV" ]]; then
  rm -rf "$SMOKE_VENV"
fi
printf "[release] creating smoke-test venv: %s\n" "$SMOKE_VENV"
"$PYTHON_BIN" -m venv "$SMOKE_VENV"

# shellcheck disable=SC1091
source "$SMOKE_VENV/bin/activate"

printf "[release] installing wheel with optional deps...\n"
python -m pip install --upgrade pip
python -m pip install "$WHEEL_PATH[pdf,gui]"

printf "[release] validating CLI entrypoints...\n"
command -v easy-pdf >/dev/null
command -v easy-pdf-gui >/dev/null

easy-pdf health >/dev/null
python -c "from easy_pdf.gui.main_window import main; print('GUI import check: ok')"

printf "[release] success. release checks completed.\n"
printf "[release] next: activate target env and install %s\n" "$WHEEL_PATH"
