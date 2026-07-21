#!/usr/bin/env python3
"""Validate tracked OpenCode policy without reading secrets."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "opencode" / "opencode.jsonc"
AGENT_KIT = ROOT.parent / "agent-kit"


def main() -> int:
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
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in sensitive_markers:
            if marker in text:
                failures.append(f"possible secret marker in {path.relative_to(ROOT)}")

    checks = (
        (["sh", "-n", str(ROOT / "bin" / "opencode-safe")], ROOT),
        ([sys.executable, str(ROOT / "scripts" / "install.py")], ROOT),
        ([sys.executable, str(AGENT_KIT / "scripts" / "validate.py")], AGENT_KIT),
    )
    for command, cwd in checks:
        result = subprocess.run(command, cwd=cwd, check=False)
        if result.returncode:
            failures.append(f"check failed: {' '.join(command)}")

    resolved_agents = {
        "build": "primary",
        "coordinator": "primary",
        "decision-auditor": "subagent",
    }
    for agent_name, expected_mode in resolved_agents.items():
        environment = os.environ.copy()
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
            required_denials = {"edit", "bash", "task", "webfetch"}
            effective: dict[str, str] = {}
            for rule in permissions:
                if rule.get("pattern") == "*":
                    effective[rule.get("permission", "")] = rule.get("action", "")
            for permission_name in required_denials:
                if effective.get(permission_name) != "deny":
                    failures.append(
                        f"decision-auditor must resolve {permission_name} as denied"
                    )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Dotfiles policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
