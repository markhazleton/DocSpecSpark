# Research: Book & Long-Form Publishing Pipeline

**Feature**: 001-book-publishing
**Date**: 2026-04-21
**Branch**: `001-book-publishing`

---

## Decision 1: Build Script Runtime

**Decision**: Node.js (`.mjs` ES module script)
**Rationale**: All existing build scripts in `src/scripts/` use `.mjs` ES module format (e.g., `generate-articles-json.mjs`, `generate-linkedin-post.mjs`). Using the same runtime eliminates a new dependency, shares the existing YAML/Markdown parsing patterns, and fits naturally into the `package.json` scripts ecosystem. The script will live at `books/scripts/build-book.mjs`.
**Alternatives considered**:
- Python: Already used for `render-linkedin-carousel.py`, but the majority of the pipeline is Node.js and the frontmatter/markdown parsing utilities are JS-native.
- Bash/PowerShell: Too fragile for cross-platform file I/O and YAML parsing.

---

## Decision 2: YAML Parsing for `book.yaml`

**Decision**: Use `js-yaml` (already available in the project as a transitive dependency via Vite/gray-matter; install explicitly if not direct).
**Rationale**: `gray-matter` is used project-wide for frontmatter parsing and it wraps `js-yaml`. For `book.yaml` (a pure YAML config file, not markdown), using `js-yaml` directly is cleaner. If `gray-matter` exposes its underlying js-yaml, that can be reused; otherwise `js-yaml` is a single lightweight install.
**Alternatives considered**:
- Manual YAML parsing: Fragile and error-prone for nested structures.
- TOML: Not consistent with the rest of the project's config format convention.

---

## Decision 3: Markdown Frontmatter Stripping

**Decision**: Reuse the existing `parseFrontmatter()` logic from `generate-articles-json.mjs` (extract it to a shared utility at `src/lib/parseFrontmatter.mjs`) or inline the same regex approach in the build script.
**Rationale**: The project already has a working, tested frontmatter parser that handles multi-line values, nested objects, and all article edge cases. Duplication is acceptable for an initial script; extraction to a shared utility is the cleaner path and reduces drift risk.
**Alternatives considered**:
- gray-matter directly: Would work and is cleaner, but changes a dependency surface. gray-matter is already used in the build context, making this safe.

---

## Decision 4: EPUB3 Rendering via Pandoc

**Decision**: Pandoc with `--to epub3` flag. Invoked via Node.js `child_process.execSync()` (or `spawnSync` for streaming output).
**Rationale**: Pandoc is the de-facto standard for document format conversion from Markdown. EPUB3 is the modern standard and the explicit choice from the clarification session (Q1). Pandoc handles table of contents generation natively via `--toc` flag and title page via metadata.
**Alternatives considered**:
- Calibre's `ebook-convert`: More opinionated layout engine, harder to script cleanly, larger dependency.
- Pure JS EPUB libraries (epub-gen, etc.): Less battle-tested for long-form content, require more custom work for TOC and chapter structure.

---

## Decision 5: PDF Rendering via Pandoc

**Decision**: Pandoc with an explicit PDF engine resolution order: `xelatex`, `lualatex`, `pdflatex`, then `typst`.
**Rationale**: Pandoc's LaTeX PDF pipeline produces professional print-quality output, but `pdflatex` fails on common Unicode characters that appear in real manuscripts. Prefer Unicode-capable LaTeX engines first, keep `pdflatex` as a fallback, and use `typst` only when LaTeX is unavailable. **Note**: LaTeX is a 2–4 GB install not standard for software engineers; MiKTeX on Windows performs on-demand package downloads that can extend the first-run PDF build by 3–20 minutes. The SC-001 60-second SLO applies to warm-start only.
**Alternatives considered**:
- Puppeteer/Chrome headless: Requires an npm dependency and a headless browser; overkill for initial release.
- WeasyPrint: Python-based; adds another runtime dependency. A viable no-LaTeX fallback for future increment.

---

