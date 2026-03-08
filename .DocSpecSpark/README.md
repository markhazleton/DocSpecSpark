# DocSpecSpark - Planning Repository

This directory contains all planning documents for the **DocSpecSpark** project - a document-focused adaptation of Spec Kit for creating business documentation (policies, procedures, handbooks, training materials).

## Project Vision

**DocSpecSpark** is a Git-based document management system for creating, versioning, and publishing business documentation. It applies the Spec-Driven Development methodology from [Spec Kit](https://github.com/github/spec-kit) to document creation workflows.

## Bootstrap The Source Repository

When you are ready to spin this planning bundle into its own source repository, copy `.DocSpecSpark/` into the root of a new `DocSpecSpark` GitHub repository and run one of these scripts:

The installed DocSpecSpark solution should keep all company-repo work products under the single top-level `.DocSpecSpark/` folder, including documents, templates, scripts, prompts, workflows, and configuration.

```powershell
./.DocSpecSpark/bootstrap-docspecspark.ps1
```

```bash
./.DocSpecSpark/bootstrap-docspecspark.sh
```

See [BOOTSTRAP.md](BOOTSTRAP.md) for the complete flow and what gets generated.

### Core Principles

> **"Constitution as Single Source of Truth"**  
> All company metadata lives in `constitution.yaml`. Templates use `{{TOKENS}}` that are automatically replaced from the constitution when documents are created.

> **"Markdown as source of truth. Git for versioning. Static site for viewing."**  
> Documents are Markdown files in Git. Static site (Docusaurus) provides professional viewing. No complex CMS required.

### Architecture: Constitution → Templates → Documents

```
constitution.yaml                    Templates (61)                Documents
├── company.legal_name        →     {{COMPANY_NAME}}         →    Acme Manufacturing Inc.
├── company.executives.ceo    →     {{CEO_NAME}}             →    John Smith
├── company.state             →     {{STATE}}                →    Ohio
├── company.dept_heads.ehs    →     {{EHS_MANAGER}}          →    David Martinez
└── ... (all metadata)        →     ... (all tokens)         →    ... (auto-replaced)

Update once in constitution → All future documents use new values
```

**Key Benefits**:
- **Consistency**: Company name, executive names, addresses are identical across all documents
- **Maintainability**: Change CEO once in constitution, not in 50 documents
- **Validation**: Constitution builder ensures required metadata is collected
- **Auditability**: Git tracks all changes to constitution and documents

### MVP: The "Spark" Approach

The Phase 1 MVP follows the "Spark" philosophy: **minimal, fast, Git-native**. No complex workflows, no web app, no SharePoint—just:

1. **Constitution Builder** - Interactive questionnaire populates company metadata
2. **Template Token Replacement** - `{{TOKENS}}` auto-filled from constitution
3. **Markdown files** stored in Git
4. **Static site** (Docusaurus) for viewing documents
5. **Git tags** for version control
6. **Minimal CLI** for scaffolding and publishing

This keeps the barrier to entry low while providing robust version control, consistent metadata, and professional document viewing.

## Key Design Principles (Post-MVP Evolution)

1. **One Repository Per Company**: Each client gets an isolated repository with their constitution, templates, and published documents
2. **Multi-Interface Support (Phase 3+)**: Accessible via CLI (Phase 1) → Web app (Phase 3) → SharePoint/Teams (Phase 4)
3. **Compliance-First (Phase 2)**: Multi-framework validation (ISO 9001, SOC 2, GDPR, HIPAA, Labor Law)
4. **Template-Driven**: Extensive library of pre-built document templates for rapid creation
5. **Hybrid Output Formats (Phase 3+)**: Markdown as source of truth, exports to MS Word/PDF with version tracking

## Planning Documents

### Getting Started
- [mvp-quick-start.md](mvp-quick-start.md) - **START HERE** - Phase 1 MVP overview, user workflows, what's included/excluded
- [phased-rollout-plan.md](phased-rollout-plan.md) - 4-phase delivery strategy (MVP → Enterprise)

### Architecture & Design
- [architecture-decisions.md](architecture-decisions.md) - Multi-interface approach, GitHub API integration, SharePoint/Teams strategy
- [integration-strategy.md](integration-strategy.md) - SharePoint, Teams, MS Word integration patterns (Phase 4)
- [user-personas.md](user-personas.md) - Technical vs. non-technical user flows
- [company-profiles.md](company-profiles.md) - 7 organizational profiles with pre-configured templates

### Core Components
- [company-constitution-schema.md](company-constitution-schema.md) - Company metadata, compliance frameworks, document governance
- [nonprofit-template-library.md](nonprofit-template-library.md) - **21 nonprofit templates** derived from KeyDocuments-NotForProfits.md analysis
- [smallbusiness-template-library.md](smallbusiness-template-library.md) - **40 small business manufacturing templates** derived from KeyDocuments-SmallBusiness.md analysis
- [workflow-commands.md](workflow-commands.md) - Spec → Plan → Tasks → Draft → Compliance Review → Publish

### Technical Specifications
- [cli-design.md](cli-design.md) - Command-line interface for technical users
- [web-app-design.md](web-app-design.md) - Web application for non-technical users (GitHub API-based)
- [github-actions-workflows.md](github-actions-workflows.md) - Automation for document generation, compliance checks, publication

### Compliance & Templates
- [compliance-frameworks/](compliance-frameworks/) - ISO 9001, SOC 2, GDPR, HIPAA, Labor Law specifications
- [template-library/](template-library/) - Policies, handbooks, training materials

## Directory Structure

```
.DocSpecSpark/
├── README.md (this file)
├── architecture-decisions.md
├── integration-strategy.md
├── user-personas.md
├── company-constitution-schema.md
├── document-templates-spec.md
├── workflow-commands.md
├── cli-design.md
├── web-app-design.md
├── github-actions-workflows.md
├── compliance-frameworks/
│   ├── iso9001-spec.md
│   ├── soc2-spec.md
│   ├── gdpr-spec.md
│   ├── hipaa-spec.md
│   └── labor-law-spec.md
└── template-library/
    ├── policies/
    ├── handbooks/
    └── training/
```

## Phased Rollout Strategy

DocSpecSpark will launch in **4 phases** over 12 months:

- **Phase 1 (Months 1-3)**: Markdown + Static Site MVP - CLI for managing documents, Docusaurus for viewing, Git for versioning
- **Phase 2 (Months 4-6)**: Compliance Validation & AI Agents - Automated framework checking, AI-assisted document creation
- **Phase 3 (Months 7-9)**: Web Application & Editing UI - Browser-based editor for non-technical users, MS Word export
- **Phase 4 (Months 10-12)**: Enterprise Integration - SharePoint, Teams, advanced Word templates, SSO (NOT part of MVP)

See [phased-rollout-plan.md](phased-rollout-plan.md) for full details.

## Current Status

✅ **Planning Phase: COMPLETE** (11/11 documents)

**Phase 1 MVP: "Spark" Edition** - FOCUS ON THIS
- **Read**: [mvp-quick-start.md](mvp-quick-start.md) for complete Phase 1 overview
- **Template Libraries**: 61 total templates (21 nonprofit + 40 small business manufacturing)
- **Focus**: Markdown documents + Git versioning + Static site viewing
- **Scope**: Minimal CLI, Docusaurus site, GitHub Pages hosting
- **Templates**: 
  - [nonprofit-template-library.md](nonprofit-template-library.md) - 21 nonprofit templates
  - [smallbusiness-template-library.md](smallbusiness-template-library.md) - 40 manufacturing templates
- **Installation**: Single `.DocSpecSpark/` root for framework assets and company documents
- **Timeline**: Months 1-3
- **Target**: 5 pilot companies, 25 documents created

**Phases 2-4**: Future ideas only, not committed development.

### Next Steps (MVP Development)

1. **Create Source Repository**: `github/docspecspark` (framework development)
2. **Build `.DocSpecSpark/` Structure**:
   - `scripts/` (bash + PowerShell)
   - `templates/` (61 templates: nonprofit + manufacturing profiles)
   - `site-theme/` (Docusaurus theme)
   - `prompts/` (AI agent prompts - future)
   - `config.yaml` (company configuration schema)
3. **Build Python CLI** (`docspec_cli`):
   - `install` - Install framework into target repo
   - `create` - Create document from template
   - `publish` - Tag version and deploy site
   - `update` - Update framework from source
   - `list` - List all documents
4. **Create 61 Templates**:
   - 21 nonprofit templates (governance, HR, finance/tax - aligned to IRS Form 990)
   - 40 small business manufacturing templates (OSHA, EPA, QMS, engineering, export, IT security)
5. **Create Example Repository**: Demo company (`acme-corp-docs`) with sample documents
6. **Recruit Pilot Companies**: 5 organizations for beta testing

## Company Profiles

DocSpecSpark supports **7 company profiles** with pre-configured templates, compliance frameworks, and workflows:

1. **Not-for-Profit** (with volunteers and staff)
2. **Early-Stage Startup** (< 10 people)
3. **Small Business - Service Industry** (10-50 employees)
4. **Small Business - Manufacturing** (50-250 employees)
5. **Mid-Sized Enterprise** (250-1000 employees)
6. **Large Enterprise** (1000+ employees)
7. **Healthcare Organization** (regulated)

See [company-profiles.md](company-profiles.md) for detailed specifications.

## Status

**Phase**: Planning & Architecture (Complete)
**Last Updated**: March 2, 2026
**Next Steps**: 
1. ✅ Multi-interface architecture defined
2. ✅ Company constitution schema created
3. ✅ SharePoint/Teams integration strategy designed
4. ✅ Template library specifications built
5. ✅ Company profiles configured
6. ✅ Phased rollout plan finalized
7. **→ Begin Phase 1 development (Core MVP)**
