param(
    [string]$Question = "为什么开源项目需要合成 demo 语料",
    [string]$TargetUri = "viking://resources/synthetic-ai-news"
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

$Cli = Join-Path $ProjectRoot ".venv\Scripts\ov-search-skill.exe"
$SourcePath = Join-Path $ProjectRoot "examples\synthetic_ai_news\source"

if (-not (Test-Path $Cli)) {
    throw "ov-search-skill.exe not found: $Cli"
}

Write-Output "1. Check OpenViking health"
& $Cli health

Write-Output ""
Write-Output "2. Import synthetic AI news corpus"
& $Cli import-local $SourcePath --to $TargetUri

Write-Output ""
Write-Output "3. Show imported tree"
& $Cli tree $TargetUri -L 1

Write-Output ""
Write-Output "4. Search synthetic corpus"
& $Cli search $Question --scope $TargetUri --top-k 5 --documents-only --format text
