---
title: "Chapter 11: Monorepo Support — Governing Multiple Applications"
part: "Part IV: Advanced Patterns"
---

# Chapter 11: Monorepo Support — Governing Multiple Applications

## The Monorepo Challenge

I noticed a pattern on a recent monorepo project: the same AI assistant that helped the payment API team implement PCI controls was suggesting those controls for a documentation site in the same repo. The assistant didn't know they were separate applications. It saw one repository, one codebase, one set of rules — and it applied them uniformly. A PR review for a documentation change flagged PCI compliance requirements. A specification for a frontend feature referenced backend patterns that had no business appearing there. The governance rules blurred across application boundaries, and no one had a clean way to stop it.

That confusion — where governance rules collapse across app boundaries — is what monorepo support prevents.

The underlying problem is structural. A monorepo offers real benefits: atomic cross-app changes, unified git history, shared tooling, simplified onboarding. But different applications in the same repository have genuinely different requirements. A customer-facing payment API needs PCI compliance controls that an internal documentation tool doesn't. A React frontend has different architectural constraints than a Python data pipeline. A QA test harness has different testing requirements than the production services it tests. Without explicit scoping, an AI coding assistant treats the entire repository as one unit and applies whatever governance context it finds to whatever problem it's currently solving.

DevSpark's monorepo support addresses this through three mechanisms: explicit application registry, governance profiles, and dependency awareness.

## When to Use Monorepo Support

In my experience, the most common mistake with monorepo governance tooling is adopting it before the problem it solves has actually appeared. Monorepo support is entirely opt-in and deliberately off by default. Most projects — including most actual monorepos — do not need it.

I've watched teams adopt multi-app support preemptively, adding three configuration files for what turns out to be a single application they were merely thinking of splitting. The overhead isn't worth it until governance confusion becomes visible friction in your workflow. If your PR reviews aren't flagging false positives across applications, if your governance rules aren't colliding, if teams aren't stepping on each other's contexts — don't solve for it yet.

What I've found is that the right trigger is specific and observable: AI assistants suggesting payment API patterns for a documentation tool, or a PR review for a frontend change flagging backend compliance requirements. When that friction is real and recurring, multi-app support earns its configuration cost. The conditions where it makes sense are: applications in the monorepo have genuinely different governance requirements (PCI vs. no-PCI, HIPAA vs. general), teams own different applications and need isolated governance contexts, or you need per-app constitutions, per-app command customizations, or per-app guardrails.

The conditions where it doesn't make sense are equally important. If all applications follow the same governance rules, the repo-wide constitution is sufficient. If you have a monorepo but only one or two applications with similar patterns, the added structure creates debt without solving a real problem.

## Enabling Multi-App Support

I designed monorepo support around three decisions, each reflecting a problem I watched recur. First, explicit registration forces teams to name their applications and declare their boundaries — that act of naming alone catches many governance confusions, because naming forces clarity about what belongs where. Second, profiles let different applications inherit different governance without duplicating rules everywhere. Third, dependency awareness prevents cross-app PR reviews from flagging irrelevant controls or missing real breaking changes. These three together solve the governance blurring problem; any one alone is insufficient.

The trade-off in making registration explicit rather than automatic was deliberate. Auto-detection would be convenient, but it would let teams defer the clarity work that registration forces. When you have to name an application and declare its path and owner and criticality, you're making decisions that would otherwise stay implicit — and implicit decisions are where governance confusion lives.

When I designed monorepo support, I made registration explicit rather than automatic. Teams must create a registry file — this forces them to name their applications and declare boundaries. That act of naming catches many governance confusions before they become problems. The registry lives at:

```
.documentation/devspark.json
```

Without this file, DevSpark operates in standard single-app mode with no behavior changes. The presence of this file activates multi-app mode.

### The Registry File

