---
classification: full-spec
risk_level: low
target_workflow: specify-full
required_artifacts: spec, plan, tasks
recommended_next_step: plan
required_gates: checklist, analyze, critic
---

# Feature Specification: Book & Long-Form Publishing Pipeline

**Feature Branch**: `001-book-publishing`
**Created**: 2026-04-21
**Status**: In Progress
**Input**: User description: "Book & Long-Form Publishing Pipeline — spec-driven composition of books (EPUB, PDF) from existing Markdown articles"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Compose a Book from Existing Articles (Priority: P1)

Mark wants to assemble a curated collection of his existing blog articles into a structured book. He creates a `book.yaml` file that lists the articles to include, their chapter order, and book metadata. He runs a single command and receives an EPUB and a PDF that he can upload to Amazon KDP or distribute directly.

**Why this priority**: This is the core value proposition of the entire pipeline. Without it, no other capability matters. It delivers immediate, tangible output (a publishable book) and validates the entire composition and rendering approach.

**Independent Test**: Create a `book.yaml` referencing two or three existing Markdown articles, run `npm run build:book -- <slug>`, and confirm that `books/publish/<slug>/book.epub` and `books/publish/<slug>/book.pdf` are produced with correct chapter structure and content.

**Acceptance Scenarios**:

1. **Given** a valid `book.yaml` with at least two article references, **When** the build command is run, **Then** a compiled `book.md` is produced in the book directory with frontmatter stripped, chapters titled, and a title page and table of contents prepended.
2. **Given** a compiled `book.md`, **When** the rendering step executes, **Then** both `book.epub` and `book.pdf` are written to `books/publish/<slug>/` with no rendering errors.
3. **Given** a `book.yaml` that references a non-existent article file, **When** the build command is run, **Then** the process halts with a clear error identifying the missing file before any output is written.

---

### User Story 2 — Tag Articles as Book-Eligible (Priority: P2)

Mark wants to mark individual blog articles as eligible for book inclusion and assign them optional book-specific metadata (a preferred chapter title, a pillar group, and an ordering hint). He edits the YAML frontmatter of an article and the information is available to the composition engine.

**Why this priority**: Without flagging articles, every article must be manually tracked in `book.yaml`. Frontmatter flags allow automation and filtering in future pipeline stages without changing the core composition engine.

**Independent Test**: Add `book: true` and `book_order: 2` to an article's frontmatter, run the article generator (`npm run generate:articles`), and confirm the flag is preserved in `articles.json`.

**Acceptance Scenarios**:

1. **Given** an article with `book: true` in its frontmatter, **When** `npm run generate:articles` runs, **Then** the article's entry in `articles.json` includes the book flag and any provided `book_title` or `book_order` values.
2. **Given** an article without any book frontmatter fields, **When** processed by the composition engine, **Then** its standard `title` is used as the chapter title and no error is produced.

---

### User Story 3 — Preview and Validate Before Publishing (Priority: P3)

Mark wants to review the generated EPUB in Kindle Previewer and the PDF in a standard viewer before uploading to Amazon KDP. He needs the output to be free of structural errors and formatted readably.

**Why this priority**: Quality validation prevents publishing malformed books. This is lower priority than generation itself — it is a workflow gate, not a system requirement.

**Independent Test**: Open the generated `book.epub` in Kindle Previewer and the generated `book.pdf` in a PDF viewer; confirm chapter headings, a table of contents, and article content appear correctly without rendering artifacts.

**Acceptance Scenarios**:

1. **Given** a generated `book.epub`, **When** opened in Kindle Previewer, **Then** the table of contents is navigable, each chapter starts on its own page, and no structural validation errors are reported.
2. **Given** a generated `book.pdf`, **When** opened in a PDF viewer, **Then** chapters are clearly separated, a title page appears, and the document is readable without layout errors.

---

### User Story 4 — Control Web Visibility per Article (Priority: P2)

Mark has written content that belongs in a book but should never appear as a standalone blog post on the website — for example, a book introduction, a connecting narrative chapter, or a piece he intends to distribute only through the published book. He adds `web_publish: false` to the article's YAML frontmatter and the article is excluded from `articles.json`, the sitemap, and all web routing. It remains available as a valid book chapter source and can be referenced in `book.yaml` exactly like any other article.

As an alternative, Mark may place book-only chapters directly in `books/<slug>/chapters/` instead of `src/content/`, keeping them physically separate from the blog corpus.

**Why this priority**: Enables editorial flexibility without compromising the website's content quality. Authors can draft book connective tissue without cluttering the blog index or exposing incomplete content publicly.

**Independent Test**: Add `web_publish: false` to an article in `src/content/`, run `npm run generate:articles`, and confirm the article does **not** appear in `articles.json`. Then reference the same article as a chapter in `book.yaml`, run `npm run build:book -- <slug>`, and confirm the article content appears correctly in the generated EPUB and PDF.

**Acceptance Scenarios**:

