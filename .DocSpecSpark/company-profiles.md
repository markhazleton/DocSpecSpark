# Company Profiles - DocSpecSpark

## Overview

DocSpecSpark supports diverse organizational types with different document needs, compliance requirements, and operational characteristics. This document defines **7 company profiles** that determine which templates, frameworks, and workflows are pre-configured during initialization.

Each profile includes recommended document templates, compliance frameworks, approval workflows, and resource allocations tailored to the organization's size, industry, and structure.

---

## Profile Selection During Initialization

```bash
# CLI initialization prompts for profile
$ docspec init --client "Acme Corp"

Welcome to DocSpecSpark! Let's set up your company.

Select your organization profile:
 1. Not-for-Profit (with volunteers)
 2. Early-Stage Startup (< 10 people)
 3. Small Business - Service Industry (10-50 employees)
 4. Small Business - Manufacturing (50-250 employees)
 5. Mid-Sized Enterprise (250-1000 employees)
 6. Large Enterprise (1000+ employees)
 7. Healthcare Organization (regulated)
 8. Custom (I'll configure manually)

Your choice [1-8]: _
```

---

## Profile 1: Not-for-Profit with Volunteers

### Characteristics
- **Size**: 5-50 people (mix of staff and volunteers)
- **Structure**: Board of Directors, Executive Director, volunteer coordinators
- **Funding**: Grants, donations, fundraising events
- **Key Challenges**: 
  - Limited budget for tooling
  - High volunteer turnover
  - Grant compliance requirements
  - Transparency for donors

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "501(c)(3) Non-Profit"
  employee_count: 15
  volunteer_count: 35
  
compliance:
  active_frameworks:
    - id: "labor-law"
      applicability: "Paid staff only"
    - id: "grant-compliance"  # Custom framework
      file: ".DocSpecSpark/compliance/custom/grant-compliance.md"
    - id: "donor-transparency"  # Custom framework
      file: ".DocSpecSpark/compliance/custom/donor-transparency.md"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["executive-director"]
      approvers: ["board-chair"]
      review_cycle: "biannual"
    
    volunteer:  # Special document type
      reviewers: ["volunteer-coordinator"]
      approvers: ["executive-director"]
      review_cycle: "annual"

branding:
  primary_color: "#2E7D32"  # Green (community-focused)
```

**Document Templates Included**:

See [nonprofit-template-library.md](nonprofit-template-library.md) for complete specifications.

| Template | Category | Priority |
|----------|----------|----------|
| **Bylaws** | Governance | HIGH |
| **Board Policy Manual** | Governance | HIGH |
| **Board Member Job Description** | Governance | HIGH |
| **Board Meeting Minutes Template** | Governance | HIGH |
| **Conflict of Interest Policy + Disclosure** | Governance | HIGH |
| **Whistleblower Policy** | Governance | HIGH |
| **Document Retention Policy** | Governance | HIGH |
| **Gift Acceptance Policy** | Policy | HIGH |
| **Privacy and Data Protection Policy** | Policy | MEDIUM |
| **Cybersecurity Policy** | Policy | MEDIUM |
| **Employee Handbook** | HR-Employee | HIGH |
| **Job Description Template** | HR-Employee | HIGH |
| **Offer Letter Template** | HR-Employee | MEDIUM |
| **Performance Review Template** | HR-Employee | MEDIUM |
| **Separation Checklist** | HR-Employee | LOW |
| **Volunteer Handbook** | HR-Volunteer | HIGH |
| **Volunteer Application** | HR-Volunteer | HIGH |
| **Volunteer Background Check Policy** | HR-Volunteer | HIGH |
| **Volunteer Role Description** | HR-Volunteer | MEDIUM |
| **Financial Policies & Procedures** | Finance | HIGH |
| **Form 990 Preparation Checklist** | Finance | HIGH |

**Total: 21 templates** derived from Essential/Important tiers in IRS Form 990 governance framework.

**Team Structure**:
```yaml
teams:
  - name: "board-directors"
    role: "Final approval on policies"
    members: ["board-chair", "board-member-1", "board-member-2"]
  
  - name: "staff-leadership"
    role: "Day-to-day operations"
    members: ["executive-director", "program-director"]
  
  - name: "volunteer-coordinators"
    role: "Volunteer management"
    members: ["volunteer-coordinator"]
