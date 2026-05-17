---
description: "Task list for 001-book-publishing"
---

# Tasks: Book & Long-Form Publishing Pipeline

**Input**: Design documents from `books/docs/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/cli-contract.md ✅, quickstart.md ✅

**Gate acknowledgements**:
- `gates/critic.md` pass 1 (warn/non-blocking) — all 3 CRs and 2 HPs resolved in plan.md and design artifacts.
- `gates/critic.md` pass 2 (warn/non-blocking) — all 3 new CRs (spawnSync maxBuffer, T007/T008 coupling, double TOC) and 4 HPs resolved in plan.md, data-model.md, and quickstart.md before this task regeneration.

**Tests**: Not requested in spec; manual validation via Kindle Previewer and PDF viewer (per constitution §VII Testing Exemption).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: US1 = book composition, US2 = article tagging, US3 = preview/validate

---

## Phase 1: Setup

**Purpose**: Repository structure and dependency initialization

- [x] T001 Create `books/` directory at repo root with a `.gitkeep` placeholder
- [x] T002 Verify `dist/` is covered by `.gitignore`; add `books/publish/` entry if needed (`.gitignore`)
- [x] T003 [P] Install `js-yaml` as a dev dependency: `npm install --save-dev js-yaml` (`package.json`, `package-lock.json`)
- [x] T004 Add `"build:book": "node books/scripts/build-book.mjs"` to `scripts` in `package.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utility and skeleton that both US1 and US2 depend on

**⚠️ CRITICAL**: T005 and T006 must be complete before any user story implementation begins.

- [x] T005 Create `books/scripts/build-book.mjs` with the script skeleton: argument parsing (reads `<slug>` from `process.argv[2]`), **slug validation** (reject slugs not matching `/^[a-z0-9-]+$/` with `"Error: slug must be lowercase alphanumeric with hyphens only."`), progress logger function (prefix `[book-publishing]`), and top-level error handler that calls `process.exit(1)` with a message
- [x] T006 Add `parseBookYaml(slug)` function in `books/scripts/build-book.mjs`: load `books/<slug>/book.yaml` using `js-yaml`, validate required fields (`title`, `author`, `output.formats`, `chapters`), validate `chapters.length >= 2` (FR-013), throw descriptive errors on any validation failure

**Checkpoint**: Skeleton script parseable; `node books/scripts/build-book.mjs missing-slug` exits 1 with a clear error.

---

## Phase 3: User Story 1 — Compose a Book from Existing Articles (Priority: P1) 🎯 MVP

**Goal**: Running `npm run build:book -- <slug>` produces `books/<slug>/book.md`, `books/publish/<slug>/book.epub`, and `books/publish/<slug>/book.pdf`.

**Independent Test**: Create `books/test-book/book.yaml` referencing two existing articles, run `npm run build:book -- test-book`, and confirm both output files exist and the EPUB opens in a reader without errors.

### Implementation for User Story 1

