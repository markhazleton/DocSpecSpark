---
title: "Appendix A: Complete Command Reference"
---

# Appendix A: Complete Command Reference

On the third project where I refined DevSpark, I kept watching the same friction surface: teams would finish writing a spec, then pause. "What comes after this?" someone would ask. "When do we use `/devspark.clarify` instead of just jumping to `/devspark.plan`?" The hesitation wasn't about understanding the commands individually — it was about not seeing how they connected. Every backtracking decision, every missed quality gate, every PR review that surfaced a problem we could have caught at the spec stage, traced back to that same gap: the pipeline existed, but the reasoning behind its shape didn't.

What I've found across those projects is that the commands aren't arbitrary. They emerged from specific failure modes — the authorization bug in Chapter 12 that traced back to an under-specified constitution, the planning debt in Chapter 8 that accumulated when teams skipped clarification and built against ambiguous requirements, the PR review cycles in Chapter 17 that kept looping because fix commits weren't isolated. The command taxonomy you see here is a direct record of those failures, organized by the stage in the feature lifecycle where the failure occurred.

The commands are organized by their role in the feature lifecycle — from understanding what needs to be built, to planning how to build it, to implementing, reviewing, and shipping. This structure forces a specific order of thinking, which is the entire point. Constraint-driven design isn't just a philosophy that applies to the systems you build with DevSpark; it applies to how DevSpark itself is used. Each command is a checkpoint. Each "Next" column is a gate. What follows is that structure laid bare.

## Constitution Commands

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `/devspark.constitution` | Create or update the project constitution | Principles and requirements in natural language | `.documentation/memory/constitution.md` |
| `/devspark.discover-constitution` | Generate constitution from existing codebase | Optional focus area | `.documentation/memory/constitution-draft.md` → `constitution.md` |
| `/devspark.evolve-constitution` | Propose constitution amendments from PR findings | PR review history | Amendment proposal document |

### Usage Examples

In Chapter 12, the root cause of the authorization bug wasn't a coding mistake — it was an unclear constitution. The team had never explicitly documented their security requirements, so the PR review had no authoritative standard to check against. Here is how to prevent that:

**Create a new constitution:**
```text
/devspark.constitution Security-first: no hardcoded credentials, validated input, 
parameterized SQL. TDD required: tests before code, 80% coverage. All public APIs 
must have documentation.
```

When you're working in an existing codebase without a constitution, the `discover` command gives you a starting point rather than a blank page:

**Discover from existing code:**
```text
/devspark.discover-constitution Focus on security and testing patterns
```

After a sprint surfaces recurring PR findings — the kind that point to a gap in your documented principles rather than individual lapses — the `evolve` command captures that learning:

**Propose amendments after sprint:**
```text
/devspark.evolve-constitution Propose amendments based on the authorization 
findings from the last three PR reviews.
```

---

## Specification Workflow Commands

| Command | Purpose | Input | Output | Next |
|---------|---------|-------|--------|------|
| `/devspark.specify` | Route-aware intake; creates spec | Feature description in product language | `.documentation/specs/{feature}/spec.md` (Status: Draft) | `/devspark.clarify` or `/devspark.plan` |
| `/devspark.clarify` | Refine requirements without technical decisions | Questions about user needs | Updated spec | `/devspark.plan` |
| `/devspark.plan` | Translate requirements to technical architecture | Tech stack and constraints | `.documentation/specs/{feature}/plan.md` | `/devspark.tasks` |
| `/devspark.tasks` | Break plan into implementable tasks | (reads plan.md) | `.documentation/specs/{feature}/tasks.md` | `/devspark.implement` |
| `/devspark.implement` | Execute tasks and write code | (reads spec, plan, tasks) | Code changes; Status: In Progress → Complete | `/devspark.create-pr` |
| `/devspark.create-pr` | Draft PR description from spec and task artifacts | (reads spec, plan, tasks, gates) | PR description | `/devspark.pr-review` |
| `/devspark.update-pr` | Refresh PR description after new commits | (reads spec, new commits) | Updated PR description | `/devspark.pr-review UPDATE` |
| `/devspark.address-pr-review` | Apply PR review findings with commit isolation | PR review findings | Isolated fix commits | `/devspark.update-pr` |

