# Plan Changelog: DocSpark Book Publishing System

**Plan file**: [plan.md](plan.md)  
**Last updated**: 2026-05-17

This file records all identified gaps, decisions, and modifications made to `plan.md` since the initial draft. Each entry includes the gap ID, what was wrong, what was changed, and the resolution status.

---

## Review Session — 2026-05-17

A structured critical review was conducted against the actual repo state. The repo had a fully functional CLI (`docspark init`, `status`, `uninstall`, `list-assets`), 22 prompt templates, and a large unintegrated book publishing corpus in `.documentation/books/` — but zero book CLI commands implemented. The plan as originally drafted treated the .NET API as a V1 requirement and left many contracts undefined.

### GAP-001 — No Acceptance Criteria Per Phase

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | Phases had only "exit criteria" sentences. No user stories, no pass/fail scenarios. |
| **Fix applied** | Added concrete acceptance scenarios (Given/When/Then) to Phases 1–4 directly in each phase block. |
| **Status** | Resolved |

### GAP-002 — `devspark-complete-guide` Naming Inconsistency

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | Plan referenced `docspark-complete-guide` in importer examples, but the real in-repo book slug is `devspark-complete-guide`. Mixed naming would cause import failures. |
| **Fix applied** | Corrected importer example to `devspark-complete-guide`. Added Open Decision 12 requiring explicit resolution before Phase 5. |
| **Status** | Partially resolved — importer example corrected; naming decision still open (OD-12) |

### GAP-003 — .NET Minimal API Premature For V1

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | FR-038–FR-044 and Phases 8–9 placed the .NET API and thin client as V1 requirements, before any book CLI commands existed. Added a second language runtime, second build system, and second dependency set to a milestone that hadn't proven its Python core. |
| **Fix applied** | Demoted .NET API and thin client to "Future Architecture". Application Architecture section now leads with "V1: Python CLI Only". Phases 8–9 renamed to Proofing/Release and Site Update. Future API and thin client moved to Phases 10–11 with explicit gates. FR-038–044 and NFR-010–013 marked *(Future)*. `apps/` and `services/` removed from the V1 repo structure diagram. Recommended First Milestone defer list updated. |
| **Status** | Resolved |

### GAP-004 — No Error Format Contract

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | FR-027 and NFR-006 required human-readable errors but gave no format, no stderr/stdout distinction, and no exit code contract. |
| **Fix applied** | Added "CLI Error And Progress Contract" section with concrete examples of `[docspark-book]` progress prefix, `Error [category]: message` stderr format, exit code table (0/1/2), and Pandoc version policy. |
| **Status** | Resolved |

### GAP-005 — Schema URI References Non-Existent Domain

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | Manifest contract used `schema: "https://docspecspark.dev/schemas/book/v1"`. The domain does not exist and implies an online dependency. Legacy mode was mentioned but not defined. |
| **Fix applied** | Schema identifier changed to `docspark/book/v1` (local, no network dependency). Legacy mode rule defined: absent `schema:` with `title`, `author`, and `chapters` present triggers legacy-compatible mode. |
| **Status** | Resolved |

### GAP-006 — Test Coverage Plan Superficial

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | Validation strategy listed test categories only. No test module names, no fixture strategy, no per-phase minimums. 10+ new CLI commands planned with no test structure defined. |
| **Fix applied** | Added "Test Architecture" section with four named test modules, three named fixture directories, and per-phase minimum coverage requirements. Noted that `devspark-complete-guide` corpus must not be used as a test fixture. |
| **Status** | Resolved |

### GAP-007 — `web_publish` Flag Has No Python Equivalent

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | Workflow 2 (documentation-to-book harvesting) had no filtering mechanism defined. The reference spec used `web_publish: false` but the plan never specified its DocSpark equivalent. |
| **Fix applied** | Added "Book-Only Chapter Flag" section to the Manifest Contract. Defined `book_only: true` as the V1 frontmatter flag for book-only chapters. Compose command logs `(book_only)` in progress output. Added Open Decision 14 (resolved: `book_only: true` is the V1 mechanism). |
| **Status** | Resolved |

