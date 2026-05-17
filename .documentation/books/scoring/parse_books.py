"""
Step 1: Parse book.yaml manifests and compute objective signals.
Outputs: books/scoring/books_data.json

Only directories with books/{slug}/book.yaml are scored. The scoring pipeline
uses the same manifest sections as the publishing pipeline:
  - frontmatter
  - chapters
  - parts[].chapters
  - appendices

Run from project root:
    python books/scoring/parse_books.py
    python books/scoring/parse_books.py project-mechanics
"""

import hashlib
import json
import re
import sys
import datetime
from pathlib import Path

import yaml

BOOKS_DIR = Path("books")
OUTPUT_FILE = Path("books/scoring/books_data.json")

# ── Book-level banned phrases (from devspark.brutal-book-review.md) ──────────

BANNED_PHRASES = [
    "leverage",          # as verb
    "empower",
    "transform your",
    "transformative",
    "holistic",
    "synergy",
    "synergize",
    "best practices",
    "next-level",
    "revolutionize",
    "revolutionizing",
    "game-changer",
    "game changer",
    "paradigm shift",
    "in today's fast-paced world",
    "in the ever-evolving",
    "in the rapidly evolving",
    "let's dive in",
    "without further ado",
    "it's important to note",
    "it is important to note",
    "you must",
    "one should always",
    "key takeaways",
    "in conclusion, we have",
    "in conclusion, we've",
    "groundbreaking",
    "innovative solution",
    "advanced strategies",
    "industry best practices",
]

BANNED_CHAPTER_OPENERS = [
    r"^in this chapter",
    r"^this chapter (will|explores|covers|discusses|examines|presents)",
    r"^we will (explore|examine|discuss|cover|look at)",
    r"^we'll (explore|examine|discuss|cover|look at)",
    r"^welcome to (chapter|part)",
    r"^according to (wikipedia|merriam)",
    r"^\w[\w\s]+ is defined as",
    r"^\w[\w\s]+ \(?\w*\)? is a (type of|kind of|form of|method|process|technique|concept)",
]

POSITIVE_PHRASES = [
    "in my experience",
    "worth examining",
    "what i've observed",
    "the trade-off",
    "trade-offs",
    "i've found",
    "a pattern that keeps",
    "one approach i",
    "what i've learned",
    "in practice",
    "on a recent project",
    "in a project",
    "i've watched",
    "i've noticed",
    "i've been",
    "raises an interesting question",
    "interesting challenge",
    "interesting tension",
    "what i've built",
    "from real experience",
]


# ── Manifest discovery ────────────────────────────────────────────────────────

def load_book_yaml(book_dir: Path) -> dict:
    yaml_path = book_dir / "book.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(yaml_path)
    try:
        loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{yaml_path} is invalid YAML: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{yaml_path} must contain a YAML object")
    return loaded


def normalize_manifest_entries(book: dict) -> list[dict]:
    """Return manifest entries in the same order the publishing pipeline uses."""
    entries: list[dict] = []

    for item in book.get("frontmatter") or []:
        entries.append({**item, "role": item.get("role") or "frontmatter"})

    parts = book.get("parts") or []
    if parts:
        for part in parts:
            part_title = str(part.get("title") or "")
            for item in part.get("chapters") or []:
                entries.append({
                    **item,
                    "role": item.get("role") or "chapter",
                    "part": item.get("part") or part_title,
                })
    else:
        for item in book.get("chapters") or []:
            entries.append({**item, "role": item.get("role") or "chapter"})

    for item in book.get("appendices") or []:
        entries.append({**item, "role": "appendix"})

    return entries


# ── Chapter parsing ────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw_fm = text[3:end]
    try:
        meta = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError:
        meta = {}
    body = text[end + 4:].lstrip("\n")
    return meta, body


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def extract_headings(body: str) -> list[str]:
    return re.findall(r"^#{1,4} .+", body, re.MULTILINE)


