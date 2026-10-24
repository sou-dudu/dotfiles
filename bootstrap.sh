#!/usr/bin/env bash
# Prepare a new Mac from this repository. Previews by default; --apply installs.
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
APPLY=0
IOS=0

for argument in "$@"; do
  case "$argument" in
    --apply) APPLY=1 ;;
    --ios) IOS=1 ;;
    -h | --help)
      echo "usage: bootstrap.sh [--apply] [--ios]"
      echo "Without --apply, only shows what would change."
      echo "--ios also covers the iOS development tools (Brewfile.ios)."
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $argument" >&2
      exit 2
      ;;
  esac
done

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: bootstrap.sh targets macOS only." >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "ERROR: Homebrew is not installed." >&2
  echo "Install it from https://brew.sh, then run this script again." >&2
  exit 1
fi

# A failing step must not stop the others: a single package that cannot be
# downloaded should not leave a new machine without its configuration links.
failed=0

brewfiles=("$ROOT/Brewfile")
if [ "$IOS" -eq 1 ]; then
  brewfiles+=("$ROOT/Brewfile.ios")
fi

for brewfile in "${brewfiles[@]}"; do
  echo "== Homebrew packages ($(basename "$brewfile"))"
  if [ "$APPLY" -eq 1 ]; then
    brew bundle --file="$brewfile" || failed=1
  else
    # `check` exits non-zero when something is missing; that is not an error here.
    brew bundle check --file="$brewfile" --verbose || true
  fi
done

for installer in install_wezterm.py install_skills.py install_shell.py; do
  echo "== ${installer%.py}"
  if [ "$APPLY" -eq 1 ]; then
    python3 "$ROOT/scripts/$installer" --apply || failed=1
  else
    python3 "$ROOT/scripts/$installer"
  fi
done

echo "== WezTerm icon"
wezterm_app="/Applications/WezTerm.app"
if [ ! -d "$wezterm_app" ]; then
  echo "SKIP  WezTerm is not installed"
elif ! command -v fileicon >/dev/null 2>&1; then
  echo "SKIP  fileicon is not installed (it comes with the Brewfile)"
elif [ "$APPLY" -eq 1 ]; then
  # A WezTerm upgrade restores the original icon; run this again to re-apply.
  fileicon set "$wezterm_app" "$ROOT/wezterm/icon.icns" || failed=1
else
  echo "ICON  $wezterm_app <- $ROOT/wezterm/icon.icns"
fi

if [ "$failed" -eq 1 ]; then
  echo
  echo "ERROR: some steps failed; see the output above. The rest was applied." >&2
  exit 1
fi

if [ "$APPLY" -eq 1 ]; then
  echo
  echo "Done. Logins and keys are manual: see docs/new-machine.md."
fi
