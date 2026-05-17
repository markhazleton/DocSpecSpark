# Implementation Plan: DocSpark Book Publishing System

**Target repo**: `github.com/markhazleton/docspecspark`  
**Local path**: `c:\GitHub\MarkHazleton\DocSpecSpark`  
**Date**: 2026-05-17  
**Last Reviewed**: 2026-05-17 (second review)  
**Status**: Active — V1 CLI milestone in progress  
**Changelog**: [plan-changelog.md](plan-changelog.md)

---

## Summary

DocSpark is a first-class publishing solution created and maintained in this repository. It currently ships as the `docspark-cli` Python/Typer CLI plus prompt templates for repeatable documentation workflows. The book publishing assets under `.documentation/books/` provide the foundation for the next product layer: manifest-driven book composition, Pandoc EPUB/PDF rendering, artifact validation, book critique prompts, rewrite-plan prompts, scoring scripts, review outputs, sample books, and published artifacts.

This plan evolves DocSpark into a full-featured, local-first book publishing system without throwing away the current architecture. The implementation should extend:

- `src/docspark_cli/` for CLI commands and packaged workflow installation.
- `templates/commands/` for AI assistant commands.
- `templates/` for reusable book manifests, editorial templates, validation checklists, and publication scaffolding.
- `scripts/` for cross-platform helper scripts.
- `.documentation/` for product documentation and MkDocs publishing.
- `tests/` for CLI, template, manifest, composition, and workflow coverage.

The goal is not to create a separate TypeScript monorepo. The goal is to make DocSpark the first-class publishing solution owned by this repo.

## Current Repo Baseline

DocSpark currently includes:

- Python package: `docspark-cli`.
- CLI entry point: `docspark = docspark_cli:main`.
- Main CLI file: `src/docspark_cli/cli.py`.
- Existing commands: `init`, `uninstall`, `status`, `list-assets`.
- Stock prompt commands installed under `.docspark/defaults/commands/`.
- User-owned work installed under `.documentation/`.
- Agent shims installed under `.github/agents/` and `.github/prompts/`.
- Cross-platform helper scripts under `scripts/bash/` and `scripts/powershell/`.
- MkDocs site sourced from `.documentation/`.
- Tests covering install, status, uninstall, gitignore behavior, and examples.

The naming boundary is:

- Repo and site: `DocSpecSpark`.
- CLI and installed framework names: `docspark`, `.docspark`, `DocSpark`.

This plan treats DocSpark as the publishing product created and maintained in the DocSpecSpark repository. The `docspark` CLI and `.docspark` installed asset root are canonical in V1.

## In-Repo Publishing Assets Reviewed

The `.documentation/books/` corpus includes several distinct assets that should be promoted into the product:

| Source | What It Provides | Plan Impact |
|---|---|---|
| `.documentation/books/docs/spec.md` | Requirements for a Markdown-to-EPUB/PDF book pipeline | Seed functional requirements and acceptance criteria |
| `.documentation/books/docs/plan.md` | Node/Pandoc implementation decisions and critic mitigations | Preserve lessons: no manual TOC, explicit PDF engine, max buffer, path validation |
| `.documentation/books/docs/tasks.md` | Completed implementation checklist for the existing book pipeline | Convert into implementation backlog for this repo |
| `.documentation/books/docs/data-model.md` | Book, chapter, article, compiled book, and output models | Convert into Python dataclasses or Pydantic models |
| `.documentation/books/docs/contracts/cli-contract.md` | CLI behavior and `book.yaml` contract | Become the first `docspark book` command contract |
| `.documentation/books/docs/quickstart.md` | Pandoc/LaTeX setup and build walkthrough | Become user docs and installed quickstart asset |
| `.documentation/books/scripts/build-book.mjs` | Working composition/render implementation | Port behavior into Python, or package as temporary legacy adapter |
| `.documentation/books/scripts/validate-book.mjs` | Artifact validation behavior | Port into Python validation command |
| `.documentation/books/scoring/*.py` | Parse, score, dashboard, remediation, rewrite tooling | Refactor into optional book quality module |
| `.documentation/books/*book-critique.md` | Full-book critique command design | Adapt into `docspark.book-critique` prompt |
| `.documentation/books/*book-rewrite-plan.md` | Rewrite-plan command design | Adapt into `docspark.book-rewrite-plan` prompt |
| `.documentation/books/*/book.yaml` | Real sample manifests | Use as fixtures and examples |
| `.documentation/books/*/chapters/*.md` | Real chapter corpus | Use as non-packaged test/example content |
| `.documentation/books/publish/*` | Generated EPUB/PDF outputs | Keep out of packaged defaults; use only as reference artifacts |

## Product Vision

DocSpark should let an author or AI assistant create, review, revise, render, validate, and release long-form books from Markdown source files.

The system should support two book creation paths:

1. **Book-native authoring**: Create a portable book workspace with `book.yaml`, chapters, editorial guidelines, decisions, reviews, and release notes.
2. **Documentation-to-book harvesting**: Select existing Markdown documents from a documentation repo and compose them into a structured book without exposing book-only chapters on the website.

The publishing system should be local-first. Manuscripts live on disk, outputs are reproducible, AI assistance is optional and auditable, and final writes remain under author control.

## Product Principles

- **Build on this repo**: Extend the existing Python CLI, templates, docs, and tests. DocSpark publishing is created and maintained here.
- **Local-first source ownership**: Markdown and YAML files remain the source of truth.
- **Manifest-driven books**: `book.yaml` defines book metadata, ordering, roles, outputs, and lifecycle state.
- **Portable workspaces**: A book can live inside a target repo, inside `.documentation/books/`, or in an explicit external path. Paths in `book.yaml` are relative to the book root directory.
- **Explicit paths**: Commands accept a book path or slug. They should not depend on hidden current-directory assumptions.
- **AI as review assistant**: Prompt workflows critique, plan, and suggest changes; they do not silently rewrite or publish.
- **Auditable outputs**: Composed Markdown, reviews, scores, and release checklists should be traceable to source content hashes.
- **Reproducible builds**: EPUB/PDF outputs should be regenerated from source with documented prerequisites.
- **No duplicate TOC/title artifacts**: Pandoc or the selected renderer owns generated TOC and title-page behavior.
- **Progressive enhancement**: Core build and validation must work without LLM credentials.

## Non-Goals For V1

- Public cloud CMS.
- Multi-user real-time editing.
- Automatic KDP upload or external bookstore publication.
- Fully autonomous book writing.
- Requiring Anthropic, OpenAI, or any specific model provider for core build workflows.
- A heavy desktop editor or thick web client.
- Replacing `.docspark` and `.documentation` install semantics.
- A .NET API or browser client (deferred to Phase 10–11).

## Target Users

- Technical authors turning documentation, articles, or project notes into books.
- AI-assisted writing workflows that need repeatable critique and rewrite planning.
- Documentation maintainers publishing internal handbooks, guides, or long-form reports.
- Editors reviewing book-length Markdown manuscripts.
- Developers who want reproducible EPUB/PDF output from source-controlled content.

## Target User Workflows

### Workflow 1 - Create A New Book

1. Run `docspark book init my-book`.
2. Edit `my-book/book.yaml`, `overview.md`, `audience.md`, `editorial-guidelines.md`, and chapter files.
3. Run `docspark book validate my-book`.
4. Run `docspark book compose my-book`.
5. Run `docspark book build my-book`.
6. Review `my-book/dist/book.epub` and `my-book/dist/book.pdf`.

### Workflow 2 - Import Existing Book Material

1. Run `docspark book import .documentation/books/project-mechanics ./books/project-mechanics`.
2. Convert `book.yaml` into the supported DocSpark schema if needed.
3. Copy chapters, cover images, editorial notes, and reviews.
4. Produce an import report with unsupported fields and assumptions.
5. Validate and build the imported book.

### Workflow 3 - Critique And Rewrite Plan

