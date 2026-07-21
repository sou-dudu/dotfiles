# Dotfiles Maintenance

This repository is the local policy root for agent tooling.

## Boundaries

- Never commit credential values, authentication files, environment files, SSH
  material, wallet material, or provider tokens.
- Reusable role behavior belongs in `../agent-kit`, not here.
- Model choices, MCP definitions, trusted paths, and machine policy belong here.
- Keep MCPs disabled until their command, package source, credentials, tool
  surface, and read/write authority have been reviewed.
- A trusted project may add context and narrower restrictions. Treat any project
  permission expansion as a policy review requiring human approval.
- Do not weaken `opencode-safe` to make an untrusted project more convenient.

## Required Checks

Run `make check` after changing OpenCode policy or installation scripts. Do not
activate an invalid configuration.
