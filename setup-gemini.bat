@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================================
echo   GEMINI PRIMARY AI SETUP - AI AGENTIC BUG ROUTER
echo ============================================================
echo.

if not exist ".env" (
  if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo [GEMINI] Created local .env from .env.example.
  ) else (
    echo [GEMINI] ERROR: .env.example was not found.
    pause
    exit /b 1
  )
)

echo [GEMINI] Gemini will be PRIMARY when LLM_PROVIDER=auto and a key is configured.
echo [GEMINI] Local Qwen/Ollama remains SECONDARY fallback.
echo [GEMINI] Registered /prototype demos stay deterministic for reliable FAIL-to-PASS validation.
echo [GEMINI] Your key is stored only in local .env, which is gitignored.
echo [GEMINI] Recommended default: gemini-3.5-flash-lite for fast hackathon usage.
echo.
set /p "OPEN_AI_STUDIO=Open Google AI Studio API-key page now? [Y/N]: "
if /I "%OPEN_AI_STUDIO%"=="Y" start "" "https://aistudio.google.com/app/apikey"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; $envPath=Join-Path (Get-Location) '.env'; $secure=Read-Host '[GEMINI] Paste Gemini API key (input hidden)' -AsSecureString; $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure); try { $key=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }; if([string]::IsNullOrWhiteSpace($key)){ throw 'No key entered.' }; $content=Get-Content $envPath -Raw; function Set-Line([string]$name,[string]$value){ $script:content=[regex]::Replace($script:content,'(?m)^'+[regex]::Escape($name)+'=.*$', $name+'='+$value); if($script:content -notmatch '(?m)^'+[regex]::Escape($name)+'='){ $script:content=$script:content.TrimEnd()+[Environment]::NewLine+$name+'='+$value+[Environment]::NewLine } }; Set-Line 'LLM_PROVIDER' 'auto'; Set-Line 'GEMINI_API_KEY' $key; Set-Line 'GEMINI_BASE_URL' 'https://generativelanguage.googleapis.com/v1beta/openai'; Set-Line 'GEMINI_MODEL' 'gemini-3.5-flash-lite'; Set-Line 'AUTOFIX_AI_ENABLED' 'false'; Set-Content -Path $envPath -Value $content -Encoding UTF8; $headers=@{Authorization='Bearer '+$key}; $body=@{model='gemini-3.5-flash-lite';messages=@(@{role='user';content='Reply with exactly READY and nothing else.'});temperature=0} | ConvertTo-Json -Depth 8; $r=Invoke-RestMethod -Method Post -Uri 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions' -Headers $headers -ContentType 'application/json' -Body $body -TimeoutSec 30; $reply=[string]$r.choices[0].message.content; if([string]::IsNullOrWhiteSpace($reply)){ throw 'Gemini returned an empty response.' }; Write-Host ('[GEMINI] Live API reply: '+$reply.Trim()); Write-Host '[GEMINI] VERIFIED: Gemini primary runtime is configured.'"

if errorlevel 1 (
  echo.
  echo [GEMINI] Setup/probe failed. Check the key, account eligibility, model quota and internet connection.
  echo [GEMINI] No key is ever committed by this script; .env remains local.
  pause
  exit /b 1
)

echo.
echo [GEMINI] READY.
echo [GEMINI] Provider policy: Gemini FIRST, local Qwen/Ollama SECOND, deterministic evidence fallback LAST.
echo [GEMINI] /prototype policy: deterministic reviewed patches for reliable live validation.
echo [GEMINI] Restart Bug Router with stop.bat then start.bat so the backend reloads .env.
echo.
pause
endlocal
