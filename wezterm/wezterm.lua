-- WezTerm configuration shared by macOS and Windows (WSL).
--
-- Self-contained on purpose: on a machine where this repository cannot be
-- cloned, copying this single file is the whole installation.
--   macOS:   ~/.config/wezterm/wezterm.lua
--   Windows: %USERPROFILE%\.config\wezterm\wezterm.lua

local wezterm = require 'wezterm'
local act = wezterm.action

local config = wezterm.config_builder()

local is_windows = wezterm.target_triple:find('windows') ~= nil
local is_macos = wezterm.target_triple:find('apple') ~= nil

-- Shell ---------------------------------------------------------------------

if is_windows then
  -- Open the first WSL distribution by default; PowerShell stays in the menu.
  local wsl_domains = wezterm.default_wsl_domains()
  for _, domain in ipairs(wsl_domains) do
    if not domain.name:lower():find('docker') then
      config.default_domain = domain.name
      break
    end
  end
  config.launch_menu = {
    { label = 'PowerShell', args = { 'pwsh.exe', '-NoLogo' } },
    { label = 'Windows PowerShell', args = { 'powershell.exe', '-NoLogo' } },
  }
end

-- Appearance ----------------------------------------------------------------

config.color_scheme = 'Tokyo Night'
config.font = wezterm.font_with_fallback { 'JetBrains Mono', 'Menlo', 'Consolas' }
config.font_size = is_macos and 14.0 or 12.0
config.window_padding = { left = 8, right = 8, top = 6, bottom = 6 }
config.window_decorations = is_macos and 'RESIZE' or 'TITLE | RESIZE'
config.use_fancy_tab_bar = false
config.hide_tab_bar_if_only_one_tab = true
config.tab_bar_at_bottom = true
config.scrollback_lines = 20000
config.audible_bell = 'Disabled'

-- Keyboard ------------------------------------------------------------------
--
-- Left Alt/Option is sent to the terminal as Meta (readline, Vim). On macOS the
-- right Option stays a composing key, so a US layout still types ñ and accents.
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = true

-- Every binding below is a letter, so it works the same on US and Spanish
-- layouts: no |, \ or [ that move around between them.
config.leader = { key = 'Space', mods = 'CTRL', timeout_milliseconds = 1000 }

config.keys = {
  -- Panes
  { key = 's', mods = 'LEADER', action = act.SplitVertical { domain = 'CurrentPaneDomain' } },
  { key = 'v', mods = 'LEADER', action = act.SplitHorizontal { domain = 'CurrentPaneDomain' } },
  { key = 'h', mods = 'LEADER', action = act.ActivatePaneDirection 'Left' },
  { key = 'j', mods = 'LEADER', action = act.ActivatePaneDirection 'Down' },
  { key = 'k', mods = 'LEADER', action = act.ActivatePaneDirection 'Up' },
  { key = 'l', mods = 'LEADER', action = act.ActivatePaneDirection 'Right' },
  { key = 'z', mods = 'LEADER', action = act.TogglePaneZoomState },
  { key = 'x', mods = 'LEADER', action = act.CloseCurrentPane { confirm = true } },

  -- Tabs
  { key = 'c', mods = 'LEADER', action = act.SpawnTab 'CurrentPaneDomain' },
  { key = 'n', mods = 'LEADER', action = act.ActivateTabRelative(1) },
  { key = 'p', mods = 'LEADER', action = act.ActivateTabRelative(-1) },

  -- Tools
  { key = 'y', mods = 'LEADER', action = act.ActivateCopyMode },
  { key = 'f', mods = 'LEADER', action = act.Search { CaseInSensitiveString = '' } },
  { key = 'o', mods = 'LEADER', action = act.ShowLauncher },
  { key = 'r', mods = 'LEADER', action = act.ReloadConfiguration },

  -- Pressing the leader twice sends a literal Ctrl+Space to the program.
  { key = 'Space', mods = 'LEADER|CTRL', action = act.SendKey { key = 'Space', mods = 'CTRL' } },
}

for index = 1, 9 do
  table.insert(config.keys, {
    key = tostring(index),
    mods = 'LEADER',
    action = act.ActivateTab(index - 1),
  })
end

return config
