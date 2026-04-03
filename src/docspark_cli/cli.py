from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json
import os
import shutil

from rich.console import Console
from rich.table import Table
import typer

APP_NAME = "DocSpark"
CLI_NAME = "docspark"
INSTALL_ROOT = ".docspark"
WORK_ROOT = ".documentation"
VERSION = "0.1.0"
SUPPORTED_AI = ("copilot", "claude", "cursor", "generic")
SUPPORTED_SHELLS = ("powershell", "bash")

COMMAND_SPECS: dict[str, dict[str, str]] = {
    "constitution": {
        "title": "Establish Documentation Principles",
        "purpose": "define the non-negotiable rules for how documents are created, reviewed, approved, and maintained",
        "deliverable": "an updated constitution in .documentation/memory/constitution.md",
    },
    "specify": {
        "title": "Define the Documentation Need",
        "purpose": "capture the audience, problem, scope, constraints, and outcomes for the document or doc set",
        "deliverable": "a document specification in .documentation/specs/",
    },
    "plan": {
        "title": "Create an Execution Plan",
        "purpose": "turn the specification into an implementation approach covering structure, review path, dependencies, and rollout",
        "deliverable": "a plan artifact linked to the active spec",
    },
    "tasks": {
        "title": "Break Work Into Tasks",
        "purpose": "produce an ordered checklist for drafting, review, approvals, migration, and publication",
        "deliverable": "a concrete task list for the active documentation change",
    },
    "implement": {
        "title": "Execute the Document Work",
        "purpose": "apply the approved plan and complete the document updates with traceable changes",
        "deliverable": "finished markdown changes plus any required supporting assets",
    },
    "pr-review": {
        "title": "Review Against the Constitution",
        "purpose": "review documentation changes for clarity, policy alignment, evidence, and operational correctness",
        "deliverable": "review findings ordered by risk",
    },
    "site-audit": {
        "title": "Audit the Documentation System",
        "purpose": "inspect the documentation repo for gaps, stale content, broken workflow assumptions, and information architecture issues",
        "deliverable": "a prioritized audit report",
    },
    "quickfix": {
        "title": "Handle a Focused Fix",
        "purpose": "solve a narrow documentation issue without forcing the full spec workflow",
        "deliverable": "a concise change plan and implementation",
    },
    "critic": {
        "title": "Stress Test the Proposal",
        "purpose": "challenge the plan from compliance, usability, governance, and operational failure angles",
        "deliverable": "explicit risks and mitigation actions",
    },
    "release": {
        "title": "Prepare a Documentation Release",
        "purpose": "package the updated documentation set for publication, release notes, and archival",
        "deliverable": "release-ready summary and archive guidance",
    },
    "publish": {
        "title": "Publish a Documentation Site",
        "purpose": "turn the approved markdown corpus into a GitHub Pages-ready static site with a landing page, clear navigation, and links to every publishable document",
        "deliverable": "a docs/ site structure, markdown-first generator config, and publication workflow ready for review or deployment",
    },
    "harvest": {
        "title": "Archive Stale Artifacts",
        "purpose": "identify obsolete drafts, superseded decisions, and completed work products that should move out of the active path",
        "deliverable": "an archive plan and cleanup list",
    },
    "evolve-constitution": {
        "title": "Improve the Rules",
        "purpose": "propose principled amendments to the documentation constitution based on actual repo pain points",
        "deliverable": "specific amendment text and rationale",
    },
    "repo-story": {
        "title": "Explain the Documentation History",
        "purpose": "turn commit history and decisions into a narrative of how the documentation system evolved",
        "deliverable": "a concise repo story",
    },
    "clarify": {
        "title": "Ask the Missing Questions",
        "purpose": "surface the unanswered questions that would make a document inaccurate, incomplete, or ambiguous",
        "deliverable": "a short clarification questionnaire",
    },
    "analyze": {
        "title": "Cross-Check Artifacts",
        "purpose": "compare constitution, spec, plan, tasks, and existing docs for contradictions or gaps",
        "deliverable": "consistency findings and recommended corrections",
    },
    "checklist": {
        "title": "Generate a Quality Checklist",
        "purpose": "produce a validation checklist for content quality, approval readiness, and publication safety",
        "deliverable": "a reusable checklist",
    },
    "personalize": {
        "title": "Create Personal Overrides",
        "purpose": "generate a user-specific command override while preserving the team baseline",
        "deliverable": "a personal command file under .documentation/{git-user}/commands/",
    },
    "discover-constitution": {
        "title": "Infer Principles From the Repo",
        "purpose": "derive a starter constitution from the current documentation structure and writing patterns",
        "deliverable": "a proposed constitution draft",
    },
    "archive": {
        "title": "Archive Completed Work",
        "purpose": "move completed specs, plans, and tasks out of the active path while retaining traceability",
        "deliverable": "an archive action plan",
    },
    "upgrade": {
        "title": "Upgrade DocSpark Assets",
        "purpose": "refresh installed stock prompts and scripts while preserving user-owned customizations",
        "deliverable": "an upgrade summary and validation checklist",
    },
    "taskstoissues": {
        "title": "Convert Tasks Into Issues",
        "purpose": "map the task list into trackable issue-sized work items for document production and review",
        "deliverable": "issue-ready task breakdown",
    },
}