```

---

## Profile 2: Early-Stage Startup (< 10 people)

### Characteristics
- **Size**: 2-9 people (mostly founders + early employees)
- **Structure**: Flat hierarchy, co-founders make decisions
- **Funding**: Seed/Angel funding, bootstrapped
- **Key Challenges**: 
  - Move fast, minimal bureaucracy
  - Preparing for investor due diligence
  - Scaling policies as team grows
  - IP protection

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "Delaware C Corporation"
  employee_count: 6
  funding_stage: "Seed"
  
compliance:
  active_frameworks:
    - id: "labor-law"
    - id: "ip-protection"  # Custom
      file: ".DocSpecSpark/compliance/custom/ip-protection.md"
  
  # SOC 2, GDPR deferred until revenue/customers

document_governance:
  version_strategy: "date-based"  # Move fast, less formal
  
  approval_workflows:
    policy:
      reviewers: []  # Skip formal review
      approvers: ["ceo"]  # CEO approves everything
      review_cycle: "as-needed"
    
    employee:
      reviewers: ["ceo"]
      approvers: ["ceo"]
      review_cycle: "as-needed"

branding:
  primary_color: "#FF6F00"  # Orange (startup energy)
```

**Document Templates Included**:
| Template | Purpose | Priority |
|----------|---------|----------|
| **Employee Offer Letter** | Hiring first employees | HIGH |
| **IP Assignment Agreement** | Protect company IP | HIGH |
| **Stock Option Plan** | Equity compensation | HIGH |
| **Code of Conduct (Simple)** | Basic behavioral expectations | MEDIUM |
| **Remote Work Policy** | Distributed team guidelines | HIGH |
| **NDA Template (Mutual)** | Partner discussions | MEDIUM |
| **Acceptable Use Policy (IT)** | Security basics | MEDIUM |
| **Data Privacy Policy (MVP)** | Minimal compliance for early users | LOW |

**Team Structure**:
```yaml
teams:
  - name: "founders"
    role: "All decision-making"
    members: ["ceo", "cto", "co-founder-3"]
```

---

## Profile 3: Small Business - Service Industry (10-50 employees)

### Characteristics
- **Size**: 10-50 employees
- **Industry**: Consulting, marketing, accounting, law firm, etc.
- **Structure**: Owner/Partners, department leads, individual contributors
- **Key Challenges**: 
  - Professional liability
  - Client confidentiality
  - Employee performance management
  - Financial controls

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "LLC"
  employee_count: 28
  industry: "Professional Services"
  
compliance:
  active_frameworks:
    - id: "labor-law"
    - id: "soc2"  # Client data protection
    - id: "professional-liability"  # Custom
      file: ".DocSpecSpark/compliance/custom/professional-liability.md"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["hr-manager", "managing-partner"]
      approvers: ["managing-partner"]
      review_cycle: "annual"
    
    client-facing:  # Special category
      reviewers: ["legal-counsel", "managing-partner"]
      approvers: ["managing-partner"]
      review_cycle: "annual"

branding:
  primary_color: "#1565C0"  # Blue (professional)
```

**Document Templates Included**:
| Template | Purpose | Priority |
|----------|---------|----------|
| **Employee Handbook** | Full HR policies | HIGH |
| **Client Confidentiality Policy** | Protect client information | HIGH |
| **Performance Review Policy** | Annual review process | HIGH |
| **Time Tracking & Billing Policy** | Client billing practices | HIGH |
| **Professional Development Policy** | Training, certifications | MEDIUM |
| **Expense Reimbursement Policy** | Travel, equipment | MEDIUM |
| **Work-from-Home Policy** | Hybrid work expectations | HIGH |
| **Client Engagement Agreement** | Standard terms of service | HIGH |
| **Anti-Harassment Policy** | Legal compliance | HIGH |
| **Document Retention Policy** | Client records, tax docs | MEDIUM |

**Team Structure**:
```yaml
teams:
  - name: "partners"
    role: "Leadership decisions"
    members: ["managing-partner", "partner-2", "partner-3"]
  
  - name: "hr-team"
    role: "Employee policies"
    members: ["hr-manager"]
  
  - name: "all-staff"
    role: "Read access to handbook"
    members: ["*"]
