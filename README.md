# DocSpark

DocSpark is a document AI tool derived from DevSpark.

It gives AI assistants a repeatable workflow for creating, reviewing, evolving, and publishing documentation systems using plain markdown prompts plus lightweight bootstrap tooling. The product is the prompt and template set. The CLI is optional automation for installing that set into a target repository.

## What's In This Repo

```text
docspark/
├── examples/             ← Reference post-install document repositories
├── templates/            ← 21 document workflow prompts + helper templates
├── scripts/              ← Context-gathering helper scripts (PowerShell + Bash)
├── quickstart/           ← Agent-specific bootstrap prompts
├── src/docspark_cli/     ← Optional CLI for automated setup
└── .documentation/       ← Guides and the starter constitution
```

## Get Started

Option A — Agent Quickstart

Point your AI assistant at one of the quickstart prompts:

- [quickstart/docspark_quickstart_copilot.md](quickstart/docspark_quickstart_copilot.md)
- [quickstart/docspark_quickstart_claudecode.md](quickstart/docspark_quickstart_claudecode.md)
- [quickstart/docspark_quickstart_cursor.md](quickstart/docspark_quickstart_cursor.md)
- [quickstart/docspark_quickstart_generic.md](quickstart/docspark_quickstart_generic.md)

Option B — CLI

```bash
uv tool install docspark-cli --from git+https://github.com/markhazleton/docspark.git
docspark init my-docs-repo
docspark init --here --ai copilot
```

## DocSpark Model

As a document AI tool derived from DevSpark, DocSpark follows the same separation-of-concerns model:

```text
.docspark/                ← Installed stock assets, safe to replace on upgrade
├── defaults/commands/
├── scripts/
├── templates/
└── VERSION

.documentation/           ← User-owned artifacts, never framework-managed
├── memory/constitution.md
├── specs/
├── commands/
├── decisions/
└── docspark.json
```

Prompt resolution order:

1. `.documentation/{git-user}/commands/`
2. `.documentation/commands/`
3. `.docspark/defaults/commands/`

Script resolution order:

1. `.documentation/scripts/{bash|powershell}/`
2. `.docspark/scripts/{bash|powershell}/`

## Slash Commands

Core workflow:

- `/docspark.constitution`
- `/docspark.specify`
- `/docspark.plan`
- `/docspark.tasks`
- `/docspark.implement`

Constitution-powered workflows:

- `/docspark.pr-review`
- `/docspark.site-audit`
- `/docspark.quickfix`
- `/docspark.critic`
- `/docspark.release`
- `/docspark.harvest`
- `/docspark.evolve-constitution`
- `/docspark.repo-story`

Quality and personalization:

- `/docspark.clarify`
- `/docspark.analyze`
- `/docspark.checklist`
- `/docspark.personalize`
- `/docspark.discover-constitution`
- `/docspark.archive`
- `/docspark.upgrade`
- `/docspark.taskstoissues`

## Prerequisites

- Any OS
- A supported AI coding assistant
- Git recommended
- `uv` plus Python 3.11+ only if using the CLI

## Development

```bash
uv sync
uv run pytest
uv run docspark init .tmp-docs --ai copilot --shell powershell
```

## Examples

See [examples/README.md](examples/README.md) for reference repositories that show what DocSpark looks like after installation in a document-centric project.

See [templates/README.md](templates/README.md) and [.documentation/quickstart.md](.documentation/quickstart.md) for the workflow details.
