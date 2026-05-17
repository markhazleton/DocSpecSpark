---
title: "Chapter 9: Autonomy and Guardrails"
part: "Part III: Architecture"
---

# Chapter 9: Autonomy and Guardrails

> **What you'll learn in this chapter:**
> - The two autonomy levels: assisted and autonomous
> - How guardrails bound agent behavior during autonomous execution
> - The pause and resume mechanism
> - How autonomy level is resolved from multiple input channels
> - Performance considerations for guardrail enforcement
> - Telemetry signals emitted during autonomous runs

## The Autonomy Problem

Giving an AI agent complete autonomy over a codebase is like giving a very capable contractor unrestricted access to your house. They are competent. They will do exactly what they believe is needed. And occasionally, what they believe is needed will not match what you actually wanted — in ways that are difficult to undo.

The challenge is that the same property that makes autonomous AI execution powerful — the ability to make many decisions quickly without interruption — is also the property that makes mistakes expensive. A human developer pauses at decision points. An autonomous AI agent continues.

DevSpark's autonomy model provides a middle path: you can control exactly how much autonomy a workflow has, at what points it pauses for human review, and what constraints bound its behavior even when running autonomously.

## The Two Autonomy Levels

DevSpark workflows declare one of two autonomy levels:

### `assisted` (Default)

In assisted mode, the workflow pauses at every step marked `pause_after: true` and at every step marked `review_after`. Guardrail breaches in assisted mode downgrade to a pause — the workflow stops and waits for human review rather than failing.

This is the appropriate level for:
- Workflows where human judgment is needed at key decision points
- Teams new to autonomous AI execution
- High-risk operations (database migrations, infrastructure changes, authentication changes)
- Any time you want to review before the agent continues

Most DevSpark workflows default to assisted mode.

### `autonomous`

In autonomous mode, the workflow runs through `pause_after` and `review_after` markers without stopping. Guardrail breaches in autonomous mode are hard failures — the workflow exits with `EXIT_GUARDRAIL_BLOCKED` (exit code 21) rather than pausing.

Autonomous mode requires that `guardrails` be declared in the workflow. A workflow that declares `autonomy.level: autonomous` without guardrails is rejected at validation time.

This is the appropriate level for:
- Well-tested workflows that have been validated in assisted mode
- CI/CD pipeline execution where human interaction is not available
- Low-risk operations with bounded scope (documentation updates, test generation)
- Situations where speed matters and the workflow's scope is tightly constrained

> **Warning:** Do not default to autonomous mode. Use assisted mode until you have validated that a workflow behaves correctly in your environment. The cost of a runaway autonomous agent touching things it shouldn't is high.

## Guardrails

Guardrails are constraints that bound agent behavior. They apply to both autonomy levels but have different failure modes: in assisted mode, a guardrail breach pauses the workflow; in autonomous mode, it terminates it.

### Available Guardrails

**`max_files_changed`** (integer)

Rejects the step when the post-step diff touches more than N files, compared to a pre-step baseline.

```yaml
guardrails:
  max_files_changed: 10
```

Use this when you want to bound how much a single workflow step can change. A step that was supposed to update a configuration file should not be touching 30 files.

**`max_total_lines_changed`** (integer)

Rejects the step when the total lines changed (added + deleted, per `git diff --numstat`) exceeds N.

```yaml
guardrails:
  max_total_lines_changed: 500
```

Use this when you want to catch unexpectedly large changes. A documentation update that changes 2,000 lines is probably doing something other than documentation.

**`restricted_paths`** (list of glob patterns)

Rejects the step when any changed path matches any of the listed globs.

```yaml
guardrails:
  restricted_paths:
    - ".devspark/**"
    - ".documentation/memory/**"
    - "*.env"
    - ".github/**"
```

Use this to protect specific directories or files from autonomous modification. The DevSpark framework files, the project constitution, environment files, and CI configuration are good candidates for restriction.