```

---

## Profile 4: Small Business - Manufacturing (~100 employees)

### Characteristics
- **Size**: ~100 employees (CEO/COO/CFO, engineering, HR, sales departments)
- **Industry**: Manufacturing, assembly, production
- **Structure**: Executive team, plant managers, engineering, quality, floor supervisors, production workers
- **Regulatory Environment**: Federal + state + local compliance stack
- **Key Challenges**: 
  - OSHA compliance (injury/illness recordkeeping, hazard communication, LOTO, confined spaces)
  - EPA/EPCRA reporting (Tier II, TRI if applicable, hazardous waste, SPCC)
  - Engineering change control and document control
  - Export controls (if applicable)
  - IT/OT security convergence
  - Quality management system (ISO 9001 or customer-specific QMS requirements)
  - HR compliance recordkeeping (I-9, FLSA, ERISA benefit plan disclosures)

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "C Corporation"  # or LLC
  employee_count: 100
  industry: "Manufacturing"
  
compliance:
  active_frameworks:
    - id: "osha-recordkeeping"
      scope: "29 CFR 1904 injury/illness logs"
    - id: "osha-safety-standards"
      scope: "HazCom, LOTO, confined space, emergency action"
    - id: "epa-epcra"
      scope: "Tier II, TRI (if thresholds met)"
      conditional: true
    - id: "epa-rcra"
      scope: "Hazardous waste generator requirements"
      conditional: true
    - id: "iso9001"
      scope: "Quality management system"
    - id: "export-controls"
      scope: "EAR compliance (BIS Eight Elements)"
      conditional: true
    - id: "nist-csf"
      scope: "Cybersecurity Framework 2.0 (IT and OT/ICS)"
    - id: "labor-law"
      scope: "FLSA, FMLA, ERISA, I-9, state wage/hour"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["hr-director", "legal-counsel", "ehs-manager"]
      approvers: ["coo", "ceo"]
      review_cycle: "annual"
    
    safety-environmental:  # Critical category - OSHA/EPA programs
      reviewers: ["ehs-manager", "plant-manager", "legal-counsel"]
      approvers: ["coo"]
      review_cycle: "quarterly"
      mandatory_training: true
    
    quality-engineering:  # QMS procedures and change control
      reviewers: ["quality-manager", "engineering-manager"]
      approvers: ["coo"]
      review_cycle: "annual"
      change_triggers: ["regulatory_change", "nonconformance", "new_equipment", "audit_finding"]
    
    export-trade:  # Export compliance (if applicable)
      reviewers: ["trade-compliance-officer", "legal-counsel"]
      approvers: ["ceo", "legal-counsel"]
      review_cycle: "semi-annual"
      mandatory: false  # Only if exporting

branding:
  primary_color: "#D32F2F"  # Red (industrial)
```

**Document Templates Included** (40 templates total):

See [smallbusiness-template-library.md](smallbusiness-template-library.md) for complete specifications.

**Corporate & Governance (4)**:
- Bylaws (Corporation) / Operating Agreement (LLC)
- Board/Owner Meeting Minutes Template
- Delegation of Authority (DoA) Matrix
- Corporate Resolutions Template

**Safety & Environmental (10)**:
- OSHA Injury & Illness Recordkeeping Procedure (300/300A/301)
- Severe Incident Reporting Procedure (OSHA 1904.39)
- Hazard Communication Program (HazCom) + SDS Management
- Lockout/Tagout (LOTO) Program + Machine-Specific Procedures
- Permit-Required Confined Space Program
- Emergency Action Plan (EAP)
- EPCRA Tier II Chemical Inventory Reporting Procedure
- TRI (Toxic Release Inventory) Reporting Procedure
- Hazardous Waste Management Program (RCRA)
- SPCC Plan (Spill Prevention, Control, and Countermeasure)

**Quality & Engineering (6)**:
- Document Control Procedure
- Engineering Change Control Procedure (ECN/ECO)
- Calibration Program Procedure
- Production Control Procedure
- Inspection and Test Procedure
- Nonconforming Material Control Procedure

