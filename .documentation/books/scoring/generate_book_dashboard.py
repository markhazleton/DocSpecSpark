"""
Step 3: Merge parse + LLM scores and generate a self-contained HTML dashboard.
Reads books_data.json + book_llm_scores.json → books-dashboard.html

Features:
  - Book-level summary cards with aggregate scores
  - Chapter-level sortable table
  - Filter by book; search by title
  - Color-coded scores (5=green → 1=red)

Run from project root:
    python books/scoring/generate_book_dashboard.py
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE   = Path("books/scoring/books_data.json")
SCORES_FILE = Path("books/scoring/book_llm_scores.json")
OUTPUT_FILE = Path("books/scoring/books-dashboard.html")


def merge(chapters: list[dict], llm_scores: dict) -> list[dict]:
    rows = []
    for c in chapters:
        cid = c["chapter_id"]
        llm = llm_scores.get(cid, {})
        if llm.get("content_hash") != c.get("content_hash"):
            llm = {}

        narrative_arc    = llm.get("narrative_arc", 0)
        argument_quality = llm.get("argument_quality", 0)
        clarity          = llm.get("clarity", 0)
        signal_ratio     = llm.get("signal_ratio", 0)
        structure        = c.get("structure_score", 0)
        has_llm_score = all(
            dim > 0 for dim in [narrative_arc, argument_quality, clarity, signal_ratio]
        )

        voice_signal = c.get("voice_signal", 3.0)
        voice = round(signal_ratio * 0.6 + voice_signal * 0.4, 1) if signal_ratio else 0

        scored_dims = [d for d in [narrative_arc, argument_quality, clarity, signal_ratio, structure, voice] if d > 0]
        overall = round(sum(scored_dims) / len(scored_dims), 1) if has_llm_score and scored_dims else 0.0

        rows.append({
            "chapter_id":       cid,
            "book_slug":        c["book_slug"],
            "book_title":       c["book_title"],
            "title":            c["title"],
            "chapter_num":      c["chapter_num"],
            "part":             c.get("part", ""),
            "last_modified":    c.get("last_modified", ""),
            "word_count":       c.get("word_count", 0),
            "narrative_arc":    narrative_arc,
            "argument_quality": argument_quality,
            "clarity":          clarity,
            "signal_ratio":     signal_ratio,
            "structure":        structure,
            "voice":            voice,
            "overall":          overall,
            "llm_scored":       has_llm_score,
            "structure_issues": c.get("structure_issues", []),
            "banned_phrases":   c.get("signals", {}).get("banned_phrases", []),
            "has_banned_opener": c.get("has_banned_opener", False),
        })
    rows.sort(key=lambda r: (r["book_slug"], r["chapter_num"]))
    return rows


def build_book_summaries(rows: list[dict]) -> list[dict]:
    books: dict[str, list] = {}
    for r in rows:
        books.setdefault(r["book_slug"], []).append(r)

    summaries = []
    for slug, chapters in sorted(books.items()):
        scored = [c for c in chapters if c["overall"] > 0]
        avg_overall  = round(sum(c["overall"] for c in scored) / len(scored), 2) if scored else 0
        avg_arc      = round(sum(c["narrative_arc"] for c in scored if c["narrative_arc"]) / max(1, sum(1 for c in scored if c["narrative_arc"])), 1) if scored else 0
        avg_arg      = round(sum(c["argument_quality"] for c in scored if c["argument_quality"]) / max(1, sum(1 for c in scored if c["argument_quality"])), 1) if scored else 0
        avg_clarity  = round(sum(c["clarity"] for c in scored if c["clarity"]) / max(1, sum(1 for c in scored if c["clarity"])), 1) if scored else 0
        avg_signal   = round(sum(c["signal_ratio"] for c in scored if c["signal_ratio"]) / max(1, sum(1 for c in scored if c["signal_ratio"])), 1) if scored else 0
        avg_struct   = round(sum(c["structure"] for c in chapters if c["structure"]) / max(1, sum(1 for c in chapters if c["structure"])), 1)
        low_count    = sum(1 for c in scored if c["overall"] < 2.5)
        summaries.append({
            "book_slug":  slug,
            "book_title": chapters[0]["book_title"],
            "chapters":   len(chapters),
            "scored":     len(scored),
            "avg_overall":  avg_overall,
            "avg_arc":      avg_arc,
            "avg_arg":      avg_arg,
            "avg_clarity":  avg_clarity,
            "avg_signal":   avg_signal,
            "avg_struct":   avg_struct,
            "low_count":    low_count,
        })
    return summaries


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mark Hazleton — Book Quality Dashboard</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          font-size: 13px; background: #f1f5f9; color: #1e293b; }}
  header {{ background: #1a2e4a; color: #e2e8f0; padding: 16px 24px; }}
  header h1 {{ font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }}
  header p  {{ font-size: 11px; color: #94a3b8; margin-top: 2px; }}

  /* Book summary cards */
  .books-section {{ padding: 16px 24px; background: #1e293b; }}
  .books-section h2 {{ color: #94a3b8; font-size: 11px; text-transform: uppercase;
                        letter-spacing: .5px; margin-bottom: 10px; }}
  .books-grid {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .book-card {{ background: #334155; border-radius: 8px; padding: 12px 16px;
                min-width: 220px; cursor: pointer; border: 2px solid transparent;
                transition: border-color .15s; }}
  .book-card:hover {{ border-color: #3b82f6; }}
  .book-card.active {{ border-color: #60a5fa; }}
  .book-card .book-title {{ font-weight: 600; color: #f1f5f9; font-size: 13px;
                             white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                             max-width: 200px; }}
  .book-card .book-meta  {{ font-size: 10px; color: #94a3b8; margin-top: 3px; }}
  .book-card .book-score {{ font-size: 22px; font-weight: 700; color: #f8fafc;
                             margin-top: 6px; }}
  .book-card .score-dims {{ display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap; }}
  .book-card .dim {{ font-size: 10px; color: #cbd5e1; background: #1e293b;
                     border-radius: 4px; padding: 2px 5px; }}
  .book-card .low-warn {{ font-size: 10px; color: #fca5a5; margin-top: 4px; }}

  /* Toolbar */
  .toolbar {{ display: flex; gap: 8px; align-items: center; padding: 10px 24px;
              background: #fff; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }}
  .toolbar input {{ padding: 5px 10px; border: 1px solid #cbd5e1; border-radius: 5px;
                    font-size: 12px; width: 220px; }}
  .toolbar input:focus {{ outline: none; border-color: #3b82f6; }}
  .toolbar label {{ font-size: 11px; color: #64748b; }}
  .filter-btn {{ padding: 4px 10px; border: 1px solid #cbd5e1; border-radius: 4px;
                 background: #f8fafc; font-size: 11px; cursor: pointer; }}
  .filter-btn.active {{ background: #1a2e4a; color: #fff; border-color: #1a2e4a; }}

  /* Table */
  .table-wrap {{ overflow-x: auto; padding: 0 24px 24px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border-radius: 8px; overflow: hidden;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-top: 12px; }}
  thead tr {{ background: #1e293b; color: #e2e8f0; }}
  th {{ padding: 9px 8px; text-align: left; font-size: 11px; font-weight: 600;
        white-space: nowrap; cursor: pointer; user-select: none;
        text-transform: uppercase; letter-spacing: .4px; }}
  th:hover {{ background: #334155; }}
  th .sort-icon {{ margin-left: 3px; opacity: .5; font-size: 9px; }}
  th.sorted .sort-icon {{ opacity: 1; }}
  td {{ padding: 7px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
  tr:hover td {{ background: #f8fafc; }}
  tr:last-child td {{ border-bottom: none; }}

  .title-cell {{ max-width: 240px; }}
  .title-cell span {{ display: block; white-space: nowrap; overflow: hidden;
                      text-overflow: ellipsis; font-weight: 500; color: #1e3a5f; }}
  .book-badge {{ display: inline-block; padding: 2px 6px; border-radius: 9px;
                 font-size: 10px; font-weight: 500; background: #dbeafe; color: #1d4ed8; }}
  .score-cell {{ text-align: center; font-weight: 600; border-radius: 4px;
                 padding: 4px 6px !important; font-size: 12px; }}
  .s5  {{ background: #166534; color: #fff; }}
  .s45 {{ background: #22c55e; color: #fff; }}
  .s35 {{ background: #bbf7d0; color: #166534; }}
  .s25 {{ background: #fef9c3; color: #854d0e; }}
  .s15 {{ background: #fed7aa; color: #9a3412; }}
  .s1  {{ background: #fca5a5; color: #7f1d1d; }}
  .s0  {{ background: #f1f5f9; color: #94a3b8; font-style: italic; font-weight: 400; }}
  .issues-icon {{ cursor: help; font-size: 11px; }}
  .no-results {{ text-align: center; padding: 40px; color: #94a3b8; }}
</style>
</head>
<body>

<header>
  <h1>Mark Hazleton — Book Quality Dashboard</h1>
  <p>Generated {generated} &middot; {total_chapters} chapters across {total_books} books &middot; Structure = rule-based &middot; Arc, Argument, Clarity, Signal = LLM-judged (Haiku)</p>
</header>

<div class="books-section">
  <h2>Books</h2>
  <div class="books-grid" id="book-cards"></div>
</div>

<div class="toolbar">
  <input type="text" id="search" placeholder="Search by chapter title…" oninput="applyFilters()">
  <label style="margin-left:8px">Hide unscored:</label>
  <input type="checkbox" id="hide-unscored" onchange="applyFilters()">
</div>

<div class="table-wrap">
<table id="main-table">
<thead>
<tr>
  <th data-col="chapter_num">#<span class="sort-icon">▼</span></th>
  <th data-col="title">Chapter Title <span class="sort-icon">▼</span></th>
  <th data-col="book_slug">Book <span class="sort-icon">▼</span></th>
  <th data-col="last_modified">Modified <span class="sort-icon">▼</span></th>
  <th data-col="word_count">Words <span class="sort-icon">▼</span></th>
  <th data-col="narrative_arc">Arc <span class="sort-icon">▼</span></th>
  <th data-col="argument_quality">Arg. <span class="sort-icon">▼</span></th>
  <th data-col="clarity">Clarity <span class="sort-icon">▼</span></th>
  <th data-col="signal_ratio">Signal <span class="sort-icon">▼</span></th>
  <th data-col="structure">Struct. <span class="sort-icon">▼</span></th>
  <th data-col="overall">Overall <span class="sort-icon">▼</span></th>
</tr>
</thead>
<tbody id="tbody"></tbody>
</table>
</div>

<script>
const CHAPTERS = {chapters_json};
const BOOKS    = {books_json};

let activeBook  = "All";
let sortCol     = "book_slug";
let sortDir     = 1;
let searchText  = "";

function scoreClass(v) {{
  if (!v || v === 0) return "s0";
  if (v >= 4.5) return "s5";
  if (v >= 3.5) return "s45";
  if (v >= 2.5) return "s35";
  if (v >= 1.5) return "s25";
  if (v >= 1.0) return "s1";
  return "s0";
}}
function scoreDisplay(v) {{
  if (!v || v === 0) return "—";
  return v % 1 === 0 ? v.toString() : v.toFixed(1);
}}

function buildBookCards() {{
  const container = document.getElementById("book-cards");
  const allCard = `<div class="book-card active" id="card-All" onclick="setBook('All')">
    <div class="book-title">All Books</div>
    <div class="book-meta">${{CHAPTERS.length}} chapters</div>
    <div class="book-score">${{(CHAPTERS.filter(c=>c.overall>0).reduce((s,c)=>s+c.overall,0)/Math.max(1,CHAPTERS.filter(c=>c.overall>0).length)).toFixed(2)}}</div>
  </div>`;
  container.innerHTML = allCard + BOOKS.map(b => {{
    const warn = b.low_count > 0 ? `<div class="low-warn">⚠ ${{b.low_count}} below 2.5</div>` : "";
    return `<div class="book-card" id="card-${{b.book_slug}}" onclick="setBook('${{b.book_slug}}')">
      <div class="book-title" title="${{b.book_title}}">${{b.book_title}}</div>
      <div class="book-meta">${{b.chapters}} chapters · ${{b.scored}} scored</div>
      <div class="book-score">${{b.avg_overall || "—"}}</div>
      <div class="score-dims">
        <span class="dim">arc ${{b.avg_arc||"—"}}</span>
        <span class="dim">arg ${{b.avg_arg||"—"}}</span>
        <span class="dim">clarity ${{b.avg_clarity||"—"}}</span>
        <span class="dim">signal ${{b.avg_signal||"—"}}</span>
        <span class="dim">struct ${{b.avg_struct||"—"}}</span>
      </div>
      ${{warn}}
    </div>`;
  }}).join("");
}}

function setBook(slug) {{
  activeBook = slug;
  document.querySelectorAll(".book-card").forEach(c => c.classList.remove("active"));
  const card = document.getElementById("card-" + slug);
  if (card) card.classList.add("active");
  applyFilters();
}}

function applyFilters() {{
  searchText = document.getElementById("search").value.toLowerCase();
  renderTable();
}}

function getSortedFiltered() {{
  let rows = CHAPTERS.filter(r => {{
    if (activeBook !== "All" && r.book_slug !== activeBook) return false;
    if (searchText && !r.title.toLowerCase().includes(searchText)) return false;
    if (document.getElementById("hide-unscored")?.checked && r.overall === 0) return false;
    return true;
  }});
  rows.sort((a, b) => {{
    let av = a[sortCol], bv = b[sortCol];
    if (typeof av === "string") av = av.toLowerCase();
    if (typeof bv === "string") bv = bv.toLowerCase();
    if (av < bv) return sortDir;
    if (av > bv) return -sortDir;
    return 0;
  }});
  return rows;
}}

function renderTable() {{
  const rows = getSortedFiltered();
  const tbody = document.getElementById("tbody");
  if (!rows.length) {{
    tbody.innerHTML = `<tr><td colspan="11" class="no-results">No chapters match the current filters.</td></tr>`;
    return;
  }}
  tbody.innerHTML = rows.map(r => {{
    const issues = [...(r.structure_issues||[]), ...(r.banned_phrases||[]).map(p=>"banned: "+p)];
    if (r.has_banned_opener) issues.push("banned opener");
    const issuesTip = issues.length ? ` title="${{issues.join("\\n")}}"` : "";
    const issuesIcon = issues.length ? ` <span class="issues-icon"${{issuesTip}}>⚠️${{issues.length}}</span>` : "";
    return `<tr>
      <td style="text-align:center;color:#64748b">${{r.chapter_num}}</td>
      <td class="title-cell"><span title="${{r.title}}">${{r.title}}</span></td>
      <td><span class="book-badge" title="${{r.book_title}}">${{r.book_slug}}</span></td>
      <td style="white-space:nowrap;color:#64748b">${{r.last_modified}}</td>
      <td style="text-align:right;color:#64748b">${{r.word_count.toLocaleString()}}</td>
      <td class="score-cell ${{scoreClass(r.narrative_arc)}}">${{scoreDisplay(r.narrative_arc)}}</td>
      <td class="score-cell ${{scoreClass(r.argument_quality)}}">${{scoreDisplay(r.argument_quality)}}</td>
      <td class="score-cell ${{scoreClass(r.clarity)}}">${{scoreDisplay(r.clarity)}}</td>
      <td class="score-cell ${{scoreClass(r.signal_ratio)}}">${{scoreDisplay(r.signal_ratio)}}</td>
      <td class="score-cell ${{scoreClass(r.structure)}}">${{scoreDisplay(r.structure)}}${{issuesIcon}}</td>
      <td class="score-cell ${{scoreClass(r.overall)}}" style="font-size:13px">${{scoreDisplay(r.overall)}}</td>
    </tr>`;
  }}).join("");
}}

function setupSort() {{
  document.querySelectorAll("th[data-col]").forEach(th => {{
    th.addEventListener("click", () => {{
      const col = th.dataset.col;
      if (sortCol === col) sortDir *= -1;
      else {{ sortCol = col; sortDir = -1; }}
      document.querySelectorAll("th").forEach(t => t.classList.remove("sorted"));
      th.classList.add("sorted");
      th.querySelector(".sort-icon").textContent = sortDir === -1 ? "▼" : "▲";
      renderTable();
    }});
  }});
  document.querySelector(`th[data-col="book_slug"]`).classList.add("sorted");
}}

buildBookCards();
setupSort();
renderTable();
</script>
</body>
</html>
"""


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Run parse_books.py first.")
        return

    chapters = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    llm_scores: dict[str, dict] = {}
    if SCORES_FILE.exists():
        for item in json.loads(SCORES_FILE.read_text(encoding="utf-8")):
            llm_scores[item["chapter_id"]] = item
    else:
        print(f"NOTE: {SCORES_FILE} not found — showing structure scores only.")

    rows = merge(chapters, llm_scores)
    book_summaries = build_book_summaries(rows)

    total_books    = len({r["book_slug"] for r in rows})
    scored_count   = sum(1 for r in rows if r["overall"] > 0)
    unscored_count = len(rows) - scored_count

    html = HTML_TEMPLATE.format(
        generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total_chapters=len(rows),
        total_books=total_books,
        chapters_json=json.dumps(rows, ensure_ascii=False),
        books_json=json.dumps(book_summaries, ensure_ascii=False),
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_FILE}")
    print(f"  {scored_count} chapters scored, {unscored_count} unscored")

    for b in book_summaries:
        print(f"\n  {b['book_title']} ({b['book_slug']})")
        print(f"    chapters={b['chapters']} scored={b['scored']} avg={b['avg_overall']}")
        print(f"    arc={b['avg_arc']} arg={b['avg_arg']} clarity={b['avg_clarity']} signal={b['avg_signal']} struct={b['avg_struct']}")
        if b["low_count"]:
            print(f"    LOW SCORE: {b['low_count']} chapter(s) below 2.5")


if __name__ == "__main__":
    main()
