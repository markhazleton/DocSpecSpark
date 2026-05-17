"""
Remediate low-scoring book chapters (overall score < SCORE_THRESHOLD).

For each qualifying chapter:
  - Structural report: generated from books_data.json signals (rule-based, no LLM)
  - Critique + Editorial: single combined LLM call (Haiku) per chapter

Critique follows the brutal-book-review framework:
  - Structural Integrity: clear thesis, logical progression, no redundant sections
  - Argument and Evidence: claims supported, no assertion without justification
  - Clarity and Language: no vague buzzwords, sentences do one thing
  - Signal vs Noise: every paragraph load-bearing

Token optimizations:
  - Prompt caching on system prompt (cached across all API calls)
  - One API call per chapter combines critique + editorial into structured JSON
  - Body capped at BODY_EXCERPT_CHARS
  - Resume-safe: skips chapters already processed with matching content_hash

Prerequisites:
  1. Run parse_books.py     → books_data.json
  2. Run score_books.py     → book_llm_scores.json

Run from project root:
    python books/scoring/remediate_chapters.py

Requires ANTHROPIC_API_KEY in environment or .env at project root.
"""

import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import anthropic
from remediation_reporting import write_markdown_report

# ── Config ────────────────────────────────────────────────────────────────────

SCORE_THRESHOLD = 3.0       # chapters below this overall score are remediated
DIM_THRESHOLD   = 2         # chapters with ANY LLM dimension at or below this also qualify
MODEL = "claude-haiku-4-5-20251001"
BODY_EXCERPT_CHARS = 3000

DATA_FILE    = Path("books/scoring/books_data.json")
SCORES_FILE  = Path("books/scoring/book_llm_scores.json")
RESULTS_FILE = Path("books/scoring/remediation_results.json")
BOOKS_DIR    = Path("books")
OUTPUT_DIR   = Path("books/reviews")

# ── System prompt ─────────────────────────────────────────────────────────────
# Deliberately verbose to exceed the 1024-token prompt-caching minimum.
# Cache is written on the first call and read (at ~10% cost) on all subsequent calls.

