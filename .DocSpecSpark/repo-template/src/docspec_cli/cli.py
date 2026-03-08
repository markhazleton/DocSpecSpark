from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
from shutil import copy2, copytree, make_archive, rmtree
from textwrap import dedent
from typing import Any

from markdown_it import MarkdownIt
import typer
import yaml
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="DocSpecSpark Phase 1 MVP CLI.")
console = Console()
markdown_renderer = MarkdownIt("commonmark", {"html": True, "linkify": True})

DOCSPEC_ROOT = ".DocSpecSpark"
DEFAULT_SITE_OUTPUT = "site"
FRAMEWORK_MANIFEST = Path("templates/manifest.yaml")
DEFAULT_THEME_CSS = """
:root {
  --page-bg: #f4f1ea;
  --panel-bg: rgba(255, 255, 255, 0.88);
  --ink: #1d2433;
  --muted: #5c6576;
  --accent: #0f6c5b;
  --accent-strong: #09473c;
  --border: rgba(29, 36, 51, 0.12);
  --shadow: 0 20px 50px rgba(15, 36, 58, 0.12);
  --code-bg: #f0ece4;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(15, 108, 91, 0.12), transparent 32%),
    linear-gradient(180deg, #f7f4ee 0%, var(--page-bg) 100%);
}

a {
  color: var(--accent-strong);
}

.shell {
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 20px 72px;
}

.hero,
.card,
.document {
  background: var(--panel-bg);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.hero {
  padding: 32px;
  margin-bottom: 28px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.76rem;
  color: var(--accent);
}

h1, h2, h3 {
  line-height: 1.15;
}

.lede {
  color: var(--muted);
  font-size: 1.05rem;
  max-width: 64ch;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
  color: var(--muted);
  font-size: 0.92rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}

.card {
  padding: 20px;
}

.card h3 {
  margin-top: 0;
}

.document {
  padding: 32px;
}

.document-header {
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}

.breadcrumbs {
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 0.9rem;
}

pre,
code {
  font-family: Consolas, "Courier New", monospace;
}

pre {
  background: var(--code-bg);
  padding: 16px;
  overflow-x: auto;
  border-radius: 14px;
}

blockquote {
  margin: 0;
  padding-left: 16px;
  border-left: 4px solid rgba(15, 108, 91, 0.35);
  color: var(--muted);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

ul.doc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

ul.doc-list li + li {
  margin-top: 12px;
}

@media (max-width: 640px) {
  .shell {
    padding: 24px 14px 48px;
  }

  .hero,
  .document,
  .card {
    padding: 20px;
    border-radius: 16px;
  }
}
""".strip()

PROFILE_OPTIONS: list[tuple[str, str]] = [
    ("not-for-profit", "Not-for-Profit (with volunteers)"),
    ("early-stage-startup", "Early-Stage Startup (< 10 people)"),
    ("small-business-service", "Small Business - Service Industry"),
    ("small-business-manufacturing", "Small Business - Manufacturing"),
    ("mid-sized-enterprise", "Mid-Sized Enterprise"),
    ("large-enterprise", "Large Enterprise"),
    ("healthcare-organization", "Healthcare Organization"),
    ("custom", "Custom"),
]

PROFILE_PRESETS: dict[str, dict[str, str]] = {
    "not-for-profit": {
        "entity_type": "501(c)(3) Non-Profit",
        "leader_title": "Executive Director",
        "review_cadence": "Biannual",
        "primary_color": "#2E7D32",
        "document_owner": "Operations and Compliance",
        "facility_name": "Main Office",
        "mission_statement": "Advance mission-driven community programs with clear governance.",
        "board_size": "9",
    },
    "early-stage-startup": {
        "entity_type": "Delaware C Corporation",
        "leader_title": "CEO",
        "review_cadence": "As-needed",
        "primary_color": "#FF6F00",
        "document_owner": "Founder Operations",
        "facility_name": "Primary Office",
        "mission_statement": "Ship quickly while establishing lightweight operating controls.",
        "board_size": "3",
    },
    "small-business-service": {
        "entity_type": "LLC",
        "leader_title": "Managing Partner",
        "review_cadence": "Annual",
        "primary_color": "#1565C0",
        "document_owner": "Operations",
        "facility_name": "Headquarters",
        "mission_statement": "Deliver consistent client service with repeatable internal practices.",
        "board_size": "3",
    },
    "small-business-manufacturing": {
        "entity_type": "C Corporation",
        "leader_title": "CEO",
        "review_cadence": "Annual",
        "primary_color": "#D32F2F",
        "document_owner": "Quality and Operations",
        "facility_name": "Main Manufacturing Facility",
        "mission_statement": "Operate a safe, compliant, and efficient production environment.",
        "board_size": "5",
    },
    "mid-sized-enterprise": {
        "entity_type": "Corporation",
        "leader_title": "CEO",
        "review_cadence": "Annual",
        "primary_color": "#283593",
        "document_owner": "Corporate Operations",
        "facility_name": "Corporate Headquarters",
        "mission_statement": "Scale governance and operating controls across multiple teams.",
        "board_size": "7",
    },
    "large-enterprise": {
        "entity_type": "Corporation",
        "leader_title": "CEO",
        "review_cadence": "Annual",
        "primary_color": "#37474F",
        "document_owner": "Enterprise Governance",
        "facility_name": "Primary Campus",
        "mission_statement": "Coordinate enterprise-wide policy management and document governance.",
        "board_size": "11",
    },
    "healthcare-organization": {
        "entity_type": "Healthcare Organization",
        "leader_title": "Chief Executive Officer",
        "review_cadence": "Annual",
        "primary_color": "#00897B",
        "document_owner": "Clinical Operations",
        "facility_name": "Main Care Facility",
        "mission_statement": "Deliver safe care with documented compliance and operational discipline.",
        "board_size": "7",
    },
    "custom": {
        "entity_type": "Organization",
        "leader_title": "Executive Lead",
        "review_cadence": "Annual",
        "primary_color": "#455A64",
        "document_owner": "Operations",
        "facility_name": "Primary Site",
        "mission_statement": "Maintain clear, reusable business documentation.",
        "board_size": "3",
    },
}

