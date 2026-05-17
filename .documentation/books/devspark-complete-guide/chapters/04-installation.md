---
title: "Chapter 3: Installation and First Steps"
part: "Part I: Foundations"
---

# Chapter 3: Installation and First Steps

## The Installation Philosophy

On a recent project, I watched a team spend two hours debugging a setup failure because one developer had an outdated Node version that conflicted with the CLI bootstrap script. Every other team member had a working install; this one person was stuck, and the rest were blocked waiting. That experience crystallized something I'd been circling around: the installation step should have zero prerequisites beyond an AI agent and a repository. No npm, no runtime, no IDE plugin. Just a prompt.

That's the design I landed on for DevSpark. The primary installation method is a single URL-based prompt pasted into your agent's chat window. The agent downloads the quickstart file, reads its instructions, and sets up the framework. I'll walk you through that path — which almost all teams should use — show you what files land where, explain how upgrades work, and cover the optional CLI path for teams with strict deployment automation requirements (rare enough that it lives later in this chapter and in Appendix C).

This design has a specific consequence worth naming: DevSpark can be installed by any developer who has an AI coding assistant and a repository, regardless of their operating system, language runtime, or tool preferences. The trade-off here is that you lose the guarantee of validation a CLI would provide — the agent might make a mistake — but in my experience that risk is far smaller than the setup friction that kills momentum on day one.

Most teams start with the prompt-first approach. A CLI path exists for teams with strict deployment automation requirements, but it's rare enough to live in Appendix C (and in Step 6 below for reference).

## Step 1: Bootstrap with the Quickstart Prompt

Open a chat with your AI agent inside the target repository. Paste the command that matches your agent:

### Claude Code

```text
Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/quickstart/devspark_quickstart_claudecode.md
```

### GitHub Copilot

```text
@workspace Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/quickstart/devspark_quickstart_copilot.md
```

### Cursor

```text
Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/quickstart/devspark_quickstart_cursor.md
```

### Any Other Agent

```text
Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/quickstart/devspark_quickstart_generic.md
```

> **Note:** The `@workspace` prefix in the Copilot version is Copilot-specific syntax that enables repository-context mode. Other agents don't need it.

### What the Agent Asks During Bootstrap

The quickstart prompt is designed to ask the minimum necessary questions to get DevSpark running. What I've found is that teams often want to front-load configuration here — resist that impulse. The agent will:

1. Check whether DevSpark or a legacy layout is already present
2. Ask for the project name (if creating a new constitution)
3. Ask for the technology stack (if creating a new constitution)
4. Ask for the top three to five core principles the project should enforce

That's it. No detailed configuration, no lengthy governance input, no technical architecture decisions. Those come later, through the proper DevSpark workflow. The goal at bootstrap time is a working installation with a minimal initial constitution — you refine from there.

> **Tip:** If you are adding DevSpark to an existing project with an established architecture and coding patterns, answer the constitution questions minimally at bootstrap time. After installation, use `/devspark.discover-constitution` to generate a comprehensive constitution from your existing code.

## Step 2: What Gets Installed

After the agent completes the bootstrap process, your repository will contain:

### Framework Files (`.devspark/`)

```
.devspark/
├── defaults/
│   ├── commands/          ← 28 slash-command prompt files
│   ├── scripts/           ← Context-gathering scripts (PowerShell + Bash)
│   │   ├── get-context.ps1
│   │   └── get-context.sh
│   └── templates/         ← Atomic prompt and workflow templates
└── VERSION                ← Installed DevSpark version (e.g., "2.1.0")
```

### Project Artifacts (`.documentation/`)

```
.documentation/
├── memory/
│   └── constitution.md    ← Your initial constitution
└── commands/              ← Placeholder for team overrides (empty)
```

### Agent Shims

The agent creates the platform-specific shim files that hook the slash commands into your agent's command system:

| Agent | Shim Location |
|-------|--------------|
| Claude Code | `.claude/commands/devspark.*.md` |
| GitHub Copilot | `.github/prompts/devspark.*.prompt.md` |
| Cursor | `.cursor/prompts/devspark.*.md` |
| Generic | Agent-specific, depends on configuration |

These shim files are thin — they typically contain only a reference to the corresponding file in `.devspark/defaults/commands/`. Their purpose is to register the slash commands with the agent's command system.

### Version File

The `.devspark/VERSION` file contains the installed semantic version of DevSpark (e.g., `2.1.0`). This version is checked during upgrade operations to determine what has changed and needs updating.

> **Warning:** Never manually edit `.devspark/` files. These are the framework defaults. Your customizations go in `.documentation/` (team-level) or `.documentation/{git-user}/` (personal). Editing `.devspark/` directly will cause your changes to be overwritten on the next upgrade.

## Step 3: Verify the Installation

After bootstrap completes, verify the installation by checking that the key files exist:

```bash
# Check that the framework was installed
ls .devspark/defaults/commands/

# Check that the constitution was created
cat .documentation/memory/constitution.md

# Check the installed version
cat .devspark/VERSION

# Check that agent shims are in place (Claude Code example)
ls .claude/commands/
```

You should see 28 command files in `.devspark/defaults/commands/`, a populated constitution at `.documentation/memory/constitution.md`, and a valid version string in `.devspark/VERSION`.

