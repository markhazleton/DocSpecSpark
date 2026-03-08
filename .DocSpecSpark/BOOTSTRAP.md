# Bootstrap a New DocSpecSpark Repository

Use this flow when you are ready to turn the planning bundle in `.DocSpecSpark/` into a dedicated `DocSpecSpark` source repository.

## Goal

Create a new repository that contains:

- a Python CLI package for `docspec`
- a single work-product folder at `.DocSpecSpark/`
- a filesystem-backed template library and manifest
- a static site build and publish pipeline
- the planning documents copied into `.DocSpecSpark/planning/`

This is now a working source repository baseline rather than only a seed scaffold.

## Recommended Flow

1. Create a new GitHub repository named `DocSpecSpark`.
2. Clone it locally.
3. Copy the full `.DocSpecSpark/` folder from this repository into the root of the new repository.
4. Run one of the bootstrap scripts from the new repository root:

### PowerShell

```powershell
./.DocSpecSpark/bootstrap-docspecspark.ps1
```

### Bash

```bash
./.DocSpecSpark/bootstrap-docspecspark.sh
```

## What the Script Creates

- `README.md`
- `pyproject.toml`
- `.gitignore`
- `src/docspec_cli/`
- `.DocSpecSpark/`

The script is additive by default. Existing files are left alone unless you pass `--force` to the shell script or `-Force` to the PowerShell script.

## After Bootstrap

Run:

```bash
uv sync
uv run docspec init ../acme-corp-docs --profile small-business-manufacturing
uv run docspec show-constitution --workspace ../acme-corp-docs
uv run docspec create employee-handbook.md --workspace ../acme-corp-docs --overwrite
uv run docspec build --workspace ../acme-corp-docs
uv run docspec publish --workspace ../acme-corp-docs --version 1.0.0
```

That gives you a working source repository plus a downstream company repository scaffold. From there you can iterate on:

1. constitution schema and questionnaire
2. template catalog depth and profile coverage
3. publication polish and site navigation
4. update/install mechanics for target company repositories

## Notes

- The planning documents remain the design reference and are copied into `planning/` for easy access.
- The generated `.DocSpecSpark/config.yaml` is intentionally compact. It is a seed file, not the final constitution model.
- If you want the planning docs copied only once, do not rerun the bootstrap with force enabled.