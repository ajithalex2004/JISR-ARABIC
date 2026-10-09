<#
.SYNOPSIS
    Automated Release Packaging Script for JISR Arabic (فهيم) Mobile App.
.DESCRIPTION
    Validates mobile environment, enforces HTTPS endpoint pinning (https://api.jisr.ae),
    runs test suites, and packages production Android (.aab / .apk) and iOS artifacts.
.PARAMETER Target
    Build target: 'appbundle' (Google Play .aab), 'apk' (Direct .apk), 'ios' (Xcode/IPA), or 'all'.
.PARAMETER ApiBase
    Production API base URL (Must begin with https://). Defaults to 'https://api.jisr.ae'.
.PARAMETER Clean
    If specified, runs 'flutter clean' before building.
.PARAMETER Obfuscate
    If specified, enables Dart code obfuscation and symbol splitting.
#>
param (
    [ValidateSet('appbundle', 'apk', 'ios', 'all')]
    [string]$Target = 'appbundle',

    [string]$ApiBase = 'https://api.jisr.ae',

    [switch]$Clean,

    [switch]$Obfuscate = $true
)

$ErrorActionPreference = 'Stop'

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  JISR Arabic Mobile Release Packaging Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Enforce HTTPS Endpoint Pinning
if (-not $ApiBase.StartsWith("https://")) {
    Write-Error "SECURITY ERROR: Release builds must use strict HTTPS. Received: '$ApiBase'"
    exit 1
}
Write-Host "[1/6] Production API Base: $ApiBase" -ForegroundColor Green

# 2. Check Flutter Tooling
$flutterCmd = Get-Command flutter -ErrorAction SilentlyContinue
if (-not $flutterCmd) {
    Write-Error "ERROR: 'flutter' command not found on PATH. Please ensure Flutter SDK is installed."
    exit 1
}
Write-Host "[2/6] Flutter Tooling detected: $($flutterCmd.Source)" -ForegroundColor Green

# 3. Android Keystore Verification
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mobileDir = Resolve-Path (Join-Path $scriptDir "..")
$keyPropertiesPath = Join-Path $mobileDir "android\key.properties"

if (Test-Path $keyPropertiesPath) {
    Write-Host "[3/6] Android signing: 'key.properties' verified for release signing." -ForegroundColor Green
} else {
    Write-Host "[3/6] WARNING: 'android/key.properties' not found. Android build will use debug signing fallback." -ForegroundColor Yellow
    Write-Host "      To configure official production signing, copy 'key.properties.example' to 'key.properties'." -ForegroundColor DarkYellow
}

# 4. Clean & Fetch Dependencies
Push-Location $mobileDir
try {
    if ($Clean) {
        Write-Host "[4/6] Running 'flutter clean'..." -ForegroundColor Cyan
        flutter clean
    }

    Write-Host "[4/6] Resolving Flutter dependencies..." -ForegroundColor Cyan
    flutter pub get

    Write-Host "[4/6] Running static analysis..." -ForegroundColor Cyan
    flutter analyze
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Static analysis reported issues. Build aborted."
        exit $LASTEXITCODE
    }

    Write-Host "[4/6] Running mobile unit tests..." -ForegroundColor Cyan
    flutter test
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Unit tests failed. Build aborted."
        exit $LASTEXITCODE
    }

    # 5. Build Artifacts
    $symbolsDir = "build/app/outputs/symbols"
    $obfuscateArgs = @()
    if ($Obfuscate) {
        if (-not (Test-Path $symbolsDir)) {
            New-Item -ItemType Directory -Path $symbolsDir -Force | Out-Null
        }
        $obfuscateArgs = @("--obfuscate", "--split-debug-info=$symbolsDir")
    }

    $dartDefines = @("--dart-define=FAHIM_API_BASE=$ApiBase")

    if ($Target -eq 'appbundle' -or $Target -eq 'all') {
        Write-Host "`n[5/6] Building Android App Bundle (.aab) for Google Play..." -ForegroundColor Cyan
        $buildArgs = @("build", "appbundle", "--release") + $dartDefines + $obfuscateArgs
        Write-Host "Executing: flutter $($buildArgs -join ' ')" -ForegroundColor DarkGray
        & flutter @buildArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $aabPath = "build/app/outputs/bundle/release/app-release.aab"
        if (Test-Path $aabPath) {
            $item = Get-Item $aabPath
            $hash = (Get-FileHash -Path $aabPath -Algorithm SHA256).Hash
            Write-Host "`n[SUCCESS] Google Play Bundle: $aabPath" -ForegroundColor Green
            Write-Host "          Size: $([math]::Round($item.Length / 1MB, 2)) MB" -ForegroundColor Green
            Write-Host "          SHA-256: $hash" -ForegroundColor DarkGray
        }
    }

    if ($Target -eq 'apk' -or $Target -eq 'all') {
        Write-Host "`n[5/6] Building Android APK (.apk) for Direct Distribution..." -ForegroundColor Cyan
        $buildArgs = @("build", "apk", "--release") + $dartDefines + $obfuscateArgs
        Write-Host "Executing: flutter $($buildArgs -join ' ')" -ForegroundColor DarkGray
        & flutter @buildArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

        $apkPath = "build/app/outputs/flutter-apk/app-release.apk"
        if (Test-Path $apkPath) {
            $item = Get-Item $apkPath
            $hash = (Get-FileHash -Path $apkPath -Algorithm SHA256).Hash
            Write-Host "`n[SUCCESS] Release APK: $apkPath" -ForegroundColor Green
            Write-Host "          Size: $([math]::Round($item.Length / 1MB, 2)) MB" -ForegroundColor Green
            Write-Host "          SHA-256: $hash" -ForegroundColor DarkGray
        }
    }

    if ($Target -eq 'ios' -or $Target -eq 'all') {
        if ($IsMacOS -or $env:OS -eq $null) {
            Write-Host "`n[5/6] Building iOS Archive (.ipa) for App Store..." -ForegroundColor Cyan
            $buildArgs = @("build", "ipa", "--release") + $dartDefines + $obfuscateArgs
            Write-Host "Executing: flutter $($buildArgs -join ' ')" -ForegroundColor DarkGray
            & flutter @buildArgs
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            Write-Host "[SUCCESS] iOS build completed successfully." -ForegroundColor Green
        } else {
            Write-Host "`n[NOTE] iOS builds must be run on macOS with Xcode installed. Skipped on Windows." -ForegroundColor Yellow
        }
    }

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "  Mobile Release Packaging Completed Successfully!" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
}
finally {
    Pop-Location
}
