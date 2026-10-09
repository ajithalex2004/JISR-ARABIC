<#
.SYNOPSIS
    JISR Arabic Production Container Deployment Script (PowerShell / Windows)
#>
[CmdletBinding()]
param (
    [switch]$BuildOnly,
    [switch]$Down
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$item = Get-Item $RootDir
if ($item.LinkType -eq "Junction" -and $item.Target) {
    $RootDir = $item.Target[0]
}

Set-Location $RootDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ">> JISR Arabic: Production Container Deployment Starting..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if ($Down) {
    Write-Host ">> Stopping and removing production containers..." -ForegroundColor Yellow
    docker compose -f docker-compose.prod.yml down
    exit 0
}

# 1. Environment file check
if (-not (Test-Path ".env.production")) {
    if (Test-Path "backend\.env") {
        Write-Host ">> Copying credentials from backend/.env to .env.production..." -ForegroundColor Yellow
        Copy-Item "backend\.env" ".env.production"
    } else {
        Write-Error "Missing .env.production file. Copy .env.production.example and populate configuration."
        exit 1
    }
}

# 2. Validate Compose configuration
Write-Host ">> Validating Docker Compose configuration..." -ForegroundColor Green
docker compose -f docker-compose.prod.yml config --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Invalid docker-compose.prod.yml configuration."
    exit 1
}

# 3. Build container images
Write-Host ">> Building production container images..." -ForegroundColor Green
docker compose -f docker-compose.prod.yml --env-file .env.production build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Container build failed."
    exit 1
}

if ($BuildOnly) {
    Write-Host ">> Build completed successfully (-BuildOnly specified)." -ForegroundColor Green
    exit 0
}

# 4. Launch services in detached mode
Write-Host ">> Launching production services (api, worker, redis, web)..." -ForegroundColor Green
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --remove-orphans

# 5. Wait for health check
Write-Host ">> Waiting for services to reach healthy state..." -ForegroundColor Green
$timeout = 60
$elapsed = 0
$healthy = $false

while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 3
    $elapsed += 3
    $status = docker compose -f docker-compose.prod.yml ps api --format "{{.Status}}"
    if ($status -match "healthy") {
        $healthy = $true
        break
    }
    Write-Host "   ... waiting for API healthcheck ($elapsed/$timeout s): $status"
}

if (-not $healthy) {
    Write-Warning "API container did not report healthy status within $timeout seconds."
    docker compose -f docker-compose.prod.yml logs --tail 30 api
} else {
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ">> JISR Arabic Production Deployment Complete!" -ForegroundColor Green
    Write-Host ">> Web Gateway:  http://localhost" -ForegroundColor White
    Write-Host ">> API Health:   http://localhost/api/health" -ForegroundColor White
    Write-Host ">> Readiness:    http://localhost/api/ready" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Cyan
}
