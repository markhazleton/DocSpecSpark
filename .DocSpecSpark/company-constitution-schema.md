# Company Constitution Schema - DocSpecSpark

## Overview

The **Company Constitution** (`constitution.yaml`) is the **single source of truth** for all company metadata in DocSpecSpark. It serves as:

1. **Company Metadata Repository**: Legal name, structure, contacts, locations - all company information
2. **Template Token Source**: Provides replacement values for all `{{TOKENS}}` in document templates
3. **Compliance Framework Registry**: Active frameworks, applicability, audit schedules
4. **Document Governance Rules**: Approval workflows, review cycles, versioning strategy
5. **Branding & Presentation**: Company colors, logos, formatting preferences

### Key Architectural Principle

**One Constitution → Many Documents**

```
constitution.yaml                    Templates
├── company.legal_name        →     {{COMPANY_NAME}}
├── company.state            →     {{STATE}}
├── company.tax_id           →     {{EIN}}
├── governance.board_chair   →     {{BOARD_CHAIR}}
├── contacts.ceo             →     {{CEO_NAME}}
└── ... (all metadata)       →     ... (all tokens)
```

Every document template uses tokens (`{{COMPANY_NAME}}`, `{{CEO_NAME}}`, `{{STATE}}`) that are **automatically replaced** with values from the constitution when documents are created.

**Result**: Change company metadata once in constitution → All future documents reflect the change.

---

## Interactive Constitution Builder

### `docspec build-constitution` Command

When initializing a new DocSpecSpark repository, users run an **interactive questionnaire** that builds the constitution:

```bash
$ docspec init

╔══════════════════════════════════════════════════════════╗
║        DocSpecSpark - Constitution Builder              ║
║  (This will create your company metadata repository)    ║
╚══════════════════════════════════════════════════════════╝

Select your organization type:
  1. Not-for-Profit (501(c)(3))
  2. Small Business - Manufacturing
  3. Small Business - Service
  4. Early-Stage Startup
  5. Healthcare Provider
  6. Mid-Sized Enterprise
  7. Large Enterprise
  8. Custom

Your choice [1-8]: 2

╔══════════════════════════════════════════════════════════╗
║     COMPANY IDENTITY & LEGAL STRUCTURE                  ║
╚══════════════════════════════════════════════════════════╝

Legal company name: Acme Manufacturing Inc.
Doing business as (DBA) [optional]: 
Legal entity type [C Corporation]: 
State of incorporation: Ohio
Year founded: 2010
Federal Tax ID (EIN): 12-3456789
Number of employees: 95

╔══════════════════════════════════════════════════════════╗
║     GOVERNANCE & LEADERSHIP                             ║
╚══════════════════════════════════════════════════════════╝

Chief Executive Officer (CEO): John Smith
Chief Operating Officer (COO): Sarah Johnson
Chief Financial Officer (CFO): Michael Lee
EHS Manager: David Martinez
Quality Manager: Lisa Chen
HR Director: Emily Wong

╔══════════════════════════════════════════════════════════╗
║     FACILITY & CONTACT INFORMATION                      ║
╚══════════════════════════════════════════════════════════╝

Primary facility address:
  Street: 500 Industrial Parkway
  City: Toledo
  State: OH
  ZIP: 43612
  Country [United States]: 

Main phone: (419) 555-0100
Main email: info@acme-mfg.com
Website: https://www.acme-mfg.com

╔══════════════════════════════════════════════════════════╗
║     REGULATORY & COMPLIANCE ENVIRONMENT                 ║
╚══════════════════════════════════════════════════════════╝

Does your company export products internationally? [y/N]: y
  → Will include Export Compliance Program template

Do you handle hazardous chemicals? [Y/n]: y
  → Will include HazCom, EPCRA Tier II templates

Do you generate hazardous waste? [y/N]: n

Do you store oil above SPCC thresholds (1,320+ gallons)? [y/N]: y
  → Will include SPCC Plan template

Do you have permit-required confined spaces? [y/N]: n

Are you ISO 9001 certified or pursuing certification? [Y/n]: y
  → Will include ISO 9001 QMS templates

╔══════════════════════════════════════════════════════════╗
║     BRANDING & PRESENTATION                             ║
╚══════════════════════════════════════════════════════════╝

Primary brand color (hex code) [#D32F2F]: 
Company logo file path [leave blank to set later]: ./logo.png
Document header text [Confidential - Internal Use Only]: 

✓ Constitution created: .DocSpecSpark/constitution.yaml
✓ Installed 40 manufacturing templates
✓ Configured regulatory frameworks (OSHA, EPA, ISO 9001, EAR)
✓ Set up document approval workflows
✓ Ready to create documents!

Next steps:
  $ docspec create policy "Lockout/Tagout Program"
  $ docspec list templates
```

### Constitution Validation

The builder includes validation logic:
- **Required vs optional fields** - Won't proceed without required data
- **Format validation** - Email addresses, phone numbers, tax IDs
- **Conditional logic** - "If exporting → ask for Trade Compliance Officer"
- **Default values** - Pre-fills based on organization type
- **Smart suggestions** - "For manufacturing, we recommend enabling OSHA recordkeeping"

### Update Existing Constitution

