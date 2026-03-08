# Small Business Manufacturing Template Library - DocSpecSpark

## Purpose

This document defines the **small business manufacturing template library** for DocSpecSpark, derived from the comprehensive analysis in [KeyDocuments-SmallBusiness.md](KeyDocuments-SmallBusiness.md).

**Target Organization**: ~100-employee U.S. manufacturing company with CEO/COO/CFO, engineering, HR, and sales departments.

**Design Principle**: Templates are Markdown files with YAML frontmatter, providing a structured starting point that organizations customize for their specific operations, products, and regulatory environment.

---

## Template Organization

Templates are stored in `.DocSpecSpark/templates/` and organized by category:

```
.DocSpecSpark/templates/
├── corporate-governance/    # Corporate formalities and authority
├── safety-environmental/    # OSHA, EPA, EHS programs
├── quality-engineering/     # QMS, change control, production
├── hr-employment/           # Employee management and compliance
├── finance-tax/             # Financial controls and tax compliance
├── commercial-legal/        # Contracts, terms, IP protection
└── it-security/             # Cybersecurity and OT/ICS security
```

---

## Phase 1 MVP Template Set (Small Business Manufacturing Profile)

Based on KeyDocuments-SmallBusiness.md, the **Essential** tier documents become Phase 1 templates:

### Corporate & Governance Templates (4 templates)

#### 1. **Bylaws Template (Corporation) / Operating Agreement Template (LLC)**
- **File**: `corporate-governance/bylaws-template.md` or `corporate-governance/operating-agreement-template.md`
- **Priority**: Essential
- **Purpose**: Defines governance and decision rules (board/owner meetings, voting, authority, officer roles)
- **Sections**:
  - Governance structure (board of directors or member-managed)
  - Officer duties and appointment process
  - Meeting requirements (frequency, quorum, notice, remote participation)
  - Voting procedures and consent resolutions
  - Delegation of authority framework
  - Indemnification provisions
  - Conflict of interest management
  - Amendment process
- **Regulatory Context**: State corporate/LLC law
- **Review Cycle**: Every 1-2 years; after financing/ownership events
- **Placeholders**: `{{ENTITY_NAME}}`, `{{STATE}}`, `{{ENTITY_TYPE}}`, `{{FISCAL_YEAR_END}}`

#### 2. **Board/Owner Meeting Minutes Template**
- **File**: `corporate-governance/meeting-minutes-template.md`
- **Priority**: Essential
- **Purpose**: Evidence of lawful decision-making for major actions (banking, financing, acquisitions, executive appointments)
- **Sections**:
  - Meeting metadata (date, time, location, type)
  - Attendees and quorum verification
  - Approval of previous minutes
  - Reports (CEO, CFO, operations)
  - Resolutions and votes
  - Action items and follow-up
  - Next meeting date
  - Exhibits (authority matrix, capital approvals, etc.)
- **Regulatory Context**: Corporate formalities; lender/auditor diligence
- **Review Cycle**: Each meeting
- **Placeholders**: `{{MEETING_DATE}}`, `{{ATTENDEES}}`, `{{RESOLUTIONS}}`

#### 3. **Delegation of Authority (DoA) Matrix Template**
- **File**: `corporate-governance/delegation-of-authority-matrix.md`
- **Priority**: Essential
- **Purpose**: Formalizes who can sign what; reduces fraud and contract disputes; enables internal controls
- **Sections**:
  - Signatory authority by role (CEO, COO, CFO, VP levels)
  - Approval thresholds by transaction type:
    - Capital expenditures
    - Operating expenses
    - Purchase orders
    - Sales contracts and discounts
    - Employment offers and separations
    - Export licenses and trade compliance approvals
    - Legal settlements
  - Dual approval requirements for high-risk commitments
  - Banking and treasury authorities
  - Real estate and lease authorities
- **Regulatory Context**: Internal control framework; lender covenants
- **Review Cycle**: Quarterly for personnel changes; annually for thresholds
- **Placeholders**: `{{COMPANY_NAME}}`, `{{APPROVAL_THRESHOLDS}}`, `{{SIGNATORIES}}`

#### 4. **Corporate Resolutions Template (Banking, Borrowing, Signing Authority)**
- **File**: `corporate-governance/corporate-resolutions-template.md`
- **Priority**: Essential
- **Purpose**: Board/owner authorization for banking relationships, borrowing, and major contracts
- **Sections**:
  - Banking resolution (account opening, signatories)
  - Borrowing resolution (loan authority, guarantees)
  - Signing authority resolution (contracts, agreements)
  - Officer appointment resolution
  - Certification and attestation
- **Review Cycle**: As needed for major actions
- **Placeholders**: `{{ENTITY_NAME}}`, `{{BANK_NAME}}`, `{{AUTHORIZED_SIGNATORIES}}`, `{{LOAN_AMOUNT}}`

### Safety & Environmental Templates (10 templates)

#### 5. **OSHA Injury & Illness Recordkeeping Procedure (OSHA 300/300A/301)**
- **File**: `safety-environmental/osha-recordkeeping-procedure.md`
- **Priority**: Essential (for covered employers)
- **Purpose**: Maintain required logs and demonstrate compliance readiness
- **Sections**:
  - Scope and applicability
  - Recordable injury/illness determination criteria
  - OSHA 300 Log maintenance procedures
  - OSHA 301 Incident Report requirements
  - OSHA 300A Annual Summary preparation and posting (Feb 1 - Apr 30)
  - Five-year retention requirement
  - Employee access to records
  - Privacy case procedures
  - Roles and responsibilities
