# Data Model: Book & Long-Form Publishing Pipeline

**Feature**: 001-book-publishing
**Date**: 2026-04-21

---

## Entities

### Book

Defined by `books/<slug>/book.yaml`. The slug is the directory name.

| Field | Type | Required | Validation | Notes |
|---|---|---|---|---|
| `title` | string | ✅ | Non-empty | Display title for title page |
| `subtitle` | string | ❌ | — | Appears below title on title page |
| `author` | string | ✅ | Non-empty | Author name for title page and EPUB metadata |
| `version` | string | ❌ | Semver-ish | e.g., `"1.0"` |
| `description` | string | ❌ | — | Used as EPUB metadata description |
| `output.formats` | string[] | ✅ | `["epub"`, `"pdf"]` subset | At least one format required |
| `chapters` | Chapter[] | ✅ | Length ≥ 2 | Ordered list; minimum 2 per FR-013 |

**Derived fields** (not in YAML):
- `slug`: directory name of `books/<slug>/`
- `outputDir`: `books/publish/<slug>/`
- `compiledPath`: `books/<slug>/book.md`

---

### Chapter

An entry in `book.yaml`'s `chapters` array.

| Field | Type | Required | Validation | Notes |
|---|---|---|---|---|
| `source` | string | ✅ | Valid relative path from repo root | e.g., `src/content/my-article.md` |
| `title` | string | ❌ | — | Overrides the article's frontmatter `title` |

**Derived fields**:
- `chapterNumber`: 1-based index in the chapters array
- `resolvedTitle`: `title` if provided, else article frontmatter `title`

---

### Article (extended frontmatter)

Existing entity in `src/content/*.md`. New optional fields added by this feature:

| Field | Type | Required | Validation | Notes |
|---|---|---|---|-|
| `book` | boolean | ❌ | — | Flags article as book-eligible |
| `book_title` | string | ❌ | — | Preferred chapter title override (informational; `book.yaml` takes precedence) |
| `book_order` | integer | ❌ | ≥ 1 | Suggested ordering hint for future auto-composition |
| `web_publish` | boolean | ❌ | `true` or `false` | Default `true`. When `false`, article is excluded from `articles.json` and all website routing/sitemap. Still a valid book chapter source (FR-014/FR-015). |
| `carousel` | boolean | ❌ | — | Pre-existing; unaffected by this feature |

⚠️ **NOTE**: These fields are **NOT** propagated automatically via Zod `.passthrough()`. The `article` output object in `generate-articles-json.mjs` uses explicit named properties — `book`, `book_title`, `book_order`, and `web_publish` must be added explicitly to that object (T017 is mandatory for the three book fields; T028 handles `web_publish` and the exclusion filter). See research.md Decision 7 correction for full explanation.

---

### Book-Only Content File

A Markdown file stored in `books/<slug>/chapters/` (or any repo-root-relative path outside `src/content/`). Not a new entity type — structurally identical to an Article (YAML frontmatter + Markdown body). The key distinction is location: these files are never scanned by `generate-articles-json.mjs` and therefore never appear on the website.

| Attribute | Value |
|---|---|
| Location | `books/<slug>/chapters/*.md` (by convention) |
| Format | Same as Article: YAML frontmatter + Markdown body |
| Web visibility | Never — not in `src/content/`, not processed by article generator |
| Book eligibility | Valid chapter source; referenced via `chapter.source` in `book.yaml` |

**When to use**: Book introductions, connecting narrative, conclusions, or any content authored specifically for the book with no intended web presence.

---

### CompiledBook (book.md)

The intermediate artifact written to `books/<slug>/book.md`.

**Structure**:
```
# {title}
## {subtitle}

By {author}

---

# Chapter 1: {resolvedTitle}

{article body — frontmatter stripped}

---

# Chapter 2: {resolvedTitle}

{article body — frontmatter stripped}

---
```

**TOC Note**: The `book.md` does NOT include a manual `## Table of Contents` section. Pandoc `--toc` is the sole TOC source — it generates a properly hyperlinked, formatted TOC from the actual heading structure at render time. A manual TOC in `book.md` would produce a duplicate TOC page in PDF output and a redundant TOC chapter in the EPUB body (NEW-CR-003 resolution).

**Properties**:
- Committed to repository (per Q2 clarification)
- Regenerated on every build run
- Consumed directly by Pandoc for rendering

---

### BookOutput

Final rendered files in `books/publish/<slug>/`.

| File | Format | Generator |
|---|---|---|
| `book.epub` | EPUB3 | Pandoc `--to epub3 --toc` |
| `book.pdf` | PDF | Pandoc `--to pdf` (LaTeX backend) |

`books/publish/` is git-ignored (generated artifact, not committed).

---

## State Transitions

### Build Script Lifecycle

```
book.yaml exists
      ↓
  [VALIDATE]  → chapter count < 2 → EXIT(1) with error
      ↓
  [COMPOSE]   → missing source file → EXIT(1) with error
      ↓         article body-only → skip with warning
  book.md written & committed
      ↓
  [RENDER LOOP] for each format:
      ├─ SUCCESS → write to books/publish/<slug>/
      └─ FAILURE → record error, continue loop
      ↓
  all formats attempted
      ↓
  any failures? → EXIT(1) with summary
  no failures?  → EXIT(0)
```

---

## Relationships

```
Book (1) ──── (N) Chapter
Chapter (1) ──── (1) Article [references by path]
Book (1) ──── (1) CompiledBook [generated]
Book (1) ──── (1..N) BookOutput [generated per format]
Article (0..N) ──── (N) Book [many-to-many via book.yaml references]
```

---

## Validation Rules Summary

| Entity | Rule | Error Behavior |
|---|---|---|
| Book | `chapters.length >= 2` | Halt before composition; EXIT(1) |
| Book | `output.formats` non-empty | Halt before rendering; EXIT(1) |
| Chapter | `source` file exists at path | Halt before composition; EXIT(1) |
| Chapter | Article has non-empty body | Skip chapter with warning; continue |
| Article | `book_order` uniqueness | Warn on duplicate; use YAML order as tiebreaker |
| Rendering | Pandoc available on PATH | Halt before rendering; EXIT(1) with install message |