1. Run a prompt workflow or CLI helper to inspect a book manifest and chapter sources.
2. Produce a full-book critique under `reviews/`.
3. Convert the critique into a rewrite plan with file-specific tasks.
4. Apply approved edits manually or through an AI assistant.
5. Rebuild, rescore, and revalidate.

### Workflow 4 - Release Candidate

1. Run `docspark book release-check <book-path>`.
2. Confirm manifest metadata, rendered outputs, proofing notes, stale scores, and validation status.
3. Generate release notes.
4. Tag or archive the release artifacts according to the target repo policy.

## Proposed Repo Structure

The implementation should fit the existing repo layout:

```text
DocSpecSpark/
  src/
    docspark_cli/
      cli.py
      book/
        __init__.py
        commands.py
        manifest.py
        paths.py
        compose.py
        render.py
        validate.py
        score.py
        importers.py
        release.py

  templates/
    commands/
      docspark.book-init.md
      docspark.book-critique.md
      docspark.book-rewrite-plan.md
      docspark.book-proof.md
      docspark.book-release.md
    book/
      book.yaml
      overview.md
      audience.md
      editorial-guidelines.md
      outline.md
      chapters/
        00-introduction.md
      reviews/
        README.md
      decisions/
        README.md
      release-notes/
        README.md

  scripts/
    powershell/
      build-book.ps1
      book-context.ps1
    bash/
      build-book.sh
      book-context.sh

  examples/
    sample-book/
      book.yaml
      chapters/
      cover.png
      .docspark/
        defaults/commands/
        templates/book/
      .documentation/
        memory/constitution.md
        books/sample-book/
      README.md

  .documentation/
    book-publishing.md
    book-quickstart.md
    book-manifest.md
    book-review-workflow.md
    plan.md
    plan-changelog.md

  tests/
    fixtures/
      minimal-book/
      legacy-book/
      hostile-paths/
    test_book_manifest.py
    test_book_compose.py
    test_book_cli.py
    test_book_install_assets.py
```

Future phases (10–11) will add `services/DocSpark.BookApi/` and `apps/book-studio/` once the V1 CLI is published.

The existing `.documentation/books/` corpus should be treated as in-repo DocSpark publishing source material during implementation. Product assets should be promoted deliberately into `templates/`, `examples/`, `scripts/`, and `src/docspark_cli/book/`.

## Application Architecture

### V1 Architecture: Python CLI Only

The V1 application architecture is the Python CLI. All book commands run as `docspark book <command>` subcommands of the existing Typer app. There is no API server, no browser client, and no second language runtime in V1.

The CLI owns:

- Manifest loading and validation.
- Path resolution and traversal rejection.
- Composition of `dist/book.md`.
- Pandoc EPUB/PDF rendering via subprocess.
- Artifact validation.
- Rule-based scoring.
- Release checklist generation.
- Context packet preparation for AI critique prompts.

All file writes go directly to the book workspace on disk. The author controls commits.

### Future Architecture: .NET API + Thin Client (Post-V1, Gated On Published V1 CLI)

*This section records the intended future architecture. It is NOT in scope for the V1 CLI milestone (Phases 0–9) or the 0.2.0 release. Implementation begins only after `docspark book build` and `docspark book score` are proven and published.*

The future architecture adds a browser-based authoring surface backed by a local .NET Minimal API. The UI is a thin client that owns only presentation — all file writes, LLM calls, manifest validation, and rendering remain in the API or CLI.

#### Thin Client Responsibilities

- Open or create a book workspace.
- Display manifest metadata, outline, chapter status, review state, proofing notes, and release readiness.
- Edit chapter Markdown and manifest fields through API calls.
- Show rendered preview or composed manuscript preview returned by the API.
- Request critique, rewrite planning, scoring, and LLM suggestions through the API.
- Present diffs and require explicit author approval before source writes.
- Show build, render, validation, and LLM progress from API events.

#### Future .NET Minimal API Responsibilities

- Enforce workspace path boundaries and reject traversal.
- Persist book assets: manifest, chapters, appendices, assets, decisions, reviews, release notes, proofing notes, generated state, and backups.
- Own LLM provider configuration, secret loading, request construction, response validation, and audit logging.
- Prevent secrets, `.env` files, generated binaries, and unrelated workspace files from entering LLM context.
- Provide endpoints for manifest validation, composition, rendering, scoring, critique, rewrite-plan generation, proofing notes, and release checks.
- Maintain `.docspec/` state such as content hashes, LLM session records, score history, page/proofing metadata, and generated previews.
- Invoke `docspark book` CLI commands where that is the least risky first implementation path.
- Bind to `127.0.0.1` by default. Never expose book workspaces as a public service.

#### Future API Endpoint Sketch

```text
GET    /health
POST   /workspaces/open
POST   /books/init
GET    /books/{bookId}
PUT    /books/{bookId}/manifest
GET    /books/{bookId}/outline
PUT    /books/{bookId}/outline
GET    /books/{bookId}/chapters/{chapterId}
PUT    /books/{bookId}/chapters/{chapterId}
POST   /books/{bookId}/validate
POST   /books/{bookId}/compose
POST   /books/{bookId}/build
POST   /books/{bookId}/score
POST   /books/{bookId}/llm/critique
POST   /books/{bookId}/llm/rewrite-plan
POST   /books/{bookId}/llm/suggest-rewrite
GET    /books/{bookId}/reviews
POST   /books/{bookId}/proofing/notes
PUT    /books/{bookId}/proofing/notes/{noteId}
POST   /books/{bookId}/release-check
GET    /operations/{operationId}
GET    /operations/{operationId}/events
```

Long-running operations should expose progress through polling first, SSE when the API is stable. Decide in Phase 10.

## Installed Workspace Structure

When a user runs `docspark init`, book publishing support should install stock assets alongside the existing documentation workflow:

```text
target-repo/
  .docspark/
    defaults/
      commands/
        docspark.book-init.md
        docspark.book-critique.md
        docspark.book-rewrite-plan.md
        docspark.book-proof.md
        docspark.book-release.md
    templates/
      book/
        book.yaml
        overview.md
        audience.md
        editorial-guidelines.md
        outline.md
        chapters/00-introduction.md
    scripts/
      powershell/build-book.ps1
      bash/build-book.sh

  .documentation/
    books/
      .gitkeep
    memory/
      constitution.md
```

Generated outputs should be gitignored by default:

```text
.documentation/books/**/dist/
.documentation/books/**/.docspec/
books/**/dist/
books/**/.docspec/
```

The final gitignore pattern should be chosen carefully so source chapters and manifests are not ignored.

## Book Workspace Structure

DocSpark should support this portable book workspace. All paths within `book.yaml` are relative to the book root directory (the directory containing `book.yaml`):

```text
my-book/
  book.yaml
  overview.md
  audience.md
  editorial-guidelines.md
  outline.md
  assets/
    cover.png
  chapters/
    00-introduction.md
    01-first-chapter.md
  appendices/
    appendix-a-reference.md
  decisions/
    2026-05-17-book-promise.md
  reviews/
    2026-05-17_book-critique.md
    2026-05-17_rewrite-plan.md
  release-notes/
    0.1.0.md
  .docspec/
    chapter-map.json
    score-history.json
    llm-sessions/
    rendered-pages/
    proofing-notes.json
    release-checklist.json
  dist/
    book.epub
    book.pdf
```

For compatibility with the existing in-repo book assets, the importer should also understand paths such as:

```text
books/<slug>/book.yaml
books/<slug>/book.md
books/<slug>/chapters/
books/publish/<slug>/book.epub
books/publish/<slug>/book.pdf
books/reviews/
books/scoring/
```

## CLI Error And Progress Contract

All `docspark book` commands MUST follow this output format to ensure consistent logging and testability.

### Standard Output (progress, success path)

One line per major step, prefixed with `[docspark-book]`:

```text
[docspark-book] Validating manifest: my-book/book.yaml
[docspark-book] Composing chapter 1/5: "Introduction"
[docspark-book] Writing my-book/dist/book.md
[docspark-book] Rendering EPUB3...
[docspark-book] Rendering PDF (xelatex)...
[docspark-book] Validating artifacts...
[docspark-book] Done. Output: my-book/dist/book.epub, my-book/dist/book.pdf
```

