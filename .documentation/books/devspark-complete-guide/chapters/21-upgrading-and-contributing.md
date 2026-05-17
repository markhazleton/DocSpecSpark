---
title: "Chapter 15: Upgrading, Extending, and Contributing"
part: "Part V: Real-World Application"
---

# Chapter 15: Upgrading, Extending, and Contributing

Upgrading DevSpark is where I learned the real cost of silent breaking changes. On a project I led with five team members, we discovered that unannounced command deprecations caused subtle behavior differences when teammates upgraded at different times. One developer's `/devspark.archive` was another's silent redirect. Bugs from that mismatch took days to trace. That experience shaped the upgrade process you'll find here: loud, visible, and dry-run first.

Three things matter in upgrades: safety, visibility, and backward compatibility. Extending DevSpark asks for a fourth: team coordination. Contributing back requires understanding the versioning and release cycle. Let me walk through each.

## Upgrading DevSpark

On a project I led, silent command changes during upgrades caused bugs that took days to trace back to a version mismatch. That's why DevSpark's upgrade process is deliberately loud—it forces teams to see what changed before anything is applied. The upgrade process mirrors the installation process: prompt-first, no CLI required for the standard path.

### Standard Upgrade (Prompt-First)

In your AI agent's chat:

```text
Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/templates/commands/upgrade.md
```

Or via the slash command:

```text
/devspark.upgrade
```

The upgrade command:
1. Reads `.devspark/VERSION` to identify the installed version
2. Downloads the latest framework files
3. Diffs the current `.devspark/defaults/` against the latest
4. Shows you what changed — new commands, modified commands, removed commands
5. Warns if team overrides in `.documentation/commands/` may be hiding structural changes in updated prompts
6. Applies the upgrade to `.devspark/defaults/`
7. Updates `.devspark/VERSION`

### The Recommended Upgrade Cadence

```bash
# Step 1: Dry run to see what's changing
/devspark.upgrade --dry-run

# Step 2: Review the proposed changes
# (The upgrade command will display diffs for each changed file)

# Step 3: Apply
/devspark.upgrade --apply
```

The dry-run-first approach asks teams to be intentional about what they're accepting. I've watched teams skip the diff and upgrade blindly, only to discover a week later that a command they'd customized now conflicts with the new base. The cost of that discovery—especially when it surfaces in production—is always higher than the ten minutes spent reviewing changes upfront. That's not a guideline; it's the reason this step exists in the design.

The dry run is especially important for teams with extensive team overrides. The upgrade might change a stock command in ways that conflict with or duplicate what the team override does. Reviewing the diff lets you decide whether to:
- Keep the team override unchanged (it still adds the right customizations to the new base)
- Update the team override to account for the new base (the base changed enough that the override needs adjustment)
- Remove the team override (the new base now includes what the override was doing)

### Breaking Changes

Breaking changes are rare but necessary. Here's how DevSpark signals them, and why the cost of announcing them clearly is worth the disruption it prevents.

When a major version introduces a breaking change, the alternative—silent migration—shifts the debugging burden onto every team using the framework. I'd rather absorb the friction of a clear warning once than have teams absorb invisible failures indefinitely. So the upgrade command calls these out explicitly:

```
Warning: v2.0.0 introduces breaking changes:

1. The /devspark.archive command is deprecated in favor of /devspark.harvest
   Legacy shim provided: /devspark.archive still works but now redirects to harvest
   Shim will be removed in v3.0.0

2. Workflow YAML schema_version changes from "0" to "1"
   Existing workflow specs must be updated before using devspark harness run
   Migration: replace schema_version: 0 with schema_version: 1 in all harness specs

Proceed with upgrade? [Y/n]:
```

DevSpark follows semantic versioning. Minor version upgrades (2.1.0 → 2.2.0) should be backward-compatible. Major version upgrades (1.x → 2.x) may include breaking changes, and the upgrade command will surface every one of them before asking you to proceed.

I learned to always commit or stash before upgrading. The upgrade touches `.devspark/` files, and merge conflicts surfacing mid-sprint are expensive—not just in time, but in team trust. The technical reason is straightforward: the upgrade modifies those files directly, and uncommitted local changes to them create conflicts the upgrade process cannot resolve cleanly. Make it a habit before you need it to be one.

