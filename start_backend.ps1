# Fahim Backend Startup Script
$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
if (-not $projectRoot) { $projectRoot = "C:\JISR ARABIC" }

$userSite = "C:\Users\athom\AppData\Roaming\Python\Python313\site-packages"
$env:PYTHONPATH = "$userSite;$projectRoot"

Write-Host "===================================================" -ForegroundColor Green
Write-Host "  Fahim (فهيم) - Arabic Learning Platform Backend" -ForegroundColor Green
Write-Host "  Starting API on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Green

$userPython = "C:\Users\athom\AppData\Local\Programs\Python\Python313\python.exe"
if (Test-Path $userPython) {
    & $userPython -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
}