### Combining Guardrails

Guardrails combine with AND semantics — a step is blocked if it violates ANY guardrail:

```yaml
autonomy:
  level: autonomous

guardrails:
  max_files_changed: 5
  max_total_lines_changed: 200
  restricted_paths:
    - ".devspark/**"
    - ".documentation/memory/**"
    - "src/auth/**"      # authentication code requires human review
    - "migrations/**"    # database migrations require human review
```

This configuration allows the workflow to run autonomously as long as it:
- Touches no more than 5 files
- Changes no more than 200 lines total
- Does not modify framework files, the constitution, auth code, or database migrations

If any of these limits are exceeded, the workflow terminates with an error.

## Resolving Autonomy Level

The effective autonomy level for a workflow run is determined by checking four sources in priority order:

1. **CLI flag**: `--autonomy assisted|autonomous` overrides everything
2. **Environment variable**: `DEVSPARK_AUTONOMY=assisted|autonomous`
3. **Project file**: `.devspark/autonomy.yaml` with `level: assisted|autonomous`
4. **Workflow default**: `autonomy.level` in the workflow YAML file

This resolution order means:
- CI/CD pipelines can force autonomous mode via environment variable without touching workflow files
- Individual developers can override to assisted mode via CLI flag while debugging
- Project-wide policy can be set in `.devspark/autonomy.yaml`
- Each workflow has its own sensible default

> **Tip:** Set `.devspark/autonomy.yaml` to `level: assisted` during initial rollout. After validating workflow behavior, you can selectively enable autonomous mode per workflow via the workflow YAML, or enable it globally via the project file.

### The `--non-interactive` Requirement

If you run `devspark run` with `--non-interactive` but without specifying an autonomy level through any of the four channels, the command exits with `EXIT_AUTONOMY_REQUIRED` (exit code 20). This prevents accidental autonomous execution in CI environments.

The error message names all three input channels:
```
Error: Non-interactive mode requires explicit autonomy level.
Set one of:
  --autonomy assisted|autonomous
  DEVSPARK_AUTONOMY=assisted|autonomous
  .devspark/autonomy.yaml (level: assisted|autonomous)
```

## Pause and Resume

When a step pauses (either explicitly via `pause_after: true` or via a guardrail breach downgrade in assisted mode), the workflow writes a resume state file and prints instructions:

```
Step 'technical-planning' completed.

Paused. Review the generated plan at .documentation/specs/user-profile/plan.md

Resume with: devspark resume 7f3a2b1c-d4e5-6789-abcd-ef0123456789
```

The resume state file lives at:
```
.documentation/telemetry/runs/{workflow_run_id}.json
```

This file contains:
- The workflow definition (schema version 1)
- The SHA-256 checksum of the workflow context at pause time (`context_checksum`)
- The `next_step_id` to resume from
- The original `workflow_run_id`

### Resuming a Paused Workflow

```bash
devspark resume 7f3a2b1c-d4e5-6789-abcd-ef0123456789
```

The resume operation:
1. Reads the state file
2. Re-resolves the workflow definition (applying current tier resolution)
3. Validates the `schema_version` (must be 1)
4. Validates the `context_checksum` (detects if the workflow changed between pause and resume)
5. Continues from `next_step_id` using the original `workflow_run_id`

If the workflow definition has changed between pause and resume (e.g., someone updated the team workflow override), `context_checksum` validation fails:

```
Error: Workflow context changed since last pause. Cannot resume safely.
Start a new run or restore the workflow to its previous state.
Exit code: EXIT_RESUME_FAILED (25)
```

This safety check prevents resuming into an inconsistent state.

## Telemetry Signals

Every guardrail evaluation emits a JSONL event to `.documentation/telemetry/workflow-events.jsonl`. The event schema includes:

```json
{
  "workflow_run_id": "7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "workflow": "spec-full",
  "step_id": "technical-planning",
  "timestamp": "2025-04-22T14:23:17Z",
  "phase": "guardrail_triggered",
  "status": "block",
  "guardrail_rule": "max_files_changed",
  "actual_value": 12,
  "limit": 5
}
```

Event phases:
- `started` — Step began execution
- `completed` — Step completed without issues
- `paused` — Workflow paused (pause_after or guardrail downgrade)
- `failed` — Step failed (with `error_class` field)
- `guardrail_triggered` — Guardrail evaluated (may or may not block)

These events are append-only (OS-level exclusive lock around every JSONL append). Multiple concurrent `devspark run` invocations write to the same file safely.

### Inspecting Telemetry

```bash
# Show events from the most recent run
devspark harness trace latest

# Show events from a specific run
devspark harness trace 7f3a2b1c-d4e5-6789-abcd-ef0123456789
```

## Performance Considerations

Guardrail enforcement has a performance cost: capturing a pre-step baseline requires SHA-1-hashing every tracked file before each step runs. On large repositories with many files, this can add measurable latency.

DevSpark short-circuits this cost when no guardrails are declared:

```yaml
# No guardrails declared → zero baseline cost
autonomy:
  level: assisted
```

When guardrails are declared, the cost is proportional to the number of tracked files. To minimize the cost on large repositories:

1. **Scope `restricted_paths` narrowly**: Instead of `"**/*"`, use specific directories like `"src/auth/**"`. The enforcer checks whether changed files match the globs — the baseline captures everything, but narrow globs reduce the post-step comparison work.

2. **Use `max_files_changed` instead of `max_total_lines_changed`** when possible: File count is O(changed files), line count requires reading the diff.

3. **Use git worktrees for concurrent autonomous runs**: The guardrail enforcer assumes a per-process working-tree boundary. Two concurrent autonomous runs against the same working tree are not supported. Use `git worktree add` to create isolated working trees for concurrent execution.

## Practical Autonomy Configurations

### Development Workflow (Team Standard)

```yaml
# .devspark/autonomy.yaml
level: assisted
```

All workflows pause at review points. Guardrail breaches pause rather than terminate. This is the right default for teams building confidence with DevSpark.

### CI/CD Pipeline (Automated Testing)

```bash
DEVSPARK_AUTONOMY=autonomous devspark harness run --non-interactive ci-workflow.yaml
```

Or in CI YAML:

```yaml
# .github/workflows/ci.yaml
- name: Run DevSpark CI workflow
  env:
    DEVSPARK_AUTONOMY: autonomous
  run: devspark harness run --non-interactive ci-checks.harness.yaml
```

### Documentation-Only Autonomous Workflow

```yaml
# templates/workflows/docs-update.yaml
autonomy:
  level: autonomous

guardrails:
  restricted_paths:
    - "src/**"
    - "tests/**"
    - ".devspark/**"
    - ".github/**"
  max_files_changed: 20
  max_total_lines_changed: 1000
```

This workflow can run autonomously but is restricted to documentation changes only. Any attempt to modify source, tests, or framework files will terminate the workflow.

## Summary

- DevSpark workflows have two autonomy levels: `assisted` (pauses at review points) and `autonomous` (runs through them).
- Guardrails bound autonomous behavior by enforcing limits on files changed, lines changed, and paths accessible.
- Guardrail breaches pause in assisted mode and terminate in autonomous mode.
- Autonomy level is resolved from CLI flag → env var → project file → workflow default.
- Non-interactive mode requires an explicit autonomy level; missing it exits with an error.
- Paused workflows can be resumed safely; the resume validates context integrity before continuing.
- Guardrail telemetry is emitted to a JSONL event log for inspection and debugging.
- Guardrail enforcement is short-circuited when no guardrails are declared, incurring zero baseline cost.

Chapter 10 covers the harness runtime in detail — how to write declarative workflow specs, execute them, and integrate them into CI/CD pipelines.
