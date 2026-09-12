@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 goto use_python

py -3.11 scripts\preflight.py --strict
if errorlevel 1 goto preflight_failed

py -3.11 scripts\bootstrap.py
if errorlevel 1 goto bootstrap_failed
goto acceptance

:use_python
python scripts\preflight.py --strict
if errorlevel 1 goto preflight_failed

python scripts\bootstrap.py
if errorlevel 1 goto bootstrap_failed

:acceptance
backend\.venv\Scripts\python.exe scripts\acceptance.py
if errorlevel 1 goto acceptance_failed

echo.
echo CLEAN-CLONE ACCEPTANCE PASSED.
exit /b 0

:preflight_failed
echo.
echo [FAIL] Environment preflight failed. Fix the reported requirement and rerun verify.bat.
pause
exit /b 1

:bootstrap_failed
echo.
echo [FAIL] Dependency bootstrap failed. Acceptance was NOT run against a partial install.
echo Close any project dev-server windows if a Windows EPERM/file-lock error was shown, then rerun verify.bat.
pause
exit /b 1

:acceptance_failed
echo.
echo [FAIL] Acceptance failed.
pause
exit /b 1
