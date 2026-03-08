# Non-Profit Template Library - DocSpecSpark

## Purpose

This document defines the **nonprofit-specific template library** for DocSpecSpark, derived from the comprehensive analysis in [KeyDocuments-NotForProfits.md](KeyDocuments-NotForProfits.md).

**Design Principle**: Templates are Markdown files with YAML frontmatter, providing a structured starting point that organizations customize for their specific needs.

---

## Template Organization

Templates are stored in `.DocSpecSpark/templates/` and organized by category:

```
.DocSpecSpark/templates/
├── governance/           # Board and organizational governance
├── policies/             # Operational and compliance policies
├── hr-employee/          # Employee management
├── hr-volunteer/         # Volunteer management
├── finance-tax/          # Financial and tax compliance
└── program-operations/   # Program-specific (youth, etc.)
```

---

## Phase 1 MVP Template Set (Non-Profit Profile)

Based on KeyDocuments-NotForProfits.md, the **Essential** tier documents become Phase 1 templates:

### Governance Templates (7 templates)

#### 1. **Bylaws Template**
- **File**: `governance/bylaws.md`
- **Priority**: Essential
- **Purpose**: Internal governance "operating system" (board structure, officers, meetings, voting)
- **Sections**:
  - Organization name and mission statement
  - Board composition (size, terms, diversity)
  - Officer roles and responsibilities
  - Quorum and voting procedures
  - Committee structure (standing and ad-hoc)
  - Meeting requirements (frequency, notice, remote participation)
  - Amendment process
  - Conflict of interest provisions
  - Indemnification
- **Regulatory Context**: State nonprofit corporation law; IRS organizational test
- **Review Cycle**: Annual review, formal amendment as needed
- **Placeholders**: `{{ORG_NAME}}`, `{{STATE}}`, `{{BOARD_SIZE}}`, `{{FISCAL_YEAR_END}}`

#### 2. **Board Policy Manual Template**
- **File**: `governance/board-policy-manual.md`
- **Priority**: Essential
- **Purpose**: Consolidates board-adopted policies; clarifies board vs. staff authorities
- **Sections**:
  - Policy framework and authority hierarchy
  - Policy list with owners and approval dates
  - Review cadence and update process
  - Cross-references to operational procedures
  - List of currently adopted policies
- **Regulatory Context**: Form 990 Part VI governance questions
- **Review Cycle**: Annual
- **Placeholders**: `{{ORG_NAME}}`, `{{POLICY_OFFICER}}`, `{{REVIEW_DATE}}`

#### 3. **Board Member Job Description Template**
- **File**: `governance/board-member-job-description.md`
- **Priority**: Important (Essential for recruitment)
- **Purpose**: Sets expectations, supports recruitment, improves fiduciary performance
- **Sections**:
  - Fiduciary duties (duty of care, loyalty, obedience)
  - Time commitment (meetings, committees, events)
  - Fundraising expectations
  - Committee service requirements
  - Confidentiality obligations
  - Conflict of interest disclosure
  - Term length and renewal
- **Review Cycle**: Every 1-2 years
- **Placeholders**: `{{ORG_NAME}}`, `{{MEETING_FREQUENCY}}`, `{{FUNDRAISING_EXPECTATION}}`

#### 4. **Board Meeting Minutes Template**
- **File**: `governance/board-meeting-minutes.md`
- **Priority**: Essential
- **Purpose**: Legal record of governance actions, decisions, and approvals
- **Sections**:
  - Meeting metadata (date, time, location, attendees)
  - Approval of previous minutes
  - Executive Director report
  - Committee reports
  - Financial reports
  - Action items and resolutions (with vote tallies)
  - Executive session notes (if applicable)
  - Next meeting date
- **Regulatory Context**: State corporate law; Form 990 Part VI; audit trail
- **Review Cycle**: Approved at next meeting
- **Placeholders**: `{{MEETING_DATE}}`, `{{ATTENDEES}}`, `{{RESOLUTIONS}}`

