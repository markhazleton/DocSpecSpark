# Architecture Decisions - DocSpecSpark

## Executive Summary

DocSpecSpark follows a **phased architecture approach** starting with a minimal "Spark" MVP:

**Phase 1 (MVP)**: Markdown + Git + Static Site (Docusaurus)
- Local CLI for document management
- Git for version control
- Static site for viewing (no authentication)
- GitHub Pages for free hosting

**Post-MVP Evolution**:
- **Phase 2**: Add compliance validation engine and AI agent integration
- **Phase 3**: Add web-based editor (GitHub API integration)
- **Phase 4**: Add SharePoint/Teams integration for enterprise

This document details the architectural decisions for all phases, but **only Phase 1 is MVP**.

---

## Decision 1: MVP Scope - "Spark" Minimalism

**Decision**: Phase 1 MVP is Markdown + Git + Static Site ONLY. No web app, no SharePoint, no complex workflows.

### Context
User requested: "MVP is just managing markdown published documents, with simple static site for viewing the documents and a robust versioning approach using GIT"

This aligns with the "Spark" philosophy from Spec Kit: minimal, fast, Git-native.

### Chosen Approach: Minimal CLI + Static Site

**Phase 1 MVP Components**:
1. **CLI**: Python tool with 5 commands (`init`, `create`, `publish`, `list`, `serve`)
2. **Storage**: Git repository (GitHub, GitLab, or self-hosted)
3. **Static Site**: Docusaurus (React-based, Markdown-native)
4. **Versioning**: Git tags (`v1.0`, `v1.1`, `v2.0`)
5. **Hosting**: GitHub Pages (free) or Netlify/Vercel
6. **Templates**: 20 Markdown templates (policies, handbooks, training)
7. **Configuration**: Simple YAML config file (company metadata, branding)

**What's NOT in MVP**:
- ❌ Compliance validation engine (manual review only in Phase 1)
- ❌ AI agent integration (added in Phase 2)
- ❌ Web-based editing (added in Phase 3)
- ❌ MS Word export (added in Phase 3)
- ❌ SharePoint/Teams integration (added in Phase 4)
- ❌ Approval workflows (use Git PR review instead)

### Advantages
- **Fast to build**: 1-3 months vs. 6-12 months for full platform
- **Low barrier to entry**: Just Git + Node.js (no complex dependencies)
- **Familiar tools**: Developers already know Git, Markdown, static sites
- **Free hosting**: GitHub Pages costs $0
- **Robust versioning**: Git is industry-standard version control
- **Easy to extend**: Each phase adds capabilities without rewriting core

### Tradeoffs
- Non-technical users must wait for Phase 3 web app
- No automated compliance checking in Phase 1 (added Phase 2)
- No Word export initially (Markdown only until Phase 3)
- Requires Git knowledge for power users (web app alleviates this in Phase 3)

### Implementation
```bash
# Phase 1 user workflow
$ docspec init --client "Acme Corp" --profile startup
$ docspec create policy "Data Privacy Policy"
$ code documents/policies/data-privacy-policy.md  # Edit in any text editor
$ docspec publish --version 1.0  # Git tag + GitHub Pages deploy
$ docspec serve  # Preview at localhost:3000
```

**Technology Stack**:
- CLI: Python (Typer framework)
- Static Site: Docusaurus 3.x
- CI/CD: GitHub Actions
- Hosting: GitHub Pages

---

## Decision 2: Multi-Interface Architecture (Post-MVP)

**Decision**: Support 3 interfaces (CLI, Web App, SharePoint/Teams) with Git as single source of truth.

**NOTE**: This is the LONG-TERM vision (Phases 2-4). Phase 1 MVP is CLI + Static Site only.

### Context (Post-MVP)

Business documentation requires accessibility across diverse user personas:
- **Legal/Compliance Officers**: Need compliance validation but may not use command-line tools
- **HR Professionals**: Need to create employee handbooks without technical knowledge
- **Executives**: Need to approve documents without learning Git workflows
- **IT/Developers**: Comfortable with CLI, Git, and automation scripts

### Post-MVP Architecture (Phases 2-4)

