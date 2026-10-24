# Terminal

`wezterm/wezterm.lua` is a single self-contained WezTerm configuration for
macOS and Windows. On Windows it opens the first WSL distribution by default.

```bash
make wezterm-preview   # show the link that would be created
make wezterm           # create ~/.config/wezterm/wezterm.lua
```

Where this repository cannot be cloned (the work PC), copy the file to
`%USERPROFILE%\.config\wezterm\wezterm.lua`.

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