- [x] T007 [US1] Add `stripFrontmatter(markdownContent)` function in `books/scripts/build-book.mjs`: uses regex `/^---[\s\S]*?---\n/` to strip YAML frontmatter. **Returns `{ body: string, frontmatter: object }`** — NOT just the body string (NEW-CR-002: `resolveChapterTitle` at T008 requires the parsed frontmatter object; returning only the body causes an unresolvable data-flow gap at T009). Parse frontmatter fields with `js-yaml.load()` on the captured frontmatter block. Log a warning if `body` is empty after stripping.
- [x] T008 [US1] Add `resolveChapterTitle(chapter, frontmatter)` function in `books/scripts/build-book.mjs`: returns `chapter.title` if defined, else `frontmatter.title` from the object returned by T007, falling back to the source filename if both are absent
- [x] T009 [US1] Add `composeBook(book, slug)` function in `books/scripts/build-book.mjs`: iterates chapters in order, loads each source file, destructures `const { body, frontmatter } = stripFrontmatter(content)`, then calls `resolveChapterTitle(chapter, frontmatter)`. Logs `[book-publishing] Composing chapter N/M: "Title"` per chapter. Warns and skips empty-body chapters. Detects duplicate `book_order` values and emits a warning (YAML declaration order as tiebreaker). Assembles `book.md` with: title page (title, subtitle, author, `---`), then chapter sections using `# Chapter N: {title}` headings with `---` separators. **Does NOT include a manual `## Table of Contents` section** — Pandoc `--toc` is the sole TOC source; a manual TOC in `book.md` produces a duplicate TOC page in PDF and a redundant TOC chapter in the EPUB body (NEW-CR-003).
- [x] T010 [US1] Add `writeCompiledBook(slug, content)` function in `books/scripts/build-book.mjs`: creates `books/<slug>/` if needed, writes composed content to `books/<slug>/book.md`, logs `[book-publishing] Writing books/<slug>/book.md`
- [x] T011 [US1] Add `renderBook(slug, book)` function in `books/scripts/build-book.mjs`: iterates `book.output.formats`, invokes Pandoc via `child_process.spawnSync` with **`{ maxBuffer: 20 * 1024 * 1024 }`** in every options object (NEW-CR-001: LaTeX verbose output exceeds 1MB default; ENOBUFS causes silent process kill with `status: null`). Format flags: epub → `--to epub3 --toc` + `--epub-cover-image <path>` if `book.cover_image` defined + `--metadata lang:<book.language||'en'>`; pdf → `--to pdf --pdf-engine=<resolved engine>` + `--metadata lang:<book.language||'en'>`. In failure collection, check `result.error?.code === 'ENOBUFS'` and emit `"Error: Pandoc output exceeded buffer limit for format '<format>'. This is a build script configuration issue, not a Pandoc rendering error."` Creates `books/publish/<slug>/` if needed, returns array of failures.
- [x] T012 [US1] Add availability checks at script startup in `books/scripts/build-book.mjs`: (a) Run `pandoc --version` via `spawnSync`; on failure log `Error: Pandoc not found. Install from https://pandoc.org/installing.html` and exit 1. Parse version string and warn if below 2.19 (NEW-HP-004: Pandoc 2.x vs 3.x EPUB3 metadata differences). (b) If `book.output.formats` includes `"pdf"`, resolve the first available PDF engine in this order: `xelatex`, `lualatex`, `pdflatex`, `typst`; on failure log an install message referencing quickstart.md and exit 1 (NEW-HP-002).
- [x] T013 [US1] Wire up the main execution flow in `books/scripts/build-book.mjs`: slug → `parseBookYaml` → availability checks (T012 logic) → `composeBook` → `writeCompiledBook` → `renderBook`. After `renderBook` returns: if failures non-empty, emit `"Warning: books/<slug>/book.md was written but not all formats rendered successfully. Resolve rendering failures before committing books/<slug>/book.md."` to stderr, exit 1 with per-format error summary. Exit 0 only when all formats succeed.
- [x] T014 [US1] Create sample book directory and fixture files:
  1. Create `books/project-mechanics/book.yaml` referencing two existing articles from `src/content/`, including `language: "en"` and `cover_image: "books/project-mechanics/cover.png"` fields
  2. Create a minimal placeholder `books/project-mechanics/cover.png` (any valid PNG; a 1×1 white pixel is sufficient — Kindle Previewer checks presence, not dimensions)
- [x] T015 [US1] Verify end-to-end with timing on a **warm-start** build: run `Measure-Command { npm run build:book -- project-mechanics }` (PowerShell) or `time npm run build:book -- project-mechanics` (bash/macOS). Confirm `books/project-mechanics/book.md` written; `books/publish/project-mechanics/book.epub` and `books/publish/project-mechanics/book.pdf` exist. Confirm elapsed time under 60 seconds warm-start (SC-001). Cold-start excluded from SLO.

**Checkpoint**: User Story 1 fully functional. EPUB and PDF generated from `book.yaml`.

