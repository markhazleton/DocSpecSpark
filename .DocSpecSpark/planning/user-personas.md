# User Personas & Interaction Flows - DocSpecSpark

## Overview

DocSpecSpark serves diverse user personas across technical and non-technical backgrounds. This document defines each persona, their preferred interfaces, and typical workflows.

---

## User Personas

### Persona 1: Technical Power User (IT/DevOps)

**Profile**:
- **Role**: IT Administrator, DevOps Engineer, Technical Writer
- **Technical Level**: Expert (comfortable with CLI, Git, YAML)
- **Primary Goals**: Automate document generation, integrate with CI/CD, maintain infrastructure
- **Preferred Interface**: CLI + AI Agents

**Characteristics**:
- Uses VS Code or terminal daily
- Understands version control concepts
- Wants automation and scriptability
- Comfortable editing YAML configuration files

**Typical Workflow**:
```bash
# Initialize new company repository
docspec init --client "Acme Corp"

# Configure constitution via YAML editing
code .DocSpecSpark/constitution.yaml

# Create new policy document via CLI + AI agent
docspec create policy "Data Privacy Policy" --frameworks gdpr,soc2

# Or use AI agent commands directly in VS Code
/docspec Data Privacy Policy
/plan  # Generates outline
/tasks # Breaks into tasks
/draft # Creates document
/compliance-review --frameworks gdpr,soc2
/publish --version 1.0 --approver "jane.smith@acme.com"

# Automate publishing via CI/CD
git tag v1.0
git push --tags  # Triggers GitHub Action to publish to SharePoint
```

**Pain Points**:
- Business users asking for document status (needs dashboard)
- Manual approval collection (wants automated workflow)
- SharePoint sync latency

---

### Persona 2: Legal/Compliance Officer

**Profile**:
- **Role**: Legal Counsel, Compliance Officer, Risk Manager
- **Technical Level**: Intermediate (comfortable with web apps, not CLI)
- **Primary Goals**: Ensure legal accuracy, validate compliance, approve documents
- **Preferred Interface**: Web Application

**Characteristics**:
- Reviews 5-10 documents per week
- Needs to see compliance violations clearly
- Wants to approve/reject with comments
- Must access from any device (laptop, tablet)

**Typical Workflow**:

**Via Web App**:
1. **Receives notification**: "Data Privacy Policy ready for review" (email or Teams)
2. **Opens web dashboard**: https://docspec.acme.com/reviews
3. **Views compliance report**:
   ```
   Document: Data Privacy Policy
   Status: Pending Legal Review
   
   Compliance Score: 92% ✅
   ✓ GDPR: 47/48 requirements met
   ✗ SOC2: 1 CRITICAL violation
   
   Critical Issues (1):
   • Missing data breach notification timeline (GDPR Art. 33)
     Location: Section 4.2
     Recommendation: Add "within 72 hours" clause
   
   High Priority (2):
   • Ambiguous "reasonable security" definition (SOC2 CC6.1)
   • Missing DPO contact information (GDPR Art. 37)
   ```
4. **Adds review comments**: 
   - "Need explicit 72-hour breach notification"
   - "Define 'reasonable security' with technical controls"
5. **Requests revision**: Clicks "Request Changes" → Notifies author via Teams
6. **Re-reviews after edits**: Receives notification when updated
7. **Approves document**: Adds digital signature, clicks "Approve for Publication"

**Pain Points**:
- Can't edit documents directly in web app (must go back to author)
- No mobile app (only responsive web)
- Difficult to compare versions side-by-side

---

### Persona 3: HR Professional

**Profile**:
- **Role**: HR Manager, HR Generalist, People Operations
- **Technical Level**: Beginner (uses Word, Excel, SharePoint daily)
- **Primary Goals**: Create employee handbooks, update policies, ensure consistency
- **Preferred Interface**: SharePoint + Teams (familiar tools)

**Characteristics**:
- Creates 2-3 new documents per month
- Updates existing handbooks quarterly
- Not familiar with Git or Markdown
- Wants WYSIWYG editing experience

**Typical Workflow**:

**Via Teams Bot**:
1. **Start in Teams**: Types `/docspec create Employee Handbook - Remote Work`
2. **Bot guides through wizard**:
   ```
   Teams Bot: I'll help you create a Remote Work Policy. Let me ask a few questions:
   
   1. Who is the audience for this policy?
      ○ All employees
      ○ Remote employees only
      ○ Managers only
   
   2. Which compliance frameworks apply?
      ☑ Labor Law
      ☐ GDPR
      ☐ HIPAA
   
   3. Select a template to start from:
      ○ Remote Work Policy (Standard)
      ○ Hybrid Work Policy
      ○ Custom (blank)
   
   [Next]
   ```
3. **Bot creates draft**: Generates initial document from template
4. **HR edits in SharePoint**: 
   - Bot posts link: "Draft created: [Edit in SharePoint](https://...)"
   - Opens Word Online, edits using familiar interface
   - Track changes enabled automatically