### Standard Error (failure path)

Human-readable messages to `stderr`, one per failure:

```text
Error [manifest]: book.yaml not found at my-book/book.yaml
Error [manifest]: Minimum 2 chapters required. Found: 1.
Error [compose]: Chapter source not found: chapters/missing.md
Error [compose]: Chapter body is empty: chapters/01-intro.md
Error [render]: Pandoc not found. Install from https://pandoc.org/installing.html
Error [render]: Pandoc version 2.14 is below the minimum supported version (2.19).
Error [render]: Pandoc rendering failed for format "pdf" (xelatex not found).
Error [validate]: EPUB not found at my-book/dist/book.epub
Error [path]: Path traversal rejected: ../../../etc/passwd
```

### Exit Codes

| Code | Meaning                                                 |
|------|---------------------------------------------------------|
| `0`  | All requested operations succeeded                      |
| `1`  | Any validation, composition, rendering, or path failure |
| `2`  | Usage error (bad arguments, missing required argument)  |

### Pandoc Version Policy

- Minimum supported version: **2.19**.
- Versions below 2.19 produce a warning and the build continues.
- Versions below 2.11 abort with `Error [render]: Pandoc version X.Y is too old to produce valid EPUB3 output.`
- The `build` command logs the detected Pandoc version in the progress output.
- Tested version range: 2.19–3.x. Behavior on Pandoc 4.x is untested and should warn.

---

## Path Resolution Contract

**V1 path convention**: Paths in `book.yaml` are relative to the **book root directory** (the directory containing `book.yaml`). This makes workspaces portable — a book can be moved, copied, or symlinked without breaking source paths.

**Example**: If `book.yaml` is at `my-book/book.yaml` and a chapter is at `my-book/chapters/01-intro.md`, the manifest entry is:

```yaml
source: chapters/01-intro.md
```

Not `my-book/chapters/01-intro.md` and not an absolute path.

**Importer behavior**: The `docspark book import` command MUST convert repo-root-relative paths from legacy `book.yaml` files (e.g., `books/devspark-complete-guide/chapters/01.md`) into book-root-relative paths (e.g., `chapters/01.md`) when copying the chapter files into the new workspace.

**Cover image**: The `cover_image` field is also resolved relative to the book root.

**Traversal rejection**: Any resolved path that escapes the book root directory is rejected with `Error [path]: Path traversal rejected`.

---

## Manifest Contract

The initial supported manifest should be compatible with the proven `book.yaml` reference format while adding lifecycle metadata where useful.

```yaml
schema: "docspark/book/v1"
title: "Example Book"
subtitle: "A Practical Guide"
author: "Author Name"
version: "0.1.0"
description: "A concise description of the book."
language: "en"
cover_image: "assets/cover.png"
publisher: ""
rights: ""
identifier: ""
date: "2026-05-17"
subjects:
  - Technical Writing

lifecycle:
  status: draft
  editorial_owner: "Author Name"
  last_reviewed: null

output:
  formats:
    - epub
    - pdf
  pdf:
    trim: "7x9.25"
    engine_order:
      - xelatex
      - lualatex
      - pdflatex
      - typst
  epub:
    cover_image: "assets/cover.png"

frontmatter:
  - source: chapters/00-foreword.md
    title: "Foreword"
    role: foreword

chapters:
  - source: chapters/01-first-chapter.md
    title: "First Chapter"
    number: "1"
    status: draft
    promise: "What the reader understands after this chapter."

appendices:
  - source: appendices/appendix-a-reference.md
    title: "Reference"
```

Compatibility rules:

- Existing manifests without `schema` and `lifecycle` are accepted in legacy-compatible mode. Legacy mode is triggered when `schema:` is absent and `title`, `author`, and `chapters` are all present.
- New manifests should include `schema: docspark/book/v1`.
- `book.yaml` remains the required filename. Do not introduce `book.yml` unless explicitly requested later.

### Book-Only Chapter Flag

Chapter source files may carry a `book_only: true` frontmatter flag to mark them as exclusively intended for book publication — they should never appear in a documentation website index or sitemap. The `compose` command reads this flag and includes the chapter unconditionally. External website generators (MkDocs, static site tools) are responsible for respecting it; DocSpark only sets and documents the convention.

When a chapter file has `book_only: true`, the `compose` command emits a progress note:

```text
[docspark-book] Composing chapter 2/4: "Book-Only Chapter" (book_only)
```

This enables Workflow 2 (documentation-to-book harvesting): authors mark website-only documents normally and mark book-only bridge chapters with `book_only: true`.

### Parts — V1 Decision: Deferred

`parts:` is present in the manifest schema for forward-compatibility but is **not implemented in V1**. The V1 `compose` command uses a flat `chapters:` array only. Authors who want visual part breaks in V1 should add a part-header chapter file with no body (a stub chapter whose title becomes the part heading).

The in-repo `devspark-complete-guide/book.yaml` uses inline YAML comments (not a `parts:` structure) to group chapters — this is the correct V1 pattern.

When `parts:` is implemented (post-V1), the `compose` command will render part headers as `##` headings so they appear in the Pandoc-generated TOC under the book title. A two-part book would produce this composed output:

```markdown
# Book Title

## Part I: Foundations

### Chapter 1: First Chapter

{chapter body}

## Part II: Advanced Topics

### Chapter 2: Second Chapter

{chapter body}
```

Until `parts:` is implemented, `docspark book validate` will emit a warning if `parts:` is present in `book.yaml` and ignore it, falling back to `chapters:`.

## Lifecycle Model

### Book Status

- `concept`
- `outline`
- `draft`
- `review`
- `revision`
- `proof`
- `release-candidate`
- `published`

### Chapter Status

- `idea`
- `outline`
- `draft`
- `reviewed`
- `revision`
- `proofed`
- `released`
- `deferred`

### Lifecycle Phases

1. Concept and positioning
2. Outline and architecture
3. Drafting
4. Composition
5. Scoring and critique
6. Rewrite planning
7. Assisted or manual revision
8. EPUB/PDF rendering
9. Artifact validation and page proofing
10. Release candidate
11. Post-publication maintenance

## Functional Requirements

### Project And Installation

- **FR-001**: `docspark init` MUST install book workflow prompts, templates, and helper scripts.
- **FR-002**: Book assets MUST follow the same stock/user ownership model as existing DocSpark assets: `.docspark` is framework-managed, `.documentation` is user-owned.
- **FR-003**: Existing DocSpark commands and tests MUST continue to work.
- **FR-004**: The CLI MUST preserve `docspark` command compatibility.

### Book Workspace

- **FR-005**: The system MUST create a new book workspace from packaged templates.
- **FR-006**: The system MUST validate `book.yaml` against the supported schema.
- **FR-007**: The system MUST support existing book manifests from `.documentation/books/*`.
- **FR-008**: The manifest MUST be the source of truth for book order and metadata.
- **FR-009**: The manifest MUST support frontmatter, chapters, appendices, custom chapter labels, and per-chapter status. `parts:` is accepted but ignored in V1 with a warning.
- **FR-010**: Commands MUST accept explicit book paths. Slug shortcuts may be supported only when unambiguous.

### Composition

- **FR-011**: The system MUST compose source Markdown files into a generated manuscript.
- **FR-012**: YAML frontmatter MUST be stripped from chapter bodies during composition while remaining available for title fallback and metadata.
- **FR-013**: Chapter title resolution MUST prefer manifest title, then source frontmatter title, then filename.
- **FR-014**: Empty chapter bodies MUST be reported as a warning; the chapter is skipped and the build continues.
- **FR-015**: Missing chapter sources MUST fail validation before rendering.
- **FR-016**: The composed manuscript MUST not include a manual table of contents when the renderer generates one.
- **FR-017**: Generated manuscript is written to `dist/book.md` and is gitignored by default.

### Rendering