```bash
$ docspec update-constitution

Current values shown, press Enter to keep:

Legal company name [Acme Manufacturing Inc.]: 
CEO [John Smith]: Jane Smith    ← Changed
COO [Sarah Johnson]: 
...

✓ Constitution updated
⚠ 12 existing documents reference {{CEO_NAME}}
  Run `docspec refresh-documents` to update them (optional)
```

---

## File Structure

Each company repository contains:

```
.DocSpecSpark/
├── constitution.yaml          # Main configuration file (THIS DOCUMENT)
├── assets/
│   ├── logo.png              # Company logo
│   ├── letterhead.png        # Document header
│   └── signature.png         # Digital signature image
├── templates/
│   ├── company-template.docx # Word reference document
│   └── styles.css            # Web/PDF styling
├── compliance/
│   ├── frameworks/           # Standard frameworks (from DocSpecSpark)
│   │   ├── iso9001.md
│   │   ├── soc2.md
│   │   ├── gdpr.md
│   │   ├── hipaa.md
│   │   └── labor-law.md
│   └── custom/               # Company-specific policies
│       ├── ai-ethics.md
│       └── supplier-code.md
└── workflows/
    └── approval-chains.yaml  # Detailed approval routing
```

---

## Constitution YAML Schema

### Section 1: Company Identity & Legal Structure

```yaml
company:
  # ════════════════════════════════════════════════════════
  # Legal Information
  # ════════════════════════════════════════════════════════
  legal_name: "Acme Manufacturing Inc."
  doing_business_as: null  # Optional DBA/trade name
  legal_entity_type: "C Corporation"  # LLC, S Corp, Partnership, 501(c)(3), etc.
  
  # Registration Details
  state: "Ohio"  # State of incorporation/formation
  jurisdiction: "Ohio, United States"
  tax_id: "12-3456789"  # EIN (Federal Tax ID)
  founded: 2010
  fiscal_year_end: "12/31"  # MM/DD format
  
  # Industry Classification
  industry: "Manufacturing - Industrial Equipment"
  naics_code: "333249"  # For regulatory applicability
  sic_code: "3599"
  employee_count: 95
  annual_revenue: "$15M - $25M"  # Optional
  
  # ════════════════════════════════════════════════════════
  # Governance & Leadership
  # ════════════════════════════════════════════════════════
  governance:
    # For Corporations
    board_chair: "Robert Williams"
    board_chair_email: "rwilliams@acme-mfg.com"
    board_size: 5  # Number of directors
    
    # For Nonprofits (additional fields)
    executive_director: null
    treasurer: null
    secretary: null
    
    # For LLCs
    managing_member: null
    members: []
  
  # ════════════════════════════════════════════════════════
  # Executive Team (Available as {{CEO_NAME}}, {{COO_TITLE}}, etc.)
  # ════════════════════════════════════════════════════════
  executives:
    ceo:
      name: "John Smith"
      title: "Chief Executive Officer"
      email: "jsmith@acme-mfg.com"
      phone: "(419) 555-0101"
    
    coo:
      name: "Sarah Johnson"
      title: "Chief Operating Officer"
      email: "sjohnson@acme-mfg.com"
      phone: "(419) 555-0102"
    
    cfo:
      name: "Michael Lee"
      title: "Chief Financial Officer"
      email: "mlee@acme-mfg.com"
      phone: "(419) 555-0103"
  
  # ════════════════════════════════════════════════════════
  # Key Department Leaders (For template tokens)
  # ════════════════════════════════════════════════════════
  department_heads:
    ehs:
      name: "David Martinez"
      title: "EHS Manager"
      email: "dmartinez@acme-mfg.com"
      certifications: ["CSP", "CHMM"]
    
    quality:
      name: "Lisa Chen"
      title: "Quality Manager"
      email: "lchen@acme-mfg.com"
      certifications: ["CQE", "CQA"]
    
    hr:
      name: "Emily Wong"
      title: "HR Director"
      email: "ewong@acme-mfg.com"
      certifications: ["SHRM-SCP"]
    
    engineering:
      name: "Tom Anderson"
      title: "Engineering Manager"
      email: "tanderson@acme-mfg.com"
    
    it:
      name: "Alex Kim"
      title: "IT Manager"
      email: "akim@acme-mfg.com"
    
    production:
      name: "Carlos Rodriguez"
      title: "Plant Manager"
      email: "crodriguez@acme-mfg.com"
    
    # For export-controlled companies
    trade_compliance:
      name: "Jennifer Park"
      title: "Trade Compliance Officer"
      email: "jpark@acme-mfg.com"
    
    # For nonprofits
    volunteer_coordinator:
      name: null
      title: null
      email: null
  
  # ════════════════════════════════════════════════════════
  # Facilities & Locations
  # ════════════════════════════════════════════════════════
  facilities:
    - id: "main-plant"
      name: "Toledo Main Manufacturing Facility"
      type: "Manufacturing Plant"
      address:
        street: "500 Industrial Parkway"
        city: "Toledo"
        state: "OH"
        zip: "43612"
        country: "United States"
      phone: "(419) 555-0100"
      is_primary: true
      
      # Regulatory identifiers (for EPA/OSHA templates)
      epa_id: "OHD987654321"  # If applicable
      osha_establishment_number: "OH12345"
      
      # Operations characteristics
      operating_hours: "24/7 (3 shifts)"
      square_footage: 85000
      hazardous_chemicals_present: true
      permit_required_confined_spaces: false
      oil_storage_capacity_gallons: 2500  # For SPCC applicability
      
    # Additional facilities (optional)
    - id: "warehouse"
      name: "Distribution Center - Cleveland"
      type: "Warehouse"
      address:
        street: "200 Logistics Blvd"
        city: "Cleveland"
        state: "OH"
        zip: "44101"
        country: "United States"
      is_primary: false
  
  # ════════════════════════════════════════════════════════
  # Primary Contact Information (Headquarters)
  # ════════════════════════════════════════════════════════
  headquarters:
    address:
      street: "500 Industrial Parkway"
      city: "Toledo"
      state: "OH"
      zip: "43612"
      country: "United States"
    
    phone: "(419) 555-0100"
    fax: "(419) 555-0199"
    email: "info@acme-mfg.com"
    website: "https://www.acme-mfg.com"
  
  # ════════════════════════════════════════════════════════
  # Emergency Contacts (For EHS templates)
  # ════════════════════════════════════════════════════════
  emergency_contacts:
    # OSHA Area Office
    osha:
      office: "Toledo Area Office"
      phone: "419-259-7542"
      address: "Federal Office Building, 234 Summit Street, Toledo, OH 43604"
    
    # EPA Region
    epa:
      region: "Region 5 (Midwest)"
      phone: "(312) 353-2000"
      emergency_hotline: "(800) 424-8802"
    
    # Local Emergency Planning Committee
    lepc:
      name: "Lucas County LEPC"
      phone: "(419) 213-4400"
      contact: "Jane Doe, LEPC Coordinator"
    
    # Fire Department
    fire_department:
      name: "Toledo Fire & Rescue"
      station: "Station 7"
      phone: "911"
      non_emergency: "(419) 936-3800"
    
    # Hospital
    hospital:
      name: "ProMedica Toledo Hospital"
      address: "2142 N. Cove Blvd, Toledo, OH 43606"
      phone: "(419) 291-4000"
      emergency_room: "(419) 291-5858"
  
  # ════════════════════════════════════════════════════════
  # External Service Providers (For template references)
  # ════════════════════════════════════════════════════════
  service_providers:
    legal_counsel:
      firm: "Smith & Associates LLP"
      attorney: "Robert Smith, Esq."
      phone: "(419) 555-9000"
      email: "rsmith@smithlaw.com"
    
    accountant:
      firm: "BigFour Accounting LLC"
      cpa: "Maria Garcia, CPA"
      phone: "(614) 555-2000"
      email: "mgarcia@bigfour.com"
    
    insurance_broker:
      firm: "Risk Management Advisors"
      agent: "Tom Johnson"
      phone: "(419) 555-3000"
      policy_number: "WC-123456789"
    
    calibration_lab:
      name: "Precision Calibration Services"
      accreditation: "ISO/IEC 17025"
      phone: "(419) 555-4000"
    
    hazardous_waste_disposal:
      name: "EnviroSafe Waste Management"
      epa_id: "OHD123456789"
      phone: "(800) 555-5000"
    
    background_check_vendor:
      name: "ScreenSafe LLC"
      phone: "(888) 555-6000"
      fcra_compliant: true
```