- **Regulatory Context**: 29 CFR 1904; OSHA recordkeeping requirements
- **Review Cycle**: Continuous; annual certification
- **Includes**: OSHA form templates (300, 300A, 301), posting checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY_ADDRESS}}`, `{{EHS_MANAGER}}`

#### 6. **Severe Incident Reporting Procedure (OSHA 1904.39)**
- **File**: `safety-environmental/severe-incident-reporting-procedure.md`
- **Priority**: Essential
- **Purpose**: Ensures timely reporting of fatalities and severe injuries; preserves scene integrity
- **Sections**:
  - Reportable events (fatality, inpatient hospitalization, amputation, eye loss)
  - Reporting timelines (8 hours for fatality, 24 hours for severe injury)
  - Reporting method (phone, online portal)
  - Scene preservation and investigation
  - Internal notification and escalation
  - External notification (OSHA, legal, insurance)
  - Documentation requirements
  - Root cause analysis triggers
- **Regulatory Context**: 29 CFR 1904.39
- **Review Cycle**: Annual; after any reportable event
- **Includes**: Incident call tree, reporting checklist, scene preservation protocol
- **Placeholders**: `{{COMPANY_NAME}}`, `{{OSHA_AREA_OFFICE}}`, `{{INCIDENT_RESPONSE_TEAM}}`

#### 7. **Hazard Communication Program (HazCom) + SDS Management**
- **File**: `safety-environmental/hazard-communication-program.md`
- **Priority**: Essential (if hazardous chemicals present)
- **Purpose**: Ensures workers understand chemical hazards; compliance with OSHA HazCom Standard
- **Sections**:
  - Program scope and responsibility
  - Chemical inventory maintenance
  - Safety Data Sheet (SDS) management and accessibility
  - Container labeling requirements (GHS)
  - Employee information and training
  - Hazardous non-routine tasks
  - Contractor chemical notification
  - Multi-employer worksite coordination
- **Regulatory Context**: 29 CFR 1910.1200 (OSHA HazCom Standard)
- **Review Cycle**: Annual; when new chemicals/processes introduced
- **Includes**: Chemical inventory template, SDS index, training checklist, label requirements
- **Placeholders**: `{{COMPANY_NAME}}`, `{{EHS_MANAGER}}`, `{{SDS_LOCATION}}`

#### 8. **Lockout/Tagout (LOTO) Program + Machine-Specific Procedures**
- **File**: `safety-environmental/lockout-tagout-program.md`
- **Priority**: Essential (if servicing exposes workers to hazardous energy)
- **Purpose**: Prevent unintended energization; controls high-severity manufacturing risk
- **Sections**:
  - Program scope and applicability
  - Energy source identification (electrical, mechanical, hydraulic, pneumatic, thermal, chemical)
  - Energy isolation procedures
  - Lockout/tagout device requirements
  - Machine-specific energy control procedures
  - Group lockout procedures
  - Shift change procedures
  - Periodic inspection (annual minimum)
  - Training requirements (authorized, affected, other employees)
  - Contractor coordination
  - Temporary removal and restoration of protection
- **Regulatory Context**: 29 CFR 1910.147 (Control of Hazardous Energy)
- **Review Cycle**: Annual; when equipment changes
- **Includes**: Machine-specific LOTO sheets template, periodic inspection checklist, training records
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY}}`, `{{AUTHORIZED_EMPLOYEES}}`

#### 9. **Permit-Required Confined Space Program**
- **File**: `safety-environmental/confined-space-program.md`
- **Priority**: Situational (Essential if permit spaces exist)
- **Purpose**: Controls confined space entry, atmospheric testing, rescue readiness
- **Sections**:
  - Confined space identification and evaluation
  - Permit-required vs. non-permit spaces
  - Entry permit system
  - Atmospheric testing protocols
  - Ventilation requirements
  - Entry procedures and attendant duties
  - Rescue and emergency services
  - Training requirements
  - Contractor coordination
  - Annual program review
- **Regulatory Context**: 29 CFR 1910.146 (Permit-Required Confined Spaces)
- **Review Cycle**: Annual; after any entry incident
- **Includes**: Entry permit template, atmospheric testing form, rescue drill log
- **Placeholders**: `{{COMPANY_NAME}}`, `{{CONFINED_SPACES_LIST}}`, `{{RESCUE_SERVICE}}`

#### 10. **Emergency Action Plan (EAP)**
- **File**: `safety-environmental/emergency-action-plan.md`
- **Priority**: Essential
- **Purpose**: Organizes actions in emergencies (fire, chemical release, severe weather, active threat)
- **Sections**:
  - Emergency escape procedures and routes
  - Critical operations shutdown procedures
  - Employee accounting procedures
  - Rescue and medical duties
  - Reporting fires and emergencies
  - Emergency contact information
  - Evacuation assembly points
  - Emergency coordinator designation
  - Severe weather procedures
  - Chemical spill response
  - Annual drills and training
