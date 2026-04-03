# DocSpark helper script
param()
Get-ChildItem .documentation -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName