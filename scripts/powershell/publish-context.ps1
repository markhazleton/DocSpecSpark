# DocSpark helper script
param()
Get-ChildItem . -Recurse -Include *.md -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\(\.git|\.venv|dist|site)\\' } |
    Select-Object FullName