- **FR-018**: The system MUST render EPUB3 and PDF outputs when requested.
- **FR-019**: Rendering MUST be adapter-based so Pandoc is isolated from the domain model.
- **FR-020**: Pandoc rendering MUST use argument arrays, not shell-concatenated commands.
- **FR-021**: PDF engine resolution MUST prefer Unicode-capable engines: `xelatex`, `lualatex`, `pdflatex`, then `typst`.
- **FR-022**: Rendering MUST support cover image, language, title, subtitle, author, publisher, rights, identifier, date, and subject metadata.
- **FR-023**: Rendering MUST stream or capture enough output to avoid buffer failures on verbose LaTeX builds.

### Validation

- **FR-024**: Validation MUST check manifest shape, unsupported fields, source file existence, duplicate numbering, missing assets, output formats, and minimum chapter count.
- **FR-025**: EPUB validation MUST inspect basic EPUB structure and use `epubcheck` when installed.
- **FR-026**: PDF validation MUST check existence, minimum size, PDF header, and page count when `pdfinfo` or a fallback is available.
- **FR-027**: Validation MUST produce human-readable errors with actionable fixes following the CLI error contract.

### Review And Scoring

- **FR-028**: The system SHOULD parse book chapters into a structured chapter index with content hashes.
- **FR-029**: The system SHOULD support scoring dimensions: narrative arc, argument quality, clarity, signal ratio, structure, voice, evidence density, and book fit.
- **FR-030**: Scores MUST be tied to content hashes and marked stale when source content changes.
- **FR-031**: LLM scoring MUST be optional and disabled cleanly when no API key is configured.
- **FR-032**: Review outputs MUST be written under the book workspace, not mixed into global directories unless explicitly configured.

### Prompt Workflows

- **FR-033**: The system MUST include a full-book critique prompt installed as `docspark.book-critique.md`.
- **FR-034**: The system MUST include a rewrite-plan prompt installed as `docspark.book-rewrite-plan.md`.
- **FR-035**: Book prompt commands MUST resolve manifest, source chapters, generated manuscript, constitution, and editorial guidelines.
- **FR-036**: Prompt outputs MUST require file-specific actions, acceptance criteria, and validation steps.
- **FR-037**: Prompt workflows MUST not invent missing evidence; blocked decisions must be explicit.

### Thin Client And .NET API *(Future Architecture — Not V1)*

These requirements apply only after the V1 CLI milestone (0.2.0) is published.

- **FR-038**: The system SHOULD provide a thin client for book creation, outline management, chapter editing, review, proofing, and release workflows.
- **FR-039**: The thin client MUST call a .NET Minimal API for durable operations instead of writing book files directly.
- **FR-040**: The .NET Minimal API MUST own LLM calls, provider configuration, secret access, context construction, response validation, and audit logging.
- **FR-041**: The .NET Minimal API MUST persist book assets including manifests, chapters, appendices, assets, reviews, decisions, release notes, proofing notes, backups, and `.docspec/` generated state.
- **FR-042**: The .NET Minimal API MUST expose progress for long-running build, render, validation, scoring, and LLM operations.
- **FR-043**: The thin client MUST require explicit author approval before applying LLM-generated changes to source files.
- **FR-044**: The API SHOULD initially invoke `docspark book` CLI commands for build and validation workflows where that reduces duplication.

### Safety And Path Handling

- **FR-045**: Path resolution MUST reject traversal outside the selected book workspace and explicitly allowed source roots.
- **FR-046**: The renderer MUST reject cover image paths outside allowed roots.
- **FR-047**: Any source rewrite helper MUST create recoverable backups before modifying manuscript files.
- **FR-048**: The system MUST not send `.env`, secrets, unrelated workspace files, or generated binaries to an LLM.
- **FR-049**: The system MUST never auto-commit, auto-push, or externally publish in V1.

### Release Management

- **FR-050**: The system MUST generate a release checklist.
- **FR-051**: Release checks MUST verify successful validation, current composed manuscript, current scores when scoring is enabled, and unresolved proofing notes.
- **FR-052**: The system SHOULD generate release notes from manifest metadata, decisions, review summaries, and changed chapters.
- **FR-053**: A book release MUST be reproducible from source and documented prerequisites.

## Non-Functional Requirements

- **NFR-001**: Core workflows must run without an LLM key.
- **NFR-002**: CLI commands must work on Windows, macOS, and Linux.
- **NFR-003**: File writes must be deterministic and testable.
- **NFR-004**: External tools must be checked before they are needed.
- **NFR-005**: Generated artifacts must be reproducible from source.
- **NFR-006**: Errors must identify the failed input path or external tool using the `Error [category]: message` format.
- **NFR-007**: The package must remain lightweight for users who only need documentation workflows.
- **NFR-008**: Large book builds should emit progress for each major step using the `[docspark-book]` prefix.
- **NFR-009**: Tests should cover schema, path safety, composition, CLI behavior, and install assets.
- **NFR-010**: *(Future)* The thin client must remain presentation-focused and avoid duplicating server-side publishing rules.
- **NFR-011**: *(Future)* The .NET Minimal API must bind locally by default and must not expose book workspaces as a public service.
- **NFR-012**: *(Future)* LLM calls must be auditable with prompt id, model, input hash, output hash, timestamp, and applied status.
- **NFR-013**: *(Future)* Asset writes through the API must be recoverable through backups or generated history.

## CLI Plan

Add a `book` command group to the existing Typer app.

```bash
docspark book init <path>
docspark book import <source> <target>
docspark book validate <book-path>
docspark book compose <book-path>
docspark book render <book-path> --format epub,pdf
docspark book build <book-path>
docspark book score <book-path>
docspark book critique <book-path>
docspark book rewrite-plan <book-path>
docspark book proof <book-path>
docspark book release-check <book-path>
```

Command behavior:

- `init`: Copy book template files into a new workspace.
- `import`: Convert a legacy `.documentation/books/<slug>` or `books/<slug>` source into the new workspace shape.
- `validate`: Validate manifest, paths, sources, assets, and prerequisites.
- `compose`: Generate `dist/book.md`.
- `render`: Render requested formats from `dist/book.md`.
- `build`: Run validate, compose, render, and artifact validation.
- `score`: Run rule-based parsing and optional LLM scoring.
- `critique`: Prepare context packet for the installed book-critique prompt workflow.
- `rewrite-plan`: Prepare context packet for the rewrite-plan prompt workflow.
- `proof`: Render PDF pages or extract page text when tools are available.
- `release-check`: Produce release checklist and readiness report.

## Data Model

Implement these models in `src/docspark_cli/book/`.

### BookManifest

- `schema`
- `title`
- `subtitle`
- `author`
- `version`
- `description`
- `language`
- `cover_image`
- `publisher`
- `rights`
- `identifier`
- `date`
- `subjects`
- `lifecycle`
- `output`
- `frontmatter`
- `parts` (parsed but ignored in V1)
- `chapters`
- `appendices`

### BookEntry

- `source`
- `title`
- `role`
- `part`
- `number`
- `numbered`
- `status`
- `promise`
- `evidence_required`

### ChapterRecord

- `id`
- `source_path`
- `title`
- `role`
- `number`
- `part`
- `status`
- `word_count`
- `content_hash`
- `headings`
- `first_paragraph`
- `body_excerpt`

### BuildResult

- `book_path`
- `manifest_path`
- `compiled_markdown`
- `output_files`
- `warnings`
- `failures`
- `tool_versions`

### ReviewIssue

- `id`
- `priority`
- `type`
- `scope`
- `source_path`
- `problem`
- `why_it_matters`
- `fix`
- `acceptance_criteria`
- `status`

### ScoreRecord

- `chapter_id` — matches `ChapterRecord.id`
- `content_hash` — SHA-256 of the chapter source file at score time
- `dimensions` — dict of dimension name → `ScoreDimension`
- `model` — LLM model identifier, or `"rule-based"` for non-LLM scores
- `prompt_version` — version string of the scoring prompt used, or `null` for rule-based
- `created_at` — ISO 8601 timestamp
- `stale` — `true` if `content_hash` no longer matches the current chapter source

