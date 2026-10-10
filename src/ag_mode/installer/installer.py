"""Installer Engine for AG Mode Manager.

Handles cross-platform setup, environment detection, binary launcher generation,
and idempotent initialization.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

from ag_mode.config import get_base_dir, get_builtin_modes_dir, get_config_path, AppConfig
from ag_mode.diagnostics.logger import logger
from ag_mode.integration.detector import detect_antigravity
from ag_mode.platform.detector import detect_platform


def install(verbose: bool = True) -> Dict[str, Any]:
    """Execute idempotent installation of AG Mode Manager."""
    results: Dict[str, Any] = {"success": False, "messages": []}

    platform_info = detect_platform()
    antigravity_env = detect_antigravity()
    base_dir = get_base_dir()

    logger.info("installer", "Starting AG Mode Manager installation", {
        "os": platform_info.display_os,
        "arch": platform_info.arch,
        "antigravity_detected": antigravity_env.detected,
    })

    # Step 1: Initialize directories
    dirs_to_create = [
        base_dir,
        base_dir / "backups",
        base_dir / "logs",
        base_dir / "custom_modes",
        base_dir / "bin",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
    results["messages"].append(f"✓ Base directories created in {base_dir}")

    # Step 2: Initialize default configuration
    cfg = AppConfig.load()
    cfg.save()
    results["messages"].append("✓ Configuration initialized")

    # Step 3: Copy or link default mode library to base directory if needed
    dest_modes = base_dir / "modes"
    builtin_modes = get_builtin_modes_dir()
    if builtin_modes.exists() and builtin_modes.resolve() != dest_modes.resolve():
        if not dest_modes.exists():
            shutil.copytree(builtin_modes, dest_modes, dirs_exist_ok=True)
            results["messages"].append("✓ Built-in mode library deployed to application data")

    # Step 4: Generate launcher scripts in ~/.ag-mode-manager/bin
    bin_dir = base_dir / "bin"
    python_exe = sys.executable

    # Windows batch launcher
    bat_file = bin_dir / "ag-mode.bat"
    bat_content = f"""@echo off
"{python_exe}" -m ag_mode.cli.main %*
"""
    with open(bat_file, "w", encoding="utf-8") as f:
        f.write(bat_content)



    # Unix shell launcher
    sh_file = bin_dir / "ag-mode"
    sh_content = f"""#!/usr/bin/env sh
exec "{python_exe}" -m ag_mode.cli.main "$@"
"""
    with open(sh_file, "w", encoding="utf-8") as f:
        f.write(sh_content)
    try:
        sh_file.chmod(0o755)
    except Exception:
        pass

    results["messages"].append(f"✓ Command-line launchers generated in {bin_dir}")

    # Step 5: Verify AntiGravity
    if antigravity_env.detected:
        results["messages"].append(f"✓ AntiGravity detected ({antigravity_env.version})")
        results["messages"].append(f"✓ Integration mechanisms: {', '.join(antigravity_env.supported_mechanisms)}")
    else:
        results["messages"].append("! AntiGravity was not detected on this system.")
        results["messages"].append("  AG Mode Manager installed independently; integration activates when AntiGravity is run.")

    results["success"] = True
    logger.success("installer", "AG Mode Manager installed successfully.")
    return results


if __name__ == "__main__":
    res = install()
    for m in res["messages"]:
        print(m)
