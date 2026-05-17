---
title: "Chapter 5: The Project Constitution"
part: "Part II: The Core Workflow"
---

# Chapter 5: The Project Constitution

## The Constitution as Institutional Memory

Software teams develop principles over time through hard experience. The security requirement that says "no hardcoded credentials" exists because someone once hardcoded a credential and it went badly. The testing requirement that says "no mocking the database in integration tests" exists because the team got burned when mocked tests passed but the production migration failed. The architectural principle that says "UI components must not access the database directly" exists because someone violated it once and it took two sprints to untangle.

These principles are institutional memory. They exist in the codebase, in team culture, and — most often — in people's heads. When a senior developer leaves, some of that memory leaves with them. When a new developer joins, they learn the hard way what the principles are.

The DevSpark constitution externalizes this institutional memory into a format that AI coding assistants can read, reference, and enforce. An AI agent that reads your constitution knows the principles before it writes a single line. An AI reviewer that reads your constitution can check code against the same standards a senior developer would apply.

This is the fundamental value of the constitution: it converts implicit team knowledge into explicit, machine-readable governance.

## Constitution Structure

On a project I worked on in 2022 — a GraphQL migration for a mid-sized fintech team of seven — I needed a way to keep both the AI agents and the human reviewers working from the same rulebook. What emerged from that project had three sections: principles (the non-negotiables), rationale (the Why behind each one), and governance (how we enforce and change them). That structure forced a kind of clarity I hadn't anticipated. Each section had to answer a different question. Principles answered *what*. Rationale answered *why this, not something else*. Governance answered *who decides when we're wrong*.

I've found this three-section model works because it separates concerns that teams routinely collapse together. When you write a principle without rationale, you get rules that feel arbitrary to new team members — and to AI agents, which have no ambient context to fill in the gaps. When you write rationale without explicit governance, the constitution becomes advisory rather than authoritative. The three sections hold each other honest.

### Principles

On that same project, I structured each principle with three layers: what's non-negotiable (MUST), what I recommend (SHOULD), and what's permitted (MAY). This vocabulary forced the team to distinguish between hard constraints and strong guidance — a distinction that mattered every time we reviewed a PR. If someone filed a MUST violation, the PR was blocked. If they filed a SHOULD violation, it was a conversation. Without that explicit distinction, I've watched teams treat everything as equally urgent, which means nothing is.

I've learned that strong principles share three properties, and each one is worth understanding on its own terms.

The first is specificity. "No bad code" is useless as a standard, but "SQL queries MUST use parameterized statements" can be checked in code review and flagged by a linter. On a project before the fintech work, we adopted a constitution that included "write clean, maintainable code" as a principle. It became decoration within a month because no two people agreed on what it meant. The moment I replaced it with measurable constraints — function length limits, file size caps, explicit nesting limits — the conversation in PR review changed. Reviewers stopped arguing about taste and started pointing at lines.

The second is visible rationale. When the reasoning isn't obvious, leaving it out invites the team to invent their own — usually wrong — explanation. I've noticed that principles without Why sections get quietly circumvented, not because developers are lazy but because they can't evaluate whether their situation is an exception. When the constitution says "Integration tests MUST NOT mock the database — use a test database instance" and then explains *why* (mocking hides schema and query incompatibilities until production), a developer facing a slow CI pipeline knows they can't trade correctness for speed. The Why section is where the institutional memory actually lives.

The third is the MUST/SHOULD distinction. I've watched teams overload MUST until it covers 80% of their requirements. At that point, the PR review tool flags constant CRITICAL violations and the signal collapses. A useful test I apply: if I would approve a PR that violates this requirement given strong enough other merits, it's a SHOULD, not a MUST. Reserve MUST for the things you would actually block a PR over, regardless of context.

The following is adapted from the constitution we built on the fintech project. I've preserved the structure and two principles that exist specifically because of failures we'd already lived through.

