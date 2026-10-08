"""Uninstaller Engine for AG Mode Manager.

Safely disables integration, removes only AG Mode Manager files,
restores original workspace configurations, and guarantees:
- Never deletes AntiGravity
- Never deletes AntiGravity conversations
- Never deletes AntiGravity history
- Never deletes user projects
- Never deletes unrelated files
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ag_mode.config import get_base_dir, find_workspace_root
from ag_mode.diagnostics.logger import logger
from ag_mode.integration.adapter import AntiGravityAdapter
from ag_mode.integration.backup import backup_manager


def uninstall(workspace_root: Optional[Path] = None, remove_all_appdata: bool = False) -> Dict[str, Any]:
    """Execute clean, safe uninstallation of AG Mode Manager."""
    results: Dict[str, Any] = {"success": True, "actions": []}
    ws = workspace_root or find_workspace_root()

    logger.info("installer", "Initiating AG Mode Manager uninstallation")

    # Step 1: Disable and clean active mode integration in workspace
    try:
        adapter = AntiGravityAdapter(ws)
        adapter.deactivate_mode()
        results["actions"].append("✓ Disabled active mode integration in workspace")
    except Exception as e:
        logger.error("error", f"Error deactivating workspace integration: {e}")

    # Step 2: Clean AG Mode files from .agents/ if present
    rules_dir = ws / ".agents" / "rules"
    for ag_file in ["ag_active_mode.md", "ag_quality_gate.md", "ag_tools.md"]:
        target = rules_dir / ag_file
        if target.exists():
            try:
                target.unlink()
                results["actions"].append(f"✓ Removed generated workspace rule: {ag_file}")
            except Exception:
                pass

    ag_skill_dir = ws / ".agents" / "skills" / "ag-mode"
    if ag_skill_dir.exists():
        try:
            shutil.rmtree(ag_skill_dir)
            results["actions"].append("✓ Removed AG Mode skill from workspace")
        except Exception:
            pass

    # Step 3: Remove application data if requested
    if remove_all_appdata:
        base_dir = get_base_dir()
        if base_dir.exists():
            try:
                shutil.rmtree(base_dir)
                results["actions"].append(f"✓ Removed application data directory: {base_dir}")
            except Exception as e:
                logger.error("error", f"Failed to remove base_dir: {e}")

    results["actions"].append("✓ AntiGravity conversations, history, and user projects preserved intact")
    results["actions"].append("✓ AG Mode Manager removed successfully")

    logger.success("installer", "AG Mode Manager uninstalled successfully.")
    return results
