---
title: "Chapter 2: Core Concepts — Constitution, Commands, and Tiers"
part: "Part I: Foundations"
---

# Chapter 2: Core Concepts — Constitution, Commands, and Tiers

I've watched teams lock themselves into a single AI agent — usually whichever one was fashionable when the project started. By the time they realized they needed a different agent for a different task, their governance, their prompt libraries, and their workflow conventions were all tangled up with that agent's assumptions. Switching meant rewriting everything. That failure mode is what pushed me to build DevSpark around three load-bearing principles: make the agent interchangeable, make personalization safe for teams, and cover the full lifecycle from the start. This chapter explains what those three principles actually mean in practice, why each one exists, and how they shape the constitution framework, the command set, and the file layout that everything else in DevSpark builds on.

## The Three Pillars

Before I walk through each pillar, let me describe the situation that made all three necessary.

On a recent project, I watched a team running Claude Code for implementation and wanting to use GitHub Copilot for PR reviews — because Copilot's review suggestions were simply better for their codebase. Reasonable enough. But their prompt library had grown around Claude-specific syntax. Their governance assumptions were baked into Claude's memory files. Even their planning artifacts had implicit expectations about how Claude would interpret them. Switching agents for even one workflow stage meant auditing and rewriting a significant chunk of their setup. They ended up just staying with Claude for reviews too, accepting a worse outcome because the switching cost was too high.

That's the scenario I designed DevSpark to prevent. The three pillars are the solution to that specific failure.

### Pillar 1: Agent-Agnostic by Default

The first principle is agent-agnostic by default — and here's what that prevents: it prevents your governance from becoming hostage to any single vendor's conventions.

In practice, I've tested this with Claude Code, GitHub Copilot, and Cursor on the same project in the same week, and the governance structure stayed intact. The reason it works is architectural. DevSpark's governance lives in plain markdown files in your repository. Because every AI agent can read files in your repository, every agent can read DevSpark's governance structures without translation.

Stock command prompts live in `.devspark/defaults/commands/`. Repository overrides live in `.documentation/commands/`. Agent-specific shims — thin files that point the agent to the right prompt — live in agent-specific directories: `.claude/commands/` for Claude Code, `.github/prompts/` for GitHub Copilot, `.cursor/prompts/` for Cursor, and so on. The shim is the only agent-specific piece. Everything behind it is shared.

What I've found is that this matters most not at project start but six months in, when a better agent comes out, or when different team members have different agent preferences, or when one agent handles a specific task better than another. Agent-agnostic architecture means you can make that call without paying a rewrite tax.

### Pillar 2: Multi-User Personalization

The second principle addresses a friction I've noticed on almost every team that adopts shared AI tooling: individuals have legitimate, idiosyncratic preferences that conflict with standardization. The usual outcome is either chaotic divergence (everyone does their own thing) or resentful conformity (everyone uses the lowest-common-denominator setup). Neither is good.

What I've found works is a tiered model: teams share prompts, but individuals can customize any command without affecting their teammates. A developer who prefers more verbose plan artifacts can create a personal override of `/devspark.plan` that produces more detail. A developer who wants to skip the clarify step can customize their personal `/devspark.specify` to behave differently. Neither change affects what other developers see.

Personal overrides live in `.documentation/{git-user}/commands/`, where `{git-user}` is the Git `user.name` on that machine. They are committed to Git, so they travel with the developer across machines and are version-controlled. Deleting the override file reverts to the team or stock behavior.

The trade-off here is worth naming: committing personal preferences to the shared repository means everyone can see each other's customizations. In my experience, that's actually an asset — it surfaces useful variations that sometimes get promoted to team-level defaults. But it does require that the team agree on the `.documentation/{git-user}/` convention up front.

### Pillar 3: Full Lifecycle Coverage

The third principle is the one I've watched get ignored most often, and it's the one with the most downstream damage. Teams adopt AI tooling for the coding phase and then scramble at PR review time, or treat release documentation as an afterthought, or have no systematic way to audit whether their codebase still matches the decisions they made six months ago.