Implement **three parallel interface layers**, all backed by the same GitHub repository:

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
├──────────────────┬──────────────────┬─────────────────────────┤
│   CLI + Agents   │   Web App        │  SharePoint/Teams       │
│  (Phase 1-2)     │   (Phase 3)      │     (Phase 4)           │
│  (Tech Users)    │ (Business Users) │  (Enterprise Users)     │
└────────┬─────────┴────────┬─────────┴───────────┬────────────┘
         │                  │                     │
         └──────────────────┼─────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  GitHub API    │
                    │  + Actions     │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Git Repository│
                    │  (Source of    │
                    │   Truth)       │
                    └────────────────┘
```

### Rationale

- **Unified source of truth**: All interfaces read/write to the same Git repository
- **Gradual adoption**: Companies can start with CLI, add web app later
- **Separation of concerns**: Technical workflows (CLI) vs. business workflows (web/SharePoint)
- **Compliance enforcement**: GitHub Actions validate all changes regardless of entry point

---

## Decision 3: GitHub API as Integration Layer (Phase 3)

### Context

Non-technical users cannot interact directly with Git commands, AI agents, or command-line tools.

### Decision

Build a **web application using GitHub API** that provides:
- Document creation wizard (replaces `/docspec` command)
- Visual outline builder (replaces `/plan` command)
- Task assignment interface (replaces `/tasks` command)
- WYSIWYG draft editor with Markdown preview (replaces `/draft` command)
- Compliance dashboard showing framework violations (replaces `/compliance-review` command)
- One-click publish with approval signature (replaces `/publish` command)

### Implementation Pattern

```javascript
// Example: Create new document via GitHub API
POST /repos/{owner}/{repo}/contents/.DocSpecSpark/specs/{doc-name}/spec.md
{
  "message": "Create spec for Data Privacy Policy",
  "content": base64(markdown_content),
  "branch": "doc/001-data-privacy-policy"
}

// Trigger GitHub Action for compliance check
POST /repos/{owner}/{repo}/actions/workflows/compliance-check.yml/dispatches
{
  "ref": "doc/001-data-privacy-policy",
  "inputs": {
    "document_path": ".DocSpecSpark/specs/001-data-privacy-policy/draft.md",
    "frameworks": "gdpr,soc2"
  }
}
```

### Technology Stack Options

| Component | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| **Frontend** | React + TypeScript | Next.js (SSR) | Vue.js |
| **Backend** | Node.js + Express | Serverless (Vercel/Netlify) | Python FastAPI |
| **Auth** | GitHub OAuth | Auth0 | Okta |
| **Database** | None (Git as DB) | PostgreSQL (cache) | MongoDB (metadata) |
| **Hosting** | Vercel | AWS Amplify | Azure Static Web Apps |

**Recommendation**: **Next.js on Vercel** with GitHub OAuth and Git as database (no separate DB needed initially).

---

## Decision 3: SharePoint/Teams Integration Strategy

### Context

Many enterprises already use Microsoft 365 for document management. SharePoint has robust versioning, approval workflows, and document co-authoring that users already understand.

### Decision

Implement **hybrid storage model**:

1. **Git Repository**: Source of truth for Markdown, compliance metadata, templates
2. **SharePoint Document Library**: Published document storage (Word/PDF exports)
3. **GitHub Actions**: Automated sync between Git and SharePoint

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  User creates document via Web App or CLI                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Git Repository       │
         │  - draft.md (source)  │
         │  - compliance.json    │
         └───────┬───────────────┘
                 │
                 │ (on publish command)
                 ▼
         ┌──────────────────────┐
         │  GitHub Action       │
         │  1. Run compliance   │
         │  2. Convert to DOCX  │
         │  3. Upload to SP     │
         └───────┬──────────────┘
                 │
                 ▼
         ┌──────────────────────┐
         │  SharePoint Library  │
         │  - Policy_v1.0.docx  │
         │  - Version history   │
         │  - Approval metadata │
         └──────────────────────┘
```

### SharePoint Integration Implementation

**Using Microsoft Graph API**:

```javascript
// Upload document to SharePoint
POST https://graph.microsoft.com/v1.0/sites/{site-id}/drives/{drive-id}/items/{parent-id}/children
{
  "name": "Data_Privacy_Policy_v1.0.docx",
  "file": {
    "@microsoft.graph.conflictBehavior": "rename"
  },
  "@microsoft.graph.sourceUrl": "https://github.com/.../draft.md"
}

// Set SharePoint metadata
PATCH https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items/{item-id}/fields
{
  "ComplianceFrameworks": "GDPR; SOC2",
  "DocumentType": "Policy",
  "ApprovalStatus": "Pending",
  "Version": "1.0"
}
```

### Teams Integration

**Teams Bot Commands**:
- `/docspec create [document-name]` - Initiates document creation workflow
- `/docspec status [doc-id]` - Shows document status and pending tasks
- `/docspec approve [doc-id]` - Approves document for publication
- `/docspec review [doc-id]` - Opens compliance review dashboard

**Adaptive Cards for Notifications**:
```json
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "TextBlock",
      "text": "Data Privacy Policy ready for review",
      "weight": "Bolder"
    },
    {
      "type": "FactSet",
      "facts": [
        {"title": "Compliance", "value": "✅ GDPR, ✅ SOC2"},
        {"title": "Readability", "value": "Grade 11 (target: 12)"},
        {"title": "Status", "value": "Awaiting Legal Approval"}
      ]
    }
  ],
  "actions": [
    {"type": "Action.OpenUrl", "title": "Review Document", "url": "..."},
    {"type": "Action.Submit", "title": "Approve", "data": {"action": "approve"}}
  ]
}
```

---

## Decision 4: MS Word Export with Version Tracking

### Context

Many business users expect Word documents (.docx) as the final deliverable. SharePoint's built-in Word versioning is familiar to enterprise users.

### Decision

Implement **dual-format strategy**:

1. **Markdown as source**: Git tracks all changes, enables diff, powers AI agents
2. **Word as distribution**: Pandoc converts Markdown → DOCX with styles, SharePoint stores versions

### Conversion Pipeline

**Using Pandoc + Custom Templates**:

```bash
# Convert Markdown to Word with custom reference doc
pandoc draft.md \
  --from markdown \
  --to docx \
  --reference-doc=templates/company-template.docx \
  --metadata title="Data Privacy Policy" \
  --metadata version="1.0" \
  --metadata date="2026-03-02" \
  --output Data_Privacy_Policy_v1.0.docx
```

**Custom Word Template Features**:
- Company logo in header
- Consistent heading styles (Heading 1, Heading 2, etc.)
- Document properties (title, author, version, compliance frameworks)
- Footnote styles for compliance citations
- Table of contents auto-generation

### Version Tracking Strategy

| Aspect | Git (Markdown) | SharePoint (Word) |
|--------|----------------|-------------------|
| **Version ID** | Semantic (v1.0, v1.1, v2.0) | Sequential (V1, V2, V3) |
| **Change Tracking** | Git diff (line-by-line) | Word Track Changes |
| **History** | Full commit log | SharePoint version history |
| **Rollback** | `git revert` | SharePoint "Restore" |
| **Approval** | Git tag + metadata | SharePoint approval workflow |

**Sync Mechanism**:
- Git tag `v1.0` → SharePoint major version `V1`
- Git commit → SharePoint minor version `V1.1`, `V1.2`, etc.
- SharePoint "Published" status → Git tag + GitHub Release

---

## Decision 5: Authentication & Authorization

### Context

Multiple user interfaces require unified identity management and permission controls.

### Decision

Implement **GitHub-based authentication** with role-based access:

```yaml
# .DocSpecSpark/permissions.yaml
roles:
  admin:
    description: "Full access to all features"
    permissions: ["create", "edit", "publish", "approve", "configure"]
    github_team: "company-admins"
  
  author:
    description: "Create and edit documents"
    permissions: ["create", "edit", "request_review"]
    github_team: "document-authors"
  
  reviewer:
    description: "Review and approve documents"
    permissions: ["review", "approve", "reject"]
    github_team: "legal-compliance"
  
  reader:
    description: "Read-only access"
    permissions: ["read"]
    github_team: "all-employees"
```

**Implementation**:
- Web App: GitHub OAuth → check team membership → grant permissions
- CLI: GitHub PAT (Personal Access Token) → same team check
- SharePoint: Sync GitHub teams → SharePoint groups (via Graph API)

