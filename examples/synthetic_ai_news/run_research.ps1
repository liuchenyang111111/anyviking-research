param(
    [string]$ConfigPath = "examples\synthetic_ai_news\research_questions.yaml",
    [string]$OutputPath = "reports\synthetic_ai_news_research_draft.md",
    [int]$TopK = 4,
    [int]$FetchK = 0
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $ProjectRoot

$Cli = Join-Path $ProjectRoot ".venv\Scripts\ov-search-skill.exe"

if (-not (Test-Path $Cli)) {
    throw "ov-search-skill.exe not found: $Cli"
}

Write-Output "1. Check OpenViking health"
& $Cli health

Write-Output ""
Write-Output "2. Generate synthetic retrieval research draft"
$ResearchArgs = @("research", $ConfigPath, "--output", $OutputPath, "--top-k", "$TopK")
if ($FetchK -gt 0) {
    $ResearchArgs += @("--fetch-k", "$FetchK")
}
& $Cli @ResearchArgs

Write-Output ""
Write-Output "Output: $OutputPath"