### GAP-008 — Scoring Dimensions Undefined At Implementation Level

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | FR-029 listed 8 dimensions but gave no output schema. `ScoreRecord.dimensions` was a bare field name. Implementers would invent incompatible formats. |
| **Fix applied** | Expanded `ScoreRecord` in Data Model with typed field descriptions. Added `ScoreDimension` sub-model (`score`, `rationale`, `flags`). Added dimension key table with descriptions of all 8 dimensions. Clarified rule-based vs. LLM scoring behavior per field. |
| **Status** | Resolved |

### GAP-009 — Pandoc Version Policy Incomplete

| Field | Detail |
| --- | --- |
| **Impact** | Low-medium |
| **Problem** | Plan said "warn below 2.19" but never said whether to abort or continue, what breaks below that version, or what the tested range is. |
| **Fix applied** | CLI Error Contract section defines exact policy: warn-and-continue below 2.19, abort below 2.11. Tested range documented as 2.19–3.x. Open Decision 7 marked RESOLVED. |
| **Status** | Resolved |

### GAP-010 — "Portable Workspace" Claim Undefined

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | Plan claimed portable workspaces but the existing `book.yaml` used repo-root-relative paths. Moving the book directory would break all source paths. |
| **Fix applied** | Added "Path Resolution Contract" section. Defined V1 convention: all paths in `book.yaml` are relative to the book root directory (the directory containing `book.yaml`). Importer must convert repo-root-relative legacy paths to book-root-relative paths. Cover image also book-root-relative. Traversal rejection rule specified. |
| **Status** | Resolved |

### GAP-011 — No CI/CD Or Packaging Milestone

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | Plan described 11 phases but never stated when the package is published, what the version is, or what a release requires. |
| **Fix applied** | Phase 9 exit criteria now includes PyPI publish of `docspark-cli` 0.2.0. SC-011 added to Success Criteria. Future gate on Phases 10–11 references published 0.2.0 explicitly. |
| **Status** | Resolved |

### GAP-012 — `quickstart/` Directory Unaddressed

| Field | Detail |
| --- | --- |
| **Impact** | Low-medium |
| **Problem** | Repo has 4 agent-specific quickstart prompts in `quickstart/`. Plan never mentioned updating them. New users following those prompts would not know book commands exist. |
| **Fix applied** | Phase 9 tasks include updating all 4 quickstart prompts. Phase 9 exit criteria include this. SC-012 added. Immediate Next Tasks Step 2 item 7 calls this out. |
| **Status** | Resolved |

### GAP-013 — `parts:` Manifest Structure Under-Specified

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | Manifest schema included `parts:` but the plan never specified how compose renders part headers, what heading level they use, or whether the feature is V1. The reference `book.yaml` used YAML comments not a `parts:` structure, creating two conflicting conventions. |
| **Fix applied** | Added "Parts — V1 Decision: Deferred" subsection to Manifest Contract. Defined V1 behavior: `parts:` accepted with a warning, ignored, falls back to `chapters:`. Showed exact post-V1 composed output format (part headers as `##` headings). Open Decision 13 marked RESOLVED. FR-009 updated to reflect the V1 warning-and-ignore behavior. |
| **Status** | Resolved |

---

## Review Session — 2026-05-17 (Second Review)

A second review was conducted against the actual repo state after the first review's changes were applied. This pass compared the plan against real file contents: `pyproject.toml`, `src/docspark_cli/cli.py`, `tests/test_cli_end_to_end.py`, `mkdocs.yml`, `.gitignore`, and the `examples/` and `dist/` directories.

