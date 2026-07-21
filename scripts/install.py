#!/usr/bin/env python3
"""Install dotfile and agent-kit links, with a dry-run default."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
DEFAULT_AGENT_KIT = ROOT.parent / "agent-kit"


def display(path: Path) -> str:
    try:
        return f"~/{path.relative_to(HOME)}"
    except ValueError:
        return str(path)


def link(source: Path, destination: Path, apply: bool) -> None:
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"missing source: {source}")

    if destination.is_symlink() and destination.resolve() == source:
        print(f"OK    {display(destination)} -> {source}")
        return

    print(f"LINK  {display(destination)} -> {source}")
    if not apply:
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup = destination.with_name(f"{destination.name}.backup-{timestamp}")
        destination.rename(backup)
        print(f"BACKUP {display(backup)}")
    destination.symlink_to(source, target_is_directory=source.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create links after previewing")
    parser.add_argument(
        "--agent-kit",
        type=Path,
        default=Path(os.environ.get("AGENT_KIT_HOME", DEFAULT_AGENT_KIT)),
        help="path to the agent-kit repository",
    )
    args = parser.parse_args()

    agent_kit = args.agent_kit.expanduser().resolve()
    links = (
        (ROOT / "opencode" / "opencode.jsonc", HOME / ".config" / "opencode" / "opencode.jsonc"),
        (ROOT / "opencode" / "instructions", HOME / ".config" / "opencode" / "instructions"),
        (ROOT / "opencode" / "trusted-projects", HOME / ".config" / "opencode" / "trusted-projects"),
        (agent_kit, HOME / ".local" / "share" / "agent-kit"),
        (
            agent_kit / "adapters" / "opencode" / "agents",
            HOME / ".config" / "opencode" / "agents",
        ),
        (ROOT / "bin" / "opencode-safe", HOME / ".local" / "bin" / "opencode-safe"),
    )

    for source, destination in links:
        link(source, destination, args.apply)

    if not args.apply:
        print("Dry run only. Re-run with --apply to install.")
    else:
        print("Installation complete. Quit and restart OpenCode to load the new configuration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
