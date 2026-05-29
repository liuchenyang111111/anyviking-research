param(
    [string]$Scope = "viking://resources/smoke-corpus",
    [string]$Question = "What is the core purpose of the second phase?"
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$Cli = Join-Path $ProjectRoot ".venv\Scripts\ar.exe"

if (-not (Test-Path $Cli)) {
    throw "ar.exe not found: $Cli. Run: .\.venv\Scripts\python.exe -m pip install -e .[openviking] --no-build-isolation"
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
Invoke-Step $Cli health

Write-Output ""
Write-Output "2. Import smoke corpus"
Invoke-Step $Cli import-local .\examples\smoke_corpus --to $Scope

Write-Output ""
Write-Output "3. Show resource tree"
Invoke-Step $Cli tree $Scope -L 2

Write-Output ""
Write-Output "4. Search with project CLI"
Invoke-Step $Cli search $Question --scope $Scope --top-k 3 --format text --documents-only