#### 5. **Conflict of Interest Policy Template**
- **File**: `governance/conflict-of-interest-policy.md`
- **Priority**: Essential
- **Purpose**: Defines conflicts, requires disclosure, establishes management procedures
- **Sections**:
  - Definitions (financial interest, potential conflict)
  - Duty to disclose
  - Disclosure procedures (timing, form)
  - Determination of conflict (who decides)
  - Conflict management (recusal, documentation)
  - Annual disclosure requirement
  - Violations and remedies
  - Records of conflicts
- **Regulatory Context**: Form 1023 and Form 990 Part VI; private inurement prevention
- **Review Cycle**: Annual
- **Includes**: Annual disclosure questionnaire template
- **Placeholders**: `{{ORG_NAME}}`, `{{DISCLOSURE_OFFICER}}`, `{{FISCAL_YEAR}}`

#### 6. **Whistleblower Policy Template**
- **File**: `governance/whistleblower-policy.md`
- **Priority**: Essential
- **Purpose**: Reporting channels and anti-retaliation protections for illegal/unethical conduct
- **Sections**:
  - Scope (who is covered, what to report)
  - Reporting options (including outside chain of command)
  - Confidentiality protections
  - Investigation process
  - Non-retaliation commitment
  - Documentation requirements
  - Corrective actions
  - Reporting to board/audit committee
- **Regulatory Context**: Form 990 Part VI; federal anti-retaliation law; Sarbanes-Oxley context
- **Review Cycle**: Annual or after any report
- **Placeholders**: `{{ORG_NAME}}`, `{{REPORTING_HOTLINE}}`, `{{AUDIT_COMMITTEE_CHAIR}}`

#### 7. **Document Retention and Destruction Policy Template**
- **File**: `governance/document-retention-policy.md`
- **Priority**: Essential
- **Purpose**: Defines retention periods and destruction controls
- **Sections**:
  - Record categories (governance, financial, HR, program, legal)
  - Retention schedule (by category)
  - Legal hold procedures
  - Destruction process and authorization
  - Electronic records and backups
  - Responsibility matrix (records custodian)
  - Audit trail
- **Regulatory Context**: Form 990 Part VI; IRS recordkeeping; obstruction statutes
- **Review Cycle**: Annual
- **Includes**: Retention schedule spreadsheet template
- **Placeholders**: `{{ORG_NAME}}`, `{{RECORDS_CUSTODIAN}}`, `{{LEGAL_HOLD_AUTHORITY}}`

### Policy Templates (3 templates)

#### 8. **Gift Acceptance Policy Template**
- **File**: `policies/gift-acceptance-policy.md`
- **Priority**: Important
- **Purpose**: Defines what gifts are accepted, approval process, and restrictions
- **Sections**:
  - Gift acceptance authority
  - Acceptable gift types (cash, stocks, property, planned gifts)
  - Restricted vs. unrestricted gifts
  - Due diligence for non-cash gifts
  - Donor recognition and anonymity
  - Gift refusal criteria
  - IRS compliance (substantiation, quid pro quo disclosures)
- **Review Cycle**: Annual or when fundraising changes
- **Placeholders**: `{{ORG_NAME}}`, `{{GIFT_ACCEPTANCE_COMMITTEE}}`, `{{MINIMUM_AMOUNTS}}`

#### 9. **Privacy and Data Protection Policy Template**
- **File**: `policies/privacy-data-protection-policy.md`
- **Priority**: Important (Essential if handling sensitive data)
- **Purpose**: Governs collection, use, storage, and protection of personal information
- **Sections**:
  - Scope (what data, whose data)
  - Data collection and consent
  - Data use limitations
  - Data security controls
  - Data retention and disposal
  - Breach notification procedures
  - Individual rights (access, correction, deletion)
  - Third-party sharing
  - Compliance framework references (GDPR if applicable, state privacy laws)
- **Review Cycle**: Annual or when laws change
- **Placeholders**: `{{ORG_NAME}}`, `{{DATA_PROTECTION_OFFICER}}`, `{{APPLICABLE_LAWS}}`