```markdown
# Meridian API Constitution
# Version: 1.4.0 | Ratified: 2022-03-10 | Last Amended: 2022-11-02
# Team: 7 engineers | Stack: Node.js, GraphQL, PostgreSQL

## Core Principles

### I. Security First (MANDATORY)

All security requirements in this section are non-negotiable. A PR that violates
any MUST requirement in this section will not be approved regardless of other merits.

- No hardcoded secrets, credentials, or API keys in source code (MUST)
  *Why: In March 2022, a developer committed an AWS access key directly to the
  repository. The key was exposed in GitHub's public search index within six hours.
  We rotated credentials and audited access, but the incident cost two days and
  nearly a compliance violation. This principle exists because of that specific event.*
- All user-supplied input MUST be validated before processing
- SQL queries MUST use parameterized statements or an ORM that handles parameterization
- Authentication MUST use an established library — no hand-rolled authentication logic
- Error messages returned to clients MUST NOT expose internal stack traces or database details
  *Why: In a 2021 incident on a predecessor project, error responses were leaking
  Postgres query strings to API consumers. A security researcher reported it.
  We were lucky it wasn't reported differently.*
- Rate limiting MUST be applied to all authentication and data-write endpoints

### II. Test-First Development (MANDATORY)

- Tests MUST be written before the implementation they verify (Red-Green-Refactor)
  *Why: Writing tests first forces you to think about the interface before the implementation.*
- Test files MUST exist for every production source file
- Unit test coverage MUST meet or exceed 80% line coverage
- Integration tests MUST NOT mock the database — use a test database instance
  *Why: We added this after a migration passed all mocked tests and then broke
  production within twenty minutes of deploy. The mocks didn't know about a schema
  constraint we'd added two weeks earlier. This was a SHOULD before that incident;
  it became a MUST the same day.*
- All public API endpoints MUST have at least one integration test covering the happy path
  and one covering a validation failure

### III. Code Quality

- Functions MUST NOT exceed 50 lines (excluding comments and blank lines)
  *Why: Functions that exceed this limit almost always have multiple responsibilities.*
- Files MUST NOT exceed 500 lines
- Maximum nesting depth: 4 levels (SHOULD — justified exceptions are permitted)
- All public APIs, exported functions, and exported types MUST have documentation comments
- No `console.log`, `print`, or equivalent debug output in production code (MUST NOT)
  *Why: Debug output in production leaks implementation details and pollutes logs.*
- No `// TODO` comments in code submitted for production (SHOULD NOT)
  Open TODOs belong in the issue tracker, not in merged code.

### IV. Architecture

- UI components MUST NOT access the database directly
  All data access MUST go through the service layer
- HTTP handlers MUST NOT contain business logic
  Business logic belongs in service classes or domain functions
- Dependencies MUST be injected, not created inside functions
  *Why: Internal creation makes unit testing impossible without mocking internals.*

### V. Documentation

- Every significant architectural decision MUST be recorded as an ADR
  in `.documentation/decisions/`
- The CHANGELOG MUST be updated in every release PR
- New dependencies MUST be documented with their purpose and the reason they
  were chosen over alternatives
```

### Governance Section

The governance section is where the constitution becomes self-sustaining. Without it, the document is a policy. With it, it's a governed standard with a change process. In practice, the amendment workflow matters more than people expect: I've seen teams where the constitution quietly fell out of date because there was no agreed mechanism for changing it. The governance section makes the constitution an artifact the team owns, not one they inherit.

```markdown
## Governance

**Authority**: This constitution supersedes all other guidance. In conflicts
between this constitution and other documents (wikis, comments, verbal agreements),
this constitution is authoritative.

**Amendment process**:
1. Propose via `/devspark.evolve-constitution`
2. Discuss in a PR — amendments to the constitution require a PR, not a chat
3. Ratify by team consensus (at least two reviewers for MANDATORY sections)
4. Update version and last-amended date

**Version control**: Constitution changes are tracked via git. Every PR that amends
the constitution must update the version number and last-amended date.

