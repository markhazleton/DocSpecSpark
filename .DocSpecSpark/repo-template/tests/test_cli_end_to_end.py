from pathlib import Path

from typer.testing import CliRunner

from docspec_cli.cli import app, build_constitution, constitution_to_tokens, render_tokens, selected_template_keys, slugify


runner = CliRunner()


def init_input() -> str:
    return "\n".join(
        [
            "Acme Manufacturing Inc.",
            "Ohio",
            "C Corporation",
            "Jane Smith",
            "Jane Smith",
            "Jane Smith",
            "Quality and Operations",
            "Annual",
            "#D32F2F",
            "Toledo Plant",
            "Build safe industrial equipment.",
            "12/31",
        ]
    ) + "\n"


def test_render_tokens_replaces_known_values() -> None:
    template = "# {{COMPANY_NAME}}\nOwner: {{DOCUMENT_OWNER}}\n"
    tokens = {
        "COMPANY_NAME": "Acme Manufacturing Inc.",
        "DOCUMENT_OWNER": "Operations",
    }

    rendered = render_tokens(template, tokens)

    assert "{{COMPANY_NAME}}" not in rendered
    assert "Acme Manufacturing Inc." in rendered
    assert "Operations" in rendered


def test_slugify_normalizes_document_names() -> None:
    assert slugify(" Lockout / Tagout Program ") == "lockout-tagout-program"


def test_profile_template_counts_match_planning_targets() -> None:
    assert len(selected_template_keys("not-for-profit")) == 21
    assert len(selected_template_keys("early-stage-startup")) == 8
    assert len(selected_template_keys("small-business-service")) == 10
    assert len(selected_template_keys("small-business-manufacturing")) == 40
    assert len(selected_template_keys("mid-sized-enterprise")) == 18
    assert len(selected_template_keys("large-enterprise")) == 25
    assert len(selected_template_keys("healthcare-organization")) == 11


def test_selected_template_keys_include_profile_specific_entries() -> None:
    template_keys = selected_template_keys("small-business-manufacturing")

    assert "hr-employee/employee-handbook.md" in template_keys
    assert "safety-environmental/lockout-tagout-program.md" in template_keys
    assert "quality-engineering/engineering-change-control-procedure.md" in template_keys
    assert "safety-environmental/spcc-plan.md" in template_keys
    assert "commercial-legal/export-compliance-program.md" in template_keys
    assert "hr-employee/training-records-procedure.md" in template_keys
    assert "it-security/acceptable-use-policy.md" in template_keys


def test_selected_template_keys_include_expanded_nonprofit_entries() -> None:
    template_keys = selected_template_keys("not-for-profit")

    assert "governance/conflict-of-interest-policy.md" in template_keys
    assert "hr-volunteer/volunteer-application.md" in template_keys
    assert "finance-tax/financial-policies-procedures.md" in template_keys
    assert "hr-employee/employee-handbook.md" in template_keys


def test_selected_template_keys_include_startup_and_service_entries() -> None:
    startup_templates = selected_template_keys("early-stage-startup")
    service_templates = selected_template_keys("small-business-service")

    assert "commercial-legal/ip-assignment-agreement.md" in startup_templates
    assert "corporate-governance/stock-option-plan.md" in startup_templates
    assert "hr-employee/remote-work-policy.md" in startup_templates
    assert "it-security/acceptable-use-policy.md" in startup_templates

    assert "policies/client-confidentiality-policy.md" in service_templates
    assert "policies/time-tracking-billing-policy.md" in service_templates
    assert "commercial-legal/client-engagement-agreement.md" in service_templates
    assert "hr-employee/professional-development-policy.md" in service_templates


def test_selected_template_keys_include_mid_enterprise_and_healthcare_entries() -> None:
    mid_templates = selected_template_keys("mid-sized-enterprise")
    large_templates = selected_template_keys("large-enterprise")
    healthcare_templates = selected_template_keys("healthcare-organization")

    assert "policies/data-governance-policy.md" in mid_templates
    assert "policies/vendor-management-policy.md" in mid_templates
    assert "governance/succession-planning-guide.md" in mid_templates
    assert "corporate-governance/m-and-a-integration-playbook.md" in mid_templates

    assert "corporate-governance/corporate-governance-charter.md" in large_templates
    assert "policies/insider-trading-policy.md" in large_templates
    assert "commercial-legal/third-party-code-of-conduct.md" in large_templates
    assert "governance/whistleblower-policy.md" in large_templates

    assert "healthcare/hipaa-privacy-policy.md" in healthcare_templates
    assert "healthcare/notice-of-privacy-practices.md" in healthcare_templates
    assert "commercial-legal/business-associate-agreement.md" in healthcare_templates