5. **Requests review**: Clicks "Ready for Review" in SharePoint
   - Triggers DocSpecSpark workflow
   - Converts Word → Markdown (background)
   - Runs compliance check
   - Notifies legal team via Teams
6. **Receives feedback**: Legal adds comments in Word
7. **Makes revisions**: Updates directly in SharePoint
8. **Final approval**: Once legal approves, clicks "Publish"
   - Word doc becomes "Version 1.0" in SharePoint
   - Markdown version tagged in Git
   - Announcement posted to company Teams channel

**Pain Points**:
- Doesn't understand Markdown syntax errors
- Confused about why changes must go through Git
- Wants instant preview of compliance score

---

### Persona 4: Executive Approver

**Profile**:
- **Role**: CEO, CFO, Chief Compliance Officer
- **Technical Level**: Beginner (relies on assistants for tech)
- **Primary Goals**: Final approval, risk oversight, minimal time investment
- **Preferred Interface**: Email/Teams (mobile-friendly)

**Characteristics**:
- Approves 1-2 high-level documents per month
- Needs executive summary, not technical details
- Often reviewing on mobile device
- Delegates detailed review to legal/compliance

**Typical Workflow**:

**Via Email/Teams (Mobile)**:
1. **Receives notification**: 
   ```
   Subject: [Action Required] Approve Data Privacy Policy v1.0
   
   From: DocSpecSpark <no-reply@docspec.acme.com>
   
   Hi Jane,
   
   The Data Privacy Policy is ready for your final approval.
   
   Summary:
   • Compliance: ✅ All frameworks met (GDPR, SOC2)
   • Legal Review: ✅ Approved by Sarah Chen (Legal)
   • HR Review: ✅ Approved by Tom Rodriguez (HR)
   • Business Impact: Updates data retention from 5 years to 7 years
   
   [View Document] [Approve] [Request Changes]
   ```
2. **Opens on mobile**: Clicks "View Document"
   - Mobile-optimized summary page
   - Key changes highlighted
   - Compliance checklist visible
3. **Approves or delegates**:
   - **Option A**: Clicks "Approve" → Adds signature → Document published
   - **Option B**: Clicks "Forward to Sarah Chen for second opinion"
4. **Receives confirmation**: "Data Privacy Policy v1.0 published and available in SharePoint"

**Pain Points**:
- Too many approval requests (wants bulk approve)
- Unclear business impact of policy changes
- Can't delegate approval authority easily

---

### Persona 5: Employee (Document Consumer)

**Profile**:
- **Role**: Any employee, contractor, or external stakeholder
- **Technical Level**: Varies (no technical assumptions)
- **Primary Goals**: Read policies, find relevant information, stay compliant
- **Preferred Interface**: SharePoint/Teams (company intranet)

**Characteristics**:
- Accesses documents occasionally (when onboarding, or as-needed)
- Needs search functionality
- Wants mobile access
- May not know exact document name

**Typical Workflow**:

**Via SharePoint Search**:
1. **Needs information**: "What's our remote work policy?"
2. **Searches in SharePoint**: Types "remote work" in search bar
3. **Finds document**: "Remote Work Policy v2.1 (Effective March 2026)"
4. **Opens in Word Online** (read-only):
   - Version 2.1 (latest)
   - Link to previous versions
   - "Published: Feb 28, 2026 | Approved by: Jane Smith"
5. **Downloads PDF** (optional): For offline reference
6. **Bookmarks for later**: Adds to "My Policies" folder

**Via Teams Channel**:
1. **Receives announcement**: "New Remote Work Policy published" (posted by bot)
2. **Clicks link**: Opens document directly in Teams
3. **Asks question**: "@DocSpecSpark Bot what are the home office reimbursements?"
4. **Bot answers**: Extracts relevant section and cites policy

**Pain Points**:
- Hard to find correct version (old vs. new)
- Doesn't know when policies are updated
- Can't easily compare "what changed" between versions

---

## Interface Comparison Matrix

| Feature | CLI + Agents | Web App | SharePoint/Teams |
|---------|--------------|---------|------------------|
| **Document Creation** | Expert (full control) | Guided wizard | Template selection |
| **Editing** | Markdown in IDE | Markdown with preview | WYSIWYG Word editor |
| **Compliance Check** | Command-line output | Visual dashboard | Auto-run (background) |
| **Approval** | Git tags + metadata | Click-to-approve | SharePoint workflow |
| **Version Control** | Full Git history | Simplified timeline | SharePoint versions |
| **Collaboration** | PR reviews | Comments panel | Word track changes |
| **Mobile Access** | Command-line (limited) | Responsive web | Teams app (native) |
| **Offline Support** | Full (local Git) | None | SharePoint sync |
| **Learning Curve** | High (Git, Markdown) | Medium (web UI) | Low (familiar tools) |

---

## Interaction Flow Diagrams

### Flow 1: Creating a New Policy (Legal Professional)