---

## Template Token Mapping

### How Tokens Work

Every document template in DocSpecSpark contains **replacement tokens** in the format `{{TOKEN_NAME}}`. When a user creates a document from a template, DocSpecSpark automatically replaces these tokens with values from the constitution.

### Token Resolution Path

```
User runs:  $ docspec create procedure "Lockout/Tagout Program"

DocSpecSpark:
  1. Loads .DocSpecSpark/constitution.yaml
  2. Loads .DocSpecSpark/templates/manufacturing/safety-environmental/lockout-tagout-program.md
  3. Scans template for {{TOKENS}}
  4. Replaces each token with constitution value
  5. Creates documents/safety/lockout-tagout-program.md with replaced values
```

### Complete Token Reference

| Token | Constitution Path | Example Value | Used In Templates |
|-------|-------------------|---------------|-------------------|
| `{{COMPANY_NAME}}` | `company.legal_name` | "Acme Manufacturing Inc." | All templates |
| `{{COMPANY_DBA}}` | `company.doing_business_as` | null | Contracts, public docs |
| `{{ENTITY_TYPE}}` | `company.legal_entity_type` | "C Corporation" | Bylaws, resolutions |
| `{{STATE}}` | `company.state` | "Ohio" | All legal documents |
| `{{EIN}}` | `company.tax_id` | "12-3456789" | Tax docs, contracts |
| `{{FISCAL_YEAR_END}}` | `company.fiscal_year_end` | "12/31" | Financial policies |
| `{{INDUSTRY}}` | `company.industry` | "Manufacturing - Industrial Equipment" | Marketing, contracts |
| `{{NAICS_CODE}}` | `company.naics_code` | "333249" | Regulatory filings |
| `{{EMPLOYEE_COUNT}}` | `company.employee_count` | 95 | Handbooks, HR policies |
| `{{FOUNDED_YEAR}}` | `company.founded` | 2010 | About company docs |
| **Governance** |
| `{{BOARD_CHAIR}}` | `company.governance.board_chair` | "Robert Williams" | Bylaws, meeting minutes |
| `{{BOARD_CHAIR_EMAIL}}` | `company.governance.board_chair_email` | "rwilliams@acme-mfg.com" | Contact lists |
| `{{BOARD_SIZE}}` | `company.governance.board_size` | 5 | Bylaws |
| **Executives** |
| `{{CEO_NAME}}` | `company.executives.ceo.name` | "John Smith" | All policy documents |
| `{{CEO_TITLE}}` | `company.executives.ceo.title` | "Chief Executive Officer" | Signature blocks |
| `{{CEO_EMAIL}}` | `company.executives.ceo.email` | "jsmith@acme-mfg.com" | Contact info |
| `{{COO_NAME}}` | `company.executives.coo.name` | "Sarah Johnson" | Operations docs |
| `{{CFO_NAME}}` | `company.executives.cfo.name` | "Michael Lee" | Financial docs |
| **Department Heads** |
| `{{EHS_MANAGER}}` | `company.department_heads.ehs.name` | "David Martinez" | OSHA/EPA programs |
| `{{EHS_MANAGER_EMAIL}}` | `company.department_heads.ehs.email` | "dmartinez@acme-mfg.com" | Safety docs |
| `{{EHS_CERTIFICATIONS}}` | `company.department_heads.ehs.certifications` | ["CSP", "CHMM"] | Professional credentials |
| `{{QUALITY_MANAGER}}` | `company.department_heads.quality.name` | "Lisa Chen" | QMS procedures |
| `{{HR_DIRECTOR}}` | `company.department_heads.hr.name` | "Emily Wong" | HR policies |
| `{{IT_MANAGER}}` | `company.department_heads.it.name` | "Alex Kim" | IT security docs |
| `{{PLANT_MANAGER}}` | `company.department_heads.production.name` | "Carlos Rodriguez" | Production procedures |
| `{{TRADE_COMPLIANCE_OFFICER}}` | `company.department_heads.trade_compliance.name` | "Jennifer Park" | Export compliance |
| **Facilities** |
| `{{FACILITY_NAME}}` | `company.facilities[0].name` | "Toledo Main Manufacturing Facility" | Site-specific docs |
| `{{FACILITY_ADDRESS}}` | `company.facilities[0].address.street` | "500 Industrial Parkway" | Contact info |
| `{{FACILITY_CITY}}` | `company.facilities[0].address.city` | "Toledo" | Address blocks |
| `{{FACILITY_STATE}}` | `company.facilities[0].address.state` | "OH" | State-specific docs |
| `{{FACILITY_ZIP}}` | `company.facilities[0].address.zip` | "43612" | Mailing addresses |
| `{{FACILITY_PHONE}}` | `company.facilities[0].phone` | "(419) 555-0100" | Contact lists |
| `{{EPA_ID}}` | `company.facilities[0].epa_id` | "OHD987654321" | EPA reports |
| `{{OSHA_ESTABLISHMENT_NUMBER}}` | `company.facilities[0].osha_establishment_number` | "OH12345" | OSHA 300 logs |
| `{{OIL_STORAGE_CAPACITY}}` | `company.facilities[0].oil_storage_capacity_gallons` | 2500 | SPCC Plan |
| **Headquarters** |
| `{{HQ_STREET}}` | `company.headquarters.address.street` | "500 Industrial Parkway" | Letterhead |
| `{{HQ_CITY}}` | `company.headquarters.address.city` | "Toledo" | Contact blocks |
| `{{HQ_STATE}}` | `company.headquarters.address.state` | "OH" | All documents |
| `{{HQ_ZIP}}` | `company.headquarters.address.zip` | "43612" | Mailing lists |
| `{{MAIN_PHONE}}` | `company.headquarters.phone` | "(419) 555-0100" | Contact info |
| `{{MAIN_EMAIL}}` | `company.headquarters.email` | "info@acme-mfg.com" | General inquiries |
| `{{WEBSITE}}` | `company.headquarters.website` | "https://www.acme-mfg.com" | Public docs |
| **Emergency Contacts** |
| `{{OSHA_AREA_OFFICE}}` | `company.emergency_contacts.osha.office` | "Toledo Area Office" | Incident reporting |
| `{{OSHA_PHONE}}` | `company.emergency_contacts.osha.phone` | "419-259-7542" | Emergency procedures |
| `{{EPA_REGION}}` | `company.emergency_contacts.epa.region` | "Region 5 (Midwest)" | EPCRA reports |
| `{{EPA_EMERGENCY_HOTLINE}}` | `company.emergency_contacts.epa.emergency_hotline` | "(800) 424-8802" | Spill response |
| `{{LEPC_NAME}}` | `company.emergency_contacts.lepc.name` | "Lucas County LEPC" | Tier II reporting |
| `{{LEPC_PHONE}}` | `company.emergency_contacts.lepc.phone` | "(419) 213-4400" | Emergency contacts |
| `{{FIRE_DEPARTMENT}}` | `company.emergency_contacts.fire_department.name` | "Toledo Fire & Rescue" | Emergency Action Plan |
| `{{HOSPITAL_NAME}}` | `company.emergency_contacts.hospital.name` | "ProMedica Toledo Hospital" | First aid procedures |
| **Service Providers** |
| `{{LEGAL_COUNSEL_FIRM}}` | `company.service_providers.legal_counsel.firm` | "Smith & Associates LLP" | Legal references |
| `{{LEGAL_COUNSEL_ATTORNEY}}` | `company.service_providers.legal_counsel.attorney` | "Robert Smith, Esq." | Document reviews |
| `{{CPA_FIRM}}` | `company.service_providers.accountant.firm` | "BigFour Accounting LLC" | Tax compliance |
| `{{CALIBRATION_LAB}}` | `company.service_providers.calibration_lab.name` | "Precision Calibration Services" | Calibration procedures |
| `{{WASTE_DISPOSAL_VENDOR}}` | `company.service_providers.hazardous_waste_disposal.name` | "EnviroSafe Waste Management" | Hazardous waste program |
| `{{BACKGROUND_CHECK_VENDOR}}` | `company.service_providers.background_check_vendor.name` | "ScreenSafe LLC" | HR screening policy |

