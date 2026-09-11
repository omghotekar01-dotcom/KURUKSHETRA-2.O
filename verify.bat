@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3.11 scripts\preflight.py --strict
  if errorlevel 1 exit /b %ERRORLEVEL%
  py -3.11 scripts\bootstrap.py
) else (
  python scripts\preflight.py --strict
  if errorlevel 1 exit /b %ERRORLEVEL%
  python scripts\bootstrap.py
)
if errorlevel 1 exit /b %ERRORLEVEL%
backend\.venv\Scripts\python.exe scripts\acceptance.py
if errorlevel 1 (
  echo Acceptance failed.
  pause
  exit /b %ERRORLEVEL%
)
echo.
echo CLEAN-CLONE ACCEPTANCE PASSED.