```
┌──────────────────────────────────────────────────────────────┐
│ Legal Officer: "We need a new data retention policy"         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Opens DocSpec Web App        │
         │  → New Document Wizard        │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Fills out form:              │
         │  • Name: Data Retention       │
         │  • Type: Policy               │
         │  • Frameworks: GDPR, SOC2     │
         │  • Template: Data Retention   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  System generates:            │
         │  • Git branch                 │
         │  • spec.md (from template)    │
         │  • outline.md (suggested)     │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  User fills outline sections  │
         │  (web form interface)         │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Clicks "Generate Draft"      │
         │  → AI agent creates draft.md  │
         │     with compliance citations │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Reviews compliance report:   │
         │  ✓ GDPR: 23/24                │
         │  ✗ SOC2: 1 violation          │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Edits draft to fix issues    │
         │  → Re-runs compliance check   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Clicks "Request Approval"    │
         │  → Notifies approvers (CEO)   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  CEO approves via email link  │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  System publishes:            │
         │  • Git tag v1.0               │
         │  • Word export to SharePoint  │
         │  • Teams announcement         │
         └───────────────────────────────┘
```

### Flow 2: Updating Existing Handbook (HR Professional)

```
┌──────────────────────────────────────────────────────────────┐
│ HR Manager: "Need to update parental leave from 8 to 12 wks" │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Opens SharePoint             │
         │  → "Employee Handbook v3.2"   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Clicks "Edit" button         │
         │  → Opens Word Online          │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Edits Section 5.3:           │
         │  "8 weeks" → "12 weeks"       │
         │  Track changes enabled        │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Clicks "Ready for Review"    │
         │  (custom SharePoint button)   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  System (background):         │
         │  • Word → Markdown            │
         │  • Creates Git PR             │
         │  • Runs compliance check      │
         │  • Notifies legal via Teams   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Legal reviews in web app     │
         │  • Sees changes highlighted   │
         │  • Compliance: ✓ All pass     │
         │  • Clicks "Approve"           │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  HR receives Teams message:   │
         │  "Legal approved. Publish?"   │
         │  Clicks "Yes"                 │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  System publishes:            │
         │  • SharePoint: v3.3 (new)     │
         │  • Git: merged to main, tag   │
         │  • Teams: Announces change    │
         │  • Emails all employees       │
         └───────────────────────────────┘
```

### Flow 3: Compliance Audit (Compliance Officer)

```
┌──────────────────────────────────────────────────────────────┐
│ Auditor: "Show all GDPR-related policies and review status"  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Opens DocSpec Web App        │
         │  → Compliance Dashboard       │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Filters by:                  │
         │  • Framework: GDPR            │
         │  • Status: All                │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────────────────────────┐
         │  Results Table:                                   │
         │  ┌──────────────────┬──────────┬────────────────┐ │
         │  │ Document         │ Status   │ GDPR Score     │ │
         │  ├──────────────────┼──────────┼────────────────┤ │
         │  │ Data Privacy     │ Current  │ ✓ 48/48 (100%) │ │
         │  │ Data Retention   │ Current  │ ✓ 24/24 (100%) │ │
         │  │ Employee Handbook│ EXPIRED  │ ✓ 36/36 (100%) │ │
         │  │ Cookie Policy    │ Draft    │ ✗ 12/15 (80%)  │ │
         │  └──────────────────┴──────────┴────────────────┘ │
         └───────────┬───────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Clicks "Export Audit Report" │
         │  → Generates PDF with:        │
         │    • All policy summaries     │
         │    • Compliance scores        │
         │    • Approval histories       │
         │    • Version timelines        │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Downloads PDF for auditor    │
         │  + Links to SharePoint docs   │
         └───────────────────────────────┘
```

---

## Accessibility Considerations

### For Non-Technical Users
1. **Guided Wizards**: Step-by-step forms with inline help
2. **Visual Compliance**: Traffic light indicators (🟢🟡🔴)
3. **Plain Language**: Avoid Git terminology (use "version" not "commit")
4. **Undo Support**: Easy rollback without Git knowledge

### For Mobile Users
1. **Responsive Design**: Web app works on tablets/phones
2. **Approval-Only Mode**: Executives can approve without editing
3. **Teams Integration**: Native mobile Teams app support
4. **Offline Reading**: SharePoint sync for offline access

### For Screen Reader Users
1. **ARIA Labels**: All buttons/forms accessible
2. **Keyboard Navigation**: Tab-through workflows
3. **Text Alternatives**: Compliance charts have text summaries
4. **High Contrast**: Supports Windows/Mac high contrast modes

---

## Training Paths by Persona

| Persona | Training Duration | Key Topics |
|---------|------------------|------------|
| **Technical Power User** | 2 hours | CLI commands, YAML editing, GitHub Actions, agent customization |
| **Legal/Compliance** | 1 hour | Web app navigation, compliance dashboard, approval workflow |
| **HR Professional** | 30 minutes | Teams bot, SharePoint editing, template selection |
| **Executive Approver** | 15 minutes | Email/Teams approval, delegation, mobile app |
| **Employee (Consumer)** | None | Just-in-time (search/browse) |

---

**Status**: Draft for review
**Next Steps**:
1. Create web app wireframes based on these flows
2. Design Teams bot conversation scripts
3. Build SharePoint custom actions (Edit → Review → Publish)
4. Create training videos for each persona