- **Regulatory Context**: 29 CFR 1910.38 (Emergency Action Plans)
- **Review Cycle**: Annual; after facility/layout changes
- **Includes**: Evacuation map template, drill checklist, contact roster
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY_ADDRESS}}`, `{{EMERGENCY_COORDINATOR}}`

#### 11. **EPCRA Tier II Chemical Inventory Reporting Procedure**
- **File**: `safety-environmental/epcra-tier-ii-procedure.md`
- **Priority**: Situational (Essential if thresholds met)
- **Purpose**: Community right-to-know compliance; annual hazardous chemical inventory reporting
- **Sections**:
  - Applicability and threshold determination
  - Chemical inventory tracking
  - Tier II form preparation
  - Submission deadlines (March 1 annually)
  - Required recipients (SERC, LEPC, fire department)
  - Chemical mixture calculations
  - Confidential location information (CBI) procedures
  - Recordkeeping requirements
- **Regulatory Context**: EPCRA Sections 311-312 (Emergency Planning and Community Right-to-Know Act)
- **Review Cycle**: Annual (Tier II cycle); continuous inventory updates
- **Includes**: Chemical inventory tracker, Tier II submission checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY_ADDRESS}}`, `{{LEPC_CONTACT}}`

#### 12. **TRI (Toxic Release Inventory) Reporting Procedure**
- **File**: `safety-environmental/tri-reporting-procedure.md`
- **Priority**: Situational (Essential if criteria met)
- **Purpose**: Annual toxic chemical release reporting (Form R)
- **Sections**:
  - Applicability determination (NAICS code, employee threshold, chemical threshold)
  - Covered chemicals list
  - Release and waste management calculations
  - Source reduction and recycling activities
  - Form R preparation workflow
  - Submission deadline (July 1 annually)
  - Certification and attestation
  - Recordkeeping (3 years)
- **Regulatory Context**: EPCRA Section 313 (Toxic Release Inventory)
- **Review Cycle**: Annual
- **Includes**: TRI calculation workbook, submission tracking
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY}}`, `{{TRI_COORDINATOR}}`

#### 13. **Hazardous Waste Management Program**
- **File**: `safety-environmental/hazardous-waste-program.md`
- **Priority**: Situational (Essential if hazardous waste generated)
- **Purpose**: Tracks waste from generation to disposal; maintains RCRA compliance
- **Sections**:
  - Generator status determination (VSQG, SQG, LQG)
  - Hazardous waste identification
  - Accumulation time limits and storage requirements
  - Container labeling and marking
  - Training requirements (annual, job-specific)
  - Manifest system and recordkeeping
  - Contingency plan and emergency procedures
  - Biennial reporting (if LQG)
  - EPA ID number maintenance
- **Regulatory Context**: RCRA (Resource Conservation and Recovery Act); 40 CFR Part 262
- **Review Cycle**: Annual; when processes change
- **Includes**: Waste determination worksheet, manifest tracking log, training records
- **Placeholders**: `{{COMPANY_NAME}}`, `{{EPA_ID_NUMBER}}`, `{{GENERATOR_STATUS}}`

#### 14. **SPCC Plan (Spill Prevention, Control, and Countermeasure)**
- **File**: `safety-environmental/spcc-plan.md`
- **Priority**: Situational (Essential if storing oil above thresholds)
- **Purpose**: Prevent oil discharges to navigable waters; defines controls, inspections, spill response
- **Sections**:
  - Facility description and oil storage capacity
  - Oil discharge history
  - Spill prevention measures
  - Drainage and containment
  - Inspection and testing procedures
  - Personnel training and spill procedures
  - Equipment failure analysis
  - Professional engineer certification (if required)
  - Plan amendments and review (5-year cycle)
- **Regulatory Context**: 40 CFR Part 112 (Oil Pollution Prevention)
- **Review Cycle**: 5-year review cycle; upon facility changes
- **Includes**: Inspection checklist, spill report form
- **Placeholders**: `{{FACILITY_NAME}}`, `{{TOTAL_OIL_CAPACITY}}`, `{{PE_CERTIFICATION}}`

### Quality & Engineering Templates (6 templates)

#### 15. **Document Control Procedure**
- **File**: `quality-engineering/document-control-procedure.md`
- **Priority**: Essential
- **Purpose**: Ensures controlled documents are current, approved, and accessible; prevents use of obsolete documents
- **Sections**:
  - Document types and hierarchy (policy, procedure, work instruction, form, record)
  - Document identification and numbering
  - Creation and approval workflow
  - Review and revision process
  - Distribution and accessibility
  - Obsolete document control
  - External documents (standards, customer specs)
  - Training on document changes
  - Master document list maintenance
- **Regulatory Context**: ISO 9001 documented information control; customer QMS requirements
- **Review Cycle**: Annual
- **Includes**: Document approval form, master document list template, revision history log
- **Placeholders**: `{{COMPANY_NAME}}`, `{{QUALITY_MANAGER}}`, `{{DOCUMENT_REPOSITORY}}`

#### 16. **Engineering Change Control Procedure (ECN/ECO)**
- **File**: `quality-engineering/engineering-change-control-procedure.md`
- **Priority**: Essential
- **Purpose**: Controlled ECN/ECO workflow tied to BOM/drawings/specs; ensures shop builds correct revision
- **Sections**:
  - Change request initiation and classification (emergency, normal, cost reduction)
  - Impact assessment (design, manufacturing, quality, cost, regulatory)
  - Cross-functional review (engineering, manufacturing, quality, purchasing, sales)
  - Approval authorities by change type and cost impact
  - BOM and drawing effectivity
  - Implementation and verification
  - Communication to affected parties (production, suppliers, customers)
  - Change record retention
- **Regulatory Context**: ISO 9001 design control; AS9100 configuration management; customer requirements
- **Review Cycle**: Annual; after quality escapes related to change control
- **Includes**: ECN/ECO request form, impact assessment checklist, approval matrix
- **Placeholders**: `{{COMPANY_NAME}}`, `{{CHANGE_CONTROL_BOARD}}`, `{{ECN_NUMBERING}}`

#### 17. **Calibration Program Procedure**
- **File**: `quality-engineering/calibration-program.md`
- **Priority**: Essential
- **Purpose**: Ensures measurement equipment accuracy and traceability; prevents defects from measurement error
- **Sections**:
  - Equipment identification and master list
  - Calibration frequency determination
  - Calibration methods and standards (NIST-traceable)
  - Out-of-tolerance procedures and product impact assessment
  - Calibration records and labels
  - External calibration lab qualification
  - Handling, storage, and preservation
  - Calibration due date tracking
- **Regulatory Context**: ISO 9001 monitoring and measurement resources; ISO/IEC 17025
- **Review Cycle**: Annual
- **Includes**: Calibration schedule template, out-of-tolerance investigation form, calibration label template
- **Placeholders**: `{{COMPANY_NAME}}`, `{{QUALITY_MANAGER}}`, `{{CALIBRATION_LAB}}`

#### 18. **Production Control Procedure**
- **File**: `quality-engineering/production-control-procedure.md`
- **Priority**: Essential
- **Purpose**: Defines production planning, work order management, material control, and traceability
- **Sections**:
  - Work order creation and release
  - BOM and routing validation
  - Material staging and kitting
  - Production floor control and status tracking
  - First article inspection (FAI) requirements
  - In-process inspection and verification
  - Nonconforming material segregation
  - Lot/serial number traceability (if required)
  - Production records and retention
- **Regulatory Context**: ISO 9001 production and service provision; customer-specific requirements
- **Review Cycle**: Annual; when production system changes
- **Includes**: Work order template, traveler/router template, FAI checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{PRODUCTION_MANAGER}}`, `{{ERP_SYSTEM}}`

