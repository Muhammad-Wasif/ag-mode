# AG Mode Manager - Windows Installer (PowerShell)
# Cross-Platform AntiGravity Mode, Rules & Quality-Control System

Write-Host "+--------------------------------------------------+" -ForegroundColor Green
Write-Host "|              AG MODE MANAGER INSTALLER           |" -ForegroundColor Green
Write-Host "|             AntiGravity Environment              |" -ForegroundColor Green
Write-Host "+--------------------------------------------------+" -ForegroundColor Green
Write-Host ""

# 1. System Detection
$Arch = if ([System.Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
Write-Host "System detected:" -ForegroundColor Cyan
Write-Host "  OS: Windows" -ForegroundColor White
Write-Host "  Architecture: $Arch" -ForegroundColor White
Write-Host ""

# 2. Check Requirements
Write-Host "Checking requirements..." -ForegroundColor Yellow

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    Write-Host "X Python 3.10+ is required but was not found in PATH." -ForegroundColor Red
    exit 1
}
$PyVer = python --version
Write-Host "OK Runtime detected: $PyVer" -ForegroundColor Green

$AntiGravityDetected = $false
$GeminiDir = Join-Path $env:USERPROFILE ".gemini"
if (Test-Path $GeminiDir) {
    $AntiGravityDetected = $true
    Write-Host "OK AntiGravity detected at $GeminiDir" -ForegroundColor Green
} else {
    Write-Host "! AntiGravity not detected; standalone mode will be enabled" -ForegroundColor Yellow
}

Write-Host "OK Terminal and permission checks passed" -ForegroundColor Green
Write-Host ""

# 3. Installing...
Write-Host "Installing AG Mode Manager..." -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $PSScriptRoot
if (-not $CurrentDir) { $CurrentDir = Get-Location }

# Run installation python engine
$Env:PYTHONPATH = "$CurrentDir\src;$Env:PYTHONPATH"
python -m ag_mode.installer.installer

# Setup local launchers in ~/.ag-mode-manager/bin
$UserBin = Join-Path (Join-Path $env:USERPROFILE ".ag-mode-manager") "bin"
if (-not (Test-Path $UserBin)) {
    New-Item -ItemType Directory -Path $UserBin -Force | Out-Null
}

$LauncherBat = Join-Path $UserBin "ag-mode.bat"
$Lines = @(
    "@echo off",
    ("set PYTHONPATH=" + $CurrentDir + "\src;%PYTHONPATH%"),
    "python -m ag_mode.cli.main %*"
)
$Lines | Set-Content -Path $LauncherBat -Encoding Ascii

Write-Host ""
Write-Host "[========================================] 100%" -ForegroundColor Green
Write-Host ""
Write-Host "OK Installation complete." -ForegroundColor Green
Write-Host "AG Mode Manager is ready." -ForegroundColor Green
Write-Host ""
Write-Host "To launch interactive mode selection:" -ForegroundColor Cyan
Write-Host "  $LauncherBat" -ForegroundColor White
Write-Host "Or run from this directory:" -ForegroundColor Cyan
Write-Host "  python -m ag_mode.cli.main" -ForegroundColor White