## Decision 6: Book Directory Layout

**Decision**:
```
books/
  <slug>/
    book.yaml       # Author-maintained book specification
    book.md         # Committed compiled output (per Q2 clarification)
    chapters/       # Optional: per-chapter markdown overrides (future)

publish/
  <slug>/
    book.epub       # Final EPUB3 output
    book.pdf        # Final PDF output
```
**Rationale**: `books/` is a first-class source directory (peer to `src/`). The `books/publish/` output keeps generated book artifacts near their source while remaining explicitly git-ignored. `book.md` is committed (Q2) for auditability.
**Alternatives considered**:
- Placing `book.yaml` inside `src/content/`: Would conflate content files with book configuration. Books are compositions, not articles.
- Single `books.json` registry: Less flexible and harder to version per-book.

---

## Decision 7: `generate:articles` Extension

**Decision**: Explicitly add `book`, `book_title`, and `book_order` to the named properties of the `article` output object constructed in `generate-articles-json.mjs` (lines ~195–252).
**Rationale**: ⚠️ **CORRECTION from original plan**: The original rationale stated "`.passthrough()` means additional frontmatter fields already flow through." This is incorrect. Zod's `.passthrough()` prevents unknown fields from being *stripped during validation*, but `generate-articles-json.mjs` constructs an explicit output object with named properties (`title`, `description`, `tags`, etc.) — it does not spread all validated fields. Fields not explicitly named in the output object are silently absent from `articles.json` regardless of Zod configuration. Therefore, `book`, `book_title`, and `book_order` will **not** appear in `articles.json` without an explicit code change. T017 is a mandatory implementation task, not a conditional one.
**Alternatives considered**:
- Separate `books-articles.json`: Creates a parallel data path that diverges from the existing content model.

---

## Decision 8: Minimum Chapter Validation (FR-013)

**Decision**: Validate chapter count ≥ 2 as the first step after parsing `book.yaml`, before any file I/O or composition begins. Exit with a descriptive error: `"Error: book.yaml must define at least 2 chapters. Found: N."`
**Rationale**: Early validation prevents partial work and confusing partial output. This aligns with the fail-fast pattern used in other build scripts for missing files.

---

## Decision 9: Progress Output Format (FR-012)

**Decision**: Use `console.log()` with prefixed step labels:
```
[book-publishing] Parsing book.yaml: "AI in Application Development"
[book-publishing] Composing chapter 1/3: "AI vs Real-World Systems"
[book-publishing] Composing chapter 2/3: "Architecture Still Wins"
[book-publishing] Composing chapter 3/3: "The Illusion of Measurement"
[book-publishing] Writing book.md...
[book-publishing] Rendering EPUB3...
[book-publishing] Rendering PDF...
[book-publishing] Done. Output: books/publish/ai-in-app-dev/book.epub, books/publish/ai-in-app-dev/book.pdf
```
**Rationale**: Consistent with how the LinkedIn carousel script logs. `console.log()` in build scripts is explicitly permitted by constitution §VII. Prefixed format makes log lines filterable in CI output.

---

## Decision 10: Error Handling & Exit Behavior (FR-007 + Q4)

**Decision**: Use a `try/catch` around each Pandoc invocation in a loop over formats. Collect all errors, continue to next format, then `process.exit(1)` with a summary of all failures after all formats are attempted.
**Rationale**: Aligns exactly with Q4 answer: attempt all formats, report all failures, exit non-zero if any failed. Partial successes are written to disk so the author can inspect working outputs.

---

## Dependency Inventory

| Dependency | Already Present | Action |
|---|---|---|
| Node.js 20 | ✅ | None |
| `js-yaml` or `gray-matter` | ✅ (gray-matter in vite ecosystem) | Install `js-yaml` as direct dev dep |
| Pandoc | ❌ (developer prerequisite) | Document in quickstart |
| LaTeX (`xelatex`, `lualatex`, or `pdflatex`) or Typst | ❌ (developer prerequisite) | Document in quickstart |
