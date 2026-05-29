param(
    [int]$Port = 1933
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PidFile = Join-Path $ProjectRoot "workspace\.openviking.pid"
$processes = @()

if (Test-Path $PidFile) {
    $pidText = Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pidText -match "^\d+$") {
        $pidProcess = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
        if ($pidProcess) {
            $processes += $pidProcess
        }
    }
}

$processes += @(Get-Process openviking-server -ErrorAction SilentlyContinue)

$pythonServers = Get-CimInstance Win32_Process -Filter "name = 'python.exe' or name = 'pythonw.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "openviking_cli\.server_bootstrap" }
foreach ($pythonServer in $pythonServers) {
    $process = Get-Process -Id $pythonServer.ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        $processes += $process
    }
}

$processes = $processes | Sort-Object Id -Unique

if (-not $processes) {
    Write-Output "No openviking-server process found."
    Remove-Item $PidFile -ErrorAction SilentlyContinue
    exit 0
}

foreach ($process in $processes) {
    Write-Output "Stopping openviking-server, PID: $($process.Id)"
    Stop-Process -Id $process.Id
}

Remove-Item $PidFile -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

try {
    Invoke-RestMethod "http://127.0.0.1:$Port/health" -TimeoutSec 3 | Out-Null
    Write-Output "Warning: port $Port still responds."
} catch {
    Write-Output "OpenViking stopped."
}
