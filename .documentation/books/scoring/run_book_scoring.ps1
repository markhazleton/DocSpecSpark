# Book scoring pipeline
# Set your API key below, then run from the project root:
#   .\.documentation\scripts\book_scoring\run_book_scoring.ps1
#
# Steps:
#   1. parse_books.py          — discover chapters, compute rule-based signals
#   2. score_books.py          — LLM scoring (narrative arc, argument, clarity, signal)
#   3. generate_book_dashboard — merge scores → HTML dashboard
#   4. remediate_chapters.py   — critique + editorial for low-scoring chapters (< 2.5)
#
# rewrite_chapters.py is intentionally NOT run automatically — review reports first.
# Run it manually:
#   .venv/Scripts/python .documentation/scripts/book_scoring/rewrite_chapters.py --dry-run
#   .venv/Scripts/python .documentation/scripts/book_scoring/rewrite_chapters.py

# ── Set API Key ────────────────────────────────────────────────────────────────
# Copy your key from run_scoring.ps1 or set ANTHROPIC_API_KEY in your environment.
# NEVER commit this file with a real key.
$env:ANTHROPIC_API_KEY = $env:ANTHROPIC_API_KEY   # set in your environment or .env file — never hardcode here
# ──────────────────────────────────────────────────────────────────────────────

$python  = ".\.venv\Scripts\python.exe"
$scripts = ".\.documentation\scripts\book_scoring"

if (-not (Test-Path $python)) {
    Write-Error "Virtual environment not found. Run from project root after creating .venv."
    exit 1
}

# Allow --score-only flag to skip remediation (useful for quick re-scores after rewrites)
$scoreOnly = $args -contains "--score-only"

Write-Host "`n=== Step 1: Parse books (rule-based signals) ===" -ForegroundColor Cyan
& $python "$scripts\parse_books.py"
if ($LASTEXITCODE -ne 0) { Write-Error "parse_books.py failed"; exit 1 }

Write-Host "`n=== Step 2: LLM scoring (narrative arc, argument, clarity, signal) ===" -ForegroundColor Cyan
& $python "$scripts\score_books.py"
if ($LASTEXITCODE -ne 0) { Write-Error "score_books.py failed"; exit 1 }

Write-Host "`n=== Step 3: Generate HTML dashboard ===" -ForegroundColor Cyan
& $python "$scripts\generate_book_dashboard.py"
if ($LASTEXITCODE -ne 0) { Write-Error "generate_book_dashboard.py failed"; exit 1 }

if (-not $scoreOnly) {
    Write-Host "`n=== Step 4: Remediate low-scoring chapters (overall < 2.5) ===" -ForegroundColor Cyan
    & $python "$scripts\remediate_chapters.py"
    if ($LASTEXITCODE -ne 0) { Write-Error "remediate_chapters.py failed"; exit 1 }
}

Write-Host "`n=== Done ===" -ForegroundColor Green
Write-Host "Dashboard:   .documentation\copilot\books-dashboard.html" -ForegroundColor Yellow
Write-Host "Reviews:     .documentation\copilot\book-reviews\" -ForegroundColor Yellow
Write-Host ""
Write-Host "To rewrite low-scoring chapters (review reports first):" -ForegroundColor Yellow
Write-Host "  .venv\Scripts\python $scripts\rewrite_chapters.py --dry-run" -ForegroundColor Gray
Write-Host "  .venv\Scripts\python $scripts\rewrite_chapters.py" -ForegroundColor Gray

$dashboard = Resolve-Path ".documentation\copilot\books-dashboard.html" -ErrorAction SilentlyContinue
if ($dashboard -and -not $env:CI) {
    try {
        $open = Read-Host "`nOpen dashboard in browser? (y/n)"
        if ($open -eq "y") { Start-Process $dashboard }
    } catch { }   # non-interactive mode — skip prompt
}