#### ScoreDimension

Each key in `dimensions` maps to an object with:

- `score` — integer 1–10, or `null` when rule-based measurement does not apply
- `rationale` — one-sentence explanation of the score
- `flags` — list of short string warnings (e.g., `"no_evidence"`, `"too_short"`), may be empty

Valid dimension keys:

| Key                | What it measures                                          |
|--------------------|-----------------------------------------------------------|
| `narrative_arc`    | Does the chapter advance a coherent through-line?         |
| `argument_quality` | Are claims supported by evidence and reasoning?           |
| `clarity`          | Is the prose unambiguous and direct?                      |
| `signal_ratio`     | Is the content dense with useful information vs. filler?  |
| `structure`        | Are headings, transitions, and flow logical?              |
| `voice`            | Is tone consistent with the editorial guidelines?         |
| `evidence_density` | Are concrete examples, data, or specifics present?        |
| `book_fit`         | Does this chapter belong in this book at this position?   |

Rule-based scoring populates `flags` and leaves `score: null` for dimensions that require LLM judgment. LLM scoring populates both `score` and `rationale`.

### ProofingNote

- `id`
- `page`
- `source_path`
- `severity`
- `issue_type`
- `problem`
- `fix`
- `status`

### BookAsset

- `id`
- `book_id`
- `asset_type`
- `relative_path`
- `content_hash`
- `media_type`
- `created_at`
- `updated_at`

### LlmSession *(Future)*

- `id`
- `book_id`
- `chapter_id`
- `operation`
- `prompt_id`
- `prompt_version`
- `provider`
- `model`
- `input_hash`
- `output_hash`
- `created_at`
- `approved`
- `applied`
- `audit_path`

### OperationRecord *(Future)*

- `id`
- `book_id`
- `operation_type`
- `status`
- `started_at`
- `completed_at`
- `progress`
- `warnings`
- `failures`
- `log_path`

## Prompt Commands To Add

Add these stock commands to `COMMAND_SPECS` and `templates/commands/`:

- `book-init`: design or initialize a book workspace.
- `book-critique`: critique a full book as a single editorial product.
- `book-rewrite-plan`: convert a critique into executable, file-specific tasks.
- `book-proof`: inspect rendered output and identify layout/readability issues.
- `book-release`: prepare release notes and a release checklist.

The existing book prompts should be normalized to DocSpark language and installed command names:

- Use `/docspark.book-critique` for full-book critique.
- Use `/docspark.book-rewrite-plan` for rewrite planning.
- Update paths from `books/{slug}/...` to support explicit book paths and `.documentation/books/{slug}/...`.
- Use `.documentation/memory/constitution.md` and `editorial-guidelines.md` as voice authorities.
- Preserve the direct, file-specific critique format.

## Rendering Strategy

V1 renderer:

- Pandoc EPUB3.
- Pandoc PDF.
- PDF engines in this order: `xelatex`, `lualatex`, `pdflatex`, `typst`.
- Optional `epubcheck`.
- Optional `pdfinfo`.

Port critical lessons from the reference implementation:

- Use `--toc`; do not generate a manual TOC section in `book.md`.
- Pass metadata explicitly.
- Support `cover_image`.
- Check Pandoc before rendering.
- Warn when Pandoc is older than 2.19; abort when below 2.11.
- Check PDF engines before PDF rendering.
- Avoid shell injection by passing arguments as arrays.
- Capture enough process output for verbose LaTeX builds (minimum 20 MB buffer).
- Continue rendering other requested formats after one format fails, then exit non-zero with all failures.

Future renderers:

- Typst-native book rendering.
- HTML/CSS paged media.
- DOCX export.
- Print-ready PDF profiles for KDP trim sizes.

## Scoring And Editorial Quality Strategy

The scoring scripts in `.documentation/books/scoring/` should be refactored into a package module rather than copied verbatim.

V1 scoring should include:

- Rule-based parsing of manifest entries.
- Word count, heading count, first paragraph, excerpt, content hash.
- Rule-based structure warnings.
- Optional LLM scoring.
- Resume-safe score storage keyed by `chapter_id` and `content_hash`.
- HTML or Markdown dashboard output.

LLM provider strategy:

- Keep core scoring provider-neutral.
- Do not hard-code Anthropic as the only supported provider in the public interface.
- If the migrated scoring script initially supports only Anthropic, mark it experimental and optional.
- Never require API keys for build, compose, render, or validation.

## Thin Client And API Strategy *(Future — Post-V1)*

*This section is design intent only. Implementation is gated on the V1 CLI milestone (0.2.0).*

The thin client should be introduced after the CLI/core book workflow is stable enough to avoid duplicating behavior. It should call the .NET Minimal API for all persistent operations.

Recommended client views:

- **Library**: open recent book workspaces, create a book, import existing material.
- **Book Overview**: manifest summary, lifecycle status, validation/build status, score summary, release readiness.
- **Outline**: reorder sections, edit titles, roles, statuses, promises, and part membership.
- **Chapter Editor**: Markdown editor, preview, metadata, review issues, suggestions, and diff approval.
- **Review Dashboard**: critiques, score history, stale score warnings, rewrite-plan tasks.
- **Proofing**: rendered page or PDF text view, proofing notes, source mapping.
- **Release**: checklist, validation status, release notes, artifact paths.

Recommended .NET Minimal API services:

- `WorkspaceService`: validates and opens allowed roots.
- `BookAssetService`: reads/writes manifests, chapters, assets, reviews, decisions, and release notes.
- `BackupService`: creates source backups before writes.
- `OperationService`: tracks long-running operations and progress.
- `LlmService`: owns provider adapters, prompt registry, context packets, and audit records.
- `PublishingService`: invokes `docspark book` commands or shared core logic for validate/compose/build.
- `ProofingService`: stores proofing notes and page/source mappings.

Persistence should remain file-first. The API may keep indexes and operation state in `.docspec/*.json`; it should not require a database to create or build a book. SQLite can be considered later if operation history or search needs outgrow JSON files.

## Documentation Plan

Add or update:

- `.documentation/book-publishing.md`
- `.documentation/book-quickstart.md`
- `.documentation/book-manifest.md`
- `.documentation/book-review-workflow.md`
- `.documentation/installation.md`
- `.documentation/quickstart.md`
- `README.md`
- `mkdocs.yml` navigation

Documentation must explain:

- What book publishing adds to DocSpark.
- Required external tools for EPUB/PDF.
- Book workspace layout.
- Manifest fields and schema version.
- Path resolution rules (book-root-relative).
- Build commands.
- Validation commands.
- AI critique and rewrite workflows.
- Generated files and gitignore guidance.
- Migration from `.documentation/books/*` reference projects.
- *(Future)* Thin client and .NET Minimal API architecture.

## Implementation Phases

### Phase 0 - Publishing Asset Harvest And Decisions

Purpose: Convert the untracked in-repo book publishing corpus into deliberate product decisions.

Tasks:

- Inventory `.documentation/books/*` and classify each file as product asset, example, test fixture, generated artifact, or archive.
- Remove stale build artifacts: delete `dist/docspecspark-0.2.0-py3-none-any.whl` and `dist/docspecspark-0.2.0.tar.gz` — these were built from a version that does not exist in `pyproject.toml` and should not be committed.
- Remove generated book corpus artifacts: delete `publish/`, `reviews/`, `scoring/__pycache__/`, and generated JSON files from `scoring/`. Remove committed `book.md` compiled manuscripts. *(Completed 2026-05-17.)*
- Remove `devspark-complete-guide/DevSparkDocumentation/` — a DevSpark docfx product site, not book chapters. *(Completed 2026-05-17.)*
- Record decisions for all open items in the Open Decisions section.
- Confirm that generated reference artifacts are not accidentally packaged.

Exit criteria:

- All Open Decisions with a "Blocks Phase X" note are resolved before that phase begins.
- Product asset locations are selected.
- Generated reference artifacts are not accidentally packaged.
- Stale `dist/` wheel artifacts removed from the repo.

### Phase 1 - Book Templates And Install Assets

Purpose: Make book publishing visible through the existing DocSpark install model.

Tasks:

- Add book template files under `templates/book/`.
- Add book prompt commands under `templates/commands/`.
- Extend `COMMAND_SPECS` with book commands.
- Extend `HELPER_TEMPLATES` or add file-backed template loading if inline strings become too large.
- Install book helper scripts for PowerShell and Bash.
- Update `test_cli_end_to_end.py` to verify installed book assets.

Exit criteria:

- `docspark init <target>` installs book commands, book templates, and book helper scripts.
- Existing install/status/uninstall behavior remains unchanged.
- `test_book_install_assets.py` passes.

Acceptance scenarios:

1. **Given** a fresh target directory, **when** `docspark init <target>` runs, **then** all five book command files exist under `.docspark/defaults/commands/`.
2. **Given** a fresh target directory, **when** `docspark init <target>` runs, **then** `.docspark/templates/book/book.yaml` and `.docspark/templates/book/chapters/00-introduction.md` exist.
3. **Given** a fresh target directory, **when** `docspark init <target>` runs, **then** `.docspark/scripts/powershell/build-book.ps1` and `.docspark/scripts/bash/build-book.sh` exist.
4. **Given** a target with an existing install, **when** `docspark init <target>` runs again, **then** the command succeeds without error and `.documentation/` contents are not overwritten.

### Phase 2 - Manifest And Path Foundation

Purpose: Build the safe core model before rendering.

Tasks:

- Create `tests/fixtures/minimal-book/` with a two-chapter valid manifest. *(The `tests/` directory currently has only `test_cli_end_to_end.py` — fixture directories do not exist yet and must be created in this phase.)*
- Create `tests/fixtures/legacy-book/` — a manifest without `schema:` and with repo-root-relative paths.
- Create `tests/fixtures/hostile-paths/` — manifests with path traversal attempts.
- Create `src/docspark_cli/book/manifest.py`.
- Implement manifest loading from `book.yaml`.
- Implement legacy-compatible validation.
- Implement entry flattening for `frontmatter`, `chapters`, and `appendices`.
- Implement path resolution with traversal protection.
- Implement content hashing.
- Add unit tests for valid and invalid manifests.

Exit criteria:

- `docspark book validate <book-path>` checks manifest shape and source paths without rendering.
- `test_book_manifest.py` passes all valid and invalid cases.

Acceptance scenarios:

1. **Given** a valid `book.yaml` with `title`, `author`, `schema: docspark/book/v1`, and two chapter sources that exist on disk, **when** `docspark book validate <book-path>` runs, **then** exit code is `0` and stdout contains `[docspark-book] Validating manifest`.
2. **Given** a `book.yaml` with only one chapter entry, **when** `docspark book validate <book-path>` runs, **then** exit code is `1` and stderr contains `Error [manifest]: Minimum 2 chapters required`.
3. **Given** a `book.yaml` with a chapter `source` pointing to a file that does not exist, **when** `docspark book validate <book-path>` runs, **then** exit code is `1` and stderr contains `Error [compose]: Chapter source not found`.
4. **Given** a `book.yaml` with `source: ../../etc/passwd`, **when** `docspark book validate <book-path>` runs, **then** exit code is `1` and stderr contains `Error [path]: Path traversal rejected`.
5. **Given** a legacy `book.yaml` with `title`, `author`, and `chapters` but no `schema:` field, **when** `docspark book validate <book-path>` runs, **then** exit code is `0` (legacy-compatible mode accepted).

### Phase 3 - Compose

Purpose: Generate a deterministic Markdown manuscript from source files.

Tasks:

- Implement frontmatter parsing.
- Implement title resolution.
- Implement heading generation for frontmatter, chapters, and appendices.
- Implement body cleanup rules from the reference script where still appropriate.
- Generate `dist/book.md`.
- Emit progress lines.
- Add gitignore patterns for generated book artifacts. The current `.gitignore` has `dist/` (the Python package dist), but book workspace dist paths are different. Add these lines:

  ```text
  .documentation/books/**/dist/
  .documentation/books/**/.docspec/
  books/**/dist/
  books/**/.docspec/
  ```

- Add tests for composition output, title fallback, no manual TOC, appendix numbering, custom chapter numbers, and missing files.

Exit criteria:

- `docspark book compose <book-path>` writes a deterministic composed manuscript.
- `test_book_compose.py` passes including no-duplicate-TOC assertion.

Acceptance scenarios:

1. **Given** a valid two-chapter book, **when** `docspark book compose <book-path>` runs, **then** `dist/book.md` is created, exit code is `0`, and the file contains `# Chapter 1:` and `# Chapter 2:` headings in order.
2. **Given** a chapter with a `title` in `book.yaml` and a different `title` in the chapter frontmatter, **when** composed, **then** `dist/book.md` uses the `book.yaml` title (manifest wins).
3. **Given** a chapter with no `title` in `book.yaml` and a `title` in the chapter frontmatter, **when** composed, **then** `dist/book.md` uses the frontmatter title (fallback).
4. **Given** a chapter with no title anywhere, **when** composed, **then** `dist/book.md` uses the filename as the title.
5. **Given** a book with an appendix entry, **when** composed, **then** `dist/book.md` contains `# Appendix A:` heading (not a numbered chapter).
6. **Given** a chapter with `number: "2B"` in `book.yaml`, **when** composed, **then** the heading reads `# Chapter 2B:` not `# Chapter 3:`.
7. **Given** a composed `dist/book.md`, **when** searched for the string `## Table of Contents`, **then** the string is absent.
8. **Given** a chapter file whose body is empty (frontmatter only), **when** composed, **then** a warning is emitted on stderr and the chapter is skipped without halting the build.

### Phase 4 - Render And Validate Artifacts

Purpose: Produce EPUB/PDF outputs and catch structural failures.

Tasks:

- Implement external tool discovery for Pandoc, PDF engines, `epubcheck`, and `pdfinfo`.
- Implement Pandoc EPUB adapter.
- Implement Pandoc PDF adapter.
- Implement artifact validation.
- Support partial render failure reporting.
- Add tests using mocks for external tools.
- Add manual validation notes for real Pandoc builds.

Exit criteria:

- `docspark book build <book-path>` can produce `dist/book.epub` and `dist/book.pdf` when prerequisites exist.
- `docspark book validate <book-path> --artifacts` catches missing or malformed outputs.
- `test_book_cli.py` passes with mocked Pandoc.

Acceptance scenarios:

1. **Given** a composed `dist/book.md` and Pandoc ≥ 2.19 installed, **when** `docspark book build <book-path>` runs, **then** `dist/book.epub` and `dist/book.pdf` are created and exit code is `0`.
2. **Given** Pandoc is not on PATH, **when** `docspark book build <book-path>` runs, **then** exit code is `1` and stderr contains `Error [render]: Pandoc not found`.
3. **Given** Pandoc is present but version is below 2.11, **when** `docspark book build` runs, **then** exit code is `1` and stderr contains `Error [render]: Pandoc version X.Y is too old`.
4. **Given** Pandoc is version 2.14 (between 2.11 and 2.19), **when** `docspark book build` runs, **then** a warning is emitted but the build continues and exit code reflects render success or failure.
5. **Given** PDF rendering fails but EPUB succeeds, **when** `docspark book build <book-path>` runs with both formats, **then** `dist/book.epub` is written, exit code is `1`, and stderr reports the PDF failure.
6. **Given** `dist/book.epub` does not exist, **when** `docspark book validate <book-path> --artifacts` runs, **then** exit code is `1` and stderr contains `Error [validate]: EPUB not found`.

### Phase 5 - Import Existing Books

Purpose: Make the reference books useful without hard-coding their layout.

Tasks:

- Implement `docspark book import <source> <target>`.
- Convert legacy repo-root-relative paths to book-root-relative paths.
- Copy chapters, appendices, cover images, reviews, and selected metadata.
- Generate `IMPORT_REPORT.md`.
- Add `tests/fixtures/legacy-book/` fixture.

