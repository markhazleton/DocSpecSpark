"""
Rewrite low-scoring book chapters based on their remediation reports.

Reads:  remediation_results.json   (critique + editorial per chapter)
        books/{slug}/{chapter_file} (the chapter to rewrite)
Writes: books/{slug}/{chapter_file} (updated in place)
        books/rewrites/backups/{safe_id}_backup.md
        books/scoring/rewrite_results.json

Rewrite phases follow book-rewrite-plan methodology:
  Phase 1 — Structural fixes (argument, sections, transitions)
  Phase 2 — Core idea reinforcement (thesis clarity)
  Phase 3 — Narrative and engagement (opening, flow)
  Phase 4 — Voice and positioning (first-person, specificity)
  Phase 5 — Polish (banned phrases, conclusion)

Uses claude-sonnet-4-6 — quality matters for actual rewrites.

Safety:
  - Original always backed up before writing
  - Only body content rewritten; frontmatter preserved byte-for-byte
  - Resume-safe: skips chapters already rewritten (content_hash match)
  - --dry-run flag: shows prompt + token estimate without writing files

Run from project root:
    python books/scoring/rewrite_chapters.py
    python books/scoring/rewrite_chapters.py --dry-run

Requires ANTHROPIC_API_KEY in environment or .env at project root.
"""

import hashlib
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────

REWRITE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS    = 8192

REMEDIATION_FILE = Path("books/scoring/remediation_results.json")
REWRITE_FILE     = Path("books/scoring/rewrite_results.json")
BOOKS_DIR        = Path("books")
BACKUP_DIR       = Path("books/rewrites/backups")

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a skilled editor rewriting book chapters for Mark Hazleton, a solutions architect.
Fix specific quality problems identified in a remediation report while preserving every
piece of factual content, technical detail, and code.

━━━ MARK'S VOICE — THE AUTHORITY ━━━

Mark writes in first person ("I") about real problems he encountered and solved.
His voice is exploratory, not prescriptive. He shares trade-offs and honest observations
grounded in project experience — never generic best-practice advice.

REQUIRED PATTERNS (use throughout):
  "in my experience"          "on a recent project"        "in practice"
  "the trade-off here"        "what I've found"            "I've noticed"
  "I've watched"              "I've been"                   "one approach I"
  "raises an interesting question"   "what I've learned"

PROHIBITED — delete or rewrite every instance:
  Chapter openers:
    "In this chapter..."   "This chapter will..."   "We will explore..."
    "We'll cover..."   "What you'll learn:"   "Learning objectives:"
  Words/phrases:
    "revolutionize" / "revolutionizing"   "game-changer" / "game changer"
    "paradigm shift"   "leverage" (as verb)   "empower"   "transformative"
    "groundbreaking"   "innovative"   "advanced strategies"
    "industry best practices"   "synergize"   "you must"   "one should always"
  Structural violations:
    "Key Takeaways" heading — convert bullets to 1–2 paragraphs of prose
    Learning objectives box at chapter start — remove it
    Passive conclusion ("In this chapter we covered…") — rewrite as forward-looking prose

━━━ BOOK REWRITE PHASING ━━━
Apply fixes in this order (from the rewrite plan):
  Phase 1 — Structural: argument structure, section ordering, missing transitions
  Phase 2 — Core idea: clarify or strengthen the chapter thesis
  Phase 3 — Narrative: rewrite opening with real problem/tension; improve flow
  Phase 4 — Voice: first-person, specific dates/tools/names, eliminate "we"
  Phase 5 — Polish: remove every remaining banned phrase; tighten conclusion

━━━ OUTPUT CONTRACT ━━━
Return ONLY the rewritten body content.
- No frontmatter (YAML between --- delimiters)
- No explanatory prose before or after
- No markdown code fences wrapping the output
- Start directly with the first line of body content
- Preserve blank lines between sections as in the original
- Preserve all internal links, image references, and markdown syntax
- Preserve all code examples exactly
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


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    fm   = text[:end + 4]
    body = text[end + 4:].lstrip("\n")
    return fm, body