#### 19. **Inspection and Test Procedure**
- **File**: `quality-engineering/inspection-test-procedure.md`
- **Priority**: Essential
- **Purpose**: Defines receiving inspection, in-process inspection, and final inspection requirements
- **Sections**:
  - Receiving inspection (raw materials, purchased parts)
  - In-process inspection points and criteria
  - Final inspection and testing
  - Inspection records and stamps/tags
  - Acceptance criteria and sampling plans
  - Inspection equipment and gages
  - Nonconforming product disposition
  - Certificate of Conformance (C of C) requirements
  - Customer-witnessed inspection coordination
- **Regulatory Context**: ISO 9001 monitoring and measurement; customer quality requirements
- **Review Cycle**: Annual
- **Includes**: Inspection report templates, sampling plan table, C of C template
- **Placeholders**: `{{COMPANY_NAME}}`, `{{QUALITY_MANAGER}}`, `{{INSPECTION_CRITERIA}}`

#### 20. **Nonconforming Material Control Procedure**
- **File**: `quality-engineering/nonconforming-material-control.md`
- **Priority**: Essential
- **Purpose**: Segregates, evaluates, and dispositions nonconforming product; prevents unintended use
- **Sections**:
  - Nonconformance identification and tagging
  - Segregation and containment
  - Nonconformance report (NCR) generation
  - Root cause analysis
  - Disposition options (rework, scrap, use-as-is, return to supplier)
  - Disposition approval authorities
  - Customer notification (MRB process if applicable)
  - Corrective action linkage
  - Nonconformance trending and analysis
- **Regulatory Context**: ISO 9001 control of nonconforming outputs; AS9100 requirements
- **Review Cycle**: Annual
- **Includes**: NCR form template, MRB approval checklist, disposition flowchart
- **Placeholders**: `{{COMPANY_NAME}}`, `{{QUALITY_MANAGER}}`, `{{MRB_AUTHORITY}}`

### HR & Employment Templates (8 templates)

#### 21. **Employee Handbook**
- **File**: `hr-employment/employee-handbook.md`
- **Priority**: Essential
- **Purpose**: Sets employment policies, reduces legal risk, standardizes conduct expectations
- **Sections**:
  - Welcome and company mission
  - Equal Employment Opportunity (EEO) and nondiscrimination
  - Harassment prevention and complaint process
  - Wage and hour policies (timekeeping, overtime, meal/rest breaks)
  - Leave policies (PTO, sick, FMLA, state leave, military, bereavement)
  - Benefits overview
  - Workplace safety and incident reporting
  - Performance management and discipline
  - Confidentiality and intellectual property
  - Technology and social media use
  - Drug and alcohol policy
  - Workplace violence prevention
  - Grievance procedures
  - Acknowledgment form
- **Regulatory Context**: Federal and state employment law; OSHA recordkeeping intersection
- **Review Cycle**: At least annual (state-specific updates frequent)
- **Placeholders**: `{{COMPANY_NAME}}`, `{{STATE}}`, `{{HR_CONTACT}}`, `{{BENEFITS_SUMMARY}}`

#### 22. **Job Description Template (Manufacturing Roles)**
- **File**: `hr-employment/job-description-template.md`
- **Priority**: Essential
- **Purpose**: Defines duties, qualifications, physical demands, safety responsibilities
- **Sections**:
  - Job title and department
  - Reports to
  - FLSA classification (exempt/non-exempt)
  - Summary and essential functions
  - Required qualifications (education, experience, certifications)
  - Physical requirements and working conditions
  - Safety responsibilities and PPE requirements
  - Equipment and tools used
  - Performance standards
  - Required training (OSHA, quality, technical)
