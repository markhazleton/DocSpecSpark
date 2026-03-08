#!/usr/bin/env pwsh

param(
    [switch]$Force,
    [switch]$SkipPlanningCopy
)

$ErrorActionPreference = 'Stop'

$docSpecRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $docSpecRoot
$templateRoot = Join-Path $docSpecRoot 'repo-template'
$planningRoot = Join-Path $repoRoot '.DocSpecSpark\planning'

if (-not (Test-Path $templateRoot)) {
    throw "Missing repo template directory: $templateRoot"
}

function Copy-TemplateTree {
    param(
        [string]$Source,
        [string]$Destination,
        [switch]$ForceCopy
    )

    Get-ChildItem -Path $Source -Force | ForEach-Object {
        if ($_.Name -in @('__pycache__', '.pytest_cache', '.ruff_cache')) {
            return
        }

        $targetPath = Join-Path $Destination $_.Name

        if ($_.PSIsContainer) {
            if (-not (Test-Path $targetPath)) {
                New-Item -ItemType Directory -Path $targetPath | Out-Null
            }

            Copy-TemplateTree -Source $_.FullName -Destination $targetPath -ForceCopy:$ForceCopy
            return
        }

        if ((Test-Path $targetPath) -and -not $ForceCopy) {
            Write-Host "skip  $targetPath"
            return
        }

        Copy-Item -Path $_.FullName -Destination $targetPath -Force:$ForceCopy
        Write-Host "write $targetPath"
    }
}

Write-Host "Bootstrapping DocSpecSpark source repository in $repoRoot"
Copy-TemplateTree -Source $templateRoot -Destination $repoRoot -ForceCopy:$Force

if (-not $SkipPlanningCopy) {
    if (-not (Test-Path $planningRoot)) {
        New-Item -ItemType Directory -Path $planningRoot | Out-Null
    }

    Get-ChildItem -Path $docSpecRoot -Filter '*.md' -File |
        Where-Object { $_.Name -notin @('BOOTSTRAP.md') } |
        ForEach-Object {
            $targetPath = Join-Path $planningRoot $_.Name
            if ((Test-Path $targetPath) -and -not $Force) {
                Write-Host "skip  $targetPath"
                return
            }

            Copy-Item -Path $_.FullName -Destination $targetPath -Force:$Force
            Write-Host "copy  $targetPath"
        }
}

Write-Host ''
Write-Host 'Bootstrap complete.'
Write-Host 'Next steps:'
Write-Host '  1. uv sync'
Write-Host '  2. uv run docspec init ../acme-corp-docs --profile small-business-manufacturing'
Write-Host '  3. uv run docspec show-constitution --workspace ../acme-corp-docs'
Write-Host '  4. uv run docspec create employee-handbook.md --workspace ../acme-corp-docs --overwrite'
Write-Host '  5. uv run docspec build --workspace ../acme-corp-docs'
Write-Host '  6. uv run docspec publish --workspace ../acme-corp-docs --version 1.0.0'