# Git identities

One Git configuration, two identities: personal by default, work for every
repository under `~/work`. No email address is stored in this repository.

## How it works

`git/config` (linked to `~/.config/git/config`) holds the shared settings and
the rules:

```ini
[include]
	path = ~/.config/git/identity-personal
[includeIf "gitdir:~/work/"]
	path = ~/.config/git/identity-work
```

The two `identity-*` files are local and untracked. Copy the examples and fill
them in:

```bash
cp git/identity-personal.example ~/.config/git/identity-personal
cp git/identity-work.example ~/.config/git/identity-work
```

Use the GitHub noreply address for the personal identity
(`<id>+<username>@users.noreply.github.com`, shown in GitHub under Settings,
Emails), and turn on "Block command line pushes that expose my email".

`user.useConfigOnly = true` makes Git refuse to commit when no identity
matches, instead of guessing one from the hostname.

## Check it

```bash
git config user.email     # run inside a repository
```

Run it once under `~/work` and once elsewhere.

## Pitfall: `~/.gitconfig` wins

Git reads `~/.config/git/config` first and `~/.gitconfig` after it, and the last
value wins. A `[user]` section left in `~/.gitconfig` therefore overrides the
work identity everywhere. Remove it and keep identity only in the two files
above.

## Work machine

Keep every work repository under `~/work` (inside WSL, in the Linux home, not on
`/mnt/c`). If work repositories live elsewhere, change the `gitdir:` path, or
switch to matching on the remote URL, which needs Git 2.36 or newer:

```ini
[includeIf "hasconfig:remote.*.url:git@github.com:company/**"]
	path = ~/.config/git/identity-work
```

## Credentials

GitHub over HTTPS authenticates with the GitHub CLI token, so Git and `gh` share
one credential and nothing else is stored:

```ini
[credential "https://github.com"]
	helper =
	helper = !gh auth git-credential
```

The empty `helper =` clears the `osxkeychain` helper that Homebrew's Git enables
system-wide. That helper ties the stored password to the Git binary, so macOS can
ask for the login keychain password again after every `brew upgrade git`.

Set it up once per machine, including inside WSL:

```bash
gh auth login
```

Check it without any prompt (it must list refs of a repository you can access):

```bash
GIT_TERMINAL_PROMPT=0 git ls-remote origin
```

An old `github.com` entry may remain in the macOS keychain; it is no longer used
and can be deleted from Keychain Access.

## Not covered here

Per-identity SSH keys and commit signing.
