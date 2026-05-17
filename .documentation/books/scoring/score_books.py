"""
Step 2: LLM scoring of chapter quality dimensions using Anthropic SDK.
Reads books_data.json, writes book_llm_scores.json.

Scores 4 dimensions that require judgment:
  narrative_arc    — does the chapter advance the book's argument/story?
  argument_quality — are claims supported with evidence or reasoning?
  clarity          — language precision; no vague buzzwords
  signal_ratio     — every paragraph load-bearing; minimal noise/padding

Structure is pre-computed (rule-based) in parse_books.py.

Resume-safe: skips chapter_ids already present with matching content_hash.

Run from project root:
    python books/scoring/score_books.py

Requires ANTHROPIC_API_KEY in environment or a .env file at project root.
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic

DATA_FILE = Path("books/scoring/books_data.json")
SCORES_FILE = Path("books/scoring/book_llm_scores.json")

BATCH_SIZE = 6    # 6 chapters/batch: good amortization without risking output truncation
MODEL = "claude-haiku-4-5-20251001"
# NOTE: claude-haiku-4-5-20251001 does not support ephemeral prompt caching
# (cache_control blocks are accepted but produce no cache tokens).
# The main token-saving strategy is the content-hash resume system: chapters are
# only re-scored when their markdown content changes.

# Deliberately verbose to exceed the 1024-token prompt-caching minimum for Haiku.
# The cache is created on the first call and read (at ~10% cost) on every subsequent call.
SYSTEM_PROMPT = """You are a rigorous literary critic scoring book chapters for Mark Hazleton,
a solutions architect, author, and practitioner with forty years of software engineering experience.
Your job is to score chapters across four quality dimensions with honesty and precision.
Reserve top scores for genuinely exceptional work. Most chapters score 2-4, not 5.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARK'S VOICE AND WRITING STANDARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mark writes in first person ("I") exclusively. No "we", no second-person "you must", no
passive "it should be noted". His prose is exploratory, not prescriptive — he shares what
he found, not what the reader must do.

HALLMARK PHRASES that signal authentic Mark voice:
  "in my experience"              "on a recent project"
  "what I've found"               "the trade-off here"
  "I've noticed"                  "I've watched"
  "in practice"                   "raises an interesting question"
  "what I've learned"             "one approach I've taken"
  "worth examining"               "interesting tension"

PROHIBITED PATTERNS — any of these reduce voice and clarity scores:
  Opening violations:
    "In this chapter..."          "This chapter will explore..."
    "We will cover..."            "What you'll learn:"
    "Learning objectives:"        "By the end of this chapter..."
  Buzzwords and clichés:
    "leverage" (as verb)          "empower"               "transformative"
    "revolutionize"               "game-changer"          "paradigm shift"
    "groundbreaking"              "innovative solution"   "synergize"
    "holistic"                    "best practices"        "next-level"
    "in today's fast-paced world" "in the ever-evolving"  "advanced strategies"
    "industry best practices"     "you must"              "one should always"
  Structural violations:
    "Key Takeaways" section heading (convert to prose instead)
    Learning objectives boxes at chapter start
    Passive conclusion summaries ("In this chapter we covered...")
    Excessive bold (more than 3 bold phrases per section)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOUR DIMENSIONS AND FULL SCORING RUBRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIMENSION 1: NARRATIVE_ARC (1-5)
Does this chapter advance the book's central argument or story?
A book is a single product, not a collection of independent articles. Each chapter
must earn its place by moving the reader's understanding forward.

Score 5 — Essential: removes critical understanding if cut; directly builds toward
          book thesis; connects explicitly to what came before and what follows.
Score 4 — Clearly contributes: chapter's connection to the book's progression is
          apparent; advances the argument even if the link isn't always explicit.
Score 3 — Standalone: on topic and useful, but could be read independently without
          meaningfully helping the overall book arc. Does not weaken but does not
          significantly strengthen.
Score 2 — Loosely connected: the chapter's relationship to the book's central
          argument is weak; could be reorganized or removed without harming
          reader comprehension of the book's thesis.
Score 1 — Disconnected: could be removed entirely without any loss to the book.
          No clear relationship to book-level thesis or progression.

NOTE: Appendices and reference chapters are expected to score 1-2 on narrative_arc —
      they are reference material, not narrative content. Score them honestly.