#### 10. **Cybersecurity and Information Security Policy Template**
- **File**: `policies/cybersecurity-policy.md`
- **Priority**: Important
- **Purpose**: Establishes cybersecurity governance and controls
- **Sections**:
  - Scope and applicability
  - Roles and responsibilities
  - Access controls and authentication
  - Data classification and handling
  - Incident response procedures
  - Device management (BYOD, laptops, mobile)
  - Email and communications security
  - Vendor/third-party risk
  - Training requirements
- **Review Cycle**: Annual
- **Placeholders**: `{{ORG_NAME}}`, `{{IT_MANAGER}}`, `{{INCIDENT_RESPONSE_TEAM}}`

### HR - Employee Templates (5 templates)

#### 11. **Employee Handbook Template**
- **File**: `hr-employee/employee-handbook.md`
- **Priority**: Essential (if employees exist)
- **Purpose**: Sets employment terms, reduces legal risk, standardizes conduct
- **Sections**:
  - Welcome and mission
  - Equal Employment Opportunity (EEO) and nondiscrimination
  - Harassment prevention and complaint process
  - Wage and hour policies (timekeeping, overtime)
  - Leave policies (PTO, sick, FMLA, state leave)
  - Benefits overview
  - Performance management and discipline
  - Confidentiality and intellectual property
  - Technology and social media use
  - Workplace safety and incident reporting
  - Grievance and complaint procedures
  - Acknowledgment form
- **Regulatory Context**: Federal and state employment law; EEOC expectations
- **Review Cycle**: At least annual (state-specific updates frequent)
- **Placeholders**: `{{ORG_NAME}}`, `{{STATE}}`, `{{BENEFITS_SUMMARY}}`, `{{HR_CONTACT}}`

#### 12. **Job Description Template**
- **File**: `hr-employee/job-description-template.md`
- **Priority**: Essential
- **Purpose**: Defines duties, qualifications, reporting, and performance criteria
- **Sections**:
  - Job title and department
  - Reports to
  - FLSA classification (exempt/non-exempt)
  - Summary and mission alignment
  - Essential duties and responsibilities
  - Required qualifications (education, experience, certifications)
  - Physical requirements and working conditions
  - Safeguarding responsibilities (if applicable)
  - Required training
- **Review Cycle**: Annual or with role changes
- **Placeholders**: `{{JOB_TITLE}}`, `{{DEPARTMENT}}`, `{{SUPERVISOR}}`, `{{FLSA_STATUS}}`

#### 13. **Offer Letter Template**
- **File**: `hr-employee/offer-letter-template.md`
- **Priority**: Essential
- **Purpose**: Establishes employment terms, at-will status, and key conditions
- **Sections**:
  - Position title and start date
  - Compensation and benefits overview
  - At-will employment statement (where applicable)
  - Contingencies (background check, references)
  - Confidentiality and conflict of interest acknowledgment
  - Acceptance signature line
- **Review Cycle**: With law/benefit changes
- **Placeholders**: `{{CANDIDATE_NAME}}`, `{{POSITION}}`, `{{START_DATE}}`, `{{SALARY}}`, `{{STATE}}`

#### 14. **Performance Review Template**
- **File**: `hr-employee/performance-review-template.md`
- **Priority**: Important
- **Purpose**: Structured evaluation process aligned to job description and goals
- **Sections**:
  - Employee and reviewer information
  - Review period
  - Job performance assessment (by competency/duty)
  - Goal achievement
  - Strengths and development areas
  - Goals for next period
  - Overall rating
  - Employee comments
  - Signatures and dates
- **Review Cycle**: Annual or semi-annual
- **Placeholders**: `{{EMPLOYEE_NAME}}`, `{{REVIEW_PERIOD}}`, `{{COMPETENCIES}}`

#### 15. **Separation Checklist Template**
- **File**: `hr-employee/separation-checklist.md`
- **Priority**: Important
- **Purpose**: Ensures consistent offboarding, protects data, recovers assets
- **Sections**:
  - Separation type (voluntary, involuntary, retirement)
  - Exit interview
  - Final paycheck and accruals
  - Benefits/COBRA notification
  - Return of property (keys, laptop, ID, files)
  - IT access termination
  - Confidentiality reminder
  - References policy
  - Unemployment information (if applicable)