- **Regulatory Context**: ADA (essential functions), FLSA (exempt/non-exempt), OSHA (safety training)
- **Review Cycle**: Annual; when roles change
- **Placeholders**: `{{JOB_TITLE}}`, `{{DEPARTMENT}}`, `{{SUPERVISOR}}`, `{{FLSA_STATUS}}`

#### 23. **Offer Letter Template**
- **File**: `hr-employment/offer-letter-template.md`
- **Priority**: Essential
- **Purpose**: Establishes employment terms, at-will status (where applicable), IP/confidentiality acknowledgments
- **Sections**:
  - Position title and start date
  - Compensation (salary/hourly rate)
  - Benefits eligibility
  - Work schedule and location
  - At-will employment statement (state-specific)
  - Contingencies (background check, drug screen, I-9 verification)
  - Confidentiality and IP assignment
  - Handbook acknowledgment
  - Acceptance signature line
- **Review Cycle**: Annual; with law/benefit changes
- **Placeholders**: `{{CANDIDATE_NAME}}`, `{{POSITION}}`, `{{START_DATE}}`, `{{COMPENSATION}}`, `{{STATE}}`

#### 24. **Background Check Policy + FCRA Compliance**
- **File**: `hr-employment/background-check-policy.md`
- **Priority**: Important (Essential for certain roles)
- **Purpose**: Standardizes screening; ensures FCRA compliance when using consumer reports
- **Sections**:
  - Scope and applicability (positions requiring background checks)
  - Types of checks (criminal, credit, motor vehicle, employment verification)
  - Pre-adverse action process (disclosure, authorization, notice)
  - Adverse action process (individualized assessment, final notice)
  - Recordkeeping and confidentiality
  - Vendor selection and oversight
  - State and local ban-the-box considerations
- **Regulatory Context**: Fair Credit Reporting Act (FCRA); state-specific laws
- **Review Cycle**: Annual
- **Includes**: FCRA disclosure form, authorization form, adverse action notice templates
- **Placeholders**: `{{COMPANY_NAME}}`, `{{SCREENING_VENDOR}}`, `{{HR_CONTACT}}`

#### 25. **Form I-9 Compliance Procedure**
- **File**: `hr-employment/form-i9-procedure.md`
- **Priority**: Essential
- **Purpose**: Employment eligibility verification and compliance evidence
- **Sections**:
  - Form I-9 completion timing (Section 1 by day 1, Section 2 within 3 days)
  - Acceptable documents (List A, B, C)
  - Remote verification procedures (if applicable)
  - Reverification for expiring work authorization
  - Retention requirements (3 years after hire or 1 year after termination, whichever later)
  - Storage and security (separate from personnel files)
  - Internal audits
  - E-Verify procedures (if enrolled)
  - ICE audit response