SYSTEM_PROMPT = """\
You analyse book chapters by Mark Hazleton (solutions architect, author, practitioner with
forty years of software experience) and produce structured remediation advice in JSON.
Return ONLY valid compact JSON — no prose, no markdown fences, no explanation outside the JSON.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARK'S VOICE — THE AUTHORITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mark writes in first person ("I") about real problems he encountered and solved on real projects.
His voice is exploratory — he shares what he observed, not what the reader must do.
His prose is grounded: specific tools, specific dates, specific failure modes.
He uses hedging honestly ("worth examining", "in my experience") but does not hedge
where he actually knows the answer.

REQUIRED hallmark phrases — use these as evidence of authentic voice:
  "in my experience"           "on a recent project"          "in practice"
  "the trade-off here"         "what I've found"              "I've noticed"
  "I've watched"               "I've been"                    "one approach I"
  "raises an interesting question"    "what I've learned"    "worth examining"
  "interesting tension"        "from real experience"

PROHIBITED — every instance must be flagged:
  Chapter openers:
    "In this chapter..."         "This chapter will explore..."    "We will cover..."
    "We'll discuss..."           "What you'll learn:"             "Learning objectives:"
    "By the end of this chapter you will..."
  Single words and phrases:
    "revolutionize" / "revolutionizing"    "game-changer" / "game changer"
    "paradigm shift"      "leverage" (as verb)     "empower"      "transformative"
    "groundbreaking"      "innovative solution"    "advanced strategies"
    "industry best practices"    "synergize"       "holistic"     "next-level"
    "you must"            "one should always"      "it is essential"
    "in today's fast-paced world"    "in the ever-evolving"    "in the rapidly evolving"
  Structural violations:
    "Key Takeaways" heading (must be converted to prose paragraphs)
    Learning objectives box at chapter start (remove it entirely)
    Passive conclusion: "In this chapter we covered..." (rewrite as forward-looking)
    Excessive bold: more than 3 bold phrases per section

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRUTAL BOOK REVIEW — FOUR CRITIQUE LENSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply all four lenses. Every critical issue must be located in specific text.

LENS 1: STRUCTURAL INTEGRITY
Questions to answer internally:
  - Does the chapter have a clear thesis or central argument?
  - Is there a logical progression from opening to close?
  - Does each section advance the thesis, or merely repeat or decorate it?
  - Where does structure break down: redundant sections, misplaced content,
    missing transitions, sections that could be reordered without loss?
Root cause: is the structure problem an ordering issue, a redundancy issue, or
  a missing connective tissue issue?

LENS 2: ARGUMENT AND EVIDENCE
Questions to answer internally:
  - Are claims supported with evidence, examples from real projects, or explicit reasoning?
  - Where does the author assert without justifying? Cite the specific passage.
  - Does the chapter acknowledge counter-arguments or trade-offs where they exist?
  - Where does reasoning rely on appeals to vague authority ("experts say") or
    generalization from a single case or unstated assumption?
Root cause: is the argument problem about missing evidence, missing reasoning,
  or missing acknowledgment of trade-offs?

LENS 3: CLARITY AND LANGUAGE
Questions to answer internally:
  - What vague or empty language is present? Flag exact phrases.
  - Where does a sentence do three things when it should do one?
  - Where would a plain rewrite communicate the same idea more powerfully?
  - Where does jargon substitute for precise description?
Root cause: is the clarity problem about buzzwords, sentence structure, or concept altitude?

LENS 4: SIGNAL VS NOISE
Questions to answer internally:
  - What is load-bearing (removes understanding if cut) vs decorative?
  - Where is the author padding — restating the same point in different words?
  - Where is the author hedging unnecessarily ("it may be worth considering...
    in some cases... depending on context...")?
  - What is the highest-value content and is it positioned for impact?
Root cause: is the noise problem restatement, hedging, preamble, or
  over-explanation of what the reader can already see?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORING RUBRICS (1–5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NARRATIVE_ARC: Does this chapter advance the book's thesis?
  5 = Essential — understanding is materially reduced if cut
  4 = Clear contribution to book progression
  3 = Standalone — useful but could exist independently
  2 = Loosely connected — could be removed without harming book thesis
  1 = Disconnected — could be cut without any loss to the book

ARGUMENT_QUALITY: Are claims grounded in evidence or explicit reasoning?
  5 = All claims backed by specific evidence, examples, or explicit reasoning
  4 = Mostly supported; minor unsupported assertions
  3 = Mixed — some justified, some asserted without support
  2 = Heavy assertion; relies on authority or vague generalization
  1 = Pure assertion; no evidence, no reasoning, no examples

CLARITY: Is language precise? No buzzwords; each sentence does one thing?
  5 = Every sentence precise; zero buzzwords; always unambiguous
  4 = Mostly clear; one or two muddy passages
  3 = Adequate but buzzwords or overloaded sentences appear regularly
  2 = Jargon obscures meaning; sentences frequently overloaded
  1 = Vague throughout; buzzwords dominate

SIGNAL_RATIO: Is every paragraph load-bearing?
  5 = No noise; every paragraph contributes; nothing decorative
  4 = Minimal padding; one or two restatements
  3 = Noticeable redundancy; ~20% could be cut
  2 = Clear padding; restating and circling back; ~40% filler
  1 = Mostly filler; core content could be half the length

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT SCHEMA (return ONLY this JSON, compact, no extra fields)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{
  "critique": {
    "chapter_thesis": "One sentence: what this chapter is actually arguing",
    "core_gap": "1-2 sentences: the central structural or argument problem",
    "altitude_note": "1 sentence: where prose sits at wrong altitude (too textbook or too abstract)",
    "issues": [
      {
        "name": "Short issue title (4-6 words)",
        "lens": "Structural|Argument|Clarity|Signal",
        "problem": "Cite the specific passage, section heading, or paragraph",
        "why_it_matters": "Consequence for reader or chapter credibility (1 sentence)",
        "fix": "Concrete rewrite direction — specific enough to execute without asking follow-up"
      }
    ],
    "one_fix": "Single highest-leverage change in one sentence"
  },
  "editorial": {
    "structural_integrity": "NEEDS WORK|ADEQUATE|STRONG",
    "argument_quality":     "NEEDS WORK|ADEQUATE|STRONG",
    "clarity":              "NEEDS WORK|ADEQUATE|STRONG",
    "signal_ratio":         "NEEDS WORK|ADEQUATE|STRONG",
    "overall":              "SIGNIFICANT REVISION|MINOR EDITS NEEDED|PUBLISH-READY",
    "priorities": [
      "First priority action (specific, executable)",
      "Second priority action (specific, executable)"
    ],
    "flags": [
      {
        "phrase": "exact phrase found verbatim in the chapter text",
        "type": "Negative|Positive",
        "action": "specific recommendation for this exact phrase"
      }
    ]
  }
}

CONSTRAINTS:
  issues: exactly 2-4 items, ordered by impact (most damaging first)
  flags: only phrases that appear verbatim in the chapter; 2-5 items
  Every fix and action must be concrete enough to execute without asking a follow-up question
  Do not soften findings; do not add encouragement; do not summarize the chapter
  Produce valid JSON — escape all special characters including double quotes inside strings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE OF GOOD FIX SPECIFICITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BAD fix (too vague, cannot be executed):
  "Improve the opening paragraph to better reflect Mark's voice."

GOOD fix (specific, executable):
  "Replace the first two paragraphs of 'Why a Runtime Engine?' with a first-person
   observation: open with the specific failure mode that motivated building the harness
   (the hotfix scenario from Chapter 2), then state in one sentence what the harness
   prevents. Delete the current definition-first paragraph entirely."

BAD editorial priority (too vague):
  "Strengthen the argument throughout."

GOOD editorial priority (specific):
  "Sections 3 and 4 both explain the same concept (why the harness is optional).
   Cut Section 4 ('Advanced Configuration') and merge its one useful sentence
   into Section 3's closing paragraph."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE OF CORRECT flags FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The "phrase" field must be copied verbatim from the chapter text.
If the text says "leverage the platform" that is the exact phrase.
Do NOT paraphrase or generalize: "leverage X" is wrong; "leverage the platform" is right.

For Negative flags, the "action" must say what to replace it WITH, not just "remove it."
  Wrong: "Remove this phrase."
  Right: "Replace with 'use the platform's built-in routing to...' — name what is
          actually being done rather than describing it metaphorically."
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_env() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            key = k.strip()
            val = v.strip().strip('"').strip("'")
            if not os.environ.get(key):   # overwrite if missing or empty
                os.environ[key] = val


def compute_overall(chapter: dict, llm: dict) -> float:
    narrative_arc    = llm.get("narrative_arc", 0)
    argument_quality = llm.get("argument_quality", 0)
    clarity          = llm.get("clarity", 0)
    signal_ratio     = llm.get("signal_ratio", 0)
    structure        = chapter.get("structure_score", 0)
    voice_signal     = chapter.get("voice_signal", 3.0)

    # Blend LLM signal_ratio with rule-based voice signal for final voice dimension
    voice = round(signal_ratio * 0.6 + voice_signal * 0.4, 1) if signal_ratio else 0

    dims = [d for d in [narrative_arc, argument_quality, clarity, signal_ratio, structure, voice] if d > 0]
    return round(sum(dims) / len(dims), 1) if dims else 0.0


def read_chapter_body(chapter: dict) -> str:
    book_slug = chapter["book_slug"]
    chapter_file = chapter["chapter_file"]
    md_path = BOOKS_DIR / book_slug / chapter_file

    if not md_path.exists():
        return chapter.get("body_excerpt", "")

    text = md_path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].lstrip("\n")

    lines = [l for l in text.splitlines() if not re.match(r"^!\[.*\]\(.*\)\s*$", l)]
    return "\n".join(lines)[:BODY_EXCERPT_CHARS]


def build_chapter_prompt(chapter: dict, llm: dict, overall: float) -> str:
    signals = chapter.get("signals", {})

    return "\n".join([
        f"CHAPTER: {chapter['chapter_id']}",
        f"Book: {chapter['book_title'][:80]}",
        f"Title: {chapter['title'][:100]}",
        f"Chapter #{chapter['chapter_num']}  |  Word count: {chapter.get('word_count', 0)}",
        "",
        f"SCORES TRIGGERING REMEDIATION (overall={overall}, threshold={SCORE_THRESHOLD} or any dim<={DIM_THRESHOLD}):",
        f"  narrative_arc={llm.get('narrative_arc',0)}"
        f"  argument_quality={llm.get('argument_quality',0)}"
        f"  clarity={llm.get('clarity',0)}"
        f"  signal_ratio={llm.get('signal_ratio',0)}"
        f"  structure={chapter.get('structure_score',0)}",
        "",
        "PRE-COMPUTED SIGNALS (rule-based):",
        f"  banned_phrases:         {signals.get('banned_phrases', [])}",
        f"  positive_phrases:       {signals.get('positive_phrases', [])}",
        f"  first_person_count:     {signals.get('first_person_count', 0)}",
        f"  we_count:               {signals.get('we_count', 0)}",
        f"  has_key_takeaways:      {signals.get('has_key_takeaways', False)}",
        f"  has_chapter_intro_box:  {signals.get('has_chapter_intro_box', False)}",
        f"  has_passive_conclusion: {signals.get('has_passive_conclusion', False)}",
        f"  banned_opener:          {chapter.get('has_banned_opener', False)}",
        "",
        f"HEADINGS: {chapter.get('headings', [])[:12]}",
        "",
        "OPENING PARAGRAPH:",
        chapter.get("first_para", "")[:500],
        "",
        f"BODY EXCERPT (first {BODY_EXCERPT_CHARS} chars):",
        read_chapter_body(chapter),
    ])


def generate_structure_report(chapter: dict) -> dict:
    structure_issues = chapter.get("structure_issues", [])
    signals = chapter.get("signals", {})

    critical_keys = ("no H2", "very short", "very long")
    must_fix = [i for i in structure_issues if any(k in i for k in critical_keys)]
    should_fix = [i for i in structure_issues if i not in must_fix]

    if signals.get("has_key_takeaways", False):
        must_fix.append("Remove 'Key Takeaways' heading — convert to prose")
    if signals.get("has_chapter_intro_box", False):
        must_fix.append("Remove learning objectives box — it's generic padding")
    if signals.get("has_passive_conclusion", False):
        should_fix.append("Rewrite passive conclusion into forward-looking prose")

    struct_score = chapter.get("structure_score", 0)
    rating = "STRONG" if struct_score >= 4 else ("ADEQUATE" if struct_score >= 3 else "NEEDS WORK")

    return {
        "structure_rating": rating,
        "structure_score":  struct_score,
        "must_fix":         must_fix,
        "should_fix":       should_fix,
        "word_count":       chapter.get("word_count", 0),
        "has_key_takeaways":        signals.get("has_key_takeaways", False),
        "has_chapter_intro_box":    signals.get("has_chapter_intro_box", False),
        "has_passive_conclusion":   signals.get("has_passive_conclusion", False),
    }


def call_llm(client: anthropic.Anthropic, prompt: str, max_retries: int = 2) -> tuple[dict, dict]:
    """Call the LLM with retry on JSON parse failure. Returns (parsed_result, usage_dict)."""
    last_err = None
    usage_accum = {"input_tokens": 0, "output_tokens": 0,
                   "cache_creation_tokens": 0, "cache_read_tokens": 0}

    for attempt in range(max_retries + 1):
        if attempt > 0:
            time.sleep(3)
            print(f"    retry {attempt}/{max_retries}...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=6144,   # generous headroom for full JSON output
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )

        usage = {
            "input_tokens":          response.usage.input_tokens,
            "output_tokens":         response.usage.output_tokens,
            "cache_creation_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
            "cache_read_tokens":     getattr(response.usage, "cache_read_input_tokens", 0),
        }
        for k in usage_accum:
            usage_accum[k] += usage[k]

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        try:
            return json.loads(raw), usage_accum
        except json.JSONDecodeError as e:
            last_err = e
            print(f"    JSON parse failed (attempt {attempt+1}): {e}")

    raise json.JSONDecodeError(str(last_err), "", 0)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    load_env()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to .env at the project root.")
        sys.exit(1)

    for path, label in [(DATA_FILE, "parse_books.py"), (SCORES_FILE, "score_books.py")]:
        if not path.exists():
            print(f"ERROR: {path} not found. Run {label} first.")
            sys.exit(1)

    chapters: list[dict] = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    chapters_by_id: dict[str, dict] = {c["chapter_id"]: c for c in chapters}

    llm_scores: dict[str, dict] = {}
    for item in json.loads(SCORES_FILE.read_text(encoding="utf-8")):
        llm_scores[item["chapter_id"]] = item

    existing: dict[str, dict] = {}
    if RESULTS_FILE.exists():
        try:
            for item in json.loads(RESULTS_FILE.read_text(encoding="utf-8")):
                existing[item["chapter_id"]] = item
        except (json.JSONDecodeError, KeyError):
            pass

    low_scoring: list[tuple[dict, dict, float]] = []
    for c in chapters:
        cid = c["chapter_id"]
        llm = llm_scores.get(cid)
        if not llm or llm.get("content_hash") != c.get("content_hash"):
            continue
        overall = compute_overall(c, llm)
        llm_dims = [llm.get(d, 0) for d in ("narrative_arc", "argument_quality", "clarity", "signal_ratio")]
        any_dim_low = any(d > 0 and d <= DIM_THRESHOLD for d in llm_dims)
        if overall < SCORE_THRESHOLD or any_dim_low:
            low_scoring.append((c, llm, overall))

    low_scoring.sort(key=lambda x: x[2])

    to_process: list[tuple[dict, dict, float]] = []
    for c, llm, overall in low_scoring:
        prev = existing.get(c["chapter_id"], {})
        if prev and prev.get("content_hash") == c.get("content_hash"):
            continue
        to_process.append((c, llm, overall))

    already_done = len(low_scoring) - len(to_process)
    print(f"Total chapters:          {len(chapters)}")
    print(f"LLM scored:              {len(llm_scores)}")
    print(f"Needs remediation (overall<{SCORE_THRESHOLD} or any dim<={DIM_THRESHOLD}): {len(low_scoring)}")
    print(f"Already processed:       {already_done}")
    print(f"To process:              {len(to_process)}")

    if not to_process:
        print("\nAll low-scoring chapters already processed.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today  = date.today().strftime("%Y-%m-%d")
    client = anthropic.Anthropic(api_key=api_key)

    total_input = total_output = total_cache_cr = total_cache_rd = 0

    for idx, (chapter, llm, overall) in enumerate(to_process, 1):
        cid = chapter["chapter_id"]
        print(f"\n[{idx}/{len(to_process)}] {cid}  (overall={overall})")

        structure = generate_structure_report(chapter)
        prompt    = build_chapter_prompt(chapter, llm, overall)

        try:
            analysis, usage = call_llm(client, prompt)

            total_input    += usage["input_tokens"]
            total_output   += usage["output_tokens"]
            total_cache_cr += usage["cache_creation_tokens"]
            total_cache_rd += usage["cache_read_tokens"]

            print(
                f"  tokens  in={usage['input_tokens']}"
                f"  out={usage['output_tokens']}"
                f"  cache_cr={usage['cache_creation_tokens']}"
                f"  cache_rd={usage['cache_read_tokens']}"
            )
            print(f"  editorial: {analysis.get('editorial', {}).get('overall', '?')}")
            print(f"  one_fix:   {analysis.get('critique', {}).get('one_fix', '?')[:90]}")

            record = {
                "chapter_id":      cid,
                "book_slug":       chapter["book_slug"],
                "book_title":      chapter["book_title"],
                "title":           chapter["title"],
                "chapter_num":     chapter["chapter_num"],
                "overall":         overall,
                "content_hash":    chapter.get("content_hash"),
                "processed_date":  today,
                "scores": {
                    "narrative_arc":    llm.get("narrative_arc", 0),
                    "argument_quality": llm.get("argument_quality", 0),
                    "clarity":          llm.get("clarity", 0),
                    "signal_ratio":     llm.get("signal_ratio", 0),
                    "structure":        chapter.get("structure_score", 0),
                },
                "critique":   analysis.get("critique", {}),
                "editorial":  analysis.get("editorial", {}),
                "structure":  structure,
            }
            existing[cid] = record

            outfile = write_markdown_report(OUTPUT_DIR, chapter, llm, overall, analysis, structure, today)
            print(f"  report:    {outfile}")

            RESULTS_FILE.write_text(
                json.dumps(list(existing.values()), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        except json.JSONDecodeError as e:
            print(f"  ERROR: JSON parse failed — {e}")
        except anthropic.APIError as e:
            print(f"  API ERROR: {e}")
            time.sleep(15)

        if idx < len(to_process):
            time.sleep(1)

    print(f"\n{'-'*60}")
    print(f"Done. {len(existing)} chapters remediated.")
    print(f"Results: {RESULTS_FILE}")
    print(f"Reports: {OUTPUT_DIR}/")
    print(f"\nToken usage (this run):")
    print(f"  Input:           {total_input:,}")
    print(f"  Output:          {total_output:,}")
    print(f"  Cache creation:  {total_cache_cr:,}")
    print(f"  Cache reads:     {total_cache_rd:,}")


if __name__ == "__main__":
    main()