SCRIPT_FILES: dict[str, str] = {
    "scripts/bash/init-company.sh": dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail
        uv run docspec init "$@"
        """
    ),
    "scripts/bash/create-document.sh": dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail
        uv run docspec create "$@"
        """
    ),
    "scripts/bash/build-site.sh": dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail
        uv run docspec build "$@"
        """
    ),
    "scripts/bash/publish-docs.sh": dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail
        uv run docspec publish "$@"
        """
    ),
    "scripts/powershell/Initialize-Company.ps1": dedent(
        """\
        #!/usr/bin/env pwsh
        $ErrorActionPreference = 'Stop'
        uv run docspec init @args
        """
    ),
    "scripts/powershell/Create-Document.ps1": dedent(
        """\
        #!/usr/bin/env pwsh
        $ErrorActionPreference = 'Stop'
        uv run docspec create @args
        """
    ),
    "scripts/powershell/Build-Site.ps1": dedent(
        """\
        #!/usr/bin/env pwsh
        $ErrorActionPreference = 'Stop'
        uv run docspec build @args
        """
    ),
    "scripts/powershell/Publish-Documents.ps1": dedent(
        """\
        #!/usr/bin/env pwsh
        $ErrorActionPreference = 'Stop'
        uv run docspec publish @args
        """
    ),
}

PUBLISH_WORKFLOW = dedent(
    """\
    name: publish-docspec-site

    on:
      workflow_dispatch:
      push:
        tags:
          - "v*"

    permissions:
      contents: read
      pages: write
      id-token: write

    jobs:
      publish:
        runs-on: ubuntu-latest
        environment:
          name: github-pages
          url: ${{ steps.deployment.outputs.page_url }}
        steps:
          - uses: actions/checkout@v4

          - uses: actions/setup-python@v5
            with:
              python-version: "3.11"

          - uses: astral-sh/setup-uv@v6

          - name: Install dependencies
            run: uv sync

          - name: Publish static site bundle
            shell: bash
            run: |
              VERSION="${GITHUB_REF_NAME#v}"
              uv run docspec publish --workspace . --version "$VERSION" --overwrite

          - uses: actions/configure-pages@v5

          - uses: actions/upload-pages-artifact@v3
            with:
              path: site

          - id: deployment
            uses: actions/deploy-pages@v4
    """
)


def profile_label(profile_key: str) -> str:
    for key, label in PROFILE_OPTIONS:
        if key == profile_key:
            return label
    return profile_key


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(resolved)
    return ordered