- **Review Cycle**: With HR process changes
- **Placeholders**: `{{EMPLOYEE_NAME}}`, `{{SEPARATION_DATE}}`, `{{PROPERTY_LIST}}`

### HR - Volunteer Templates (4 templates)

#### 16. **Volunteer Handbook Template**
- **File**: `hr-volunteer/volunteer-handbook.md`
- **Priority**: Important (Essential for public-facing volunteer programs)
- **Purpose**: Clarifies volunteer conduct, supervision, safety, and reporting
- **Sections**:
  - Welcome and mission
  - Volunteer eligibility and screening
  - Code of conduct
  - Safeguarding responsibilities (especially with vulnerable populations)
  - Confidentiality
  - Reporting requirements (incidents, concerns, misconduct)
  - Supervision and support
  - Expense reimbursement (if applicable)
  - Dismissal procedures
  - Media and photography policies
  - Acknowledgment form
- **Regulatory Context**: Risk management; insurer expectations; safeguarding standards
- **Review Cycle**: Annual and after incidents
- **Placeholders**: `{{ORG_NAME}}`, `{{VOLUNTEER_COORDINATOR}}`, `{{SCREENING_REQUIREMENTS}}`

#### 17. **Volunteer Application Template**
- **File**: `hr-volunteer/volunteer-application.md`
- **Priority**: Essential (for volunteer screening)
- **Purpose**: Collects information for screening and role matching
- **Sections**:
  - Personal information
  - Availability and interests
  - Skills and experience
  - References
  - Background check consent (if required)
  - Emergency contact
  - Agreements (confidentiality, code of conduct)
  - Signature and date
- **Review Cycle**: When screening requirements change
- **Placeholders**: `{{ORG_NAME}}`, `{{PROGRAM_OPTIONS}}`, `{{SCREENING_NOTICE}}`

#### 18. **Volunteer Background Check Policy Template**
- **File**: `hr-volunteer/volunteer-background-check-policy.md`
- **Priority**: Essential (when volunteers work with vulnerable populations)
- **Purpose**: Defines screening tiers and processes
- **Sections**:
  - Scope (which roles require screening)
  - Screening tiers (reference checks, criminal background, driving records)
  - Process and timing
  - Disqualification criteria
  - Confidentiality of results
  - Re-screening frequency
  - Appeal process
- **Regulatory Context**: State-specific requirements; safeguarding best practices
- **Review Cycle**: Annual
- **Placeholders**: `{{ORG_NAME}}`, `{{SCREENING_VENDOR}}`, `{{DISQUALIFYING_OFFENSES}}`

#### 19. **Volunteer Role Description Template**
- **File**: `hr-volunteer/volunteer-role-description.md`
- **Priority**: Important
- **Purpose**: Defines volunteer role, duties, and supervision
- **Sections**:
  - Role title
  - Program/department
  - Supervisor
  - Time commitment
  - Duties and responsibilities
  - Required qualifications and training
  - Safeguarding responsibilities
  - Support provided
- **Review Cycle**: Annual or with program changes
- **Placeholders**: `{{ROLE_TITLE}}`, `{{PROGRAM}}`, `{{TIME_COMMITMENT}}`, `{{SUPERVISOR}}`

### Finance and Tax Templates (2 templates)

#### 20. **Financial Policies and Procedures Manual Template**
- **File**: `finance-tax/financial-policies-procedures.md`
- **Priority**: Essential
- **Purpose**: Consolidates financial controls, approval authorities, and accounting policies
- **Sections**:
  - Budget development and approval process
  - Financial reporting to board
  - Cash handling and deposit procedures
  - Procurement and purchasing authorities
  - Expense reimbursement
  - Credit card policies
  - Signing authorities
  - Segregation of duties
  - Investment policies (if applicable)
  - Internal controls and audit cooperation
- **Review Cycle**: Annual or with audit findings
- **Placeholders**: `{{ORG_NAME}}`, `{{CFO}}`, `{{APPROVAL_THRESHOLDS}}`, `{{FISCAL_YEAR_END}}`