**HR & Employment (8)**:
- Employee Handbook (Manufacturing-Specific)
- Job Description Template (Manufacturing Roles)
- Offer Letter Template
- Background Check Policy + FCRA Compliance
- Form I-9 Compliance Procedure
- Payroll and Timekeeping Recordkeeping Procedure
- Benefits Plan Summary Plan Descriptions (SPD) Template
- Training Records Management Procedure

**Finance & Tax (3)**:
- Financial Policies and Procedures Manual
- Tax Compliance Calendar and Filing Procedure
- Permits and Compliance Obligations Register

**Commercial & Legal (4)**:
- Export Compliance Program (ECP/ICP)
- Standard Terms and Conditions (Sales)
- Purchase Order Terms and Conditions
- Confidentiality/NDA Template

**IT & Cybersecurity (5)**:
- Cybersecurity Policy (NIST CSF 2.0 Aligned)
- Incident Response Plan
- Business Continuity and Disaster Recovery Plan
- OT/ICS Security Procedure
- Acceptable Use Policy (IT Systems)

**Team Structure**:
```yaml
teams:
  - name: "executive-team"
    role: "Strategic decisions and corporate governance"
    members: ["ceo", "coo", "cfo"]
  
  - name: "safety-environmental-committee"
    role: "OSHA/EPA compliance, safety programs, environmental reporting"
    members: ["ehs-manager", "plant-manager", "coo"]
  
  - name: "quality-engineering-team"
    role: "ISO 9001 compliance, document control, change control"
    members: ["quality-manager", "engineering-manager", "coo"]
  
  - name: "trade-compliance-team"  # If exporting
    role: "Export controls, restricted party screening, classification"
    members: ["trade-compliance-officer", "sales-director", "legal-counsel"]
    conditional: true
  
  - name: "hr-team"
    role: "Employment policies, benefits, I-9, training records"
    members: ["hr-director", "payroll-manager"]
  
  - name: "it-security-team"
    role: "Cybersecurity (IT and OT/ICS), incident response, DR/BC"
    members: ["it-manager", "coo", "cfo"]
```

---

## Profile 5: Mid-Sized Enterprise (250-1000 employees)

### Characteristics
- **Size**: 250-1000 employees
- **Structure**: C-suite, multiple departments, middle management
- **Operations**: Multiple locations, possibly international
- **Key Challenges**: 
  - Complex org structure
  - Regulatory compliance (varies by industry)
  - Change management
  - Data governance

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "C Corporation"
  employee_count: 520
  locations: ["US-HQ", "US-West", "Canada", "UK"]
  
compliance:
  active_frameworks:
    - id: "soc2"
    - id: "iso9001"
    - id: "gdpr"  # International operations
    - id: "labor-law"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["legal", "compliance", "hr"]
      approvers: ["legal-counsel", "chief-compliance-officer"]
      review_cycle: "annual"
      version_strategy: "semantic"
    
    handbook:
      reviewers: ["hr", "legal", "compliance"]
      approvers: ["chief-hr-officer", "legal-counsel"]
      review_cycle: "annual"

integrations:
  sharepoint:
    enabled: true
    sync_strategy: "on-publish"
  teams:
    enabled: true

branding:
  primary_color: "#0277BD"  # Corporate blue
```

**Document Templates Included**: (All from previous profiles PLUS)
| Template | Purpose | Priority |
|----------|---------|----------|
| **Business Continuity Plan** | Disaster recovery | HIGH |
| **Information Security Policy (Comprehensive)** | CISO-level framework | HIGH |
| **Data Governance Policy** | Data ownership, classification | HIGH |
| **Vendor Management Policy** | Third-party risk | HIGH |
| **Travel & Expense Policy** | Global operations | MEDIUM |
| **Severance Policy** | Layoffs, terminations | MEDIUM |
| **Succession Planning Guide** | Leadership continuity | MEDIUM |
| **M&A Integration Playbook** | Acquisitions | LOW |

**Team Structure**:
```yaml
teams:
  - name: "executive-leadership"
    members: ["ceo", "cfo", "coo", "cto", "chro"]
  
  - name: "legal-compliance"
    members: ["legal-counsel", "chief-compliance-officer", "legal-team"]
  
  - name: "hr-leadership"
    members: ["chief-hr-officer", "hr-directors"]
  
  - name: "information-security"
    members: ["ciso", "infosec-team"]
