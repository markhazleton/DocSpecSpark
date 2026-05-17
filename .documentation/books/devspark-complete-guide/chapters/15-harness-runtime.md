---
title: "Chapter 10: The Harness Runtime — Declarative Engineering Workflows"
part: "Part III: Architecture"
---

# Chapter 10: The Harness Runtime — Declarative Engineering Workflows

## Why a Runtime Engine?

On a recent release automation project, I found myself executing the same sequence of slash commands by hand every sprint: run the site audit, feed results into a constitution analysis, review findings, archive completed specs, generate the changelog, then cut a release commit. Five commands, in order, each depending on the output of the last. If a check failed midway, I had to remember where I was and what still needed to run. The slash-command interface had no way to chain these steps, no way to halt on a failed validation and wait for me, and no auditable record of what had actually executed. I was the runtime, and I was unreliable.

That experience is what the harness runtime is designed to replace. The slash-command workflow — covered in Parts I and II — remains the primary DevSpark interface. It requires no CLI, no runtime environment, and no configuration beyond the quickstart prompt. For the vast majority of DevSpark use cases, it is sufficient. But in practice, a specific class of workflows keeps appearing that the slash-command model cannot handle alone: **multi-step engineering workflows that span multiple tools, require conditional logic, need auditable execution records, or must run without human interaction**.

I've encountered three recurring shapes to this problem:

- A documentation pipeline that runs `/devspark.site-audit`, feeds results to a constitution evolution analysis, then creates a GitHub Issue with findings — all without human interaction
- A CI job that validates all specs on the main branch are `Complete`, runs the site audit, and fails the build if there are CRITICAL violations
- An automated release workflow that archives completed specs, generates release notes, creates a GitHub tag, and publishes the CHANGELOG — coordinated across the DevSpark command set and external tools

Each of these requires a runtime that can execute a sequence of steps, handle failures, maintain state between steps, and produce an auditable record. The harness runtime is that engine.

> **Important:** The harness runtime does not replace the slash-command workflow. The 28 slash commands remain the primary user interface. The harness runtime is additive — it extends DevSpark for scenarios where terminal-driven, automated, or multi-tool execution is needed.

## The Harness Runtime Architecture

The harness runtime consists of two major components working together, bridged by an adapter layer.

**Workflow Specs** — YAML or JSON files that declare what steps to execute, in what order, with what adapters, and under what conditions.

**Execution Engine** — The CLI that parses the spec, resolves templates, enforces guardrails, writes telemetry events, and manages the pause/resume lifecycle.

### The Adapter Model

The adapter layer is where a portable spec becomes a concrete tool invocation. DevSpark ships with adapters for every major AI agent and a safe `noop` default:

| Adapter | Invokes | When to Use |
|---------|---------|-------------|
| `noop` | Nothing — logs what would be run | CI dry runs, contract testing, debugging |
| `manual` | Pauses and waits for human input | Manual review steps requiring TTY |
| `claude_code` | Claude Code CLI (`claude`) | Running steps with Claude Code |
| `copilot` | GitHub Copilot CLI | Running steps with Copilot |
| `cursor` | Cursor CLI | Running steps with Cursor |

The `noop` adapter is the safe default for any environment where you are not sure which agent is available. It executes the full workflow control flow — guardrail evaluation, pause semantics, telemetry — without invoking any actual AI tool. This makes it ideal for CI dry runs and spec validation.

### Checking Available Adapters

```bash
devspark adapter list
```

Output:
```
Built-in adapters:
  noop      — always available (dry-run safe)
  manual    — requires TTY (available: yes)
  claude_code — requires 'claude' CLI (available: yes, path: /usr/local/bin/claude)
  copilot   — requires 'gh' with Copilot extension (available: no)
  cursor    — requires Cursor CLI (available: no)

Saved default adapter: claude_code
```

To save a default adapter (persisted in user config, not in `.devspark/`):

```bash
devspark adapter default claude_code
```

## Writing a Harness Workflow Spec

