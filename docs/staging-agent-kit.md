# Staging Agent Kit

The staging account may use only the agent-kit revision recorded in
`locks/agent-kit-staging.json`. The lock records repository identity, exact
commit and Git tree, plus a SHA-256 checksum of the deterministic
`git ls-tree -r -z --full-tree HEAD` output. Validation also hashes the raw
worktree bytes for every tracked regular file and symlink against its HEAD blob,
without Git filters. It rejects unsupported tracked entry types and any
untracked or ignored path without reading those paths.

Issues #139 and #141 remain prerequisites. Preparing or previewing this change
does not activate staging, alter host permissions, or authorize installation.
The current lock has `activation_enabled` set to `false` because the locked
agent-kit change still requires merge and the staging prerequisites are not
complete. Locked apply fails closed while this flag is false; dry-run and source
validation remain available.

## Reviewed update procedure

1. Stop OpenCode for the staging account. Do not change ownership or permissions.
2. Fetch the candidate through the normal administrator-controlled process, then
   review the complete old-to-new SHA diff. Record the exact reviewed commit.
3. Update the lock's repository, commit, tree, and tracked-tree checksum. Keep
   `activation_enabled` false while reviewing every required source. The source
   must ultimately be administrator-owned and read-only to the staging account,
   as must the installed links.
4. In the candidate agent-kit, run
   `python3 scripts/generate_adapters.py --check` and
   `python3 scripts/validate.py`.
5. Validate this repository against that exact checkout, then preview all links:

   ```bash
   AGENT_KIT_HOME=/reviewed/agent-kit make check-source
    python3 scripts/validate.py --source-only \
      --agent-kit /reviewed/agent-kit --lock locks/agent-kit-staging.json \
      --target-home /staging/home
   python3 scripts/install.py --staging --target-home /staging/home \
     --agent-kit /reviewed/agent-kit
   ```

6. Complete #139 and #141 and inspect the staging account's full effective
   OpenCode roles and permissions. Only after all required roles and denials,
   including web search, pass independent review may a new reviewed lock set
   `activation_enabled` to `true`.
7. Obtain explicit approval for that exact lock, source, account, effective
   validation, and link plan. Only an administrator may then repeat the installer
   with `--apply`. This repository does not perform host permission changes.
8. Inspect the staging account's effective OpenCode roles and permissions before
   restart by running the full validation without `--source-only` and with the
   same `--target-home`; this makes OpenCode resolve configuration from staging,
   not the administrator's home. Coordinator, explorer, implementer, reviewer,
   tester, researcher, ops-observer, and decision-auditor must all resolve. The
   auditor must deny edit, shell, task, external-directory, web-fetch, and
   web-search access. Restart OpenCode only after they match the review.
9. If validation or effective policy differs, stop OpenCode, restore the backed-up
   links and prior locked source, inspect the effective roles again, and restart
   only after rollback is confirmed.

Dotfiles secret-marker validation reads only tracked regular files and never
follows tracked symlinks. Keep the reviewed source inaccessible for staging
writes as an additional host control.
