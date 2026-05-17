"""
Book scoring pipeline runner — Python equivalent of run_book_scoring.ps1.

Run from project root:
    python books/scoring/run_book_scoring.py
    python books/scoring/run_book_scoring.py project-mechanics
    python books/scoring/run_book_scoring.py --score-only
    python books/scoring/run_book_scoring.py --help

API key is read from .env at the project root (ANTHROPIC_API_KEY=sk-ant-...).
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path("books/scoring")
PYTHON  = sys.executable   # same interpreter that's running this script


def run(label: str, script: str, extra_args: list[str] = []) -> None:
    print(f"\n{'='*60}", flush=True)
    print(f"  {label}", flush=True)
    print(f"{'='*60}", flush=True)
    sys.stdout.flush()
    result = subprocess.run([PYTHON, str(SCRIPTS / script)] + extra_args)
    if result.returncode != 0:
        print(f"\nERROR: {script} failed (exit {result.returncode}). Stopping.", flush=True)
        sys.exit(result.returncode)


def main() -> None:
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        print("Steps:")
        print("  1. parse_books.py          — discover chapters, rule-based signals")
        print("  2. score_books.py          — LLM scoring (arc, argument, clarity, signal)")
        print("  3. generate_book_dashboard.py — merge scores -> HTML dashboard")
        print("  4. remediate_chapters.py   — critique low-scoring chapters")
        print("")
        print("rewrite_chapters.py is intentionally NOT run automatically.")
        print("Review reports first, then run manually:")
        print(f"  {PYTHON} {SCRIPTS}/rewrite_chapters.py --dry-run")
        print(f"  {PYTHON} {SCRIPTS}/rewrite_chapters.py")
        return

    score_only = "--score-only" in args
    parse_args = [a for a in args if not a.startswith("-")]

    run("Step 1: Parse books (rule-based signals)", "parse_books.py", parse_args)
    run("Step 2: LLM scoring", "score_books.py")
    run("Step 3: Generate HTML dashboard", "generate_book_dashboard.py")

    if not score_only:
        run("Step 4: Remediate low-scoring chapters", "remediate_chapters.py")

    print("\n" + "="*60, flush=True)
    print("  Done", flush=True)
    print("="*60, flush=True)
    print(f"  Dashboard : books/scoring/books-dashboard.html", flush=True)
    print(f"  Reviews   : books/reviews/", flush=True)
    print(f"", flush=True)
    print(f"  To rewrite (review reports first):", flush=True)
    print(f"    python {SCRIPTS}/rewrite_chapters.py --dry-run", flush=True)
    print(f"    python {SCRIPTS}/rewrite_chapters.py", flush=True)


if __name__ == "__main__":
    main()
