---
description: Perform a full-book critique from the book manifest and chapter sources, identifying structural, narrative, voice, and product-quality weaknesses with prioritized fixes
handoffs:
  - label: Create Rewrite Plan
    agent: devspark.book-rewrite-plan
    prompt: Convert this critique into an executable book rewrite plan
  - label: Apply Revisions
    agent: devspark.write-article
    prompt: Apply the highest-priority book critique fixes to the manuscript
  - label: Run Editorial Scorecard
    agent: devspark.editorial
    prompt: Run a formal editorial scorecard on the revised book content
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. The input may be:
- A book slug, such as `project-mechanics`
- A book title, such as `Developing with DevSpark`
- A path to `books/{slug}/book.yaml`, `books/{slug}/book.md`, or a chapter file
- Empty, only if the target book is obvious from the active conversation

If the target book cannot be resolved with confidence, ask for the slug or path.

---

## Overview

This command critiques a book as a single editorial product, not as a folder of independent articles.

Goal:
Identify what prevents the book from being exceptional, memorable, coherent, and reusable as intellectual property, then provide a prioritized path to fix it.

This command does **not** rewrite chapters. It diagnoses the manuscript and produces an actionable critique suitable for `/devspark.book-rewrite-plan`.

---

## Prerequisites

Read these files before generating the critique:

| File | Purpose |
|------|---------|
| `.documentation/memory/constitution.md` | Required voice, tone, and quality authority |
| `books/{slug}/book.yaml` | Source of truth for book metadata and chapter order |
| Manifest-listed chapter files | Source manuscript content |
| `books/{slug}/book.md` | Generated manuscript snapshot; use only to detect composition/layout issues |

Use `book.yaml`. Do not look for `book.yml` unless the user explicitly provides one.

---

## Step 1 - Resolve The Book

Resolve `$ARGUMENTS` in this order:

1. If it is a path, infer `{slug}` from `books/{slug}/...`.
2. If it is a slug, require `books/{slug}/book.yaml`.
3. If it is a title fragment, search `books/*/book.yaml` titles and subtitles.
4. If no argument is provided, use the active conversation only if exactly one book is clearly implied.

Before analysis, verify:
- `book.yaml` exists
- Each `frontmatter`, `chapters`, `parts[].chapters`, and `appendices` source path exists
- The manifest order is clear
- `book.md` exists if the generated manuscript is part of the requested review

If source paths are missing, report them as a Critical Issue and continue with the available files.

---

## Step 2 - Load The Manuscript

Build the reading order from `book.yaml`:

1. `frontmatter`
2. `parts[].chapters`, preserving part order, or `chapters` if no parts exist
3. `appendices`

For each entry, capture:
- Book slug and title
- Manifest role (`frontmatter`, `chapter`, `appendix`, or part membership)
- Manifest title and chapter number if present
- Source file path
- Chapter body
- Approximate word count

Use `book.md` only as a generated artifact check. Do not treat generated `book.md` as the canonical source when chapter files are available.

---

## Step 3 - Deep Analysis (Internal Only)

Perform the analysis internally. Output only the distilled findings in Step 4.

### Book Thesis And Positioning
- What is the one-sentence core idea?
- Is it memorable, teachable, and ownable?
- Is the intended reader specific enough?
- Does the promise match the manuscript the reader actually gets?

### Story And Structure
- Is there a book-level narrative arc?
- Does each chapter advance that arc, or merely sit near the topic?
- Are frontmatter and appendices doing their proper jobs?
- Where are ideas buried, repeated, or introduced too late?

### Chapter Function
For every chapter, classify its job:
- Essential: book breaks if removed
- Supporting: useful and clearly connected
- Standalone: good article, weak book function
- Redundant: repeats existing material
- Misplaced: useful but in the wrong position

### Argument And Evidence
- Which claims are grounded in project evidence, data, dates, named systems, or explicit reasoning?
- Where does the book assert authority without showing the underlying experience?
- Where are counterarguments, trade-offs, or failure modes missing?

### Voice And Altitude
- Does the manuscript sound like Mark: first-person, practical, exploratory, specific?
- Where does it become generic documentation, textbook explanation, or AI-flavored advice?
- Where does it over-teach basics instead of showing hard-won judgment?

### Signal, Pacing, And Reader Experience
- Where does the reader lean in, skim, or disengage?
- Which sections are load-bearing?
- Which sections are padding, summary, setup, or repetition?
- Where would a reader need a diagram, table, model, or transition?

