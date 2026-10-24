# AI agents

The goal is that switching tool or provider costs nothing. Behavior is written
once, in a neutral format, and each tool only gets a thin link to it.

## Skills

Skills live once, in [`skills/`](../skills), as standard `SKILL.md` folders.
`scripts/install_skills.py` links each one into both tools:

```
skills/<name>  ->  ~/.claude/skills/<name>           (Claude Code)
               ->  ~/.config/opencode/skills/<name>  (OpenCode)
```

```bash
python3 scripts/install_skills.py          # preview
python3 scripts/install_skills.py --apply
```

Each skill is linked on its own, so skills installed by plugins in the same
folders are not touched. OpenCode denies skills by default; a new skill also
needs an `allow` entry in `opencode/opencode.jsonc`.

To use the same skills at work, clone this public repository inside WSL (or copy
`skills/`) and run the installer. Skills here must never contain company
information.

## Commit messages

The `commit-message` skill holds the convention: `type: Imperative subject
(ticket)`, with `feat`, `fix`, `docs` or `chore`, a description of at most 50
characters, and the ticket at the end. At work the ticket key comes from the
branch name; in personal projects it is the GitHub issue number, `(#12)`.

## MCP servers

None enabled. Each one needs its command, package source, credentials, tool
surface and read/write authority reviewed first. See [ios.md](ios.md) for the
first candidate.

## Not centralized yet

Permissions, hooks and Claude Code `settings.json` are deliberately left for
later: they differ per tool and are not portable.
