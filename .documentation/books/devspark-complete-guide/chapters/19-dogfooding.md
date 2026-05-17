---
title: "Chapter 19: Dogfooding — Building the Framework on Itself"
part: "Part V: Living with DevSpark"
---

# Chapter 19: Dogfooding — Building the Framework on Itself

> **What you'll learn in this chapter:**
> - What it means to govern a framework using its own governance
> - The bootstrapping problem and how layered initialization solved it
> - What DevSpark's own commit history reveals about the framework's health
> - A real PR review on a real framework change — findings and all
> - Five lessons only visible from the inside

## What Dogfooding Means for a Framework

"Eating your own dog food" — using your own product in your daily work — is a standard principle in software development. For most products, it means product managers and engineers use the application they're building. The feedback loop is direct: when something is confusing, the person who built it experiences the confusion.

For a development framework, dogfooding means something more specific. Every new feature of DevSpark is built using DevSpark. The specification for the new `/devspark.batch-workflow` command is written using `/devspark.specify`. The PR for the updated constitution template is reviewed using `/devspark.pr-review`. The quarterly retrospective uses `/devspark.repo-story`. The framework governs itself.

This circularity creates a unique feedback mechanism. If a command is awkward to use, I notice it immediately because I'm using the command. If the quality gates produce false positives that developers route around, I route around them on my own PRs. If the constitution template produces constitutions that are too vague to enforce, my own DevSpark constitution suffers the same problem.

The DevSpark source repository is both the product and the production environment.

## The Bootstrapping Problem

There is an obvious chicken-and-egg problem: how do you use DevSpark to build DevSpark before DevSpark exists?

The answer is layered initialization. The DevSpark repository has three phases in its git history:

**Phase 0 — Core files, pre-governance (first 47 commits)**: The initial command prompt files, the directory structure, and the basic scripts were written directly — no specs, no quality gates, no PR review process. These are the foundational files that DevSpark needs to exist before it can govern anything. You cannot write a spec using a spec command that doesn't yet exist.

**Phase 1 — Constitution establishment (commits 48–63)**: Once the core commands existed, the DevSpark repository's own constitution was written using those commands. This is the meta-moment: using `/devspark.constitution` to write the constitution for the DevSpark project. The DevSpark constitution covers prompt quality (MANDATORY: every atomic prompt must have valid frontmatter), schema integrity (all workflow YAML must pass validation), backward compatibility (existing slash commands must remain available after upgrades), and documentation-first (every new command must have documentation before the PR merges).

**Phase 2 — Governance applies to everything (commit 64 onwards)**: From this point, every change to DevSpark — including changes to the core command files — goes through the DevSpark workflow. The v0.1.0 tag marks this transition.

The conventional commit compliance rate tells the story: pre-v0.1.0, it's around 60% (the manual early commits, non-governed). Post-v0.1.0, it's 98.1% (787 total commits as of April 2025, 773 compliant). The framework governs its own compliance.

## DevSpark's Own Constitution

The DevSpark constitution is not the same as the templates in Appendix B. The templates are starting points for typical projects. The DevSpark constitution governs a prompt-engineering and CLI project, which has specific requirements:

```markdown
# DevSpark Constitution — v1.2.0

## I. Prompt Quality (MANDATORY)

- Every atomic prompt MUST have valid YAML frontmatter with `id`, `audience`, 
  `category`, and `exposed` fields (MUST)
- Prompt instructions MUST be unambiguous — if two readers could interpret a 
  prompt differently, it needs revision (MUST)
- Prompts MUST NOT assume a specific AI agent — all instructions must be
  agent-agnostic (MUST NOT)
- Every prompt change MUST be validated against at least two different AI agents
  before merging (MUST)

## II. Schema Integrity

- Every workflow YAML MUST pass `devspark workflows validate` (MUST)
- The `schema_version` field MUST be updated when breaking schema changes are made
- All new prompts MUST have contract tests under `tests/`

## III. Backward Compatibility

- Existing slash commands MUST remain available after upgrades (MUST)
- Stock prompt files MUST NOT be removed without a minimum 90-day deprecation period
- Breaking changes MUST increment the major version (MUST)

## IV. Documentation First

- Every new command MUST have documentation in `.documentation/DevSparkDocumentation/`
  before the PR is merged (MUST)
- Usage guides MUST include at least three worked examples
- Anti-patterns MUST be documented alongside correct usage
```