```

---

## Profile 6: Large Enterprise (1000+ employees)

### Characteristics
- **Size**: 1000+ employees
- **Structure**: Complex hierarchy, business units, global operations
- **Governance**: Board of Directors, audit committees, formal controls
- **Key Challenges**: 
  - Regulatory diversity (multi-jurisdiction)
  - Policy consistency across BUs
  - Audit readiness
  - Stakeholder management

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "Public Corporation"
  employee_count: 2500
  locations: ["Global - 15 countries"]
  
compliance:
  active_frameworks:
    - id: "soc2"
      type: "Type II"
    - id: "iso9001"
    - id: "iso27001"
    - id: "gdpr"
    - id: "ccpa"  # California
    - id: "hipaa"  # If applicable
    - id: "sox"  # Sarbanes-Oxley (public companies)
      file: ".DocSpecSpark/compliance/custom/sox-compliance.md"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["legal", "compliance", "audit", "risk-management"]
      approvers: ["legal-counsel", "chief-compliance-officer", "audit-committee-chair"]
      review_cycle: "biannual"
      require_board_notification: true
    
    public-disclosure:  # Special category
      reviewers: ["legal", "investor-relations", "communications"]
      approvers: ["ceo", "general-counsel", "board-chair"]
      review_cycle: "as-needed"

  audit_trail:
    log_access_history: true
    require_approval_signature: true
    blockchain_hash: true  # Immutable audit trail

integrations:
  sharepoint:
    enabled: true
    sync_strategy: "real-time"
  teams:
    enabled: true
  sso:
    provider: "okta"
    require_mfa: true

branding:
  primary_color: "#004D40"  # Dark teal (enterprise)
```

**Document Templates Included**: (All from previous profiles PLUS)
| Template | Purpose | Priority |
|----------|---------|----------|
| **Corporate Governance Charter** | Board bylaws, committees | HIGH |
| **Insider Trading Policy** | Securities compliance | HIGH |
| **Whistleblower Policy** | Anonymous reporting | HIGH |
| **Anti-Bribery & Corruption Policy** | FCPA compliance | HIGH |
| **Records Management Policy** | Legal hold, retention | HIGH |
| **Crisis Communication Plan** | PR emergencies | HIGH |
| **Global HR Policy Framework** | Multi-country compliance | HIGH |
| **Third-Party Code of Conduct** | Supplier ethics | MEDIUM |

**Team Structure**:
```yaml
teams:
  - name: "board-of-directors"
    members: ["board-chair", "board-members"]
  
  - name: "c-suite"
    members: ["ceo", "cfo", "coo", "cto", "chro", "general-counsel", "ciso"]
  
  - name: "compliance-committee"
    members: ["chief-compliance-officer", "legal-team", "audit-team", "risk-management"]
  
  - name: "document-governance-team"
    role: "Manages DocSpecSpark itself"
    members: ["compliance-analyst", "legal-operations", "it-governance"]
```

---

## Profile 7: Healthcare Organization (Regulated)

### Characteristics
- **Size**: Varies (clinic to hospital system)
- **Industry**: Healthcare provider, medical device, biotech
- **Key Challenges**: 
  - HIPAA compliance (mandatory)
  - Patient safety
  - Clinical protocols
  - Medical staff credentialing

### Pre-Configured Settings

**Constitution Defaults**:
```yaml
company:
  legal_entity_type: "Healthcare Corporation"
  employee_count: 350
  industry: "Healthcare"
  
compliance:
  active_frameworks:
    - id: "hipaa"
      scope: "All PHI-related operations"
      mandatory: true
    - id: "labor-law"
    - id: "osha"
      applicability: "Clinical and laboratory safety"
    - id: "clinical-quality"  # Custom
      file: ".DocSpecSpark/compliance/custom/clinical-quality.md"

document_governance:
  approval_workflows:
    policy:
      reviewers: ["legal", "compliance", "medical-director", "privacy-officer"]
      approvers: ["chief-medical-officer", "legal-counsel"]
      review_cycle: "annual"
      hipaa_review_required: true
    
    clinical-protocol:  # Special category
      reviewers: ["medical-director", "quality-assurance"]
      approvers: ["chief-medical-officer"]
      review_cycle: "biannual"
      evidence_based: true

branding:
  primary_color: "#1976D2"  # Healthcare blue
```

