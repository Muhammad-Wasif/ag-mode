"""Configuration management for AG Mode Manager.

Handles global settings, directory locations, workspace detection,
and active mode persistence.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_SETTINGS: Dict[str, Any] = {
    "startup_behavior": "interactive",  # 'interactive' | 'quiet' | 'last_active'
    "default_mode": None,              # mode id or None
    "theme": "matrix_green",           # 'matrix_green' | 'cyber_dark' | 'minimal'
    "scope": "workspace",              # 'workspace' | 'session' | 'global'
    "auto_backup": True,
    "sanitized_logging": True,
    "integration_enabled": True,
    "last_active_mode": None,
}


def get_base_dir() -> Path:
    """Return the base application directory ~/.ag-mode-manager."""
    home = Path.home()
    base = home / ".ag-mode-manager"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_config_path() -> Path:
    return get_base_dir() / "config.json"


def get_active_mode_path() -> Path:
    return get_base_dir() / "active_mode.json"


def get_backups_dir() -> Path:
    d = get_base_dir() / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_logs_dir() -> Path:
    d = get_base_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_custom_modes_dir() -> Path:
    d = get_base_dir() / "custom_modes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_builtin_modes_dir() -> Path:
    """Resolve directory containing built-in modes."""
    # First check relative to package / repo root
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parent.parent
    builtin = repo_root / "modes"
    if builtin.exists():
        return builtin
    # Fallback to base dir modes/ if installed
    installed_modes = get_base_dir() / "modes"
    installed_modes.mkdir(parents=True, exist_ok=True)
    return installed_modes


def find_workspace_root(start_path: Optional[Path] = None) -> Path:
    """Walk up from start_path to find repository or workspace root.

    Returns the directory containing .git, .agents, or fallback to start_path.
    """
    current = (start_path or Path.cwd()).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / ".agents").exists() or (parent / "GEMINI.md").exists():
            return parent
    return current


@dataclass
class AppConfig:
    startup_behavior: str = "interactive"
    default_mode: Optional[str] = None
    theme: str = "matrix_green"
    scope: str = "workspace"
    auto_backup: bool = True
    sanitized_logging: bool = True
    integration_enabled: bool = True
    last_active_mode: Optional[str] = None
    custom_paths: list[str] = field(default_factory=list)

    @classmethod
    def load(cls) -> AppConfig:
        config_path = get_config_path()
        if not config_path.exists():
            cfg = cls()
            cfg.save()
            return cfg
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(DEFAULT_SETTINGS)
            merged.update(data)
            return cls(
                startup_behavior=merged.get("startup_behavior", "interactive"),
                default_mode=merged.get("default_mode"),
                theme=merged.get("theme", "matrix_green"),
                scope=merged.get("scope", "workspace"),
                auto_backup=bool(merged.get("auto_backup", True)),
                sanitized_logging=bool(merged.get("sanitized_logging", True)),
                integration_enabled=bool(merged.get("integration_enabled", True)),
                last_active_mode=merged.get("last_active_mode"),
                custom_paths=list(merged.get("custom_paths", [])),
            )
        except Exception:
            # Fallback safely on corruption without crashing
            return cls()

    def save(self) -> None:
        config_path = get_config_path()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}", file=sys.stderr)


@dataclass
class ActiveModeState:
    mode_id: str
    mode_name: str
    activated_at: str
    workspace_path: str
    scope: str
    dependencies: list[str] = field(default_factory=list)
    composed_with: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, workspace_path: Optional[Path] = None) -> Optional[ActiveModeState]:
        # Check workspace first if workspace exists
        if workspace_path:
            ws_state = workspace_path / ".agents" / "ag_mode_state.json"
            if ws_state.exists():
                try:
                    with open(ws_state, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return cls(**data)
                except Exception:
                    pass

        # Fallback to global active mode state
        global_state = get_active_mode_path()
        if global_state.exists():
            try:
                with open(global_state, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except Exception:
                pass
        return None

    def save(self, workspace_path: Optional[Path] = None) -> None:
        data = asdict(self)
        # Save globally
        with open(get_active_mode_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Save to workspace if requested
        if workspace_path:
            agents_dir = workspace_path / ".agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            with open(agents_dir / "ag_mode_state.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    @classmethod
    def clear(cls, workspace_path: Optional[Path] = None) -> None:
        global_state = get_active_mode_path()
        if global_state.exists():
            try:
                global_state.unlink()
            except Exception:
                pass
        if workspace_path:
            ws_state = workspace_path / ".agents" / "ag_mode_state.json"
            if ws_state.exists():
                try:
                    ws_state.unlink()
                except Exception:
                    pass
