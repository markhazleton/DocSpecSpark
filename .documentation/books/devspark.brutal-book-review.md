---
description: Produce a no-nonsense, high-standards critique of a book or manuscript — identifying structural flaws, argument gaps, and clarity failures with precise, actionable guidance to fix each one
handoffs:
  - label: Apply Revisions
    agent: devspark.write-article
    prompt: Apply the brutal book review critique suggestions to revise the content
  - label: Run Editorial Scorecard
    agent: devspark.editorial
    prompt: Run a formal editorial scorecard on the content I just reviewed
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input may be:
- A path to a manuscript file
- Raw manuscript text pasted inline
- A book title or slug to locate in the repo

---

## Overview

This command produces a **no-nonsense, high-standards critique** of a book or manuscript. The goal is not to praise or summarize — it is to:

> **Identify what prevents this work from being exceptional, and provide precise, actionable guidance to fix it.**

This is the feedback a senior editor, architect, or executive reviewer gives when time is limited, standards are high, and "good enough" is not acceptable.

---

## Prerequisites

Read these files **before generating any critique**:

| File | Purpose |
|------|---------|
| `.documentation/memory/constitution.md` | **REQUIRED** — Voice and quality standards are the authority for tone judgments |
| Manuscript file (from `$ARGUMENTS`) | **REQUIRED** — The content under review |

---

## Step 1 — Identify the Manuscript

Parse `$ARGUMENTS` for:
- A file path — read the file directly
- Inline content — use it as-is
- A slug or title — search `books/` and `src/content/` for a match
- Empty — ask: "Please provide the manuscript content or file path to review."

Read the full content before proceeding to Step 2.

---

## Step 2 — Deep Analysis (Internal — Do Not Output)

Work through all four lenses internally. Output only the distilled findings in Step 3.

### 2a. Structural Integrity

- Does the work have a clear thesis or central argument?
- Does each chapter or section advance that argument, or repeat it?
- Is there a logical progression from opening to close?
- Where does structure break down — redundant sections, misplaced content, missing transitions?

### 2b. Argument and Evidence

- Are claims supported with evidence, examples, or reasoning?
- Where does the author assert without justifying?
- Are counter-arguments acknowledged?
- Where does reasoning rely on appeals to authority or vague generalization?

### 2c. Clarity and Language

- Flag vague or empty language: "leverage", "empower", "transform", "holistic", "synergy", "best practices", "next-level"
- Where does jargon obscure meaning rather than carry it?
- Where is a sentence doing three things when it should do one?
- Where would a plain rewrite communicate the same idea more powerfully?

### 2d. Signal vs. Noise

- What is load-bearing (removes understanding if cut) versus decorative (can be deleted without loss)?
- Where is the author padding — restating, hedging, circling back unnecessarily?
- What is the highest-value content and is it positioned for impact?

---

## Step 3 — Select Issues by Priority

From Step 2, classify all findings into:

1. **Critical Issues** — Fundamentally undermine the work (must fix before publication)
2. **Significant Weaknesses** — Patterns that reduce credibility or value (should fix)
3. **Minor Observations** — Lower-priority polish items (nice to fix)
4. **One Redeeming Quality** — What genuinely works (maximum one item)

Each Critical or Significant issue must be:
- Located in the text by chapter, section, or passage
- Diagnosed at root cause, not just symptom
- Fixable through specific editorial action

---

## Step 4 — Write the Critique

### Output Format

```markdown
# Brutal Book Review: {Title}

**Content**: {filename or description}
**Date**: {YYYY-MM-DD}
**Reviewer**: devspark.brutal-book-review

---

## Critical Issues

Issues that fundamentally undermine the work. Fix before publication.

1. **{Issue Name}**
   **Problem**: {specific location and what is wrong}
   **Why it matters**: {consequence for the reader or the work's credibility}
   **Fix**: {concrete rewrite direction or structural change}

2. {repeat as needed}

---

## Significant Weaknesses

Patterns that reduce credibility or value.

1. **{Issue Name}**
   **Problem**: {specific location and what is wrong}
   **Why it matters**: {consequence}
   **Fix**: {concrete action}

2. {repeat as needed}

---

## Minor Observations

Lower-priority items.

1. {brief item with fix}
2. {brief item with fix}

---

## One Redeeming Quality

{Maximum one item. Name it specifically — not "the writing is clear" but "the opening case study in Chapter 2 is the most load-bearing section in the book and earns its length."}

---

## If You Only Fix One Thing

{The single highest-leverage change, with a one-sentence justification.}
```

**Hard constraints:**
- Do not summarize the book's content
- Do not flatter
- Do not hedge — say exactly what is wrong and how to fix it
- Reference specific passages, chapters, or sections by name
- Every critique must include the problem, why it matters, and exactly what to do
- Maximum response length: 800 words

**Tone**: Direct. Honest. Respectful of the author's effort, uncompromising on quality.

---

## Step 5 — Write the Output File

Write the critique to:

```
books/reviews/{YYYY-MM-DD}_{slug}_review.md
```

Check if the directory exists; create it if missing.

---

## Step 6 — Report to User

After writing the file:

```
Brutal book review complete.

  File    : books/reviews/{YYYY-MM-DD}_{slug}_review.md
  Content : {title or filename}

Critical issues found: {n}
Significant weaknesses: {n}
Minor observations: {n}

If you only fix one thing: {one sentence}

Suggested next steps:
  /devspark.editorial  — formal editorial scorecard
  /devspark.write-article  — apply revisions in a new draft
```

---

## Guidelines

### Signal Over Noise

Prioritize findings by impact, not quantity. Three precise critical issues are more valuable than a list of twenty vague observations.

### Specificity is Non-Negotiable

Every fix must be concrete enough to execute without follow-up. "Tighten the argument" is not actionable. "Cut the three-paragraph restatement of the thesis in Chapter 4, Section 2 — the reader already has it from Chapter 1" is.

### What This Command Does NOT Do

- Rewrite content — that belongs to the author or `/devspark.write-article`
- Check factual accuracy — that requires domain expertise
- Produce a pass/fail score — use `/devspark.editorial` for that
- Summarize the book — the author already knows what they wrote

---

## Context

$ARGUMENTS
