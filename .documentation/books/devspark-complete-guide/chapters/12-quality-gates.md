---
title: "Chapter 7: Quality Gates — Reviews, Audits, and Risk Analysis"
part: "Part II: The Core Workflow"
---

# Chapter 7: Quality Gates — Reviews, Audits, and Risk Analysis

Quality gates are easy to skip when you're under deadline pressure. On a recent project, I was patching what looked like a minor authentication flow — a quick fix to the token refresh logic — and I skipped both `/devspark.analyze` and `/devspark.critic` because I thought the change was too small to warrant them. We caught the actual problem in PR review after the code was already written: a race condition in token refresh that critic would have surfaced in about thirty seconds. That's the kind of experience that changes how you work. Now I run critic on anything touching async state or security, without exception, regardless of how "small" the change appears to be.

## Quality Gates as a System

DevSpark's quality assurance isn't a single command. It's a system of gates at different stages of the workflow, each designed to catch different categories of problems:

| Gate | When to Use | What It Catches |
|------|-------------|----------------|
| `/devspark.analyze` | After tasks, before implement | Cross-artifact consistency issues |
| `/devspark.critic` | After tasks, before implement | Technical risks and architectural problems |
| `/devspark.checklist` | After tasks, before implement | Requirements quality issues |
| `/devspark.pr-review` | After implement, before merge | Constitution violations in actual code |
| `/devspark.site-audit` | Anytime | Full codebase compliance health |

Not all of these are necessary on every feature. For a genuinely trivial quickfix — correcting a typo in a locale string, bumping a dependency version — most of them are overhead you don't need. For a complex feature touching security or core architecture, running all of them before implementation starts will save significant rework. I learned that lesson concretely on a user authentication overhaul: I skipped the critic pass because the sprint deadline was tight, and we discovered during code review a privilege escalation path that would have been flagged immediately. The fix cost two days of rework and a second round of review. The critic run would have cost ten minutes. The decision heuristic I use now: if the feature touches auth, async state, payments, data ownership, or any shared infrastructure, all three pre-implementation gates run before a single line of code gets written.

## `/devspark.analyze`: Cross-Artifact Consistency

The analyze command checks that your spec, plan, and tasks are internally consistent with each other and with the constitution. It runs before you start writing code, while the plan is still editable and a discovered mismatch costs minutes rather than days.

```text
/devspark.analyze
```

In my experience, analyze is most valuable when there's distance between the person who wrote the spec and the person who wrote the tasks — or when those two artifacts were written days apart. The most common finding is a spec requirement that never made it into any task, and therefore would never get built. I've also seen the reverse: tasks implementing something the spec doesn't actually require, which quietly inflates scope.

One real false negative worth knowing about: analyze can miss inconsistencies that live inside prose descriptions rather than explicit acceptance criteria. If your spec says "the form should feel responsive" and your tasks make no mention of loading states or optimistic updates, analyze may not flag it. That kind of requirement needs checklist, not analyze.

### Example Output

```markdown
## Artifact Consistency Analysis: User Profile Page

### Spec → Plan Coverage
- ✅ Rate limiting on email updates: addressed in plan (Section 3.2)
- ✅ Input validation: addressed in plan (Zod schema in src/schemas/)
- ⚠️ Session persistence: spec requires session storage, but plan only includes
  database schema changes. Add session layer task to plan.

### Plan → Task Coverage
- ✅ All plan components have corresponding tasks
- ✅ Test tasks precede implementation tasks in each phase

### Constitution Alignment
- ✅ Plan references Section I (Security) for input validation approach
- ⚠️ Plan does not reference Section IV (Architecture) for service layer separation.
  The handler plan puts business logic in the handler function.
  Move business logic to a service layer per Section IV before implementation begins.
```

The analyze output is saved to `.documentation/specs/{feature}/gates/analyze.md`. The downstream `/devspark.implement` and `/devspark.pr-review` commands read this file automatically.

## `/devspark.critic`: Adversarial Risk Analysis

The critic command takes an adversarial stance toward your plan. It's designed to find what you missed, not to validate what you got right. Think of it as asking a skeptical senior architect to poke holes in your design before you commit to building it.

```text
/devspark.critic
```

Or with a specific focus area:

```text
/devspark.critic Focus on security implications and race conditions.
```

What I've found is that critic earns its keep on two categories of features: anything touching authentication or authorization, and anything involving concurrent writes. Those are the areas where the gap between "seems fine" and "is actually fine" is widest and most expensive. I've watched teams skip the critic on a "simple" profile update endpoint and then spend three days in incident response after discovering that user IDs were being read from the request body rather than the session token — exactly the kind of finding critic surfaces immediately.

One honest caveat on false positives: critic can flag risks that your architecture has already mitigated elsewhere. On a project where we had a robust optimistic locking strategy at the database layer, critic still flagged concurrent write risk on every plan that touched user records. The findings weren't wrong — they were just already addressed at a level critic couldn't see from the plan alone. The discipline is to read each finding and verify it's actually mitigated, not to dismiss it because it seems familiar.

