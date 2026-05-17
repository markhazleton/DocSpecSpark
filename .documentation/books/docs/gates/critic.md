```yaml
gate: critic
status: warn
blocking: false
severity: warning
summary: "Second-pass critic: 0 showstoppers. All prior 3 CRs and 2 HPs confirmed resolved. 3 new critical implementation traps identified: spawnSync maxBuffer overflow for verbose LaTeX builds, T007/T008 function coupling discards frontmatter title before resolveChapterTitle needs it, and double-TOC defect from book.md manual TOC + Pandoc --toc flag. 4 high-priority concerns. Proceed with caution — all are fixable within implementation without spec revision."
```

## Technical Risk Assessment — Second Pass

**Analysis Date:** 2026-04-22
**Pass:** 2 of 2 (post-plan-revision, post-tasks-regeneration)
**Risk Posture:** YELLOW
**Detected Stack:** Node.js 20 (ES Modules) + `child_process.spawnSync` + File System
**External Runtime Dependencies:** Pandoc (external binary) + LaTeX/pdflatex (MiKTeX / TeX Live)

---

### Executive Summary

All three critical risks from the first critic pass (CR-001 SC-001 warm-start SLO, CR-002 Zod passthrough misread, CR-003 missing `cover_image`) are confirmed resolved across spec.md, plan.md, research.md, tasks.md, and contracts/cli-contract.md. The feature is architecturally sound and no constitution violations exist.

However, three new critical implementation traps have emerged from closer examination of the function-level design in tasks.md and data-model.md: (1) `child_process.spawnSync` default `maxBuffer` will be exceeded by verbose LaTeX PDF output on large books, silently killing the process with ENOBUFS; (2) `stripFrontmatter()` (T007) discards the frontmatter object that `resolveChapterTitle()` (T008) requires — the function boundary design creates an unresolvable dependency unless explicitly addressed; and (3) `book.md` contains a manually assembled `## Table of Contents` section while `--toc` is passed to Pandoc, producing a visible duplicate TOC in all rendered formats.

These are implementation-level defects, not architectural ones. They can be addressed within the existing task descriptions without spec or plan revision.

---

### Prior Critic Pass Resolution Verification

| ID | Original Risk | Status | Evidence |
|----|--------------|--------|---------|
| CR-001 | SC-001 60-second SLO unfeasible under LaTeX cold-start | ✅ RESOLVED | spec.md SC-001 now qualified with warm-start; plan.md Technical Context updated; quickstart.md documents MiKTeX cold-start caveat |
| CR-002 | Zod `.passthrough()` misread; T017 was conditional | ✅ RESOLVED | research.md Decision 7 corrected with ⚠️ CORRECTION label; T016 reframed as audit; T017 made unconditional |
| CR-003 | `book.yaml` had no `cover_image` field; EPUB SC-002 at risk | ✅ RESOLVED | contracts/cli-contract.md has `cover_image` and `language` fields; T011 passes `--epub-cover-image` when defined; T014 creates placeholder cover.png |
| HP-002 | PDF engine not pinned; non-deterministic across platforms | ✅ RESOLVED | T011 and research.md Decision 5 now specify `--pdf-engine=pdflatex` |
| HP-003 | Slug argument used raw in file paths | ✅ RESOLVED | T005 adds `/^[a-z0-9-]+$/` regex validation |

---

### Showstopper Risks (Must Fix Before Implementation)

| ID | Category | Location | Risk Description | Likely Impact | Mitigation Required |
|----|----------|----------|------------------|---------------|---------------------|
| — | — | — | No SHOWSTOPPER risks detected. No constitution violations found. | — | — |

---

### Critical Risks (High Probability of Costly Issues)

