# Quickstart: Book & Long-Form Publishing Pipeline

**Feature**: 001-book-publishing
**Date**: 2026-04-21

---

## Prerequisites

Install these tools before using the book pipeline:

### 1. Pandoc

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt install pandoc

# Windows (winget)
winget install JohnMacFarlane.Pandoc
```

Verify: `pandoc --version`

> **Minimum version**: Pandoc 2.19 or later required. Pandoc 3.x is recommended and is the tested version for this pipeline. Pandoc 2.x and 3.x have differing EPUB3 metadata handling; using older versions may produce structurally different EPUB output.

### 2. LaTeX (for PDF output)

```bash
# macOS
brew install --cask mactex-no-gui

# Ubuntu/Debian
sudo apt install texlive texlive-latex-extra

# Windows
# Install MiKTeX from https://miktex.org/download
```

Verify one of: `xelatex --version`, `lualatex --version`, `pdflatex --version`, or `typst --version`

> **PDF-only alternative**: If LaTeX is unavailable, PDF can be skipped by setting `formats: [epub]` in `book.yaml` for initial testing.

> **Windows MiKTeX note**: MiKTeX downloads LaTeX packages on-demand during the first PDF run. This can add 3–20 minutes to a first-time PDF build. The 60-second SC-001 performance SLO applies only to **warm-start** builds (Pandoc and the PDF engine fully initialized). Run the build once manually before using it as a benchmark.

### 3. Install `js-yaml` dev dependency

```bash
npm install --save-dev js-yaml
```

---

## End-to-End Test Scenario

### Step 1 — Create a Book Directory

```bash
mkdir -p books/my-first-book
```

### Step 2 — Create `book.yaml`

```yaml
title: "My First Book"
subtitle: "A Practitioner's Perspective"
author: "Mark Hazleton"
version: "1.0"
description: "A collection of technical insights"
language: "en"
cover_image: "books/my-first-book/cover.png"   # optional; required for zero-error Kindle Previewer validation

output:
  formats:
    - epub
    - pdf

chapters:
  - source: src/content/ai-assisted-development-claude-and-github-copilot.md
    title: "AI-Assisted Development in Practice"

  - source: src/content/ai-and-critical-thinking-in-software-development.md
    title: "Critical Thinking in the Age of AI"
```

> **Cover image for Kindle Previewer**: To achieve zero structural errors in Kindle Previewer (SC-002), provide a cover image. Create a 1600×2560px PNG (standard KDP cover ratio) and reference it in `cover_image`. A placeholder can be any valid PNG. Without a cover image, Kindle Previewer reports a "Missing Cover" error.

### Step 3 — Run the Build

```bash
npm run build:book -- my-first-book
```

### Step 4 — Expected Output

```
[book-publishing] Parsing book.yaml: "My First Book"
[book-publishing] Composing chapter 1/2: "AI-Assisted Development in Practice"
[book-publishing] Composing chapter 2/2: "Critical Thinking in the Age of AI"
[book-publishing] Writing books/my-first-book/book.md
[book-publishing] Rendering EPUB3...
[book-publishing] Rendering PDF...
[book-publishing] Validating artifacts...
[book-publishing] Done. Output: books/publish/my-first-book/book.epub, books/publish/my-first-book/book.pdf
```

You can also run the stages separately:

```bash
npm run book:compose -- my-first-book
npm run book:render -- my-first-book
npm run book:validate -- my-first-book
npm run book:score -- my-first-book
```

### Step 5 — Validate EPUB

Open `books/publish/my-first-book/book.epub` in [Kindle Previewer](https://www.amazon.com/ap/signin?clientContext=132-1234567-1234567&openid.return_to=https%3A%2F%2Fkdp.amazon.com%2Fen_US%2Fhelp%2Ftopic%2FG202131170&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_kdp_desktop_us&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0) or any EPUB reader.

Verify:
- [ ] Title page shows title, subtitle, and author
- [ ] Table of contents lists both chapters with correct titles
- [ ] Each chapter opens correctly and contains article content
- [ ] No rendering errors reported

### Step 6 — Validate PDF

Open `books/publish/my-first-book/book.pdf` in any PDF viewer.

Verify:
- [ ] Title page present
- [ ] Chapter separators visible
- [ ] Content readable without layout artifacts

---

## Tagging Articles as Book-Eligible

In any article's YAML frontmatter:

```yaml
---
title: "AI-Assisted Development"
date: "2026-01-15"
description: "..."
tags: ["AI", "Development"]
author: "Mark Hazleton"
book: true
book_title: "AI-Assisted Development in Practice"
book_order: 1
---
```

After editing frontmatter, regenerate the article index:

```bash
npm run generate:articles
```

Verify `src/data/articles.json` includes the `book`, `book_title`, and `book_order` fields for the article.

---

## Common Errors

| Error Message | Cause | Fix |
|---|---|---|
| `Pandoc not found` | Pandoc not installed or not on PATH | Install Pandoc (see Prerequisites) |
| `Minimum 2 chapters required. Found: 1` | book.yaml has only one chapter | Add at least one more chapter entry |
| `Chapter source not found: src/content/...` | Article file path is wrong | Fix path in book.yaml (relative to repo root) |
| `No PDF engine found` | No supported PDF engine installed | Install TeX Live/MiKTeX, install Typst, or set `formats: [epub]` |

---

## Git Notes

- `books/<slug>/book.yaml` — **commit** (source of truth)
- `books/<slug>/book.md` — **commit** (auditable compiled snapshot)
- `books/publish/` — **do not commit** (add to `.gitignore` if not already present)