- **Regulatory Context**: USCIS Form I-9 requirements; INA anti-discrimination provisions
- **Review Cycle**: Annual internal audit
- **Includes**: I-9 completion checklist, retention tracker, audit checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{HR_MANAGER}}`, `{{E_VERIFY_STATUS}}`

#### 26. **Payroll and Timekeeping Recordkeeping Procedure**
- **File**: `hr-employment/payroll-timekeeping-records.md`
- **Priority**: Essential
- **Purpose**: Wage/hour compliance evidence; supports FLSA requirements
- **Sections**:
  - Timekeeping system and approval workflow
  - Required records (personal info, hours worked, wages paid, deductions)
  - Overtime calculation and approval
  - Meal and rest period tracking (state-specific)
  - Recordkeeping retention (3 years minimum)
  - Payroll register maintenance
  - Pay stub requirements
  - Wage payment timing (state-specific)
  - Final paycheck procedures
- **Regulatory Context**: FLSA recordkeeping requirements; state wage/hour laws
- **Review Cycle**: Annual retention audit
- **Placeholders**: `{{COMPANY_NAME}}`, `{{PAYROLL_SYSTEM}}`, `{{STATE}}`

#### 27. **Benefits Plan Summary Plan Descriptions (SPD) Template**
- **File**: `hr-employment/benefits-spd-template.md`
- **Priority**: Important (Essential if ERISA plans exist)
- **Purpose**: Required disclosure of benefits, rights, and obligations
- **Sections**:
  - Plan information (name, type, plan number, plan year)
  - Eligibility and enrollment
  - Benefits covered (coverage levels, deductibles, limits)
  - Claims procedures
  - Appeals process
  - COBRA continuation coverage rights
  - Plan amendment and termination rights
  - ERISA rights statement
  - Plan administrator contact information
- **Regulatory Context**: ERISA Section 104(b); 29 CFR 2520.102-3
- **Review Cycle**: At least annually; on plan changes (SMM required)
- **Includes**: SPD distribution tracking, SMM template
- **Placeholders**: `{{COMPANY_NAME}}`, `{{PLAN_NAME}}`, `{{PLAN_ADMIN}}`, `{{PLAN_YEAR}}`

#### 28. **Training Records Management Procedure**
- **File**: `hr-employment/training-records-procedure.md`
- **Priority**: Essential
- **Purpose**: Evidence of required training (OSHA, quality, technical); supports competency
- **Sections**:
  - Training needs assessment (by role and regulatory requirement)
  - Training matrix (role × required training)
  - Training delivery and documentation
  - Competency evaluation
  - Training records retention
  - New hire orientation training
  - OSHA-required training tracking (HazCom, LOTO, PPE, forklift, etc.)
  - Quality system training
  - Retraining and refresher requirements
  - Training effectiveness evaluation
- **Regulatory Context**: OSHA training requirements; ISO 9001 competence
- **Review Cycle**: Quarterly
- **Includes**: Training matrix template, attendance log, competency sign-off form
- **Placeholders**: `{{COMPANY_NAME}}`, `{{TRAINING_COORDINATOR}}`, `{{LMS_SYSTEM}}`

### Finance & Tax Templates (3 templates)

#### 29. **Financial Policies and Procedures Manual**
- **File**: `finance-tax/financial-policies-procedures.md`
- **Priority**: Essential
- **Purpose**: Consolidates financial controls, approval authorities, accounting policies
- **Sections**:
  - Delegation of financial authority (aligned to DoA matrix)
  - Budget development and approval
  - Purchase order and procurement procedures
  - Accounts payable and disbursements
  - Accounts receivable and collections
  - Cash handling and bank reconciliation
  - Credit card policies
  - Expense reimbursement
  - Capital expenditure approval
  - Inventory valuation and controls
  - Fixed asset management
  - Segregation of duties
  - Month-end/year-end close procedures
  - Internal audit schedule
- **Regulatory Context**: GAAP; internal control frameworks (COSO); lender covenants
- **Review Cycle**: Annual; after audit findings
- **Placeholders**: `{{COMPANY_NAME}}`, `{{CFO}}`, `{{APPROVAL_THRESHOLDS}}`, `{{FISCAL_YEAR_END}}`

#### 30. **Tax Compliance Calendar and Filing Procedure**
- **File**: `finance-tax/tax-compliance-calendar.md`
- **Priority**: Essential
- **Purpose**: Ensures accurate and timely filing; supports tax positions
- **Sections**:
  - Federal corporate income tax (Form 1120 or 1120S)
  - State corporate income tax (state-specific)
  - Federal payroll taxes (940, 941/944)
  - State unemployment and payroll taxes
  - Sales and use tax (if applicable)
  - Property tax
  - Estimated tax payments
  - Extension procedures
  - Tax position documentation
  - Recordkeeping and retention (7 years minimum)
  - External CPA coordination
- **Review Cycle**: Annual; quarterly for estimated payments
- **Includes**: Tax calendar template, filing checklist, document retention schedule
- **Placeholders**: `{{COMPANY_NAME}}`, `{{TAX_YEAR_END}}`, `{{CPA_FIRM}}`, `{{STATES}}`

#### 31. **Permits and Compliance Obligations Register**
- **File**: `finance-tax/permits-compliance-register.md`
- **Priority**: Essential
- **Purpose**: Authoritative list of all permits/registrations and reporting deadlines
- **Sections**:
  - Environmental permits (air, water, waste, SPCC)
  - Building and fire permits
  - Business licenses (state, local)
  - Professional licenses
  - Export licenses (if applicable)
  - Permit renewal deadlines
  - Operating constraints and conditions
  - Required records and reporting
  - Permit custodians and responsibility matrix
  - Annual compliance review
- **Regulatory Context**: State/local/federal permit requirements (highly variable)
- **Review Cycle**: Quarterly
- **Includes**: Permit tracking spreadsheet, renewal checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{FACILITY_ADDRESS}}`, `{{COMPLIANCE_OFFICER}}`

### Commercial & Legal Templates (4 templates)

#### 32. **Export Compliance Program (ECP/ICP)**
- **File**: `commercial-legal/export-compliance-program.md`
- **Priority**: Situational (Essential if exporting)
- **Purpose**: Prevent unauthorized exports; standardizes classification, license determination, recordkeeping
- **Sections**:
  - Management commitment and resources
  - Risk assessment (products, countries, end users)
  - Export authorization process (ECCN/CCL classification)
  - Restricted party screening (SDN, Entity List, Denied Persons)
  - License determination and application
  - Recordkeeping (5 years minimum)
  - Training (initial and annual)
  - Audits and compliance testing
  - Corrective actions and self-disclosure
  - Red flag procedures
- **Regulatory Context**: Export Administration Regulations (EAR); BIS Eight Elements guidance
- **Review Cycle**: Semi-annual; after rule changes or violations
- **Includes**: Classification worksheet, screening checklist, training records
- **Placeholders**: `{{COMPANY_NAME}}`, `{{TRADE_COMPLIANCE_OFFICER}}`, `{{PRODUCTS}}`

#### 33. **Standard Terms and Conditions (Sales)**
- **File**: `commercial-legal/sales-terms-conditions.md`
- **Priority**: Essential
- **Purpose**: Defines default contract terms; limits liability; protects IP
- **Sections**:
  - Offer and acceptance
  - Price and payment terms
  - Delivery terms (Incoterms)
  - Title and risk of loss
  - Warranties (express and implied limitations)
  - Limitation of liability
  - Intellectual property ownership
  - Confidentiality
  - Export compliance obligations
  - Dispute resolution and governing law
  - Force majeure
  - Cancellation and returns
- **Review Cycle**: Annual; when products/risks change
- **Placeholders**: `{{COMPANY_NAME}}`, `{{PAYMENT_TERMS}}`, `{{WARRANTY_PERIOD}}`, `{{JURISDICTION}}`

