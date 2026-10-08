"""AntiGravity Environment Detector.

Detects whether AntiGravity is installed, what surfaces are available
(CLI, IDE, 2.0 Desktop, global config, workspace customization),
and identifies the safest supported integration mechanisms.
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ag_mode.config import find_workspace_root


@dataclass
class AntiGravityEnvironment:
    detected: bool
    version: Optional[str]
    has_cli: bool
    has_ide: bool
    has_app: bool
    has_global_config: bool
    cli_path: Optional[str]
    ide_path: Optional[str]
    global_config_path: Optional[str]
    workspace_root: Path
    has_workspace_agents: bool
    has_workspace_rules: bool
    has_workspace_gemini_md: bool
    supported_mechanisms: List[str] = field(default_factory=list)


def detect_antigravity(target_workspace: Optional[Path] = None) -> AntiGravityEnvironment:
    """Inspect system to detect AntiGravity installation and supported integration mechanisms."""
    home = Path.home()
    gemini_dir = home / ".gemini"

    # 1. Check CLI
    cli_cmd = shutil.which("agy") or shutil.which("antigravity")
    has_cli = bool(cli_cmd)
    cli_path = cli_cmd

    # 2. Check IDE
    ide_dir = gemini_dir / "antigravity-ide"
    has_ide = ide_dir.exists()
    ide_path = str(ide_dir) if has_ide else None

    # 3. Check App 2.0
    app_dir = gemini_dir / "antigravity"
    has_app = app_dir.exists()

    # 4. Check Global Config
    global_cfg = gemini_dir / "config"
    has_global_cfg = global_cfg.exists()
    global_cfg_path = str(global_cfg) if has_global_cfg else None

    # 5. Check Workspace
    ws_root = find_workspace_root(target_workspace)
    ws_agents = (ws_root / ".agents").exists()
    ws_rules = (ws_root / ".agents" / "rules").exists()
    ws_gemini_md = (ws_root / "GEMINI.md").exists() or (ws_root / "AGENTS.md").exists()

    # Overall detection flag
    detected = has_cli or has_ide or has_app or has_global_cfg or ws_agents

    # Determine supported mechanisms (in order of preference & safety)
    supported: List[str] = []
    if ws_root:
        supported.append("workspace_rules")        # .agents/rules/*.md (Safest, highest priority)
        supported.append("workspace_root_rules")   # GEMINI.md / AGENTS.md (Always loaded)
        supported.append("workspace_skills")       # .agents/skills/
        supported.append("workspace_hooks")        # .agents/hooks.json
    if has_cli:
        supported.append("cli_launcher")           # agy wrapper
    if has_global_cfg:
        supported.append("global_rules_ref")       # references in config

    version = None
    if has_ide:
        version = "AntiGravity IDE (detected)"
    elif has_app:
        version = "AntiGravity 2.0 (detected)"
    elif has_cli:
        version = "AntiGravity CLI (detected)"
    elif detected:
        version = "AntiGravity Environment"

    return AntiGravityEnvironment(
        detected=detected,
        version=version,
        has_cli=has_cli,
        has_ide=has_ide,
        has_app=has_app,
        has_global_config=has_global_cfg,
        cli_path=cli_path,
        ide_path=ide_path,
        global_config_path=global_cfg_path,
        workspace_root=ws_root,
        has_workspace_agents=ws_agents,
        has_workspace_rules=ws_rules,
        has_workspace_gemini_md=ws_gemini_md,
        supported_mechanisms=supported,
    )