### GAP-014 — Stale `dist/` Wheel Artifacts Committed

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | `dist/docspecspark-0.2.0-py3-none-any.whl` and `dist/docspecspark-0.2.0.tar.gz` were present in the repo. `pyproject.toml` says version `0.1.0`. These artifacts were built from a version that does not exist in source, and `.gitignore` has `dist/` — meaning they were either force-added or committed before the gitignore was in place. |
| **Fix applied** | Added explicit Phase 0 task to delete the stale artifacts. |
| **Status** | Resolved in plan; cleanup task added to Phase 0 |

### GAP-015 — Open Decision 1 Already Answered By Repo

| Field | Detail |
| --- | --- |
| **Impact** | Low |
| **Problem** | OD-1 (examples location) was left open, but the repo already has `examples/policy-portal/` as a committed, tested example. The test `test_examples_policy_portal_snapshot_exists` asserts this layout. The decision was already made in practice. |
| **Fix applied** | OD-1 marked **RESOLVED**: `examples/` is the correct location. |
| **Status** | Resolved |

### GAP-016 — Open Decision 2 Already Answered; Gitignore Pattern Missing

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | OD-2 (`dist/book.md` gitignored) was left open, but the existing plan body had already removed `dist/book.md` from the book workspace structure (see Structural Changes Summary from first review). Additionally, the current `.gitignore` only has a top-level `dist/` entry that covers the Python package dist — it does not cover book workspace `dist/` paths like `.documentation/books/**/dist/`. |
| **Fix applied** | OD-2 marked **RESOLVED**. Phase 3 task added to insert the four book-workspace gitignore patterns. |
| **Status** | Resolved |

### GAP-017 — Open Decision 6 Already Answered By Naming Conventions

| Field | Detail |
| --- | --- |
| **Impact** | Low |
| **Problem** | OD-6 (expose `docspecspark` alias) was left open. The CLI entrypoint, install root, and package name all use `docspark`/`docspark-cli`. There is no `docspecspark` command anywhere in the codebase. The answer is clearly no. |
| **Fix applied** | OD-6 marked **RESOLVED**: no alias. |
| **Status** | Resolved |

### GAP-018 — Open Decision 8 Already Answered By Corpus Cleanup

| Field | Detail |
| --- | --- |
| **Impact** | Low |
| **Problem** | OD-8 (generated EPUB/PDF in examples) was left open despite the plan already stating generated outputs should be excluded. The `publish/` folder was deleted from `.documentation/books/` during the Phase 0 corpus cleanup. |
| **Fix applied** | OD-8 marked **RESOLVED**: generated EPUB/PDF artifacts are never committed. |
| **Status** | Resolved |

### GAP-019 — `tests/fixtures/` Directories Not Yet Created

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | The plan's Test Architecture section references `tests/fixtures/minimal-book/`, `tests/fixtures/legacy-book/`, and `tests/fixtures/hostile-paths/`. The `tests/` directory currently contains only `test_cli_end_to_end.py`. No fixture directories exist. Phases 2–5 depend on these fixtures, but no phase explicitly assigned the task of creating them. |
| **Fix applied** | Fixture directory creation added as explicit tasks at the top of Phase 2, with a note that they do not yet exist. |
| **Status** | Resolved |

### GAP-020 — `examples/sample-book` Shape Did Not Match Actual Example Pattern

| Field | Detail |
| --- | --- |
| **Impact** | Low |
| **Problem** | The Proposed Repo Structure showed `examples/sample-book/` with only `book.yaml`, `chapters/`, and `README.md` — a bare book workspace, not a DocSpark-installed workspace. The actual `examples/policy-portal/` includes `.docspark/`, `.documentation/`, and `.github/` directories, which is the correct shape for a DocSpark example. |
| **Fix applied** | `examples/sample-book/` structure in Proposed Repo Structure updated to include `.docspark/`, `.documentation/`, and `cover.png` to match the installed pattern. |
| **Status** | Resolved |

### GAP-021 — `VERSION` Hardcoded In `cli.py`, Will Drift From `pyproject.toml`