**Version**: 1.4.0 | **Ratified**: 2022-03-10 | **Last Amended**: 2022-11-02
```

## The MUST/SHOULD/MAY Vocabulary

Using this vocabulary consistently matters because DevSpark commands interpret it precisely:

| Term | Meaning | How Commands Handle It |
|------|---------|----------------------|
| **MUST** | Non-negotiable | CRITICAL finding if violated; PR blocked |
| **MUST NOT** | Prohibited | CRITICAL finding if violated; PR blocked |
| **SHOULD** | Strongly recommended | HIGH finding if violated; PR should be fixed |
| **SHOULD NOT** | Discouraged | HIGH finding if violated; PR should be fixed |
| **MAY** | Optional, permitted | Informational only; no finding raised |

The most common mistake in constitutions is overusing MUST. When 80% of your requirements are MUST, the PR review tool will flag constant CRITICAL violations and the signal-to-noise ratio collapses. Reserve MUST for the things you would actually block a PR over, regardless of other merits.

A useful test: if you would approve a PR that violates this requirement, it's a SHOULD, not a MUST.

## Creating a Constitution for Greenfield Projects

For a new project where you know what principles you want, use `/devspark.constitution` directly:

```text
/devspark.constitution 
- Security first: no hardcoded credentials, parameterized SQL, validated input
- TDD required: tests before code, 80% coverage minimum
- All public APIs documented
- No console.log in production
- Functions max 50 lines, files max 500 lines
- ADR for all significant decisions
```

The command generates a properly structured constitution from your requirements and writes it to `/.documentation/memory/constitution.md`.

## The Discovery Workflow for Brownfield Projects

Existing projects present a different challenge. The code already has implicit principles — patterns that the team has been following without explicitly stating them. Discovering and codifying these patterns is the job of `/devspark.discover-constitution`.

### Running the Discovery

```text
/devspark.discover-constitution
```

Or with a focus area:

```text
/devspark.discover-constitution Focus on security and testing patterns
```

The command scans your codebase and produces a report of what it finds, organized by confidence:

```markdown
## Discovery Report

### High Confidence Findings

**Testing Pattern**
- All source files in `src/` have corresponding test files in `tests/`
- Test files use Vitest with `describe/it` structure
- Coverage reporting is configured (vitest.config.ts)
- Coverage target: 80% (found in CI configuration)
→ Confidence: HIGH — consistent across 94% of source files

**Database Access Pattern**
- Database access is consistently mediated through repository classes
- No direct `db.query()` calls outside of `src/repositories/`
- Repository pattern applied in 100% of examined files
→ Confidence: HIGH — no violations found

### Medium Confidence Findings

**Error Handling**
- Most handlers return structured error objects with `code` and `message` fields
- Some older handlers return plain strings
→ Confidence: MEDIUM — 73% consistent. Inconsistency likely historical drift.

**Documentation**
- TypeDoc comments present on 65% of exported functions
→ Confidence: MEDIUM — not consistently enforced

### Low Confidence Findings

**Dependency injection**
→ Confidence: LOW — mixed patterns, cannot determine intent

### Clarifying Questions

1. Is the 80% coverage threshold a hard requirement or a target?
2. Should new endpoints follow the structured error format even though older ones don't?
3. Is TypeDoc comment coverage a requirement you want to enforce going forward?
4. What is the policy on direct database access outside repositories? Is it a violation or just discouraged?
```

The discovery command's questions are targeted at exactly the places where the evidence is ambiguous. Answering them produces a constitution that accurately reflects both what the team has been doing and what they intend to do going forward.

### Finalizing the Draft

After the discovery conversation, the command generates a draft constitution at `/.documentation/memory/constitution-draft.md`. Review it, make adjustments, then ratify it:

```text
/devspark.constitution Finalize the draft at .documentation/memory/constitution-draft.md 
with the following changes: 80% coverage is a hard requirement (MUST), 
structured error format is required for new endpoints but not for existing ones,
TypeDoc is SHOULD not MUST.
```

## Evolving the Constitution

Constitutions should evolve as projects evolve. New patterns emerge, old requirements become outdated, and PR reviews surface violations that reveal gaps in the constitution. What I started with on the fintech project in early 2022 looked meaningfully different from what we were working against by the end of the year — not because the principles were wrong, but because the team learned things that sharpened them.

### The Evolution Workflow

After a series of PR reviews, use `/devspark.evolve-constitution` to propose amendments based on findings:

```text
/devspark.evolve-constitution Propose amendments based on the last three PR reviews.
```

The command reads the PR review history and identifies:
- Requirements that are consistently violated (suggesting they need clarification or may be overly strict)
- New patterns that have emerged and should be formalized
- Gaps where the constitution has no coverage for a category of violation

The output is a proposed amendment set, not an automatic change. The team reviews and approves via a PR before the constitution is updated.

> **Tip:** Run `/devspark.evolve-constitution` at the end of each sprint as part of your release process. PR review findings accumulate valuable signal about where your constitution needs refinement.

## Multi-App Constitutions

When using DevSpark's optional multi-app monorepo support (covered in Chapter 11), each application can have its own constitution that extends the repository-wide constitution.

### Layered Governance

```
/.documentation/memory/constitution.md          ← Repo-wide: applies to all apps
apps/payment-api/.documentation/memory/constitution.md  ← App-specific: additive only
apps/admin-web/.documentation/memory/constitution.md    ← App-specific: additive only
```

App-local constitutions are **additive**. They can add new requirements or tighten existing ones, but they cannot weaken or override repo-wide requirements. DevSpark detects and warns about weakening attempts.

```markdown
# apps/payment-api/.documentation/memory/constitution.md
# (extends repo constitution)

