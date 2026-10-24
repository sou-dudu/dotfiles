---
name: commit-message
description: Write Git commit messages in the house format (type, imperative subject, ticket code). Use whenever creating or amending a commit, or when asked for a commit message.
---

# Commit messages

Format of the subject line:

```
<type>: <Imperative verb phrase> (<ticket>)
```

Example: `fix: Retry upload on timeout (ABC-123)`

## Rules

1. **Type** is one of `feat`, `fix`, `docs`, `chore`, followed by a colon and a
   space.
2. **Capital letter** after the colon, then a verb in the **imperative mood**:
   "Add", "Fix", "Remove", never "Added" or "Adds".
3. **Keep it short**: the description (everything between `: ` and the ticket)
   is at most 50 characters. The ticket suffix does not count toward the limit.
4. No period at the end of the subject.
5. Put the **ticket at the end of the subject**, in parentheses.
6. If more explanation is needed, leave a blank line after the subject and add a
   body wrapped at 72 characters. Explain what changed and **why**, not how.
7. One logical change per commit.

## Finding the ticket

- **Work**: use the ticket key from the branch name (for example
  `feature/ABC-123-retry-upload` gives `ABC-123`).
- **Personal projects**: use the GitHub issue number from the branch name or
  from the task being worked on, written as `(#12)`. GitHub links it
  automatically.
- If no ticket can be determined from the branch or the conversation, **ask
  once** instead of inventing one. If the user confirms there is none, omit the
  suffix.

## Do not

- Do not put secrets, credentials or internal URLs in a message.
- Do not add attribution lines unless the environment explicitly requires them.