### How Critic Thinks

The critic doesn't ask "is this plan reasonable?" It asks:
- "What is the worst-case scenario if this is deployed?"
- "What attack vector does this create?"
- "What happens under concurrent load?"
- "What fails silently that should fail loudly?"
- "What is the most expensive mistake someone could make with this?"

### Example Output

```markdown
## Adversarial Risk Analysis: User Profile Page

### SHOWSTOPPERS (Constitution violations — must fix before implement)

1. **Email update enables account takeover via timing attack**
   
   The plan updates the email address immediately on PUT /api/users/me. If an 
   attacker can guess another user's ID (IDs are sequential integers per plan),
   they cannot directly update the email. However, if the email field is used 
   as a login identifier and there's no email verification step, an attacker who 
   gains temporary access can permanently lock the legitimate user out by changing
   the email.
   
   Constitution reference: Section I.iv — "Authentication MUST use established patterns"
   
   **Required fix**: Add email verification flow. The new email is pending until 
   the user clicks a confirmation link. Current email remains active until confirmed.

2. **No authorization check on user ID**
   
   The spec says the endpoint is `PUT /api/users/me`, implying the user ID comes
   from the authenticated session. The plan's handler code fetches the user ID
   from the request body. If the implementation follows the plan literally, any 
   authenticated user can update any other user's profile.
   
   Constitution reference: Section I.ii — "All user-supplied input MUST be validated"
   (User ID in request body is user-supplied input)
   
   **Required fix**: Derive user ID exclusively from the authenticated session token,
   never from the request body. Update plan before implementation begins.

### HIGH RISKS (Should fix before implement)

1. **Missing concurrency handling for concurrent profile updates**
   
   If a user submits the form twice quickly (double-click), both requests may succeed,
   with the second overwriting valid data from the first. The plan has no mention of
   optimistic locking or last-write-wins semantics.
   
   **Recommended**: Add an `updated_at` timestamp column and use optimistic concurrency
   control: reject updates where the client's `updated_at` doesn't match the server's.

### MEDIUM RISKS (Consider before merge)

1. **Display name allows HTML characters**
   
   The validation allows 2–50 characters but doesn't strip HTML. If the display name
   is rendered unsanitized anywhere (email templates, notifications), this enables
   stored XSS. The plan doesn't mention HTML escaping.

### LOW RISKS (Informational)

1. The plan doesn't document the decision to not require email verification.
   Record this as an ADR regardless of whether the decision changes.
```

The critic output is saved to `.documentation/specs/{feature}/gates/critic.md`. Finding SHOWSTOPPERS before implementation is exactly what critic is designed for — and the ones in the example above are not hypothetical; I've seen both the email-as-login vulnerability and the session-vs-body user ID mistake appear in real PR reviews on projects that skipped this gate.

## `/devspark.checklist`: Requirements Quality Validation

The checklist command evaluates the quality of your requirements — not whether the implementation plan is sound, but whether the specification itself is complete, testable, and unambiguous.

```text
/devspark.checklist
```

This is particularly useful for features with complex user stories, features handed off between teams, features where requirements come from external stakeholders, and features where ambiguity in the spec could cause significant rework. In practice, I run checklist whenever I didn't write the spec myself. The findings from checklist rarely block implementation outright, but they consistently surface the kind of quiet ambiguity that generates two rounds of back-and-forth with a product owner after code is already merged.

### Example Output

```markdown
## Requirements Checklist: User Profile Page

### Completeness
- ✅ Happy path defined (user updates profile successfully)
- ✅ Validation failure defined (bad email, name too short/long)
- ⚠️ Network error handling: spec says "user sees a specific error message" but
  doesn't define the message content. Use "Network error. Please try again." 
  as the standard and update the spec to reflect this.
- ❌ Session expiry during update: not addressed. Add acceptance criteria for
  this case before implementation begins — the expected behavior is that the
  user is redirected to login and the update is discarded.

### Testability
- ✅ All acceptance criteria are specific and binary (either satisfied or not)
- ⚠️ "changes persist across sessions" — testable, but the test requires creating
  a profile, closing the session, opening a new session, and checking the values.
  Add this as an explicit acceptance test in the spec.

### Ambiguity
- ❌ "display name" vs "name" used interchangeably in spec. Standardize to
  "display name" throughout before implementation begins.
- ⚠️ "current values pre-populated" — the spec means the form loads with existing
  values already filled in. Confirm this interpretation with the product owner
  and update the spec to remove the ambiguity.
```

The checklist output is saved to `.documentation/specs/{feature}/gates/checklist.md`.

## `/devspark.pr-review`: The Primary Review Gate

The PR review is the most important quality gate. It runs after implementation, against actual code, and it's the last checkpoint before merge.

### How PR Review Works

The review command reads:
1. The project constitution
2. The feature spec (including its status)
3. The PR diff (the actual code changes)
4. Any quality gate outputs from analyze, critic, or checklist