Harness workflow specs are YAML files. The schema is validated by `devspark harness validate` before execution.

### Minimal Spec

```yaml
# docs-audit.harness.yaml
schema_version: 1
name: documentation-audit
description: Run site audit and file findings

autonomy:
  level: assisted

steps:
  - id: run-site-audit
    adapter: claude_code
    prompt: |
      /devspark.site-audit Full codebase compliance scan.
      Output findings to .documentation/audit-results.md
    pause_after: true

  - id: review-findings
    adapter: manual
    prompt: |
      Review the findings in .documentation/audit-results.md.
      Confirm when ready to proceed.
    pause_after: true

  - id: create-issue
    adapter: claude_code
    prompt: |
      Based on the site audit findings in .documentation/audit-results.md,
      create a GitHub Issue using /devspark.taskstoissues for the CRITICAL
      and HIGH findings.
    pause_after: false
```

### Full Spec with Guardrails and Conditions

```yaml
# release-workflow.harness.yaml
schema_version: 1
name: sprint-release
description: Archive completed specs and generate release notes

autonomy:
  level: autonomous

guardrails:
  max_files_changed: 30
  restricted_paths:
    - "src/**"
    - "tests/**"
  max_total_lines_changed: 2000

steps:
  - id: verify-specs-complete
    adapter: claude_code
    prompt: |
      Verify that all specs in .documentation/specs/ on the current branch
      have Status: Complete. List any incomplete specs and fail if any exist.
    on_failure: fail
    output_type: validation_report

  - id: archive-specs
    adapter: claude_code
    prompt: /devspark.release Archive all Complete specs for this sprint.
    when: "previous step output indicates all specs complete"
    pause_after: false
    output_type: release_artifacts

  - id: generate-changelog
    adapter: claude_code
    prompt: |
      Update CHANGELOG.md with the release notes from the archived specs.
      Use the release date format: ## [X.Y.Z] — YYYY-MM-DD
    review_after: true

  - id: commit-release
    adapter: claude_code
    prompt: |
      Stage all release artifacts and create a commit:
      "chore(release): v{version} — {sprint-name}"
    on_failure: pause
```

### Spec Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `schema_version` | Yes | Always `1` (current) |
| `name` | Yes | Unique workflow identifier |
| `description` | No | Human-readable description |
| `autonomy.level` | Yes | `assisted` or `autonomous` |
| `guardrails` | Required for autonomous | Constraints on agent behavior |
| `steps[].id` | Yes | Unique step identifier |
| `steps[].adapter` | Yes | Which adapter to use |
| `steps[].prompt` | Yes | The instruction to execute |
| `steps[].pause_after` | No | `true` to pause after step (default: false) |
| `steps[].when` | No | Conditional execution expression |
| `steps[].on_failure` | No | `fail`, `pause`, or `skip` (default: `fail`) |
| `steps[].output_type` | No | Labels the output for downstream steps |
| `steps[].review_after` | No | `true` to pause for human review after step |

## The Workflow Execution Lifecycle

### Step 1: Validate

Always validate before running:

```bash
devspark harness validate release-workflow.harness.yaml
```

Validation checks:
- YAML syntax
- Schema version compatibility
- Required fields present
- Step IDs unique
- Referenced workflow prompts resolvable via the tier chain
- Guardrails declared if `autonomy.level: autonomous`

If validation fails, it reports specific errors with file location. Fix errors before running.

### Step 2: Dry Run

With the `noop` adapter, you can do a full dry run that simulates execution without invoking any AI agent:

```bash
devspark harness run release-workflow.harness.yaml --adapter noop --dry-run
```

A dry run exercises the full control flow: guardrail evaluation, pause semantics, conditional step logic. The output shows what each step would do if run with a real adapter.

### Step 3: Run

```bash
devspark harness run release-workflow.harness.yaml
```

The runner:
1. Reads the spec
2. Resolves the autonomy level
3. Sets up guardrail baseline
4. Executes steps in order, applying pause/continue/skip logic
5. Writes telemetry events to `.documentation/telemetry/workflow-events.jsonl`
6. On pause: writes resume state and prints instructions
7. On completion: summarizes the run