1. **Given** an article with `web_publish: false` in its frontmatter, **When** `npm run generate:articles` runs, **Then** that article is absent from `articles.json` and will not be routed or indexed on the website.
2. **Given** an article with `web_publish: false`, **When** it is referenced as a chapter source in `book.yaml` and `npm run build:book` is run, **Then** the article content is included normally in the composed `book.md` and rendered output — the `web_publish` flag has no effect on book composition.
3. **Given** an article without a `web_publish` field, **When** processed by either pipeline, **Then** it is treated as `web_publish: true` — included in the website build as normal.
4. **Given** a Markdown file stored in `books/<slug>/chapters/` (outside `src/content/`), **When** referenced as a chapter source in `book.yaml`, **Then** the composition engine reads and includes it successfully.

---

### Edge Cases

- What happens when a referenced article file has no body content (only frontmatter)? The composition engine should skip it with a warning rather than producing an empty chapter.
- What happens when two articles have the same `book_order` value? The composition engine should use file declaration order in `book.yaml` as a tiebreaker and emit a warning.
- What happens when Pandoc is not installed or not on the system path? The build script should detect this before attempting rendering and exit with a clear installation message.
- What happens when one format fails but another succeeds (e.g., EPUB renders but PDF fails)? The script attempts all formats, writes successful outputs to disk, reports each failure with the format name and error, then exits non-zero so the overall build is marked failed.
- What happens when the `books/publish/<slug>/` directory already exists from a prior build? The script should overwrite existing outputs rather than fail.
- What happens when `book.yaml` defines fewer than 2 chapters? The composition engine halts before writing any output and reports a clear error stating the minimum chapter requirement.
- What happens when a chapter source has `web_publish: false`? The composition engine reads the file normally and includes it in the book — the `web_publish` flag is irrelevant to book composition.
- What happens when `web_publish` is absent from frontmatter? The article is treated as `web_publish: true` and included in the website build (opt-in exclusion model).
- What happens when a chapter source path points to `books/<slug>/chapters/` instead of `src/content/`? The composition engine reads the file by its repo-root-relative path; no special handling is required.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a `book.yaml` file as the single source of truth for book composition, including metadata (title, subtitle, author, version, description), optional frontmatter, optional parts, an ordered chapter list, and optional appendices.
- **FR-002**: The composition engine MUST strip YAML frontmatter from each referenced article and concatenate chapter content into a single `book.md` file.
- **FR-003**: The composition engine MUST prepend a title page (title, subtitle, author) to `book.md`. A navigable table of contents MUST appear in the rendered EPUB3 and PDF outputs; it is generated by Pandoc `--toc` at render time and is NOT included as a manual section in `book.md` — a manual TOC in `book.md` produces a duplicate TOC page in PDF and a redundant TOC chapter in the EPUB body (see plan.md Critic Gate Mitigations — Pass 2, NEW-CR-003).
- **FR-004**: The composition engine MUST apply a chapter title override from `book.yaml` when provided; otherwise it MUST fall back to the article's frontmatter `title`.
- **FR-005**: The rendering engine MUST produce output in every format listed in `book.yaml`'s `output.formats` array; supported formats are `epub` (EPUB3) and `pdf`. EPUB output MUST conform to the EPUB3 standard to ensure compatibility with Amazon KDP and modern reading devices.
- **FR-006**: The build script MUST place all output files under `books/publish/<slug>/` using the book slug derived from the directory name of `book.yaml`.
- **FR-007**: The build script MUST exit with a non-zero status code and a human-readable error message when any required input file is missing or the rendering tool is unavailable. When rendering multiple formats, the script MUST attempt every format before exiting — if one or more formats fail, all failures MUST be reported and the script MUST exit non-zero; any formats that succeeded MUST still be written to disk.
- **FR-008**: Article frontmatter MUST support the following optional publishing flags: `book` (boolean), `book_title` (string), `book_order` (integer), `web_publish` (boolean, default `true`).
- **FR-009**: The `generate:articles` script MUST propagate `book`, `book_title`, and `book_order` values from article frontmatter into `articles.json` for articles included in the website build. (`web_publish` is not propagated into `articles.json` — its presence in the output array implicitly indicates `web_publish: true`.)
- **FR-010**: The composition engine MUST insert a visible separator between chapters in `book.md`.
- **FR-011**: The compiled `book.md` MUST be written to `books/<slug>/book.md` and committed to the repository alongside `book.yaml`; it serves as an auditable snapshot of the composed book at the time of the last build.
- **FR-012**: The build script MUST emit one human-readable progress line per major step (composition start, each chapter processed, each output format rendered, final output paths) to standard output on a successful run.
- **FR-013**: The composition engine MUST validate that `book.yaml` defines a minimum of 2 chapters; if fewer than 2 are provided, the build MUST halt before composition with a clear error message.
- **FR-014**: The `generate:articles` script MUST exclude any article with `web_publish: false` from the `articles.json` output entirely. Articles without a `web_publish` field are treated as `web_publish: true` (opt-in exclusion model). Exclusion from `articles.json` implicitly prevents prerendering, sitemap inclusion, and web routing for that article.
- **FR-015**: The composition engine MUST accept any repo-root-relative Markdown file as a valid `chapter.source`, regardless of its `web_publish` flag or its location in the repository. `web_publish: false` articles and files stored outside `src/content/` (e.g., `books/<slug>/chapters/`) are equally valid chapter sources.
- **FR-016**: Book-only Markdown files MAY be stored in `books/<slug>/chapters/` as an alternative to `src/content/`. They follow the same format (YAML frontmatter + Markdown body) and are processed identically by the composition engine but are never processed by the website build.
- **FR-017**: The build script MUST validate `book.yaml` against the supported schema and fail on unsupported top-level fields or unsupported entry fields.
- **FR-018**: The build script MUST run artifact validation after rendering, including duplicate-numbering checks, EPUB structure inspection, optional `epubcheck` validation when installed, and PDF existence/page-count checks.