**Document Templates Included**:
| Template | Purpose | Priority |
|----------|---------|----------|
| **HIPAA Privacy Policy** | Patient data protection | HIGH |
| **HIPAA Security Policy** | Technical safeguards | HIGH |
| **Notice of Privacy Practices** | Patient-facing disclosure | HIGH |
| **Business Associate Agreement (BAA)** | Vendor contracts | HIGH |
| **Breach Notification Policy** | HIPAA breach response | HIGH |
| **Patient Rights Policy** | Access, amendment requests | HIGH |
| **Medical Staff Bylaws** | Credentialing, privileges | HIGH |
| **Infection Control Policy** | Clinical safety | HIGH |
| **Adverse Event Reporting** | Patient safety | HIGH |
| **Clinical Documentation Standards** | Medical records | MEDIUM |
| **Telehealth Policy** | Virtual care compliance | MEDIUM |

---

## Profile Comparison Matrix

| Feature | Not-for-Profit | Startup | Service (10-50) | Manufacturing | Mid-Size | Enterprise | Healthcare |
|---------|----------------|---------|-----------------|---------------|----------|------------|------------|
| **Default Templates** | 8 | 8 | 10 | 12 | 18 | 25 | 11 |
| **Compliance Frameworks** | 3 | 2 | 3 | 4 | 4 | 7 | 4 |
| **Approval Layers** | 2 | 1 | 2 | 3 | 3 | 4+ | 3 |
| **Review Frequency** | Biannual | As-needed | Annual | Quarterly | Annual | Biannual | Annual |
| **SharePoint Integration** | Optional | No | Optional | Yes | Yes | Required | Yes |
| **Custom Frameworks** | 2 | 1 | 1 | 2 | 0 | 1 | 1 |
| **Industry-Specific** | ✅ Grants | ❌ | ❌ | ✅ Safety | ❌ | ✅ SOX | ✅ HIPAA |

---

## Profile Migration & Evolution

### Startup → Small Business
```bash
# As startup grows, migrate to small business profile
$ docspec migrate-profile --from startup --to small-business-service

Migrating profile...
✓ Adding templates: Employee Handbook, Performance Review Policy
✓ Upgrading approval workflows (2 layers)
✓ Activating compliance framework: SOC 2
✓ Enabling SharePoint integration (optional)

Migration complete. 4 new templates available, 2 workflows updated.
```

### Profile Auto-Detection
```yaml
# .DocSpecSpark/constitution.yaml
company:
  profile: "startup"
  profile_override: false  # Allow auto-upgrade suggestions
  
  # Triggers auto-suggestion
  employee_count: 55  # Profile says "< 10", but actual is 55
  
# System suggests:
# "Your company has grown! Consider upgrading to 'small-business-service' profile."
```

---

## Customization Examples

### Example 1: Hybrid Profile (Manufacturing + Healthcare)
```yaml
# Medical device manufacturer
company:
  base_profile: "manufacturing"
  
compliance:
  active_frameworks:
    - id: "iso9001"  # From manufacturing
    - id: "iso13485"  # Medical devices (custom)
    - id: "fda-qsr"   # FDA Quality System Regulation
    - id: "hipaa"     # From healthcare profile
```

### Example 2: International Non-Profit
```yaml
# Non-profit operating in EU
company:
  base_profile: "not-for-profit"
  
compliance:
  active_frameworks:
    - id: "grant-compliance"
    - id: "gdpr"  # Added for EU operations
```

---

**Status**: Draft for review
**Next Steps**:
1. Create initialization wizard that prompts for profile
2. Build template bundles for each profile
3. Create migration scripts between profiles
4. Test profile defaults with sample companies
