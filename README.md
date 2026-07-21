# Dotfiles

Local policy and machine integration for OpenCode.

This repository intentionally does not contain reusable agent prompts. Those live
in the sibling `agent-kit` repository. This repository owns:

- model assignment;
- trusted-project selection;
- local permission policy;
- OpenCode installation links;
- future MCP registration and credential references;
- safe launch behavior for untrusted repositories.

## Install

Preview all filesystem changes:

```bash
python3 scripts/install.py
```

Apply after reviewing the preview:

```bash
python3 scripts/install.py --apply
```

The installer backs up conflicting files instead of deleting them. It does not
touch OpenCode's package files, plugins, authentication store, or provider state.

After installation, launch OpenCode through:

```bash
opencode-safe
```

The launcher enables project configuration only for roots listed in
`opencode/trusted-projects`. Everywhere else it sets
`OPENCODE_DISABLE_PROJECT_CONFIG=1`.

## Validate

```bash
make check
```

Configuration changes require quitting and restarting OpenCode.
