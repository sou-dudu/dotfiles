#!/usr/bin/env python3
"""Install dotfile and agent-kit links, with a dry-run default."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_kit_lock import LockValidationError, load_lock, validate_agent_kit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AGENT_KIT = ROOT.parent / "agent-kit"
STAGING_LOCK = ROOT / "locks" / "agent-kit-staging.json"


def display(path: Path, target_home: Path) -> str:
    try:
        return f"~/{path.relative_to(target_home)}"
    except ValueError:
        return str(path)


def link(source: Path, destination: Path, target_home: Path, apply: bool) -> None:
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"missing source: {source}")

    if destination.is_symlink() and destination.resolve() == source:
        print(f"OK    {display(destination, target_home)} -> {source}")
        return

    print(f"LINK  {display(destination, target_home)} -> {source}")
    if not apply:
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup = destination.with_name(f"{destination.name}.backup-{timestamp}")
        destination.rename(backup)
        print(f"BACKUP {display(backup, target_home)}")
    destination.symlink_to(source, target_is_directory=source.is_dir())


def preflight_links(links: tuple[tuple[Path, Path], ...], target_home: Path) -> None:
    """Validate the complete plan before apply can mutate any destination."""
    destinations: set[Path] = set()
    for source, destination in links:
        resolved_source = source.resolve()
        if not resolved_source.exists():
            raise FileNotFoundError(f"missing source: {resolved_source}")
        if destination in destinations:
            raise ValueError(f"duplicate link destination: {destination}")
        destinations.add(destination)

        try:
            relative = destination.relative_to(target_home)
        except ValueError as error:
            raise ValueError(
                f"link destination is outside target home: {destination}"
            ) from error
        if not relative.parts or ".." in relative.parts:
            raise ValueError(f"unsafe link destination: {destination}")

        parent = destination.parent
        while True:
            if parent.is_symlink():
                raise ValueError(f"destination parent must not be a symlink: {parent}")
            if parent.exists() and not parent.is_dir():
                raise NotADirectoryError(
                    f"destination parent is not a directory: {parent}"
                )
            if parent == parent.parent:
                break
            parent = parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create links after previewing")
    parser.add_argument(
        "--target-home",
        type=Path,
        help="absolute home directory to receive links (required with a lock)",
    )
    parser.add_argument(
        "--agent-kit",
        type=Path,
        default=Path(os.environ.get("AGENT_KIT_HOME", DEFAULT_AGENT_KIT)),
        help="path to the agent-kit repository",
    )
    lock_group = parser.add_mutually_exclusive_group()
    lock_group.add_argument(
        "--staging",
        action="store_true",
        help="require the reviewed staging agent-kit lock",
    )
    lock_group.add_argument(
        "--lock",
        type=Path,
        help="require an explicit agent-kit lock file",
    )
    args = parser.parse_args()

    if (args.staging or args.lock is not None) and args.target_home is None:
        parser.error("locked installation requires an explicit absolute --target-home")
    if args.target_home is not None and not (args.staging or args.lock is not None):
        parser.error("--target-home requires --staging or --lock")
    if args.target_home is not None and not args.target_home.is_absolute():
        parser.error("--target-home must be absolute")

    agent_kit = args.agent_kit.expanduser().resolve()
    target_home = Path(os.path.abspath(args.target_home or Path.home()))
    links = (
        (
            ROOT / "opencode" / "opencode.jsonc",
            target_home / ".config" / "opencode" / "opencode.jsonc",
        ),
        (
            ROOT / "opencode" / "instructions",
            target_home / ".config" / "opencode" / "instructions",
        ),
        (
            ROOT / "opencode" / "trusted-projects",
            target_home / ".config" / "opencode" / "trusted-projects",
        ),
        (agent_kit, target_home / ".local" / "share" / "agent-kit"),
        (
            agent_kit / "adapters" / "opencode" / "agents",
            target_home / ".config" / "opencode" / "agents",
        ),
        (
            ROOT / "bin" / "opencode-safe",
            target_home / ".local" / "bin" / "opencode-safe",
        ),
    )

    try:
        lock_path = STAGING_LOCK if args.staging else args.lock
        if lock_path is not None:
            validate_agent_kit(agent_kit, lock_path)
            print(f"LOCK  {agent_kit} matches {lock_path.expanduser().resolve()}")
            activation_enabled = load_lock(lock_path.expanduser().resolve())[
                "activation_enabled"
            ]
            if args.apply and not activation_enabled:
                raise LockValidationError("agent-kit lock activation is disabled")
        preflight_links(links, target_home)
    except (FileNotFoundError, LockValidationError, NotADirectoryError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"HOME  {target_home}")
    for source, destination in links:
        link(source, destination, target_home, args.apply)

    if not args.apply:
        print("Dry run only. Re-run with --apply to install.")
    else:
        print(
            "Installation complete. Quit and restart OpenCode to load the new "
            "configuration."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