Exit criteria:

- At least one reference book imports into the new workspace shape and validates.
- `test_book_cli.py` covers `book import` with the legacy fixture.

### Phase 6 - Review Prompts And Rewrite Planning

Purpose: Productize the strongest editorial workflows in the in-repo book corpus.

Tasks:

- Adapt book critique prompt to DocSpark naming and path conventions.
- Adapt rewrite-plan prompt to DocSpark naming and path conventions.
- Add prompt context helper script: `book-context`.
- Add documentation for critique and rewrite workflow.
- Add tests confirming prompt assets install and use correct command names.

Exit criteria:

- Installed projects can run `/docspark.book-critique` and `/docspark.book-rewrite-plan` through agent shims.
- The prompts reference real DocSpark paths and commands.

### Phase 7 - Scoring And Dashboard

Purpose: Bring in optional quality metrics without making LLMs mandatory.

Tasks:

- Port `parse_books.py` behavior to package code.
- Store score state under `.docspec/score-history.json`.
- Implement rule-based score summary using the `ScoreRecord` / `ScoreDimension` schema.
- Add optional provider adapter for LLM scoring (Anthropic, marked experimental).
- Generate Markdown or HTML dashboard.
- Mark stale scores when content hashes change.

Exit criteria:

- `docspark book score <book-path>` works without an API key in rule-only mode.
- Optional LLM scoring is clearly gated by configuration and credentials.

### Phase 8 - Proofing And Release

Purpose: Close the publication loop.

Tasks:

- Implement `docspark book proof <book-path>` with PDF text extraction first.
- Add optional PDF page image rendering when Poppler is installed.
- Track proofing notes under `.docspec/proofing-notes.json`.
- Implement release checklist generation.
- Implement release notes scaffold.
- Add docs for release candidate workflow.

Exit criteria:

- `docspark book release-check <book-path>` reports build, validation, scoring, proofing, and metadata readiness.

### Phase 9 - Site And README Update

Purpose: Make the feature discoverable and publish the V1 milestone.

Tasks:

- Update README.
- Add book docs to MkDocs navigation.
- Add MkDocs exclusion for `.documentation/books/**` so chapter source files are not accidentally rendered as site pages. Use `exclude_docs:` or an explicit `nav:` that omits the books subtree.
- Add quickstart examples.
- Add migration guidance.
- Update all 4 `quickstart/` agent prompts with a book publishing section.
- Replace the hardcoded `VERSION = "0.1.0"` string in `cli.py` with a dynamic read from package metadata (`importlib.metadata.version("docspark-cli")`), so `pyproject.toml` remains the single version source of truth. Update the corresponding test assertion.
- Bump version to `0.2.0` in `pyproject.toml` and publish to PyPI.
- Run `uv run pytest`.
- Run `mkdocs build --strict` if MkDocs dependencies are available.

Exit criteria:

- Tests pass.
- Documentation site builds or any missing local dependency is documented.
- `docspark-cli` 0.2.0 published to PyPI.
- All 4 `quickstart/` agent prompts updated with book command section.
- MkDocs nav does not expose `.documentation/books/` chapter files as site pages.

### Phase 10 - .NET Minimal API *(Future — Gated On Published V1 CLI)*

Purpose: Add the local service boundary for LLM calls and durable book asset persistence.

Gate: Phase 10 does not begin until `docspark-cli` 0.2.0 is published and at least one real book has been built and released using the CLI alone.

Tasks:

- Create `services/DocSpark.BookApi/`.
- Implement local-only startup defaults bound to `127.0.0.1`.
- Add workspace open/init endpoints with path validation.
- Add manifest, outline, chapter, asset, review, decision, and release-note read/write endpoints.
- Add backup-on-write behavior.
- Add `.docspec/` persistence for operations, LLM sessions, score history, and proofing notes.
- Add LLM provider abstraction and audit records.
- Add endpoints that invoke `docspark book validate`, `compose`, `build`, `score`, and `release-check`.
- Add tests for path safety, backup behavior, and LLM context filtering.

Exit criteria:

- The API can open a book workspace, persist book assets, run core book commands, and record LLM audit metadata without exposing a public service.

### Phase 11 - Thin Client *(Future — Gated On Published .NET API)*

Purpose: Add a browser-based authoring surface without moving publishing rules into the client.

Gate: Phase 11 does not begin until the Phase 10 API is stable and its endpoint contract is documented.

Tasks:

- Create `apps/book-studio/`.
- Implement Library, Book Overview, Outline, Chapter Editor, Review Dashboard, Proofing, and Release views.
- Add API client services for all persistent operations.
- Add operation progress display.
- Add diff/approval flow for LLM suggestions.
- Add visual states for stale scores, unresolved proofing notes, validation failures, and release readiness.
- Add lightweight UI tests or smoke tests for core flows.

Exit criteria:

- A user can create/open a book, edit manifest/chapter assets through the API, request critique or rewrite-plan work, approve changes, and run build/validation from the thin client.

## Recommended First Milestone

The first milestone should stay focused on the useful non-LLM core.

Deliver:

- Book templates installed by `docspark init`.
- `docspark book init`.
- `docspark book validate`.
- `docspark book compose`.
- `docspark book build` using Pandoc when available.
- Artifact validation.
- One sample book fixture.
- Updated README and MkDocs docs.
- Tests for install assets, manifest validation, path safety, and composition.

Defer:

- Thin client and .NET API (Phases 10–11) until the CLI is published and proven.
- Page-image proofing (PDF page rendering via Poppler).
- Provider-neutral LLM scoring beyond the Anthropic experimental adapter.
- Release automation beyond checklist generation.

## Migration From Existing Book Work

The existing implementation in `.documentation/books/` should be treated as DocSpark-owned publishing work that needs to be organized into the final product layout.

Migration actions:

- Port behavior from JavaScript scripts into Python modules.
- Preserve the critical rendering and validation lessons.
- Normalize all prompt names to DocSpark command names.
- Keep sample book content as fixtures/examples only when licensing and size are appropriate.
- Do not package generated EPUB/PDF outputs.
- Do not commit LLM cache files, pycache files, or generated dashboards unless explicitly selected as documentation examples.

Suggested importer:

```bash
docspark book import .documentation/books/project-mechanics examples/project-mechanics-book
docspark book import .documentation/books/devspark-complete-guide examples/devspark-complete-guide-book
```

Importer responsibilities:

- Read legacy `book.yaml`.
- Copy chapters and assets.
- Preserve frontmatter, chapters, appendices, and custom numbering.
- Convert repo-root-relative source paths to book-root-relative paths.
- Convert output paths to `dist/`.
- Create missing `overview.md`, `audience.md`, `editorial-guidelines.md`, and `outline.md`.
- Copy reviews into `reviews/` when requested.
- Write `IMPORT_REPORT.md` with unsupported fields and assumptions.

## Test Architecture

All book tests extend the existing pattern in `tests/test_cli_end_to_end.py` — `tmp_path` fixtures, subprocess CLI invocation, and file-system assertions. Do not introduce a separate test runner or framework.

### Test Modules

| Module | Coverage |
| --- | --- |
| `tests/test_book_manifest.py` | Schema loading, legacy mode, traversal rejection, missing fields, unsupported fields |
| `tests/test_book_compose.py` | Title resolution, frontmatter stripping, no-TOC assertion, empty body warning, appendix lettering, custom chapter numbers |
| `tests/test_book_cli.py` | book init, validate, compose, build (mocked Pandoc), import — progress format and exit codes |
| `tests/test_book_install_assets.py` | Installed book commands, templates, and scripts after docspark init |

### Fixture Strategy

- `tests/fixtures/minimal-book/` — two-chapter book with a valid `book.yaml`, used in the majority of manifest and compose tests.
- `tests/fixtures/legacy-book/` — a manifest without `schema:` and with repo-root-relative paths, used to test importer and legacy-compat mode.
- `tests/fixtures/hostile-paths/` — manifests with path traversal attempts, used to test rejection.
- The `devspark-complete-guide` corpus in `.documentation/books/` MUST NOT be used as a test fixture — it is too large and its paths will break in `tmp_path` contexts. Use it only for manual validation.

