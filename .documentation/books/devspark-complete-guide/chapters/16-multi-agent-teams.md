---
title: "Chapter 12: Multi-Agent and Multi-User Teams"
part: "Part IV: Advanced Patterns"
---

# Chapter 12: Multi-Agent and Multi-User Teams

> **What you'll learn in this chapter:**
> - How DevSpark handles teams where different developers use different AI agents
> - The personalization workflow and how to create personal command overrides
> - Onboarding new team members onto DevSpark
> - The improvement loop — from developer observation to framework improvement
> - Contribution model for DevSpark prompt improvements

## The Multi-Agent Reality

Development teams don't use a single tool. Some developers prefer Claude Code for its deep file-system access. Others prefer GitHub Copilot because it's already integrated into their VS Code workflow. Some use Cursor for its multi-file editing. Some use Gemini CLI. In a team of eight developers, it would not be unusual to have four different AI agents in daily use.

Traditional workflow standardization fails in this environment. If your "structured AI workflow" requires Claude Code, half the team ignores it. If it requires specific IDE plugins, the developers who prefer terminal-based editors won't participate.

DevSpark's multi-agent architecture makes the workflow agent-agnostic. The governance structures — the constitution, the specs, the command prompts — are plain markdown files. Every AI agent that can read files can use DevSpark. The agent-specific pieces (shim files, command discovery) are thin and isolated. The shared governance layer is universal.

## How Agent-Agnostic Architecture Works

When Developer Alice (using Claude Code) and Developer Bob (using GitHub Copilot) both use `/devspark.pr-review` on the same PR, here is what happens:

**Alice's invocation:**
- Claude Code sees `.claude/commands/devspark.pr-review.md` (the shim)
- The shim points to `.devspark/defaults/commands/devspark.pr-review.md`
- Claude Code reads the prompt and the constitution and generates a review

**Bob's invocation:**
- GitHub Copilot sees `.github/prompts/devspark.pr-review.prompt.md` (the shim)
- The shim points to `.devspark/defaults/commands/devspark.pr-review.md`
- Copilot reads the same prompt and the same constitution and generates a review

Both reviews derive from the same prompt file and the same constitution. The outputs will differ (different models produce different prose) but they will evaluate the same principles against the same code. The governance is consistent even though the agents are different.

### Shim Files Are Thin

The shim files are deliberately minimal. A Claude Code shim for `/devspark.pr-review` might look like:

```markdown
---
description: Constitution-driven pull request review
---

See the full review prompt at `.devspark/defaults/commands/devspark.pr-review.md`
and execute it against the current PR.
```

The shim does one thing: tell the agent where the real prompt is. The real prompt lives in `.devspark/defaults/commands/`. This means upgrading the DevSpark framework automatically upgrades the behavior for all agents — the shims don't need to change because they point at the framework default, which was updated.

### Team Customizations Apply to All Agents

Team-level overrides in `.documentation/commands/` apply regardless of which agent picks them up. If the team creates a custom `devspark.pr-review.md` that adds an extra database migration check, that check runs for Alice's Claude Code invocation and Bob's Copilot invocation alike.

## The Personalization Workflow

Personal overrides allow individual developers to customize their DevSpark experience without affecting teammates.

### Creating a Personal Override

```text
/devspark.personalize I want /devspark.plan to produce more detailed architecture 
diagrams using Mermaid syntax, and to include estimated complexity scores 
for each implementation task.
```

The personalize command:
1. Reads `git config user.name` to determine your namespace (`alice`, `bob`, etc.)
2. Reads the current framework default for the specified command
3. Generates a modified version incorporating your preferences
4. Creates `.documentation/{username}/commands/devspark.plan.md`
5. Shows you the diff and asks for confirmation before writing

The output file is committed to the repository. This is intentional — your personal overrides travel with you across machines and are version-controlled.

### Personal Override File Structure

```
.documentation/
├── alice/
│   └── commands/
│       ├── devspark.plan.md    ← Alice's customized plan command
│       └── devspark.critic.md  ← Alice's customized critic command
├── bob/
│   └── commands/
│       └── devspark.specify.md ← Bob's customized specify command
└── commands/
    └── devspark.pr-review.md   ← Team-wide PR review customization
```

### Reverting a Personal Override

Delete the file and commit:

```bash
git rm .documentation/alice/commands/devspark.plan.md
git commit -m "chore: revert personal plan override — using team default"
```

After deletion, `devspark.plan` for Alice resolves to the team override (if any) or the framework default.

### What to Personalize

Good candidates for personal overrides:
- Verbosity level of output (more/less detail in plans, reviews, etc.)
- Output format preferences (Mermaid diagrams, specific markdown structure)
- Language-specific hints (prefer Rust patterns, use Python type annotations)
- Domain-specific context (add security scanning instructions to every review)
- Workflow shortcuts (skip clarify step by default for a command you use for small things)

Bad candidates for personal overrides:
- Security requirements (these should be in the constitution, not personal preferences)
- Team conventions (these should be team overrides, not personal)
- Architecture decisions (these should be in the constitution or ADRs)

## Onboarding New Team Members

Onboarding a developer onto a DevSpark-governed project takes about 30 minutes. The process:

### 1. Install DevSpark for Their Agent

The new developer opens their AI agent in the cloned repository and runs the matching quickstart prompt. The quickstart detects an existing installation and skips the constitution creation step:

```
DevSpark is already installed in this repository (version 2.1.0).
Existing constitution found at .documentation/memory/constitution.md.

Setting up agent-specific shim files for [their agent]...
✅ Agent shim files created.

Bootstrap complete. Type /devspark. to see available commands.
```

### 2. Read the Constitution

```text
/devspark.constitution --show
```

Or just open `.documentation/memory/constitution.md` directly. The new developer should understand the project's principles before writing any code.

### 3. Run a Site Audit to Understand Current State

```text
/devspark.site-audit
```

The site audit gives a new developer an immediate picture of the codebase's health status — where the code is fully compliant, where violations exist, and what the constitution's priorities are.

### 4. Review Recent Specs

The `.documentation/specs/` directory contains the history of features that have been built. Reading recent specs — especially their plans and tasks — gives a new developer architectural context that would otherwise take weeks to absorb.

This is one of the less obvious benefits of the DevSpark spec workflow: specs are institutional memory. A developer reading a six-month-old spec for a feature learns not just what was built, but why, how it was planned, what risks the critic identified, and how the PR review findings were addressed.

## The Improvement Loop

DevSpark is not a static framework. It evolves based on real usage experience. The improvement loop is the mechanism for turning developer observations into framework improvements.

### From Observation to Improvement

The improvement loop has four steps:

**Step 1: Observe**

A developer notices a gap in the framework — a command that produces unclear output, a workflow that doesn't handle an edge case well, a missing command for a common task.

**Step 2: File an Improvement**

```text
/devspark.specify --improvement The critic command doesn't flag when a spec 
has no acceptance criteria. Without acceptance criteria, the AI-generated code 
is unverifiable.
```

This creates a GitHub Issue via the improvement adapter, categorized as a framework improvement.

**Step 3: Evaluate**

The DevSpark maintainers (or the team, for custom overrides) evaluate the improvement:
- Is this a real gap or a misunderstanding of the existing behavior?
- Does it affect only this project or the framework broadly?
- Should this be a personal override, a team override, or a stock change?

**Step 4: Implement**

If the improvement is valid:
- For personal/team improvements: create an override
- For stock improvements: submit a PR to the DevSpark repository

### The GitHub Issue Adapter

The improvement loop uses a GitHub Issue adapter to file improvements as structured issues:

```markdown
## DevSpark Framework Improvement

**Reporter**: Alice (via /devspark.specify --improvement)
**Date**: 2025-04-22
**Severity**: Medium
**Component**: /devspark.critic

### Observed Gap

The critic command does not check whether the spec has acceptance criteria defined.
Acceptance criteria are essential for verifying that the implementation matches
what was intended. Without them, the "Complete" status is meaningless.

### Proposed Improvement

Critic should flag specs with no acceptance criteria section as a HIGH risk:
"Spec has no acceptance criteria — implementation cannot be objectively verified."

### Context

Observed during the user profile feature (spec: .documentation/specs/user-profile/spec.md).
The spec was marked Complete with 7 tasks done, but two acceptance criteria were 
never explicitly stated and were not implemented.
```

## The Contribution Model

DevSpark welcomes contributions to the framework itself. The contribution model is designed to maintain framework quality while enabling community improvements.

### What Can Be Contributed

- **New atomic prompts**: For workflows that don't exist yet
- **Improved existing prompts**: Clearer language, better examples, missing edge cases
- **New workflow specs**: Multi-step workflows for common engineering patterns
- **New adapter implementations**: Supporting additional AI agents
- **Documentation improvements**: Corrections, clarifications, additional examples

### How to Contribute

1. Fork the DevSpark repository at [github.com/markhazleton/devspark](https://github.com/markhazleton/devspark)
2. Create a branch from `main`
3. Make your changes following the [CONTRIBUTING.md](https://github.com/markhazleton/devspark/blob/main/CONTRIBUTING.md) guidelines
4. Run the validation suite: `devspark workflows validate` and `pytest tests/`
5. Submit a PR

All PRs go through the standard DevSpark PR review workflow — the framework reviews itself. This is the dogfooding practice described in Chapter 14.

### Contribution Standards

- Atomic prompts must have valid YAML frontmatter with all required fields
- Workflow YAML must pass schema validation
- All new prompts must have contract tests
- Changes to stock prompts must not break existing behavior without a migration path

## Summary

- DevSpark is agent-agnostic because governance lives in markdown files that every agent can read. Agent-specific shim files are thin and point to shared framework defaults.
- Team overrides apply to all agents; personal overrides apply only to the developer who created them.
- `/devspark.personalize` creates personal command overrides namespaced by Git username.
- New team member onboarding takes ~30 minutes: install shims, read the constitution, run a site audit, review recent specs.
- Specs serve as institutional memory — they capture the why, the how, and the risk analysis for every feature.
- The improvement loop converts developer observations into structured GitHub Issues and (eventually) framework improvements.
- DevSpark uses its own PR review workflow to evaluate contributions to the framework itself.

Chapter 13 covers the lifecycle commands — release, harvest, repo-story, and constitution evolution — the tools for keeping your repository and governance healthy over time.
