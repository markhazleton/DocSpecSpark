# DocSpark helper script
param()
Get-ChildItem . -Recurse -Include *.md -File | Select-Object -First 50 FullName