DIMENSION 2: ARGUMENT_QUALITY (1-5)
Are the chapter's claims supported with evidence, examples, or explicit reasoning?
Look for: specific examples from real projects, data or metrics, explicit logical
reasoning, acknowledged counter-arguments or trade-offs.
Watch for: assertion without evidence, appeals to vague authority ("industry experts
say"), generalization from a single case, hand-waving over complexity.

Score 5 — Fully grounded: every significant claim is backed by a specific example,
          real project data, explicit reasoning, or acknowledged trade-off.
          Reader never has to take anything on faith.
Score 4 — Mostly supported: strong overall evidence base with minor assertions
          that don't materially weaken the argument.
Score 3 — Mixed: some claims are well-supported with concrete evidence; others
          are asserted without justification. Reader must fill gaps.
Score 2 — Heavy assertion: the majority of claims rest on authority, generalization,
          or confidence rather than evidence. Reads like opinion presented as fact.
Score 1 — Pure assertion: no real evidence, no examples, no reasoning. Claims are
          stated as truisms. Reader has no way to evaluate them.

DIMENSION 3: CLARITY (1-5)
Does the language communicate precisely? No vague buzzwords; each sentence does one job.
Clarity is about whether the meaning is always unambiguous and efficiently expressed.
A technically complex topic can still score 5 if every sentence is clear.

Score 5 — Pristine: every sentence is precise; zero vague buzzwords; meaning is
          always unambiguous; reader never has to re-read for comprehension.
Score 4 — Mostly clear: prose is generally precise with one or two muddy passages
          or occasional buzzword that could be replaced with specifics.
Score 3 — Adequate: meaning is accessible but buzzwords or multi-purpose sentences
          appear regularly; some passages require effort to parse.
Score 2 — Jargon-heavy: terminology obscures rather than carries meaning; sentences
          frequently do three things at once; reader must interpret rather than read.
Score 1 — Opaque: vague throughout; buzzwords dominate; specific meaning must be
          reconstructed from context. High re-read rate.

DIMENSION 4: SIGNAL_RATIO (1-5)
Is every paragraph load-bearing? Signal = content that removes uncertainty or builds
understanding. Noise = padding, restatement, hedging, preamble.
Ask: if this paragraph were cut, would the reader miss any understanding?

Score 5 — No noise: every paragraph is load-bearing; nothing decorative; no
          restatements or unnecessary hedging; density is uniformly high.
Score 4 — Minimal noise: strong signal throughout with one or two restatements
          or preamble paragraphs that could be cut without loss.
Score 3 — Noticeable redundancy: the chapter restates points or hedges more than
          necessary; perhaps 15-25% of words could be removed without loss.
Score 2 — Clear padding: significant portions are restatement, circling back,
          or filler; the chapter's core content could be half the current length.
Score 1 — Mostly filler: the core insight or argument could be expressed in a
          fraction of the current word count. Padding is the dominant mode.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CALIBRATION GUIDANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A chapter with real project examples, first-person voice, and tight prose earns 4s.
A chapter that leads with "In this chapter we will explore..." earns a 2 on signal_ratio
  regardless of its content (the opener is pure noise).
A chapter with "leverage", "empower", and "transformative" in the first paragraph
  earns a 2 on clarity regardless of structural quality.
An appendix is expected to score 1-2 on narrative_arc; don't penalize it on other dims.
Generic tech writing that could have been written by anyone earns 2s across the board.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCRETE CALIBRATION EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NARRATIVE_ARC examples:
  Score 5 — Chapter opens by referencing the previous chapter's unresolved question,
             advances the book's core argument with new evidence, and closes by setting
             up the next chapter's problem. Removing this chapter would leave a visible
             gap in the reader's understanding.
  Score 3 — Chapter covers a relevant topic with good writing but reads as a standalone
             article. The reader could skip it and follow the rest of the book without
             difficulty. It enriches but does not advance the narrative.
  Score 1 — Chapter could be placed anywhere in the book, or removed entirely, without
             affecting the reader's understanding of any other chapter. It reads as an
             article that was inserted into the book, not written for it.

ARGUMENT_QUALITY examples:
  Score 5 — "On the WebSpark project in Q3 2023, we measured a 40% reduction in
             review cycle time after introducing the /devspark.specify workflow. The
             improvement was consistent across three consecutive sprints." (Specific,
             measurable, from a named real project.)
  Score 2 — "DevSpark significantly improves development velocity and code quality.
             Many teams that adopt structured workflows report better outcomes across
             the board." (General claim, vague authority, no specific evidence.)

CLARITY examples:
  Score 5 — Every sentence is a single declarative act. Technical terms are defined
             when introduced. No sentence requires re-reading.
  Score 2 — "The holistic approach leverages synergistic workflows to empower teams
             to deliver transformative outcomes at scale." (Four buzzwords, zero meaning.)

SIGNAL_RATIO examples:
  Score 5 — First paragraph introduces the problem. Second paragraph gives the solution.
             Third paragraph shows a real example. Nothing is repeated; nothing is
             introduced and then re-explained two paragraphs later.
  Score 2 — Chapter spends two paragraphs introducing what it's about to cover, then
             covers it, then summarizes what it just covered. The core content is
             embedded in roughly 50% of the total word count.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY a JSON array — no prose, no markdown fences, no explanation:
[{"chapter_id":"...","narrative_arc":N,"argument_quality":N,"clarity":N,"signal_ratio":N}, ...]

