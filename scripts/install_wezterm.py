#!/usr/bin/env python3
"""Link the WezTerm configuration, with a dry-run default."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from install import ROOT, link, preflight_links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create the link after previewing")
    args = parser.parse_args()

    target_home = Path.home()
    links = (
        (
            ROOT / "wezterm" / "wezterm.lua",
            target_home / ".config" / "wezterm" / "wezterm.lua",
        ),
    )

    try:
        preflight_links(links, target_home)
    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"HOME  {target_home}")
    for source, destination in links:
        link(source, destination, target_home, args.apply)

    if not args.apply:
        print("Dry run only. Re-run with --apply to install.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