### Template Example: Lockout/Tagout Program

**Template file**: `.DocSpecSpark/templates/manufacturing/safety-environmental/lockout-tagout-program.md`

```markdown
---
title: "Lockout/Tagout (LOTO) Energy Control Program"
company: {{COMPANY_NAME}}
facility: {{FACILITY_NAME}}
effective_date: {{CURRENT_DATE}}
owner: {{EHS_MANAGER}}
---

# Lockout/Tagout (LOTO) Energy Control Program

**Company**: {{COMPANY_NAME}}  
**Facility**: {{FACILITY_NAME}}, {{FACILITY_ADDRESS}}, {{FACILITY_CITY}}, {{FACILITY_STATE}} {{FACILITY_ZIP}}  
**Program Owner**: {{EHS_MANAGER}}, {{EHS_MANAGER_TITLE}}  
**Approved By**: {{COO_NAME}}, {{COO_TITLE}}  
**Effective Date**: {{EFFECTIVE_DATE}}

## 1. Purpose and Scope

This Lockout/Tagout (LOTO) program establishes {{COMPANY_NAME}}'s procedures for controlling hazardous energy during servicing and maintenance of machinery and equipment at the {{FACILITY_NAME}}.

## 2. Responsibilities

### 2.1 Management
**{{COO_NAME}}, {{COO_TITLE}}** is responsible for overall program approval and resource allocation.

### 2.2 EHS Manager
**{{EHS_MANAGER}}** is responsible for:
- Program development and updates
- Annual procedure audits
- Training coordination
- LOTO device procurement

Contact: {{EHS_MANAGER_EMAIL}}

### 2.3 Plant Manager
**{{PLANT_MANAGER}}** is responsible for ensuring all maintenance staff are trained and authorized.

## 3. Emergency Contacts

In case of LOTO-related injury:
- **Emergency Services**: 911
- **Facility Emergency Line**: {{FACILITY_PHONE}}
- **EHS Manager (24/7)**: {{EHS_MANAGER_PHONE}}
- **Hospital**: {{HOSPITAL_NAME}}, {{HOSPITAL_PHONE}}

## 4. Training Records

Training coordinated by {{HR_DIRECTOR}}, {{HR_DIRECTOR_TITLE}}.
Training records maintained per {{COMPANY_NAME}} retention policy.

---

**Document Control**  
Owner: {{EHS_MANAGER}}  
Approver: {{COO_NAME}}  
Revision: 1.0  
Review Cycle: Annual
```

**After `docspec create` command**, the generated document becomes:

```markdown
---
title: "Lockout/Tagout (LOTO) Energy Control Program"
company: Acme Manufacturing Inc.
facility: Toledo Main Manufacturing Facility
effective_date: 2026-03-02
owner: David Martinez
---

# Lockout/Tagout (LOTO) Energy Control Program

**Company**: Acme Manufacturing Inc.  
**Facility**: Toledo Main Manufacturing Facility, 500 Industrial Parkway, Toledo, OH 43612  
**Program Owner**: David Martinez, EHS Manager  
**Approved By**: Sarah Johnson, Chief Operating Officer  
**Effective Date**: 2026-03-02

## 1. Purpose and Scope

This Lockout/Tagout (LOTO) program establishes Acme Manufacturing Inc.'s procedures for controlling hazardous energy during servicing and maintenance of machinery and equipment at the Toledo Main Manufacturing Facility.

## 2. Responsibilities

### 2.1 Management
**Sarah Johnson, Chief Operating Officer** is responsible for overall program approval and resource allocation.

### 2.2 EHS Manager
**David Martinez** is responsible for:
- Program development and updates
- Annual procedure audits
- Training coordination
- LOTO device procurement

Contact: dmartinez@acme-mfg.com

### 2.3 Plant Manager
**Carlos Rodriguez** is responsible for ensuring all maintenance staff are trained and authorized.

## 3. Emergency Contacts

In case of LOTO-related injury:
- **Emergency Services**: 911
- **Facility Emergency Line**: (419) 555-0100
- **EHS Manager (24/7)**: (419) 555-0150
- **Hospital**: ProMedica Toledo Hospital, (419) 291-4000

## 4. Training Records

Training coordinated by Emily Wong, HR Director.
Training records maintained per Acme Manufacturing Inc. retention policy.

---

**Document Control**  
Owner: David Martinez  
Approver: Sarah Johnson  
Revision: 1.0  
Review Cycle: Annual
```

### Special Tokens

| Token | Behavior | Example |
|-------|----------|---------|
| `{{CURRENT_DATE}}` | Today's date (YYYY-MM-DD) | 2026-03-02 |
| `{{CURRENT_YEAR}}` | Current year | 2026 |
| `{{DOCUMENT_TITLE}}` | Derived from filename | "Lockout/Tagout Program" |
| `{{VERSION}}` | Auto-incremented (v1.0, v1.1) | v1.0 |
| `{{LAST_UPDATED}}` | Last Git commit date | 2026-03-02 |

---

### Section 2: Compliance Frameworks

```yaml
compliance:
  # Active Frameworks
  active_frameworks:
    - id: "gdpr"
      name: "General Data Protection Regulation"
      version: "2018"
      authority: "European Union"
      applicability: "Processes personal data of EU citizens"
      scope: "All customer-facing applications"
      contact: "dpo@acme.com"
      last_audit: "2025-06-15"
      next_audit: "2026-06-15"
      certification_number: "GDPR-2025-12345"
      
    - id: "hipaa"
      name: "Health Insurance Portability and Accountability Act"
      version: "2013 Omnibus Rule"
      authority: "U.S. Department of Health and Human Services"
      applicability: "Processes Protected Health Information (PHI)"
      scope: "Patient data platform only"
      contact: "compliance@acme.com"
      last_audit: "2025-09-01"
      next_audit: "2026-09-01"
      
    - id: "soc2"
      name: "SOC 2 Type II"
      version: "2017 Trust Services Criteria"
      authority: "AICPA"
      applicability: "Cloud service providers handling customer data"
      scope: "All production systems"
      audit_firm: "BigFour Audit LLP"
      audit_period: "2025-01-01 to 2025-12-31"
      report_date: "2026-01-15"
      certification_number: "SOC2-2025-ACME-001"
      
    - id: "iso9001"
      name: "ISO 9001:2015 Quality Management System"
      version: "2015"
      authority: "International Organization for Standardization"
      applicability: "Quality management across all operations"
      scope: "Product development, customer support"
      certification_body: "ISO Cert International"
      certificate_number: "ISO9001-2025-54321"
      
    - id: "labor-law"
      name: "U.S. Labor Law Compliance"
      version: "Current"
      authority: "U.S. Department of Labor"
      applicability: "All employment practices"
      scope: "HR policies, employee handbooks, workplace safety"
      contact: "hr@acme.com"
  
  # Inactive/Historical Frameworks (completed, no longer applicable)
  inactive_frameworks:
    - id: "pci-dss"
      name: "Payment Card Industry Data Security Standard"
      reason_inactive: "No longer processing credit cards (switched to Stripe)"
      deactivated_date: "2024-03-15"
  
  # Custom Policies (company-specific requirements)
  custom_policies:
    - name: "AI Ethics Policy"
      description: "Internal guidelines for ethical AI development and deployment"
      file: ".DocSpecSpark/compliance/custom/ai-ethics.md"
      mandatory: true
      applies_to: ["policies", "training"]
      
    - name: "Supplier Code of Conduct"
      description: "Requirements for third-party vendors"
      file: ".DocSpecSpark/compliance/custom/supplier-code.md"
      mandatory: false
      applies_to: ["policies"]
  
  # Framework Mappings (cross-references)
  framework_mappings:
    - gdpr_article: "Art. 32 (Security of Processing)"
      maps_to:
        - framework: "soc2"
          control: "CC6.1"
        - framework: "iso9001"
          clause: "7.1.6"
```

### Section 3: Document Governance

```yaml
document_governance:
  # Version Strategy
  version_strategy: "semantic"  # Options: semantic | date-based | sequential
  version_format: "v{MAJOR}.{MINOR}.{PATCH}"  # Example: v1.2.3
  
  # Retention Policy
  retention_policy:
    strategy: "perpetual"  # Options: perpetual | time-based | event-based
    # For time-based: retention_years: 7
    # For event-based: retain_until: "superseded"
    
  # Approval Workflows (by document type)
  approval_workflows:
    policy:
      reviewers:
        - role: "legal"
          required: true
          github_team: "legal-team"
        - role: "compliance"
          required: true
          github_team: "compliance-team"
        - role: "information-security"
          required: false  # Optional reviewer
          github_team: "infosec-team"
      
      approvers:
        - role: "legal-director"
          required: true
          github_team: "legal-leadership"
        - role: "ceo"
          required: true  # CEO must approve all policies
          github_team: "executive-team"
      
      review_cycle: "annual"  # Options: annual | biannual | quarterly | as-needed
      auto_expire: true
      expiration_warning_days: 90
      
    handbook:
      reviewers:
        - role: "hr"
          required: true
          github_team: "hr-team"
        - role: "legal"
          required: true
          github_team: "legal-team"
      
      approvers:
        - role: "hr-director"
          required: true
          github_team: "hr-leadership"
      
      review_cycle: "biannual"
      auto_expire: false
      
    training:
      reviewers:
        - role: "subject-matter-expert"
          required: true
          assigned_per_document: true  # Not a fixed team
        - role: "training-coordinator"
          required: true
          github_team: "learning-development"
      
      approvers:
        - role: "training-director"
          required: true
          github_team: "learning-development"
      
      review_cycle: "as-needed"
      auto_expire: false
  
  # Audit Trail Requirements
  audit_trail:
    require_approval_signature: true
    require_review_comments: true
    track_all_changes: true
    log_access_history: false  # May require separate system
  
  # Notification Settings
  notifications:
    expiration_reminders:
      enabled: true
      recipients: ["document-owner", "approvers"]
      schedule: [90, 60, 30, 14, 7]  # Days before expiration
    
    approval_requests:
      enabled: true
      method: "teams"  # Options: email | teams | slack
      escalation_days: 7  # Escalate if no response
```