#### 34. **Purchase Order Terms and Conditions**
- **File**: `commercial-legal/purchase-order-terms.md`
- **Priority**: Essential
- **Purpose**: Defines supplier obligations, quality requirements, warranties
- **Sections**:
  - Acceptance and order changes
  - Price and payment terms
  - Delivery schedules and penalties
  - Quality and inspection rights
  - Supplier warranties
  - Nonconforming goods and returns
  - Intellectual property and confidentiality
  - Compliance with laws (labor, environmental, export)
  - Right to audit
  - Termination for convenience and cause
- **Review Cycle**: Annual
- **Placeholders**: `{{COMPANY_NAME}}`, `{{PAYMENT_TERMS}}`, `{{QUALITY_STANDARDS}}`

#### 35. **Confidentiality/NDA Template**
- **File**: `commercial-legal/nda-template.md`
- **Priority**: Important
- **Purpose**: Protects proprietary information in customer/supplier/partner relationships
- **Sections**:
  - Definition of confidential information
  - Obligations of receiving party
  - Exclusions (public domain, prior knowledge, independent development)
  - Term and survival
  - Return or destruction of materials
  - No license or rights granted
  - Remedies for breach
  - Governing law and jurisdiction
- **Review Cycle**: As needed for new relationships
- **Placeholders**: `{{COMPANY_NAME}}`, `{{COUNTERPARTY}}`, `{{TERM}}`, `{{JURISDICTION}}`

### IT & Cybersecurity Templates (5 templates)

#### 36. **Cybersecurity Policy (NIST CSF 2.0 Aligned)**
- **File**: `it-security/cybersecurity-policy.md`
- **Priority**: Essential
- **Purpose**: Establishes cybersecurity governance and controls; aligns to NIST CSF 2.0
- **Sections**:
  - Scope and applicability (IT and OT environments)
  - Roles and responsibilities (CISO, IT manager, users)
  - Asset inventory and management
  - Access controls and authentication (MFA, least privilege)
  - Data classification and protection
  - Network security (firewalls, segmentation, OT/IT separation)
  - Vulnerability management and patching
  - Incident response procedures
  - Business continuity and disaster recovery
  - Third-party risk management
  - Security awareness training
  - Compliance monitoring and audits
- **Regulatory Context**: NIST Cybersecurity Framework 2.0; customer requirements
- **Review Cycle**: Annual; after cyber events
- **Placeholders**: `{{COMPANY_NAME}}`, `{{IT_MANAGER}}`, `{{INCIDENT_RESPONSE_TEAM}}`

#### 37. **Incident Response Plan**
- **File**: `it-security/incident-response-plan.md`
- **Priority**: Essential
- **Purpose**: Defines detection, response, containment, recovery, and lessons learned for cyber incidents
- **Sections**:
  - Incident definition and classification (severity levels)
  - Incident response team (roles and contact info)
  - Detection and reporting procedures
  - Initial triage and assessment
  - Containment strategies
  - Eradication and recovery
  - Communication plan (internal, customers, law enforcement, media)
  - Evidence preservation and forensics
  - Post-incident review and lessons learned
  - Regulatory breach notification (if applicable)
- **Regulatory Context**: NIST SP 800-61; state breach notification laws
- **Review Cycle**: Annual; after incidents
- **Includes**: Incident classification matrix, incident log template, communication templates
- **Placeholders**: `{{COMPANY_NAME}}`, `{{IR_TEAM}}`, `{{NOTIFICATION_THRESHOLDS}}`

#### 38. **Business Continuity and Disaster Recovery Plan**
- **File**: `it-security/business-continuity-disaster-recovery.md`
- **Priority**: Essential
- **Purpose**: Ensures critical operations can continue/recover after disruptions
- **Sections**:
  - Business impact analysis (critical processes, RTOs, RPOs)
  - Continuity strategies by scenario (IT failure, facility loss, pandemic, supply chain)
  - Backup procedures and testing
  - Disaster recovery procedures (IT systems, data restoration)
  - Alternate work locations
  - Communication and notification
  - Roles and responsibilities
  - Plan activation and decision criteria
  - Annual testing and tabletop exercises
  - Plan maintenance and updates
- **Regulatory Context**: NIST SP 800-34; customer requirements; lender expectations
- **Review Cycle**: Annual; after tests or actual events
- **Includes**: BIA template, DR runbook, test checklist
- **Placeholders**: `{{COMPANY_NAME}}`, `{{CRITICAL_SYSTEMS}}`, `{{RTO}}`, `{{RPO}}`

#### 39. **OT/ICS Security Procedure**
- **File**: `it-security/ot-ics-security.md`
- **Priority**: Important (Essential for connected manufacturing systems)
- **Purpose**: Secures operational technology and industrial control systems; addresses IT/OT convergence risks
- **Sections**:
  - OT asset inventory (PLCs, HMIs, SCADA, robots)
  - Network segmentation (IT/OT separation, DMZ)
  - Access controls (physical and logical)
  - OT-specific patching and change management
  - Remote access security (VPN, MFA)
  - Monitoring and anomaly detection
  - Incident response for OT environments
  - Vendor and contractor access
  - Backup and recovery for control systems
  - Safety system integrity
