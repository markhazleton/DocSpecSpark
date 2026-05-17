```yaml
gate: analyze
status: warn
blocking: false
severity: warning
summary: "Pass 3 (post-critic-pass-2): 100% FR/SC/edge-case coverage, 0 constitution violations, 0 unmapped tasks. 2 MEDIUM inconsistencies: spec.md FR-003 not updated to reflect NEW-CR-003 TOC strategy decision; plan.md still lists gray-matter as frontmatter stripping dep but T007 uses regex+js-yaml. Non-blocking — proceed to implement."
```

## Specification Analysis Report — Pass 3

**Analysis Date:** 2026-04-22
**Pass:** 3 of N (post-plan-revision pass 2, post-tasks-regeneration pass 2)
**Artifacts analyzed:** spec.md, plan.md, tasks.md, data-model.md, contracts/cli-contract.md, research.md, quickstart.md

---

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I3 | Inconsistency | MEDIUM | spec.md FR-003 vs tasks.md T009, data-model.md | spec.md FR-003 states "The composition engine MUST prepend a title page (title, subtitle, author) **and a table of contents** to `book.md`." The NEW-CR-003 resolution (plan.md Critic Pass 2 Mitigations) explicitly removed the manual TOC from `book.md` assembly, delegating to Pandoc `--toc`. `data-model.md` CompiledBook section now reads "does NOT include a manual TOC." T009 reinforces this. The spec MUST was not updated — spec and implementation are contradictory on whether `book.md` contains a TOC section. | Update spec.md FR-003: replace "and a table of contents" with "and Pandoc `--toc` generates a navigable table of contents in the rendered output." The end-user outcome is identical; the spec must reflect the implementation decision. |
| I4 | Inconsistency | MEDIUM | plan.md Technical Context (Primary Dependencies) | plan.md still lists "`gray-matter` (already present — frontmatter stripping)" as a primary dependency. T007 uses `regex + js-yaml.load()` for frontmatter parsing — not gray-matter. research.md Decision 3 specifies inline regex approach. This was the I2 finding from analyze pass 1 and pass 2; it was documented but not fixed. gray-matter is present in the project but is not used by the book pipeline for frontmatter stripping. | Update plan.md Technical Context: change "`gray-matter` (already present — frontmatter stripping)" to "`gray-matter` (present in project — NOT used by book pipeline; frontmatter stripping done via regex + `js-yaml.load()` per research.md Decision 3)". One-line fix. |
| N3 | Inconsistency | LOW | tasks.md Dependencies section | The dependency chain shows `T001 → T003 → T005...` implying T003 (`npm install js-yaml`) depends on T001 (`create books/` directory). These are independent operations — installing an npm package has no dependency on creating a directory. The Parallel Execution table correctly shows T001–T004 as "all independent." | Update dependency chain: change `T001 → T003 → T005` to `T003 → T005` (T001 and T003 are independent parallel setup tasks). Minor inconsistency between the two sections of tasks.md. |
| N4 | Ambiguity | LOW | tasks.md T013 | T013 wiring description: "slug → `parseBookYaml` → availability checks (T012 logic)." The Pandoc availability check (T012 part a) does not require YAML context and should run before `parseBookYaml`. Only the pdflatex check (T012 part b) requires knowing `book.output.formats`. The sequencing as described runs YAML parsing before Pandoc is confirmed available — minor waste if book.yaml is malformed AND Pandoc is missing. | Consider revising T013 flow to: "slug → Pandoc availability check → `parseBookYaml` → pdflatex check (if pdf in formats) → `composeBook`...". Low impact — functionally acceptable either way but the described order is suboptimal. |

---

## Coverage Summary

