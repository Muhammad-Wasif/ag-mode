"""Repair Engine for AG Mode Manager.

Validates application integrity, configuration schemas, mode registry,
restores damaged files, and repairs AntiGravity workspace integration.
Never repairs by blindly deleting the entire installation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ag_mode.config import get_base_dir, get_builtin_modes_dir, get_config_path, AppConfig, find_workspace_root
from ag_mode.core.registry import mode_registry
from ag_mode.diagnostics.logger import logger
from ag_mode.integration.adapter import AntiGravityAdapter
from ag_mode.integration.detector import detect_antigravity


def repair(workspace_root: Optional[Path] = None) -> Dict[str, Any]:
    """Execute non-destructive repair and health audit."""
    results: Dict[str, Any] = {
        "success": True,
        "actions": [],
        "warnings": [],
        "errors": [],
    }
    base_dir = get_base_dir()

    logger.info("diagnostics", "Starting repair procedure")

    # 1. Check directories
    required_dirs = [base_dir, base_dir / "backups", base_dir / "logs", base_dir / "custom_modes", base_dir / "bin"]
    for d in required_dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            results["actions"].append(f"✓ Restored missing directory: {d.name}")

    # 2. Validate & Repair config.json
    cfg_path = get_config_path()
    if not cfg_path.exists():
        cfg = AppConfig()
        cfg.save()
        results["actions"].append("✓ Rebuilt missing config.json with defaults")
    else:
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                json.load(f)
            results["actions"].append("✓ config.json syntax verified")
        except Exception:
            # Corrupted json: create backup and regenerate valid config
            corrupt_backup = cfg_path.with_suffix(".corrupt.bak")
            cfg_path.replace(corrupt_backup)
            cfg = AppConfig()
            cfg.save()
            results["actions"].append(f"✓ Repaired corrupted config.json (archived original to {corrupt_backup.name})")

    # 3. Validate Mode Registry
    mode_registry.load_all()
    count = len(mode_registry.modes)
    if count == 0:
        results["warnings"].append("Mode registry was empty; triggering library regeneration")
        from ag_mode.core.seed_library import generate_library
        generate_library(get_builtin_modes_dir())
        mode_registry.load_all()
        results["actions"].append(f"✓ Regenerated mode library ({len(mode_registry.modes)} modes restored)")
    else:
        results["actions"].append(f"✓ Mode registry validated ({count} modes available)")

    # 4. Validate AntiGravity Integration
    ws = workspace_root or find_workspace_root()
    env = detect_antigravity(ws)
    if env.detected:
        results["actions"].append(f"✓ AntiGravity environment detected ({env.version})")
    else:
        results["warnings"].append("AntiGravity environment not currently detected")

    # 5. Check workspace state consistency
    state_file = ws / ".agents" / "ag_mode_state.json"
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            mid = data.get("mode_id")
            if mid and mid not in mode_registry.modes:
                results["warnings"].append(f"Active mode '{mid}' in workspace not found in registry")
            else:
                results["actions"].append(f"✓ Workspace active mode '{mid}' verified")
        except Exception:
            results["warnings"].append("Workspace ag_mode_state.json corrupted; refreshing adapter")
            adapter = AntiGravityAdapter(ws)
            adapter.deactivate_mode()

    logger.success("diagnostics", "Repair procedure completed successfully", {"actions": results["actions"]})
    return results