- **Regulatory Context**: NIST OT security guidance; ICS-CERT advisories
- **Review Cycle**: Annual; when OT systems change
- **Placeholders**: `{{COMPANY_NAME}}`, `{{OT_SYSTEMS}}`, `{{IT_OT_BOUNDARIES}}`

#### 40. **Acceptable Use Policy (IT Systems)**
- **File**: `it-security/acceptable-use-policy.md`
- **Priority**: Essential
- **Purpose**: Defines appropriate use of company IT resources; reduces security and liability risks
- **Sections**:
  - Scope (email, internet, devices, networks)
  - Acceptable use standards
  - Prohibited activities (personal business, illegal content, malware)
  - Password management and MFA requirements
  - Data handling and confidentiality
  - Personal use of company resources
  - Remote work and BYOD
  - Monitoring and privacy expectations
  - Violations and consequences
  - Acknowledgment requirement
- **Review Cycle**: Annual
- **Placeholders**: `{{COMPANY_NAME}}`, `{{IT_CONTACT}}`, `{{MONITORING_DISCLOSURE}}`

---

## Template Metadata Schema

Each template includes consistent YAML frontmatter:

```yaml
---
title: "Template Name"
category: "corporate-governance | safety-environmental | quality-engineering | hr-employment | finance-tax | commercial-legal | it-security"
priority: "essential | important | situational"
version: "1.0"
effective_date: "YYYY-MM-DD"
review_cycle: "annual | semi-annual | quarterly | continuous | as-needed"
applicable_regulations: ["OSHA 1910.147", "29 CFR 1904", "ISO 9001", "NIST CSF 2.0"]
owner: "CEO | COO | CFO | EHS Manager | Quality Manager | HR Manager | IT Manager"
approved_by: "Board | CEO | Management Team"
approval_date: "YYYY-MM-DD"
supersedes: "None | Previous version reference"
related_documents: ["List of related policies/procedures"]
state_specific: true/false  # Flags templates requiring state customization
---
```

---

## Situational Templates (Not Phase 1 MVP)

These are **Phase 2+ ideas** based on operations triggers:

### Aerospace/Defense
- **AS9100 Quality Management System Manual**
- **ITAR Compliance Program**
- **First Article Inspection (FAI) Procedure (AS9102)**

### Medical Devices
- **FDA 21 CFR Part 820 QMS Manual**
- **Design History File (DHF) Procedure**
- **Medical Device Reporting (MDR) Procedure**

### Food Manufacturing
- **HACCP Plan Template**
- **Food Safety Plan (FSMA)**
- **Allergen Control Program**

---

## Phase 1 MVP Summary

**Total Templates for Small Business Manufacturing Profile: 40**

Distribution:
- Corporate & Governance: 4 templates
- Safety & Environmental: 10 templates
- Quality & Engineering: 6 templates
- HR & Employment: 8 templates
- Finance & Tax: 3 templates
- Commercial & Legal: 4 templates
- IT & Cybersecurity: 5 templates

**All 40 templates are derived from the "Essential" and high-priority "Important" tiers** identified in KeyDocuments-SmallBusiness.md for a ~100-employee manufacturing company.

---

## Implementation Notes

### Template Customization Process

```bash
# User creates document from template
$ docspec create procedure "Lockout/Tagout Program"

# CLI prompts for placeholders
Company name: Acme Manufacturing
Facility: Main Plant - Toledo, OH
EHS Manager: Jane Smith

# CLI generates:
# documents/safety/lockout-tagout-program.md
# Pre-filled with metadata and placeholder values
# User edits in Markdown editor to add machine-specific procedures
```

### State-Specific Customization

Templates flagged `state_specific: true` prompt for state during creation:
- Employee Handbook (state wage/hour, leave laws)
- Background Check Policy (ban-the-box, credit check restrictions)
- At-Will Employment Language (Montana exception)
- Payroll Procedures (state tax withholding, wage payment timing)

### Compliance Validation (Phase 2 Idea)

Future compliance engine would:
- Check OSHA recordkeeping completeness (300 log entries, annual summary posting)
- Validate engineering change control references match BOM/drawing revision
- Flag missing required training for roles (LOTO authorized persons, forklift operators)
- Warn about permit expiration dates

### Template Updates

When DocSpecSpark publishes updated templates:
```bash
$ docspec update
Found regulatory change: OSHA updates to HazCom Standard
Updated template: hazard-communication-program.md (v1.0 → v1.1)

✓ Updated template in .DocSpecSpark/templates/
✓ Your existing documents are NOT changed
✓ Review change log: .DocSpecSpark/CHANGELOG.md

To apply updates to existing documents: Manual review recommended
```

---

## Sources and Alignment

This template library is **directly aligned** with:

1. **KeyDocuments-SmallBusiness.md** - Comprehensive manufacturing compliance analysis
2. **OSHA Standards** - 29 CFR 1910 (General Industry), 29 CFR 1904 (Recordkeeping)
3. **EPA Regulations** - EPCRA, RCRA, CWA (SPCC), CAA
4. **ISO 9001:2015** - Quality management systems
5. **NIST Cybersecurity Framework 2.0** - Cybersecurity governance
6. **Export Administration Regulations (EAR)** - BIS Eight Elements guidance
7. **FLSA, FMLA, ERISA** - Federal employment and benefits law
8. **COSO Internal Control Framework** - Financial controls

---

*This template library represents Phase 1 MVP scope for small business manufacturing. Additional templates (AS9100, ITAR, FDA QSR, HACCP) are future ideas based on industry-specific triggers.*