```json
{
  "version": 1,
  "mode": "multi-app",
  "profiles": {
    "api-profile": {
      "description": "Shared rules for all API services",
      "rules": [
        "100% integration test coverage for all endpoints",
        "OpenAPI spec required for all public endpoints",
        "Rate limiting on all authentication endpoints"
      ]
    },
    "web-profile": {
      "description": "Shared rules for web applications",
      "rules": [
        "Lighthouse performance score ≥ 90",
        "WCAG 2.1 AA compliance required",
        "Bundle size budget: 250KB initial load"
      ]
    },
    "internal-profile": {
      "description": "Relaxed rules for internal tools",
      "rules": [
        "Integration tests for critical paths only",
        "Basic auth acceptable for internal tools"
      ]
    }
  },
  "apps": [
    {
      "id": "payment-api",
      "path": "apps/payment-api",
      "kind": "api",
      "purpose": "Customer-facing payment processing API",
      "owner": "platform-team",
      "criticality": "critical",
      "inherits": ["api-profile"],
      "dependsOn": []
    },
    {
      "id": "admin-web",
      "path": "apps/admin-web",
      "kind": "web",
      "purpose": "Internal administration dashboard",
      "owner": "admin-team",
      "criticality": "medium",
      "inherits": ["web-profile", "internal-profile"],
      "dependsOn": ["admin-api"]
    },
    {
      "id": "admin-api",
      "path": "apps/admin-api",
      "kind": "api",
      "purpose": "Backend for admin dashboard",
      "owner": "admin-team",
      "criticality": "medium",
      "inherits": ["api-profile", "internal-profile"],
      "dependsOn": []
    },
    {
      "id": "shared-ui-library",
      "path": "packages/shared-ui",
      "kind": "library",
      "purpose": "Shared React components",
      "owner": "frontend-guild",
      "criticality": "high",
      "inherits": ["web-profile"],
      "dependsOn": []
    }
  ]
}
```

### Registry Schema Fields

**Profile fields:**
- `description`: Human-readable description for documentation and review display
- `rules`: Governance rules specific to this profile, evaluated in all reviews for apps that inherit the profile

**Application fields:**
- `id`: Unique identifier used in `--app <id>` flags
- `path`: Relative path from repository root to the application directory
- `kind`: Application type (`api`, `web`, `library`, `service`, `tool`, `qa`)
- `purpose`: Human-readable description for documentation and context-setting
- `owner`: Team or individual responsible for this application
- `criticality`: Risk level (`critical`, `high`, `medium`, `low`)
- `inherits`: List of profile IDs whose rules apply to this application
- `dependsOn`: List of other application IDs that this application depends on

## Scoping Commands to Applications

Once registered, any DevSpark command can be scoped to a specific application:

```text
/devspark.specify --app payment-api Add a recurring payment scheduling feature.
```

When `--app payment-api` is specified:
1. The resolver prepends `apps/payment-api/templates/` to the resolution chain
2. The constitution lookup reads `apps/payment-api/.documentation/memory/constitution.md` (if it exists) in addition to the repo-wide constitution
3. The profile rules from `api-profile` are included in the governance context
4. Artifacts are created under `apps/payment-api/.documentation/specs/`

```text
/devspark.pr-review --app payment-api
```

PR review with app scope:
1. Applies repo-wide constitution AND `apps/payment-api/.documentation/memory/constitution.md`
2. Applies `api-profile` rules from the registry
3. Checks dependency impacts on apps that `dependsOn` payment-api
4. Reports findings at both levels (repo-wide violations vs. PCI-specific violations)

### Repo-Wide Operations

For operations that should span all applications:

```text
/devspark.site-audit --repo-scope
/devspark.release --repo-scope
```

Repo-scope operations aggregate results across all registered applications.

## Governance Profiles

Profiles are the DRY mechanism for monorepo governance. Instead of duplicating the same rules in every application's constitution, define them once in the profile and inherit them. I've found this is where the real governance leverage lives — a rule defined in a profile applies consistently across every application that inherits it, and updating the profile propagates the change everywhere.

### Profile Inheritance

An application that declares `"inherits": ["api-profile"]` gets all API profile rules applied to it automatically. An application that declares `"inherits": ["web-profile", "internal-profile"]` gets rules from both profiles — they combine with AND semantics.

Profile rules are additive. They cannot conflict with or weaken the repo-wide constitution. DevSpark detects and warns about conflicts:

```
Warning: admin-web inherits internal-profile which includes:
  "Basic auth acceptable for internal tools"
  
The repo-wide constitution states:
  "Authentication MUST use an established library — no hand-rolled auth"
  
Basic authentication implemented without a library violates the repo-wide constitution.
The profile rule is narrower than the constitution violation it may appear to permit.
Profile rule retained but note: it does not override the MUST requirement.
```

### When Profiles Conflict

