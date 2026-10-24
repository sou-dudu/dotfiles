# dotfiles

My workstation as code: the same way of working on macOS and on Windows (WSL),
reproducible on a new machine with one command.

## Tools and why

| Tool | Why |
|---|---|
| **WezTerm** | One config file that works on macOS and Windows, with built-in panes and tabs. [Details](docs/terminal.md) |
| **WSL** | Gives Windows the same Linux shell, Git and tools as the Mac. |
| **Homebrew** | One `Brewfile` lists every package, so a new Mac installs in one step. |
| **Git + GitHub CLI** | Version control and pull requests from the terminal. |
| **OpenCode** | AI agent in the terminal, with a local permission policy and a safe launcher. [Details](docs/opencode.md) |
| **Terraform, kubectl, helm** | Daily infrastructure and CI/CD work. |
| **Tailscale** | Private access to the Mac mini from other devices, with nothing exposed to the internet. |
| **VS Code (Vim keys) + Neovim** *(planned)* | One editing model: VS Code for daily work, Neovim for quick edits. |

## New machine

```bash
git clone https://github.com/sou-dudu/dotfiles.git ~/Projects/dotfiles
cd ~/Projects/dotfiles
./bootstrap.sh          # preview, changes nothing
./bootstrap.sh --apply  # install and link
```

Prerequisites and manual login steps: [docs/new-machine.md](docs/new-machine.md).

## Rules

- Preview first; `--apply` to change anything. Existing files are backed up.
- No secrets in Git: those stay in a password manager.
- Reusable agent prompts live in a separate repository.