def first_body_paragraph(body: str) -> str:
    in_code = False
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        if (stripped
                and not stripped.startswith("#")
                and not stripped.startswith("!")
                and not stripped.startswith(">")
                and len(stripped) > 20):
            return stripped
    return ""


def check_banned_opener(first_para: str) -> bool:
    lower = first_para.lower().strip()
    return any(re.match(pat, lower) for pat in BANNED_CHAPTER_OPENERS)


def compute_voice_signals(body: str) -> dict:
    lower = body.lower()
    banned_hits = [p for p in BANNED_PHRASES if p in lower]
    positive_hits = [p for p in POSITIVE_PHRASES if p in lower]

    first_person_count = len(re.findall(r"\bi\b", body))
    we_count = len(re.findall(r"\bwe\b", lower))
    bold_count = len(re.findall(r"\*\*[^*]+\*\*", body))
    code_block_count = len(re.findall(r"```", body)) // 2

    has_key_takeaways = bool(re.search(r"#{1,4}\s*key takeaways", lower))
    has_chapter_intro_box = bool(re.search(
        r"(what you.ll learn|learning objectives|chapter overview)",
        lower
    ))
    has_passive_conclusion = bool(re.search(
        r"#{1,4}\s*(conclusion|summary|in this chapter we (covered|explored))",
        lower
    ))

    return {
        "banned_phrases": banned_hits,
        "positive_phrases": positive_hits,
        "first_person_count": first_person_count,
        "we_count": we_count,
        "bold_count": bold_count,
        "code_block_count": code_block_count,
        "has_key_takeaways": has_key_takeaways,
        "has_chapter_intro_box": has_chapter_intro_box,
        "has_passive_conclusion": has_passive_conclusion,
    }


def score_structure(headings: list[str], wc: int, signals: dict) -> tuple[int, list[str]]:
    issues = []
    score = 5

    h2_count = sum(1 for h in headings if h.startswith("## "))
    if wc > 800 and h2_count == 0:
        issues.append("no H2 headings in a substantial chapter")
        score -= 2
    elif wc > 400 and h2_count < 2:
        issues.append(f"only {h2_count} H2 heading(s) — may be thin structure")
        score -= 1

    if wc < 300:
        issues.append(f"very short chapter ({wc} words) — may lack substance")
        score -= 1
    elif wc > 10000:
        issues.append(f"very long chapter ({wc} words) — consider splitting")
        score -= 1

    if signals["has_key_takeaways"]:
        issues.append("'Key Takeaways' heading violates voice standards")
        score -= 1

    if signals["has_chapter_intro_box"]:
        issues.append("'What you'll learn' / learning objectives box is generic padding")
        score -= 1

    if signals["has_passive_conclusion"]:
        issues.append("passive conclusion section ('In this chapter we covered…')")
        score -= 1

    return max(1, score), issues


def clean_manifest_title(title: str) -> str:
    title = re.sub(r"^chapter\s+\d+[a-z]?[:.]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^appendix\s+[a-z0-9]+[:.]\s*", "", title, flags=re.IGNORECASE)
    return title.strip()