### Minimum Coverage Per Phase Exit

- Phase 1: `test_book_install_assets.py` passes.
- Phase 2: `test_book_manifest.py` passes all valid and invalid cases.
- Phase 3: `test_book_compose.py` passes including no-duplicate-TOC assertion.
- Phase 4: `test_book_cli.py` passes with mocked Pandoc.
- Phase 5: `test_book_cli.py` covers `book import` with legacy fixture.

## Validation Strategy

Automated tests:

- CLI command registration.
- Installed book assets.
- Manifest parsing.
- Legacy manifest compatibility.
- Unsupported manifest fields.
- Path traversal rejection.
- Missing source file errors.
- Composition output snapshots.
- No duplicate TOC.
- Appendix and custom numbering.
- External tool detection mocked.
- Partial render failure mocked.

Manual validation:

- Build EPUB and PDF from a sample book on Windows.
- Open EPUB in Kindle Previewer or an EPUB reader.
- Open PDF in a PDF viewer.
- Confirm title metadata, TOC, chapter starts, appendix numbering, and no duplicate title/TOC artifacts.

Documentation validation:

- `uv run pytest`
- `mkdocs build --strict`
- Verify README commands match the CLI.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Scope expands into a full writing IDE too early | Core publishing slips | Ship CLI, templates, and prompts first; gate Phases 10–11 |
| Porting JS scripts to Python changes behavior | Existing lessons are lost | Use reference books as fixtures and snapshot composition output |
| Pandoc/LaTeX setup is heavy | User friction | Document prerequisites, allow EPUB-only, detect tools early |
| EPUB output differs by Pandoc version | Validation inconsistency | Warn below Pandoc 2.19, abort below 2.11 |
| LLM scoring hard-codes one provider | Feature is brittle | Keep scoring optional and wrap provider-specific code |
| Generated files are accidentally packaged | Repo bloat | Classify reference files before migration and update gitignore |
| Path traversal bug | Safety issue | Centralize path resolution and test hostile paths |
| Thin client duplicates publishing rules | Maintenance drift | All file writes and business logic remain in CLI/API, not client |
| API accidentally becomes public service | Security risk | Bind to localhost by default; Future phase only |
| LLM context leaks unrelated files | Privacy and trust risk | Centralize context packet construction and audit input hashes |
| Prompt names are inconsistent | Product confusion | Normalize all installed book prompts to `docspark.*` |
| Existing users are broken by naming cleanup | Adoption risk | Preserve `docspark` CLI and `.docspark` install paths in V1 |
| `devspark-complete-guide` naming confusion | Import failures | Resolve Open Decision 12 before Phase 5 |

## Open Decisions

1. **RESOLVED** — Public book examples live under `examples/`. The repo already uses `examples/policy-portal/` as the established pattern and `test_examples_policy_portal_snapshot_exists` tests it. `.documentation/books/` remains user-owned active work space.
2. **RESOLVED** — `dist/book.md` is gitignored. Gitignore patterns for book workspace generated outputs are added in Phase 3: `.documentation/books/**/dist/`, `.documentation/books/**/.docspec/`, `books/**/dist/`, `books/**/.docspec/`. Note: the existing top-level `dist/` entry covers only the Python package dist, not book workspace dist paths.
3. Should Pydantic be added for schema validation, or should validation remain dependency-light? (Recommendation: dataclasses + explicit validation for V1.)
4. Which LLM provider adapters should be supported first? (Recommendation: defer to Phase 7; Anthropic adapter marked experimental.)
5. Should `docspark book critique` execute prompts directly, or only prepare context? (Recommendation: prepare context only in V1 — write a context file for the agent to consume.)
6. **RESOLVED** — No `docspecspark` command alias. The CLI is `docspark`, the install root is `.docspark`, the package is `docspark-cli`. No alias will be introduced.
7. **RESOLVED** — Minimum supported Pandoc version is **2.19**. Warn and continue below 2.19; abort below 2.11.
8. **RESOLVED** — Generated EPUB/PDF artifacts are never committed. `publish/` has been deleted from `.documentation/books/`. Outputs go to `dist/` inside the book workspace, which is gitignored.
9. Should the .NET API invoke the Python CLI for all publishing operations initially? (Recommendation: moot for V1 — defer API to Phase 10.)
10. Should the thin client use polling, SSE, or WebSockets for progress? (Recommendation: polling first; SSE when API is stable. Decide in Phase 10.)
11. Should `.docspec/` state remain JSON-only in V1? (Recommendation: yes; revisit in Phase 10.)
12. **MUST RESOLVE BEFORE PHASE 5** — Is `devspark-complete-guide` a DevSpark product book or a DocSpark pipeline example? If a DevSpark product, reference it externally only. If a DocSpark example, rename it and update content to describe DocSpark.
13. **RESOLVED** — `parts:` is deferred from V1. The V1 `compose` command uses a flat `chapters:` array only. `parts:` in `book.yaml` is accepted with a warning and ignored.
14. **RESOLVED** — The `book_only: true` frontmatter flag is the V1 mechanism for marking chapters as book-only. The `compose` command reads and logs this flag; website generators are responsible for filtering.

## Success Criteria

### V1 CLI Milestone (Phases 0–9, version 0.2.0)

- **SC-001**: A new book workspace can be created with `docspark book init`.
- **SC-002**: A valid book manifest can be validated without external rendering tools.
- **SC-003**: A composed Markdown manuscript can be generated from manifest-listed chapter files.
- **SC-004**: EPUB and PDF can be rendered when Pandoc and a PDF engine are installed.
- **SC-005**: Artifact validation catches missing or malformed outputs.
- **SC-006**: Existing DocSpark init/status/uninstall workflows continue to pass tests.
- **SC-007**: Book critique and rewrite-plan prompts install under DocSpark command names.
- **SC-008**: At least one reference book can be imported and built.
- **SC-009**: LLM-dependent features are optional and fail with clear configuration guidance.
- **SC-010**: Documentation explains the complete author workflow from book creation through release check.
- **SC-011**: `docspark-cli` version 0.2.0 is published to PyPI with book publishing commands included.
- **SC-012**: All quickstart prompts cover book publishing commands.
- **SC-013**: Progress output follows the `[docspark-book]` prefix contract on all commands.
- **SC-014**: Path traversal is rejected with an actionable error on all commands.

### Future Architecture Milestone (Phases 10–11, gated on V1 CLI)

- **SC-015**: The .NET Minimal API can persist book assets and own LLM calls with auditable session records.
- **SC-016**: The thin client performs book workflows through the API and does not write source files directly.

## Immediate Next Tasks

**Step 1 — One blocking decision remains before Phase 5:**

1. **Decide** Open Decision 12: is `devspark-complete-guide` a DocSpark example or a DevSpark artifact? (Blocks Phase 5.) All other blocking decisions (OD-1, OD-2, OD-6, OD-8) are now resolved.

**Step 2 — Phase 0 cleanup tasks:**

1. Delete stale dist artifacts: `dist/docspecspark-0.2.0-py3-none-any.whl` and `dist/docspecspark-0.2.0.tar.gz`.

**Step 3 — Begin Phase 1 implementation:**

1. Add book command specs to `COMMAND_SPECS` and create `templates/commands/` book prompt files.
2. Create `tests/fixtures/minimal-book/` with a two-chapter valid manifest.
3. Create `src/docspark_cli/book/` with `manifest.py` and `paths.py`.
4. Add `tests/test_book_manifest.py` covering all validation cases.
5. Port composition behavior from `.documentation/books/scripts/build-book.mjs` into `src/docspark_cli/book/compose.py`.
6. Update README and MkDocs navigation with the book quickstart (add MkDocs `exclude_docs:` for `.documentation/books/**`).
7. Update all 4 `quickstart/` agent prompts to mention book commands.
