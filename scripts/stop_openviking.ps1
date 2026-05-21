param(
    [int]$Port = 1933
)

$ErrorActionPreference = "Stop"

$processes = Get-Process openviking-server -ErrorAction SilentlyContinue

if (-not $processes) {
    Write-Output "No openviking-server process found."
    exit 0
}

foreach ($process in $processes) {
    Write-Output "Stopping openviking-server, PID: $($process.Id)"
    Stop-Process -Id $process.Id
}

Start-Sleep -Seconds 2

try {
    Invoke-RestMethod "http://127.0.0.1:$Port/health" -TimeoutSec 3 | Out-Null
    Write-Output "Warning: port $Port still responds."
} catch {
    Write-Output "OpenViking stopped."
}