Where N is an integer 1-5. The array must contain exactly as many objects as chapters provided,
in the same order. Do not omit any chapter. Do not add extra fields.
"""


def load_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                key = k.strip()
                val = v.strip().strip('"').strip("'")
                if not os.environ.get(key):   # overwrite if missing or empty
                    os.environ[key] = val


def build_chapter_block(chapter: dict, index: int) -> str:
    headings = chapter.get("headings", [])[:10]
    first_para = chapter.get("first_para", "")[:400]
    excerpt = chapter.get("body_excerpt", "")[:500]

    lines = [
        f"--- CHAPTER {index} ---",
        f"chapter_id: {chapter['chapter_id']}",
        f"book: {chapter['book_title'][:60]}",
        f"title: {chapter['title'][:80]}",
        f"word_count: {chapter['word_count']}",
        f"headings: {headings or 'none'}",
        f"first_paragraph: {first_para}",
        f"body_excerpt: {excerpt}",
    ]
    return "\n".join(lines)


def score_batch(client: anthropic.Anthropic, batch: list[dict]) -> tuple[list[dict], dict]:
    blocks = [build_chapter_block(c, i + 1) for i, c in enumerate(batch)]
    user_content = (
        f"Score these {len(batch)} book chapters. "
        f"Return a JSON array with exactly {len(batch)} objects in order.\n\n"
        + "\n\n".join(blocks)
    )

    # max_tokens: generous budget — each chapter produces ~60 tokens of pretty-printed JSON
    response = client.messages.create(
        model=MODEL,
        max_tokens=max(512, len(batch) * 100),
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
    )

    usage = {
        "input_tokens":  response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)

    result = []
    for i, item in enumerate(parsed):
        chapter_id = item.get("chapter_id") or batch[i]["chapter_id"]
        result.append({
            "chapter_id": chapter_id,
            "content_hash": batch[i].get("content_hash"),
            "narrative_arc":    max(1, min(5, int(item.get("narrative_arc", 3)))),
            "argument_quality": max(1, min(5, int(item.get("argument_quality", 3)))),
            "clarity":          max(1, min(5, int(item.get("clarity", 3)))),
            "signal_ratio":     max(1, min(5, int(item.get("signal_ratio", 3)))),
        })
    return result, usage


def main():
    load_env()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Add it to a .env file at the project root:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Run parse_books.py first.")
        sys.exit(1)

    chapters = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_scores: dict[str, dict] = {}
    if SCORES_FILE.exists():
        for item in json.loads(SCORES_FILE.read_text(encoding="utf-8")):
            existing_scores[item["chapter_id"]] = item

    valid_ids = {c["chapter_id"] for c in chapters}
    existing_scores = {
        chapter_id: score
        for chapter_id, score in existing_scores.items()
        if chapter_id in valid_ids
    }

    to_score = [
        c for c in chapters
        if (c["chapter_id"] not in existing_scores
            or existing_scores[c["chapter_id"]].get("content_hash") != c.get("content_hash"))
    ]

    print(f"Total chapters: {len(chapters)}")
    print(f"Already scored: {len(existing_scores)}")
    print(f"To score:       {len(to_score)}")

    if not to_score:
        print("All chapters already scored.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    batches = [to_score[i:i + BATCH_SIZE] for i in range(0, len(to_score), BATCH_SIZE)]
    total_input = 0
    total_output = 0

    for batch_num, batch in enumerate(batches, 1):
        ids = [c["chapter_id"] for c in batch]
        print(f"\nBatch {batch_num}/{len(batches)}: {ids}")

        try:
            scores, usage = score_batch(client, batch)
            total_input  += usage["input_tokens"]
            total_output += usage["output_tokens"]
            for score in scores:
                existing_scores[score["chapter_id"]] = score
                print(
                    f"  {score['chapter_id']}: "
                    f"arc={score['narrative_arc']} "
                    f"arg={score['argument_quality']} "
                    f"clarity={score['clarity']} "
                    f"signal={score['signal_ratio']}"
                )

            SCORES_FILE.write_text(
                json.dumps(list(existing_scores.values()), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        except json.JSONDecodeError as e:
            print(f"  ERROR parsing JSON for batch {batch_num}: {e}")
            print("  Skipping batch — will retry on next run.")
        except anthropic.APIError as e:
            print(f"  API ERROR: {e}")
            print("  Waiting 10s then continuing...")
            time.sleep(10)

        if batch_num < len(batches):
            time.sleep(1)

    print(f"\nDone. Scored {len(existing_scores)} chapters.")
    print(f"Scores written to {SCORES_FILE}")
    print(f"\nToken usage (this run):")
    print(f"  Input:   {total_input:,}")
    print(f"  Output:  {total_output:,}")

    scores_list = list(existing_scores.values())
    if scores_list:
        for dim in ("narrative_arc", "argument_quality", "clarity", "signal_ratio"):
            avg = sum(s[dim] for s in scores_list) / len(scores_list)
            low = sum(1 for s in scores_list if s[dim] <= 2)
            print(f"  {dim:18s}: avg={avg:.1f}  score<=2: {low}")


if __name__ == "__main__":
    main()
