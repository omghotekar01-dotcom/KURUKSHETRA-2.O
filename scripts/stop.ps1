Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root ".run"

# PID files can outlive the process that created them. Windows may then reuse the
# numeric PID for an unrelated process, including the PowerShell/cmd tree that is
# currently starting this project. Treat recorded PIDs as hints and verify them
# before issuing a process-tree kill.
$launcherProcessIds = @()
$currentProcessId = [int]$PID
for ($depth = 0; $depth -lt 32 -and $currentProcessId -gt 0; $depth++) {
    if ($launcherProcessIds -contains $currentProcessId) { break }
    $launcherProcessIds += $currentProcessId
    $currentProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $currentProcessId" -ErrorAction SilentlyContinue
    if ($null -eq $currentProcess) { break }
    $parentProcessId = [int]$currentProcess.ParentProcessId
    if ($parentProcessId -le 0 -or $parentProcessId -eq $currentProcessId) { break }
    $currentProcessId = $parentProcessId
}

foreach ($name in @("frontend", "backend")) {
    $pidFile = Join-Path $RunDir "$name.pid"
    if (-not (Test-Path $pidFile)) { continue }

    $processIdText = (Get-Content $pidFile | Select-Object -First 1)
    if ($processIdText -notmatch '^\d+$') {
        Write-Host "Removing invalid $name PID record." -ForegroundColor Yellow
        Remove-Item $pidFile -Force
        continue
    }

    $processId = [int]$processIdText
    $trackedProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
    if ($null -eq $trackedProcess) {
        Write-Host "Removing stale $name PID record ($processId); process is already stopped." -ForegroundColor DarkGray
        Remove-Item $pidFile -Force
        continue
    }

    if ($launcherProcessIds -contains $processId) {
        Write-Host "Ignoring reused $name PID $processId because it belongs to the current launcher process tree." -ForegroundColor Yellow
        Remove-Item $pidFile -Force
        continue
    }

    $commandLine = [string]$trackedProcess.CommandLine
    $belongsToCheckout = -not [string]::IsNullOrWhiteSpace($commandLine) -and
        $commandLine.IndexOf($Root, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
    if (-not $belongsToCheckout) {
        Write-Host "Ignoring reused $name PID $processId because it is not owned by this checkout." -ForegroundColor Yellow
        Remove-Item $pidFile -Force
        continue
    }

    Write-Host "Stopping $name process tree (PID $processId)..."
    & taskkill /PID $processId /T /F 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Best-effort stop for $name PID $processId did not complete; continuing safely." -ForegroundColor Yellow
    }
    Remove-Item $pidFile -Force
}

Write-Host "AI Agentic Bug Router local services stopped." -ForegroundColor Green