| Field | Detail |
| --- | --- |
| **Impact** | Medium |
| **Problem** | `cli.py` contains `VERSION = "0.1.0"` as a hardcoded string. `pyproject.toml` is the canonical version source. When Phase 9 bumps to `0.2.0`, two files must be updated in sync. The test `test_package_version_is_alpha_start` asserts `__version__ == "0.1.0"`, which will also need updating. A single source of truth is safer. |
| **Fix applied** | Phase 9 task added to replace the hardcoded string with `importlib.metadata.version("docspark-cli")` and update the test accordingly. |
| **Status** | Resolved in plan; implementation deferred to Phase 9 |

### GAP-022 — MkDocs Will Render `.documentation/books/` Chapter Files As Site Pages

| Field | Detail |
| --- | --- |
| **Impact** | High |
| **Problem** | `mkdocs.yml` uses `docs_dir: .documentation`. The `.documentation/books/` corpus — including all chapter `.md` files from `devspark-complete-guide` and `project-mechanics` — sits inside that tree. Without explicit exclusion, MkDocs will attempt to render all of them as site pages, producing broken links, unexpected nav entries, and a bloated site. |
| **Fix applied** | Phase 9 tasks updated to include adding MkDocs `exclude_docs:` (or explicit `nav:`) to prevent `.documentation/books/**` from becoming site pages. Phase 9 exit criteria updated with this requirement. |
| **Status** | Resolved in plan; implementation deferred to Phase 9 |

---

## Structural Changes Summary

| Change | Reason |
| --- | --- |
| Removed Critical Review section from `plan.md` | Moved to this changelog; plan is now clean executable spec |
| Split into `plan.md` + `plan-changelog.md` | Keeps the plan readable; audit trail in separate file |
| Phases renumbered: old 8 (API) → 10, old 9 (client) → 11, old 10 (proof) → 8, old 11 (site) → 9 | Reflects V1 boundary: CLI phases 0–9, future phases 10–11 |
| `apps/` and `services/` removed from V1 repo structure | Not built until Phase 10–11 gate |
| `tests/fixtures/` added to repo structure | Required by Test Architecture section |
| `dist/book.md` removed from Book Workspace Structure | Generated output, gitignored; not committed |
| Open Decisions 13 and 14 marked RESOLVED | `parts:` deferred; `book_only: true` adopted |
| Open Decision 7 marked RESOLVED | Pandoc ≥ 2.19 warn, < 2.11 abort |

---

## Open Decisions Tracker

| # | Decision | Status | Blocks |
| --- | --- | --- | --- |
| 1 | Examples under `examples/` vs `.documentation/books/`? | **Resolved**: `examples/` — matches existing repo pattern | — |
| 2 | Is `dist/book.md` gitignored? | **Resolved**: yes — book workspace gitignore patterns added in Phase 3 | — |
| 3 | Pydantic vs. dataclasses for manifest validation? | Open | Phase 2 |
| 4 | Which LLM provider adapter first? | Open | Phase 7 |
| 5 | `critique` command: execute prompts or prepare context only? | Open | Phase 6 |
| 6 | Expose `docspecspark` command alias? | **Resolved**: no alias | — |
| 7 | Minimum Pandoc version | **Resolved**: ≥ 2.19 warn, < 2.11 abort | — |
| 8 | Allow generated EPUB/PDF in examples? | **Resolved**: never — `publish/` deleted; book `dist/` gitignored | — |
| 9 | .NET API invoke CLI or share logic? | Open | Phase 10 |
| 10 | Thin client progress: polling, SSE, or WebSockets? | Open | Phase 10 |
| 11 | `.docspec/` JSON-only or SQLite? | Open | Phase 10 |
| 12 | Is `devspark-complete-guide` a DevSpark book or DocSpark example? | **Must resolve** | Phase 5 |
| 13 | Does `parts:` ship in V1? | **Resolved**: deferred; warn-and-ignore in V1 | — |
| 14 | `web_publish: false` or `book_only: true` for book-only chapters? | **Resolved**: `book_only: true` | — |
