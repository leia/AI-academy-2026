param(
    [string]$Port = "8787"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Error "Missing .venv. Please create/activate your virtual env first."
    exit 1
}

# Ensure .env is loaded by uvicorn process; Vite will call API_URL explicitly
$env:VITE_API_URL = "http://localhost:$Port"

Write-Host "Starting API on port $Port and frontend (Vite) on 5173..." -ForegroundColor Cyan

$api = Start-Process -NoNewWindow powershell -ArgumentList "-NoProfile", "-Command", ".\.venv\Scripts\python.exe -m uvicorn api:app --reload --port $Port" -PassThru
$web = Start-Process -NoNewWindow powershell -WorkingDirectory "frontend" -ArgumentList "-NoProfile", "-Command", "npm run dev" -PassThru

Write-Host "API pid: $($api.Id); Frontend pid: $($web.Id)" -ForegroundColor Green
Write-Host "Press Ctrl+C in each console to stop."

Wait-Process -Id $api.Id -ErrorAction SilentlyContinue
Wait-Process -Id $web.Id -ErrorAction SilentlyContinue