### Section 4: Branding & Templates

```yaml
branding:
  # Visual Identity
  company_name_display: "Acme Health"  # How name appears in documents
  tagline: "Innovation in Healthcare Technology"
  
  # Colors (for web app and PDF)
  colors:
    primary: "#003366"    # Dark blue
    secondary: "#0066CC"  # Lighter blue
    accent: "#FF6600"     # Orange
    text: "#333333"
    background: "#FFFFFF"
  
  # Typography
  fonts:
    primary: "Calibri"    # Body text
    headings: "Arial"     # Headings
    monospace: "Consolas" # Code blocks
  
  # Assets
  logo: ".DocSpecSpark/assets/logo.png"
  logo_dark: ".DocSpecSpark/assets/logo-dark.png"  # For dark backgrounds
  letterhead: ".DocSpecSpark/assets/letterhead.png"
  footer_image: ".DocSpecSpark/assets/footer.png"
  
  # Document Templates
  word_template: ".DocSpecSpark/templates/company-template.docx"
  pdf_template: ".DocSpecSpark/templates/company-template.html"  # For Pandoc
  css_stylesheet: ".DocSpecSpark/templates/styles.css"
  
  # Document Header/Footer
  header:
    include_logo: true
    include_company_name: true
    include_document_title: false
    custom_text: "Confidential - Internal Use Only"
  
  footer:
    include_page_numbers: true
    include_version: true
    include_date: true
    custom_text: "© 2026 Acme Corporation. All rights reserved."
```

### Section 5: Document Types & Templates

```yaml
document_types:
  # Define available document types and their properties
  policy:
    display_name: "Policy"
    description: "Company-wide rules and guidelines"
    require_legal_review: true
    require_compliance_review: true
    default_audience: "all-employees"
    default_classification: "internal"
    available_templates:
      - "data-privacy-policy"
      - "information-security-policy"
      - "acceptable-use-policy"
      - "remote-work-policy"
    
  procedure:
    display_name: "Standard Operating Procedure (SOP)"
    description: "Step-by-step instructions for processes"
    require_legal_review: false
    require_compliance_review: true
    default_audience: "relevant-teams"
    default_classification: "internal"
    available_templates:
      - "incident-response-procedure"
      - "data-backup-procedure"
      - "employee-onboarding-procedure"
    
  handbook:
    display_name: "Employee Handbook"
    description: "Comprehensive employment policies and expectations"
    require_legal_review: true
    require_compliance_review: true
    default_audience: "all-employees"
    default_classification: "internal"
    available_templates:
      - "new-employee-handbook"
      - "code-of-conduct"
      - "anti-harassment-policy"
      - "leave-time-off-policy"
    
  training:
    display_name: "Training Material"
    description: "Educational content for employee development"
    require_legal_review: false
    require_compliance_review: true
    default_audience: "trainees"
    default_classification: "internal"
    available_templates:
      - "security-awareness-training"
      - "gdpr-training"
      - "hipaa-training"
      - "harassment-prevention-training"
  
  # Classification Levels
  classification_levels:
    - id: "public"
      description: "Can be shared publicly"
      watermark: null
      
    - id: "internal"
      description: "For employees only"
      watermark: "Internal Use Only"
      
    - id: "confidential"
      description: "Sensitive business information"
      watermark: "Confidential"
      access_control: true
      
    - id: "restricted"
      description: "Highly sensitive (legal, financial, PHI)"
      watermark: "Restricted - Need to Know Only"
      access_control: true
      encryption_required: true
```

### Section 6: Integration Settings

```yaml
integrations:
  # GitHub
  github:
    organization: "acme-corp"
    repository: "docspecspark-acme"
    default_branch: "main"
    require_pull_requests: true
    require_approvals: 2  # For document publication
  
  # SharePoint
  sharepoint:
    enabled: true
    tenant_id: "your-tenant-id"
    site_url: "https://acme.sharepoint.com/sites/policies"
    document_library: "Published Documents"
    sync_strategy: "on-publish"  # Options: on-publish | scheduled | real-time
    
    # Folder structure in SharePoint
    folder_structure: "by-type"  # Options: by-type | by-date | flat
    # by-type: /Policies, /Handbooks, /Training
    # by-date: /2026, /2025
    # flat: all in root
    
    metadata_mapping:
      - sharepoint_field: "DocumentType"
        docspec_field: "document_type"
      - sharepoint_field: "ComplianceFrameworks"
        docspec_field: "compliance.applicable_frameworks"
      - sharepoint_field: "ApprovalStatus"
        docspec_field: "workflow.status"
      - sharepoint_field: "Version"
        docspec_field: "version"
  
  # Microsoft Teams
  teams:
    enabled: true
    team_id: "your-team-id"
    channel_id: "your-channel-id"
    notifications:
      - event: "document_created"
        channel: "general"
      - event: "approval_needed"
        channel: "approvals"
      - event: "document_published"
        channel: "announcements"
  
  # Single Sign-On
  sso:
    provider: "azure-ad"  # Options: azure-ad | okta | auth0
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    # client_secret stored in GitHub Secrets
```

