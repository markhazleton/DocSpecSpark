---
title: "Chapter 8: The Tiered Prompt Model"
part: "Part III: Architecture"
---

# Chapter 8: The Tiered Prompt Model

On a project a few years ago, I watched a fifteen-developer team spend nearly three weeks arguing about plan formatting. One developer wanted JSON output. Another wanted Markdown with a specific heading structure. A third had built a custom plaintext template he swore by. Meanwhile, the features we were supposed to be building sat waiting. The friction wasn't about code quality or architecture—it was pure process noise, the kind that emerges when a shared tool has no way to accommodate individual preferences without breaking shared standards.

That's when I started thinking seriously about resolution models. The problem wasn't that people had different preferences. That's healthy. The problem was that our tooling forced a binary choice: either everyone uses the same thing, or everyone maintains their own fork. What I needed was a way to let people optimize individually without undermining the framework the whole team depended on. The tiered resolution model emerged from that mess.

I'll walk through how the three-tier resolution chain works—personal, team, framework—and show why we needed the five-tier extension when the harness runtime came into play. Then I'll cover the internal structure of atomic prompts, workflows, and aliases, and explain why we made the choice to store personal overrides in Git. If you're building on DevSpark or thinking about a similar structure for your own tooling, understanding this chain will tell you exactly where to put things and why.

## Why a Tiered Resolution Model?

In my experience, teams that share a development framework eventually hit the same wall. Someone wants more verbose output. A security-focused team needs extra checks on every PR review. A Python-heavy team wants language-specific examples in implementation guidance. These aren't unreasonable requests—they reflect legitimate differences in how people work.

Without a resolution model, you're left with three bad options: maintain separate command sets for each team and developer (a maintenance nightmare), use a single shared command set with no customization (forcing everyone to accept the least-common-denominator experience), or accept that developers will use fundamentally different processes (which defeats the purpose of a shared framework in the first place).

The tiered resolution model I built for DevSpark solves this by allowing customization at three independent levels—personal, team, and framework—with a clear, deterministic priority order. The framework provides the defaults. Teams override where they need to. Individuals override where they want to. No level requires the others to change.

## The Three-Tier Resolution Chain

For slash commands (the standard DevSpark interface), the resolver checks tiers in this order:

```
1. Personal override:  .documentation/{git-user}/commands/{command}.md
2. Team customization: .documentation/commands/{command}.md
3. Framework default:  .devspark/defaults/commands/{command}.md
```

The first tier that has a file for the requested command wins. The resolver does not merge—it uses the first match and stops. That determinism is intentional. Merging sounds appealing until you're debugging why a command behaves differently on two machines.

### Example: Resolving `/devspark.plan`

Developer Alice has created a personal override for the plan command. The repository has no team-level plan override. The framework default exists.

```
Requested: /devspark.plan

Check: .documentation/alice/commands/devspark.plan.md → EXISTS → use this file
```

Result: Alice's personal override runs. The resolver found a match at the first tier and stopped—it never checked for a team or framework file.

The same logic applies at all levels. If a file exists at tier N, resolution stops; if not, it checks tier N+1. A developer with no personal override will use the team override if it exists, otherwise the framework default. Without personal or team overrides, a developer falls through to the framework default. This is the complete algorithm, and what I've found is that once you see it stated plainly, it becomes easy to reason about when something resolves unexpectedly.

### Why Personal Overrides Are Git-Committed

Personal overrides live in `.documentation/{git-user}/commands/`. This is inside the project repository, committed to Git. That might seem counterintuitive—why are "personal" preferences committed to the shared repository?

Because personal overrides need to be available wherever you work. If you clone the repository on a new machine, your overrides are immediately available. If another developer clones the repository to review your work, they can see your overrides. If you leave a project, your overrides remain in the repository as a record (and can be cleaned up with a standard PR). What I've found in practice is that the portability benefit outweighs the slight oddity of personal preferences living in a shared repo.