def test_constitution_to_tokens_contains_expected_company_values() -> None:
    constitution = build_constitution(
        company_name="Acme Manufacturing Inc.",
        profile_key="small-business-manufacturing",
        state="Ohio",
        entity_type="C Corporation",
        leader_name="Jane Smith",
        primary_contact="Jane Smith",
        approver_name="Jane Smith",
        document_owner="Quality and Operations",
        review_cadence="Annual",
        primary_color="#D32F2F",
        facility_name="Toledo Plant",
        mission_statement="Build safe industrial equipment.",
        fiscal_year_end="12/31",
    )

    tokens = constitution_to_tokens(constitution)

    assert tokens["COMPANY_NAME"] == "Acme Manufacturing Inc."
    assert tokens["STATE"] == "Ohio"
    assert tokens["EHS_MANAGER"] == "Quality and Operations"
    assert tokens["BOARD_CHAIR"] == "Jane Smith"
    assert tokens["HR_CONTACT"] == "Jane Smith"
    assert tokens["PAYMENT_TERMS"] == "Net 30"


def test_init_creates_target_workspace_and_status_reports_it(tmp_path: Path) -> None:
    workspace = tmp_path / "acme-docs"

    result = runner.invoke(app, ["init", str(workspace), "--profile", "small-business-manufacturing"], input=init_input())
    assert result.exit_code == 0, result.stdout
    assert (workspace / ".DocSpecSpark" / "constitution.yaml").exists()
    assert (workspace / ".github" / "workflows" / "docspec-publish.yml").exists()

    status_result = runner.invoke(app, ["status", str(workspace)])
    assert status_result.exit_code == 0, status_result.stdout
    assert "Framework: present" in status_result.stdout
    assert "Constitution: present" in status_result.stdout


def test_create_renders_document_from_filesystem_template(tmp_path: Path) -> None:
    workspace = tmp_path / "acme-docs"
    init_result = runner.invoke(app, ["init", str(workspace), "--profile", "small-business-manufacturing"], input=init_input())
    assert init_result.exit_code == 0, init_result.stdout

    create_result = runner.invoke(
        app,
        ["create", "employee-handbook.md", "--workspace", str(workspace), "--overwrite"],
    )
    assert create_result.exit_code == 0, create_result.stdout

    created = workspace / ".DocSpecSpark" / "documents" / "hr-employee" / "employee-handbook.md"
    assert created.exists()
    content = created.read_text(encoding="utf-8")
    assert "Acme Manufacturing Inc. Employee Handbook" in content
    assert "Jane Smith" in content


def test_publish_builds_site_and_release_bundle(tmp_path: Path) -> None:
    workspace = tmp_path / "acme-docs"
    init_result = runner.invoke(app, ["init", str(workspace), "--profile", "small-business-manufacturing"], input=init_input())
    assert init_result.exit_code == 0, init_result.stdout

    create_result = runner.invoke(
        app,
        ["create", "employee-handbook.md", "--workspace", str(workspace), "--overwrite"],
    )
    assert create_result.exit_code == 0, create_result.stdout

    publish_result = runner.invoke(
        app,
        ["publish", "--workspace", str(workspace), "--version", "1.0.0", "--overwrite"],
    )
    assert publish_result.exit_code == 0, publish_result.stdout

    assert (workspace / "site" / "index.html").exists()
    assert (workspace / "site" / "hr-employee" / "employee-handbook.html").exists()
    assert (workspace / ".DocSpecSpark" / "releases" / "v1.0.0" / "manifest.yaml").exists()
    assert (workspace / "dist" / "docspec-site-v1.0.0.zip").exists()


def test_healthcare_profile_can_render_specialized_document(tmp_path: Path) -> None:
    workspace = tmp_path / "healthcare-docs"
    result = runner.invoke(
        app,
        ["init", str(workspace), "--profile", "healthcare-organization"],
        input=init_input(),
    )
    assert result.exit_code == 0, result.stdout

    create_result = runner.invoke(
        app,
        ["create", "hipaa-privacy-policy.md", "--workspace", str(workspace), "--overwrite"],
    )
    assert create_result.exit_code == 0, create_result.stdout

    created = workspace / ".DocSpecSpark" / "documents" / "healthcare" / "hipaa-privacy-policy.md"
    assert created.exists()
    content = created.read_text(encoding="utf-8")
    assert "Acme Manufacturing Inc. HIPAA Privacy Policy" in content