### CLI Upgrade

For teams using the optional CLI:

```bash
uv tool install devspark-cli --force --from git+https://github.com/markhazleton/devspark.git
devspark upgrade
```

`devspark upgrade` via CLI does the same check-diff-apply process as the prompt-first upgrade.

## Extending DevSpark with Custom Commands

DevSpark is designed to be extended. Custom commands follow the same three-tier resolution model as stock commands and work alongside them without conflict.

### Creating a Custom Team Command

Suppose your team needs a command `/devspark.db-review` that reviews all database-related changes against your database coding standards. This doesn't exist in the stock command set, but it can be created as a team override:

1. Create `.documentation/commands/devspark.db-review.md`:

```markdown
---
description: Database change review — validates migrations, schema changes, and query patterns
---

# Database Change Review

You are reviewing database-related changes in this PR against the project constitution
and these additional database coding standards:

## Database Standards (from .documentation/standards/database.md)

[Read .documentation/standards/database.md and include relevant standards here]

## Review Checklist

For each database change (migration files, schema definitions, ORM queries):

1. **Migrations are reversible**: Every `up` migration MUST have a corresponding `down`
2. **No data-destructive changes without backup strategy**: Any migration that could 
   lose data MUST document the backup and recovery approach
3. **Indexes on foreign keys**: All foreign key columns MUST have indexes
4. **No N+1 queries**: Identify any code that fetches related records in a loop
5. **Parameterized queries**: All raw SQL MUST use parameterized statements
6. **Migration filename format**: MUST be `YYYYMMDD-HHMMSS-description.sql`

## Constitution Reference

Also apply all relevant principles from `.documentation/memory/constitution.md`,
particularly Section I (Security First) regarding SQL injection prevention.

## Output Format

Report findings at CRITICAL, HIGH, MEDIUM, LOW severity.
Group findings by file.
Reference specific line numbers.
```

2. Create an agent shim for Claude Code in `.claude/commands/devspark.db-review.md`:

```markdown
---
description: Database change review
---

Follow the instructions at `.documentation/commands/devspark.db-review.md`
```

3. Repeat the shim for other agents your team uses.

After committing these files, `/devspark.db-review` is available to everyone on the team.

### Creating Custom Atomic Prompts (Harness Runtime)

For harness runtime workflows, custom atomic prompts follow the same structure as stock prompts:

```markdown
---
id: db-migration-review
audience: developer
category: quality-assurance
exposed: true
description: Review database migration files against project standards
---

# Database Migration Review

[... prompt content ...]
```

Place this file in a location the resolver will find it:
- For team-wide: `.devspark/team/templates/prompts/atomic/db-migration-review.md`
- For personal: `~/.devspark/personal/{username}/templates/prompts/atomic/db-migration-review.md`

The resolver will find it automatically.

## Writing Community Extensions

DevSpark has a community extension model for sharing commands and workflows that might not be appropriate for the stock framework.

### Extension Structure

A DevSpark extension is a git repository with the following layout:

```
my-devspark-extension/
├── README.md                    ← What the extension does, install instructions
├── commands/                    ← Custom command prompt files
│   └── devspark.my-command.md
├── atomic/                      ← Custom atomic prompts (if any)
│   └── my-atomic-prompt.md
├── workflows/                   ← Custom harness workflows (if any)
│   └── my-workflow.yaml
└── install.md                   ← Installation instructions
```

### Installing an Extension

Currently, extension installation is manual — copy the extension files to the appropriate locations in your repository. A community registry is planned for future releases.

### Extension Guidelines