## PCI Compliance (MANDATORY)

These requirements are in addition to all repo-wide requirements.

- All payment data MUST be encrypted at rest and in transit (AES-256 minimum)
- Credit card numbers MUST NOT appear in logs, error messages, or stack traces
- PCI DSS Level 1 compliance MUST be maintained
- All payment processing MUST be isolated in the `payment-processing` service module
- No payment credentials MUST be cached client-side for more than 60 seconds

## API Versioning

- All payment endpoints MUST include an `API-Version` header
- Breaking changes to payment APIs MUST increment the major version
- The previous major version MUST remain supported for 90 days after a breaking change
```

### When to Create App-Local Constitutions

Most multi-app repositories need only the repo-wide constitution. Create app-local constitutions when:
- An application has compliance requirements that don't apply to other apps (PCI, HIPAA, SOC2)
- An application has significantly different risk profiles (customer-facing vs. internal tooling)
- Platform-specific technical requirements exist that only apply to one app

## Integrating with Agent Instruction Files

Most AI coding assistants also use their own instruction files: `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `.cursorrules` for Cursor. These files overlap with the constitution in purpose but serve a different function.

### The Hierarchy

```
Constitution (.documentation/memory/constitution.md)
  ↓ WHAT must be true — non-negotiable principles
  
Agent instruction files (CLAUDE.md, .github/copilot-instructions.md)
  ↓ HOW to work — implementation guidance for this specific agent
  
Coding standards (.documentation/standards.md)
  ↓ HOW we code — conventions and library choices
```

The constitution defines principles. Agent instruction files define implementation guidance that is specific to how a particular agent should work. The key rule is: **reference, don't duplicate**.

```markdown
# .github/copilot-instructions.md

## Foundational Documents

Before generating or reviewing code, consult these documents:

1. **Project Constitution**: `/.documentation/memory/constitution.md`
   - Contains non-negotiable principles
   - Violations are blocking issues in PR review

## Security Implementation (implements constitution Section I)

When implementing input validation:
- Use Zod schemas defined in `src/schemas/`
- Call `validateRequest(schema, req.body)` from `src/lib/validation`
- Return 400 with `{ code: "VALIDATION_ERROR", message: "..." }` on failure

For database queries:
- Use Prisma ORM (parameterized by default)
- Never use `$queryRawUnsafe()` or string concatenation in queries
```

The constitution says "all user input MUST be validated." The agent instruction file explains how to do that with the specific tools this project uses. They complement each other and don't duplicate.

## What Belongs in Your Constitution (and What Doesn't)

A common question is what should be in the constitution vs. what should go in other documents. The litmus test:

**Put it in the constitution if:**
- You would reject a PR that violates it, regardless of other merits
- It applies project-wide, not to specific components
- It's a principle, not an implementation detail

**Put it elsewhere:**

| Content | Where it belongs |
|---------|-----------------|
| "All input MUST be validated" | Constitution |
| "Use Zod for validation" | Agent instruction file or standards doc |
| "Why we chose PostgreSQL over MySQL" | Architecture Decision Record |
| "How to name your branch" | CONTRIBUTING.md |
| "The PR process steps" | CONTRIBUTING.md |
| "Which logging library to use" | Agent instruction file |
| "Log format: `{ level, timestamp, message }`" | Standards doc |

## Moving Forward

The constitution I started with on the fintech project in early 2022 is not the one the team was using by the end of that year, and that's the point. A constitution that never changes is a constitution no one is using — or a team that has stopped learning. What makes it work isn't the document itself but the practice of treating it as authoritative and amending it when you're wrong.

Once the constitution is in place, it feeds everything downstream: the agent instruction files that tell Copilot or Claude how to implement each principle, the automated PR review that checks compliance on every merge, and the onboarding process for new developers who need to understand not just what the rules are but why they exist. All of that starts here.

If you're not sure where to begin, start with the three principles that have caused the most friction on your team — the ones that come up in code review, the ones that prompted a production incident, the ones a senior developer enforces by instinct but has never written down. Those are your constitution's foundation. The rest can follow.

Chapter 6 covers right-sized workflows — the full spectrum from one-liner quickfixes through architectural changes, and how `/devspark.specify` routes you to the appropriate process.
