param(
  [Parameter(Mandatory = $true)]
  [string]$Slug,

  [Parameter(Mandatory = $false)]
  [switch]$Open
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Ensure Pandoc is on PATH (Windows default install location)
# ---------------------------------------------------------------------------
$pandocDir = Join-Path $env:LOCALAPPDATA "Pandoc"
if (Test-Path $pandocDir) {
  $env:PATH = "$pandocDir$([IO.Path]::PathSeparator)$env:PATH"
}

# ---------------------------------------------------------------------------
# Run the book build pipeline
# ---------------------------------------------------------------------------
Write-Host "Building book: $Slug" -ForegroundColor Cyan
Write-Host ""

npm run build:book -- $Slug

if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "Build failed (exit $LASTEXITCODE). Check output above." -ForegroundColor Red
  exit 1
}

# ---------------------------------------------------------------------------
# Report output paths
# ---------------------------------------------------------------------------
$outDir = Join-Path "books\publish" $Slug
Write-Host ""
Write-Host "Output:" -ForegroundColor Green

Get-ChildItem $outDir -ErrorAction SilentlyContinue | ForEach-Object {
  $kb = [math]::Round($_.Length / 1KB)
  Write-Host "  $($_.FullName)  ($kb KB)" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Optionally open the output folder in Explorer
# ---------------------------------------------------------------------------
if ($Open) {
  Start-Process explorer.exe (Resolve-Path $outDir)
}
