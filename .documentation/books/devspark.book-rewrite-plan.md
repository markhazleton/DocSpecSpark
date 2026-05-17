---
description: Convert a book critique into a sequenced, file-specific rewrite plan with task priorities, acceptance criteria, and validation steps
handoffs:
  - label: Apply Revisions
    agent: devspark.write-article
    prompt: Apply the rewrite plan tasks to the book manuscript in priority order
  - label: Rebuild Book
    agent: devspark.implement
    prompt: Regenerate the book Markdown, EPUB, and PDF after the rewrite tasks are complete
  - label: Re-critique Book
    agent: devspark.book-critique
    prompt: Re-run the full-book critique after the rewrite plan has been implemented
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding. The input may be:
- A path to a critique file, usually `books/reviews/{date}_{slug}_book-critique.md`
- Raw critique text pasted inline
- A book slug or title, in which case locate the newest matching critique in `books/reviews/`
- Empty, only if the active conversation contains a complete critique

If no critique can be resolved, ask for the critique file path or book slug.

---

## Overview

This command turns a book critique into an executable rewrite plan.

Goal:
Convert editorial findings into sequenced, file-specific tasks that can be implemented without reinterpreting the critique.

This command does **not** rewrite the manuscript. It produces the plan that guides rewriting.

---

## Prerequisites

Read these files before generating the plan:

| File | Purpose |
|------|---------|
| Critique input | Source findings and priorities |
| `.documentation/memory/constitution.md` | Voice and tone authority |
| `books/{slug}/book.yaml` | Source of truth for title, sequence, and source paths |
| Manifest-listed chapter files | Used only to validate task scope and file paths |

If the critique does not identify a slug, infer it from file names, manifest titles, or source paths. If inference is ambiguous, ask for the slug.

---

## Step 1 - Resolve Inputs

Resolve `$ARGUMENTS` in this order:

1. If it is a file path, read that critique.
2. If it is inline critique text, use it directly.
3. If it is a slug or title, find the newest matching file in `books/reviews/`.
4. If it is empty, use the active conversation only if it contains a complete critique.

Then resolve the book manifest:
- Require `books/{slug}/book.yaml`.
- Load the manifest order.
- Validate that all task scopes reference real manifest-listed files when possible.

Use `book.yaml`. Do not refer to `book.yml`.

---

## Step 2 - Parse The Critique

Extract and preserve:
- Executive summary problem
- Core idea assessment
- Critical Issues
- Significant Weaknesses
- Breakthrough Opportunities
- Chapter-Level Actions
- Voice and positioning notes
- Production notes
- "If You Only Fix One Thing"

If the critique contains vague items, convert them into executable tasks only when the surrounding text provides enough specificity. Otherwise mark the task as **Blocked** and state what decision or evidence is missing.

---

## Step 3 - Normalize Task Types

Every task must fit one of these types:

- **Structure**: reorder, split, merge, cut, add missing bridge, change chapter role
- **Core Idea**: sharpen thesis, name model, repeat book promise, clarify reader payoff
- **Narrative**: replace generic opening, add project scene, create transition, improve chapter close
- **Evidence**: add real project example, metric, date, trade-off, counterexample, or explicit reasoning
- **Voice**: remove generic/prescriptive language, restore first-person practitioner voice
- **Signal**: cut repetition, summary, throat-clearing, excessive bold, or decorative sections
- **Production**: manifest, title/subtitle, numbering, TOC, generated `book.md`, EPUB, or PDF issue

Do not create broad tasks such as "improve Chapter 4." Each task must name the specific edit.

---

## Step 4 - Sequence Work

Order tasks by dependency and impact:

1. **Phase 0 - Production And Source Integrity**
   - Fix manifest/source mismatches, stale generated files, duplicate title pages, numbering, or artifact problems that would distort review or build output.
2. **Phase 1 - Structural Fixes**
   - Reorder, merge, split, cut, or bridge chapters/sections before line editing.
3. **Phase 2 - Core Idea Reinforcement**
   - Clarify the book thesis, reader promise, named frameworks, and recurring concepts.
4. **Phase 3 - Narrative And Evidence**
   - Add concrete scenes, project evidence, counterarguments, transitions, and stronger chapter openings/closes.
5. **Phase 4 - Voice And Positioning**
   - Restore Mark's first-person exploratory voice and remove generic documentation tone.
6. **Phase 5 - Final Polish**
   - Tighten language, remove banned phrases, reduce excessive bold, and clean headings.
7. **Phase 6 - Validation**
   - Regenerate and validate book artifacts.

Tasks in earlier phases should unblock later tasks. Do not bury structural problems under polish.

---

## Step 5 - Output

Write the plan in this format:

````markdown
# Book Rewrite Plan: {Book Title}

**Book**: `{slug}`
**Manifest**: `books/{slug}/book.yaml`
**Source Critique**: `{critique path or inline}`
**Date**: {YYYY-MM-DD}
**Planner**: devspark.book-rewrite-plan

---

## Rewrite Strategy

{Short explanation of the sequencing logic. Name the highest-risk dependency.}

## Priority Summary

| Priority | Count | Meaning |
|----------|-------|---------|
| P0 | {n} | Must complete before publication or before other rewrite work |
| P1 | {n} | High-impact book quality improvements |
| P2 | {n} | Useful polish or enhancement |
| Blocked | {n} | Needs author decision or missing evidence |

## Phase 0 - Production And Source Integrity

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|
| BRP-000 | P0 | `path` | {specific action} | {observable result} |

## Phase 1 - Structural Fixes

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|
| BRP-001 | P0/P1/P2 | `path` | {specific action} | {observable result} |

## Phase 2 - Core Idea Reinforcement

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|

## Phase 3 - Narrative And Evidence

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|

## Phase 4 - Voice And Positioning

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|

## Phase 5 - Final Polish

| ID | Priority | Scope | Task | Acceptance Criteria |
|----|----------|-------|------|---------------------|

## Phase 6 - Validation

Run these checks after implementation:

```bash
npm run book:all -- {slug}
npm run type-check
npm run lint
```

If the rewrite changes markdown sources, confirm:
- `books/{slug}/book.md` regenerated from manifest sources
- `books/publish/{slug}/book.epub` regenerated
- `books/publish/{slug}/book.pdf` regenerated
- No duplicate title page or duplicate chapter numbering appears in the generated output

## Blocked Decisions

| Decision | Why It Blocks Work | Required Answer |
|----------|--------------------|-----------------|
| {decision} | {reason} | {needed answer} |

## Implementation Notes

- Work P0 tasks first.
- Do not line-edit sections scheduled for structural movement until the movement is complete.
- Preserve YAML frontmatter and manifest source paths unless the task explicitly changes them.
- Keep factual claims, dates, project names, code, links, and commands intact unless the task explicitly calls for correction.
````

Omit empty task rows, but keep the phase headings so the plan remains predictable.

---

## Step 6 - Write The Output File

Write the plan to:

```text
books/reviews/{YYYY-MM-DD}_{slug}_rewrite-plan.md
```

If that file already exists, append a short numeric suffix, such as `_2`.

---

## Step 7 - Report To User

After writing the file, report:

```text
Book rewrite plan complete.

  File    : books/reviews/{YYYY-MM-DD}_{slug}_rewrite-plan.md
  Book    : {Book Title}
  Source  : {critique path or inline}

P0 tasks: {n}
P1 tasks: {n}
P2 tasks: {n}
Blocked decisions: {n}

Start with: {first P0 task id and summary}
```

---

## Guidelines

- Make tasks executable, not aspirational.
- Every task needs a scope, action, and acceptance criteria.
- Keep one task to one coherent edit. Split multi-chapter or multi-file work unless the files must move together.
- Preserve the critique's priority order unless dependency order requires a different sequence.
- Do not invent missing evidence. Add a blocked decision when the author must supply a story, metric, or position.
- Use the constitution as the authority for voice, not generic writing advice.
- Include validation steps that match the current book pipeline.
