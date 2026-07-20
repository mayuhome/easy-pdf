#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.build-venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

printf "[build] project root: %s\n" "$ROOT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[build] error: python executable not found: $PYTHON_BIN" >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  printf "[build] creating virtual environment: %s\n" "$VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

printf "[build] upgrading pip/build tooling...\n"
python -m pip install --upgrade pip setuptools wheel build

printf "[build] cleaning old artifacts...\n"
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist"
find "$ROOT_DIR" -maxdepth 1 -name "*.egg-info" -type d -exec rm -rf {} +

printf "[build] building wheel and sdist...\n"
python -m build "$ROOT_DIR"

printf "[build] done. artifacts:\n"
ls -1 "$ROOT_DIR/dist"