### Product Quality
- Does the book feel publication-ready as a book?
- Are the title, subtitle, table of contents, chapter openers, appendices, and generated artifacts aligned?
- Are there obvious production issues such as duplicate title pages, inconsistent numbering, stale generated output, or manifest/content drift?

---

## Step 4 - Classify Findings

Classify findings into:

1. **Critical Issues** - Fundamentally weaken the book; must fix before publication
2. **Significant Weaknesses** - Reduce credibility, coherence, or reader value
3. **Breakthrough Opportunities** - High-upside changes that could make the book more distinctive
4. **Minor Observations** - Lower-risk polish or consistency fixes
5. **Chapter-Level Actions** - Specific fixes mapped to source files

Every Critical Issue, Significant Weakness, and Chapter-Level Action must include:
- **Problem**: specific chapter, section, passage, or artifact
- **Why it matters**: consequence for reader, credibility, or book value
- **Fix**: concrete editorial action that can be executed without follow-up

Do not include generic advice such as "strengthen the narrative" unless you name exactly where and how.

---

## Step 5 - Output

Write the critique in this format:

```markdown
# Book Critique: {Book Title}

**Book**: `{slug}`
**Manifest**: `books/{slug}/book.yaml`
**Date**: {YYYY-MM-DD}
**Reviewer**: devspark.book-critique

---

## Executive Summary

{Direct assessment of the book as a product. Do not summarize the content. State the highest-leverage editorial problem and the repair path.}

## Core Idea Assessment

**Current core idea**: {one sentence}
**Strength**: {1-2 sentences}
**Failure mode**: {1-2 sentences}
**Fix**: {specific action}

## Story And Structure

{Book-level arc diagnosis, including what chapters are misplaced, redundant, or missing.}

## Reader Experience Map

| Segment | Reader State | Cause | Fix |
|---------|--------------|-------|-----|
| {chapter/range} | {lean in/skim/disengage} | {specific cause} | {specific fix} |

## Critical Issues

1. **{Issue name}**
   - **Problem**: {specific location and problem}
   - **Why it matters**: {consequence}
   - **Fix**: {specific action}

## Significant Weaknesses

1. **{Issue name}**
   - **Problem**: {specific location and problem}
   - **Why it matters**: {consequence}
   - **Fix**: {specific action}

## Breakthrough Opportunities

1. **{Opportunity name}**
   - **Why it matters**: {upside}
   - **How to execute**: {specific action}

## Chapter-Level Actions

| Priority | Source | Action | Acceptance Criteria |
|----------|--------|--------|---------------------|
| P0/P1/P2 | `books/{slug}/chapters/file.md` | {specific edit} | {observable result} |

## Voice And Positioning

{Specific voice problems and positioning fixes, grounded in the constitution.}

## Production Notes

{Generated manuscript, PDF/EPUB, manifest, numbering, TOC, title/subtitle, or artifact issues if found.}

## If You Only Fix One Thing

{Single highest-leverage change and why it matters.}

## Suggested Next Step

Run `/devspark.book-rewrite-plan` against this critique.
```

---

## Step 6 - Write The Output File

Write the critique to:

```text
books/reviews/{YYYY-MM-DD}_{slug}_book-critique.md
```

If that file already exists, append a short numeric suffix, such as `_2`.

---

## Step 7 - Report To User

After writing the file, report:

```text
Book critique complete.

  File    : books/reviews/{YYYY-MM-DD}_{slug}_book-critique.md
  Book    : {Book Title}
  Chapters reviewed: {n}

Critical issues: {n}
Significant weaknesses: {n}
Breakthrough opportunities: {n}

If you only fix one thing: {one sentence}

Suggested next step:
  /devspark.book-rewrite-plan books/reviews/{YYYY-MM-DD}_{slug}_book-critique.md
```

---

## Guidelines

- Be direct, specific, and unsentimental.
- Do not summarize the book; the author knows what they wrote.
- Evaluate the book as a system: thesis, sequence, reader experience, evidence, voice, and production quality.
- Use the constitution as the authority for voice and tone.
- Prefer fewer, sharper findings over a long list of vague observations.
- Do not invent chapter titles, file paths, evidence, or reader promises not present in the manuscript.
- Mark blocked or missing evidence clearly instead of filling gaps with speculation.