| ID | Category | Location | Risk Description | Likely Impact | Recommended Action |
|----|----------|----------|------------------|---------------|--------------------|
| NEW-CR-001 | Node.js API / Silent Failure | tasks.md T011 | `child_process.spawnSync` default `maxBuffer` is 1 MB per stream. LaTeX (`pdflatex`) invoked internally by Pandoc produces verbose stdout/stderr output. For a 20-chapter book, pdflatex log output routinely exceeds 2–5 MB. When the buffer is exceeded Node.js throws ENOBUFS and kills the child process, but this manifests as a `spawnSync` error object with `status: null` and `signal: 'SIGTERM'` — not a clear user-visible error. T011 collects `spawnSync` failures but does not check for the ENOBUFS scenario specifically. | T015 verification on a large sample book will fail with an opaque error message. Developer will spend 30–120 minutes debugging what appears to be a Pandoc crash before discovering the maxBuffer limit. | In T011, add `maxBuffer: 20 * 1024 * 1024` (20 MB) to the `spawnSync` options object. Also check for `error.code === 'ENOBUFS'` in failure collection and emit a specific message: `"Error: Pandoc output exceeded buffer limit. This is a build script configuration issue, not a Pandoc error."` |
| NEW-CR-002 | Implementation Trap / Function Design | tasks.md T007, T008 | T007 defines `stripFrontmatter(markdownContent)` using regex to strip and return the body-only string. T008 defines `resolveChapterTitle(chapter, frontmatter)` which requires a parsed `frontmatter` object to access `frontmatter.title`. But T007 discards the parsed frontmatter — it only returns the stripped body. No task defines a `parseFrontmatter(content)` function that returns both `{body, matter}`. T009 calls both T007 and T008, but the data flow between them is unspecified. The developer will implement T007 as a pure strip function and T008 as a resolver, then realize at T009 that `frontmatter.title` is inaccessible — requiring refactor of T007 or an extra `gray-matter`/`js-yaml` parse call per chapter. | Mid-implementation rework at T009. Either T007 must be refactored to return `{body, frontmatter}` instead of just the body string, or a separate parse step must be added (duplicating file I/O or YAML parsing). Estimated 1–2 hour rework. | Revise T007 to: `stripFrontmatter(markdownContent)` returns `{ body: string, frontmatter: object }`. Update T008 to consume this shape. Update T009's chapter loop to destructure `const { body, frontmatter } = stripFrontmatter(content)`. This is a single-line signature change to T007 but must be done before implementation begins to avoid rework. |
| NEW-CR-003 | Content Quality / Double TOC | data-model.md (CompiledBook structure), tasks.md T009, T011 | `data-model.md` specifies `book.md` contains a `## Table of Contents` section with a manual bullet list of chapter titles. T011 also passes `--toc` to Pandoc for both EPUB3 and PDF. Pandoc `--toc` inserts its auto-generated TOC at the start of the rendered document. For PDF: the rendered document will have (1) the Pandoc auto-TOC page followed by (2) the `## Table of Contents` chapter from `book.md` content — two TOC pages visible to the reader. For EPUB: the `--toc` generates a navigation document (nav.xhtml) for sidebar navigation AND a TOC chapter appears in the body flow. This is a visible, structural quality defect in all output formats. | SC-002 requires Kindle Previewer zero structural errors. A duplicate TOC section in the EPUB body may trigger a validation warning. More importantly, the PDF output will be professionally embarrassing: two sequential TOC pages. US3 manual validation (T020–T021) will flag this. | Decision required: (A) Remove `--toc` from Pandoc flags and rely solely on the manually assembled TOC in `book.md`; OR (B) Remove the `## Table of Contents` section from T009's `book.md` assembly and rely solely on Pandoc `--toc`. Option B is recommended — Pandoc `--toc` generates a hyperlinked, properly formatted TOC from actual headings; the manual bullet list in `book.md` is redundant and fragile. Update data-model.md and T009 to remove the manual TOC section before T009 is implemented. |

---

### High-Priority Concerns