### Step 4: Trace

After a run (or during debugging):

```bash
# Show events from the most recent run
devspark harness trace latest

# Show events from a specific run
devspark harness trace 7f3a2b1c

# Filter by step
devspark harness trace latest --step generate-changelog
```

Trace output:

```
Workflow Run: 7f3a2b1c-d4e5-6789-abcd-ef0123456789
Workflow: sprint-release
Started: 2025-04-22T14:00:00Z
Status: paused

Steps:
  [✅] verify-specs-complete (14:00:01 → 14:00:45)
  [✅] archive-specs (14:00:45 → 14:02:12)
  [⏸ ] generate-changelog — paused at review_after (14:02:12)
  [⬜] commit-release — pending
```

### Step 5: Resume

```bash
devspark resume 7f3a2b1c-d4e5-6789-abcd-ef0123456789
```

## The `devspark doctor` Command

Before running any harness workflow, use `devspark doctor` to verify that the environment has the prerequisites the workflow needs:

```bash
devspark doctor
```

Output:
```
DevSpark Doctor — Environment Validation

Runtime
  ✅ Python 3.12.2 (required: ≥3.11)
  ✅ DevSpark CLI 2.1.0

Adapters
  ✅ noop — always available
  ✅ manual — TTY available
  ✅ claude_code — claude CLI found at /usr/local/bin/claude
  ❌ copilot — gh Copilot extension not installed
  ❌ cursor — cursor CLI not found

Repository
  ✅ .devspark/ present (version 2.1.0)
  ✅ .documentation/memory/constitution.md present
  ✅ git repository (branch: main, clean working tree)

Telemetry
  ✅ .documentation/telemetry/ writable
  ✅ Concurrent-safe JSONL writer available

Summary: 9/11 checks passed. Copilot and Cursor adapters unavailable — 
use noop, manual, or claude_code for workflows on this machine.
```

## Harness Runtime in CI/CD

The harness runtime integrates cleanly with CI/CD pipelines. The key configuration is the autonomy level and non-interactive flag:

```yaml
# .github/workflows/devspark-ci.yml
name: DevSpark CI Checks

on:
  push:
    branches: [main]
  pull_request:

jobs:
  devspark-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install DevSpark CLI
        run: uv tool install devspark-cli --force --from git+https://github.com/markhazleton/devspark.git
        
      - name: Run DevSpark Doctor
        run: devspark doctor
        
      - name: Validate Workflow Specs
        run: devspark workflows validate
        
      - name: Run CI Checks (noop adapter — dry run only)
        run: |
          DEVSPARK_AUTONOMY=autonomous devspark harness run \
            --non-interactive \
            --adapter noop \
            .devspark/defaults/templates/workflows/ci-checks.yaml
```

> **Note:** In CI, use the `noop` adapter for dry-run validation and reserve real AI adapter runs for when an AI agent is available and authorized. Many CI pipelines use DevSpark for workflow validation without running actual AI-generated code changes.

## Artifact Layout

The harness runtime writes execution artifacts to:

```
.documentation/
├── devspark/
│   └── runs/
│       ├── {workflow_run_id}.json    ← Pause state (for resume)
│       └── {workflow_run_id}/        ← Per-step outputs (if configured)
│           ├── verify-specs-complete.md
│           ├── archive-specs.md
│           └── generate-changelog.md
└── telemetry/
    └── workflow-events.jsonl          ← Append-only telemetry log
```

The run artifacts are generated records, not framework files. Upgrading DevSpark does not touch them.

The harness runtime becomes especially powerful when combined with custom adapters — the focus of Chapter 11. Before going there, it's worth making sure your specs are structured so failures surface early rather than midway through a long-running workflow. A workflow that fails loudly on step one beats one that silently skips a validation and discovers the problem at the commit step.

In Chapter 11, we move to advanced patterns: monorepo support and the multi-app registry that governs multiple applications in a single repository.