The "two AI agents" requirement in Section I is the most unusual principle in any constitution I've written. It exists because AI assistants interpret prompts differently. A prompt that works well with Claude Code may produce confused behavior with GitHub Copilot because the two agents have different expectations about context, response format, and instruction style. Validating against two agents before merging is the only way to catch agent-specific prompt failures.

This principle emerged from a real incident: a `/devspark.critic` prompt update that worked correctly with Claude Code but caused Copilot to produce output in the wrong format, which broke the downstream parsing in a team's custom workflow. The principle was added to the constitution after the incident. The CI now runs automated checks against multiple agent adapters using the `noop` adapter for smoke testing and the real adapters for behavioral validation.

## A Real PR Review on a Real Framework PR

The most direct evidence that dogfooding works is the quality of the reviews that DevSpark produces on its own PRs. Here is a condensed summary of the review for PR #28 — the tiered workflow engine introduction.

PR #28 added the declarative YAML workflow specification system described in Chapter 15. It was the largest PR in the repository's history at the time: 1,843 lines changed across 47 files.

The spec had been flagged by the critic as potentially oversized — 1,843 lines is above the threshold where reviewers struggle to hold the entire change in mind simultaneously. The response was a documented justification in the spec: the tiered workflow engine is a single coherent feature addition, not scope creep. The 1,843 lines reflect a new system, not a patchwork of unrelated changes. The spec documented the justification; the PR review accepted it.

The actual review findings:

**HIGH — Guardrail enforcer lacks short-circuit when no guardrails declared**

The guardrail enforcer, which validates that file changes don't exceed declared limits, was computing a per-step baseline (SHA-1 hashes of all tracked files) even when no guardrails were declared on the workflow. On repositories with hundreds of tracked files and workflows with many short steps, this added latency for no reason — there's nothing to enforce if there are no guardrails.

The fix: short-circuit the enforcer when `workflow.guardrails` is None or empty. Zero cost for guardrail-free runs. Verified with a benchmark: 40ms saved per step in a typical 10-step workflow on a 500-file repository.

This finding came from `/devspark.pr-review` on the DevSpark repository itself. The framework caught a performance issue in its own implementation.

**HIGH — Missing explicit error for non-interactive without autonomy level**

When `--non-interactive` was specified without an autonomy level (no flag, no environment variable, no project file), the runner fell through to the workflow default. This was the intended behavior when running interactively — but in a CI environment with `--non-interactive`, silently defaulting to an autonomy level the CI team hadn't explicitly chosen could cause accidental autonomous execution.

The fix: detect `--non-interactive` + no autonomy source → exit with `EXIT_AUTONOMY_REQUIRED` (exit code 20) with a message naming all three input channels (flag, environment variable, project file). Now CI pipelines fail explicitly rather than silently choosing an autonomy level.

**MEDIUM — Concurrency documentation incomplete**

The audit trail writer is concurrency-safe (it uses OS-level exclusive file locking), but the documentation didn't explain how. Teams setting up concurrent harness runs needed to know the safety guarantees — specifically, whether two concurrent runs writing to the same telemetry file would corrupt it.

Fix: documented the OS-level exclusive lock mechanism in the autonomy model documentation.

