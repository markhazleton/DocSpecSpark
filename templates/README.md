# DocSpark Prompt Templates

This directory is the core DocSpark product, a document AI workflow derived from DevSpark.

`templates/commands/` contains the 21 slash-command prompts that drive the document workflow. The remaining files are helper templates used by plans, specs, checklists, and editor configuration.

## Commands

- `constitution.md` through `upgrade.md` adapt the DevSpark workflow surface for document AI work.
- Every command is rewritten for document systems rather than software implementation.
- Installed projects receive these files under `.docspark/defaults/commands/` with the `docspark.` prefix.

## Helper Templates

- `spec-template.md`
- `plan-template.md`
- `tasks-template.md`
- `checklist-template.md`
- `agent-file-template.md`
- `vscode-settings.json`