#### 21. **Form 990 Preparation Checklist Template**
- **File**: `finance-tax/form-990-preparation-checklist.md`
- **Priority**: Essential
- **Purpose**: Ensures complete and accurate annual filing
- **Sections**:
  - Financial data collection timeline
  - Governance questions (Part VI) checklist
  - Schedule requirements review
  - Board review process
  - Preparer responsibilities
  - Filing deadline and extension process
  - Public disclosure preparation
- **Regulatory Context**: IRS Form 990 requirements
- **Review Cycle**: Annual (mid-year prep)
- **Placeholders**: `{{ORG_NAME}}`, `{{FISCAL_YEAR_END}}`, `{{TAX_PREPARER}}`, `{{BOARD_REVIEW_DATE}}`

---

## Template Metadata Schema

Each template includes consistent YAML frontmatter:

```yaml
---
title: "Template Name"
category: "governance | policies | hr-employee | hr-volunteer | finance-tax | program-operations"
priority: "essential | important | situational"
version: "1.0"
effective_date: "YYYY-MM-DD"
review_cycle: "annual | semi-annual | as-needed"
applicable_frameworks: ["Form 990", "State Nonprofit Law", "Employment Law"]
owner: "Board | Executive Director | CFO | HR Manager"
approved_by: "Board | Executive Committee"
approval_date: "YYYY-MM-DD"
supersedes: "None | Previous version reference"
related_documents: ["List of related policies/templates"]
---
```

---

## Situational Templates (Not Phase 1 MVP)

These are **Phase 2+ ideas** based on KeyDocuments guide:

### Youth Safeguarding (if serving minors)
- **Youth Protection Policy Template**
- **Child Abuse Reporting Procedures Template**
- **Parent/Guardian Consent Forms Template**

### Federal Grants (if receiving federal awards)
- **Federal Grants Management Policy Template**
- **Uniform Guidance Compliance Procedures Template**
- **Subrecipient Monitoring Template**

### Healthcare/Medical Services
- **HIPAA Compliance Policy Template**
- **Medical Records Retention Schedule Template**

---

## Phase 1 MVP Summary

**Total Templates for Non-Profit Profile: 21**

Distribution:
- Governance: 7 templates
- Policies: 3 templates
- HR - Employee: 5 templates
- HR - Volunteer: 4 templates
- Finance/Tax: 2 templates

**All 21 templates are derived from the "Essential" and high-priority "Important" tiers** identified in KeyDocuments-NotForProfits.md.

---

## Implementation Notes

### Template Customization Process

```bash
# User creates document from template
$ docspec create handbook "Employee Handbook"

# CLI prompts for placeholders
Company name: Acme Nonprofit
State: California
HR Contact: hr@acmenonprofit.org

# CLI generates:
# documents/handbooks/employee-handbook.md
# Pre-filled with metadata and placeholder values
# User edits in Markdown editor
```

### Compliance Validation (Phase 2 Idea)

Future compliance engine would:
- Check that required sections are present
- Validate against Form 990 Part VI governance questions
- Flag missing policies referenced in bylaws
- Warn about state-specific requirements

### Template Updates

When DocSpecSpark publishes updated templates:
```bash
$ docspec update
Found new template: youth-protection-policy.md
Found updated template: conflict-of-interest-policy.md (v1.0 → v1.1)

✓ Added new template to .DocSpecSpark/templates/
✓ Updated existing template (your documents are NOT changed)

To use new template: docspec create policy "Youth Protection Policy"
```

---

## Sources and Alignment

This template library is **directly aligned** with:

1. **KeyDocuments-NotForProfits.md** - Comprehensive nonprofit document requirements analysis
2. **IRS Form 990 Part VI** - Governance and policy disclosure questions
3. **IRS Form 1023** - Tax-exemption application requirements
4. **National Council of Nonprofits** - Governance best practices
5. **BoardSource** - Board governance resources
6. **Nonprofit Risk Management Center** - Risk and safeguarding standards

---

*This template library represents Phase 1 MVP scope. Additional templates (youth safeguarding, federal grants, healthcare) are future ideas based on operational triggers.*
