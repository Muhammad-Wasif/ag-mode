"""Distribution packager for AG Mode Manager.

Builds standalone, self-extracting single-file installers:
1. Windows:
   - dist/installer-ag-mode-2.1.3-windows.bat (Double-clickable standalone batch file with embedded payload)
   - dist/installer-ag-mode-2.1.3-windows.ps1 (Standalone PowerShell script with embedded payload)
2. macOS:
   - dist/installer-ag-mode-2.1.3-macos.sh (Terminal shell script with embedded payload)
   - dist/installer-ag-mode-2.1.3-macos.command (Double-clickable Finder command)
3. Linux:
   - dist/installer-ag-mode-2.1.3-linux.sh (Self-extracting bash installer)
   - dist/installer-ag-mode-2.1.3-linux.tar.gz (Portable tarball with install.sh)
"""

from __future__ import annotations

import base64
import io
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
DIST_DIR = REPO_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)


def build_zip_in_memory() -> bytes:
    """Create a zip of the ag-mode-manager package in memory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add src/
        for p in (REPO_ROOT / "src").rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                arcname = p.relative_to(REPO_ROOT)
                zf.write(p, arcname)

        # Add modes/
        for p in (REPO_ROOT / "modes").rglob("*"):
            if p.is_file():
                arcname = p.relative_to(REPO_ROOT)
                zf.write(p, arcname)

        # Add docs/
        for p in (REPO_ROOT / "docs").rglob("*"):
            if p.is_file():
                arcname = p.relative_to(REPO_ROOT)
                zf.write(p, arcname)

        # Add README.md, setup.py
        for fname in ["README.md", "setup.py"]:
            fpath = REPO_ROOT / fname
            if fpath.exists():
                zf.write(fpath, fname)

    return buf.getvalue()


def build_windows_setup_bat(zip_bytes: bytes) -> None:
    b64_data = base64.b64encode(zip_bytes).decode("ascii")
    b64_lines = [b64_data[i:i+76] for i in range(0, len(b64_data), 76)]

    bat_path = DIST_DIR / "installer-ag-mode-2.1.3-windows.bat"
    
    script_header = """@echo off
setlocal enabledelayedexpansion
title AG Mode Manager Setup - AntiGravity
color 0A

echo +==================================================================+
echo   AG MODE MANAGER INSTALLER - AntiGravity Environment Setup        
echo +==================================================================+
echo.
echo Installing AG Mode Manager for AntiGravity...
echo.

:: 2. Prepare destination in %USERPROFILE%\\.ag-mode-manager
set "INSTALL_DIR=%USERPROFILE%\\.ag-mode-manager"
set "BIN_DIR=%INSTALL_DIR%\\bin"
set "PYTHON_DIR=%INSTALL_DIR%\\python"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

:: 1. Check Python
set "PYTHON_EXE=python"
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Python 3 not found globally. Attempting to download local Python runtime...
    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Write-Host 'Downloading Python...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%TEMP%\\py.zip' -UseBasicParsing; Write-Host 'Extracting...'; Expand-Archive -Path '%TEMP%\\py.zip' -DestinationPath '%PYTHON_DIR%' -Force; Remove-Item '%TEMP%\\py.zip' -Force; Write-Host 'Python downloaded.' } catch { Write-Host '[ERROR] Internet issue or download failed: ' $_.Exception.Message; exit 1 }"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Installation failed due to internet or download issue.
        pause
        exit /b 1
    )
    :: Un-comment the import site line in python311._pth so pip works
    powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content '%PYTHON_DIR%\\python311._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\\python311._pth'"
    
    :: Download get-pip.py
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\\get-pip.py' -UseBasicParsing } catch { exit 1 }"
    "%PYTHON_DIR%\\python.exe" "%PYTHON_DIR%\\get-pip.py" --no-warn-script-location >nul 2>nul
    
    set "PYTHON_EXE=%PYTHON_DIR%\\python.exe"
)

echo [1/5] Extracting embedded application files...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$marker = '::' + ' ' + '---AG_PAYLOAD_BEGIN---'; $all = [IO.File]::ReadAllText('%~f0'); $idx = $all.IndexOf($marker); if ($idx -lt 0) { exit 1 }; $b64 = $all.Substring($idx + $marker.Length).Trim(); $bytes = [Convert]::FromBase64String($b64); $zip = [IO.Path]::Combine($env:TEMP, 'ag_setup.zip'); [IO.File]::WriteAllBytes($zip, $bytes); Expand-Archive -Path $zip -DestinationPath '%INSTALL_DIR%' -Force; Remove-Item $zip -Force"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to extract application archive.
    pause
    exit /b 1
)