To verify that the slash commands are working in your agent:

1. Open a new chat session with your AI agent in the repository
2. Type `/devspark.` and check if your agent's autocomplete shows the DevSpark commands
3. If autocomplete is not showing commands, restart your IDE completely (this is a common fix — IDE extensions often require a full restart to pick up newly created command files)

> **Troubleshooting:** If commands are not appearing after a full restart, verify that the agent shim files exist in the correct location. Run the quickstart prompt again — it is idempotent and will refresh the files without touching your constitution or project artifacts.

## Step 4: Create or Refine Your Constitution

The bootstrap process creates a minimal initial constitution. In most cases, you will want to refine it before using DevSpark for real work.

For a **new project** where you know what principles you want:

```text
/devspark.constitution Security-first: no hardcoded credentials, all input validated, parameterized SQL. TDD required: tests before code, 80% coverage minimum. All public APIs must have documentation.
```

For an **existing project** where you want to codify existing patterns:

```text
/devspark.discover-constitution
```

The discover command will:
1. Scan your codebase for existing patterns (testing, security, architecture, code quality)
2. Report findings with confidence levels (high/medium/low consistency)
3. Ask 8–10 targeted questions to fill gaps
4. Generate a draft constitution at `/.documentation/memory/constitution-draft.md`
5. Prompt you to review and finalize with `/devspark.constitution`

Chapter 5 covers the constitution creation and discovery process in full depth.

## Step 5: Run Your First Command

With the installation verified and the constitution in place, run your first real DevSpark workflow step:

```text
/devspark.specify Add a user profile page that shows account information and allows editing the display name and email address.
```

The `/devspark.specify` command will:
1. Classify the request (one-off fix, quick spec, or full spec) and explain the recommendation
2. Ask you to confirm or override the routing
3. If proceeding with a spec, create `.documentation/specs/user-profile/spec.md` with status `Draft`

The output from this command is the starting artifact for your first feature workflow. Chapter 4 walks through the complete lifecycle from this point.

## Step 6: CLI Installation (Optional)

For teams that need terminal-driven setup, scripted deployment, or the optional harness runtime, DevSpark provides a CLI that can be installed with `uv`:

```bash
uv tool install devspark-cli --force --from git+https://github.com/markhazleton/devspark.git
```

After installation, verify the CLI is working:

```bash
devspark doctor
```

`devspark doctor` checks the current machine for harness prerequisites and reports what is available, what is missing, and what adapters can be used on this machine.

To install or upgrade DevSpark in a repository via the CLI:

```bash
devspark upgrade
```

> **Note:** The CLI is additive. It does not replace the prompt-first workflow. The 28 slash commands remain the primary user interface. The CLI adds `devspark doctor`, `devspark harness ...`, and `devspark adapter ...` for terminal-driven operation. Chapter 10 covers the harness runtime in detail.

### When to Use the CLI

In practice, I've found the CLI useful in a narrow set of circumstances. Use it when you need:
- **Terminal-driven automation**: scripted installation across multiple repositories
- **CI/CD integration**: running workflow steps as part of a build pipeline
- **Declarative execution specs**: YAML-described multi-step engineering workflows
- **Environment validation**: `devspark doctor` confirms what is available on a machine

For typical solo and team development, the prompt-first quickstart is sufficient. See Appendix C for the full CLI bootstrap reference.

## Upgrading DevSpark

DevSpark updates happen frequently, and the upgrade process mirrors the installation process: prompt-first.

In your AI agent's chat interface:

```text
Follow the instructions at https://raw.githubusercontent.com/markhazleton/devspark/main/templates/commands/upgrade.md
```

Or via the slash command after a working installation:

```text
/devspark.upgrade
```

The upgrade command:
1. Reads `.devspark/VERSION` to determine the installed version
2. Downloads and compares the latest framework defaults
3. Shows you what changed in `.devspark/defaults/commands/`
4. Warns if any `.documentation/commands/` team overrides may be hiding structural changes in the updated stock prompts
5. Updates `.devspark/defaults/` with the new framework files
6. Updates `.devspark/VERSION` to the new version

The upgrade explicitly preserves your `.documentation/` directory. Your constitution, specs, decisions, and team overrides are untouched.

> **Recommended cadence:** Run a dry-run first, review the proposed changes, then apply. The upgrade command supports this workflow — it will show you what would change before committing to it.

## Quick Reference: Installation Checklist

```
☐ Open AI agent chat in target repository
☐ Paste agent-specific quickstart URL
☐ Answer bootstrap questions (project name, stack, principles)
☐ Verify .devspark/ directory exists
☐ Verify .documentation/memory/constitution.md exists
☐ Verify .devspark/VERSION contains a version string
☐ Verify agent shims exist in agent-specific directory
☐ Restart IDE if slash commands are not appearing
☐ Refine constitution with /devspark.constitution or /devspark.discover-constitution
☐ Run /devspark.specify to test the workflow
```

Once bootstrap completes, you'll have a working constitution and a set of agent shims ready to use. Before moving on, verify that `.devspark/` and `.documentation/` exist in your repo root — if they do, installation succeeded. Chapter 4 walks you through your first complete workflow, from `/devspark.specify` through a merged pull request.