Extensions in the community registry must follow these guidelines:
- Do not modify files in `.devspark/` (these are framework files)
- Do not modify `.documentation/memory/constitution.md` (the user's constitution)
- All commands must use the `devspark.` namespace prefix
- Extensions must document which DevSpark version they are compatible with
- Extensions must include at least one worked example in their README

## Contributing to DevSpark

DevSpark is open source, and contributions are welcome. The contribution process uses DevSpark's own workflow:

### Step 1: Fork and Clone

```bash
git clone https://github.com/markhazleton/devspark.git
cd devspark
```

### Step 2: Check for an Existing Issue

Browse [open issues](https://github.com/markhazleton/devspark/issues) to see if your contribution idea is already being tracked. If not, open one first — it prevents duplicate work and gets early feedback on whether the contribution is appropriate.

### Step 3: Create a Branch and Spec

For anything beyond a documentation fix, create a spec first:

```text
/devspark.specify [description of your contribution]
```

This creates a spec in the DevSpark repository's own `.documentation/specs/` directory. Yes, you're contributing a spec to the DevSpark spec system. Dogfooding.

### Step 4: Implement

Follow the standard DevSpark workflow through implementation. Run the test suite:

```bash
# Validate all workflow YAML
devspark workflows validate

# Run contract tests
pytest tests/

# Validate atomic prompt frontmatter
pytest tests/test_atomic_prompt_frontmatter_contract.py
```

All tests must pass.

### Step 5: Review

```text
/devspark.pr-review
```

DevSpark reviews its own PRs using its own review command. Findings from the review must be addressed before the PR can be approved. This is not negotiable — the DevSpark constitution applies to DevSpark itself.

### Step 6: Submit

Push your branch and open a PR on the GitHub repository. The maintainers will review using `/devspark.pr-review` and may request changes. The process is the same process described in this book.

### Contribution Areas

The most valuable contribution areas, in approximate priority:

1. **Agent shim templates** for agents not currently supported
2. **Community workflow specs** for common engineering patterns
3. **Documentation improvements** — additional examples, clarifications, anti-patterns
4. **Bug reports** with reproduction steps
5. **Constitution templates** for common project types (web API, React SPA, Python data pipeline, etc.)
6. **Test coverage improvements** — contract tests for edge cases

## Future Direction

DevSpark's roadmap includes several capabilities under active development:

### Enhanced Observability

Structured metrics storage and visualization. The current telemetry model (JSONL event log) is powerful but requires manual inspection. A dashboard that visualizes workflow execution patterns, guardrail trigger rates, and spec lifecycle metrics is planned.

### Business Value Alignment

The ability to link specs to business goals or OKRs, making the connection between development work and organizational objectives explicit. This enables reporting on AI-assisted development velocity in business terms rather than just technical metrics.

### CI/CD Integration

First-class support for running DevSpark audits as pipeline steps. Current CI integration requires manual setup. The goal is a GitHub Action that installs DevSpark, runs the appropriate checks, and reports findings as PR review comments.

### Cross-Project Governance

Organizational-level governance where a parent constitution applies across multiple repositories, with repository-level constitutions serving as additive layers. The monorepo model scaled to multi-repository organizations.

### Contribution-Based Prompt Evolution

An automated pipeline that collects usage data from the community (opt-in, anonymized), identifies patterns in what prompts are customized and how, and proposes stock prompt improvements based on aggregate wisdom.

## What the Upgrade Model Protects—and Where Contribution Begins

I've seen framework upgrades break production when teams couldn't see what changed. The diff-first, dry-run model makes that class of failure nearly impossible—not because it prevents change, but because it makes change visible before it lands. What I've found is that the teams who take the dry run seriously are the same teams who catch the conflicts early, before they metastasize into behavioral bugs that look unrelated to any upgrade.

The trade-off here is worth naming: a mandatory review step adds friction. Teams in a hurry will want to skip it. In my experience, that friction is exactly the point. The ten minutes spent reading a diff is the cheapest form of incident prevention available.

Once you've extended DevSpark for your own context—added custom commands, built team-specific workflows, tuned the constitution for your domain—you'll start to notice which gaps are structural and which are just yours. That distinction is where contribution begins. The teams who contribute the most useful extensions aren't the ones who read the framework spec most carefully; they're the ones who hit a real wall, solved it locally, and recognized that other teams will hit the same wall. If you've built something that made your upgrade smoother or your reviews sharper, that's worth sharing. The contribution process is the same workflow you've been using throughout this book—spec, plan, implement, review, submit. The only difference is that this time, you're improving the tool itself.

---

You've reached the end of the main narrative. The appendices that follow provide reference material — command quick-reference, constitution templates for common project types, and a troubleshooting guide — that you can return to as needed.