def build_rewrite_instructions(record: dict) -> str:
    critique  = record.get("critique", {})
    editorial = record.get("editorial", {})
    structure = record.get("structure", {})
    scores    = record.get("scores", {})

    lines = [
        f"CHAPTER: {record['chapter_id']}",
        f"Book: {record.get('book_title', '')}",
        f"Title: {record.get('title', '')}",
        f"Current overall score: {record['overall']}/5.0",
        f"Scores: arc={scores.get('narrative_arc',0)}"
        f" arg={scores.get('argument_quality',0)}"
        f" clarity={scores.get('clarity',0)}"
        f" signal={scores.get('signal_ratio',0)}"
        f" structure={scores.get('structure',0)}",
        "",
        "━━━ REWRITE INSTRUCTIONS ━━━",
        "",
        "CHAPTER THESIS (what it's trying to argue):",
        critique.get("chapter_thesis", "—"),
        "",
        "CORE GAP (the central problem):",
        critique.get("core_gap", "—"),
        "",
        "ALTITUDE NOTE:",
        critique.get("altitude_note", "—"),
        "",
        "PRIORITY FIXES (apply in phase order):",
    ]

    for i, p in enumerate(editorial.get("priorities", []), 1):
        lines.append(f"  {i}. {p}")

    lines += ["", "SPECIFIC ISSUES WITH EXACT FIXES:"]
    for issue in critique.get("issues", []):
        lines += [
            "",
            f"  [{issue.get('name', 'Issue')}] — {issue.get('lens', '')} lens",
            f"  Problem: {issue.get('problem', '')}",
            f"  Why it matters: {issue.get('why_it_matters', '')}",
            f"  Fix: {issue.get('fix', '')}",
        ]

    flags = editorial.get("flags", [])
    if flags:
        lines += ["", "EXACT PHRASES TO CHANGE:"]
        for f in flags:
            if f.get("type") == "Negative":
                lines.append(f"  REPLACE: \"{f.get('phrase', '')}\"")
                lines.append(f"  WITH:    {f.get('action', '')}")
                lines.append("")

    must_fix = structure.get("must_fix", [])
    if must_fix:
        lines += ["", "STRUCTURAL FIXES:"]
        for s in must_fix:
            lines.append(f"  - {s}")

    lines += ["", "━━━ CHAPTER BODY TO REWRITE ━━━", ""]
    return "\n".join(lines)


def call_rewrite(client: anthropic.Anthropic, instructions: str, body: str) -> tuple[str, dict]:
    response = client.messages.create(
        model=REWRITE_MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": instructions + body}],
    )

    usage = {
        "input_tokens":          response.usage.input_tokens,
        "output_tokens":         response.usage.output_tokens,
        "cache_creation_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
        "cache_read_tokens":     getattr(response.usage, "cache_read_input_tokens", 0),
    }

    rewritten = response.content[0].text.strip()
    if rewritten.startswith("```"):
        rewritten = rewritten.split("```")[1]
        if rewritten.startswith(("markdown", "md")):
            rewritten = rewritten.split("\n", 1)[1]
        rewritten = rewritten.strip()

    return rewritten, usage


