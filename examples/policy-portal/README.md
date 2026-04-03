# DocSpark Example: Policy Portal

This is a minimal example showing what a document repository looks like after DocSpark is installed.

DocSpark is a document AI tool derived from DevSpark. This example demonstrates how DocSpark adapts that model for a documentation system with constitution governance and multi-user overrides.

## What's Here

```text
examples/policy-portal/
├── .docspark/                          ← Framework assets, safe to replace
│   ├── defaults/commands/
│   │   ├── docspark.constitution.md
│   │   ├── docspark.specify.md
│   │   ├── docspark.plan.md
│   │   └── docspark.implement.md
│   ├── memory/
│   │   └── constitution.md            ← Stock seed constitution
│   └── VERSION
├── .documentation/                    ← User-owned work
│   ├── memory/
│   │   └── constitution.md            ← Customized governance rules
│   ├── commands/
│   │   └── docspark.pr-review.md      ← Team override example
│   ├── morgan-hazleton/
│   │   └── commands/
│   │       └── docspark.specify.md    ← Personal override example
│   ├── specs/
│   │   └── onboarding-handbook-refresh.md
│   └── decisions/
│       └── 001-review-cadence.md
├── .github/
│   ├── agents/
│   │   └── docspark.specify.agent.md
│   └── prompts/
│       └── docspark.specify.prompt.md
└── README.md
```

## Key Concepts Demonstrated

1. `.docspark/` vs `.documentation/` — framework files stay replaceable, while project work remains user-owned.
2. Constitution governance — the stock seed lives in `.docspark/memory/constitution.md`, but the active project rules live in `.documentation/memory/constitution.md`.
3. Multi-user overrides — team behavior can live in `.documentation/commands/`, while a specific user can override only their own workflow in `.documentation/{git-user}/commands/`.
4. Agent shims — `.github/agents/` and `.github/prompts/` show how Copilot resolves the three-tier prompt lookup.

## Try It

Copy this directory into a fresh repository if you want a concrete starting point for a documentation system managed with DocSpark.