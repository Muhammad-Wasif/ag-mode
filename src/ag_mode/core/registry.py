"""Dynamic Mode Registry and Metadata.

Loads built-in and custom modes, provides dynamic numbering, category indexing,
and multi-attribute searching.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ag_mode.config import get_builtin_modes_dir, get_custom_modes_dir
from ag_mode.diagnostics.logger import logger


CATEGORIES: List[str] = [
    "Web Development",
    "Mobile Development",
    "Desktop Development",
    "Cloud & DevOps",
    "Systems & Hardware",
    "Software Engineering",
    "Data & AI",
    "Cybersecurity",
    "Academic & Study",
    "Languages & Writing",
    "Research",
    "General",
]


@dataclass
class ModeMetadata:
    id: str
    name: str
    category: str
    description: str
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    security_profile: Dict[str, str] = field(default_factory=dict)
    is_custom: bool = False
    directory: Optional[str] = None

    def get_file_path(self, rel_filename: str) -> Optional[Path]:
        if not self.directory:
            return None
        p = Path(self.directory) / rel_filename
        return p if p.exists() else None

    def load_file_content(self, rel_filename: str) -> str:
        p = self.get_file_path(rel_filename)
        if not p or not p.is_file():
            return ""
        try:
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error("error", f"Failed to read mode file {p}: {e}")
            return ""


class ModeRegistry:
    """Central registry for discovering, numbering, and searching modes."""

    def __init__(self, builtin_dir: Optional[Path] = None, custom_dir: Optional[Path] = None):
        self.builtin_dir = builtin_dir or get_builtin_modes_dir()
        self.custom_dir = custom_dir or get_custom_modes_dir()
        self.modes: Dict[str, ModeMetadata] = {}
        self.load_all()

    def load_all(self) -> None:
        """Discover and load all built-in and custom modes."""
        self.modes.clear()

        # 1. Load registry index (modes.json) if available
        index_file = self.builtin_dir / "modes.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data.get("modes", []):
                    mode_dir = self.builtin_dir / item.get("directory", item["id"])
                    item["directory"] = str(mode_dir)
                    item["is_custom"] = False
                    mode = ModeMetadata(**item)
                    self.modes[mode.id] = mode
            except Exception as e:
                logger.error("error", f"Error parsing modes.json: {e}")

        # 2. Discover built-in directory subfolders
        if self.builtin_dir.exists():
            for folder in self.builtin_dir.iterdir():
                if folder.is_dir() and folder.name not in self.modes:
                    self._load_mode_from_dir(folder, is_custom=False)

        # 3. Discover custom mode subfolders
        if self.custom_dir.exists():
            for folder in self.custom_dir.iterdir():
                if folder.is_dir():
                    self._load_mode_from_dir(folder, is_custom=True)

    def _load_mode_from_dir(self, folder: Path, is_custom: bool) -> None:
        manifest_file = folder / "mode.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["id"] = data.get("id", folder.name)
                data["directory"] = str(folder)
                data["is_custom"] = is_custom
                mode = ModeMetadata(**data)
                self.modes[mode.id] = mode
                return
            except Exception as e:
                logger.error("error", f"Failed to load mode from {folder}: {e}")

        # Infer mode if no mode.json
        name = folder.name.replace("-", " ").title()
        md_files = [f.name for f in folder.glob("*.md")]
        mode = ModeMetadata(
            id=folder.name,
            name=name,
            category="Development" if not is_custom else "General",
            description=f"Mode for {name}",
            directory=str(folder),
            files=md_files,
            is_custom=is_custom,
        )
        self.modes[mode.id] = mode

    def get(self, mode_id: str) -> Optional[ModeMetadata]:
        return self.modes.get(mode_id)

    def get_by_category(self, category: str) -> List[ModeMetadata]:
        return [m for m in self.modes.values() if m.category.lower() == category.lower()]

    def get_categories(self) -> List[str]:
        # Return standard categories first, plus any custom categories
        cats = list(CATEGORIES)
        for m in self.modes.values():
            if m.category not in cats:
                cats.append(m.category)
        return cats

    def get_numbered_modes(self, category: Optional[str] = None) -> List[Tuple[int, ModeMetadata]]:
        """Dynamically assign sequential numbers 1..N based on current list."""
        if category:
            modes = self.get_by_category(category)
        else:
            modes = list(self.modes.values())
        return list(enumerate(modes, start=1))

    def search(self, query: str, category: Optional[str] = None) -> List[ModeMetadata]:
        """Search modes by name, description, tags, and category."""
        q = query.strip().lower()
        if not q:
            return self.get_by_category(category) if category else list(self.modes.values())

        words = q.split()
        results = []

        pool = self.get_by_category(category) if category else list(self.modes.values())
        for mode in pool:
            searchable_text = f"{mode.name} {mode.id} {mode.category} {mode.description} {' '.join(mode.tags)}".lower()
            if all(word in searchable_text for word in words):
                results.append(mode)

        return results


# Global singleton instance
mode_registry = ModeRegistry()
