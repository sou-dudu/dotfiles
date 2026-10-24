# Terminal

`wezterm/wezterm.lua` is a single self-contained WezTerm configuration for
macOS and Windows. On Windows it opens the first WSL distribution by default.

```bash
make wezterm-preview   # show the link that would be created
make wezterm           # create ~/.config/wezterm/wezterm.lua
```

Where this repository cannot be cloned (the work PC), copy the file to
`%USERPROFILE%\.config\wezterm\wezterm.lua`.

## Icon

The icon is a cat in a terminal window: `wezterm/icon.svg` is the source and
`wezterm/icon.icns` the result. `./bootstrap.sh --apply` sets it on
`/Applications/WezTerm.app` with `fileicon`. A WezTerm upgrade restores the
original icon, so run the bootstrap again to re-apply it. The Dock may need
`killall Dock` to show the change.

To change the design, edit the SVG and run `make wezterm-icon` to rebuild the
`.icns` (needs `swift`, from the Command Line Tools).

## Shortcuts

The leader is `Ctrl+Space`, followed by a letter:

| Key | Action |
|---|---|
| `s` / `v` | split down / right |
| `h j k l` | move between panes |
| `z` | zoom pane |
| `x` | close pane |
| `c` | new tab |
| `n` / `p` | next / previous tab |
| `1`-`9` | jump to tab |
| `y` | copy mode |
| `f` | search |
| `o` | launcher |
| `r` | reload configuration |

They are letters only, so they behave the same on US and Spanish keyboards.

## Prompt

[Starship](https://starship.rs) draws the prompt: the working directory (shortened
to the repository root), the Git branch and status, and the version of a tool
when a project uses it. Its configuration is `starship/starship.toml`, linked to
`~/.config/starship.toml` by `make shell`; `zsh/zshrc` turns it on when
`starship` is installed.

Icons come from a Nerd Font symbol set, which WezTerm bundles as a fallback, so
no extra font is needed there. Other terminals need a Nerd Font.

To try a change, edit the file and open a new terminal.
