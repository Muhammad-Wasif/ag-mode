"""Dependency Resolver for AG Mode Manager.

Resolves dependency hierarchies (e.g. Full-Stack -> Frontend, Backend, DB, Security)
with topological sort, cycle detection, and deduplication.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from ag_mode.core.registry import ModeMetadata, ModeRegistry, mode_registry
from ag_mode.diagnostics.logger import logger


class DependencyResolver:
    """Resolves mode dependencies without duplicates or circular lockups."""

    def __init__(self, registry: ModeRegistry = mode_registry):
        self.registry = registry

    def resolve(self, mode_id: str) -> List[ModeMetadata]:
        """Resolve all dependencies for a mode in execution order.

        Returns list of ModeMetadata where dependencies come before the root mode.
        """
        resolved: List[ModeMetadata] = []
        visited: Set[str] = set()
        visiting: Set[str] = set()

        def dfs(curr_id: str) -> None:
            if curr_id in visiting:
                logger.warning("integration", f"Circular dependency detected involving mode: {curr_id}")
                return
            if curr_id in visited:
                return

            visiting.add(curr_id)
            mode = self.registry.get(curr_id)
            if mode:
                for dep_id in mode.dependencies:
                    dfs(dep_id)
                visited.add(curr_id)
                visiting.remove(curr_id)
                resolved.append(mode)
            else:
                visiting.remove(curr_id)
                logger.warning("integration", f"Dependency mode not found: {curr_id}")

        dfs(mode_id)
        return resolved

    def collect_all_files(self, modes: List[ModeMetadata]) -> List[Tuple[ModeMetadata, str]]:
        """Collect all files across a resolved list of modes, deduplicating identical files."""
        collected: List[Tuple[ModeMetadata, str]] = []
        seen_keys: Set[str] = set()

        for m in modes:
            for f in m.files:
                # Deduplication key combines file name and mode
                key = f"{m.id}:{f}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    collected.append((m, f))

        return collected
