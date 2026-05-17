---
title: "Chapter 13: Lifecycle Commands — Release, Harvest, and Evolution"
part: "Part IV: Advanced Patterns"
---

# Chapter 13: Lifecycle Commands — Release, Harvest, and Evolution

## Why Lifecycle Commands Matter

The core DevSpark workflow (specify → plan → implement → review → merge) creates artifacts: specs, plans, tasks, gate outputs. Over time, these artifacts accumulate. Some remain relevant. Others become stale — they describe features that were implemented months ago and have since been changed or deprecated. Without a lifecycle management process, `.documentation/` becomes a graveyard of outdated specs and partial plans.

On a recent project with a team of eight, by sprint 12 we had 47 specs scattered across three directories, most of them marked Complete. The problem was we couldn't tell which had actually shipped, which had been superseded, and which described features that had changed so significantly that the specs were actively misleading. New team members were reading stale specs and making implementation decisions based on them. That's the specific pain these commands were built to address. The lifecycle commands run after every sprint to archive completed specs, discard stale ones, and evolve the governance rules.

## `/devspark.release`: End-of-Sprint Archival

In my experience, by sprint 12 most teams have lost track of which specs actually shipped versus which were superseded or abandoned. Release prevents that. The release command runs at the end of a sprint to archive completed specs and generate release documentation.

```text
/devspark.release
```

### What Release Does

The archival side of release is more constrained than it first appears. Release identifies specs marked Complete and validates them against the task checklist — a spec is only archivable if all tasks are actually done. This prevents the common failure mode of marking a spec Complete while leaving edge cases or cleanup tasks unchecked. Once validated, completed spec directories move to `.documentation/specs/archived/` under a version-tagged path, so the living directory stays current and the archive path tells you exactly which release each spec shipped with.

The documentation side synthesizes completed specs into user-facing release notes and updates `CHANGELOG.md`. What I've found useful here is that release doesn't just copy spec content — it generates notes in user-facing language, which forces a useful translation from implementation framing to outcome framing. It also proposes a semantic version bump based on the nature of changes: patch for bug fixes, minor for features, major for breaking changes. The proposal is always human-reviewable before it's applied.

The governance side handles architectural decisions captured during planning. Release reads plan files for significant architectural decisions and formats them as ADRs if they don't already have one. The trade-off here is worth naming: this extraction is best-effort — release can identify decisions that were explicitly flagged during planning, but it can't recover reasoning that was never written down. That's one reason the planning commands encourage explicit decision capture rather than leaving it implicit in the implementation.

### Release Output

```markdown
## Release: v1.3.0 — 2025-04-22

### Features

**User Profile Page** (spec: user-profile)
Allow users to view and update their display name and email address.
Includes validation, error handling, and rate limiting on the email update endpoint.

**Product List Filters** (spec: product-filters)  
Filter the product list by category and price range.
Results update dynamically. Filter state persists in URL parameters.

### Bug Fixes

**Health Endpoint Status** (quickfix: health-endpoint-503)
The /api/health endpoint now returns 503 when the database connection is unhealthy.

### Archived Specs

- .documentation/specs/user-profile/ → .documentation/specs/archived/v1.3.0/user-profile/
- .documentation/specs/product-filters/ → .documentation/specs/archived/v1.3.0/product-filters/

### Decisions Extracted

- ADR-007: Email verification deferred — Security vs. scope trade-off
  See: .documentation/decisions/ADR-007.md

**Proposed version**: v1.3.0 (minor release — new features, no breaking changes)
```

### What Release Won't Archive

- Specs with `Status: Draft` or `Status: In Progress` — these are actively being worked
- Specs with unchecked tasks despite a `Complete` status
- Specs that have been explicitly excluded

If incomplete specs are found on main, the release command warns:

```
Warning: 1 spec on main branch is not Complete:

  .documentation/specs/payment-integration/spec.md (Status: In Progress)
  
This spec will NOT be archived. Either complete it before release or
move it to a new sprint and update its branch association.

Proceeding with release of 2 complete specs...
```

Release is designed to run at sprint end, when you have a stable set of completed work to archive. Once you've run release, the next command to reach for is harvest — which cleans up the specs that didn't make the cut and extracts reusable knowledge from the planning process.

## `/devspark.harvest`: Knowledge-Preserving Cleanup

The harvest command is the canonical ongoing cleanup workflow. Unlike release (which runs on a sprint cadence), harvest can run anytime the repository needs housekeeping.

```text
/devspark.harvest
```

### What Harvest Does

Harvest performs a comprehensive cleanup:

1. **Identifies stale artifacts**: Specs and plans that have been superseded, decisions that reference deleted code, temporary analysis files
2. **Extracts knowledge before deletion**: For anything being removed, harvest first checks whether it contains insights that should be preserved — in a decision record, in the constitution, or in architectural documentation
3. **Consolidates redundancy**: Multiple specs that describe the same feature (e.g., a spec and its multiple revision drafts) are consolidated
4. **Updates CHANGELOG**: Ensures that completed work captured only in specs is reflected in CHANGELOG
5. **Archives or removes**: Moves archivable content to the archive hierarchy and removes genuinely stale content
6. **Reports what changed**: Provides a summary of everything that was moved, archived, or deleted

### The Knowledge Preservation Principle

The key design principle of harvest is: **never delete information without checking whether it has value**. This is why harvest is not just `rm -rf .documentation/specs/done/`. It actively reads the content being removed and asks: does this contain architectural reasoning, decision context, or institutional knowledge that should be preserved?

If it does, harvest captures that knowledge in a permanent artifact (an ADR, a constitution amendment, or a documentation note) before removing the source.

### Harvest Report Example

```markdown
## Harvest Report — 2025-04-22

### Specs Archived (2)
- auth-refactor/ → archived/2025-04/ (Complete, merged 2025-03-15)
- password-reset/ → archived/2025-04/ (Complete, merged 2025-02-28)

### Knowledge Extracted Before Archive
- auth-refactor/plan.md contained the rationale for choosing JWT over sessions
  → Created ADR-008: JWT Token Strategy
  → Added principle to constitution: "Session tokens MUST use JWT with 15-minute expiry"

### Files Removed (5)
- specs/auth-refactor/gates/critic-v1.md (superseded by critic-v2.md in same directory)
- specs/password-reset/notes-alice.md (working notes, no permanent value)
- docs/temp-analysis-2025-01.md (temporary analysis file, referenced content extracted)

### CHANGELOG Updates (1)
- auth-refactor feature was Complete but not in CHANGELOG — added under v1.2.0 section

### No Action Needed (3)
- specs/payment-integration/ — Status: In Progress, not archivable
- decisions/ADR-005.md — Current, references active code
- memory/constitution.md — Current, reviewed, no updates needed
```

The harvest report is saved to `.documentation/` and can be reviewed before any permanent changes are committed.

> **Tip:** Run harvest at the end of a sprint, after release. Release archives the sprint's completed specs. Harvest cleans up any remaining stale content and ensures knowledge is preserved properly.

## `/devspark.commit-audit`: Repository Health Analysis

The commit audit command analyzes the repository's git commit history for workflow signals, hygiene patterns, and delivery metrics.

```text
/devspark.commit-audit
```

Or with a scope:

```text
/devspark.commit-audit --since 2025-01-01 --author alice
/devspark.commit-audit --branch feature/payment-integration
```

### What Commit Audit Analyzes

- **Conventional commit compliance**: What percentage of commits follow `type(scope): description` format
- **Commit message quality**: Average message length, presence of body, presence of issue references
- **PR merge patterns**: Direct-to-main merges vs. PR merges, PR size distribution
- **Spec compliance signals**: Are commits prefixed with spec references? Are spec status transitions reflected in commits?
- **Workflow violations**: Large commits that should have been multiple PRs, commits on main without PR review

### Example Output

```markdown
## Commit Audit: main (last 90 days)

**Period**: 2025-01-15 → 2025-04-15
**Total commits**: 183
**Conventional commits**: 180 (98.4%)
**PR-merged commits**: 178 (97.3%) — 5 direct commits to main ⚠️

### Commit Type Distribution
  feat: 67 (36.6%)    chore: 41 (22.4%)    fix: 28 (15.3%)
  refactor: 22        docs: 18              test: 7

### PR Health
  Average PR size: 312 lines changed (healthy range: 100–500)
  Largest PR: 2,847 lines — suggests spec decomposition was insufficient
  Smallest PR: 3 lines — appropriate for quickfix

### Direct-to-Main Commits (5) — requires investigation
  a1b2c3d — "quick hotfix" (2025-03-22) — bypassed PR review
  e4f5g6h — "fix typo in README" (2025-02-14) — appropriate exception?
  [3 more...]

### Spec Compliance Signal
  42% of feat: commits reference a spec in the message body
  Recommendation: Use conventional commits with spec references for traceability:
  "feat(user-profile): implement profile edit form [spec: user-profile]"

### Overall Repository Health: 84/100
```

## `/devspark.repo-story`: Evidence-Based Repository Narrative

The repo story command generates a narrative about the repository's evolution, based on git history, spec artifacts, and commit analysis.

```text
/devspark.repo-story
```

This is useful for:
- Onboarding new team members who need historical context
- Generating documentation for project handoffs
- Creating portfolio-quality project descriptions
- Retrospectives and post-mortems

### What Repo Story Generates

The output is a structured narrative document that includes:

**Project Overview**: What the repository does, why it exists, who maintains it

