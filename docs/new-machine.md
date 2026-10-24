# New Mac

From a factory-fresh Mac to a working setup. Everything except the manual steps
below is done by `bootstrap.sh`.

## 1. Prerequisites

```bash
xcode-select --install
```

Install Homebrew from <https://brew.sh>. `bootstrap.sh` checks for it but does
not install it, so you can read the official installer before running it.

## 2. Clone and preview

```bash
mkdir -p ~/Projects && cd ~/Projects
git clone https://github.com/sou-dudu/dotfiles.git
cd dotfiles
./bootstrap.sh
```

Without arguments the script changes nothing. It lists the Homebrew packages
that are missing or outdated and the links it would create. On a Mac that
already has some of them, `--apply` also upgrades the outdated ones. Existing files are backed up as
`*.backup-<timestamp>`, never deleted.

## 3. Apply

```bash
./bootstrap.sh --apply
```

This installs the `Brewfile` and links the WezTerm, skills, zsh and Git
configuration. An existing `~/.zshrc` is moved aside as `~/.zshrc.backup-<date>`.
Your Git identity stays in `~/.gitconfig`, which is not tracked: set it with
`git config --global user.name` and `user.email`.

### Apps already installed by hand

`brew bundle` refuses to overwrite an app that was installed outside Homebrew.
On a Mac that already has them, let Homebrew take ownership once:

```bash
brew install --cask --adopt claude google-chrome obsidian telegram vlc
```

## 4. Manual steps

These are deliberately not scripted: they involve credentials, and this
repository never stores credential values.

- [ ] Sign in to 1Password and enable its CLI integration.
- [ ] `gh auth login`
- [ ] Sign in to Tailscale (needed to reach this Mac from the iPhone).
- [ ] Sign in to OpenCode providers; the authentication store stays outside Git.
- [ ] Add the machine's SSH key to GitHub. Generate a new key per machine.
- [ ] For `--ios`, sign in to the App Store first: `mas` installs Xcode with
      your Apple ID.
- [ ] Set the keyboard layout and remap Caps Lock to Escape/Ctrl in System
      Settings.

## Not covered yet

- OpenCode policy links (`scripts/install.py`) need the sibling `agent-kit`
  checkout and are installed separately, following
  [staging-agent-kit.md](staging-agent-kit.md).
- tmux and editor configuration are not in the repository yet.

## Work PC (Windows)

Only WezTerm is configured there. Install it with `winget install wez.wezterm`
and copy `wezterm/wezterm.lua` to `%USERPROFILE%\.config\wezterm\wezterm.lua`.
