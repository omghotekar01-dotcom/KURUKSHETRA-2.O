param(
    [switch]$NoBrowser,
    [switch]$SkipSetup,
    [switch]$Verify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root ".run"
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$EnvFile = Join-Path $Root ".env"
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null

function Invoke-ProjectPython {
    param([string]$Script, [string[]]$Arguments = @())
    $Py = Get-Command py -ErrorAction SilentlyContinue
    if ($Py) {
        & py -3.11 $Script @Arguments
    }
    else {
        $Python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $Python) { throw "Python 3.11 is required. Install it and run start.bat again." }
        & python $Script @Arguments
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Test-BackendHealth {
    try {
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        return ($null -ne $result)
    }
    catch { return $false }
}

function Test-LocalPort {
    param([int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync("127.0.0.1", $Port)
        if (-not $task.Wait(400)) { return $false }
        return $client.Connected
    }
    catch { return $false }
    finally { $client.Dispose() }
}

Write-Host ""
Write-Host "AI Agentic Bug Router" -ForegroundColor Cyan
Write-Host "Reproducible local launcher" -ForegroundColor DarkGray
Write-Host ""

Invoke-ProjectPython (Join-Path $Root "scripts\preflight.py") @("--strict")

if (-not $SkipSetup) {
    Invoke-ProjectPython (Join-Path $Root "scripts\bootstrap.py")
}

if (-not (Test-Path $VenvPython)) {
    throw "backend/.venv is missing. Run start.bat without -SkipSetup."
}

if ($Verify) {
    & $VenvPython (Join-Path $Root "scripts\acceptance.py")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-BackendHealth)) {
    if (Test-LocalPort 8000) {
        throw "Port 8000 is occupied by another service and /health is not responding. Stop that process before launching."
    }
    $backendCommand = "Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --env-file '$EnvFile'"
    $backendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)
    Set-Content -Path (Join-Path $RunDir "backend.pid") -Value $backendProcess.Id
    Write-Host "Started backend shell PID $($backendProcess.Id)" -ForegroundColor Green
}
else {
    Write-Host "Backend already healthy on port 8000; reusing it." -ForegroundColor Yellow
}

$backendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-BackendHealth) { $backendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $backendReady) { throw "Backend did not become healthy within 60 seconds. Check the backend terminal." }
Write-Host "Backend health: PASS" -ForegroundColor Green

if (-not (Test-LocalPort 5173)) {
    $frontendCommand = "Set-Location '$FrontendDir'; npm run dev -- --host 127.0.0.1"
    $frontendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)
    Set-Content -Path (Join-Path $RunDir "frontend.pid") -Value $frontendProcess.Id
    Write-Host "Started frontend shell PID $($frontendProcess.Id)" -ForegroundColor Green
}
else {
    Write-Host "Frontend port 5173 is already active; reusing it." -ForegroundColor Yellow
}

$frontendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-LocalPort 5173) { $frontendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $frontendReady) { throw "Frontend did not become available within 60 seconds. Check the frontend terminal." }

Write-Host ""
Write-Host "READY" -ForegroundColor Green
Write-Host "Dashboard:       http://127.0.0.1:5173"
Write-Host "API health:      http://127.0.0.1:8000/health"
Write-Host "API docs:        http://127.0.0.1:8000/docs"
Write-Host "Evidence Lab:    http://127.0.0.1:5173/evidence"
Write-Host "Remediation:     http://127.0.0.1:5173/remediate"
Write-Host "Evaluation Lab:  http://127.0.0.1:5173/evaluation"
Write-Host "Stop services:   stop.bat"
Write-Host ""

if (-not $NoBrowser) {
    Start-Process "http://127.0.0.1:5173"
}