The resolution is: repo-wide constitution always wins. If a profile rule appears to weaken a constitution requirement, DevSpark warns but doesn't automatically resolve the conflict. A human must decide whether to:
- Keep the profile rule (accepting that it doesn't override the MUST requirement)
- Remove the profile rule (it's misleading)
- Amend the constitution (if the constitution is actually too strict for some legitimate case)

This raises an interesting question about where to draw the boundary between repo-wide and profile-level governance. In practice, I've found the right heuristic is: if a rule needs to vary by application, it belongs in a profile; if it's a non-negotiable floor for the entire codebase, it belongs in the constitution. Mixing those levels is where conflicts originate.

## Dependency-Aware PR Reviews

This is where monorepo complexity surfaces most acutely. The `dependsOn` registry field enables dependency-aware PR reviews — and this is the mechanism I've found most teams don't think they need until the first time a breaking API change ships without anyone noticing that a downstream application depended on the removed endpoint.

When a PR changes `apps/admin-api`, the review engine knows that `apps/admin-web` depends on it and checks for potential breaking changes:

```markdown
## Dependency Impact Analysis

**Changed application**: admin-api
**Dependent applications**: admin-web (dependsOn: admin-api)

### Breaking Change Check

The PR removes the `GET /api/admin/users/:id/permissions` endpoint.
admin-web calls this endpoint from `src/components/UserDetailPanel.tsx:47`.

**Risk**: HIGH — admin-web will break when this change deploys.

**Recommendation**: Either keep the endpoint (add deprecation notice) or
update admin-web in the same PR to remove the dependency.
```

Dependency impact analysis runs automatically when PR review is run on a PR that touches registered applications. It does not require the `--app` flag — it detects which applications are affected by the changed files and traverses the dependency graph to find downstream consumers.

## Managing Applications

### Registering a New Application

```text
/devspark.add-application
```

The command walks through the registration:
1. Application ID (must be unique, slug format)
2. Path (relative to repository root)
3. Kind (api, web, library, service, tool, qa)
4. Purpose (human-readable description)
5. Owner (team or individual)
6. Criticality (critical, high, medium, low)
7. Profiles to inherit
8. Applications this app depends on

After registration, run validation:

```text
/devspark.validate-registry
```

### Listing Applications

```text
/devspark.list-applications
```

Output:
```
Registered Applications (4)

├── payment-api [critical] — Customer-facing payment processing API
│   Path: apps/payment-api
│   Owner: platform-team
│   Profiles: api-profile
│   Dependencies: none
│
├── admin-web [medium] — Internal administration dashboard
│   Path: apps/admin-web
│   Owner: admin-team
│   Profiles: web-profile, internal-profile
│   Dependencies: admin-api
│
├── admin-api [medium] — Backend for admin dashboard
│   Path: apps/admin-api
│   Owner: admin-team
│   Profiles: api-profile, internal-profile
│   Dependencies: none
│
└── shared-ui-library [high] — Shared React components
    Path: packages/shared-ui
    Owner: frontend-guild
    Profiles: web-profile
    Dependencies: none
```

### Validating the Registry

```text
/devspark.validate-registry
```

Validation checks:
- All `id` values are unique
- All `path` values exist on disk
- All `inherits` values reference defined profiles
- All `dependsOn` values reference registered application IDs
- No circular dependencies
- All `criticality` values are valid
- Registry JSON is schema-valid

## Per-App Directory Structure

A properly configured multi-app repository looks like:

```
.documentation/
├── memory/constitution.md        ← Repo-wide constitution
├── devspark.json                 ← Application registry
└── specs/                        ← Repo-level specs (if any)

apps/
├── payment-api/
│   ├── .documentation/
│   │   ├── memory/constitution.md  ← PCI-specific additions
│   │   ├── commands/               ← App-level command overrides
│   │   └── specs/                  ← Payment API specs
│   └── src/
│       └── ...
├── admin-web/
│   ├── .documentation/
│   │   └── specs/                  ← Admin web specs
│   └── src/
│       └── ...
└── admin-api/
    ├── .documentation/
    │   └── specs/                  ← Admin API specs
    └── src/
        └── ...
```

In my experience, most teams implementing monorepo support should start here — with the registry. List your applications, make their boundaries explicit, and let that naming process surface the governance questions you didn't know you had. Add profiles only if you find governance rules diverging across applications in ways the repo-wide constitution can't handle cleanly. Dependency awareness can wait until PR review false positives — or missed breaking changes — become a real friction point. Each layer builds on the previous; adding all three at once without a concrete problem to solve creates configuration debt that outlasts the confusion you were trying to prevent.

Chapter 12 covers multi-agent and multi-user teams — how multiple developers using different AI agents collaborate effectively in a DevSpark-governed repository.