DevSpark covers the complete software development lifecycle — not just the coding phase. The command set spans:

- Requirements specification and clarification
- Technical planning and task breakdown
- Risk analysis and adversarial review
- Implementation with constitution-based guardrails
- Pull request drafting and review
- Release documentation and archival
- Codebase health audits and knowledge harvest
- Constitution creation, discovery, and evolution

The phrase "Adaptive System Life Cycle Development" (ASLCD) captures the intent: the lifecycle adapts to real-world development conditions. Brownfield projects have different needs than greenfield ones. Bug fixes have different needs than architectural changes. What I've learned is that right-sizing the workflow to the actual work is what keeps teams from either over-engineering small changes or under-engineering large ones. Chapter 6 covers that explicitly.

## The Project Constitution

The constitution is the most important concept in DevSpark. Everything else in the framework flows from it.

### What a Constitution Is

A constitution is a single markdown file at `/.documentation/memory/constitution.md` in your project root. It defines your project's non-negotiable principles: coding standards, security requirements, testing expectations, architectural constraints. It is written in plain English, using a `MUST`/`SHOULD`/`MAY` vocabulary that conveys requirement strength without ambiguity.

Every DevSpark command reads the constitution before doing anything. This means:

- Code reviews check findings against the constitution's principles
- Implementation commands know what standards to follow
- Risk analysis flags constitution violations as showstoppers
- Site audits scan the entire codebase against constitution requirements
- PR reviews won't approve unless the spec is complete and constitution-compliant

The constitution is not documentation that you write once and forget. It is a living governance document that every AI agent reads in every session, and that evolves through a structured amendment process as your project matures.

### Constitution Vocabulary

Effective constitutions use a small, consistent vocabulary:

| Term | Meaning | Enforcement in Reviews |
|------|---------|----------------------|
| **MUST** | Non-negotiable, mandatory | CRITICAL finding if violated |
| **MUST NOT** | Prohibited, never allowed | CRITICAL finding if violated |
| **SHOULD** | Strongly recommended | HIGH finding if violated |
| **SHOULD NOT** | Discouraged | HIGH finding if violated |
| **MAY** | Optional, permitted | Informational only |

The discipline of using MUST sparingly matters more than it might seem. When everything is a MUST requirement, nothing is. What I've found is that the teams who get the most value from constitution enforcement are the ones who reserve MUST for the principles that would cause them to reject a PR regardless of other merits — and put everything else in SHOULD.

### Constitution Location

The constitution lives outside the DevSpark framework directory intentionally. `.devspark/` contains the DevSpark framework files. `.documentation/` contains your project artifacts. When you upgrade DevSpark, the framework files update, but your constitution — your project's own governance — is untouched.

This separation is by design: DevSpark's uninstall process removes `.devspark/` but does not touch `.documentation/`. Your architectural decisions, your specs, and your constitution remain even after the framework is removed.

### A Minimal Constitution Example

```markdown
# MyProject Constitution

## I. Security First (MANDATORY)

- No hardcoded secrets or credentials (MUST)
- All user input MUST be validated before processing
- SQL queries MUST use parameterized statements
- Authentication MUST use an established library — no hand-rolled auth

## II. Test-First Development (MANDATORY)

- Tests MUST be written before implementation (Red-Green-Refactor)
- Unit test coverage MUST exceed 80%
- All public API endpoints MUST have integration tests

## III. Code Quality

- Functions MUST NOT exceed 50 lines
- Files MUST NOT exceed 500 lines
- All public APIs MUST have JSDoc or XML documentation comments
- No `console.log` in production code (MUST NOT)

## Governance

- Constitution supersedes all other guidance
- Amendments require team review and documentation
- All PRs MUST verify constitution compliance

**Version**: 1.0.0 | **Ratified**: 2025-04-01
```

Chapter 5 covers the constitution in full depth, including the discovery workflow for brownfield projects, amendment processes, and multi-app constitutions.

## The Slash-Command Workflow