def compute_chapter(book_slug: str, book_title: str, entry: dict, chapter_num: int) -> dict:
    source = entry["source"]
    path = Path(source)
    if not path.is_absolute():
        path = Path(source)

    if not path.exists():
        raise FileNotFoundError(source)

    text = path.read_text(encoding="utf-8", errors="replace")
    hash_input = text + "\n" + json.dumps(
        {
            "title": entry.get("title", ""),
            "role": entry.get("role", ""),
            "part": entry.get("part", ""),
            "number": entry.get("number", ""),
        },
        sort_keys=True,
    )
    content_hash = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    meta, body = parse_frontmatter(text)

    chapter_id = f"{book_slug}/{path.stem}"
    title = (
        str(entry.get("title") or "")
        or str(meta.get("title") or "")
        or next((h.lstrip("#").strip() for h in extract_headings(body) if h.startswith("# ")), "")
        or path.stem.replace("-", " ").title()
    )
    title = clean_manifest_title(title)

    wc = word_count(body)
    headings = extract_headings(body)
    first_para = first_body_paragraph(body)
    signals = compute_voice_signals(body)
    structure_score, structure_issues = score_structure(headings, wc, signals)
    has_banned_opener = check_banned_opener(first_para)

    voice_signal = 3.0
    voice_signal -= len(signals["banned_phrases"]) * 0.4
    voice_signal += len(signals["positive_phrases"]) * 0.3
    voice_signal -= signals["we_count"] * 0.15
    voice_signal = round(max(1.0, min(5.0, voice_signal)), 1)

    return {
        "content_hash": content_hash,
        "book_slug": book_slug,
        "book_title": book_title,
        "chapter_id": chapter_id,
        "chapter_file": str(path.relative_to(BOOKS_DIR / book_slug)),
        "chapter_num": chapter_num,
        "title": title[:120],
        "role": str(entry.get("role") or "chapter"),
        "part": str(entry.get("part") or meta.get("part") or ""),
        "last_modified": datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
        "word_count": wc,
        "headings": headings[:20],
        "first_para": first_para[:500],
        "body_excerpt": body[:1500],
        "signals": signals,
        "structure_issues": structure_issues,
        "structure_score": structure_score,
        "has_banned_opener": has_banned_opener,
        "voice_signal": voice_signal,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    requested_slugs = {
        arg for arg in sys.argv[1:]
        if not arg.startswith("-")
    }

    if not BOOKS_DIR.exists():
        print(f"ERROR: {BOOKS_DIR} not found. Run from project root.")
        sys.exit(1)

    book_dirs = sorted(
        d for d in BOOKS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".") and (d / "book.yaml").exists()
    )
    if requested_slugs:
        book_dirs = [d for d in book_dirs if d.name in requested_slugs]

    if not book_dirs:
        print(f"No book.yaml manifests found under {BOOKS_DIR}/")
        sys.exit(1)

    all_chapters: list[dict] = []

    for book_dir in book_dirs:
        book_slug = book_dir.name
        try:
            book_meta = load_book_yaml(book_dir)
        except (FileNotFoundError, ValueError) as exc:
            print(f"  [{book_slug}] ERROR: {exc}")
            sys.exit(1)

        entries = normalize_manifest_entries(book_meta)
        if not entries:
            print(f"  [{book_slug}] No manifest entries found — skipping.")
            continue

        book_title = str(book_meta.get("title") or book_slug.replace("-", " ").title())

        print(f"\nBook: {book_slug} ({book_title})")
        print(f"  Found {len(entries)} manifest section(s)")

        for i, entry in enumerate(entries, 1):
            source = entry.get("source", "")
            role = entry.get("role", "chapter")
            print(f"    [{i:2d}/{len(entries)}] {role:11s} {source}")
            try:
                chapter_data = compute_chapter(book_slug, book_title, entry, i)
                all_chapters.append(chapter_data)
            except FileNotFoundError:
                print(f"ERROR: Chapter source not found: {source}")
                sys.exit(1)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(all_chapters, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {len(all_chapters)} sections across {len(book_dirs)} books -> {OUTPUT_FILE}")

    if all_chapters:
        avg_struct = sum(c["structure_score"] for c in all_chapters) / len(all_chapters)
        banned_openers = sum(1 for c in all_chapters if c["has_banned_opener"])
        avg_wc = sum(c["word_count"] for c in all_chapters) / len(all_chapters)
        print(f"\nQuick stats:")
        print(f"  Avg structure score: {avg_struct:.1f}/5")
        print(f"  Banned openers:      {banned_openers}")
        print(f"  Avg word count:      {avg_wc:.0f}")
        books_seen = sorted({c["book_slug"] for c in all_chapters})
        for b in books_seen:
            count = sum(1 for c in all_chapters if c["book_slug"] == b)
            print(f"  {b}: {count} section(s)")


if __name__ == "__main__":
    main()
