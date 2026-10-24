# OpenCode

Local policy and machine integration for [OpenCode](https://opencode.ai). The
configuration lives in `opencode/`, with launch and install helpers in `bin/`
and `scripts/`.

Reusable agent prompts and roles are intentionally not here. They live in the
separate `agent-kit` repository. This repository owns:

- model assignment;
- trusted-project selection;
- local permission policy;
- OpenCode installation links;
- future MCP registration and credential references;
- safe launch behavior for untrusted repositories.

The reasoning behind these boundaries is in [policy-model.md](policy-model.md).

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
For the separately approved staging workflow, use the pinned validation and
activation procedure in [staging-agent-kit.md](staging-agent-kit.md).

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