echo [2/5] Installing terminal UI dependencies (rich, prompt_toolkit)...
"%PYTHON_EXE%" -m pip install --quiet --disable-pip-version-check rich prompt_toolkit >nul 2>nul

echo [3/5] Generating launcher scripts...
set "LAUNCH_BAT=%BIN_DIR%\\launch-antigravity.bat"
(
echo @echo off
echo set "PYTHONPATH=%INSTALL_DIR%\\src;%%PYTHONPATH%%"
echo "%PYTHON_EXE%" -m ag_mode.cli.launcher %%*
) > "%LAUNCH_BAT%"

(
echo @echo off
echo set "PYTHONPATH=%INSTALL_DIR%\\src;%%PYTHONPATH%%"
echo "%PYTHON_EXE%" -m ag_mode.cli.main %%*
) > "%BIN_DIR%\\ag-mode.bat"

(
echo @echo off
echo "%BIN_DIR%\\ag-mode.bat" %%*
) > "%BIN_DIR%\\ag.bat"

del /q "%BIN_DIR%\\*.ps1" 2>nul

echo [4/5] Adding AG Mode Manager to permanent user PATH...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$bin = '%BIN_DIR%'; $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($userPath -notlike '*' + $bin + '*') { [Environment]::SetEnvironmentVariable('Path', $userPath + ';' + $bin, 'User'); Write-Host '  OK PATH updated' }"

echo [5/5] Creating Desktop and AntiGravity integration shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$sh = New-Object -ComObject WScript.Shell; $d = [Environment]::GetFolderPath('Desktop'); $sc = $sh.CreateShortcut($d + '\\AntiGravity (with AG Mode).lnk'); $sc.TargetPath = '%LAUNCH_BAT%'; $sc.Description = 'Launch AntiGravity with Mode Selector'; $agIco = (Get-ChildItem -Path $env:LOCALAPPDATA -Filter 'Antigravity IDE.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName; if ($agIco) { $sc.IconLocation = $agIco }; $sc.Save(); Write-Host '  OK Desktop shortcut created: AntiGravity (with AG Mode).lnk'"

:: Initialize configuration and default modes
set "PYTHONPATH=%INSTALL_DIR%\\src;%PYTHONPATH%"
"%PYTHON_EXE%" -m ag_mode.installer.installer >nul 2>nul

echo.
echo +==================================================================+
echo   INSTALLATION COMPLETE!
echo +==================================================================+
echo.
echo AG Mode Manager is now permanently installed on your system!
echo Location: %INSTALL_DIR%
echo.
echo Features configured:
echo   - Desktop shortcut 'AntiGravity (with AG Mode)' created.
echo   - CLI commands 'ag' and 'ag-mode' added to PATH globally.
echo   - Active mode selector will open automatically when launching AntiGravity!
echo.
pause
exit /b 0

:: ---AG_PAYLOAD_BEGIN---
"""

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(script_header)
        for line in b64_lines:
            f.write(line + "\n")

    print(f"Built Windows batch installer: {bat_path} ({bat_path.stat().st_size // 1024} KB)")


def build_windows_setup_ps1(zip_bytes: bytes) -> None:
    b64_data = base64.b64encode(zip_bytes).decode("ascii")
    b64_lines = [b64_data[i:i+76] for i in range(0, len(b64_data), 76)]

    ps1_path = DIST_DIR / "installer-ag-mode-2.1.3-windows.ps1"
    
    header = """# AG Mode Manager Setup - PowerShell Edition
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "+==================================================================+" -ForegroundColor Green
Write-Host "  AG MODE MANAGER INSTALLER - AntiGravity Windows PowerShell Setup   " -ForegroundColor Green
Write-Host "+==================================================================+" -ForegroundColor Green
Write-Host ""

# Check Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[ERROR] Python 3.10+ was not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ or Microsoft Store."
    pause
    exit 1
}

$installDir = Join-Path $env:USERPROFILE ".ag-mode-manager"
$binDir = Join-Path $installDir "bin"
New-Item -ItemType Directory -Path $installDir, $binDir -Force | Out-Null

Write-Host "[1/5] Extracting embedded application files..." -ForegroundColor Cyan
$zipPath = Join-Path $env:TEMP "ag_setup_$([System.IO.Path]::GetRandomFileName()).zip"

$b64 = @"
"""

    footer = """"@

$bytes = [Convert]::FromBase64String($b64.Trim())
[IO.File]::WriteAllBytes($zipPath, $bytes)
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath -Force

