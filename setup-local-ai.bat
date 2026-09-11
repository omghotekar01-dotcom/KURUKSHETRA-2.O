@echo off
setlocal
cd /d "%~dp0"

where ollama >nul 2>nul
if errorlevel 1 (
  echo [LOCAL AI] Ollama is not installed or not on PATH.
  echo Install Ollama for Windows, reopen this terminal, then run this file again.
  echo The built-in AutoFix targets can still run with deterministic verified fallback.
  exit /b 1
)

echo [LOCAL AI] Checking Ollama service...
ollama list >nul 2>nul
if errorlevel 1 (
  echo [LOCAL AI] Ollama service is not reachable. Starting it in a minimized window...
  start "Ollama Local AI" /min cmd /k "ollama serve"
  timeout /t 4 /nobreak >nul
  ollama list >nul 2>nul
  if errorlevel 1 (
    echo [LOCAL AI] Ollama service still is not reachable.
    echo Open the Ollama Windows app once, then run setup-local-ai.bat again.
    exit /b 1
  )
)

echo [LOCAL AI] Pulling the default zero-cost model: qwen3:4b
ollama pull qwen3:4b
if errorlevel 1 (
  echo [LOCAL AI] Model pull failed. Check connectivity and free disk space, then retry.
  exit /b 1
)

ollama list | findstr /I /C:"qwen3:4b" >nul
if errorlevel 1 (
  echo [LOCAL AI] qwen3:4b was not found after pull. Refusing to report READY.
  exit /b 1
)

echo.
echo [LOCAL AI] Ollama service: REACHABLE
echo [LOCAL AI] qwen3:4b: INSTALLED
echo [LOCAL AI] Start the project with start.bat.
echo [LOCAL AI] Open the printed Judge Intake URL and click "Test Qwen now".
echo [LOCAL AI] That button performs a real chat-completions inference probe and shows provider, model and latency.
endlocal