---

## Example Configurations

### Example 1: Small Healthcare Startup (< 50 employees)

```yaml
company:
  legal_name: "HealthTech Innovations Inc."
  industry: "Healthcare Technology"
  employee_count: 35
  
compliance:
  active_frameworks:
    - id: "hipaa"  # Required for healthcare
    - id: "soc2"   # For cloud services
    # No GDPR (US-only customers)
  
document_governance:
  version_strategy: "semantic"
  approval_workflows:
    policy:
      reviewers: ["ceo"]  # Small team, CEO reviews everything
      approvers: ["ceo"]
      review_cycle: "annual"
    handbook:
      reviewers: ["hr-manager"]
      approvers: ["ceo"]
      review_cycle: "as-needed"
  
integrations:
  sharepoint:
    enabled: false  # Using GitHub only
  teams:
    enabled: true
```

### Example 2: Enterprise Financial Services (1000+ employees)

```yaml
company:
  legal_name: "Global Finance Corp"
  industry: "Financial Services"
  employee_count: 1500
  
compliance:
  active_frameworks:
    - id: "soc2"
    - id: "iso9001"
    - id: "iso27001"  # Information security
    - id: "pci-dss"   # Payment processing
    - id: "gdpr"      # International operations
    - id: "labor-law"
  
  custom_policies:
    - name: "Anti-Money Laundering (AML)"
      file: ".DocSpecSpark/compliance/custom/aml.md"
      mandatory: true
    - name: "Know Your Customer (KYC)"
      file: ".DocSpecSpark/compliance/custom/kyc.md"
      mandatory: true
  
document_governance:
  version_strategy: "semantic"
  approval_workflows:
    policy:
      reviewers: ["legal", "compliance", "risk-management", "information-security"]
      approvers: ["legal-counsel", "chief-compliance-officer", "ceo"]
      review_cycle: "biannual"
    handbook:
      reviewers: ["hr", "legal", "compliance"]
      approvers: ["chief-hr-officer", "legal-counsel"]
      review_cycle: "annual"
  
  audit_trail:
    require_approval_signature: true
    require_review_comments: true
    track_all_changes: true
    log_access_history: true  # Required for financial services
  
integrations:
  sharepoint:
    enabled: true
    folder_structure: "by-type"
    sync_strategy: "real-time"
  teams:
    enabled: true
  sso:
    provider: "okta"
```

### Example 3: Tech Company (No Healthcare/Finance)

```yaml
company:
  legal_name: "CloudSoft Technologies LLC"
  industry: "Software Development"
  employee_count: 120
  
compliance:
  active_frameworks:
    - id: "soc2"
    - id: "gdpr"  # EU customers
    - id: "labor-law"
  
  custom_policies:
    - name: "Open Source Policy"
      file: ".DocSpecSpark/compliance/custom/open-source.md"
      mandatory: false
  
document_governance:
  version_strategy: "date-based"
  version_format: "v{YYYY}-{MM}-{DD}"
  
  approval_workflows:
    policy:
      reviewers: ["legal", "engineering-leadership"]
      approvers: ["cto", "ceo"]
      review_cycle: "as-needed"
    handbook:
      reviewers: ["hr", "legal"]
      approvers: ["head-of-people"]
      review_cycle: "annual"
    training:
      reviewers: ["subject-matter-expert"]
      approvers: ["training-coordinator"]
      review_cycle: "as-needed"
  
integrations:
  sharepoint:
    enabled: false
  teams:
    enabled: false
  # Using GitHub only
```

---

## Validation Rules

The DocSpecSpark CLI validates constitution.yaml on initialization:

### Required Fields
- `company.legal_name`
- `company.industry`
- `compliance.active_frameworks` (at least one)
- `document_governance.version_strategy`
- `branding.company_name_display`

### Conditional Requirements
- If `integrations.sharepoint.enabled = true`, require `sharepoint.tenant_id` and `sharepoint.site_url`
- If `document_governance.approval_workflows` defined, require GitHub teams to exist
- If compliance framework requires contact, validate email format

### Auto-Generated Fields
- `company.repository_initialized_date` (set on `docspec init`)
- `company.docspecspark_version` (tracks CLI version used)
- `metadata.last_updated` (updated on constitution changes)

---

## Migration & Updates

### Updating Constitution

```bash
# Validate changes before committing
docspec validate-constitution

# Update compliance frameworks
docspec compliance update gdpr --version 2024

# Add new framework
docspec compliance add pci-dss

# Remove deactivated framework
docspec compliance deactivate soc2 --reason "Audit not renewed"
```

### Schema Versioning

Constitutional schema follows semantic versioning:
- **MAJOR**: Breaking changes (require migration script)
- **MINOR**: New optional fields
- **PATCH**: Clarifications, examples

Current schema version: **v1.0.0**

---

**Status**: Draft for review
**Next Steps**:
1. Validate schema with sample companies
2. Create YAML validation script
3. Build constitution editor in web app
4. Add migration tools for schema updates
