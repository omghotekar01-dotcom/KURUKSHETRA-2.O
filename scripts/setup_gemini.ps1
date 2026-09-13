Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EnvPath = Join-Path $Root '.env'
$ExamplePath = Join-Path $Root '.env.example'

if (-not (Test-Path $EnvPath)) {
    if (-not (Test-Path $ExamplePath)) {
        throw '.env and .env.example are both missing.'
    }
    Copy-Item $ExamplePath $EnvPath -Force
    Write-Host '[GEMINI] Created .env from .env.example.' -ForegroundColor Green
}

function Set-EnvValue {
    param(
        [string]$Name,
        [string]$Value
    )

    $lines = @(Get-Content $EnvPath -ErrorAction Stop)
    $pattern = '^' + [regex]::Escape($Name) + '='
    $updated = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $pattern) {
            $lines[$i] = "$Name=$Value"
            $updated = $true
            break
        }
    }
    if (-not $updated) {
        $lines += "$Name=$Value"
    }
    Set-Content -Path $EnvPath -Value $lines -Encoding UTF8
}

Write-Host ''
Write-Host 'Gemini Developer API setup' -ForegroundColor Cyan
Write-Host 'The key is written only to your local .env file. Do not commit .env.' -ForegroundColor DarkGray
Write-Host ''

$secure = Read-Host 'Paste GEMINI_API_KEY' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

if ([string]::IsNullOrWhiteSpace($key)) {
    throw 'Gemini API key cannot be empty.'
}

Set-EnvValue 'LLM_PROVIDER' 'auto'
Set-EnvValue 'GEMINI_API_KEY' $key.Trim()
Set-EnvValue 'GEMINI_BASE_URL' 'https://generativelanguage.googleapis.com/v1beta/openai'
Set-EnvValue 'GEMINI_MODEL' 'gemini-3.5-flash-lite'

Write-Host '[GEMINI] Configuration saved locally.' -ForegroundColor Green
Write-Host '[GEMINI] Provider order: local Ollama/Qwen first, Gemini free-tier fallback second.' -ForegroundColor Cyan
Write-Host '[GEMINI] Model: gemini-3.5-flash-lite (chosen for fast/high-headroom free-tier use).' -ForegroundColor Cyan
Write-Host ''
Write-Host '[GEMINI] Testing the configured OpenAI-compatible Gemini endpoint...' -ForegroundColor Yellow

$headers = @{
    Authorization = "Bearer $($key.Trim())"
    'Content-Type' = 'application/json'
}
$body = @{
    model = 'gemini-3.5-flash-lite'
    temperature = 0
    max_tokens = 16
    messages = @(
        @{ role = 'system'; content = 'Reply with exactly READY.' },
        @{ role = 'user'; content = 'Connectivity check.' }
    )
} | ConvertTo-Json -Depth 8

try {
    $response = Invoke-RestMethod -Method Post -Uri 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions' -Headers $headers -Body $body -TimeoutSec 20
    $reply = [string]$response.choices[0].message.content
    if ([string]::IsNullOrWhiteSpace($reply)) {
        throw 'Gemini returned an empty response.'
    }
    Write-Host ("[GEMINI] Live inference: PASS -> " + $reply.Trim()) -ForegroundColor Green
    Write-Host '[GEMINI] Restart Bug Router with start.bat so every AI-backed path reloads the key.' -ForegroundColor Green
}
catch {
    Write-Host ('[GEMINI] Live probe failed: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host '[GEMINI] The key was still saved to .env. Check the key/quota, then rerun this setup.' -ForegroundColor Yellow
    exit 2
}
