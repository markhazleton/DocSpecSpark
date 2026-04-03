---
name: "docspark.specify"
description: "Resolve and run the DocSpark specify workflow"
---

## Prompt Resolution

Determine the current git user by running `git config user.name`. Normalize to a folder-safe slug: lowercase, replace spaces with hyphens, strip non-alphanumeric or hyphen characters.

Read and execute the instructions from the first file that exists:
1. `.documentation/{git-user}/commands/docspark.specify.md`
2. `.documentation/commands/docspark.specify.md`
3. `.docspark/defaults/commands/docspark.specify.md`

## User Input

{{input}}