| ID | Category | Location | Issue | Impact | Suggestion |
|----|----------|----------|-------|--------|------------|
| NEW-HP-001 | Artifact Inconsistency | data-model.md lines ~65–68 | `data-model.md` Article section still states: "These fields flow through to `src/data/articles.json` via the existing `.passthrough()` schema in `generate-articles-json.mjs`." This is the exact incorrect statement that CR-002 corrected in research.md Decision 7 and tasks.md T016/T017. `data-model.md` was not updated as part of the plan revision. | Developer reads data-model.md during T016/T017 and sees the original incorrect passthrough claim, contradicting research.md. Creates confusion about whether T017 is truly necessary. Low probability of blocking implementation but erodes artifact trustworthiness. | Update data-model.md Article section to add: "⚠️ NOTE: These fields are NOT propagated automatically via Zod `.passthrough()`. The `article` output object in `generate-articles-json.mjs` uses explicit named properties — `book`, `book_title`, and `book_order` must be added explicitly (T017). See research.md Decision 7 correction." |
| NEW-HP-002 | Operational / DX | tasks.md T012 | T012 adds a Pandoc availability check (`pandoc --version`), but does NOT check for pdflatex/LaTeX availability. If Pandoc is installed but LaTeX is absent, the script proceeds to T011's PDF render step. Pandoc then fails internally with: `Error producing PDF. ! LaTeX Error: File not found` — a message that doesn't indicate the LaTeX installation prerequisite. This will be confusing for developers who have installed Pandoc but not LaTeX (a common scenario given HP-001's observation that LaTeX is not a standard developer dependency). | Developer sees Pandoc failure message, doubts their Pandoc installation, reinstalls Pandoc, fails again, and eventually discovers LaTeX is the missing dependency. Estimated 15–30 minutes of confusion. | Add a pdflatex availability check to T012 (alongside the Pandoc check): run `pdflatex --version` via `spawnSync`; if non-zero, emit: `"Error: pdflatex not found. Install TeX Live (Linux/macOS) or MiKTeX (Windows). See quickstart.md for installation instructions."` Only check if `book.output.formats` includes `"pdf"`. |
| NEW-HP-003 | Stale Guidance | tasks.md T022 | T022 (US3 validation remediation) says: "If EPUB3 structural errors are found: adjust Pandoc flags in `renderBook()` (e.g., add `--epub-cover-image`, `--metadata` flags) and rebuild until Kindle Previewer reports zero errors." Both `--epub-cover-image` and `--metadata lang:` are already implemented in T011. If T020 finds Kindle Previewer errors after a correct T011 implementation, following T022's guidance will cause the developer to search for code that needs to be added — only to find it already exists. | 30–60 minutes of wasted investigation during T022 remediation. The guidance contradicts the actual implementation state. | Rewrite T022 as: "If Kindle Previewer reports structural errors after T020: (1) verify `book.yaml` has a valid `cover_image` path and the file exists; (2) verify `--epub-cover-image` and `--metadata lang:` are present in the `renderBook()` epub invocation (already implemented in T011); (3) run `epubcheck books/publish/<slug>/book.epub` to identify any remaining structural issues beyond Kindle Previewer's validation." |
| NEW-HP-004 | Reproducibility | quickstart.md, contracts/cli-contract.md | Pandoc minimum version is not pinned anywhere. Pandoc 3.x changed EPUB3 metadata handling and `--epub-metadata` flag behavior vs. Pandoc 2.x. `--toc-title` option changed; `--epub-chapter-level` behavior differs. If a developer has Pandoc 2.19 and tests pass, a CI environment with Pandoc 3.2 may produce different EPUB structure. This was flagged in the prior critic's dependency risk table and remains unresolved. | Non-reproducible EPUB output across developer environments. Kindle Previewer validation result on one machine does not guarantee same result on another. | Add to quickstart.md Prerequisites: "Pandoc 2.19 or later (Pandoc 3.x recommended and tested)." Add to contracts/cli-contract.md dependency table: minimum Pandoc version. Pin in T012's availability check: parse `pandoc --version` output and warn if below 2.19. |

---

### Framework-Specific Red Flags

**Node.js `.mjs` build script checklist (updated pass 2):**

- [✅] Unhandled promise rejections — synchronous `spawnSync`; no async risk
- [✅] Shell injection — `spawnSync` with args-as-array; confirmed safe
- [✅] Slug input validation — `/^[a-z0-9-]+$/` added in T005 (HP-003 resolved)
- [⚠️] **`spawnSync` maxBuffer not configured** — default 1MB insufficient for LaTeX verbosity (NEW-CR-001)
- [✅] PDF engine pinned — `--pdf-engine=pdflatex` in T011 (HP-002 resolved)
- [⚠️] **Function return type mismatch** — `stripFrontmatter` returns string, `resolveChapterTitle` needs object (NEW-CR-002)
- [✅] Error aggregation — collect-all-failures pattern, exit non-zero with summary (FR-007/Q4)
- [⚠️] **LaTeX availability not checked** — pdflatex missing gives opaque Pandoc error (NEW-HP-002)
- [✅] Progress logging — `[book-publishing]` prefix, `console.log()` in scripts (§VII)

---

### Architecture Red Flags

- [❌] Over-engineered for stated requirements — No. Script is appropriately minimal.
- [❌] Under-engineered for implied scale — No. Single-developer workstation tool.
- [❌] Single point of failure without redundancy — No. Developer tool; no availability SLA.
- [⚠️] Missing cross-platform validation task — T015 verifies one machine only; Windows/macOS/Linux parity unverified.
- [✅] Async/concurrency handling — Synchronous script; no async hazards.
- [⚠️] **TOC strategy conflict** — manual TOC in book.md + Pandoc `--toc` produces duplicate output (NEW-CR-003)

---

### Missing Critical Tasks

- **Specify `spawnSync` options**: Add `maxBuffer: 20 * 1024 * 1024` and ENOBUFS check to T011
- **Resolve `stripFrontmatter` return type**: Update T007 before implementation to return `{body, frontmatter}`
- **Decide TOC strategy**: Remove manual TOC from T009 OR remove `--toc` from T011 (pick one)
- **Add pdflatex availability check**: Extend T012 to check LaTeX when PDF format requested
- **Correct data-model.md passthrough claim**: One-line fix to prevent developer confusion
- **Pin Pandoc minimum version**: Add to quickstart.md and T012 version check

---

### Questionable Assumptions

1. **"1MB is enough for spawnSync output"** (implicit in T011) → Why this will fail: LaTeX verbose output for a 20-chapter PDF build routinely exceeds 2–5 MB. The default `maxBuffer: 1 * 1024 * 1024` causes spawnSync to kill the child process with ENOBUFS. This produces `status: null, signal: 'SIGTERM'` in the result object — superficially identical to a legitimate Pandoc crash. Developer will waste significant time on a Node.js configuration issue disguised as a Pandoc problem.
2. **"`stripFrontmatter()` and `resolveChapterTitle()` are independent functions"** → Why this will fail: T008 signature is `resolveChapterTitle(chapter, frontmatter)` — it takes a parsed frontmatter object. T007 returns a stripped body string. At T009 integration, the developer must either (a) parse frontmatter separately before calling `stripFrontmatter`, (b) change T007 to return both, or (c) fall back to always using `chapter.title` or the filename. Option (c) silently breaks FR-004 (frontmatter title fallback) for any article without `chapter.title` set.
3. **"Pandoc `--toc` and manual TOC coexist cleanly"** → Why this will fail: Pandoc inserts its auto-generated TOC before the first heading; `book.md` also contains a `## Table of Contents` chapter. PDF output will show two distinct TOC pages to the reader. EPUB output will contain a "Table of Contents" body chapter alongside the navigation document TOC. Both are noticeable quality issues detectable at T020/T021 — causing rework loop.

---

### Dependencies Risk Assessment

| Dependency | Concern | Status |
|------------|---------|--------|
| Pandoc (external binary) | Version not pinned; 2.x vs 3.x EPUB3 metadata behavior differs | 🔴 Still unresolved (NEW-HP-004) |
| LaTeX / pdflatex | Not checked at startup; missing LaTeX produces opaque error | 🔴 Still unresolved (NEW-HP-002) |
| `js-yaml` | Lightweight, low risk; version unpinned (minor) | 🟡 Low risk |
| `spawnSync` (Node.js built-in) | maxBuffer default 1MB insufficient for LaTeX verbosity | 🔴 New finding (NEW-CR-001) |
| `gray-matter` / existing build scripts | No additional risk | ✅ No change |

---

### Estimated Technical Debt at Launch

- **Code Debt**: `spawnSync` without maxBuffer config; undefined frontmatter data flow between T007 and T008; manual TOC in book.md requiring manual maintenance on every build
- **Operational Debt**: No cross-platform build validation; pdflatex availability check absent; Pandoc version unpinned
- **Documentation Debt**: data-model.md passthrough claim uncorrected; T022 contains stale flag guidance
- **Testing Debt**: No automated tests for `generate-articles-json.mjs` book field propagation; single-platform T015 validation

---

### Metrics

- Showstopper Count: **0**
- Critical Risk Count: **3** (NEW-CR-001 through NEW-CR-003)
- High-Priority Concerns: **4** (NEW-HP-001 through NEW-HP-004)
- Prior Critic CRs Resolved: **3 of 3** (CR-001, CR-002, CR-003 all confirmed)
- Prior Critic HPs Resolved: **2 of 5** (HP-002 and HP-003 resolved; HP-001, HP-004, HP-005 accepted/documented)
- Missing Implementation Details: **3** (spawnSync maxBuffer, stripFrontmatter return type, TOC strategy)
- Stale Artifacts: **1** (data-model.md passthrough claim)

---

## GO/NO-GO RECOMMENDATION

```text
[ ] STOP - Showstoppers present, cannot proceed to implementation
[ ] CONDITIONAL - Fix critical risks first, then reassess
[x] PROCEED WITH CAUTION - Document acknowledged risks, add mitigation tasks
```

**Required Actions Before Starting T007/T008/T009 (Implementation-Level Fixes):**

1. **[NEW-CR-001] Add `maxBuffer: 20 * 1024 * 1024` to `spawnSync` options in T011.** Also add explicit ENOBUFS error detection in the failure collection block.

2. **[NEW-CR-002] Revise T007 return type before implementing it.** Change T007 signature: `stripFrontmatter(markdownContent)` → returns `{ body: string, frontmatter: object }`. Update T008 to receive the frontmatter object from T007's output. Update T009 chapter loop accordingly.

3. **[NEW-CR-003] Decide TOC strategy before implementing T009 and T011.** Recommended: remove the manual `## Table of Contents` section from `book.md` assembly in T009 and rely solely on Pandoc `--toc`. Update data-model.md CompiledBook structure to reflect the decision.

**Recommended Pre-Implementation Fixes (High Priority):**

- **[NEW-HP-001]** Update data-model.md Article section to correct the passthrough claim (one-line fix)
- **[NEW-HP-002]** Extend T012 to check pdflatex availability when PDF format is requested
- **[NEW-HP-003]** Rewrite T022 to reflect that `--epub-cover-image` and `--metadata` are already in T011
- **[NEW-HP-004]** Pin minimum Pandoc version in quickstart.md and add version check to T012
