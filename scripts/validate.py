#!/usr/bin/env python3
"""Validate tracked OpenCode policy without reading secrets."""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from agent_kit_lock import LockValidationError, validate_agent_kit


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "opencode" / "opencode.jsonc"
DEFAULT_AGENT_KIT = ROOT.parent / "agent-kit"


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError("could not enumerate tracked files for secret scan")
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent-kit",
        type=Path,
        default=Path(os.environ.get("AGENT_KIT_HOME", DEFAULT_AGENT_KIT)),
        help="agent-kit repository to validate",
    )
    parser.add_argument("--lock", type=Path, help="lock required for the selected agent-kit")
    parser.add_argument(
        "--target-home",
        type=Path,
        help="absolute staging home used for a locked installation preview",
    )
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="skip effective-agent inspection before staging links are installed",
    )
    args = parser.parse_args()
    agent_kit = args.agent_kit.expanduser().resolve()
    failures: list[str] = []

    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invalid OpenCode JSONC subset: {error}")
        return 1

    if config.get("$schema") != "https://opencode.ai/config.json":
        failures.append("OpenCode schema declaration is missing")
    if config.get("share") != "disabled":
        failures.append("session sharing must remain disabled")
    if config.get("default_agent") != "build":
        failures.append("build must remain the default agent")

    agents = config.get("agent", {})
    auditor = agents.get("decision-auditor", {})
    if auditor.get("model") != "openai/gpt-5.6-sol":
        failures.append("decision-auditor must use openai/gpt-5.6-sol")
    if auditor.get("temperature") != 0:
        failures.append("decision-auditor temperature must remain zero")

    if config.get("mcp"):
        failures.append("MCPs must not be enabled without a policy review")

    permission = config.get("permission", {})
    if permission.get("doom_loop") != "deny":
        failures.append("doom-loop protection must remain denied")
    if permission.get("external_directory", {}).get("*") != "deny":
        failures.append("external directories must be denied by default")
    skill_policy = permission.get("skill", {})
    if skill_policy.get("*") != "deny":
        failures.append("skills must be denied by default")
    for skill_name in (
        "delegation-workflow",
        "repo-audit",
        "incident-triage",
        "hypothesis-test",
        "release-check",
        "policy-audit",
    ):
        if skill_policy.get(skill_name) != "allow":
            failures.append(f"agent-kit skill must be allowed: {skill_name}")
    for pattern in ("rm *", "sudo *", "ssh *", "gh workflow run*"):
        if permission.get("bash", {}).get(pattern) != "deny":
            failures.append(f"bash policy must deny {pattern!r}")

    sensitive_markers = (
        "BEGIN OPENSSH " + "PRIVATE KEY",
        "BEGIN " + "PRIVATE KEY",
        "WALLET_PRIVATE" + "_KEY=",
        "API" + "_KEY=",
        "TOK" + "EN=",
    )
    try:
        scan_paths = tracked_files()
    except RuntimeError as error:
        failures.append(str(error))
        scan_paths = []
    for path in scan_paths:
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in sensitive_markers:
            if marker in text:
                failures.append(f"possible secret marker in {path.relative_to(ROOT)}")

    if args.lock:
        try:
            validate_agent_kit(agent_kit, args.lock)
        except LockValidationError as error:
            failures.append(str(error))

    install_check = [
        sys.executable,
        str(ROOT / "scripts" / "install.py"),
        "--agent-kit",
        str(agent_kit),
    ]
    if args.lock:
        if args.target_home is None:
            failures.append("locked validation requires an explicit --target-home")
        else:
            install_check.extend(
                (
                    "--lock",
                    str(args.lock.expanduser().resolve()),
                    "--target-home",
                    str(args.target_home.expanduser()),
                )
            )
    checks = [
        (["sh", "-n", str(ROOT / "bin" / "opencode-safe")], ROOT),
        (install_check, ROOT),
    ]
    if not args.lock:
        checks.append(([sys.executable, str(agent_kit / "scripts" / "validate.py")], agent_kit))
    for command, cwd in checks:
        result = subprocess.run(command, cwd=cwd, check=False)
        if result.returncode:
            failures.append(f"check failed: {' '.join(command)}")

    resolved_agents = {
        "coordinator": "primary",
        "explorer": "subagent",
        "implementer": "subagent",
        "reviewer": "subagent",
        "tester": "subagent",
        "researcher": "subagent",
        "ops-observer": "subagent",
        "decision-auditor": "subagent",
    }
    if args.source_only:
        resolved_agents = {}
    for agent_name, expected_mode in resolved_agents.items():
        environment = os.environ.copy()
        if args.target_home is not None:
            environment["HOME"] = str(args.target_home.expanduser())
            environment.pop("XDG_CONFIG_HOME", None)
            environment.pop("XDG_DATA_HOME", None)
            environment.pop("OPENCODE_CONFIG", None)
            environment.pop("OPENCODE_CONFIG_CONTENT", None)
        environment["OPENCODE_DISABLE_PROJECT_CONFIG"] = "1"
        result = subprocess.run(
            ["opencode", "debug", "agent", agent_name],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            failures.append(f"OpenCode could not resolve agent {agent_name}")
            continue
        try:
            resolved = json.loads(result.stdout)
        except json.JSONDecodeError:
            failures.append(f"OpenCode returned invalid agent data for {agent_name}")
            continue
        if resolved.get("mode") != expected_mode:
            failures.append(
                f"{agent_name} resolved mode is {resolved.get('mode')!r}, expected {expected_mode!r}"
            )

        permissions = resolved.get("permission", [])
        if agent_name == "decision-auditor":
            required_denials = {
                "edit",
                "bash",
                "task",
                "external_directory",
                "webfetch",
                "websearch",
            }
            for permission_name in required_denials:
                matching = [
                    rule
                    for rule in permissions
                    if rule.get("permission") == permission_name
                ]
                if not matching or any(rule.get("action") != "deny" for rule in matching):
                    failures.append(
                        "decision-auditor must resolve every "
                        f"{permission_name} rule as denied"
                    )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Dotfiles policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