### Key Entities

- **Book**: Defined by `book.yaml`; has a slug (directory name), metadata fields, output format list, and an ordered chapter list.
- **Chapter**: An entry in the chapter list; references one Markdown article source file and optionally provides a title override.
- **Frontmatter Section**: An unnumbered manifest entry rendered before Chapter 1, such as a foreword or introduction.
- **Appendix**: A manifest entry rendered after numbered chapters as Appendix A/B/C.
- **Article**: A Markdown file that may reside in `src/content/` or in `books/<slug>/chapters/`; may carry optional frontmatter flags (`book`, `book_title`, `book_order`, `web_publish`). Articles with `web_publish: false` (or stored outside `src/content/`) are excluded from the website but are valid book chapter sources.
- **Compiled Book (`book.md`)**: The intermediate Markdown document produced by the composition engine; consumed by the rendering engine.
- **Book Output**: The final EPUB or PDF file written to `books/publish/<slug>/`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A complete EPUB and PDF can be generated from a `book.yaml` referencing three or more existing articles in under 60 seconds on a standard developer workstation with Pandoc and LaTeX already installed and initialized (warm-start). Cold-start builds (e.g., MiKTeX first-run package downloads on Windows) are explicitly excluded from this SLO and may take significantly longer.
- **SC-002**: The generated EPUB passes Kindle Previewer validation with zero structural errors on the first attempt for any valid `book.yaml` input that includes a `cover_image` field pointing to a valid PNG or JPEG file. Books without a cover image are not expected to pass zero-error Kindle Previewer validation.
- **SC-003**: The composition and rendering workflow requires no additional authoring work beyond creating `book.yaml` — existing article Markdown is used without modification.
- **SC-004**: The publishing pipeline does not affect existing blog build or LinkedIn carousel outputs — both continue to build successfully after the pipeline is added.
- **SC-005**: A developer unfamiliar with the pipeline can produce their first book output by following only the steps in `quickstart.md` without requiring external assistance or knowledge beyond what is documented there.

---

## Assumptions

- The external rendering tool (Pandoc) is installed and available on the system path on developer workstations; installation is a prerequisite, not a pipeline responsibility.
- Existing article Markdown files are well-formed; the composition engine applies best-effort frontmatter stripping but does not perform deep content validation.
- The `books/` and `books/publish/` directories are additive to the repository structure and do not conflict with the existing `docs/` build output directory.
- The compiled `book.md` is a committed artifact stored alongside `book.yaml` in `books/<slug>/`; it is regenerated and recommitted whenever source articles or `book.yaml` change.
- Output quality for direct distribution via the rendering tool's defaults is acceptable for initial release; advanced styling is a future enhancement.
- The initial implementation targets a single-book build command (`npm run build:book -- <slug>`); multi-book batch builds are out of scope.
- Article source paths in `book.yaml` are relative to the repository root (e.g., `src/content/my-article.md`).
- The `carousel` frontmatter flag (pre-existing) is unaffected by this pipeline; `book` is a separate independent flag.

---

## Clarifications

### Session 2026-04-21

- Q: What EPUB version should the rendering engine target for output? → A: EPUB3 — the modern standard, compatible with Amazon KDP and the Pandoc default.
- Q: Should the intermediate `book.md` be treated as ephemeral build output or committed to the repository? → A: Committed — stored at `books/<slug>/book.md` alongside `book.yaml` for auditability and offline review.
- Q: What should the build script output during a successful run? → A: Progress lines — one line per major step (compose, render each format, output paths); silent only on errors.
- Q: When rendering multiple formats and one fails, should the script exit immediately or attempt all formats first? → A: Attempt all formats before exiting — report all failures and exit non-zero; successful format outputs are still written to disk.
- Q: What is the minimum number of chapters required in `book.yaml` for a valid build? → A: Minimum 2 chapters — build halts with a clear error if fewer than 2 are defined.

### Session 2026-04-22

- Q: Is it possible to have an article that is not published on the web, only included in a book? → A: Yes — adding `web_publish: false` to an article's frontmatter excludes it from `articles.json` and the website while keeping it available as a book chapter source (FR-014/FR-015). Articles may also be placed in `books/<slug>/chapters/` to physically separate them from the blog corpus (FR-016).
- Q: What is the default behavior when `web_publish` is absent from frontmatter? → A: Treated as `true` — opt-in exclusion model; existing articles are unaffected without any frontmatter changes.
