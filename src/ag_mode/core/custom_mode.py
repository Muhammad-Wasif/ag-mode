"""Custom Mode Creator.

Allows users to create, configure, list, and delete their own custom modes.
Generates directory structure with README.md, core.md, tools.md, workflow.md, quality-gate.md,
and mode.json manifest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from ag_mode.config import get_custom_modes_dir
from ag_mode.core.registry import ModeMetadata, mode_registry
from ag_mode.diagnostics.logger import logger


def slugify(text: str) -> str:
    """Convert mode name to a safe URL/filesystem slug."""
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", s)


class CustomModeManager:
    """Manages creation and lifecycle of custom modes."""

    def __init__(self, custom_dir: Optional[Path] = None):
        self.custom_dir = custom_dir or get_custom_modes_dir()
        self.custom_dir.mkdir(parents=True, exist_ok=True)

    def create_mode(
        self,
        name: str,
        description: str,
        category: str = "General",
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        quality_gates: Optional[List[str]] = None,
        custom_files: Optional[Dict[str, str]] = None,
    ) -> ModeMetadata:
        """Create a new custom mode directory with standard template files and manifest."""
        mode_id = slugify(name)
        mode_path = self.custom_dir / mode_id
        mode_path.mkdir(parents=True, exist_ok=True)

        deps = dependencies or []
        tgs = tags or [slugify(name)]
        gates = quality_gates or [
            "Project requirements documented",
            "Code adheres to custom mode quality standards",
            "Tests executed successfully",
        ]

        files_dict = {
            "README.md": f"# {name}\n\n{description}\n\n*Custom mode created with AG Mode Manager.*",
            "core.md": f"# {name} Core Workflow & Directives\n\n1. Define project scope and core requirements.\n2. Adhere to domain standards.\n3. Verify all outputs before delivery.",
            "tools.md": f"# {name} Recommended Tools & SDKs\n\n- Primary toolchains and SDKs for {name}.",
            "workflow.md": f"# {name} Execution Workflow\n\nPhase 1: Planning\nPhase 2: Execution\nPhase 3: Verification\nPhase 4: Review",
            "quality-gate.md": f"# {name} Quality Gate\n\n" + "\n".join([f"- [ ] {g}" for g in gates]),
        }
        if custom_files:
            files_dict.update(custom_files)

        for fname, content in files_dict.items():
            with open(mode_path / fname, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")

        manifest = {
            "id": mode_id,
            "name": name,
            "category": category,
            "description": description,
            "version": "1.0.0",
            "dependencies": deps,
            "tags": tgs,
            "files": list(files_dict.keys()),
            "quality_gates": gates,
            "security_profile": {"custom": "Standard safe execution policy"},
            "is_custom": True,
        }

        with open(mode_path / "mode.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Refresh central registry
        mode_registry.load_all()

        logger.success("integration", f"Created custom mode '{name}' (id: {mode_id})", {"path": str(mode_path)})
        return mode_registry.get(mode_id) or ModeMetadata(**manifest, directory=str(mode_path))

    def list_custom_modes(self) -> List[ModeMetadata]:
        return [m for m in mode_registry.modes.values() if m.is_custom]

    def delete_custom_mode(self, mode_id: str) -> bool:
        mode_path = self.custom_dir / mode_id
        if mode_path.exists() and mode_path.is_dir():
            import shutil
            try:
                shutil.rmtree(mode_path)
                mode_registry.load_all()
                logger.info("integration", f"Deleted custom mode {mode_id}")
                return True
            except Exception as e:
                logger.error("error", f"Failed deleting custom mode {mode_id}: {e}")
                return False
        return False


custom_mode_manager = CustomModeManager()