### Route Classification

When you pass a feature request to `/devspark.specify`, the system analyzes the request and routes it to one of three workflows, depending on scope and complexity. Understanding which workflow your request triggers is essential — it determines how much upfront specification work you do before writing code. A bug fix in a single file and a multi-service authentication redesign should not go through the same intake process; the routing logic enforces that distinction automatically, based on signals in your request.

| Route | When Used | Overhead |
|-------|-----------|---------|
| `one-off-fix` | Clear bug, single file, trivial change | Redirects to `/devspark.quickfix` |
| `quick-spec` | Clear scope, low architectural impact, <1 day | Lightweight spec without separate plan |
| `full-spec` | Multi-file, architectural implications, complex requirements | Full pipeline |

### Sequencing and Branching Logic

The "Next" column in the table above is not a suggestion — it reflects the dependency structure that the quality gates enforce. But the path through the pipeline isn't always linear, and understanding when to branch is as important as knowing the commands themselves.

`/devspark.clarify` is optional for well-scoped requests, but required when ambiguity exists in the original feature description. In practice, the signal I've used is this: if a reasonable engineer could interpret the spec two different ways and make meaningfully different implementation choices, clarification is not optional. Chapter 6 covers the scoping conversation in detail; the short version is that skipping clarification on an ambiguous spec doesn't save time — it defers the ambiguity into implementation, where resolving it costs more. Jumping directly from `/devspark.specify` to `/devspark.plan` is valid only when the specification is fully detailed and the route classification returned `quick-spec` or the request was explicitly scoped before being passed to the command.

The loop at the end of the pipeline — `/devspark.address-pr-review` feeding back into `/devspark.update-pr` — is intentional and important. When PR review findings surface, fixing them in isolated commits and then refreshing the PR description keeps the PR narrative in sync with the actual state of the code. I've watched teams skip the `update-pr` step after addressing review comments, and the result is a PR description that describes the original intent but not the final implementation. That disconnect creates exactly the kind of documentation debt the lifecycle commands are designed to prevent.

---

## Lightweight Workflow

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `/devspark.quickfix` | Single-command workflow for small changes | Fix description | Tracking record in `.documentation/quickfixes/` + applied fix |

**When to use quickfix:**
- Fewer than 3 files affected
- Clear root cause
- No architectural implications
- Total implementation time < 30 minutes

---

## Quality Assurance Commands

| Command | Purpose | Reads | Output | When to Run |
|---------|---------|-------|--------|-------------|
| `/devspark.analyze` | Cross-artifact consistency check | spec.md, plan.md, tasks.md | `.documentation/specs/{feature}/gates/analyze.md` | After `/devspark.tasks`, before `/devspark.implement` |
| `/devspark.critic` | Adversarial risk analysis | spec.md, plan.md | `.documentation/specs/{feature}/gates/critic.md` | After `/devspark.tasks`, before `/devspark.implement` |
| `/devspark.checklist` | Requirements quality validation | spec.md | `.documentation/specs/{feature}/gates/checklist.md` | After `/devspark.specify`, before `/devspark.plan` |
| `/devspark.pr-review` | Constitution-driven PR review | constitution.md, PR diff, spec status | Review findings with CRITICAL/HIGH/MEDIUM/LOW severity | After `/devspark.create-pr` |
| `/devspark.site-audit` | Full codebase compliance scan | constitution.md, all source files | Codebase health report | Anytime; recommended at start and end of sprint |

### PR Review Severity Reference

| Level | Definition | PR Disposition |
|-------|-----------|----------------|
| CRITICAL | MUST requirement violated | Changes Required — must fix before approval |
| HIGH | SHOULD requirement violated | Changes Requested — should fix |
| MEDIUM | Best practice concern | Reviewer judgment — fix or document |
| LOW | Minor issue | Informational |
| APPROVED | No blocking findings | Ready to merge |

---

