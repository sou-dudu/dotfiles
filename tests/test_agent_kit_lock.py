from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
sys.path.insert(0, str(ROOT / "scripts"))

from agent_kit_lock import tracked_tree_sha256  # noqa: E402


class AgentKitLockInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.agent_kit = self.root / "agent-kit"
        self.home = self.root / "home"
        self.home.mkdir()
        self.agent_kit.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.invalid")
        self.git("remote", "add", "origin", "https://github.com/example/agent-kit.git")

        files = {
            ".gitignore": "*.ignored\n",
            "adapters/opencode/agents/test.md": "generated\n",
            "scripts/generate_adapters.py": "raise SystemExit(0)\n",
            "scripts/validate.py": "raise SystemExit(0)\n",
            "tracked.txt": "clean\n",
        }
        for relative, content in files.items():
            path = self.agent_kit / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        (self.agent_kit / "tracked-link").symlink_to("tracked.txt")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.lock = self.root / "lock.json"
        self.write_lock()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.agent_kit,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def write_lock(
        self, *, extra_source: str | None = None, activation_enabled: bool = True
    ) -> None:
        sources = [
            "adapters/opencode/agents",
            "scripts/generate_adapters.py",
            "scripts/validate.py",
        ]
        if extra_source:
            sources.append(extra_source)
        data = {
            "schema_version": 1,
            "activation_enabled": activation_enabled,
            "repository": "github.com/example/agent-kit",
            "commit": self.git("rev-parse", "HEAD"),
            "tree": self.git("rev-parse", "HEAD^{tree}"),
            "tracked_tree_sha256": tracked_tree_sha256(self.agent_kit),
            "required_sources": sources,
        }
        self.lock.write_text(json.dumps(data), encoding="utf-8")

    def install(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(self.home)
        return subprocess.run(
            [
                sys.executable,
                str(INSTALL),
                "--agent-kit",
                str(self.agent_kit),
                "--lock",
                str(self.lock),
                "--target-home",
                str(self.home),
                *arguments,
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_failed_without_home_mutation(self, expected: str) -> None:
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_correct_revision_previews_without_mutation(self) -> None:
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run only", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_wrong_revision_fails(self) -> None:
        (self.agent_kit / "tracked.txt").write_text("new commit\n", encoding="utf-8")
        self.git("add", "tracked.txt")
        self.git("commit", "-m", "wrong revision")
        self.assert_failed_without_home_mutation("does not match locked")

    def test_dirty_tracked_source_fails(self) -> None:
        (self.agent_kit / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        self.assert_failed_without_home_mutation("tracked worktree is dirty")

    def test_skip_worktree_cannot_hide_byte_mismatch(self) -> None:
        self.git("update-index", "--skip-worktree", "tracked.txt")
        (self.agent_kit / "tracked.txt").write_text("hidden dirty\n", encoding="utf-8")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=no"), "")
        self.assert_failed_without_home_mutation("worktree bytes do not match HEAD")

    def test_skip_worktree_cannot_hide_symlink_byte_mismatch(self) -> None:
        self.git("update-index", "--skip-worktree", "tracked-link")
        (self.agent_kit / "tracked-link").unlink()
        (self.agent_kit / "tracked-link").symlink_to("other-target")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=no"), "")
        self.assert_failed_without_home_mutation("worktree bytes do not match HEAD")

    def test_repository_mismatch_fails(self) -> None:
        self.git("remote", "set-url", "origin", "https://github.com/other/repo.git")
        self.assert_failed_without_home_mutation("repository identity does not match")

    def test_untracked_file_fails(self) -> None:
        (self.agent_kit / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        self.assert_failed_without_home_mutation("untracked or ignored files")

    def test_ignored_file_fails(self) -> None:
        (self.agent_kit / "cache.ignored").write_text("ignored\n", encoding="utf-8")
        self.assert_failed_without_home_mutation("untracked or ignored files")

    def test_activation_false_apply_fails_without_mutation(self) -> None:
        self.write_lock(activation_enabled=False)
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lock activation is disabled", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_broken_destination_parent_symlink_fails_before_any_mutation(self) -> None:
        local = self.home / ".local"
        local.mkdir()
        broken = local / "share"
        broken.symlink_to(self.root / "missing-directory", target_is_directory=True)

        result = self.install("--apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("destination parent must not be a symlink", result.stderr)
        self.assertFalse((self.home / ".config").exists())
        self.assertTrue(broken.is_symlink())
        self.assertEqual(os.readlink(broken), str(self.root / "missing-directory"))

    def test_missing_required_source_fails(self) -> None:
        self.write_lock(extra_source="missing/source.md")
        self.assert_failed_without_home_mutation("missing or unsafe agent-kit source")

    def test_staging_preview_requires_explicit_target_home(self) -> None:
        environment = os.environ.copy()
        environment["HOME"] = str(self.home)
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALL),
                "--staging",
                "--agent-kit",
                str(self.agent_kit),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires an explicit absolute --target-home", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_staging_rejects_relative_target_home(self) -> None:
        environment = os.environ.copy()
        environment["HOME"] = str(self.home)
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALL),
                "--staging",
                "--target-home",
                "relative-home",
                "--agent-kit",
                str(self.agent_kit),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--target-home must be absolute", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_target_home_requires_lock(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALL),
                "--target-home",
                str(self.home),
                "--agent-kit",
                str(self.agent_kit),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--target-home requires --staging or --lock", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