HELPER_TEMPLATES = {
    "spec-template.md": "# Document Spec\n\n## Summary\n\n## Audience\n\n## Problem\n\n## Scope\n\n## Required Sources\n\n## Approval Path\n\n## Success Criteria\n",
    "plan-template.md": "# Document Plan\n\n## Scope\n\n## Information Architecture\n\n## Review Workflow\n\n## Risks\n\n## Rollout\n",
    "tasks-template.md": "# Document Tasks\n\n- [ ] Confirm scope\n- [ ] Gather sources\n- [ ] Draft content\n- [ ] Run review\n- [ ] Publish or merge\n",
    "checklist-template.md": "# Document Quality Checklist\n\n- [ ] Audience is explicit\n- [ ] Source of truth is identified\n- [ ] Required reviewers are listed\n- [ ] Action steps are testable\n- [ ] Ownership is clear\n",
    "site-index-template.md": "# [COMPANY_NAME] Documentation\n\nWelcome to the central documentation hub for [COMPANY_NAME]. This landing page should orient readers quickly, route them to the right document set, and highlight the most important operational guidance first.\n\n## Start Here\n\n- [About this documentation set](about.md)\n- [Policies and standards](policies/index.md)\n- [Procedures and playbooks](procedures/index.md)\n- [Reference and forms](reference/index.md)\n\n## Featured Documents\n\n- [Primary handbook](handbook.md)\n- [Operational checklist](operations/checklist.md)\n- [Latest release notes](releases/index.md)\n\n## Document Catalog\n\nAdd a generated or maintained index of every publishable markdown document, grouped by audience or function rather than by raw folder name.\n",
    "mkdocs-template.yml": "site_name: [COMPANY_NAME] Documentation\nsite_description: Trusted operational guidance for [COMPANY_NAME]\nsite_url: [SITE_URL]\nrepo_url: [REPOSITORY_URL]\ndocs_dir: docs\nsite_dir: site\ntheme:\n  name: material\n  features:\n    - navigation.indexes\n    - navigation.sections\n    - navigation.top\n    - search.suggest\n    - search.highlight\nmarkdown_extensions:\n  - admonition\n  - attr_list\n  - def_list\n  - tables\n  - toc:\n      permalink: true\nplugins:\n  - search\nnav:\n  - Home: index.md\n",
    "github-pages-workflow-template.yml": "name: docspark-publish\n\non:\n  push:\n    branches: [main]\n    paths:\n      - 'docs/**'\n      - 'mkdocs.yml'\n      - '.github/workflows/docspark-publish.yml'\n  workflow_dispatch:\n\npermissions:\n  contents: read\n  pages: write\n  id-token: write\n\nconcurrency:\n  group: github-pages\n  cancel-in-progress: true\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n    environment:\n      name: github-pages\n      url: ${{ steps.deployment.outputs.page_url }}\n    steps:\n      - name: Check out repository\n        uses: actions/checkout@v4\n\n      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n\n      - name: Install static site generator\n        run: pip install mkdocs-material\n\n      - name: Build site\n        run: mkdocs build --strict\n\n      - name: Configure Pages\n        uses: actions/configure-pages@v5\n\n      - name: Upload Pages artifact\n        uses: actions/upload-pages-artifact@v3\n        with:\n          path: site\n\n      - name: Deploy to GitHub Pages\n        id: deployment\n        uses: actions/deploy-pages@v4\n",
    "agent-file-template.md": "## Prompt Resolution\n\nResolve from personal override, then team override, then stock DocSpark command.\n\n## User Input\n\n{{input}}\n",
    "vscode-settings.json": json.dumps(
        {
            "chat.agent.enabled": True,
            "github.copilot.chat.codeGeneration.instructions": [
                {"text": "Use DocSpark workflow prompts when the repo is document-driven."}
            ],
        },
        indent=2,
    )
    + "\n",
}