---

## Phase 4: User Story 2 — Tag Articles as Book-Eligible (Priority: P2)

**Goal**: Articles with `book: true`, `book_title`, and `book_order` in frontmatter have those fields preserved in `src/data/articles.json`.

**Independent Test**: Add `book: true` and `book_order: 1` to any article's frontmatter, run `npm run generate:articles`, and confirm the values appear in `src/data/articles.json` for that article's entry.

### Implementation for User Story 2

- [x] T016 [US2] Confirm that the explicit `article` output object in `generate-articles-json.mjs` does **not** include `book`, `book_title`, `book_order`, or `web_publish` (silently absent despite Zod `.passthrough()` — see research.md Decision 7 correction and data-model.md ⚠️ NOTE). Document as confirmation that T017 and T028 are required.
- [x] T017 [US2] Update `generate-articles-json.mjs` to explicitly include `book`, `book_title`, and `book_order` in the named properties of the `article` output object (FR-009). Unconditional — Zod `.passthrough()` does NOT propagate these automatically. Note: `web_publish` propagation and filtering are handled in T028.
- [x] T018 [US2] Add `book: true`, `book_title`, and `book_order` frontmatter fields to two existing articles in `src/content/` used as verification fixtures (same articles referenced by `books/project-mechanics/book.yaml`)
- [x] T019 [US2] Run `npm run generate:articles` and verify `src/data/articles.json` entries for modified articles include all three book fields with correct values
- [x] T027 [US2] Update `generate-articles-json.mjs` to filter out any article where `frontmatter.web_publish === false` before writing the output array to `articles.json` (FR-014). Articles without `web_publish` are unaffected (default `true`). Do **not** add `web_publish` as a named output property — presence in `articles.json` implicitly signals web-published; propagating the value adds noise without information.
- [x] T028 [US2] Add `web_publish: false` to one article in `src/content/` as a verification fixture; run `npm run generate:articles` and confirm that article is **absent** from `articles.json`
- [x] T029 [US2] Verify that a `web_publish: false` article referenced as a chapter in `books/project-mechanics/book.yaml` is included correctly in the generated book — rebuild with `npm run build:book -- project-mechanics` and confirm the chapter content appears in `book.md` (the `web_publish` flag must have zero effect on composition, FR-015)
- [x] T030 [US2] Create a book-only chapter file at `books/project-mechanics/chapters/book-intro.md` (YAML frontmatter + body; no `web_publish` field needed since it is outside `src/content/`); add it as the first chapter in `books/project-mechanics/book.yaml`; rebuild and confirm it appears as Chapter 1 in both EPUB and PDF output (FR-016)

**Checkpoint**: User Story 2 and User Story 4 fully functional. Book frontmatter fields flow through to `articles.json`; `web_publish: false` articles are excluded from the website and confirmed present in book output; book-only chapter files in `books/<slug>/chapters/` compose correctly.

---

## Phase 5: User Story 3 — Preview and Validate (Priority: P3)

**Goal**: Generated EPUB3 opens in Kindle Previewer without structural errors; generated PDF is readable in a PDF viewer.

**Independent Test**: Open `books/publish/project-mechanics/book.epub` in Kindle Previewer; open `books/publish/project-mechanics/book.pdf` in a PDF viewer; confirm both pass the acceptance scenarios in spec.md.

### Implementation for User Story 3

- [ ] T020 [P] [US3] Perform manual EPUB3 validation: open `books/publish/project-mechanics/book.epub` in Kindle Previewer; verify Pandoc-generated TOC navigation, chapter start pages, zero structural errors; document result in `books/project-mechanics/VALIDATION.md`
- [ ] T021 [P] [US3] Perform manual PDF validation: open `books/publish/project-mechanics/book.pdf` in a PDF viewer; verify title page, single Pandoc-generated TOC page (no manual duplicate), chapter separators, readable content; document result in `books/project-mechanics/VALIDATION.md`
- [ ] T022 [US3] If Kindle Previewer reports structural errors after T020: (1) verify `book.yaml` has a valid `cover_image` path and the file exists; (2) verify `--epub-cover-image` and `--metadata lang:` are in the `renderBook()` epub invocation (already implemented in T011 — check args array assembly, not whether to add them); (3) run `epubcheck books/publish/project-mechanics/book.epub` for detailed structural diagnostics; (4) confirm `pandoc --version` is 2.19+ (older versions have differing EPUB3 metadata handling)

