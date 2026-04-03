# DocSpark Prompt Templates

This directory is the core DocSpark product, a document AI workflow derived from DevSpark.

`templates/commands/` contains the 22 slash-command prompts that drive the document workflow. The remaining files are helper templates used by plans, specs, checklists, editor configuration, and static-site publication scaffolding.

## Commands

- `constitution.md` through `upgrade.md` adapt the DevSpark workflow surface for document AI work.
- `publish.md` adds a publication workflow for building a GitHub Pages-ready documentation site from markdown.
- Every command is rewritten for document systems rather than software implementation.
- Installed projects receive these files under `.docspark/defaults/commands/` with the `docspark.` prefix.

## Helper Templates

- `spec-template.md`
- `plan-template.md`
- `tasks-template.md`
- `checklist-template.md`
- `site-index-template.md`
- `mkdocs-template.yml`
- `github-pages-workflow-template.yml`
- `agent-file-template.md`
- `vscode-settings.json`