| Requirement | Has Tasks? | Task IDs | Notes |
|---|---|---|---|
| FR-001 (book.yaml single source) | ✅ | T006 | parseBookYaml validates all required fields |
| FR-002 (strip frontmatter + concatenate) | ✅ | T007, T009 | stripFrontmatter + composeBook |
| FR-003 (title page + TOC) | ✅ | T009, T011 | title page in T009; Pandoc --toc in T011 (spec.md wording inconsistent — I3) |
| FR-004 (chapter title override) | ✅ | T008, T009 | resolveChapterTitle fallback chain |
| FR-005 (EPUB3 + PDF output) | ✅ | T011 | epub3 + pdflatex, both formats in renderBook |
| FR-006 (books/publish/<slug>/ output dir) | ✅ | T011, T013 | publish dir created in renderBook |
| FR-007 (exit non-zero; attempt all formats) | ✅ | T012, T013 | availability check + collect-all-failures loop |
| FR-008 (article frontmatter flags) | ✅ | T018 | adds book/book_title/book_order to fixture articles |
| FR-009 (generate:articles propagates flags) | ✅ | T016, T017, T019 | audit → explicit add → verification |
| FR-010 (visible chapter separator) | ✅ | T009 | --- separator in composeBook |
| FR-011 (book.md committed) | ✅ | T010, T013 | writeCompiledBook + wired in main flow |
| FR-012 (progress output per step) | ✅ | T009, T010, T011 | [book-publishing] prefix per step |
| FR-013 (minimum 2 chapters validation) | ✅ | T006 | chapters.length >= 2 check in parseBookYaml |
| SC-001 (60-second warm-start SLO) | ✅ | T015 | warm-start timing verification |
| SC-002 (Kindle Previewer zero errors) | ✅ | T020, T022 | manual validation + remediation |
| SC-003 (no additional authoring work) | ✅ | — | inherent in composition design |
| SC-004 (existing pipeline unaffected) | ✅ | T025 | npm run build regression check |
| SC-005 (quickstart.md self-sufficient) | ✅ | — | quickstart.md artifact exists and updated |
| Edge: empty article body | ✅ | T009 | warns and skips empty-body chapters |
| Edge: duplicate book_order | ✅ | T009 | warning + YAML declaration order tiebreaker |
| Edge: Pandoc not installed | ✅ | T012 | startup availability check |
| Edge: one format fails | ✅ | T013 | collect-all-failures, write successes, exit 1 |
| Edge: dist dir already exists | ✅ | T011 | creates-if-needed (overwrites) |
| Edge: fewer than 2 chapters | ✅ | T006 | FR-013 validation in parseBookYaml |

**Coverage: 13/13 FRs (100%), 5/5 SCs (100%), 6/6 edge cases (100%)**

---

## Constitution Alignment Issues

None. All 9 constitution principles confirmed N/A or PASS (see plan.md Constitution Check section).

---

## Unmapped Tasks

None. All 26 tasks map to at least one FR, SC, or quality gate concern.

---

## Metrics

| Metric | Value |
|---|---|
| Total FRs | 13 |
| Total SCs | 5 |
| Total Edge Cases | 6 |
| Total Tasks | 26 |
| FR Coverage | 100% (13/13) |
| SC Coverage | 100% (5/5) |
| Edge Case Coverage | 100% (6/6) |
| Constitution Violations | 0 |
| Unmapped Tasks | 0 |
| Critical Issues | 0 |
| MEDIUM Inconsistencies | 2 (I3, I4) |
| LOW Notes | 2 (N3, N4) |

---

## Next Actions

No critical issues. All 13 FRs, 5 SCs, and 6 edge cases are covered. Gate status: **WARN / non-blocking**.

**Recommended before committing `book.md` to human readers:**
- **I3** (MEDIUM): Update spec.md FR-003 to replace "prepend...a table of contents to `book.md`" with language that acknowledges Pandoc `--toc` as the TOC source. One-sentence change. Otherwise spec.md will confuse a developer who reads it and then looks at `book.md` with no TOC section.
- **I4** (MEDIUM, carry-forward): Update plan.md Technical Context Primary Dependencies to clarify gray-matter is NOT used by the book pipeline for frontmatter stripping. One-line change. Has been open since pass 1 analyze gate.

**Optional improvements (LOW, safe to defer):**
- **N3**: Fix dependency chain to reflect that T001 and T003 are independent (not T001 → T003).
- **N4**: Reorder T013 wiring to check Pandoc before parseBookYaml.

**Proceed to `/devspark.implement`** — all gates are non-blocking.