def framework_search_roots(search_start: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("DOCSPEC_FRAMEWORK_ROOT")
    if configured:
        candidates.append(Path(configured))

    for start in [search_start, Path.cwd(), Path(__file__).resolve()]:
        if start is None:
            continue
        path = start.resolve()
        if path.name == DOCSPEC_ROOT:
            candidates.append(path)
        candidates.extend(parent / DOCSPEC_ROOT for parent in [path, *path.parents])

    return unique_paths(candidates)


def resolve_framework_root(search_start: Path | None = None) -> Path:
    for candidate in framework_search_roots(search_start):
        if (candidate / FRAMEWORK_MANIFEST).exists():
            return candidate
    raise typer.BadParameter(
        "Could not locate the DocSpecSpark framework payload. Expected .DocSpecSpark/templates/manifest.yaml."
    )


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise typer.BadParameter(f"File not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise typer.BadParameter(f"Expected mapping in {path}")
    return payload


def write_yaml(path: Path, payload: dict[str, Any], overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise typer.BadParameter(f"File already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def write_text(path: Path, content: str, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise typer.BadParameter(f"File already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path, overwrite: bool = False) -> None:
    if target.exists() and not overwrite:
        raise typer.BadParameter(f"File already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, target)


def replace_tree(source: Path, target: Path, overwrite: bool = False) -> None:
    if target.exists():
        if not overwrite:
            raise typer.BadParameter(f"Directory already exists: {target}")
        rmtree(target)
    copytree(source, target)


def load_template_manifest(framework_root: Path) -> dict[str, Any]:
    payload = load_yaml(framework_root / FRAMEWORK_MANIFEST)
    if not isinstance(payload.get("base_templates", []), list):
        raise typer.BadParameter("Template manifest must define a base_templates list")
    if not isinstance(payload.get("profiles", {}), dict):
        raise typer.BadParameter("Template manifest must define a profiles mapping")
    return payload


def template_aliases(framework_root: Path) -> dict[str, str]:
    manifest = load_template_manifest(framework_root)
    aliases = manifest.get("aliases", {})
    if not isinstance(aliases, dict):
        raise typer.BadParameter("Template manifest aliases must be a mapping")
    return {str(key): str(value) for key, value in aliases.items()}


def selected_template_keys(profile_key: str, framework_root: Path | None = None) -> list[str]:
    resolved_framework_root = framework_root or resolve_framework_root()
    manifest = load_template_manifest(resolved_framework_root)
    profiles = manifest["profiles"]
    if profile_key not in profiles:
        valid = ", ".join(sorted(profiles))
        raise typer.BadParameter(f"Unknown profile '{profile_key}'. Use one of: {valid}")
    profile_payload = profiles[profile_key] or {}
    profile_templates = profile_payload.get("templates", [])
    if not isinstance(profile_templates, list):
        raise typer.BadParameter(f"Profile '{profile_key}' templates entry must be a list")
    return [str(item) for item in manifest["base_templates"]] + [str(item) for item in profile_templates]


def load_tokens(config_path: Path) -> dict[str, str]:
    payload = load_yaml(config_path)
    tokens = payload.get("tokens", {})
    if not isinstance(tokens, dict):
        raise typer.BadParameter("Expected 'tokens' mapping in config file")
    return {str(key): str(value) for key, value in tokens.items()}


def render_tokens(template_text: str, tokens: dict[str, str]) -> str:
    rendered = template_text
    for key, value in tokens.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "document"


def pick_profile(profile: str | None) -> str:
    if profile:
        if profile not in PROFILE_PRESETS:
            valid = ", ".join(key for key, _ in PROFILE_OPTIONS)
            raise typer.BadParameter(f"Unknown profile '{profile}'. Use one of: {valid}")
        return profile

    console.print("Select your organization profile:")
    for index, (_, label) in enumerate(PROFILE_OPTIONS, start=1):
        console.print(f"  {index}. {label}")

    choice = typer.prompt("Your choice [1-8]", default="1")
    try:
        position = int(choice) - 1
        return PROFILE_OPTIONS[position][0]
    except (IndexError, ValueError) as error:
        raise typer.BadParameter("Profile choice must be a number between 1 and 8") from error


def build_constitution(
    company_name: str,
    profile_key: str,
    state: str,
    entity_type: str,
    leader_name: str,
    primary_contact: str,
    approver_name: str,
    document_owner: str,
    review_cadence: str,
    primary_color: str,
    facility_name: str,
    mission_statement: str,
    fiscal_year_end: str,
) -> dict[str, Any]:
    preset = PROFILE_PRESETS[profile_key]
    people = {
        "primary_contact": primary_contact,
        "leadership_title": preset["leader_title"],
        "leadership_name": leader_name,
        "document_owner": document_owner,
        "approver_name": approver_name,
        "privacy_contact": document_owner,
        "volunteer_coordinator": primary_contact,
        "ehs_manager": document_owner,
        "quality_manager": document_owner,
        "hr_contact": primary_contact,
        "it_contact": primary_contact,
        "finance_contact": approver_name,
        "legal_contact": approver_name,
        "board_chair": approver_name,
        "board_size": preset["board_size"],
        "privacy_officer": document_owner,
        "trade_compliance_officer": document_owner,
        "medical_director": approver_name,
        "training_coordinator": primary_contact,
        "incident_response_team": document_owner,
        "plan_admin": document_owner,
    }
    return {
        "docspecspark": {
            "version": "0.3.0",
            "initialized_at": datetime.now(UTC).isoformat(),
            "profile": profile_key,
            "profile_label": profile_label(profile_key),
        },
        "company": {
            "name": company_name,
            "legal_entity_type": entity_type,
            "state": state,
            "facility_name": facility_name,
            "mission_statement": mission_statement,
            "fiscal_year_end": fiscal_year_end,
        },
        "people": people,
        "document_governance": {
            "review_cadence": review_cadence,
            "documents_root": ".DocSpecSpark/documents",
            "template_root": ".DocSpecSpark/templates",
            "releases_root": ".DocSpecSpark/releases",
            "site_theme_root": ".DocSpecSpark/site-theme",
        },
        "branding": {
            "primary_color": primary_color,
        },
    }


def constitution_to_tokens(constitution: dict[str, Any]) -> dict[str, str]:
    company = constitution["company"]
    people = constitution["people"]
    governance = constitution["document_governance"]
    branding = constitution["branding"]
    return {
        "COMPANY_NAME": company["name"],
        "ORG_NAME": company["name"],
        "ENTITY_NAME": company["name"],
        "STATE": company["state"],
        "LEGAL_ENTITY_TYPE": company["legal_entity_type"],
        "FACILITY_NAME": company["facility_name"],
        "MISSION_STATEMENT": company["mission_statement"],
        "FISCAL_YEAR_END": company["fiscal_year_end"],
        "PRIMARY_CONTACT_NAME": people["primary_contact"],
        "LEADERSHIP_TITLE": people["leadership_title"],
        "LEADERSHIP_NAME": people["leadership_name"],
        "DOCUMENT_OWNER": people["document_owner"],
        "APPROVER_NAME": people["approver_name"],
        "PRIVACY_CONTACT": people["privacy_contact"],
        "VOLUNTEER_COORDINATOR": people["volunteer_coordinator"],
        "EHS_MANAGER": people["ehs_manager"],
        "QUALITY_MANAGER": people["quality_manager"],
        "HR_CONTACT": people["hr_contact"],
        "IT_CONTACT": people["it_contact"],
        "FINANCE_CONTACT": people["finance_contact"],
        "LEGAL_CONTACT": people["legal_contact"],
        "BOARD_CHAIR": people["board_chair"],
        "BOARD_SIZE": people["board_size"],
        "PRIVACY_OFFICER": people["privacy_officer"],
        "TRADE_COMPLIANCE_OFFICER": people["trade_compliance_officer"],
        "MEDICAL_DIRECTOR": people["medical_director"],
        "TRAINING_COORDINATOR": people["training_coordinator"],
        "INCIDENT_RESPONSE_TEAM": people["incident_response_team"],
        "PLAN_ADMIN": people["plan_admin"],
        "JURISDICTION": company["state"],
        "PAYMENT_TERMS": "Net 30",
        "WARRANTY_PERIOD": "12 months",
        "REVIEW_CADENCE": governance["review_cadence"],
        "PRIMARY_COLOR": branding["primary_color"],
    }


def build_config(constitution: dict[str, Any]) -> dict[str, Any]:
    return {
        "framework": {
            "name": "DocSpecSpark",
            "version": constitution["docspecspark"]["version"],
        },
        "profile": constitution["docspecspark"]["profile"],
        "tokens": constitution_to_tokens(constitution),
    }


def resolve_template_path(template: str, templates_root: Path, aliases: dict[str, str] | None = None) -> Path:
    normalized = aliases.get(template, template) if aliases else template
    direct = templates_root / normalized
    if direct.exists():
        return direct

    with_suffix = templates_root / f"{normalized}.md"
    if with_suffix.exists():
        return with_suffix

    candidate = Path(normalized)
    if candidate.exists():
        return candidate

    template_name = candidate.name if candidate.name else normalized
    template_stem = Path(template_name).stem
    matches = sorted(
        path
        for path in templates_root.rglob("*.md")
        if path.name == template_name or path.stem == template_stem
    )
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        options = ", ".join(str(path.relative_to(templates_root)) for path in matches)
        raise typer.BadParameter(f"Template name is ambiguous: {template} ({options})")
    raise typer.BadParameter(f"Template not found: {template}")


def install_templates(
    source_framework_root: Path,
    templates_root: Path,
    profile_key: str,
    overwrite: bool = False,
) -> list[Path]:
    source_templates_root = source_framework_root / "templates"
    installed: list[Path] = []
    copy_file(source_templates_root / "manifest.yaml", templates_root / "manifest.yaml", overwrite=overwrite)
    for template_key in selected_template_keys(profile_key, source_framework_root):
        source = source_templates_root / template_key
        if not source.exists():
            raise typer.BadParameter(f"Framework template is missing: {source}")
        target = templates_root / template_key
        copy_file(source, target, overwrite=overwrite)
        installed.append(target)
    return installed


def install_scripts(framework_root: Path, overwrite: bool = False) -> None:
    for relative_path, content in SCRIPT_FILES.items():
        write_text(framework_root / relative_path, content, overwrite=overwrite)


def parse_frontmatter(markdown_text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", markdown_text, re.DOTALL)
    if not match:
        return {}, markdown_text
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise typer.BadParameter("Document frontmatter must be a YAML mapping")
    return frontmatter, match.group(2)


def normalize_version(version: str) -> str:
    normalized = version.strip()
    if normalized.lower().startswith("v"):
        normalized = normalized[1:]
    if not re.match(r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9._-]+)?$", normalized):
        raise typer.BadParameter("Version must look like 1.0.0 or 1.0.0-rc1")
    return normalized


def document_title(relative_path: Path, metadata: dict[str, Any]) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return relative_path.stem.replace("-", " ").title()


def company_name_for_workspace(workspace: Path) -> str:
    constitution_path = workspace / DOCSPEC_ROOT / "constitution.yaml"
    if not constitution_path.exists():
        return workspace.name.replace("-", " ").title()
    constitution = load_yaml(constitution_path)
    company = constitution.get("company", {})
    if isinstance(company, dict) and isinstance(company.get("name"), str):
        return company["name"]
    return workspace.name.replace("-", " ").title()


def build_document_records(workspace: Path) -> list[dict[str, Any]]:
    documents_root = workspace / DOCSPEC_ROOT / "documents"
    if not documents_root.exists():
        raise typer.BadParameter(f"Documents directory not found: {documents_root}")

    records: list[dict[str, Any]] = []
    for document_path in sorted(documents_root.rglob("*.md")):
        relative_path = document_path.relative_to(documents_root)
        metadata, body = parse_frontmatter(document_path.read_text(encoding="utf-8"))
        category = relative_path.parent.as_posix() if relative_path.parent != Path(".") else "general"
        html_path = relative_path.with_suffix(".html")
        records.append(
            {
                "source": document_path,
                "relative_markdown": relative_path,
                "relative_html": html_path,
                "metadata": metadata,
                "body": body,
                "category": category,
                "title": document_title(relative_path, metadata),
            }
        )
    return records


def ensure_theme_css(framework_root: Path, output_root: Path) -> Path:
    theme_source = framework_root / "site-theme" / "default.css"
    target = output_root / "assets" / "docspec.css"
    target.parent.mkdir(parents=True, exist_ok=True)
    if theme_source.exists():
        target.write_text(theme_source.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        target.write_text(DEFAULT_THEME_CSS + "\n", encoding="utf-8")
    return target


def render_index_html(company_name: str, generated_at: str, records: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record["category"], []).append(record)

    cards = []
    for category, category_records in sorted(grouped.items()):
        items = "".join(
            (
                f'<li><a href="{escape(record["relative_html"].as_posix())}">{escape(record["title"])}</a>'
                f' <span class="meta">{escape(record["relative_markdown"].as_posix())}</span></li>'
            )
            for record in category_records
        )
        cards.append(
            f"""
            <section class=\"card\">
              <h3>{escape(category.replace('-', ' ').title())}</h3>
              <ul class=\"doc-list\">{items}</ul>
            </section>
            """
        )

    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{escape(company_name)} Documentation</title>
          <link rel="stylesheet" href="assets/docspec.css">
        </head>
        <body>
          <main class="shell">
            <section class="hero">
              <div class="eyebrow">DocSpecSpark Publication</div>
              <h1>{escape(company_name)} Documentation</h1>
              <p class="lede">Static publication built from the rendered documents stored under .DocSpecSpark/documents.</p>
              <div class="meta">
                <span>{len(records)} documents</span>
                <span>Generated {escape(generated_at)}</span>
              </div>
            </section>
            <section class="grid">
              {''.join(cards)}
            </section>
          </main>
        </body>
        </html>
        """
    )


def render_document_html(company_name: str, record: dict[str, Any]) -> str:
    parts = record["relative_html"].parts
    prefix = "../" * (len(parts) - 1)
    breadcrumbs = " / ".join(escape(part) for part in record["relative_markdown"].parts)
    metadata_rows = []
    for key in ["owner", "review_cadence", "version", "effective_date"]:
        value = record["metadata"].get(key)
        if value:
            metadata_rows.append(f"<span>{escape(key.replace('_', ' ').title())}: {escape(str(value))}</span>")
    body_html = markdown_renderer.render(record["body"])

    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{escape(record['title'])} | {escape(company_name)}</title>
          <link rel="stylesheet" href="{prefix}assets/docspec.css">
        </head>
        <body>
          <main class="shell">
            <article class="document">
              <div class="document-header">
                <div class="breadcrumbs"><a href="{prefix}index.html">All documents</a> / {breadcrumbs}</div>
                <div class="eyebrow">Published document</div>
                <h1>{escape(record['title'])}</h1>
                <div class="meta">{''.join(metadata_rows)}</div>
              </div>
              {body_html}
            </article>
          </main>
        </body>
        </html>
        """
    )


def output_path_for_workspace(workspace: Path, output: Path) -> Path:
    return output if output.is_absolute() else workspace / output


def build_site(workspace: Path, output_dir: Path, overwrite: bool = True) -> tuple[Path, list[dict[str, Any]]]:
    framework_root = workspace / DOCSPEC_ROOT
    if not framework_root.exists():
        raise typer.BadParameter(f"Framework directory not found: {framework_root}")

    records = build_document_records(workspace)
    if not records:
        raise typer.BadParameter("No rendered documents found under .DocSpecSpark/documents")

    output_root = output_path_for_workspace(workspace, output_dir)
    if output_root.exists() and overwrite:
        rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    ensure_theme_css(framework_root, output_root)

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    company_name = company_name_for_workspace(workspace)
    for record in records:
        target = output_root / record["relative_html"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_document_html(company_name, record), encoding="utf-8")

    index_html = render_index_html(company_name, generated_at, records)
    (output_root / "index.html").write_text(index_html, encoding="utf-8")
    (output_root / "documents.json").write_text(
        json.dumps(
            [
                {
                    "title": record["title"],
                    "category": record["category"],
                    "markdown_path": record["relative_markdown"].as_posix(),
                    "html_path": record["relative_html"].as_posix(),
                }
                for record in records
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_root, records


def publish_site_bundle(
    workspace: Path,
    version: str,
    output_dir: Path,
    archive_dir: Path,
    overwrite: bool = False,
) -> tuple[Path, Path, Path, list[dict[str, Any]]]:
    normalized_version = normalize_version(version)
    site_root, records = build_site(workspace, output_dir, overwrite=True)
    framework_root = workspace / DOCSPEC_ROOT
    release_root = framework_root / "releases" / f"v{normalized_version}"
    if release_root.exists():
        if not overwrite:
            raise typer.BadParameter(f"Release already exists: {release_root}")
        rmtree(release_root)
    release_root.parent.mkdir(parents=True, exist_ok=True)
    copytree(site_root, release_root / "site")

    archive_output_root = output_path_for_workspace(workspace, archive_dir)
    archive_output_root.mkdir(parents=True, exist_ok=True)
    archive_base = archive_output_root / f"docspec-site-v{normalized_version}"
    archive_file = archive_base.with_suffix(".zip")
    if archive_file.exists() and overwrite:
        archive_file.unlink()
    elif archive_file.exists():
        raise typer.BadParameter(f"Archive already exists: {archive_file}")

    archive_path = Path(make_archive(str(archive_base), "zip", root_dir=site_root))
    manifest = {
        "version": normalized_version,
        "published_at": datetime.now(UTC).isoformat(),
        "company": company_name_for_workspace(workspace),
        "site_output": str(site_root.relative_to(workspace)),
        "archive": str(archive_path.relative_to(workspace)),
        "documents": [record["relative_markdown"].as_posix() for record in records],
    }
    write_yaml(release_root / "manifest.yaml", manifest, overwrite=True)
    write_yaml(framework_root / "releases" / "latest.yaml", manifest, overwrite=True)
    return site_root, release_root, archive_path, records


def initialize_company_workspace(
    workspace: Path,
    profile_key: str,
    overwrite: bool = False,
    source_framework_root: Path | None = None,
) -> tuple[dict[str, Any], list[Path]]:
    preset = PROFILE_PRESETS[profile_key]
    company_name = typer.prompt("Legal company name")
    state = typer.prompt("State of incorporation or operation", default="Ohio")
    entity_type = typer.prompt("Legal entity type", default=preset["entity_type"])
    leader_name = typer.prompt(f"{preset['leader_title']} name")
    primary_contact = typer.prompt("Primary contact name", default=leader_name)
    approver_name = typer.prompt("Document approver name", default=leader_name)
    document_owner = typer.prompt("Document owner team", default=preset["document_owner"])
    review_cadence = typer.prompt("Default review cadence", default=preset["review_cadence"])
    primary_color = typer.prompt("Primary brand color", default=preset["primary_color"])
    facility_name = typer.prompt("Primary facility or office", default=preset["facility_name"])
    mission_statement = typer.prompt("Mission statement", default=preset["mission_statement"])
    fiscal_year_end = typer.prompt("Fiscal year end (MM/DD)", default="12/31")

    constitution = build_constitution(
        company_name=company_name,
        profile_key=profile_key,
        state=state,
        entity_type=entity_type,
        leader_name=leader_name,
        primary_contact=primary_contact,
        approver_name=approver_name,
        document_owner=document_owner,
        review_cadence=review_cadence,
        primary_color=primary_color,
        facility_name=facility_name,
        mission_statement=mission_statement,
        fiscal_year_end=fiscal_year_end,
    )

    resolved_source_framework_root = source_framework_root or resolve_framework_root(workspace)
    framework_root = workspace / DOCSPEC_ROOT
    templates_root = framework_root / "templates"
    documents_root = framework_root / "documents"
    workflow_root = framework_root / "workflows"
    site_theme_root = framework_root / "site-theme"

    workspace.mkdir(parents=True, exist_ok=True)
    write_yaml(framework_root / "constitution.yaml", constitution, overwrite=overwrite)
    write_yaml(framework_root / "config.yaml", build_config(constitution), overwrite=overwrite)
    write_text(framework_root / "VERSION", constitution["docspecspark"]["version"], overwrite=overwrite)
    write_text(
        framework_root / "README.md",
        "Framework-managed templates, releases, site theme, and configuration for this company repository.",
        overwrite=overwrite,
    )
    write_text(
        framework_root / "prompts" / "README.md",
        "Reserved for future AI prompt packs and agent integrations.",
        overwrite=overwrite,
    )
    installed_templates = install_templates(resolved_source_framework_root, templates_root, profile_key, overwrite=overwrite)
    replace_tree(resolved_source_framework_root / "site-theme", site_theme_root, overwrite=overwrite)
    install_scripts(framework_root, overwrite=overwrite)
    write_text(workflow_root / "publish.yml", PUBLISH_WORKFLOW, overwrite=overwrite)
    write_text(workspace / ".github" / "workflows" / "docspec-publish.yml", PUBLISH_WORKFLOW, overwrite=overwrite)

    for relative_path in installed_templates:
        relative_parent = relative_path.relative_to(templates_root).parent
        (documents_root / relative_parent).mkdir(parents=True, exist_ok=True)

    readme_path = workspace / "README.md"
    if overwrite or not readme_path.exists():
        write_text(
            readme_path,
            dedent(
                f"""\
                # {company_name} Documentation

                This repository was initialized by DocSpecSpark for the {profile_label(profile_key)} profile.

                ## Quick Start

                ```bash
                uv run docspec show-constitution --workspace .
                uv run docspec list-templates --templates-root .DocSpecSpark/templates
                uv run docspec create employee-handbook.md --workspace . --overwrite
                uv run docspec build --workspace .
                uv run docspec publish --workspace . --version 1.0.0
                ```

                ## Repository Layout

                - `.DocSpecSpark/`: framework-managed templates, config, release manifests, scripts, and site theme assets
                - `.DocSpecSpark/documents/`: rendered company documents
                - `.github/workflows/docspec-publish.yml`: GitHub Pages publication workflow
                - `site/`: generated static publication output
                - `dist/`: zipped publication bundles created by `docspec publish`
                """
            ),
            overwrite=overwrite,
        )

    return constitution, installed_templates


@app.command("init")
def init_company(
    path: Path = typer.Argument(Path("."), help="Target company repository path"),
    profile: str | None = typer.Option(None, "--profile", help="Organization profile key"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing scaffold files"),
) -> None:
    """Initialize a company documentation repository."""
    workspace = path.resolve()
    profile_key = pick_profile(profile)
    constitution, installed_templates = initialize_company_workspace(workspace, profile_key, overwrite=overwrite)

    console.print(f"Initialized company repository at {workspace}")
    console.print(f"Profile: {constitution['docspecspark']['profile_label']}")
    console.print(f"Templates installed: {len(installed_templates)}")
    console.print("Next steps:")
    console.print(f"  1. cd {workspace}")
    console.print("  2. uv run docspec show-constitution")
    console.print("  3. uv run docspec list-templates")
    console.print("  4. uv run docspec create employee-handbook.md --overwrite")
    console.print("  5. uv run docspec build")
    console.print("  6. uv run docspec publish --version 1.0.0")


@app.command("status")
def status(workspace: Path = typer.Argument(Path("."))) -> None:
    """Show whether a company repository has been initialized."""
    root = workspace.resolve()
    framework_dir = root / DOCSPEC_ROOT
    templates_dir = framework_dir / "templates"
    config_file = framework_dir / "config.yaml"
    constitution_file = framework_dir / "constitution.yaml"
    documents_dir = framework_dir / "documents"
    site_dir = root / DEFAULT_SITE_OUTPUT
    latest_release = framework_dir / "releases" / "latest.yaml"

    template_count = len(list(templates_dir.rglob("*.md"))) if templates_dir.exists() else 0
    document_count = len(list(documents_dir.rglob("*.md"))) if documents_dir.exists() else 0

    console.print(f"Workspace: {root}")
    console.print(f"Framework: {'present' if framework_dir.exists() else 'missing'}")
    console.print(f"Constitution: {'present' if constitution_file.exists() else 'missing'}")
    console.print(f"Config: {'present' if config_file.exists() else 'missing'}")
    console.print(f"Templates: {template_count}")
    console.print(f"Documents: {document_count}")
    console.print(f"Site: {'present' if site_dir.exists() else 'missing'}")
    console.print(f"Latest release: {'present' if latest_release.exists() else 'missing'}")


@app.command("show-constitution")
def show_constitution(workspace: Path = typer.Option(Path("."), "--workspace")) -> None:
    """Show a concise company constitution summary."""
    constitution = load_yaml(workspace / DOCSPEC_ROOT / "constitution.yaml")
    company = constitution.get("company", {})
    people = constitution.get("people", {})
    docs = constitution.get("document_governance", {})

    table = Table(title="Company Constitution")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Company", str(company.get("name", "")))
    table.add_row("Profile", str(constitution.get("docspecspark", {}).get("profile_label", "")))
    table.add_row("Entity Type", str(company.get("legal_entity_type", "")))
    table.add_row("State", str(company.get("state", "")))
    table.add_row("Leader", f"{people.get('leadership_title', '')} {people.get('leadership_name', '')}".strip())
    table.add_row("Document Owner", str(people.get("document_owner", "")))
    table.add_row("Approver", str(people.get("approver_name", "")))
    table.add_row("Review Cadence", str(docs.get("review_cadence", "")))
    console.print(table)


@app.command("list-templates")
def list_templates(
    templates_root: Path = typer.Option(Path(".DocSpecSpark/templates"), "--templates-root")
) -> None:
    """List available Markdown templates."""
    if not templates_root.exists():
        raise typer.BadParameter(f"Templates directory not found: {templates_root}")

    templates = sorted(path for path in templates_root.rglob("*.md") if path.name != "README.md")
    if not templates:
        console.print("No templates found.")
        return

    for template_path in templates:
        console.print(template_path.relative_to(templates_root))


@app.command("create")
def create_document(
    template: str = typer.Argument(..., help="Template name or path"),
    workspace: Path = typer.Option(Path("."), "--workspace"),
    output_name: str | None = typer.Option(None, "--output-name", help="Optional output file name without extension"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite an existing output file"),
) -> None:
    """Create a company document from a template."""
    root = workspace.resolve()
    templates_root = root / DOCSPEC_ROOT / "templates"
    config_path = root / DOCSPEC_ROOT / "config.yaml"
    aliases = template_aliases(resolve_framework_root(root))
    template_path = resolve_template_path(template, templates_root, aliases=aliases)
    relative_template = template_path.relative_to(templates_root)
    output_stem = output_name or template_path.stem
    output_path = root / DOCSPEC_ROOT / "documents" / relative_template.parent / f"{slugify(output_stem)}.md"

    if output_path.exists() and not overwrite:
        raise typer.BadParameter(f"Output file already exists: {output_path}")

    tokens = load_tokens(config_path)
    tokens["DOCUMENT_TITLE"] = output_stem.replace("-", " ").title()
    rendered = render_tokens(template_path.read_text(encoding="utf-8"), tokens)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    console.print(f"Created {output_path}")


@app.command("list")
def list_documents(workspace: Path = typer.Option(Path("."), "--workspace")) -> None:
    """List rendered company documents."""
    documents_root = workspace.resolve() / DOCSPEC_ROOT / "documents"
    if not documents_root.exists():
        console.print("No documents directory found.")
        return

    documents = sorted(documents_root.rglob("*.md"))
    if not documents:
        console.print("No rendered documents found.")
        return

    for document_path in documents:
        console.print(document_path.relative_to(documents_root))


@app.command("render-template")
def render_template(
    template: str = typer.Argument(..., help="Template name or path"),
    output: Path = typer.Argument(..., help="Output file to create"),
    config: Path = typer.Option(Path(".DocSpecSpark/config.yaml"), "--config"),
    templates_root: Path = typer.Option(Path(".DocSpecSpark/templates"), "--templates-root"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite an existing output file"),
) -> None:
    """Render a template to an explicit output path."""
    aliases = template_aliases(resolve_framework_root())
    template_path = resolve_template_path(template, templates_root, aliases=aliases)
    if output.exists() and not overwrite:
        raise typer.BadParameter(f"Output file already exists: {output}")

    tokens = load_tokens(config)
    rendered = render_tokens(template_path.read_text(encoding="utf-8"), tokens)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    console.print(f"Rendered {template_path} -> {output}")


@app.command("build")
def build_command(
    workspace: Path = typer.Option(Path("."), "--workspace"),
    output_dir: Path = typer.Option(Path(DEFAULT_SITE_OUTPUT), "--output-dir"),
) -> None:
    """Build the static publication site."""
    site_root, records = build_site(workspace.resolve(), output_dir)
    console.print(f"Built static site at {site_root}")
    console.print(f"Documents published: {len(records)}")


@app.command("serve")
def serve_command(
    workspace: Path = typer.Option(Path("."), "--workspace"),
    output_dir: Path = typer.Option(Path(DEFAULT_SITE_OUTPUT), "--output-dir"),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    rebuild: bool = typer.Option(True, "--rebuild/--no-rebuild"),
) -> None:
    """Serve the static publication site locally."""
    resolved_workspace = workspace.resolve()
    if rebuild:
        site_root, _ = build_site(resolved_workspace, output_dir)
    else:
        site_root = output_path_for_workspace(resolved_workspace, output_dir)
        if not site_root.exists():
            raise typer.BadParameter(f"Site directory not found: {site_root}")

    handler = partial(SimpleHTTPRequestHandler, directory=str(site_root))
    with ThreadingHTTPServer((host, port), handler) as server:
        console.print(f"Serving {site_root} at http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            console.print("Stopped local server.")


@app.command("publish")
def publish_command(
    version: str = typer.Option(..., "--version", help="Semantic version for this publication, for example 1.0.0"),
    workspace: Path = typer.Option(Path("."), "--workspace"),
    output_dir: Path = typer.Option(Path(DEFAULT_SITE_OUTPUT), "--output-dir"),
    archive_dir: Path = typer.Option(Path("dist"), "--archive-dir"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite an existing release and archive"),
) -> None:
    """Build the site, create a release snapshot, and package a zip artifact."""
    site_root, release_root, archive_path, records = publish_site_bundle(
        workspace.resolve(),
        version,
        output_dir,
        archive_dir,
        overwrite=overwrite,
    )
    console.print(f"Built site at {site_root}")
    console.print(f"Release manifest: {release_root / 'manifest.yaml'}")
    console.print(f"Archive: {archive_path}")
    console.print(f"Documents published: {len(records)}")


if __name__ == "__main__":
    app()