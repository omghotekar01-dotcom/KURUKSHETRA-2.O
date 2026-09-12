@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================================
echo   BUG ROUTER - VALIDATION REPAIR + SELF-CHECK
echo ============================================================
echo.

if not exist ".env" (
  if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo [ENV] Created .env from .env.example.
  ) else (
    echo [FAIL] .env.example is missing.
    pause
    exit /b 1
  )
)

echo [1/4] Forcing registered /prototype demos onto deterministic reviewed repairs...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p=Join-Path (Get-Location) '.env'; $c=Get-Content $p -Raw; if($c -match '(?m)^AUTOFIX_AI_ENABLED='){ $c=[regex]::Replace($c,'(?m)^AUTOFIX_AI_ENABLED=.*$','AUTOFIX_AI_ENABLED=false') } else { $c=$c.TrimEnd()+[Environment]::NewLine+'AUTOFIX_AI_ENABLED=false'+[Environment]::NewLine }; Set-Content -Path $p -Value $c -Encoding UTF8"
if errorlevel 1 goto :fail

set "PY=backend\.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo [2/4] Backend virtual environment is missing. Creating it...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.11 -m venv backend\.venv
  ) else (
    python -m venv backend\.venv
  )
  if errorlevel 1 goto :fail
) else (
  echo [2/4] Backend virtual environment found.
)

echo [3/4] Repairing pinned validation dependencies...
"%PY%" -m pip install --disable-pip-version-check -r backend\requirements.txt
if errorlevel 1 goto :fail

echo.
echo [4/4] Running isolated FAIL-to-PASS proof for every registered demo target...
"%PY%" scripts\validate_demo_contracts.py
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   VALIDATION READY
echo ============================================================
echo Registered /prototype targets now use the deterministic exact-patch path.
echo Gemini remains available for incident reasoning and Judge Intake.
echo.
echo Restart the product so .env is reloaded:
echo   stop.bat
echo   start.bat
echo.
pause
exit /b 0

:fail
echo.
echo [FAIL] Validation repair/self-check did not complete.
echo Read the error above. Do not use the live AutoFix demo until this script passes.
echo.
pause
exit /b 1
