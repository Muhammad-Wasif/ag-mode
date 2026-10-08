"""Mode Composer for multi-mode activation.

Allows activating combinations (e.g. WEB + CYBERSECURITY, DATA SCIENCE + MACHINE LEARNING),
merging compatible rules, and detecting conflicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ag_mode.core.registry import ModeMetadata, ModeRegistry, mode_registry
from ag_mode.core.resolver import DependencyResolver
from ag_mode.diagnostics.logger import logger


@dataclass
class CompositionConflict:
    category: str
    description: str
    conflicting_modes: List[str]
    suggested_resolution: str


@dataclass
class ComposedMode:
    primary_mode_id: str
    all_mode_ids: List[str]
    combined_name: str
    resolved_modes: List[ModeMetadata]
    merged_quality_gates: List[str]
    merged_security_profile: Dict[str, str]
    conflicts: List[CompositionConflict] = field(default_factory=list)


class ModeComposer:
    """Composes multiple modes into a unified execution profile."""

    def __init__(self, registry: ModeRegistry = mode_registry):
        self.registry = registry
        self.resolver = DependencyResolver(registry)

    def compose(self, mode_ids: List[str]) -> ComposedMode:
        if not mode_ids:
            raise ValueError("At least one mode ID must be provided.")

        primary_id = mode_ids[0]
        all_resolved: List[ModeMetadata] = []
        seen_ids: Set[str] = set()

        for mid in mode_ids:
            resolved_chain = self.resolver.resolve(mid)
            for m in resolved_chain:
                if m.id not in seen_ids:
                    seen_ids.add(m.id)
                    all_resolved.append(m)

        names = [self.registry.get(m).name if self.registry.get(m) else m for m in mode_ids]
        combined_name = " + ".join(names)

        # Merge quality gates
        merged_gates: List[str] = []
        for m in all_resolved:
            for g in m.quality_gates:
                if g not in merged_gates:
                    merged_gates.append(g)

        # Merge security profiles
        merged_sec: Dict[str, str] = {}
        conflicts: List[CompositionConflict] = []

        for m in all_resolved:
            for k, v in m.security_profile.items():
                if k in merged_sec and merged_sec[k] != v:
                    # Potential conflict
                    conflicts.append(CompositionConflict(
                        category=k,
                        description=f"Mode {m.name} defines {k}='{v}', but earlier mode defined '{merged_sec[k]}'.",
                        conflicting_modes=[primary_id, m.id],
                        suggested_resolution=f"Defaulting to strictest policy ('{v}').",
                    ))
                    # Strictest policy usually takes precedence in security
                    merged_sec[k] = f"{merged_sec[k]} ; {v}"
                else:
                    merged_sec[k] = v

        logger.info("integration", f"Composed modes: {combined_name}", {"modes": mode_ids, "resolved_count": len(all_resolved)})

        return ComposedMode(
            primary_mode_id=primary_id,
            all_mode_ids=mode_ids,
            combined_name=combined_name,
            resolved_modes=all_resolved,
            merged_quality_gates=merged_gates,
            merged_security_profile=merged_sec,
            conflicts=conflicts,
        )