DevSpark's operational interface is a set of slash commands — prompts typed into your AI agent's chat interface, not terminal commands. The full workflow covers 28 commands organized into categories.

### The Core Development Pipeline

The standard workflow for a new feature follows a pipeline where each command produces an artifact that the next command consumes:

```
/devspark.constitution   → Creates or updates /.documentation/memory/constitution.md
        ↓
/devspark.specify        → Creates .documentation/specs/<feature>/spec.md (Status: Draft)
        ↓
/devspark.clarify        → Refines requirements in the spec (Status: still Draft)
        ↓
/devspark.plan           → Creates .documentation/specs/<feature>/plan.md
        ↓
/devspark.tasks          → Creates .documentation/specs/<feature>/tasks.md
        ↓
/devspark.implement      → Writes code; updates Status: In Progress → Complete
        ↓
/devspark.create-pr      → Drafts PR using spec, task, and gate context
        ↓
/devspark.pr-review      → Reviews PR against constitution; produces findings
        ↓
/devspark.address-pr-review → Author applies fixes with commit isolation
        ↓
/devspark.pr-review UPDATE → Focused re-review against latest fix iteration
        ↓
[Merge PR]
```

This pipeline is not a sequence to execute in one sitting. Each artifact persists between sessions. I've run `/devspark.specify` on Monday, `/devspark.plan` on Wednesday, and `/devspark.implement` the following Monday. The spec file carries the work forward.

### Command Categories

**Constitution Commands** manage the governance document:
- `/devspark.constitution` — Create or update the constitution
- `/devspark.discover-constitution` — Analyze existing code and generate a constitution draft
- `/devspark.evolve-constitution` — Propose amendments based on PR review findings

**Full Spec Workflow Commands** cover major features and architectural changes:
- `/devspark.specify` — Route-aware intake; classifies work and creates the spec
- `/devspark.clarify` — Refine requirements without introducing technical decisions
- `/devspark.plan` — Translate requirements into technical architecture
- `/devspark.tasks` — Break the plan into implementable task items
- `/devspark.analyze` — Cross-artifact consistency check (optional quality gate)
- `/devspark.critic` — Adversarial risk analysis (optional quality gate)
- `/devspark.checklist` — Requirements quality validation (optional quality gate)
- `/devspark.implement` — Execute tasks and write code
- `/devspark.create-pr` — Draft the pull request description
- `/devspark.update-pr` — Refresh PR description after new commits
- `/devspark.pr-review` — Review PR against the constitution
- `/devspark.address-pr-review` — Apply review findings with commit isolation

**Lightweight Workflow** for small changes:
- `/devspark.quickfix` — Single-command workflow for bug fixes and minor changes

**Quality Assurance** commands that work independently of any spec:
- `/devspark.pr-review` — Can also review PRs without a spec (constitution-only mode)
- `/devspark.site-audit` — Full codebase compliance scan
- `/devspark.critic` — Can analyze any artifact, not just specs

**Lifecycle Commands** for repository health:
- `/devspark.release` — Archive completed specs, generate release notes
- `/devspark.harvest` — Knowledge-preserving cleanup and archival
- `/devspark.repo-story` — Evidence-based repository narrative
- `/devspark.commit-audit` — Analyze commit history for workflow signals
- `/devspark.taskstoissues` — Convert tasks.md entries to GitHub Issues
- `/devspark.personalize` — Create per-user command customizations
- `/devspark.upgrade` — Check installed version and guide upgrade

### Spec Status Lifecycle

Every specification has a `Status:` field that tracks its position in the lifecycle:

| Status | Set By | Gate |
|--------|--------|------|
| `Draft` | `/devspark.specify` | Cannot approve PR |
| `In Progress` | `/devspark.implement` (start) | Cannot approve PR |
| `Complete` | `/devspark.implement` (all tasks done) | PR approval allowed |

The spec must reach `Complete` before PR approval is possible. `/devspark.pr-review` flags incomplete specs as CRITICAL findings. `/devspark.release` skips specs that are not `Complete`. This lifecycle enforcement is baked into every command that interacts with spec status — it is not something that can be accidentally bypassed.

