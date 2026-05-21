param(
    [string]$Scope = "viking://resources/smoke-corpus",
    [string]$Question = "second phase core local retrieval"
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
$Cli = Join-Path $ScriptsDir "ov-search-skill.exe"

if (-not (Test-Path $Ov)) {
    throw "ov.exe not found: $Ov"
}

if (-not (Test-Path $Cli)) {
    throw "ov-search-skill.exe not found: $Cli. Run: .\.venv\Scripts\python.exe -m pip install -e . --no-deps --no-build-isolation"
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
Write-Output "2. Import smoke corpus"
Invoke-Step $Ov add-resource .\examples\smoke_corpus --to $Scope --wait

Write-Output ""
Write-Output "3. Wait for background queues"
Invoke-Step $Ov wait

Write-Output ""
Write-Output "4. Show resource tree"
Invoke-Step $Ov tree $Scope -L 2

Write-Output ""
Write-Output "5. Search with ov find"
Invoke-Step $Ov find $Question --uri $Scope

Write-Output ""
Write-Output "6. Search with project CLI"
Invoke-Step $Cli search $Question --scope $Scope --top-k 3