**Checkpoint**: User Story 3 complete. Both formats validated and results documented.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T023 [P] Update `README.md` with a brief "Book Pipeline" section referencing `quickstart.md`
- [x] T024 [P] Confirm `books/publish/` is git-ignored: run `git status` after a build and verify no generated book artifacts appear as untracked
- [x] T025 Run `npm run build` (full site build) and verify it completes without errors; existing blog, SEO assets, and LinkedIn carousel pipeline unaffected (SC-004)
- [x] T026 Run `npm run type-check` and `npm run lint` to confirm no TypeScript or ESLint errors from changes to `generate-articles-json.mjs`

---

## Dependencies

```
T001 → T003 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015
T004 (independent — package.json scripts change)
T001 → T002 (independent of script work)
T016 → T017 → T018 → T019 (US2 chain)
T016 → T027 → T028 (US4 web_publish chain, can run in parallel with T017 chain after T016)
T015, T028 → T029 (requires both US1 sample book and web_publish filter in place)
T015 → T030 (book-only chapter verification requires US1 working build)
T015 → T020, T021 → T022 (US3 depends on US1 sample book output)
T025 depends on T015, T019, T028 (validate no regressions)
T026 depends on T017, T027 (lint after generate-articles-json.mjs changes)
```

## Parallel Execution Opportunities

| Group | Tasks | Notes |
|---|---|---|
| Setup group | T001, T002, T003, T004 | All independent file changes |
| Script internals (after T005) | T007, T008 after T006 completes | Can be coded in parallel |
| US2 book fields | T016, then T017 chain | Sequential: audit → implement → fixture → verify |
| US4 web_publish (after T016) | T027 → T028 | Parallel with T017 chain after T016 |
| web_publish book validation | T029 | Requires T015 + T028 |
| Book-only chapters | T030 | Requires T015 only |
| Validation | T020, T021 after T015 | Fully parallel manual checks |
| Polish | T023, T024 | Fully independent |

## Key Implementation Notes (from Critic Pass 2)

Read before starting Phase 3:

- **T007 return type is mandatory**: `stripFrontmatter()` MUST return `{ body, frontmatter }`. If it returns only a string, `resolveChapterTitle()` in T008 has no frontmatter, silently breaking FR-004 for chapters without an explicit title override.
- **T009 must NOT add a manual TOC**: `book.md` intentionally has no `## Table of Contents` section. Pandoc `--toc` generates a hyperlinked TOC from actual headings. Adding a manual list produces two TOC pages in PDF and a duplicate TOC body chapter in EPUB.
- **T011 maxBuffer is not optional**: `{ maxBuffer: 20 * 1024 * 1024 }` required in every `spawnSync` call. LaTeX stdout exceeds 1MB default; ENOBUFS produces `status: null` — looks like a Pandoc crash.
- **T017 is unconditional**: `book`, `book_title`, `book_order` will NOT appear in `articles.json` without an explicit change to the named output object in `generate-articles-json.mjs`.

## Task Summary

| Metric | Value |
|---|---|
| Total tasks | 30 |
| Phase 1 (Setup) | 4 |
| Phase 2 (Foundational) | 2 |
| Phase 3 (US1 — MVP) | 9 |
| Phase 4 (US2 + US4) | 8 |
| Phase 5 (US3) | 3 |
| Phase 6 (Polish) | 4 |
| Parallelizable [P] | 13 |
| MVP scope (US1 only) | T001–T015 |