The `{git-user}` namespacing ensures that Alice's overrides in `.documentation/alice/` don't conflict with Bob's overrides in `.documentation/bob/`. The naming comes from `git config user.name`, so it is consistent across machines as long as your Git username is consistent.

## The Internal Anatomy of Prompts

The harness runtime (covered in Chapter 10) organizes prompts into three artifact types: atomic prompts, workflows, and aliases. Understanding these types explains how DevSpark composes complex multi-step operations from simple building blocks—and, more importantly, where you can inject your own customization.

### Atomic Prompts

Atomic prompts are the smallest unit of AI instruction. They live in `templates/prompts/atomic/` and are identified by a frontmatter `id:` field:

```markdown
---
id: specify-intake
audience: developer
category: spec-workflow
exposed: true
description: Route-aware specification intake command
---

# Specification Intake

You are a specification assistant. Your task is to classify the incoming 
development request and route it to the appropriate workflow.

[... prompt content ...]
```

The frontmatter fields control how the atomic prompt behaves in composition:
- `id`: Unique identifier used for resolution and workflow composition
- `audience`: Who this prompt is for (`developer`, `reviewer`, `architect`)
- `category`: Logical grouping for discovery and filtering
- `exposed`: Whether this prompt is directly user-invocable vs. only usable in workflows

### Workflows

Workflows are YAML files that define ordered sequences of atomic prompts. They live in `templates/workflows/`:

```yaml
# templates/workflows/spec-full.yaml
name: full-spec-workflow
description: Complete specification workflow for major features
autonomy:
  level: assisted

guardrails:
  max_files_changed: 5
  restricted_paths:
    - ".devspark/**"
    - ".documentation/memory/**"

steps:
  - id: specify-intake
    pause_after: true
    output_type: spec_document

  - id: clarify-requirements
    pause_after: true
    when: "user confirms clarification needed"

  - id: technical-planning
    pause_after: true
    output_type: plan_document

  - id: task-breakdown
    pause_after: false
    on_failure: pause

  - id: implementation
    review_after: true
    output_type: code_changes
```

Key workflow fields:
- `pause_after: true` — Pause the workflow at this step and wait for user input before continuing
- `when` — Conditional execution (step is skipped if condition is false)
- `on_failure` — What to do when a step fails (`pause`, `fail`, `skip`)
- `review_after: true` — Flag this step for human review after completion
- `autonomy.level` — `assisted` (pauses at pause_after steps) or `autonomous` (runs through)
- `guardrails` — Constraints on how many files can change and which paths are restricted

### Aliases

Aliases are the user-facing command names. They are thin YAML files that point at a target workflow:

```yaml
# templates/aliases/devspark.specify.yaml
name: devspark.specify
description: Specification intake — use this to start new work
target_workflow: spec-full
exposed: true
```

When you type `/devspark.specify`, the resolver:
1. Looks up the alias `devspark.specify`
2. Finds it points to workflow `spec-full`
3. Resolves the workflow definition
4. Executes each step by resolving the atomic prompt at each step's `id`

This three-level composition—alias → workflow → atomic prompts—provides a clean separation between the user interface (aliases), the sequencing (workflows), and the actual AI instructions (atomic prompts). Each level can be customized independently. The trade-off here is that this indirection adds a layer of abstraction to debug when something resolves unexpectedly, but in my experience the ability to swap out any layer without touching the others more than pays for that cost.

## Creating Personal and Team Overrides

### Personal Override

To create a personal override for `/devspark.plan`:

```text
/devspark.personalize I want /devspark.plan to produce more detailed 
file-by-file breakdowns, including estimated line counts for each file and 
explicit dependency injection patterns.
```

The personalize command:
1. Reads your Git username to determine your namespace
2. Creates `.documentation/{username}/commands/devspark.plan.md`
3. Generates a customized version of the plan prompt incorporating your preferences
4. Commits the file

