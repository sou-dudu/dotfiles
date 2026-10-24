# iOS development

Everything iOS lives apart from the base setup: `Brewfile.ios` and
`./bootstrap.sh --ios`. Machines that do not use it, including the work setup,
are unaffected.

## Xcode

`./bootstrap.sh --ios --apply` installs Xcode through `mas` (sign in to the App Store first; it is a very large download). Or install it from the App Store by hand. Then point the command line tools at it. This
asks for your password, so it is a manual step:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

Check with `xcodebuild -version`.

## Project layout

Describe the project in a `project.yml` and generate the `.xcodeproj` with
`xcodegen`, so the project file is not hand-edited and diffs stay readable.
`swiftlint` and `swiftformat` keep style consistent; pipe `xcodebuild` through
`xcbeautify` for readable output.

## Build tools for agents: MCP or not

Start without an MCP. An agent can already run `xcodebuild` and the simulator
from the command line, and the Claude desktop app has simulator tools built in.
Add an MCP only if that proves too clumsy.

Candidates, reviewed from public sources and not installed:

| Option | Notes |
|---|---|
| Xcode's built-in MCP (Xcode 26.3+) | Apple's own, exposes project structure, build, tests and documentation. Fewest tools (about 20 in one comparison), smallest review surface. |
| [XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP) | Community project, many more tools (78+ in the same comparison): simulator, device, UI automation. More power, so more to review. |

Before enabling XcodeBuildMCP, check against the policy in `AGENTS.md`:

- the repository to trust: several forks and mirrors exist, so pin the official
  one and a version;
- the install source (Homebrew or npm) and whether it phones home;
- device build and install, and UI automation, are write actions: turn off the
  tool groups that are not needed;
- no credentials should be needed.

Recommendation: try Xcode's built-in MCP first, since it is first-party and
smaller, and keep XcodeBuildMCP for later.
