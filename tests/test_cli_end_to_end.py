from pathlib import Path

from typer.testing import CliRunner

from docspark_cli import __version__
from docspark_cli.cli import app, stock_command_names


runner = CliRunner()


def test_package_version_is_alpha_start() -> None:
    assert __version__ == "0.1.0"


def test_init_creates_docspark_layout(tmp_path: Path) -> None:
    workspace = tmp_path / "acme-docs"

    result = runner.invoke(app, ["init", str(workspace), "--ai", "copilot", "--shell", "powershell"])

    assert result.exit_code == 0, result.stdout
    assert (workspace / ".docspark" / "defaults" / "commands" / "docspark.publish.md").exists()
    assert (workspace / ".docspark" / "defaults" / "commands" / "docspark.specify.md").exists()
    assert (workspace / ".docspark" / "templates" / "mkdocs-template.yml").exists()
    assert (workspace / ".docspark" / "templates" / "site-index-template.md").exists()
    assert (workspace / ".docspark" / "templates" / "spec-template.md").exists()
    assert (workspace / ".docspark" / "scripts" / "powershell" / "common.ps1").exists()
    assert (workspace / ".docspark" / "scripts" / "powershell" / "publish-context.ps1").exists()
    assert (workspace / ".documentation" / "memory" / "constitution.md").exists()
    assert (workspace / ".github" / "agents" / "docspark.specify.agent.md").exists()
    assert (workspace / ".github" / "agents" / "docspark.publish.agent.md").exists()
    assert (workspace / ".github" / "prompts" / "docspark.specify.prompt.md").exists()
    assert (workspace / ".github" / "prompts" / "docspark.publish.prompt.md").exists()
    assert (workspace / ".vscode" / "settings.json").exists()
    assert len(list((workspace / ".docspark" / "defaults" / "commands").glob("*.md"))) == len(stock_command_names())


def test_status_reports_inventory(tmp_path: Path) -> None:
    workspace = tmp_path / "status-docs"
    init_result = runner.invoke(app, ["init", str(workspace), "--ai", "cursor", "--shell", "bash"])
    assert init_result.exit_code == 0, init_result.stdout

    result = runner.invoke(app, ["status", str(workspace)])

    assert result.exit_code == 0, result.stdout
    assert "Installed" in result.stdout
    assert str(len(stock_command_names())) in result.stdout


def test_uninstall_removes_install_root_but_keeps_documentation(tmp_path: Path) -> None:
    workspace = tmp_path / "cleanup-docs"
    init_result = runner.invoke(app, ["init", str(workspace)])
    assert init_result.exit_code == 0, init_result.stdout

    uninstall_result = runner.invoke(app, ["uninstall", str(workspace)])

    assert uninstall_result.exit_code == 0, uninstall_result.stdout
    assert not (workspace / ".docspark").exists()
    assert (workspace / ".documentation").exists()


def test_gitignore_entry_added_once(tmp_path: Path) -> None:
    workspace = tmp_path / "ignore-docs"
    workspace.mkdir()
    (workspace / ".gitignore").write_text("node_modules/\n", encoding="utf-8")

    first = runner.invoke(app, ["init", str(workspace)])
    second = runner.invoke(app, ["init", str(workspace)])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    gitignore = (workspace / ".gitignore").read_text(encoding="utf-8")
    assert gitignore.count(".documentation/*/commands/") == 1


def test_examples_policy_portal_snapshot_exists() -> None:
    example_root = Path("examples") / "policy-portal"

    assert (example_root / ".docspark" / "defaults" / "commands" / "docspark.specify.md").exists()
    assert (example_root / ".documentation" / "memory" / "constitution.md").exists()
    assert (example_root / ".documentation" / "commands" / "docspark.pr-review.md").exists()
    assert (example_root / ".documentation" / "morgan-hazleton" / "commands" / "docspark.specify.md").exists()
    assert (example_root / ".github" / "agents" / "docspark.specify.agent.md").exists()