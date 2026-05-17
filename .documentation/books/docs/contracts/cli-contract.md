# CLI Contract: build-book script

**Feature**: 001-book-publishing
**Date**: 2026-04-21

---

## Command

```bash
node books/scripts/build-book.mjs <slug>
node books/scripts/build-book.mjs <slug> --compose-only
node books/scripts/build-book.mjs <slug> --render-only
node books/scripts/validate-book.mjs <slug>
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `<slug>` | ✅ | Directory name under `books/` matching the target book |
| `--compose-only` | No | Write only `books/<slug>/book.md` |
| `--render-only` | No | Render and validate from an existing `book.md` |

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | All formats rendered successfully |
| `1` | Any validation, composition, or rendering failure |

### Standard Output (success path)

One progress line per major step, prefixed with `[book-publishing]`:

```
[book-publishing] Parsing book.yaml: "<Book Title>"
[book-publishing] Composing chapter N/M: "<Chapter Title>"
[book-publishing] Writing books/<slug>/book.md
[book-publishing] Rendering EPUB3...
[book-publishing] Rendering PDF...
[book-publishing] Validating artifacts...
[book-publishing] Done. Output: books/publish/<slug>/book.epub, books/publish/<slug>/book.pdf
```

### Standard Error (failure path)

Human-readable messages to `stderr`, one per failure:

```
Error: book.yaml not found at books/<slug>/book.yaml
Error: Chapter source not found: src/content/missing-article.md
Error: Minimum 2 chapters required. Found: 1.
Error: Pandoc not found. Install from https://pandoc.org/installing.html
Error: Pandoc rendering failed for format "pdf": <pandoc stderr>
```

---

## book.yaml Schema Contract

```yaml
title: string          # required, non-empty
subtitle: string       # optional
author: string         # required, non-empty
version: string        # optional, e.g. "1.0"
description: string    # optional, used as EPUB metadata
language: string       # optional, IETF language tag, e.g. "en" (default: "en"); used as dc:language in EPUB3 metadata
cover_image: string    # optional, repo-root-relative path to cover image PNG/JPEG; passed as --epub-cover-image to Pandoc; REQUIRED for zero-error Kindle Previewer validation (SC-002)
publisher: string      # optional, EPUB/PDF metadata
rights: string         # optional, EPUB/PDF metadata
identifier: string     # optional, ISBN/UUID/URI metadata
date: string           # optional, publication date metadata
subjects: string[]     # optional, repeated subject metadata

output:
  formats:             # required, array with at least one entry
    - epub             # EPUB3 output
    - pdf              # PDF output via a Unicode-capable LaTeX engine when available

frontmatter:           # optional, unnumbered sections before Chapter 1
  - source: string
    title: string
    role: string       # optional, e.g. foreword or introduction

chapters:              # required, minimum 2 entries
  - source: string     # required, repo-root-relative path to .md file
    title: string      # optional, overrides article frontmatter title; do not include "Chapter N:"
    number: string     # optional explicit chapter label, e.g. "2B"

appendices:            # optional, rendered after chapters as Appendix A/B/C...
  - source: string
    title: string      # do not include "Appendix A:"
```

---

## `npm run` Integration

The build command MUST be registered in `package.json` as:

```json
{
  "build:book": "node books/scripts/build-book.mjs",
  "book:compose": "node books/scripts/build-book.mjs",
  "book:render": "node books/scripts/build-book.mjs",
  "book:validate": "node books/scripts/validate-book.mjs",
  "book:score": "python books/scoring/run_book_scoring.py --score-only",
  "book:all": "node books/scripts/build-book.mjs"
}
```

Usage: `npm run build:book -- <slug>`

---

## Article Frontmatter Extension Contract

Optional fields added to article YAML frontmatter for book pipeline integration:

```yaml
book: true             # boolean — marks article as book-eligible
book_title: string     # optional — preferred chapter title
book_order: integer    # optional — ordering hint (≥1)
web_publish: false     # boolean, default true — when false, excluded from articles.json,
                       # sitemap, and web routing; still valid as a book chapter source
```

`book`, `book_title`, and `book_order` are propagated into `articles.json`. `web_publish` is NOT propagated — presence in `articles.json` implicitly means `web_publish: true`. Articles with `web_publish: false` are filtered out of `articles.json` entirely before it is written.