COMMON_SCRIPT_HEADER = "# DocSpark helper script\n"

SHELL_SCRIPTS = {
    "powershell": {
        "common.ps1": COMMON_SCRIPT_HEADER + "param()\nWrite-Output 'DocSpark PowerShell helpers loaded.'\n",
        "platform.ps1": COMMON_SCRIPT_HEADER + "param()\nWrite-Output 'powershell'\n",
        "check-prerequisites.ps1": COMMON_SCRIPT_HEADER + "param()\nGet-Command git, uv -ErrorAction SilentlyContinue | Select-Object Name\n",
        "create-new-document.ps1": COMMON_SCRIPT_HEADER + "param([string]$Name)\nWrite-Output \"Create spec for: $Name\"\n",
        "setup-plan.ps1": COMMON_SCRIPT_HEADER + "param([string]$SpecPath)\nWrite-Output \"Plan context for: $SpecPath\"\n",
        "document-context.ps1": COMMON_SCRIPT_HEADER + "param()\nGet-ChildItem .documentation -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName\n",
        "review-context.ps1": COMMON_SCRIPT_HEADER + "param()\nGet-ChildItem . -Recurse -Include *.md -File | Select-Object -First 50 FullName\n",
        "release-context.ps1": COMMON_SCRIPT_HEADER + "param()\nWrite-Output 'Prepare release notes from specs, decisions, and merged docs.'\n",
        "publish-context.ps1": COMMON_SCRIPT_HEADER + "param()\nGet-ChildItem . -Recurse -Include *.md -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\\\(\\.git|\\.venv|dist|site)\\\\' } | Select-Object FullName\n",
    },
    "bash": {
        "common.sh": COMMON_SCRIPT_HEADER + "printf 'DocSpark Bash helpers loaded.\\n'\n",
        "platform.sh": COMMON_SCRIPT_HEADER + "printf 'bash\\n'\n",
        "check-prerequisites.sh": COMMON_SCRIPT_HEADER + "command -v git >/dev/null && echo git\ncommand -v uv >/dev/null && echo uv\n",
        "create-new-document.sh": COMMON_SCRIPT_HEADER + "printf 'Create spec for: %s\\n' \"${1:-unnamed}\"\n",
        "setup-plan.sh": COMMON_SCRIPT_HEADER + "printf 'Plan context for: %s\\n' \"${1:-spec}\"\n",
        "document-context.sh": COMMON_SCRIPT_HEADER + "find .documentation -type f 2>/dev/null\n",
        "review-context.sh": COMMON_SCRIPT_HEADER + "find . -name '*.md' -type f | head -n 50\n",
        "release-context.sh": COMMON_SCRIPT_HEADER + "printf 'Prepare release notes from specs, decisions, and merged docs.\\n'\n",
        "publish-context.sh": COMMON_SCRIPT_HEADER + "find . -type f -name '*.md' ! -path './.git/*' ! -path './.venv/*' ! -path './dist/*' ! -path './site/*'\n",
    },
}

STARTER_CONSTITUTION = """# DocSpark Constitution\n\n## Project\n[PROJECT_NAME]\n\n## Purpose\nMaintain documentation as an operational system, not a pile of isolated markdown files.\n\n## Core Principles\n- Write for the actual audience and decision context.\n- Make ownership, review cadence, and approval paths explicit.\n- Prefer one source of truth over duplicated guidance.\n- Treat ambiguity as a defect and resolve it early.\n- Archive stale work so active guidance stays trustworthy.\n\n## Stack\n- Markdown\n- Git\n- AI assistant workflows\n\n## Review Standard\nEvery substantive document change should name the owner, reviewers, and publication path.\n"""

DOCSPARK_SETTINGS = {
    "ai": "copilot",
    "shell": "powershell",
    "command_prefix": "docspark",
}

