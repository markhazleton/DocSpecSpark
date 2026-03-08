# DocSpecSpark

DocSpecSpark is the source repository for a document-first framework that initializes company documentation repositories, renders markdown documents from reusable templates, and publishes a static documentation site plus versioned release bundles.

This repository now includes:

- the CLI package in `src/docspec_cli/`
- the framework payload in `.DocSpecSpark/`
- filesystem-backed templates in `.DocSpecSpark/templates/`
- a working build, serve, and publish pipeline for rendered documents
- planning and design material in `.DocSpecSpark/planning/`

The current framework payload now aligns its profile counts to the planning matrix and includes concrete starter catalogs for nonprofit, startup, service, manufacturing, mid-sized enterprise, large enterprise, and healthcare profiles, backed by richer profile-specific constitution tokens.

## Source Repo Workflow

```bash
uv sync
uv run pytest
uv run docspec init ../acme-corp-docs --profile small-business-manufacturing
uv run docspec create employee-handbook.md --workspace ../acme-corp-docs --overwrite
uv run docspec build --workspace ../acme-corp-docs
uv run docspec publish --workspace ../acme-corp-docs --version 1.0.0
```

## What `docspec init` Produces

In a target company repository, the CLI creates:

- `.DocSpecSpark/constitution.yaml`
- `.DocSpecSpark/config.yaml`
- `.DocSpecSpark/templates/` with profile-selected framework templates
- `.DocSpecSpark/documents/` for rendered outputs
- `.DocSpecSpark/site-theme/` and `.DocSpecSpark/releases/`
- `.github/workflows/docspec-publish.yml` for GitHub Pages publication

## Publication Pipeline

- `docspec build` renders `.DocSpecSpark/documents/` into a static site under `site/`
- `docspec serve` previews that site locally
- `docspec publish --version X.Y.Z` builds the site, snapshots it to `.DocSpecSpark/releases/vX.Y.Z/`, and writes a zip bundle to `dist/`

## Repository Layout

```text
.
├── .DocSpecSpark/
│   ├── planning/
│   ├── site-theme/
│   └── templates/
├── src/docspec_cli/
├── tests/
└── pyproject.toml
```

## Current Scope

The source repo now covers the bootstrap path, filesystem-backed templates, target-repo scaffolding, static site generation, release packaging, and a profile-aware template catalog whose per-profile counts match the current planning targets. The broader planning documents still describe future expansion areas such as richer questionnaires, compliance validation, and Microsoft 365 integrations.
