#!/usr/bin/env bash
# Rebuild wezterm/icon.icns from wezterm/icon.svg. macOS only; needs swift and iconutil.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

swift "$ROOT/scripts/render_iconset.swift" "$ROOT/wezterm/icon.svg" "$WORK/WezTerm.iconset"
iconutil -c icns "$WORK/WezTerm.iconset" -o "$ROOT/wezterm/icon.icns"
echo "Wrote wezterm/icon.icns"
