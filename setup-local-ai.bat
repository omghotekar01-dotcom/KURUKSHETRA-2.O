@echo off
setlocal
where ollama >nul 2>nul
if errorlevel 1 (
  echo [LOCAL AI] Ollama is not installed or not on PATH.
  echo Install Ollama for Windows, reopen this terminal, then run this file again.
  echo The AutoFix prototype itself can still run with deterministic verification.
  exit /b 1
)

echo [LOCAL AI] Pulling the default zero-cost model: qwen3:4b
ollama pull qwen3:4b
if errorlevel 1 (
  echo [LOCAL AI] Model pull failed. Check connectivity/disk space and retry.
  exit /b 1
)

echo.
echo [LOCAL AI] qwen3:4b is ready.
echo Start the project with start.bat. Ollama normally exposes http://localhost:11434 automatically.
echo Open /prototype to run the real AutoFix proof.
endlocal
