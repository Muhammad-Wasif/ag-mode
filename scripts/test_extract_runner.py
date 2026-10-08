import subprocess
import tempfile
import pathlib

test_bat = pathlib.Path(tempfile.gettempdir()) / "test_extract.bat"
content = r"""@echo off
set "INSTALL_DIR=%USERPROFILE%\.ag_test_dir"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo Running extraction...
powershell -NoProfile -Command "$marker = '::' + ' ---AG_PAYLOAD_BEGIN---'; $all = [IO.File]::ReadAllText('C:\Users\Admin\Desktop\ag-mode-manager\dist\AG-Mode-Manager-Setup.bat'); $idx = $all.IndexOf($marker); Write-Host ('Marker idx: ' + $idx); if ($idx -lt 0) { exit 1 }; $b64 = $all.Substring($idx + $marker.Length).Trim(); $bytes = [Convert]::FromBase64String($b64); $zip = [IO.Path]::Combine($env:TEMP, 'ag_test.zip'); [IO.File]::WriteAllBytes($zip, $bytes); Expand-Archive -Path $zip -DestinationPath '%INSTALL_DIR%' -Force; Remove-Item $zip -Force; Write-Host 'Extraction SUCCESS'"
echo Extraction finished with code: %ERRORLEVEL%
dir "%INSTALL_DIR%"
rmdir /s /q "%INSTALL_DIR%"
"""
test_bat.write_text(content, encoding="utf-8")
res = subprocess.run(["cmd.exe", "/c", str(test_bat)], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
