#!/usr/bin/env python3
"""Validate a local agent-kit checkout against a reviewed lock."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class LockValidationError(ValueError):
    """The selected agent-kit does not satisfy its lock."""


def _git(source: Path, *arguments: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=source,
        check=False,
        capture_output=True,
        text=text,
    )
    if result.returncode:
        error = (
            result.stderr.strip()
            if text
            else result.stderr.decode(errors="replace").strip()
        )
        raise LockValidationError(f"git {' '.join(arguments)} failed: {error}")
    return result.stdout


def tracked_tree_sha256(source: Path, revision: str = "HEAD") -> str:
    """Hash Git's deterministic recursive tree listing, including modes and blob IDs."""
    listing = _git(source, "ls-tree", "-r", "-z", "--full-tree", revision, text=False)
    assert isinstance(listing, bytes)
    return hashlib.sha256(listing).hexdigest()


def _git_blob_id(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def verify_worktree_bytes(source: Path, revision: str = "HEAD") -> None:
    """Compare every tracked regular file or symlink byte-for-byte with Git."""
    listing = _git(source, "ls-tree", "-r", "-z", "--full-tree", revision, text=False)
    assert isinstance(listing, bytes)
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        metadata, separator, relative_bytes = entry.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            raise LockValidationError("agent-kit tree contains an invalid entry")
        mode, object_type, expected_id = fields
        if object_type != b"blob" or mode not in {b"100644", b"100755", b"120000"}:
            relative = os.fsdecode(relative_bytes)
            raise LockValidationError(
                f"unsupported tracked entry type in agent-kit: {relative}"
            )

        relative = Path(os.fsdecode(relative_bytes))
        path = source / relative
        try:
            parent = path.parent
            while parent != source:
                if parent.is_symlink():
                    raise LockValidationError(
                        f"tracked agent-kit parent must not be a symlink: {parent}"
                    )
                parent = parent.parent
            file_mode = path.lstat().st_mode
            if mode == b"120000":
                if not stat.S_ISLNK(file_mode):
                    raise LockValidationError(
                        f"agent-kit worktree type does not match HEAD: {relative}"
                    )
                content = os.readlink(os.fsencode(path))
            else:
                if not stat.S_ISREG(file_mode):
                    raise LockValidationError(
                        f"agent-kit worktree type does not match HEAD: {relative}"
                    )
                content = path.read_bytes()
        except FileNotFoundError as error:
            raise LockValidationError(
                f"tracked agent-kit worktree file is missing: {relative}"
            ) from error
        if _git_blob_id(content).encode() != expected_id:
            raise LockValidationError(
                f"agent-kit worktree bytes do not match HEAD: {relative}"
            )


def _repository_identity(remote: str) -> str:
    value = remote.strip()
    if value.startswith("git@") and ":" in value:
        host, path = value[4:].split(":", 1)
        value = f"{host}/{path}"
    elif "://" in value:
        parsed = urlparse(value)
        value = f"{parsed.hostname or ''}/{parsed.path.lstrip('/')}"
    return value.removesuffix(".git").rstrip("/").lower()


def load_lock(path: Path) -> dict[str, object]:
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LockValidationError(f"invalid agent-kit lock {path}: {error}") from error

    required_keys = {
        "schema_version",
        "activation_enabled",
        "repository",
        "commit",
        "tree",
        "tracked_tree_sha256",
        "required_sources",
    }
    if set(lock) != required_keys or lock.get("schema_version") != 1:
        raise LockValidationError("agent-kit lock has an unsupported schema")
    if not isinstance(lock["activation_enabled"], bool):
        raise LockValidationError("agent-kit lock activation flag is invalid")
    if not isinstance(lock["repository"], str) or not lock["repository"]:
        raise LockValidationError("agent-kit lock repository is invalid")
    if not isinstance(lock["commit"], str) or not HEX40.fullmatch(lock["commit"]):
        raise LockValidationError("agent-kit lock commit is invalid")
    if not isinstance(lock["tree"], str) or not HEX40.fullmatch(lock["tree"]):
        raise LockValidationError("agent-kit lock tree is invalid")
    if not isinstance(lock["tracked_tree_sha256"], str) or not HEX64.fullmatch(
        lock["tracked_tree_sha256"]
    ):
        raise LockValidationError("agent-kit lock tracked-tree checksum is invalid")
    sources = lock["required_sources"]
    if (
        not isinstance(sources, list)
        or not sources
        or not all(isinstance(item, str) and item for item in sources)
    ):
        raise LockValidationError("agent-kit lock required_sources is invalid")
    return lock


def _run_python_check(source: Path, relative_script: str, *arguments: str) -> None:
    result = subprocess.run(
        [sys.executable, str(source / relative_script), *arguments],
        cwd=source,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        details = (result.stdout + result.stderr).strip()
        command = " ".join((relative_script, *arguments))
        raise LockValidationError(f"agent-kit check failed: {command}\n{details}")


def validate_agent_kit(source: Path, lock_path: Path, *, run_checks: bool = True) -> None:
    """Fail unless source exactly matches the reviewed lock and passes its checks."""
    source = source.expanduser().resolve()
    lock = load_lock(lock_path.expanduser().resolve())
    if not source.is_dir():
        raise LockValidationError(f"missing agent-kit source: {source}")

    top_level = Path(str(_git(source, "rev-parse", "--show-toplevel")).strip()).resolve()
    if top_level != source:
        raise LockValidationError(f"agent-kit source is not a Git worktree root: {source}")

    remote = str(_git(source, "config", "--get", "remote.origin.url")).strip()
    if _repository_identity(remote) != _repository_identity(str(lock["repository"])):
        raise LockValidationError("agent-kit repository identity does not match the lock")

    head = str(_git(source, "rev-parse", "HEAD")).strip()
    if head != lock["commit"]:
        raise LockValidationError(
            f"agent-kit revision {head} does not match locked {lock['commit']}"
        )

    status = str(_git(source, "status", "--porcelain", "--untracked-files=no"))
    if status:
        raise LockValidationError("agent-kit tracked worktree is dirty")
    untracked = _git(source, "ls-files", "--others", "--exclude-standard", "-z", text=False)
    ignored = _git(
        source,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
        text=False,
    )
    if untracked or ignored:
        raise LockValidationError("agent-kit contains untracked or ignored files")

    tree = str(_git(source, "rev-parse", "HEAD^{tree}")).strip()
    if tree != lock["tree"]:
        raise LockValidationError("agent-kit tree does not match the lock")
    if tracked_tree_sha256(source) != lock["tracked_tree_sha256"]:
        raise LockValidationError("agent-kit tracked-tree checksum does not match the lock")
    verify_worktree_bytes(source)

    for relative in lock["required_sources"]:
        relative_path = Path(str(relative))
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise LockValidationError(f"unsafe required source in agent-kit lock: {relative}")
        required = source / relative_path
        tracked = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{relative_path.as_posix()}"],
            cwd=source,
            check=False,
            capture_output=True,
        )
        if (
            tracked.returncode
            or not required.exists()
            or not required.resolve().is_relative_to(source)
        ):
            raise LockValidationError(f"missing or unsafe agent-kit source: {relative}")

    if run_checks:
        _run_python_check(source, "scripts/generate_adapters.py", "--check")
        _run_python_check(source, "scripts/validate.py")