**Evolutionary Timeline**: A chronological narrative of how the project developed, keyed to significant commits, merged specs, and version milestones

**Architecture Decisions**: A synthesized summary of the ADRs and decisions visible in the git history and documentation

**Developer FAQ**: Questions that a new developer would ask, answered from the evidence in the repository (not from assumptions)

**Current State**: Health metrics, open specs, recent activity

```markdown
## Repository Story: payment-platform

**Maintainer**: Platform Team | **Started**: 2024-09-15 | **Last Release**: v2.3.1 (2025-04-18)

### What This Repository Does

The payment-platform repository houses the customer-facing payment processing
API and its associated admin tooling. It handles payment intake, routing to
payment processors (Stripe for cards, Plaid for ACH), and reconciliation.

As of v2.3.1, the platform processes approximately [X] transactions per day
with [X]ms median latency. It is PCI DSS Level 1 compliant.

### How It Evolved

The project began in September 2024 as a minimal payment intake endpoint
built on Node.js + Express. The first 47 commits established the basic 
infrastructure: payment intake, Stripe integration, and webhook handling.

The architectural shift to a service layer pattern came in November 2024
(ADR-003), prompted by a failure in direct-handler database access that
caused a production incident. The refactor took 3 weeks and 12 PRs, but
fundamentally changed how the codebase is structured...
[continues]
```

## `/devspark.evolve-constitution`: Closing the Governance Loop

After running the project through multiple sprints and accumulating PR review findings, the constitution evolves to reflect what you've learned.

```text
/devspark.evolve-constitution
```

Or with specific input:

```text
/devspark.evolve-constitution Based on the last sprint's PR reviews, propose amendments 
focused on the authorization and session management findings.
```

### What Evolution Does

1. **Reads PR review history**: Scans `.documentation/specs/*/` for PR review outputs
2. **Identifies patterns**: Groups findings that point to the same gap
3. **Proposes amendments**: Drafts constitution changes that would prevent the recurring findings
4. **Estimates impact**: Predicts how many past findings each amendment would catch
5. **Outputs a proposal**: A human-reviewable amendment proposal, not an automatic change

### Example Amendment Proposal

```markdown
## Constitution Evolution Proposal

**Based on**: 6 PR reviews (2025-03-01 → 2025-04-22)
**Recurring patterns**: 3 identified

---

### Proposed Amendment 1: Authorization Requirements (HIGH priority)

**Pattern**: 3 of 6 PR reviews contained findings about missing authorization checks.
All three followed the same pattern: endpoint added, authenticated, but not 
checked that the authenticated user has permission to perform the action.

**Proposed addition to Section I (Security First)**:

```markdown
- Every endpoint that modifies or returns user-specific data MUST verify 
  that the authenticated user has the required role or resource ownership (MUST)
- Authorization checks MUST be performed at the handler level, not only at the 
  middleware level — middleware establishes identity, handlers confirm permission
```

**Estimated impact**: Would catch 3/3 of the identified findings.
**Confidence**: HIGH — the pattern is consistent and the principle is unambiguous.

---

### Proposed Amendment 2: Error Message Security (MEDIUM priority)

**Pattern**: 2 of 6 reviews flagged error messages that included internal details.
[...]
```

The proposal is saved to `.documentation/memory/constitution-evolution-proposal.md`. The team reviews it, discusses it, and (if approved) uses `/devspark.constitution` to apply the accepted amendments.

## Building a Sprint Cadence

The lifecycle commands work together in a sustainable sprint-by-sprint rhythm:

```
During sprint:
  /devspark.specify → /devspark.plan → /devspark.tasks → /devspark.implement
  → /devspark.create-pr → /devspark.pr-review → merge
  
  (Any time): /devspark.quickfix for small fixes
  (Periodic): /devspark.site-audit for health check

End of sprint:
  /devspark.release    ← Archive completed specs, generate release notes
  /devspark.harvest    ← Clean up stale content, preserve knowledge
  
Monthly or quarterly:
  /devspark.commit-audit   ← Repository health analysis
  /devspark.repo-story     ← Updated project narrative
  /devspark.evolve-constitution  ← Governance evolution based on PR findings
```

This cadence keeps the repository healthy, the governance current, and the documentation accurate without requiring constant manual maintenance.

What I've found is that teams who skip the end-of-sprint cadence for a few sprints don't immediately feel the pain — the `.documentation/` directory gets a little noisier, a few stale specs linger, and the CHANGELOG drifts slightly behind reality. But by sprint 15 or 20, the accumulated drift becomes a real tax on every new team member and every retrospective. The commands themselves are fast; the friction is remembering to run them. Building release and harvest into the sprint closing ritual — the same moment you close the sprint board — is the pattern that sticks.

Chapter 14 closes with the experience of dogfooding DevSpark on its own source repository — the unique challenge and benefit of using a framework to build itself.
