param(
    [string]$SourcePath = "D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16",
    [string]$TargetUri = "viking://resources/news-us-china-2026-05"
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$ScriptsDir = Join-Path $ProjectRoot ".venv\Scripts"
$Ov = Join-Path $ScriptsDir "ov.exe"

if (-not (Test-Path $Ov)) {
    throw "ov.exe not found: $Ov"
}

if (-not (Test-Path $SourcePath)) {
    throw "news corpus path not found: $SourcePath"
}

function Invoke-Step {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}

Write-Output "1. Check OpenViking health"
Invoke-Step $Ov health

Write-Output ""
Write-Output "2. Count markdown files"
$files = Get-ChildItem -Recurse -File -Filter *.md -LiteralPath $SourcePath
Write-Output "Markdown files: $($files.Count)"
Write-Output "Source path: $SourcePath"
Write-Output "Target URI: $TargetUri"

Write-Output ""
Write-Output "3. Import news corpus"
Invoke-Step $Ov add-resource $SourcePath --to $TargetUri --wait

Write-Output ""
Write-Output "4. Wait for background queues"
Invoke-Step $Ov wait

Write-Output ""
Write-Output "5. Show imported tree"
Invoke-Step $Ov tree $TargetUri -L 2