## The Three-Tier Prompt Model

When you type `/devspark.specify`, how does your AI agent know which prompt file to use? The three-tier resolution model governs this.

### Resolution Priority

The resolver walks a deterministic chain and uses the first match it finds:

1. **Personal override** — `.documentation/{git-user}/commands/devspark.specify.md`
2. **Team customization** — `.documentation/commands/devspark.specify.md`
3. **Framework default** — `.devspark/defaults/commands/devspark.specify.md`

If you have a personal override for `/devspark.specify`, it takes priority over everything. If your team has a team customization and you don't have a personal override, the team customization runs. If neither exists, the framework default runs.

This model serves a specific purpose: it allows individuals to optimize for their own workflow, allows teams to standardize their shared experience, and allows the framework to provide sensible defaults for everything — without any of these three levels requiring the others to change.

### Personal Overrides in Practice

Consider a developer who works primarily in Python and finds that the default `/devspark.plan` output is too brief for the complexity of projects they work on. They can create:

`.documentation/alice/commands/devspark.plan.md`

...with a modified version of the plan prompt that asks for more detailed file-by-file breakdowns. Alice's plan commands produce more detail. Alice's teammates who don't have this override continue to use the team or stock behavior. Neither Alice nor her teammates need to coordinate.

> **Tip:** Use `/devspark.personalize` to create personal overrides. The command walks you through the process and ensures the file ends up in the right location with the right naming.

### The Harness Runtime Extension

The tiered prompt model extends to the optional harness runtime (covered in Chapter 10). When running workflows through the CLI, the resolver checks five tiers:

1. App-local templates (multi-app mode only)
2. Personal overrides (`~/.devspark/personal/{git_user}/templates/`)
3. Team templates (`.devspark/team/templates/`)
4. Workspace stock templates (`templates/`)
5. Framework stock templates (`.devspark/defaults/templates/`)

This extended chain supports the harness runtime's more sophisticated workflow composition model.

## The File System Layout

A DevSpark-governed repository has a consistent directory structure:

```
your-project/
├── .devspark/                      ← DevSpark framework (do not edit)
│   ├── defaults/commands/          ← Stock slash-command prompts
│   ├── defaults/scripts/           ← Context-gathering scripts
│   └── VERSION                     ← Installed DevSpark version
│
├── .documentation/                 ← Your project artifacts (edit freely)
│   ├── memory/
│   │   └── constitution.md         ← The project constitution
│   ├── commands/                   ← Team-level command overrides (optional)
│   ├── {git-user}/commands/        ← Per-user command overrides (optional)
│   ├── specs/                      ← Feature specifications
│   │   └── {feature-name}/
│   │       ├── spec.md             ← Requirements specification
│   │       ├── plan.md             ← Technical plan
│   │       ├── tasks.md            ← Task breakdown
│   │       └── gates/              ← Quality gate outputs
│   │           ├── analyze.md
│   │           ├── critic.md
│   │           └── checklist.md
│   ├── decisions/                  ← Architecture Decision Records
│   └── telemetry/                  ← Harness runtime event logs
│
└── [agent shims]                   ← Agent-specific command files
    ├── .claude/commands/           ← Claude Code
    ├── .github/prompts/            ← GitHub Copilot
    └── .cursor/prompts/            ← Cursor
```

The clean separation between `.devspark/` (framework) and `.documentation/` (your work) is fundamental to DevSpark's upgrade model. When you upgrade DevSpark, only `.devspark/` changes. Your specs, your constitution, and your decisions stay untouched.

---

These three principles — agent-agnostic operation, personal overrides without team conflict, and full lifecycle coverage — are not incidental design choices. They are the answer to a specific set of failures I encountered and wanted to prevent from recurring. Every command and every constitution rule in the chapters that follow is shaped by them. Before you run your first `/devspark` command, understanding these pillars explains why the command behaves identically regardless of which agent you're using — and why your teammate's version of that same command can look different from yours without either of you creating a problem for the other.