Both HIGH findings were substantive. The guardrail short-circuit caught a performance regression that would have been invisible in normal testing (tests don't benchmark; they verify correctness). The non-interactive safety check caught a genuine risk for CI environments that would have been hard to debug once encountered.

The PR was approved after the HIGH findings were fixed. The MEDIUM documentation issue was fixed in the same commit.

## What the Commit History Reveals

The DevSpark repository's commit audit (April 2025):

```
Total commits: 787
Conventional commit compliance: 98.1% (773/787)
PR-merged commits: 96.4% (758/787)
Direct-to-main commits: 29 (3.7%) — mostly documentation fixes, config updates

Commit type distribution:
  feat:     198 (25.2%)
  chore:    187 (23.8%)
  fix:      143 (18.2%)
  docs:     124 (15.8%)
  refactor:  89 (11.3%)
  test:      46 (5.8%)

Average PR size: 247 lines changed
Largest PR: 1,843 lines (PR #28 — tiered workflow engine)
Median PR size: 94 lines
```

The 98.1% conventional commit compliance is a direct output of the commit workflow. The few non-compliant commits are all in the pre-v0.1.0 bootstrap phase or in the 29 direct-to-main commits (emergency documentation fixes).

The commit type distribution is informative. The balance between `feat` (25.2%), `fix` (18.2%), and `refactor` (11.3%) reflects a maturing project: more features than fixes is normal early in a project; the refactor proportion suggests active improvement rather than stagnation. The `docs` proportion (15.8%) reflects the documentation-first constitution — documentation commits are a significant fraction because documentation is required alongside every feature.

The 29 direct-to-main commits (3.7%) are worth examining. A zero direct-to-main rate would be suspicious — documentation typos and configuration updates that require a full PR cycle create friction that slows work. The 3.7% reflects a balance: most changes go through the workflow, small documentation updates don't.

## Five Lessons from the Inside

**Lesson 1: Your constitution is always more vague than you think.**

The initial DevSpark constitution was written with high confidence that the principles were specific and measurable. The first site audit produced findings like "Prompt instructions should be unambiguous" — which is a principle, not a finding. The finding is: "The `/devspark.specify` prompt on line 23 says 'analyze complexity' without defining what analysis means or what output to produce."

Turning vague principles into findings that can be acted on requires a constitution that specifies behavior, not intent. "Prompts MUST be unambiguous" is intent. "If two readers could interpret a prompt differently, the prompt needs revision" is behavior — you can test it by having two readers interpret the prompt.

Every constitution needs a first audit cycle to discover where the principles are too vague. Plan for it.

**Lesson 2: The clarify step compounds value over time.**

Early in the DevSpark project, I sometimes skipped or abbreviated the clarify step when the feature seemed clear. I was always wrong. The features that seemed clear were the ones where the unasked questions surfaced as PR findings or implementation surprises.

After six months of consistent use, the most reliable predictor of a smooth implementation is a thorough clarification phase. The features that get stuck in review or require implementation rework almost always had abbreviated clarification.

**Lesson 3: The critic is adversarial by design — treat it accordingly.**

The critic intentionally over-flags. It's not trying to stop your work; it's trying to identify every possible risk so you can decide which ones matter. Treating critic output as a blocklist ("I can't proceed until these are all addressed") misses the point entirely.

The right posture is risk triage: read every SHOWSTOPPER, ask "if this scenario occurred in production, what would the impact be?", and document the risk acceptance for anything you're not fixing. The critic gives you the analysis; you make the decision.

For the DevSpark PR #28 reviewer, the critic flagged the 1,843-line PR size. The human decision was: justified, documented, proceed. The critic didn't block the PR; it prompted a decision that was then recorded.

**Lesson 4: Team overrides are the most reliable path to sustained customization.**

Personal overrides — changes that live in `.documentation/{username}/commands/` — are easy to create and easy to forget. They're not reviewed by the team. They drift. Two developers with the same personal override will implement them differently over time, and neither will notice because the overrides live in personal directories.

Team overrides — in `.documentation/commands/` — go through the normal PR process. They're visible to everyone. They evolve with explicit team agreement. If two or more developers have the same personal override, promoting it to a team override almost always produces a better version: the team discussion resolves the ambiguities that each developer had handled differently in their personal version.

**Lesson 5: The ultimate test is the site audit passing on the project that built the site audit.**

Running `/devspark.site-audit` on the DevSpark repository itself and seeing it pass is more informative than any user testimonial. The framework team has to live with every quality gate they build. If a gate produces too many false positives, it shows up in their own audit results. If a gate misses real issues, it shows up in their own PR reviews.

As of April 2025: 100% compliance on MUST requirements, 3 MEDIUM findings for maintainability (files that should be split), 0 HIGH or CRITICAL findings. The score reflects not low standards but daily use of the framework by the team that built it.

---

> **On Transparency**
>
> The commit history data and PR review findings in this chapter are drawn from actual DevSpark repository activity. The PR #28 findings are from the actual review run on the actual PR. I've presented them accurately, including the findings that caught real issues in my own implementation. If you're evaluating DevSpark for your own use, this transparency matters more than polished case studies would.
