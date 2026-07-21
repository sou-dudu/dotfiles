# Policy Model

## Trust Layers

1. `agent-kit` supplies reusable behavior and conservative role permissions.
2. This repository supplies models, machine policy, trusted roots, and MCP review.
3. A trusted project supplies its architecture and may narrow permissions.
4. The operating-system account remains the final credential boundary.

OpenCode merges global and project configuration. The `opencode-safe` launcher
therefore disables project configuration unless the repository root appears in
`opencode/trusted-projects`. Trust means the project's agent configuration has
been reviewed; it does not make prompts an operating-system sandbox.

Untrusted launches also disable automatic external skill scans. Global skill
invocation is deny-by-default with a named allowlist for the agent kit and the
OpenCode configuration skill.

## Model Assignment

`openai/gpt-5.6-sol` is assigned to coordination, research, independent review,
and decision auditing. Reusable role definitions intentionally contain no model
IDs, so a different machine can choose different models without modifying the
agent kit.

The decision auditor has temperature zero, no shell, no edits, no network fetch,
no external-directory access, and no subdelegation. Those restrictions support
its intended veto, abstain, and shadow-evaluation role. They do not yet connect it
to any production decision system.

## Human Approval

Human approval remains required for deployment, merge, publication, production
writes, secrets, financial actions, destructive operations, and permission
changes. A coding agent may prepare such a change but may not execute it.

## Limits

Repository configuration can override agent-level configuration in trusted
projects. Strong isolation requires a separate operating-system user or sandbox
without production credentials. This repository reduces accidental authority; it
does not claim to be a complete security boundary.
