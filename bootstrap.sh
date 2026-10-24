#!/usr/bin/env bash
# Prepare a new Mac from this repository. Previews by default; --apply installs.
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
APPLY=0

case "${1:-}" in
  "") ;;
  --apply) APPLY=1 ;;
  -h | --help)
    echo "usage: bootstrap.sh [--apply]"
    echo "Without --apply, only shows what would change."
    exit 0
    ;;
  *)
    echo "ERROR: unknown argument: $1" >&2
    exit 2
    ;;
esac

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: bootstrap.sh targets macOS only." >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "ERROR: Homebrew is not installed." >&2
  echo "Install it from https://brew.sh, then run this script again." >&2
  exit 1
fi

echo "== Homebrew packages (Brewfile)"
if [ "$APPLY" -eq 1 ]; then
  brew bundle --file="$ROOT/Brewfile"
else
  # `check` exits non-zero when something is missing; that is not an error here.
  brew bundle check --file="$ROOT/Brewfile" --verbose || true
fi

echo "== WezTerm configuration"
if [ "$APPLY" -eq 1 ]; then
  python3 "$ROOT/scripts/install_wezterm.py" --apply
else
  python3 "$ROOT/scripts/install_wezterm.py"
fi

if [ "$APPLY" -eq 1 ]; then
  echo
  echo "Done. Logins and keys are manual: see docs/new-machine.md."
fi
