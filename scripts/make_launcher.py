"""Generator for launcher and installer files."""
import sys
from pathlib import Path

launcher_content = '''"""AntiGravity Smart Launcher.

Invoked before AntiGravity starts:
1. Shows currently active mode
2. Offers one-keystroke to keep mode or change mode in TUI
3. Automatically launches AntiGravity IDE
4. Stays active while AntiGravity is open, and automatically closes when AntiGravity exits.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from ag_mode.config import ActiveModeState, AppConfig, find_workspace_root
from ag_mode.tui.app import launch_tui


def find_antigravity_executable() -> Path | None:
    """Locate the real AntiGravity executable across standard install paths."""
    # 1. Check PATH
    agy = shutil.which("antigravity") or shutil.which("agy")
    if agy:
        return Path(agy)

    # 2. Windows standard locations
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("PROGRAMFILES", "")
        candidates = [
            Path(local_app_data) / "Programs" / "Antigravity IDE" / "Antigravity IDE.exe",
            Path(local_app_data) / "Programs" / "antigravity" / "Antigravity.exe",
            Path(prog_files) / "Antigravity IDE" / "Antigravity IDE.exe",
            Path(prog_files) / "antigravity" / "Antigravity.exe",
        ]
        for c in candidates:
            if c.exists():
                return c

        # Check Desktop shortcut
        desktop = Path.home() / "Desktop"
        for lnk_name in ["Antigravity IDE.lnk", "Antigravity.lnk"]:
            lnk_path = desktop / lnk_name
            if lnk_path.exists():
                try:
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    sc = shell.CreateShortcut(str(lnk_path))
                    target = Path(sc.TargetPath)
                    if target.exists() and "launch-antigravity" not in str(target).lower():
                        return target
                except Exception:
                    pass

    # 3. macOS standard locations
    elif sys.platform == "darwin":
        candidates = [
            Path("/Applications/Antigravity IDE.app/Contents/MacOS/Antigravity IDE"),
            Path("/Applications/Antigravity.app/Contents/MacOS/Antigravity"),
        ]
        for c in candidates:
            if c.exists():
                return c

    # 4. Linux standard locations
    else:
        candidates = [
            Path("/usr/bin/antigravity"),
            Path("/usr/local/bin/antigravity"),
            Path.home() / ".local" / "bin" / "antigravity",
        ]
        for c in candidates:
            if c.exists():
                return c

    return None


def is_antigravity_running() -> bool:
    """Check if AntiGravity IDE process is currently running on the system."""
    try:
        if sys.platform == "win32":
            output = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq Antigravity*"],
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return "antigravity" in output.lower()
        else:
            code = subprocess.call(["pgrep", "-f", "antigravity"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return code == 0
    except Exception:
        return False


def smart_launch() -> None:
    ws = find_workspace_root()
    state = ActiveModeState.load(ws)
    active_name = state.mode_name if state else "None (Default)"
    active_slug = state.mode_slug if state else "none"

    print("+==================================================================+")
    print("|                    ANTIGRAVITY MODE SELECTOR                     |")
    print("+==================================================================+")
    print(f"|  Active Mode: {active_name:<50} |")
    print(f"|  Identifier:  {active_slug:<50} |")
    print("+==================================================================+")
    print("|  [Enter] Start AntiGravity in this mode (Auto in 5s)             |")
    print("|  [C]     Change Mode (open full interactive selection menu)      |")
    print("|  [Q]     Quit                                                    |")
    print("+==================================================================+")
    print("")

    choice = ""
    try:
        if sys.platform == "win32":
            import msvcrt
            start_t = time.time()
            prompt_printed = False
            while time.time() - start_t < 5.0:
                remaining = int(5.0 - (time.time() - start_t))
                if not prompt_printed:
                    sys.stdout.write(f"\\rAuto-launching in {remaining}s... (Press [C] to change, [Enter] now) ")
                    sys.stdout.flush()
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    if ch in (b"\\r", b"\\n"):
                        choice = "ENTER"
                        break
                    elif ch in (b"c", b"C"):
                        choice = "C"
                        break
                    elif ch in (b"q", b"Q"):
                        choice = "Q"
                        break
                time.sleep(0.05)
            print("")
        else:
            import select
            print("Press [Enter] to continue or [C] to change mode (auto-launch in 5s)...")
            rlist, _, _ = select.select([sys.stdin], [], [], 5.0)
            if rlist:
                line = sys.stdin.readline().strip().lower()
                if line == "c":
                    choice = "C"
                elif line == "q":
                    choice = "Q"
                else:
                    choice = "ENTER"
    except Exception:
        pass

    if choice == "Q":
        print("Launch cancelled.")
        return

    if choice == "C":
        launch_tui(ws)
        # Reload state after TUI selection
        state = ActiveModeState.load(ws)
        if state:
            active_name = state.mode_name
            active_slug = state.mode_slug

    # Launch AntiGravity
    exe = find_antigravity_executable()
    if exe and exe.exists():
        print("")
        print(f"Starting AntiGravity IDE: {exe}")
        try:
            if sys.platform == "win32":
                proc = subprocess.Popen([str(exe)])
            else:
                proc = subprocess.Popen([str(exe)])

            print("")
            print("+==================================================================+")
            print(f"|  AntiGravity IDE is running (Mode: {active_name})")
            print("|  Rules synced to ~/.gemini/config/rules/ag_active_mode.md")
            print("|")
            print("|  This console window will close automatically when AntiGravity exits.")
            print("+==================================================================+")
            print("")

            # Initial brief grace period for process to spawn
            time.sleep(3.0)

            # Keep window open while AntiGravity is running
            while is_antigravity_running():
                time.sleep(2.0)

            print("AntiGravity has closed. Exiting AG Mode Manager.")
            time.sleep(0.5)

        except Exception as e:
            print(f"Error starting AntiGravity: {e}")
            input("Press Enter to exit...")
    else:
        print("")
        print("[NOTICE] AntiGravity executable not found at default location.")
        print(f"Mode [{active_name}] is active and saved globally.")
        print("Please launch AntiGravity manually.")
        input("Press Enter to exit...")


if __name__ == "__main__":
    smart_launch()
'''

target_dir = Path("C:/Users/Admin/Desktop/ag-mode-manager/src/ag_mode/cli")
target_dir.mkdir(parents=True, exist_ok=True)
with open(target_dir / "launcher.py", "w", encoding="utf-8") as f:
    f.write(launcher_content.strip() + "\n")
print("Successfully generated updated launcher.py")