## Lifecycle Commands

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `/devspark.release` | Archive Complete specs; generate release notes; update CHANGELOG | End of sprint |
| `/devspark.harvest` | Knowledge-preserving cleanup of stale documentation | End of sprint (after release) |
| `/devspark.commit-audit` | Analyze git history for workflow compliance and health signals | Monthly or quarterly |
| `/devspark.repo-story` | Generate evidence-based project narrative from git history | Onboarding, handoffs, retrospectives |
| `/devspark.taskstoissues` | Convert tasks.md entries to GitHub Issues | When tasks need to be tracked in the issue tracker |
| `/devspark.personalize` | Create per-user command customizations | When a developer wants to adjust command behavior |
| `/devspark.upgrade` | Check installed version and guide safe upgrade | When a new DevSpark version is released |

---

## Multi-App Commands (Optional)

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/devspark.add-application` | Register a new application in the multi-app registry | When adding a new application to a monorepo |
| `/devspark.list-applications` | Display all registered applications and their profiles | For visibility and documentation |
| `/devspark.validate-registry` | Validate `.documentation/devspark.json` schema, references, and consistency | After registry changes |

These commands are only relevant when using the optional multi-app monorepo support (Chapter 11).

---

## Optional CLI Commands (Terminal, Not Slash Commands)

These are terminal commands available after installing the optional DevSpark CLI (`uv tool install devspark-cli`).

| Command | Purpose |
|---------|---------|
| `devspark doctor` | Validate environment: Python version, CLI version, adapter availability, repository health |
| `devspark harness validate <spec>` | Validate a harness workflow spec file without executing |
| `devspark harness run <spec>` | Execute a harness workflow spec |
| `devspark harness run <spec> --dry-run` | Simulate execution with noop adapter |
| `devspark harness trace latest` | Show execution events from the most recent run |
| `devspark harness trace <run-id>` | Show execution events from a specific run |
| `devspark adapter list` | Show built-in adapters and local availability |
| `devspark adapter default <name>` | Save the default adapter to user config |
| `devspark resume <run-id>` | Resume a paused workflow run |
| `devspark upgrade` | Check and apply DevSpark framework upgrades |
| `devspark workflows validate` | Validate all workflow YAML files in templates/workflows/ |

---

## Spec Status Reference

| Status | Set By | Meaning | Gates |
|--------|--------|---------|-------|
| `Draft` | `/devspark.specify` | Spec created; planning in progress | PR cannot be approved |
| `In Progress` | `/devspark.implement` (start) | Implementation underway | PR cannot be approved |
| `Complete` | `/devspark.implement` (all tasks done) | All tasks checked; ready for PR | PR approval allowed |

**Status gate enforcement:**
- `/devspark.pr-review` flags non-Complete specs as CRITICAL
- `/devspark.release` only archives Complete specs
- `/devspark.site-audit` flags Draft or In Progress specs on main branch as anti-patterns

---

## Directory Reference

| Directory | Purpose | Owner |
|-----------|---------|-------|
| `.devspark/` | DevSpark framework files | DevSpark (do not edit) |
| `.devspark/defaults/commands/` | Stock slash-command prompt files | DevSpark |
| `.devspark/VERSION` | Installed framework version | DevSpark |
| `.documentation/` | Your project artifacts | You |
| `.documentation/memory/constitution.md` | The project constitution | You |
| `.documentation/commands/` | Team-level command overrides | Your team |
| `.documentation/{username}/commands/` | Personal command overrides | Individual developer |
| `.documentation/specs/{feature}/` | Feature specifications | You |
| `.documentation/specs/{feature}/spec.md` | Requirements specification | You |
| `.documentation/specs/{feature}/plan.md` | Technical plan | You |
| `.documentation/specs/{feature}/tasks.md` | Task breakdown | You |
| `.documentation/specs/{feature}/gates/` | Quality gate outputs | DevSpark |
| `.documentation/decisions/` | Architecture Decision Records | You |
| `.documentation/devspark.json` | Multi-app registry (optional) | Your team |
| `.documentation/telemetry/` | Harness runtime event logs | DevSpark |
