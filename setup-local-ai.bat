@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "MODEL=qwen3:4b"

where ollama >nul 2>nul
if errorlevel 1 (
  echo [LOCAL AI] Ollama is not installed or is not on PATH.
  echo [LOCAL AI] Install Ollama for Windows, open it once, reopen this terminal, then retry.
  echo [LOCAL AI] The built-in AutoFix targets can still use deterministic verified fallback.
  exit /b 1
)

echo [LOCAL AI] Checking Ollama service...
ollama list >nul 2>nul
if errorlevel 1 (
  echo [LOCAL AI] Ollama is not reachable yet. Starting "ollama serve"...
  start "Ollama Local AI" /min cmd /c "ollama serve"

  set "OLLAMA_READY="
  for /L %%I in (1,1,20) do (
    if not defined OLLAMA_READY (
      ollama list >nul 2>nul
      if not errorlevel 1 (
        set "OLLAMA_READY=1"
      ) else (
        echo [LOCAL AI] Waiting for service... %%I/20
        timeout /t 2 /nobreak >nul
      )
    )
  )

  if not defined OLLAMA_READY (
    echo [LOCAL AI] Ollama service did not become reachable within the startup window.
    echo [LOCAL AI] Open the Ollama Windows app once, then run setup-local-ai.bat again.
    exit /b 1
  )
)

echo [LOCAL AI] Ollama service: REACHABLE
echo [LOCAL AI] Ensuring model is installed: %MODEL%
ollama pull %MODEL%
if errorlevel 1 (
  echo [LOCAL AI] Model pull failed. Check internet access and free disk space, then retry.
  exit /b 1
)

ollama list | findstr /I /C:"%MODEL%" >nul
if errorlevel 1 (
  echo [LOCAL AI] %MODEL% was not found after pull. Refusing to report READY.
  exit /b 1
)

echo [LOCAL AI] Running a real local inference warm-up...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$payload = @{model='%MODEL%';stream=$false;messages=@(@{role='user';content='Reply with exactly READY and nothing else.'});options=@{temperature=0}}; $body = ConvertTo-Json -InputObject $payload -Depth 8; try { $r = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:11434/api/chat' -ContentType 'application/json' -Body $body -TimeoutSec 120; if ([string]::IsNullOrWhiteSpace([string]$r.message.content)) { exit 2 }; Write-Host ('[LOCAL AI] Native inference reply: ' + ([string]$r.message.content).Trim()) } catch { Write-Host ('[LOCAL AI] Inference probe failed: ' + $_.Exception.Message); exit 3 }"
if errorlevel 1 (
  echo [LOCAL AI] Ollama and the model are installed, but a real inference call failed.
  echo [LOCAL AI] Close/reopen the Ollama app and retry before the judge demo.
  exit /b 1
)

echo.
echo [LOCAL AI] Ollama service: REACHABLE
echo [LOCAL AI] %MODEL%: INSTALLED + INFERENCE VERIFIED
echo [LOCAL AI] Start the product with start.bat.
echo [LOCAL AI] In Judge Intake, "Test Qwen now" performs the backend's own live inference proof.
endlocal