console = Console()
app = typer.Typer(help="DocSpark CLI for a document AI workflow derived from DevSpark.", add_completion=False)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_shell() -> str:
    return "powershell" if os.name == "nt" else "bash"


def resolve_workspace(target: Path | None, here: bool) -> Path:
    if here:
        return Path.cwd().resolve()
    if target is None:
        raise typer.BadParameter("Provide a target path or use --here.")
    return target.resolve()


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str, *, force: bool = False) -> None:
    if path.exists() and not force:
        return
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def append_unique_line(path: Path, line: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = existing.splitlines()
    if line in lines:
        return
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{prefix}{line}\n")


def render_command_markdown(name: str, spec: dict[str, str]) -> str:
    return (
        f"# /{CLI_NAME}.{name}\n\n"
        f"## Goal\n{spec['title']}\n\n"
        f"## Use This Command To\n{spec['purpose'].capitalize()}.\n\n"
        "## Operating Rules\n"
        "- Work from the repository's constitution before inventing new policy.\n"
        "- Prefer updating existing source-of-truth documents over creating duplicates.\n"
        "- Call out assumptions and missing information explicitly.\n"
        "- Keep outputs in markdown unless the user asks for another format.\n\n"
        f"## Expected Output\nProduce {spec['deliverable']}.\n"
    )


def stock_command_names() -> list[str]:
    return list(COMMAND_SPECS.keys())


def agent_shim_text(name: str) -> str:
    return f"---\nname: \"{CLI_NAME}.{name}\"\ndescription: \"Resolve and run the DocSpark {name} workflow\"\n---\n\n## Prompt Resolution\n\nDetermine the current git user by running `git config user.name`. Normalize to a folder-safe slug: lowercase, replace spaces with hyphens, strip non-alphanumeric or hyphen characters.\n\nRead and execute the instructions from the first file that exists:\n1. `.documentation/{{git-user}}/commands/{CLI_NAME}.{name}.md`\n2. `.documentation/commands/{CLI_NAME}.{name}.md`\n3. `.{CLI_NAME}/defaults/commands/{CLI_NAME}.{name}.md`\n\n## User Input\n\n{{input}}\n"


def prompt_shim_text(name: str) -> str:
    return agent_shim_text(name).split("---\n", 2)[-1]


def install_commands(install_root: Path, *, force: bool) -> None:
    commands_root = install_root / "defaults" / "commands"
    for name, spec in COMMAND_SPECS.items():
        write_text(commands_root / f"{CLI_NAME}.{name}.md", render_command_markdown(name, spec), force=force)


def install_templates(install_root: Path, *, force: bool) -> None:
    templates_root = install_root / "templates"
    for name, content in HELPER_TEMPLATES.items():
        write_text(templates_root / name, content, force=force)


def install_scripts(install_root: Path, shell_name: str, *, force: bool) -> None:
    script_root = install_root / "scripts" / shell_name
    for name, content in SHELL_SCRIPTS[shell_name].items():
        write_text(script_root / name, content, force=force)


def install_shims(workspace: Path, *, force: bool) -> None:
    agents_root = workspace / ".github" / "agents"
    prompts_root = workspace / ".github" / "prompts"
    for name in stock_command_names():
        write_text(agents_root / f"{CLI_NAME}.{name}.agent.md", agent_shim_text(name), force=force)
        write_text(prompts_root / f"{CLI_NAME}.{name}.prompt.md", prompt_shim_text(name), force=force)


def install_workspace_files(workspace: Path, ai: str, shell_name: str, *, force: bool) -> None:
    install_root = workspace / INSTALL_ROOT
    work_root = workspace / WORK_ROOT
    for path in [
        install_root / "defaults" / "commands",
        install_root / "scripts" / shell_name,
        install_root / "templates",
        install_root / "memory",
        work_root / "memory",
        work_root / "specs",
        work_root / "commands",
        work_root / "decisions",
        workspace / ".github" / "agents",
        workspace / ".github" / "prompts",
        workspace / ".vscode",
    ]:
        ensure_directory(path)

    install_commands(install_root, force=force)
    install_templates(install_root, force=force)
    install_scripts(install_root, shell_name, force=force)
    install_shims(workspace, force=force)

    constitution = STARTER_CONSTITUTION.replace("[PROJECT_NAME]", workspace.name)
    write_text(install_root / "memory" / "constitution.md", constitution, force=force)
    write_text(work_root / "memory" / "constitution.md", constitution, force=False)

    settings = dict(DOCSPARK_SETTINGS)
    settings["ai"] = ai
    settings["shell"] = shell_name
    write_text(work_root / "docspark.json", json.dumps(settings, indent=2) + "\n", force=force)
    write_text(workspace / ".vscode" / "settings.json", HELPER_TEMPLATES["vscode-settings.json"], force=False)

    version_text = (
        f"version: {VERSION}\n"
        f"installed: {datetime.now(UTC).date().isoformat()}\n"
        "method: cli\n"
        "migrated-from: fresh\n"
    )
    write_text(install_root / "VERSION", version_text, force=True)
    append_unique_line(workspace / ".gitignore", "# DocSpark")
    append_unique_line(workspace / ".gitignore", ".documentation/*/commands/")


def remove_if_exists(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


@app.command()
def init(
    target: Path | None = typer.Argument(None, exists=False, file_okay=False, dir_okay=True),
    here: bool = typer.Option(False, "--here", help="Install into the current directory."),
    ai: str = typer.Option("copilot", "--ai", help="Primary assistant."),
    shell: str | None = typer.Option(None, "--shell", help="Script shell to install."),
    force: bool = typer.Option(False, "--force", help="Overwrite stock DocSpark files."),
) -> None:
    if ai not in SUPPORTED_AI:
        raise typer.BadParameter(f"Unsupported AI '{ai}'. Choose from: {', '.join(SUPPORTED_AI)}")
    shell_name = shell or default_shell()
    if shell_name not in SUPPORTED_SHELLS:
        raise typer.BadParameter(f"Unsupported shell '{shell_name}'. Choose from: {', '.join(SUPPORTED_SHELLS)}")

    workspace = resolve_workspace(target, here)
    ensure_directory(workspace)
    install_workspace_files(workspace, ai, shell_name, force=force)
    console.print(f"Installed {APP_NAME} {VERSION} into {workspace}")
    console.print(f"Stock commands: {len(stock_command_names())}")
    console.print(f"Primary AI: {ai}")
    console.print(f"Shell scripts: {shell_name}")


@app.command("uninstall")
def uninstall(
    target: Path | None = typer.Argument(None, exists=False, file_okay=False, dir_okay=True),
    here: bool = typer.Option(False, "--here", help="Uninstall from the current directory."),
) -> None:
    workspace = resolve_workspace(target, here)
    remove_if_exists(workspace / INSTALL_ROOT)
    for name in stock_command_names():
        remove_if_exists(workspace / ".github" / "agents" / f"{CLI_NAME}.{name}.agent.md")
        remove_if_exists(workspace / ".github" / "prompts" / f"{CLI_NAME}.{name}.prompt.md")
    console.print(f"Removed {INSTALL_ROOT} and DocSpark shims from {workspace}")


@app.command()
def status(
    target: Path = typer.Argument(Path("."), exists=False, file_okay=False, dir_okay=True),
) -> None:
    workspace = target.resolve()
    install_root = workspace / INSTALL_ROOT
    commands_root = install_root / "defaults" / "commands"
    table = Table(title=f"{APP_NAME} Status")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Workspace", str(workspace))
    table.add_row("Installed", "yes" if install_root.exists() else "no")
    table.add_row("Stock commands", str(len(list(commands_root.glob("*.md"))) if commands_root.exists() else 0))
    table.add_row("Constitution", "yes" if (workspace / WORK_ROOT / "memory" / "constitution.md").exists() else "no")
    table.add_row("Agent shims", str(len(list((workspace / ".github" / "agents").glob(f"{CLI_NAME}.*.agent.md"))) if (workspace / ".github" / "agents").exists() else 0))
    console.print(table)


@app.command("list-assets")
def list_assets() -> None:
    table = Table(title=f"{APP_NAME} Asset Inventory")
    table.add_column("Type")
    table.add_column("Count")
    table.add_row("Commands", str(len(stock_command_names())))
    table.add_row("Helper templates", str(len(HELPER_TEMPLATES)))
    table.add_row("PowerShell scripts", str(len(SHELL_SCRIPTS["powershell"])))
    table.add_row("Bash scripts", str(len(SHELL_SCRIPTS["bash"])))
    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()