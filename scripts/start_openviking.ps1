param(
    [string]$ConfigPath = "config\ov.conf",
    [string]$HostName = "127.0.0.1",
    [int]$Port = 1933
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Server = Join-Path $ProjectRoot ".venv\Scripts\openviking-server.exe"
$Config = Resolve-Path (Join-Path $ProjectRoot $ConfigPath)
$BaseUrl = "http://${HostName}:$Port"

if (-not (Test-Path $Server)) {
    throw "openviking-server not found: $Server. Activate .venv and install openviking first."
}

try {
    $health = Invoke-RestMethod "$BaseUrl/health" -TimeoutSec 3
    if ($health.healthy) {
        Write-Output "OpenViking is already running at $BaseUrl."
        exit 0
    }
} catch {
    # Continue when the service is not running.
}

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$process = Start-Process `
    -FilePath $Server `
    -ArgumentList @("--config", $Config.Path, "--host", $HostName, "--port", [string]$Port) `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 8

try {
    $health = Invoke-RestMethod "$BaseUrl/health" -TimeoutSec 10
    Write-Output "OpenViking started."
    Write-Output "PID: $($process.Id)"
    Write-Output "Health: $($health.status), version $($health.version)"
} catch {
    throw "OpenViking process started but health check failed. PID: $($process.Id). Check terminal output or logs."
}