It produces a structured review with findings categorized by severity.

### Review Severity Levels

| Severity | Definition | PR Disposition |
|----------|-----------|----------------|
| CRITICAL | MUST requirement violated | Changes Required — must fix |
| HIGH | SHOULD requirement violated | Changes Requested — should fix |
| MEDIUM | Best practice concern | Consider fixing — reviewer's judgment |
| LOW | Minor issue | Informational — fix if convenient |
| APPROVED | No blocking findings | Ready to merge |

A PR is approved only when there are no CRITICAL findings and all HIGH findings have been addressed or explicitly accepted with documented rationale.

### Spec Status Check

The PR review checks spec status before evaluating code:

```markdown
## Pre-Review Check

**Spec status**: In Progress ⚠️

The spec is not yet Complete. PR approval requires:
- All tasks marked [x] in tasks.md
- Spec status set to Complete

This review will proceed for informational purposes, but approval is blocked
until the spec reaches Complete status.
```

A spec in `In Progress` state means some tasks are not done. A spec in `Draft` state means implementation hasn't started. Neither can be approved.

### The Address-PR-Review Loop

When findings require fixes, the loop is:

```text
/devspark.address-pr-review
```

This command:
1. Reads the review findings
2. Groups fixes by severity (CRITICAL first)
3. Applies fixes one finding at a time, committing each separately
4. Uses commit messages that reference the finding: `fix: address PR review finding [HIGH-1] — add rate limiting to email update endpoint`

The commit isolation is deliberate. It makes the fix history auditable: you can see exactly which commit addressed which finding, and whether any finding was addressed incorrectly.

After fixes are applied:

```text
/devspark.update-pr   ← Updates PR description with new commit context
/devspark.pr-review UPDATE  ← Focused review of just the fixed findings
```

The `UPDATE` mode review doesn't repeat the full review. It checks whether the specific findings from the previous review were adequately addressed. This keeps the re-review efficient.

## `/devspark.site-audit`: Full Codebase Compliance

The site audit is not a per-feature gate. It's a periodic codebase health check that scans the entire repository against the constitution.

```text
/devspark.site-audit
```

Or with a specific focus:

```text
/devspark.site-audit Focus on security compliance
/devspark.site-audit Scope to src/api/ only
```

### What Site Audit Finds

- Files that violate MUST requirements (hardcoded credentials, functions exceeding line limits, etc.)
- Specs in Draft or In Progress status on the main branch (a lifecycle violation)
- Missing test files for source files
- Inconsistent patterns across the codebase
- Documentation gaps in public APIs

### Site Audit Output

```markdown
## Site Audit: MyProject

**Date**: 2025-04-22
**Scope**: Full repository
**Constitution**: v1.2.0

### CRITICAL Violations (2)

1. **Hardcoded API key** — `src/integrations/stripe.ts:14`
   `const STRIPE_KEY = "sk_live_abc123..."` 
   Constitution Section I.i: No hardcoded credentials
   **Action**: Move to environment variable immediately

2. **Spec in In Progress status on main** — `.documentation/specs/user-auth/spec.md`
   This spec has been In Progress for 17 days. Either complete or archive.
   Constitution Section V.ii: Incomplete specs on main are anti-patterns

### HIGH Violations (4)

[... additional findings ...]

### Overall Health Score: 73/100
```

What I've found most useful about site audit is running it at the start of each sprint as a baseline, then again at the end. The delta between those two runs shows whether the sprint improved or degraded codebase health in a way that individual PR reviews don't reveal — you can merge clean PRs all sprint and still accumulate drift at the system level.

## Persisting Gate Outputs

All quality gate outputs are stored under `.documentation/specs/{feature}/gates/`:

```
.documentation/specs/user-profile/gates/
├── analyze.md      ← /devspark.analyze output
├── critic.md       ← /devspark.critic output
└── checklist.md    ← /devspark.checklist output
```

These files aren't just for human review. The `implement`, `create-pr`, and `pr-review` commands read them. A PR description generated by `/devspark.create-pr` will automatically include a quality gates section if gate outputs exist:

```markdown
## Quality Gates

**Critic Analysis**: Run — 2 SHOWSTOPPERS found and addressed (see gates/critic.md)
**Checklist**: Run — 2 completeness issues resolved before implementation
**Analyze**: Run — 1 consistency issue (session persistence) resolved in plan amendment
```

This makes the PR description self-documenting: reviewers know which analysis was done, what was found, and how it was addressed — without having to dig through commit history.

---

The pattern across all five gates is the same: earlier is cheaper. The trade-off here is real — each gate costs time upfront that you might not feel like you have. What I've learned, sometimes painfully, is that the time is never actually saved by skipping the gate; it just gets spent later, under worse conditions, on code that already exists. The gates I skip are the ones I end up wishing I'd run.

Chapter 8 goes inside the framework itself: the tiered prompt model that governs how commands are resolved across personal, team, and framework tiers — and why that architecture makes the constitution more durable than a simple config file.
