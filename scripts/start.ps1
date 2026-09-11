param(
    [switch]$NoBrowser,
    [switch]$SkipSetup,
    [switch]$Verify,
    [int]$BackendPort = 0,
    [int]$FrontendPort = 0
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

function Test-LocalPort {
    param([int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync("127.0.0.1", $Port)
        if (-not $task.Wait(350)) { return $false }
        return $client.Connected
    }
    catch { return $false }
    finally { $client.Dispose() }
}

function Select-FreePort {
    param(
        [int]$Requested,
        [int]$Preferred,
        [int]$FallbackStart,
        [string]$Name
    )

    if ($Requested -gt 0) {
        if (Test-LocalPort $Requested) {
            throw "$Name port $Requested is already occupied. Choose another port or omit the port argument for automatic selection."
        }
        return $Requested
    }

    if (-not (Test-LocalPort $Preferred)) { return $Preferred }

    for ($candidate = $FallbackStart; $candidate -lt ($FallbackStart + 100); $candidate++) {
        if (-not (Test-LocalPort $candidate)) { return $candidate }
    }

    throw "Could not find a free local port for $Name."
}

function Test-BackendHealth {
    param([int]$Port)
    try {
        $result = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
        return ($null -ne $result -and $result.status -eq "ok")
    }
    catch { return $false }
}

function Test-FrontendHttp {
    param([int]$Port)
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 2
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    }
    catch { return $false }
}

Write-Host ""
Write-Host "AI Agentic Bug Router" -ForegroundColor Cyan
Write-Host "Reproducible local launcher" -ForegroundColor DarkGray
Write-Host ""

Invoke-ProjectPython (Join-Path $Root "scripts\preflight.py") @("--strict", "--ci")

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

$ResolvedBackendPort = Select-FreePort -Requested $BackendPort -Preferred 8000 -FallbackStart 8011 -Name "Backend"
$ResolvedFrontendPort = Select-FreePort -Requested $FrontendPort -Preferred 5173 -FallbackStart 5181 -Name "Frontend"

$ApiBase = "http://127.0.0.1:$ResolvedBackendPort"
$DashboardBase = "http://127.0.0.1:$ResolvedFrontendPort"

Write-Host "Selected backend port:  $ResolvedBackendPort" -ForegroundColor Cyan
Write-Host "Selected frontend port: $ResolvedFrontendPort" -ForegroundColor Cyan

$backendCommand = "Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --reload --host 127.0.0.1 --port $ResolvedBackendPort --env-file '$EnvFile'"
$backendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)
Set-Content -Path (Join-Path $RunDir "backend.pid") -Value $backendProcess.Id
Set-Content -Path (Join-Path $RunDir "backend.port") -Value $ResolvedBackendPort
Write-Host "Started backend shell PID $($backendProcess.Id)" -ForegroundColor Green

$backendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-BackendHealth $ResolvedBackendPort) { $backendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $backendReady) {
    throw "Backend did not become healthy on port $ResolvedBackendPort within 60 seconds. Check the backend terminal."
}
Write-Host "Backend health: PASS" -ForegroundColor Green

$frontendCommand = "Set-Location '$FrontendDir'; `$env:VITE_API_BASE_URL='$ApiBase'; npm run dev -- --host 127.0.0.1 --port $ResolvedFrontendPort --strictPort"
$frontendProcess = Start-Process powershell -PassThru -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)
Set-Content -Path (Join-Path $RunDir "frontend.pid") -Value $frontendProcess.Id
Set-Content -Path (Join-Path $RunDir "frontend.port") -Value $ResolvedFrontendPort
Write-Host "Started frontend shell PID $($frontendProcess.Id)" -ForegroundColor Green

$frontendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    if (Test-FrontendHttp $ResolvedFrontendPort) { $frontendReady = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $frontendReady) {
    throw "Frontend did not become available on port $ResolvedFrontendPort within 60 seconds. Check the frontend terminal."
}
Write-Host "Frontend health: PASS" -ForegroundColor Green

Write-Host ""
Write-Host "READY" -ForegroundColor Green
Write-Host "Dashboard:       $DashboardBase"
Write-Host "Real AutoFix:    $DashboardBase/prototype"
Write-Host "AI Reasoning:    $DashboardBase/ai"
Write-Host "Judge Mode:      $DashboardBase/demo"
Write-Host "API health:      $ApiBase/health"
Write-Host "API docs:        $ApiBase/docs"
Write-Host "Evidence Lab:    $DashboardBase/evidence"
Write-Host "Remediation:     $DashboardBase/remediate"
Write-Host "Evaluation Lab:  $DashboardBase/evaluation"
Write-Host "Readiness:       $DashboardBase/readiness"
Write-Host "Stop services:   stop.bat"
Write-Host ""

if (-not $NoBrowser) {
    Start-Process $DashboardBase
}
