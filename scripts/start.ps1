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
    param([int]$Port)
    try {
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
        return ($null -ne $result -and $result.status -eq "ok")
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

function Find-FreePort {
    param([int]$StartPort, [int]$EndPort)
    for ($Port = $StartPort; $Port -le $EndPort; $Port++) {
        if (-not (Test-LocalPort $Port)) { return $Port }
    }
    throw "No free local port found in range $StartPort-$EndPort."
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

# The frontend must remain on localhost:5173 because that is the default trusted
# development origin configured by the API. The backend port can move safely.
if (Test-LocalPort 5173) {
    throw "Frontend port 5173 is already occupied. Stop that process (or run stop.bat if it is a previous project launch) before starting this build."
}

$BackendPort = Find-FreePort 8000 8099
if ($BackendPort -ne 8000) {
    Write-Host "Port 8000 is occupied; using backend port $BackendPort instead." -ForegroundColor Yellow
}

$backendCommand = "Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort --env-file '$EnvFile'"
$backendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)
Set-Content -Path (Join-Path $RunDir "backend.pid") -Value $backendProcess.Id
Set-Content -Path (Join-Path $RunDir "backend.port") -Value $BackendPort
Write-Host "Started backend shell PID $($backendProcess.Id) on port $BackendPort" -ForegroundColor Green

$backendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-BackendHealth $BackendPort) { $backendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $backendReady) { throw "Backend did not become healthy within 60 seconds. Check the backend terminal." }
Write-Host "Backend health: PASS" -ForegroundColor Green

$ApiBase = "http://127.0.0.1:$BackendPort"
$frontendCommand = "Set-Location '$FrontendDir'; `$env:VITE_API_BASE_URL='$ApiBase'; npm run dev -- --host localhost --port 5173 --strictPort"
$frontendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)
Set-Content -Path (Join-Path $RunDir "frontend.pid") -Value $frontendProcess.Id
Set-Content -Path (Join-Path $RunDir "frontend.port") -Value 5173
Write-Host "Started frontend shell PID $($frontendProcess.Id)" -ForegroundColor Green

$frontendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-LocalPort 5173) { $frontendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $frontendReady) { throw "Frontend did not become available within 60 seconds. Check the frontend terminal." }

Write-Host ""
Write-Host "READY" -ForegroundColor Green
Write-Host "Dashboard:       http://localhost:5173"
Write-Host "API health:      $ApiBase/health"
Write-Host "API docs:        $ApiBase/docs"
Write-Host "Evidence Lab:    http://localhost:5173/evidence"
Write-Host "Remediation:     http://localhost:5173/remediate"
Write-Host "Evaluation Lab:  http://localhost:5173/evaluation"
Write-Host "Stop services:   stop.bat"
Write-Host ""

if (-not $NoBrowser) {
    Start-Process "http://localhost:5173"
}
