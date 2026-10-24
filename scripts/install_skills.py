#!/usr/bin/env python3
"""Link every skill in skills/ into Claude Code and OpenCode, dry-run by default."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from install import ROOT, link, preflight_links


SKILLS = ROOT / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create links after previewing")
    args = parser.parse_args()

    target_home = Path.home()
    skill_dirs = sorted(
        path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file()
    )
    # One link per skill, so skills installed by plugins in the same
    # directories are left alone.
    targets = (
        target_home / ".claude" / "skills",
        target_home / ".config" / "opencode" / "skills",
    )
    links = tuple(
        (skill, target / skill.name) for skill in skill_dirs for target in targets
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
