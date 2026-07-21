# MCP Policy

No MCP server is enabled by default.

Before adding one, document:

1. Exact package, command or remote URL, and version pin.
2. Tools exposed by the server.
3. Files, network services, and credentials it can access.
4. Whether each operation is read-only or mutating.
5. Which agent roles may use it.
6. Timeout and failure behavior.
7. How authentication is referenced without entering Git.
8. Removal and incident-response procedure.

Initial candidates should be read-only documentation, analytics, and
observability servers. Generic shell, SSH, wallet, order-placement, unrestricted
database, and production-control MCPs are prohibited.

MCP configuration will be added to `opencode.jsonc` only after this review. Keep
experimental fragments in this directory; OpenCode does not auto-load them.