To revert: delete the file and commit the deletion.

### Team Override

Team overrides require a PR (they affect all team members):

1. Create `.documentation/commands/devspark.plan.md`
2. Base it on the framework default (`cat .devspark/defaults/commands/devspark.plan.md`)
3. Modify for team-specific requirements
4. Submit a PR for team review

> **Warning:** Team overrides that deviate significantly from framework defaults can cause problems when upgrading DevSpark. The upgrade process warns when team overrides may hide structural changes in updated stock prompts. Review warnings carefully before applying upgrades.

## The Extended Five-Tier Resolution (Harness Runtime)

The harness runtime uses a five-tier resolution chain that extends the standard three tiers:

```
1. App-local:     {app.path}/templates/{tier}/{id}.{ext}  (multi-app only)
2. Personal:      ~/.devspark/personal/{git_user}/templates/{tier}/{id}.{ext}
3. Team:          .devspark/team/templates/{tier}/{id}.{ext}
4. Workspace:     templates/{tier}/{id}.{ext}
5. Framework:     .devspark/defaults/templates/{tier}/{id}.{ext}
```

Two tiers that don't exist in the standard chain:

**App-local** (Tier 1): Only active in multi-app mode when `--app <id>` is supplied. App-local templates live under the application's path and shadow everything below them for that invocation only.

**Personal** (Tier 2): In the harness runtime, personal overrides live in the user's home directory (`~/.devspark/personal/{git_user}/`), not in the project repository. This allows personal preferences that persist across all projects on that machine. This raises an interesting question about when to use home-directory personal overrides versus Git-committed ones—the answer largely comes down to whether you want the override to travel with the repository or with the developer.

### Resolution Implementation

The resolution logic is implemented in `src/devspark_cli/resolution.py`. The algorithm is straightforward:

```python
def resolve(id: str, ext: str, tier: str, context: ResolutionContext) -> Path:
    candidates = [
        app_local_path(id, ext, tier, context),   # if multi-app mode
        personal_path(id, ext, tier, context),
        team_path(id, ext, tier),
        workspace_path(id, ext, tier),
        framework_path(id, ext, tier),
    ]
    for path in candidates:
        if path is not None and path.exists():
            return path
    raise ResolutionError(f"No template found for {id}")
```

Resolution is tested by `tests/test_alias_resolution_contract.py` and `tests/test_script_resolution_contract.py`. Every PR to the DevSpark repository runs these tests.

## Multi-App Resolution

When `.documentation/devspark.json` declares `mode: multi-app`, passing `--app <id>` to any harness command causes the resolver to prepend the app-local template directory to the resolution chain.

```bash
devspark harness run --app payment-api spec.yaml
```

For this invocation, the resolver checks `apps/payment-api/templates/` before any other tier. This allows the payment API to have completely customized workflow behavior—different guardrails, different pause semantics, different atomic prompts—without affecting how other apps in the monorepo behave.

## Validating the Resolution Chain

After creating or modifying overrides, validate that the resolution chain works correctly:

```bash
# Validate all workflow YAML files
devspark workflows validate

# Run the resolution contract tests
pytest tests/test_alias_resolution_contract.py
pytest tests/test_atomic_prompt_frontmatter_contract.py
```

For slash-command overrides (not harness runtime), validation is simpler—verify the file exists in the right location and that the AI agent's autocomplete shows the command. The file presence is the resolution—there's no schema to validate beyond the markdown format.

---

Now that you see how the chain works, a developer can customize without asking permission, a team can standardize without forcing uniformity, and the framework can evolve without breaking anyone's workflow. What I've learned from building this is that the resolution order itself is almost never what people get wrong—it's understanding which tier to put something in, and why. The next step is understanding what lives inside a prompt so you can build your own overrides at the right level—which is exactly what Chapter 9's autonomy model makes concrete, showing how guardrails and workflow control flow interact with the prompts you've just seen defined here.