Write-Host "[2/5] Installing terminal UI dependencies (rich, prompt_toolkit)..." -ForegroundColor Cyan
& python -m pip install --quiet --disable-pip-version-check rich prompt_toolkit 2>$null

Write-Host "[3/5] Generating launcher scripts..." -ForegroundColor Cyan
$launchBat = Join-Path $binDir "launch-antigravity.bat"
@"
@echo off
set "PYTHONPATH=$installDir\\src;%PYTHONPATH%"
python -m ag_mode.cli.launcher %*
"@ | Set-Content -Path $launchBat -Encoding ASCII

@"
@echo off
set "PYTHONPATH=$installDir\\src;%PYTHONPATH%"
python -m ag_mode.cli.main %*
"@ | Set-Content -Path (Join-Path $binDir "ag-mode.bat") -Encoding ASCII

@"
@echo off
"$binDir\\ag-mode.bat" %*
"@ | Set-Content -Path (Join-Path $binDir "ag.bat") -Encoding ASCII

Write-Host "[4/5] Adding AG Mode Manager to permanent user PATH..." -ForegroundColor Cyan
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$binDir", 'User')
    Write-Host "  OK User PATH updated" -ForegroundColor Green
}

Write-Host "[5/5] Creating Desktop shortcut..." -ForegroundColor Cyan
$sh = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$sc = $sh.CreateShortcut((Join-Path $desktop "AntiGravity (with AG Mode).lnk"))
$sc.TargetPath = $launchBat
$sc.Description = "Launch AntiGravity with Mode Selector"
$agIco = (Get-ChildItem -Path $env:LOCALAPPDATA -Filter "Antigravity IDE.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
if ($agIco) { $sc.IconLocation = $agIco }
$sc.Save()
Write-Host "  OK Desktop shortcut created: AntiGravity (with AG Mode).lnk" -ForegroundColor Green

# Initialize
$env:PYTHONPATH = "$installDir\\src;$env:PYTHONPATH"
& python -m ag_mode.installer.installer 2>$null

Write-Host ""
Write-Host "+==================================================================+" -ForegroundColor Green
Write-Host "  INSTALLATION COMPLETE!                                            " -ForegroundColor Green
Write-Host "+==================================================================+" -ForegroundColor Green
Write-Host "Location: $installDir"
Write-Host "Commands 'ag' and 'ag-mode' are ready to use in any terminal."
Write-Host "Desktop shortcut 'AntiGravity (with AG Mode)' is ready."
Write-Host ""
"""

    with open(ps1_path, "w", encoding="utf-8") as f:
        f.write(header)
        for line in b64_lines:
            f.write(line + "\n")
        f.write(footer)

    print(f"Built Windows PowerShell installer: {ps1_path} ({ps1_path.stat().st_size // 1024} KB)")


def build_linux_setup_sh(zip_bytes: bytes) -> None:
    b64_data = base64.b64encode(zip_bytes).decode("ascii")
    b64_lines = [b64_data[i:i+76] for i in range(0, len(b64_data), 76)]

    sh_path = DIST_DIR / "installer-ag-mode-2.1.3-linux.sh"

    script = """#!/usr/bin/env bash
# AG Mode Manager - Standalone Linux Installer
set -e

GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
NC='\\033[0m'

echo -e "${GREEN}+==================================================================+${NC}"
echo -e "${GREEN}  AG MODE MANAGER INSTALLER - AntiGravity Linux Environment         ${NC}"
echo -e "${GREEN}+==================================================================+${NC}"
echo ""

INSTALL_DIR="$HOME/.ag-mode-manager"
BIN_DIR="$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

if command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
else
    echo "Python 3 is required. Please install Python 3."
    exit 1
fi

echo -e "${CYAN}[1/4] Extracting embedded application files...${NC}"
TEMP_ZIP=$(mktemp /tmp/ag_bundle_XXXXXX.zip)
sed -e '1,/^#__PAYLOAD_START__$/d' "$0" | base64 -d > "$TEMP_ZIP"
unzip -q -o "$TEMP_ZIP" -d "$INSTALL_DIR"
rm -f "$TEMP_ZIP"

echo -e "${CYAN}[2/4] Installing dependencies (rich, prompt_toolkit)...${NC}"
$PY -m pip install --quiet --user rich prompt_toolkit 2>/dev/null || true

echo -e "${CYAN}[3/4] Creating launcher executables...${NC}"
cat << 'EOF' > "$BIN_DIR/ag-mode"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
exec python3 -m ag_mode.cli.main "$@"
EOF
chmod +x "$BIN_DIR/ag-mode"
ln -sf "$BIN_DIR/ag-mode" "$BIN_DIR/ag"

cat << 'EOF' > "$BIN_DIR/launch-antigravity"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
python3 -m ag_mode.cli.launcher "$@"
EOF
chmod +x "$BIN_DIR/launch-antigravity"

echo -e "${CYAN}[4/4] Configuring shell PATH...${NC}"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q ".ag-mode-manager/bin" "$rc"; then
        echo 'export PATH="$HOME/.ag-mode-manager/bin:$PATH"' >> "$rc"
    fi
done

# Desktop Entry on Linux
DESKTOP_DIR="$HOME/.local/share/applications"
if [ -d "$DESKTOP_DIR" ]; then
    cat << EOF > "$DESKTOP_DIR/antigravity-ag-mode.desktop"
[Desktop Entry]
Name=AntiGravity (with AG Mode)
Comment=Launch AntiGravity with AG Mode Selector
Exec=$BIN_DIR/launch-antigravity
Terminal=true
Type=Application
Categories=Development;IDE;
EOF
    chmod +x "$DESKTOP_DIR/antigravity-ag-mode.desktop"
fi

export PYTHONPATH="$INSTALL_DIR/src:$PYTHONPATH"
$PY -m ag_mode.installer.installer >/dev/null 2>&1 || true

echo ""
echo -e "${GREEN}+==================================================================+${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE!                                            ${NC}"
echo -e "${GREEN}+==================================================================+${NC}"
echo ""
echo "How to use:"
echo "  1. Run 'launch-antigravity' to select a mode and start AntiGravity."
echo "  2. Run 'ag' or 'ag-mode' in terminal anytime to change modes."
echo ""
exit 0
#__PAYLOAD_START__
"""

    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(script)
        for line in b64_lines:
            f.write(line + "\n")

    print(f"Built Linux shell installer: {sh_path} ({sh_path.stat().st_size // 1024} KB)")


def build_linux_tarball() -> None:
    tar_path = DIST_DIR / "installer-ag-mode-2.1.3-linux.tar.gz"
    install_script = """#!/usr/bin/env bash
set -e
INSTALL_DIR="$HOME/.ag-mode-manager"
BIN_DIR="$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/modes" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/docs" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

cat << 'EOF' > "$BIN_DIR/ag-mode"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
exec python3 -m ag_mode.cli.main "$@"
EOF
chmod +x "$BIN_DIR/ag-mode"
ln -sf "$BIN_DIR/ag-mode" "$BIN_DIR/ag"

cat << 'EOF' > "$BIN_DIR/launch-antigravity"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
python3 -m ag_mode.cli.launcher "$@"
EOF
chmod +x "$BIN_DIR/launch-antigravity"

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q ".ag-mode-manager/bin" "$rc"; then
        echo 'export PATH="$HOME/.ag-mode-manager/bin:$PATH"' >> "$rc"
    fi
done

python3 -m pip install --quiet --user rich prompt_toolkit 2>/dev/null || true
export PYTHONPATH="$INSTALL_DIR/src:$PYTHONPATH"
python3 -m ag_mode.installer.installer >/dev/null 2>&1 || true

echo "AG Mode Manager installed successfully to $INSTALL_DIR!"
echo "Commands 'ag' and 'launch-antigravity' are available in PATH."
"""

    with tarfile.open(tar_path, "w:gz") as tar:
        for p in (REPO_ROOT / "src").rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                tar.add(p, arcname=str(p.relative_to(REPO_ROOT)))
        for p in (REPO_ROOT / "modes").rglob("*"):
            if p.is_file():
                tar.add(p, arcname=str(p.relative_to(REPO_ROOT)))
        for p in (REPO_ROOT / "docs").rglob("*"):
            if p.is_file():
                tar.add(p, arcname=str(p.relative_to(REPO_ROOT)))
        for fname in ["README.md", "setup.py"]:
            fpath = REPO_ROOT / fname
            if fpath.exists():
                tar.add(fpath, arcname=fname)

        # Add install.sh
        ti = tarfile.TarInfo(name="install.sh")
        ti_bytes = install_script.encode("utf-8")
        ti.size = len(ti_bytes)
        ti.mode = 0o755
        tar.addfile(ti, io.BytesIO(ti_bytes))

    print(f"Built Linux portable tarball: {tar_path} ({tar_path.stat().st_size // 1024} KB)")


def build_macos_setup_sh(zip_bytes: bytes) -> None:
    b64_data = base64.b64encode(zip_bytes).decode("ascii")
    b64_lines = [b64_data[i:i+76] for i in range(0, len(b64_data), 76)]

    sh_path = DIST_DIR / "installer-ag-mode-2.1.3-macos.sh"

    script = """#!/usr/bin/env bash
# AG Mode Manager - Standalone macOS Installer
set -e

GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
NC='\\033[0m'

echo -e "${GREEN}+==================================================================+${NC}"
echo -e "${GREEN}  AG MODE MANAGER INSTALLER - AntiGravity macOS Environment         ${NC}"
echo -e "${GREEN}+==================================================================+${NC}"
echo ""

INSTALL_DIR="$HOME/.ag-mode-manager"
BIN_DIR="$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

if command -v python3 >/dev/null 2>&1; then
    PY="python3"
else
    echo "Python 3 is required. Please install Python 3."
    exit 1
fi

echo -e "${CYAN}[1/4] Extracting embedded application files...${NC}"
TEMP_ZIP=$(mktemp /tmp/ag_bundle_XXXXXX.zip)
sed -e '1,/^#__PAYLOAD_START__$/d' "$0" | base64 -D > "$TEMP_ZIP" 2>/dev/null || sed -e '1,/^#__PAYLOAD_START__$/d' "$0" | base64 -d > "$TEMP_ZIP"
unzip -q -o "$TEMP_ZIP" -d "$INSTALL_DIR"
rm -f "$TEMP_ZIP"

echo -e "${CYAN}[2/4] Installing dependencies (rich, prompt_toolkit)...${NC}"
$PY -m pip install --quiet --user rich prompt_toolkit 2>/dev/null || true

echo -e "${CYAN}[3/4] Creating launcher executables...${NC}"
cat << 'EOF' > "$BIN_DIR/ag-mode"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
exec python3 -m ag_mode.cli.main "$@"
EOF
chmod +x "$BIN_DIR/ag-mode"
ln -sf "$BIN_DIR/ag-mode" "$BIN_DIR/ag"

cat << 'EOF' > "$BIN_DIR/launch-antigravity"
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.ag-mode-manager/src:$PYTHONPATH"
python3 -m ag_mode.cli.launcher "$@"
EOF
chmod +x "$BIN_DIR/launch-antigravity"

# Desktop shortcut on macOS
DESKTOP_COMMAND="$HOME/Desktop/AntiGravity (with AG Mode).command"
cat << EOF > "$DESKTOP_COMMAND"
#!/usr/bin/env bash
"$BIN_DIR/launch-antigravity"
EOF
chmod +x "$DESKTOP_COMMAND"

echo -e "${CYAN}[4/4] Configuring shell PATH...${NC}"
for rc in "$HOME/.zprofile" "$HOME/.zshrc" "$HOME/.bash_profile"; do
    if [ -f "$rc" ] && ! grep -q ".ag-mode-manager/bin" "$rc"; then
        echo 'export PATH="$HOME/.ag-mode-manager/bin:$PATH"' >> "$rc"
    fi
done

export PYTHONPATH="$INSTALL_DIR/src:$PYTHONPATH"
$PY -m ag_mode.installer.installer >/dev/null 2>&1 || true

echo ""
echo -e "${GREEN}+==================================================================+${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE!                                            ${NC}"
echo -e "${GREEN}+==================================================================+${NC}"
echo ""
echo "How to use:"
echo "  1. Double-click 'AntiGravity (with AG Mode).command' on your Desktop."
echo "  2. Or run 'ag' or 'ag-mode' in Terminal anytime to change modes."
echo ""
exit 0
#__PAYLOAD_START__
"""

    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(script)
        for line in b64_lines:
            f.write(line + "\n")

    print(f"Built macOS shell installer: {sh_path} ({sh_path.stat().st_size // 1024} KB)")

    # Also build the double-clickable .command file version for macOS Finder
    cmd_path = DIST_DIR / "installer-ag-mode-2.1.3-macos.command"
    shutil.copy(sh_path, cmd_path)
    print(f"Built macOS Finder .command installer: {cmd_path} ({cmd_path.stat().st_size // 1024} KB)")


def main():
    print("Building compressed in-memory archive...")
    zip_bytes = build_zip_in_memory()
    print(f"Archive size: {len(zip_bytes) // 1024} KB")

    # 2 for Windows: .bat and .ps1
    build_windows_setup_bat(zip_bytes)
    build_windows_setup_ps1(zip_bytes)

    # 2 for Linux: .sh and .tar.gz
    build_linux_setup_sh(zip_bytes)
    build_linux_tarball()

    # 2 for macOS: .sh and .command
    build_macos_setup_sh(zip_bytes)

    print("\nAll standalone single-file installers built successfully in dist/:")
    for f in DIST_DIR.iterdir():
        print(f"  - {f.name:<38} ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
