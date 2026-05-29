param(
    [switch]$NoOpenViking,
    [switch]$Dev
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonExe = "py"
    $PythonArgs = @("-3.12")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonExe = "python"
    $PythonArgs = @()
} else {
    throw "Python 3.12 was not found. Install Python 3.12 first."
}

Write-Output "Creating virtual environment: .venv"
& $PythonExe @PythonArgs -m venv .venv

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created: $VenvPython"
}

Write-Output "Upgrading packaging tools"
& $VenvPython -m pip install --upgrade pip setuptools wheel

$extras = @()
if (-not $NoOpenViking) {
    $extras += "openviking"
}
if ($Dev) {
    $extras += "dev"
}

$installTarget = "."
if ($extras.Count -gt 0) {
    $installTarget = ".[{0}]" -f ($extras -join ",")
}

Write-Output "Installing AnyViking Research: $installTarget"
& $VenvPython -m pip install -e $installTarget --no-build-isolation

$OvConf = Join-Path $ProjectRoot "config\ov.conf"
$OvConfExample = Join-Path $ProjectRoot "config\ov.conf.example"
$OvCliConf = Join-Path $ProjectRoot "config\ovcli.conf"
$OvCliConfExample = Join-Path $ProjectRoot "config\ovcli.conf.example"

if ((Test-Path $OvConfExample) -and -not (Test-Path $OvConf)) {
    Copy-Item $OvConfExample $OvConf
    Write-Output "Created config\ov.conf"
}

if ((Test-Path $OvCliConfExample) -and -not (Test-Path $OvCliConf)) {
    Copy-Item $OvCliConfExample $OvCliConf
    Write-Output "Created config\ovcli.conf"
}

Write-Output ""
Write-Output "Install complete."
Write-Output "Activate: .\.venv\Scripts\Activate.ps1"
Write-Output "Check:    .\.venv\Scripts\anyviking.exe doctor"
