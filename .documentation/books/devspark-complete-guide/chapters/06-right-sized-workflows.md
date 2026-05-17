---
title: "Chapter 6: Right-Sized Workflows — From Quickfix to Full Spec"
part: "Part II: The Core Workflow"
---

# Chapter 6: Right-Sized Workflows — From Quickfix to Full Spec

> **What you'll learn in this chapter:**
> - How to choose the right workflow for any development task
> - The quickfix workflow for bug fixes and small changes
> - The quick-spec route for medium-complexity work
> - The full spec workflow for major features and architectural changes
> - How `/devspark.specify` routes work and how to override them
> - Anti-patterns for each workflow level

## The Right-Sizing Problem

One of the most common objections to structured development processes is overhead. "I just want to fix a typo — I don't need a specification." This objection is correct. A typo fix does not need a specification.

DevSpark addresses this directly through right-sized workflows. The same framework that governs a complex architectural change also supports a one-line fix with zero process overhead. The key is matching the workflow to the task, not applying the same process uniformly to everything.

The process tax table that every developer implicitly maintains looks something like this:

| Task | Appropriate process overhead | What goes wrong without it |
|------|-----------------------------|-----------------------------|
| Typo fix | None | Nothing |
| Bug fix (one file) | Minimal — record the fix | Hard to trace if it recurs |
| Bug fix (multiple files) | Light spec — understand root cause | Risk of fixing symptoms, not root cause |
| New feature (well-understood) | Quick spec | Scope creep, missed requirements |
| New feature (complex) | Full spec | Architectural inconsistency, rework |
| Architectural change | Full spec + adversarial review | Irreversible decisions made without analysis |

DevSpark provides three workflow levels that map to these ranges.

## Level 1: Quickfix — Zero to Minimal Overhead

The quickfix workflow is for changes that are:
- Small (fewer than three files affected)
- Well-understood (clear root cause or requirement)
- Low-risk (no architectural implications)

Typical candidates: typo in UI text, missing null check, wrong HTTP status code in a handler, incorrect conditional in a formatter, single-file refactor of an obvious pattern.

### Running Quickfix

```text
/devspark.quickfix The status endpoint at /api/health is returning 200 even when 
the database connection is unhealthy. It should return 503 when the DB check fails.
```

The quickfix command:
1. Validates that the request is appropriately scoped for quickfix (warns if it looks bigger)
2. Creates a lightweight tracking record in `.documentation/quickfixes/`
3. Applies the fix
4. Verifies against the constitution (a quickfix still must not violate MUST requirements)
5. Marks the fix as complete

The tracking record is minimal:

```markdown
# Quickfix: Health Endpoint Status Code

**Date**: 2025-04-22
**File(s) affected**: src/api/health/handler.ts
**Fix**: Return 503 instead of 200 when database connectivity check fails
**Verified**: Constitution Section II.iii (proper HTTP status codes for service health)
```

### The Quickfix Scope Warning

If you use `/devspark.quickfix` for something that belongs in a full spec, the command will warn you:

```
This fix touches 7 files and involves changes to the authentication middleware.
This looks like a full-spec task, not a quickfix.

Recommendation: Use /devspark.specify instead.
Proceed with quickfix anyway? [y/N]
```

Accepting the override is your choice. The warning exists to prevent scope creep in the quickfix workflow, not to block you.

> **Anti-pattern:** Using quickfix for architectural changes because the full spec workflow feels like overhead. The overhead exists because architectural changes have downstream consequences. The spec is the mechanism that surfaces those consequences before they become expensive to fix.

## Level 2: Quick Spec — Medium Complexity

The quick spec route is for work that is:
- Larger than a quickfix (multiple files, multiple concerns)
- Smaller than a full spec (clear requirements, low architectural impact)
- Well-bounded (the scope is understood before starting)

Typical candidates: adding a filter to an existing list view, implementing a new API endpoint that follows established patterns, adding form validation to an existing form, updating a data model with a non-breaking change.

### Running Quick Spec

The quick spec route is selected by `/devspark.specify` automatically for appropriate requests, or you can explicitly request it:

```text
/devspark.specify --quick Add a search filter to the products list. 
Users should be able to filter by category and price range. 
The results should update without a page reload.
```

The quick spec produces a lighter artifact than the full spec:

```markdown
# Quick Spec: Product List Filters

**Status**: Draft
**Route**: quick-spec
**Created**: 2025-04-22

## Intent

Allow users to filter the product list by category and price range.
Results update dynamically without full page reload.

## Scope

- Category filter: multi-select dropdown, values from product categories
- Price range filter: min/max input, validates that min ≤ max
- Filter state persists in URL parameters (supports sharing filtered URLs)

## Constraints

- No new database indexes required (existing product table supports this)
- Must work within the existing search component architecture

## Action Plan

1. Add filter state management to `useProductList` hook
2. Create `ProductFilters` component with category and price inputs
3. Update API query parameters in the product list endpoint
4. Update URL parameter handling
5. Add filter-related tests
```

Note: the quick spec has no separate plan file. The action plan is embedded in the spec itself. This is intentional — the lightweight route optimizes for the case where requirements and technical approach are both clear enough to capture in one document.

## Level 3: Full Spec — Major Features and Architectural Changes

The full spec workflow is the complete pipeline covered in Chapter 4:

```
/devspark.specify → /devspark.clarify → /devspark.plan → /devspark.tasks → 
/devspark.implement → /devspark.create-pr → /devspark.pr-review → merge
```

This route is appropriate for:
- Features that touch multiple concerns or subsystems
- Changes with architectural implications
- Work where the requirements are not yet fully understood
- Anything that would take more than a day to implement

The overhead of the full spec workflow — the clarify step, the separate plan, the task breakdown — pays for itself by surfacing misunderstandings before they are encoded in code. The cost of fixing a misunderstanding in the spec phase is measured in minutes. The cost of fixing it after implementation is measured in hours or days.

## The Route-Aware Intake System

`/devspark.specify` is the canonical entry point for all new work. It classifies the request and recommends a route before creating any artifacts:

```
/devspark.specify Add user authentication to the admin dashboard
```

Output:
```
Classification: full-spec

Rationale: Authentication is a security-critical feature that touches middleware, 
session management, database schema (users table), and multiple UI components.
Misunderstanding requirements here has high cost. A full spec is appropriate.

Options:
  Y → Proceed with full spec
  Q → Redirect to quickfix (if you believe this is smaller than it appears)
  S → Proceed with quick spec (if you have a very clear picture of scope)

[Y/q/s]:
```

This classification is a recommendation, not a constraint. You can override it. But the AI's classification is often correct, and accepting it without argument saves rework later.

### Classification Heuristics

The intake system uses several heuristics for classification:

| Signal | Suggests |
|--------|---------|
| Single file mentioned | quickfix |
| "Bug", "typo", "wrong" | quickfix |
| "Existing feature", "add to", "update" | quick-spec |
| "New feature", "user stories" | full-spec |
| Security-related | full-spec |
| Multiple concerns in one sentence | full-spec |
| Architectural terms (middleware, schema, service) | full-spec |
| Vague requirements | full-spec (to clarify before locking in) |

## The Clarify Gate: Staying in Product Language

The clarify step (`/devspark.clarify`) is optional but often valuable. Its purpose is to resolve specification ambiguities before moving to technical planning. The critical rule: clarify stays in product language.

Good clarify inputs:
```text
/devspark.clarify Focus on edge cases: what happens if a user tries to set 
an email address that's already taken by another account?
```

```text
/devspark.clarify What are the requirements around internationalization? 
Should the profile support characters from non-Latin scripts?
```

Bad clarify inputs:
```text
/devspark.clarify Should we use Redis or database-backed sessions?
/devspark.clarify Should the API return 409 or 422 for duplicate email?
```

The second pair are implementation decisions. They belong in the plan phase. If you ask them in the clarify phase, you are locking in technical choices before the requirements are fully understood. The plan phase is designed for exactly these decisions — when you have a complete requirement set to evaluate options against.

> **Tip:** A good clarify session asks about user needs, constraints, edge cases, and acceptance criteria. It does not ask about technology choices, library preferences, or implementation patterns.

## Choosing Between Routes: A Decision Guide

When in doubt, use this decision guide:

```
Is this a single, well-understood change to one or two files?
  YES → /devspark.quickfix
  NO  → Continue

Do you have clear requirements AND clear technical approach?
  YES → /devspark.specify (will likely route to quick-spec)
  NO  → /devspark.specify (will likely route to full-spec)

Does this touch security, authentication, data integrity, or core architecture?
  YES → full-spec, even if it seems small
  NO  → Continue

Does this change the schema, public API, or shared interfaces?
  YES → full-spec
  NO  → quick-spec or quickfix depending on size

Is the scope clearly bounded AND can it be done in under half a day?
  YES → quick-spec
  NO  → full-spec
```

## Sprint Overhead Reality Check

The most common concern about DevSpark workflows is sprint overhead. Let's put numbers on it:

| Workflow | Overhead estimate | Value delivered |
|----------|------------------|-----------------|
| Quickfix | 2–3 minutes | Traceability, constitution validation |
| Quick spec | 10–15 minutes | Requirements clarity, scope control |
| Full spec | 20–30 minutes | Full traceability, architectural review, risk analysis |

These are setup costs, not total task costs. A feature that takes 8 hours to implement costs an additional 20–30 minutes of DevSpark overhead — about 5% of total time. The ROI comes from avoiding rework, which in complex features commonly runs 20–40% of total time without a structured process.

The math is straightforward: 5% overhead to avoid 20–40% rework is a good trade. The only way it isn't is if your requirements are so clear and your implementation so well-bounded that rework never happens. In practice, that's rare.

## Summary

- DevSpark provides three workflow levels: quickfix for small/well-understood changes, quick-spec for medium complexity, full spec for major features and architectural work.
- `/devspark.specify` is the canonical intake point for all work. It classifies, explains, and routes you appropriately.
- Classification is a recommendation, not a constraint. Override when you have context the AI doesn't.
- The clarify step must stay in product language. Technical questions belong in the plan phase.
- Sprint overhead (5%) consistently beats the alternative (20–40% rework) for work above the quickfix threshold.

Chapter 7 covers the quality gate commands — the critic, checker, and audit tools that verify your work before it reaches PR review.
