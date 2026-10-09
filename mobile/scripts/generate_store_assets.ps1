# JISR Arabic (فهيم) — Store Graphic Asset Generator
# Generates official Google Play Store & Apple App Store graphic assets:
# 1. Google Play Store Icon (512x512 PNG, RGB)
# 2. Apple App Store Icon (1024x1024 PNG, RGB without alpha)
# 3. Google Play Feature Graphic (1024x500 PNG)

param(
    [string]$SourceLogoPath = "assets\logos\jisr-logo-3-512.png",
    [string]$OutputDir = "mobile\assets\store"
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

Write-Host "[JISR] Initializing Store Graphic Asset Generator..." -ForegroundColor Cyan

# Resolve paths
$repoRoot = (Get-Item -Path ".").FullName
$resolvedSourceLogo = Join-Path $repoRoot $SourceLogoPath
$resolvedOutputDir = Join-Path $repoRoot $OutputDir

if (-not (Test-Path $resolvedSourceLogo)) {
    # Fallback to mobile icon if logo not found
    $resolvedSourceLogo = Join-Path $repoRoot "mobile\assets\icon.png"
}

if (-not (Test-Path $resolvedSourceLogo)) {
    Write-Error "Source logo not found at $SourceLogoPath or mobile\assets\icon.png"
    exit 1
}

if (-not (Test-Path $resolvedOutputDir)) {
    New-Item -ItemType Directory -Path $resolvedOutputDir -Force | Out-Null
    Write-Host "Created directory: $resolvedOutputDir" -ForegroundColor Green
}

$srcImage = [System.Drawing.Image]::FromFile($resolvedSourceLogo)

try {
    # -------------------------------------------------------------
    # 1. Google Play Store Icon (512 x 512, 32-bit RGB)
    # -------------------------------------------------------------
    Write-Host "[1/3] Generating Google Play Store Icon (512x512)..." -ForegroundColor Yellow
    $playIconPath = Join-Path $resolvedOutputDir "icon_playstore_512.png"
    $bmpPlay = New-Object System.Drawing.Bitmap 512, 512, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $gPlay = [System.Drawing.Graphics]::FromImage($bmpPlay)
    $gPlay.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gPlay.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $gPlay.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    # Background: Brand dark slate/navy #0F172A
    $bgBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(15, 23, 42))
    $gPlay.FillRectangle($bgBrush, 0, 0, 512, 512)
    $bgBrush.Dispose()

    # Draw logo with 32px padding (safe zone)
    $padPlay = 32
    $logoSizePlay = 512 - ($padPlay * 2)
    $gPlay.DrawImage($srcImage, $padPlay, $padPlay, $logoSizePlay, $logoSizePlay)

    $bmpPlay.Save($playIconPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $gPlay.Dispose()
    $bmpPlay.Dispose()
    Write-Host "  Generated: $playIconPath" -ForegroundColor Green

    # -------------------------------------------------------------
    # 2. Apple App Store Icon (1024 x 1024, 24-bit RGB, No Alpha)
    # -------------------------------------------------------------
    Write-Host "[2/3] Generating Apple App Store Icon (1024x1024)..." -ForegroundColor Yellow
    $appStoreIconPath = Join-Path $resolvedOutputDir "icon_appstore_1024.png"
    $bmpApple = New-Object System.Drawing.Bitmap 1024, 1024, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $gApple = [System.Drawing.Graphics]::FromImage($bmpApple)
    $gApple.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gApple.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $gApple.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    # Background: Solid Deep Navy #0F172A
    $appleBgBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(15, 23, 42))
    $gApple.FillRectangle($appleBgBrush, 0, 0, 1024, 1024)
    $appleBgBrush.Dispose()

    # Subtle border accent
    $accentPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(5, 150, 105)), 4
    $gApple.DrawRectangle($accentPen, 16, 16, 992, 992)
    $accentPen.Dispose()

    # Draw centered logo scaled to 880x880 with 72px padding
    $padApple = 72
    $logoSizeApple = 1024 - ($padApple * 2)
    $gApple.DrawImage($srcImage, $padApple, $padApple, $logoSizeApple, $logoSizeApple)

    $bmpApple.Save($appStoreIconPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $gApple.Dispose()
    $bmpApple.Dispose()
    Write-Host "  Generated: $appStoreIconPath" -ForegroundColor Green

    # -------------------------------------------------------------
    # 3. Google Play Feature Graphic (1024 x 500, Landscape)
    # -------------------------------------------------------------
    Write-Host "[3/3] Generating Google Play Feature Graphic (1024x500)..." -ForegroundColor Yellow
    $featureGraphicPath = Join-Path $resolvedOutputDir "feature_graphic_1024x500.png"
    $bmpFeature = New-Object System.Drawing.Bitmap 1024, 500, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $gFeature = [System.Drawing.Graphics]::FromImage($bmpFeature)
    $gFeature.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gFeature.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $gFeature.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

    # Background Gradient (Deep Navy #0F172A to Slate #1E293B)
    $rectFeature = New-Object System.Drawing.Rectangle 0, 0, 1024, 500
    $gradBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        $rectFeature,
        [System.Drawing.Color]::FromArgb(15, 23, 42),
        [System.Drawing.Color]::FromArgb(30, 41, 59),
        [System.Drawing.Drawing2D.LinearGradientMode]::Horizontal
    )
    $gFeature.FillRectangle($gradBrush, $rectFeature)
    $gradBrush.Dispose()

    # Decorative Arch / Bridge accents (Emerald & Gold)
    $emeraldPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(5, 150, 105)), 3
    $goldPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(217, 119, 6)), 2
    $gFeature.DrawArc($emeraldPen, 40, -100, 600, 600, 45, 90)
    $gFeature.DrawArc($goldPen, 60, -80, 560, 560, 45, 90)
    $emeraldPen.Dispose()
    $goldPen.Dispose()

    # Left: Brand Logo (360 x 360, centered vertically at Y = 70, X = 50)
    $gFeature.DrawImage($srcImage, 50, 70, 360, 360)

    # Right: Marketing Titles and Typography
    $fontTitle = [System.Drawing.Font]::new("Segoe UI", [single]34.0, [System.Drawing.FontStyle]::Bold)
    $fontSubtitle = [System.Drawing.Font]::new("Segoe UI", [single]20.0, [System.Drawing.FontStyle]::Bold)
    $fontTagline = [System.Drawing.Font]::new("Segoe UI", [single]14.0, [System.Drawing.FontStyle]::Regular)
    $fontBadge = [System.Drawing.Font]::new("Segoe UI", [single]12.0, [System.Drawing.FontStyle]::Bold)

    $whiteBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 255, 255))
    $goldBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(245, 158, 11))
    $emeraldBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(16, 185, 129))
    $subBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(203, 213, 225))

    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Near

    # Main Titles
    $gFeature.DrawString("جسر | JISR", $fontTitle, $whiteBrush, 450, 80, $sf)
    $gFeature.DrawString("تعلم العربية مع فهيم", $fontSubtitle, $goldBrush, 452, 145, $sf)
    $gFeature.DrawString("Fahim: Your Smart Arabic AI Tutor", $fontTagline, $subBrush, 452, 190, $sf)

    # Feature Badges
    $badgeRect1 = New-Object System.Drawing.Rectangle 452, 245, 230, 40
    $badgeBg1 = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(20, 40, 60))
    $gFeature.FillRectangle($badgeBg1, $badgeRect1)
    $badgeBorder1 = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(5, 150, 105)), 1
    $gFeature.DrawRectangle($badgeBorder1, $badgeRect1)
    $gFeature.DrawString("منهاج دولة الإمارات", $fontBadge, $emeraldBrush, 464, 254, $sf)

    $badgeRect2 = New-Object System.Drawing.Rectangle 695, 245, 230, 40
    $gFeature.FillRectangle($badgeBg1, $badgeRect2)
    $gFeature.DrawRectangle($badgeBorder1, $badgeRect2)
    $gFeature.DrawString("معلم نطق صوتي ذكي", $fontBadge, $goldBrush, 715, 254, $sf)

    # Bottom Tagline
    $gFeature.DrawString("K-12 Student Mastery • Ad-Free • Safe & Secure", $fontBadge, $subBrush, 452, 320, $sf)

    # Cleanup GDI+ resources
    $fontTitle.Dispose()
    $fontSubtitle.Dispose()
    $fontTagline.Dispose()
    $fontBadge.Dispose()
    $whiteBrush.Dispose()
    $goldBrush.Dispose()
    $emeraldBrush.Dispose()
    $subBrush.Dispose()
    $badgeBg1.Dispose()
    $badgeBorder1.Dispose()
    $sf.Dispose()

    $bmpFeature.Save($featureGraphicPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $gFeature.Dispose()
    $bmpFeature.Dispose()
    Write-Host "  Generated: $featureGraphicPath" -ForegroundColor Green

    Write-Host "[JISR] All store graphic assets successfully generated in: $resolvedOutputDir" -ForegroundColor Green

} finally {
    $srcImage.Dispose()
}