param(
    [string]$Question = "特朗普访华实际达成了哪些成果"
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

$Cli = Join-Path $ProjectRoot ".venv\Scripts\ov-search-skill.exe"
$SourcePath = "D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16"
$TargetUri = "viking://resources/news-us-china-2026-05"

if (-not (Test-Path $Cli)) {
    throw "ov-search-skill.exe not found: $Cli"
}

Write-Output "1. Check OpenViking health"
& $Cli health

Write-Output ""
Write-Output "2. Import old news corpus"
& $Cli import-local $SourcePath --to $TargetUri

Write-Output ""
Write-Output "3. Show imported tree"
& $Cli tree $TargetUri -L 1

Write-Output ""
Write-Output "4. Search news corpus"
& $Cli search $Question --scope $TargetUri --top-k 5 --documents-only --format text
