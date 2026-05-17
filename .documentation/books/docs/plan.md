# Implementation Plan: Book & Long-Form Publishing Pipeline

**Branch**: `001-book-publishing` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-book-publishing/spec.md`

## Summary

Enable spec-driven composition of EPUB3 and PDF books from existing Markdown articles. A Node.js build script (`books/scripts/build-book.mjs`) reads a `book.yaml` manifest, strips frontmatter from referenced articles, assembles a `book.md` intermediate document (committed to the repository), and invokes Pandoc to render the final outputs into `books/publish/<slug>/`. The article generator is extended to propagate four new optional frontmatter fields (`book`, `book_title`, `book_order`, `web_publish`) into `articles.json` and to filter out articles with `web_publish: false` from the website build. Articles marked `web_publish: false` (or stored in `books/<slug>/chapters/`) remain valid book chapter sources but never appear on the website.

## Technical Context

**Language/Version**: Node.js 20 (ES Modules, `.mjs`)
**Primary Dependencies**: `js-yaml` (dev dep — YAML parsing for `book.yaml` AND frontmatter parsing in `stripFrontmatter()` via regex + `js-yaml.load()`), `gray-matter` (present in project — **NOT used by book pipeline**; frontmatter stripping done via inline regex + `js-yaml.load()` per research.md Decision 3), `child_process.spawnSync` (Node.js built-in — Pandoc invocation; `maxBuffer: 20 * 1024 * 1024` required — LaTeX verbose output exceeds 1MB default)
**Storage**: File system — `books/<slug>/book.yaml` (source), `books/<slug>/book.md` (committed compiled), `books/publish/<slug>/` (generated outputs, git-ignored)
**Testing**: Manual validation via Kindle Previewer (EPUB3) and PDF viewer (automated tests not in scope per constitution §VII Testing Exemption)
**Target Platform**: Developer workstation (cross-platform: macOS, Linux, Windows); Pandoc and LaTeX must be installed separately
**Project Type**: Build script extension to existing static site pipeline
**Performance Goals**: Full EPUB3 + PDF build completes in < 60 seconds for a book of up to 20 chapters **on a warm-start build** (Pandoc and LaTeX pre-installed and initialized). Cold-start builds — especially MiKTeX first-run on Windows — may take significantly longer and are excluded from the SC-001 SLO.
**PDF Rendering**: The build prefers Unicode-capable LaTeX engines (`xelatex`, then `lualatex`) before falling back to `pdflatex` and then `typst`.
**EPUB3 Cover Image**: `book.yaml` supports an optional `cover_image` field (repo-root-relative path). When provided, passed as `--epub-cover-image` to Pandoc. Required for zero-error Kindle Previewer validation (SC-002).
**Constraints**: Must not affect existing `npm run build` or LinkedIn carousel pipeline (SC-004); `books/publish/` output must remain git-ignored; no runtime server dependencies (Constitution §I)
**Scale/Scope**: Single-book build command; one developer workstation at a time; books up to ~20 chapters covering typical article corpus size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| §I Static-First Architecture | ✅ PASS | Build script runs at authoring time only; no runtime server dependencies introduced |
| §II Content-Driven Design | ✅ PASS | Markdown + YAML frontmatter remain the single source of truth; `book.yaml` follows the same pattern |
| §III SEO-Optimized | ✅ N/A | No new React pages introduced; book outputs are files, not web pages |
| §IV Accessibility Standards | ✅ N/A | No UI components introduced |
| §V Performance Standards | ✅ PASS | Pipeline is a build-time script; no impact on page load metrics |
| §VI Security Requirements | ✅ PASS | No secrets, no inline scripts, no new HTTP surfaces; `child_process.spawnSync` uses Pandoc from PATH (no shell injection risk when args are passed as array) |
| §VII Code Quality Standards | ✅ PASS | Script in `src/scripts/` may use `console.log()`; Node.js `.mjs` format consistent with existing scripts |
| §VIII Content Voice & Tone | ✅ N/A | Pipeline produces book files; does not generate article prose |
| §IX Dual Licensing | ✅ PASS | Pipeline code is MIT; book content inherits CC BY-NC 4.0 from existing articles |

**No constitution violations. No complexity justification required.**

## Critic Gate Mitigations

*Resolved from `gates/critic.md` (2026-04-21). All 3 critical risks addressed before implementation.*

| Risk | ID | Resolution | Artifact Updated |
|---|---|---|---|
| SC-001 60-second SLO unachievable under LaTeX cold-start | CR-001 | Qualified SC-001 to warm-start only; added cold-start caveat to spec.md, plan.md, and quickstart.md | spec.md, plan.md, quickstart.md |
| Zod `.passthrough()` misread — T017 was conditional, but book fields are silently dropped by the explicit output object | CR-002 | Corrected research.md Decision 7; made T017 unconditional; corrected T016 to describe the actual audit finding | research.md, tasks.md |
| `book.yaml` had no `cover_image` field; Pandoc EPUB3 without cover triggers Kindle Previewer “Missing Cover” error, breaking SC-002 | CR-003 | Added `cover_image` (optional) and `language` (optional) to `book.yaml` contract; updated T011 to pass `--epub-cover-image`; added Kindle Previewer guidance to quickstart.md | contracts/cli-contract.md, tasks.md, quickstart.md |

**Additional high-priority mitigations applied:**

| Concern | ID | Resolution |
|---|---|---|
| Pandoc PDF engine not controlled — non-deterministic across platforms | HP-002 | Engine selection is explicit: xelatex → lualatex → pdflatex → typst |
| Slug argument used raw in file paths — no input validation | HP-003 | Added slug regex validation (`/^[a-z0-9-]+$/`) to T005 |

## Critic Gate Mitigations — Pass 2

*Resolved from `gates/critic.md` (2026-04-22). All 3 new critical risks addressed before tasks are executed.*

| Risk | ID | Resolution | Artifact Updated |
|---|---|---|---|
| `spawnSync` default 1MB `maxBuffer` insufficient for verbose LaTeX PDF output (2–5 MB for 20-chapter builds); ENOBUFS produces opaque `status: null` failure disguised as Pandoc crash | NEW-CR-001 | Added `maxBuffer: 20 * 1024 * 1024` (20 MB) to all `spawnSync` options in T011; added ENOBUFS-specific error detection with clear user message | tasks.md T011 |
| `stripFrontmatter()` (T007) returns body string only, but `resolveChapterTitle()` (T008) requires a parsed frontmatter object — coupling gap causes mid-implementation rework at T009 | NEW-CR-002 | Revised T007 signature to return `{ body: string, frontmatter: object }`; updated T008 and T009 to destructure accordingly; no additional dependencies needed | tasks.md T007, T008, T009 |
| `book.md` manually assembles `## Table of Contents` bullet list AND T011 passes `--toc` to Pandoc — produces two TOC pages in PDF and redundant TOC chapter in EPUB body | NEW-CR-003 | **TOC Strategy Decision**: Removed manual `## Table of Contents` section from `book.md` assembly in T009; Pandoc `--toc` is the sole TOC source (hyperlinked, correctly formatted from actual headings). Updated data-model.md CompiledBook structure | tasks.md T009, T011, data-model.md |

**Additional high-priority mitigations applied (pass 2):**

| Concern | ID | Resolution |
|---|---|---|
| `data-model.md` Article section still claims passthrough propagates book fields automatically (incorrect — corrected in research.md Decision 7 but not in data-model.md) | NEW-HP-001 | Added ⚠️ NOTE to data-model.md Article section pointing to research.md Decision 7 correction | data-model.md |
| T012 checks Pandoc availability but not PDF engines; missing LaTeX produces opaque Pandoc internal error | NEW-HP-002 | Extended T012 to check `xelatex`, `lualatex`, `pdflatex`, then `typst` when `output.formats` includes `"pdf"`; emits install message referencing quickstart.md | tasks.md T012 |
| T022 instructs developer to add `--epub-cover-image` and `--metadata` flags that are already implemented in T011 — stale remediation guidance | NEW-HP-003 | Rewrote T022 to describe what to investigate when cover_image is configured but errors persist (epubcheck, path validation) | tasks.md T022 |
| Pandoc minimum version unpinned; Pandoc 2.x vs 3.x have differing EPUB3 metadata behavior | NEW-HP-004 | Added Pandoc minimum version (2.19+) to quickstart.md Prerequisites; added version check guidance to T012 | quickstart.md, tasks.md T012 |

## Project Structure

### Documentation (this feature)

```text
specs/001-book-publishing/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer setup and test scenario
├── contracts/
│   └── cli-contract.md  # CLI command schema and book.yaml contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task list (generated by /devspark.tasks)
```

### Source Code (repository root)

```text
books/                          # NEW — book source directory
  <slug>/
    book.yaml                   # Author-maintained book spec (committed)
    book.md                     # Compiled intermediate (committed, regenerated on build)
    chapters/                   # OPTIONAL — book-only Markdown files (never web-published)

src/
  scripts/
    build-book.mjs              # NEW — book build script
    generate-articles-json.mjs  # MODIFIED — add book frontmatter propagation, web_publish filter

dist/                           # Existing build output (git-ignored)
  books/
    <slug>/
      book.epub                 # NEW — generated EPUB3
      book.pdf                  # NEW — generated PDF

package.json                    # MODIFIED — add "build:book" script
```

**Structure Decision**: Single-project layout. The `books/` directory is a peer to `src/` containing configuration and committed compiled output. All generated artifacts go to `books/publish/`, which is explicitly git-ignored.

## Complexity Tracking

No constitution violations. No additional complexity justification required.