def estimate_tokens(text: str) -> int:
    return len(text) // 4


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    dry_run = "--dry-run" in sys.argv

    load_env()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to .env at project root.")
        sys.exit(1)

    if not REMEDIATION_FILE.exists():
        print(f"ERROR: {REMEDIATION_FILE} not found. Run remediate_chapters.py first.")
        sys.exit(1)

    remediation: list[dict] = json.loads(REMEDIATION_FILE.read_text(encoding="utf-8"))

    rewrite_results: dict[str, dict] = {}
    if REWRITE_FILE.exists():
        try:
            for item in json.loads(REWRITE_FILE.read_text(encoding="utf-8")):
                rewrite_results[item["chapter_id"]] = item
        except (json.JSONDecodeError, KeyError):
            pass

    to_process: list[dict] = []
    skip_count = 0
    for record in remediation:
        cid       = record["chapter_id"]
        book_slug = record.get("book_slug", cid.split("/")[0])
        chapter_file = None

        # Locate the markdown file via the remediation record
        # chapter_id format: {book_slug}/{chapter_stem}
        chapter_stem = cid.split("/", 1)[1] if "/" in cid else cid
        book_dir = BOOKS_DIR / book_slug

        # Search common locations
        candidates = [
            book_dir / "chapters" / f"{chapter_stem}.md",
            book_dir / f"{chapter_stem}.md",
        ]
        # Also search subdirectories one level deep
        if book_dir.is_dir():
            for subdir in book_dir.iterdir():
                if subdir.is_dir():
                    candidates.append(subdir / f"{chapter_stem}.md")

        md_path = next((p for p in candidates if p.exists()), None)
        if not md_path:
            print(f"  SKIP {cid} — markdown file not found")
            continue

        current_text = md_path.read_text(encoding="utf-8", errors="replace")
        current_hash = hashlib.md5(current_text.encode("utf-8")).hexdigest()

        prev = rewrite_results.get(cid, {})
        if prev.get("rewritten_hash") == current_hash:
            skip_count += 1
            continue

        to_process.append({
            **record,
            "_md_path":      md_path,
            "_current_text": current_text,
        })

    mode_label = "DRY RUN — " if dry_run else ""
    print(f"{mode_label}Chapters in remediation queue: {len(remediation)}")
    print(f"Already rewritten (hash match): {skip_count}")
    print(f"To rewrite:                     {len(to_process)}")

    if not to_process:
        print("\nAll remediated chapters already rewritten.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic(api_key=api_key)
    today  = date.today().strftime("%Y-%m-%d")

    total_input = total_output = total_cache_cr = total_cache_rd = 0

    for idx, record in enumerate(to_process, 1):
        cid      = record["chapter_id"]
        md_path  = record["_md_path"]
        original = record["_current_text"]

        fm, body = split_frontmatter(original)
        instructions = build_rewrite_instructions(record)

        est_in  = estimate_tokens(SYSTEM_PROMPT + instructions + body)
        est_out = estimate_tokens(body)

        print(f"\n[{idx}/{len(to_process)}] {cid}  (overall={record['overall']})")
        print(f"  body:    {len(body):,} chars  ~{estimate_tokens(body):,} tokens")
        print(f"  est in:  ~{est_in:,} tokens  |  est out: ~{est_out:,} tokens")

        if dry_run:
            print("  [DRY RUN] Would call API here — skipping.")
            print("  Instructions preview:")
            for line in instructions.splitlines()[:20]:
                print(f"    {line}")
            print("    ...")
            continue

        try:
            rewritten_body, usage = call_rewrite(client, instructions, body)

            total_input    += usage["input_tokens"]
            total_output   += usage["output_tokens"]
            total_cache_cr += usage["cache_creation_tokens"]
            total_cache_rd += usage["cache_read_tokens"]

            print(
                f"  tokens  in={usage['input_tokens']:,}"
                f"  out={usage['output_tokens']:,}"
                f"  cache_cr={usage['cache_creation_tokens']:,}"
                f"  cache_rd={usage['cache_read_tokens']:,}"
            )

            ratio = len(rewritten_body) / max(len(body), 1)
            if ratio < 0.5 or ratio > 2.0:
                print(f"  WARNING: body ratio {ratio:.2f} unusual "
                      f"({len(body):,} → {len(rewritten_body):,} chars)")

            # Backup
            safe_id     = cid.replace("/", "_")
            backup_path = BACKUP_DIR / f"{safe_id}_backup.md"
            backup_path.write_text(original, encoding="utf-8")
            print(f"  backup:  {backup_path}")

            # Write updated chapter
            updated = (fm + "\n\n" + rewritten_body + "\n") if fm else (rewritten_body + "\n")
            md_path.write_text(updated, encoding="utf-8")
            print(f"  written: {md_path}")

            new_hash = hashlib.md5(updated.encode("utf-8")).hexdigest()
            rewrite_results[cid] = {
                "chapter_id":      cid,
                "book_slug":       record.get("book_slug", ""),
                "title":           record.get("title", ""),
                "original_score":  record["overall"],
                "rewritten_date":  today,
                "rewritten_hash":  new_hash,
                "original_hash":   record.get("content_hash"),
                "usage":           usage,
            }

            REWRITE_FILE.write_text(
                json.dumps(list(rewrite_results.values()), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        except anthropic.APIError as e:
            print(f"  API ERROR: {e}")
            time.sleep(15)

        if idx < len(to_process):
            time.sleep(2)

    if dry_run:
        print(f"\n[DRY RUN complete — no files written]")
        return

    rewritten_count = len([v for v in rewrite_results.values() if "rewritten_hash" in v])
    print(f"\n{'-'*60}")
    print(f"Done. {rewritten_count} chapters rewritten.")
    print(f"Backups:  {BACKUP_DIR}/")
    print(f"Progress: {REWRITE_FILE}")
    print(f"\nToken usage (this run):")
    print(f"  Input:           {total_input:,}")
    print(f"  Output:          {total_output:,}")
    print(f"  Cache creation:  {total_cache_cr:,}")
    print(f"  Cache reads:     {total_cache_rd:,}")
    print(f"\nNEXT STEP: Re-score the rewritten chapters:")
    print(f"  python books/scoring/run_book_scoring.py")


if __name__ == "__main__":
    main()