---

## Decision 6: Offline Support & Conflict Resolution

### Context

Non-technical users may edit Word documents offline in SharePoint, creating potential conflicts with Git-based workflows.

### Decision

Implement **unidirectional sync** for published documents:

**Rule**: 
- **Before Publication**: Git is source of truth (all edits via web app or CLI)
- **After Publication**: SharePoint is source of truth for published Word docs
- **Re-editing Published Docs**: Creates new draft in Git with "Edit Published Document" workflow

**Conflict Prevention**:
```
Published Document Workflow:
1. User clicks "Edit" in SharePoint
2. System checks if document is being edited in Git
3. If yes → Show warning, lock SharePoint file
4. If no → Create new Git branch, lock SharePoint until re-published
```

---

## Decision 7: Compliance Framework Storage

### Context

The user noted that the constitution must include company metadata. Compliance frameworks must be per-company configurable.

### Decision

Store company constitution as **enhanced YAML + Markdown hybrid**:

**File**: `.DocSpecSpark/constitution.yaml`

```yaml
company:
  name: "Acme Corporation"
  industry: "Healthcare Technology"
  jurisdiction: "United States (California)"
  employee_count: 250
  founded: 2015
  
compliance:
  active_frameworks:
    - id: "gdpr"
      version: "2018"
      applicability: "Processes EU citizen data"
      contact: "dpo@acme.com"
    
    - id: "hipaa"
      version: "2013 Omnibus Rule"
      applicability: "Healthcare data processing"
      contact: "compliance@acme.com"
    
    - id: "soc2"
      type: "Type II"
      audit_date: "2025-12-15"
      auditor: "BigFour Audit LLP"
  
  custom_policies:
    - name: "AI Ethics Policy"
      file: ".DocSpecSpark/compliance/custom/ai-ethics.md"
      mandatory: true

document_governance:
  approval_workflows:
    policy:
      reviewers: ["legal", "compliance"]
      approvers: ["ceo", "legal-director"]
      review_cycle: "annual"
    
    handbook:
      reviewers: ["hr", "legal"]
      approvers: ["hr-director"]
      review_cycle: "biannual"
  
  version_strategy: "semantic"  # semantic | date-based | sequential
  retention_policy: "perpetual"  # All versions kept in Git
  
branding:
  logo: ".DocSpecSpark/assets/logo.png"
  primary_color: "#003366"
  font_family: "Calibri"
  word_template: ".DocSpecSpark/templates/acme-template.docx"
```

**Plus**: Separate Markdown files in `.compliance/frameworks/` for detailed requirements (same as planned).

---

## Summary of Architectural Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **User Interfaces** | CLI + Web App + SharePoint/Teams | Serve technical and non-technical users |
| **API Layer** | GitHub API + GitHub Actions | No separate backend infrastructure needed |
| **Source of Truth** | Git Repository (Markdown) | Version control, compliance validation, AI agents |
| **Distribution Format** | MS Word (via Pandoc) | Business user expectations, SharePoint integration |
| **Document Storage** | Hybrid (Git + SharePoint) | Git for drafts/compliance, SharePoint for published |
| **Authentication** | GitHub OAuth + Teams | Unified identity, team-based permissions |
| **Compliance Frameworks** | YAML config + Markdown principles | Per-company customization, machine-readable |
| **Version Tracking** | Semantic versioning in Git → SharePoint versions | Bidirectional sync with clear source of truth |
| **Offline Editing** | Unidirectional after publish | Prevent conflicts, maintain Git authority |

---

## Open Questions

1. **Should web app be open-source or commercial?** (Impacts monetization strategy)
2. **Should we support Google Workspace (Docs) in addition to MS Word?** (Cross-platform compatibility)
3. **Should compliance checks run on every commit or only on PR?** (Performance vs. rigor trade-off)
4. **Should SharePoint sync be real-time or scheduled?** (API rate limits, cost)
5. **Should we support document templates in Word format or only Markdown?** (Authoring complexity)

---

**Status**: Draft for review
**Next Steps**: 
1. Validate architecture with stakeholders
2. Create company constitution schema (detailed)
3. Design web app wireframes
4. Prototype SharePoint integration
