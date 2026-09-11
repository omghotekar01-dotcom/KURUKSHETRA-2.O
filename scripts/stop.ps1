Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root ".run"

foreach ($name in @("frontend", "backend")) {
    $pidFile = Join-Path $RunDir "$name.pid"
    if (-not (Test-Path $pidFile)) { continue }

    $processId = (Get-Content $pidFile | Select-Object -First 1)
    if ($processId -match '^\d+$') {
        Write-Host "Stopping $name process tree (PID $processId)..."
        & taskkill /PID $processId /T /F | Out-Null
    }
    Remove-Item $pidFile -Force
}

Write-Host "AI Agentic Bug Router local services stopped." -ForegroundColor Green
