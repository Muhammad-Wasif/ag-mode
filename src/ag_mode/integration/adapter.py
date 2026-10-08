"""AntiGravity Integration Adapter.

Safely connects active mode knowledge, rules, quality gates, tools,
and skills into AntiGravity workspaces using officially supported
hierarchical rules (.agents/rules/*.md, GEMINI.md) and skills (.agents/skills/).
"""

from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from ag_mode.config import ActiveModeState, AppConfig, find_workspace_root
from ag_mode.core.composer import ComposedMode, ModeComposer
from ag_mode.core.context import inspect_workspace
from ag_mode.core.registry import ModeMetadata, mode_registry
from ag_mode.core.resolver import DependencyResolver
from ag_mode.diagnostics.logger import logger
from ag_mode.integration.backup import backup_manager
from ag_mode.integration.detector import detect_antigravity



def _build_mode_announcement(composed) -> str:
    """Build a rich mode announcement that AntiGravity reads at the start of each conversation."""
    try:
        mode_list = ', '.join(m.name for m in composed.resolved_modes)
    except Exception:
        mode_list = str(composed)
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        '# ============================================================',
        f'# ACTIVE MODE: {composed.combined_name.upper()}',
        '# ============================================================',
        '#',
        '# MANDATORY CONVERSATION OPENER:',
        '# At the start of EVERY new conversation, you MUST say:',
        f'#   "I am operating in [{composed.combined_name}] mode.',
        f'#    All my responses follow {composed.combined_name} standards."',
        '#',
        f'# Mode activated: {now}',
        f'# Mode components: {mode_list}',
        '# ============================================================',
        '',
    ]
    return '\n'.join(lines)


class AntiGravityAdapter:
    """Safe, non-destructive AntiGravity integration adapter."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or find_workspace_root()
        self.detector = detect_antigravity(self.workspace_root)
        self.resolver = DependencyResolver(mode_registry)
        self.composer = ModeComposer(mode_registry)

    def activate_mode(
        self,
        mode_id: str,
        composed_with: Optional[List[str]] = None,
        scope: str = "workspace",
    ) -> Dict[str, Any]:
        """Activate a mode or composition of modes within the workspace.

        Returns status dict with step-by-step verification results.
        """
        results: Dict[str, Any] = {
            "success": False,
            "steps": [],
            "mode_name": "",
            "warnings": [],
        }

        # Step 1: Validate mode
        primary_mode = mode_registry.get(mode_id)
        if not primary_mode:
            results["error"] = f"Mode '{mode_id}' not found in registry."
            logger.error("activation", results["error"])
            return results

        results["mode_name"] = primary_mode.name
        results["steps"].append("✓ Mode found")

        # Step 2: Resolve dependencies and composition
        try:
            mode_ids = [mode_id] + (composed_with or [])
            composed: ComposedMode = self.composer.compose(mode_ids)
            results["steps"].append("✓ Dependencies resolved")
        except Exception as e:
            results["error"] = f"Failed resolving mode dependencies: {e}"
            logger.error("activation", results["error"])
            return results

        # Step 3: Inspect existing workspace
        inspection = inspect_workspace(self.workspace_root)
        results["steps"].append(f"✓ Workspace inspected: {inspection.summary}")

        # Step 4: Backup existing configuration
        paths_to_backup = [
            self.workspace_root / ".agents" / "rules" / "ag_active_mode.md",
            self.workspace_root / ".agents" / "rules" / "ag_quality_gate.md",
            self.workspace_root / ".agents" / "rules" / "ag_tools.md",
            self.workspace_root / ".agents" / "ag_mode_state.json",
            self.workspace_root / "GEMINI.md",
        ]
        snapshot_id = backup_manager.create_snapshot(
            paths_to_backup,
            reason=f"Activating mode {composed.combined_name}",
        )
        results["steps"].append(f"✓ Reversible backup created (snapshot: {snapshot_id})")

        # Step 5: Generate Active Mode Instructions Content
        try:
            mode_content = self._build_mode_instructions(composed, inspection)
            quality_gate_content = self._build_quality_gate_instructions(composed)
            tools_content = self._build_tools_instructions(composed)
            root_gemini_content = self._build_gemini_md(composed)

            results["steps"].append("✓ Rules and UI/UX knowledge compiled")
            results["steps"].append("✓ Security rules and quality gates compiled")
        except Exception as e:
            results["error"] = f"Failed compiling mode files: {e}"
            logger.error("activation", results["error"])
            backup_manager.rollback(snapshot_id)
            return results

        # Step 6: Connect instructions to AntiGravity workspace
        try:
            agents_dir = self.workspace_root / ".agents"
            rules_dir = agents_dir / "rules"
            skills_dir = agents_dir / "skills" / "ag-mode"
            rules_dir.mkdir(parents=True, exist_ok=True)
            skills_dir.mkdir(parents=True, exist_ok=True)

            # 1. Write active mode rule
            with open(rules_dir / "ag_active_mode.md", "w", encoding="utf-8") as f:
                f.write(mode_content)

            # 2. Write quality gate rule
            with open(rules_dir / "ag_quality_gate.md", "w", encoding="utf-8") as f:
                f.write(quality_gate_content)

            # 3. Write tools rule
            with open(rules_dir / "ag_tools.md", "w", encoding="utf-8") as f:
                f.write(tools_content)

            # 4. Write interactive skill (SKILL.md)
            skill_content = self._build_skill_md(composed)
            with open(skills_dir / "SKILL.md", "w", encoding="utf-8") as f:
                f.write(skill_content)

            # 5. Write or update GEMINI.md at root
            self._update_gemini_md(root_gemini_content)

            # ALWAYS write to global ~/.gemini/config/rules/ so AntiGravity
            # picks up the mode regardless of whether a workspace is open.
            global_rules = Path.home() / '.gemini' / 'config' / 'rules'
            global_rules.mkdir(parents=True, exist_ok=True)
            # Build a rich conversation announcement banner
            announcement = _build_mode_announcement(composed)
            with open(global_rules / 'ag_active_mode.md', 'w', encoding='utf-8') as gf:
                gf.write(announcement + '\n\n' + mode_content)
            with open(global_rules / 'ag_quality_gate.md', 'w', encoding='utf-8') as gf:
                gf.write(quality_gate_content)
            with open(global_rules / 'ag_tools.md', 'w', encoding='utf-8') as gf:
                gf.write(tools_content)
            results['steps'].append('[OK] Global AntiGravity rules updated: ~/.gemini/config/rules/')
            results['steps'].append('[OK] Mode announcement written - AntiGravity will announce mode at conversation start')
            if scope == 'global':
                results['steps'].append('[OK] Scope: Global (applies to ALL AntiGravity sessions)')

            # 6. Save active mode state
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            state = ActiveModeState(
                mode_id=mode_id,
                mode_name=composed.combined_name,
                activated_at=now_iso,
                workspace_path=str(self.workspace_root.resolve()),
                scope=scope,
                dependencies=[m.id for m in composed.resolved_modes if m.id != mode_id],
                composed_with=composed_with or [],
            )
            state.save(self.workspace_root if scope == "workspace" else None)

            # Update app config
            cfg = AppConfig.load()
            cfg.last_active_mode = mode_id
            cfg.save()

            results["steps"].append("✓ AntiGravity integration connected")
            results["steps"].append(f"✓ Mode activated: {composed.combined_name}")
            results["success"] = True
            logger.success("activation", f"Mode {composed.combined_name} activated successfully in {self.workspace_root}")

        except Exception as e:
            results["error"] = f"Failed applying integration files: {e}"
            logger.error("error", results["error"])
            backup_manager.rollback(snapshot_id)
            results["steps"].append("✕ Activation failed. Rollback executed.")
            return results

        return results

    def deactivate_mode(self) -> bool:
        """Safely clear active mode from workspace and restore previous configuration."""
        paths_to_backup = [
            self.workspace_root / ".agents" / "rules" / "ag_active_mode.md",
            self.workspace_root / ".agents" / "rules" / "ag_quality_gate.md",
            self.workspace_root / ".agents" / "rules" / "ag_tools.md",
            self.workspace_root / ".agents" / "ag_mode_state.json",
            self.workspace_root / "GEMINI.md",
        ]
        backup_manager.create_snapshot(paths_to_backup, reason="Deactivating active mode")

        # Safely remove AG Mode generated files
        files_to_remove = [
            self.workspace_root / ".agents" / "rules" / "ag_active_mode.md",
            self.workspace_root / ".agents" / "rules" / "ag_quality_gate.md",
            self.workspace_root / ".agents" / "rules" / "ag_tools.md",
            self.workspace_root / ".agents" / "ag_mode_state.json",
        ]
        for f in files_to_remove:
            if f.exists():
                try:
                    f.unlink()
                except Exception as e:
                    logger.error("error", f"Failed to delete {f}: {e}")

        # Clean GEMINI.md marker
        gemini_file = self.workspace_root / "GEMINI.md"
        if gemini_file.exists():
            try:
                with open(gemini_file, "r", encoding="utf-8") as f:
                    content = f.read()
                marker_start = "<!-- AG_MODE_MANAGER_START -->"
                marker_end = "<!-- AG_MODE_MANAGER_END -->"
                if marker_start in content and marker_end in content:
                    idx1 = content.find(marker_start)
                    idx2 = content.find(marker_end) + len(marker_end)
                    cleaned = content[:idx1].strip() + "\n\n" + content[idx2:].strip()
                    cleaned = cleaned.strip()
                    if cleaned:
                        with open(gemini_file, "w", encoding="utf-8") as f:
                            f.write(cleaned + "\n")
                    else:
                        gemini_file.unlink()
            except Exception as e:
                logger.error("error", f"Failed cleaning GEMINI.md: {e}")

        # Clean global rules if present
        global_rules = Path.home() / '.gemini' / 'config' / 'rules'
        for gf in ['ag_active_mode.md', 'ag_quality_gate.md', 'ag_tools.md']:
            gp = global_rules / gf
            if gp.exists():
                try:
                    gp.unlink()
                except Exception:
                    pass
        ActiveModeState.clear(self.workspace_root)
        logger.info("integration", "Deactivated active mode and cleared workspace integration.")
        return True

    def _build_mode_instructions(self, composed: ComposedMode, inspection: Any) -> str:
        """Aggregate and structure instructions across all resolved modes."""
        lines = [
            f"# AG MODE: {composed.combined_name.upper()}",
            f"> Activated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Scope: Workspace",
            "",
            "## Operating Persona & Mandate",
            f"You are operating under **{composed.combined_name}**.",
            "Operate with the depth, discipline, architectural rigor, and quality standards of an elite engineering team.",
            "",
            "## Workspace Context",
            f"- Project state: {inspection.summary}",
            f"- Languages detected: {', '.join(inspection.languages) if inspection.languages else 'None yet'}",
            f"- Frameworks detected: {', '.join(inspection.frameworks) if inspection.frameworks else 'None yet'}",
            "",
            "---",
            "",
        ]

        # Gather file contents from resolved modes
        for mode in composed.resolved_modes:
            lines.append(f"## {mode.name} Standards")
            lines.append(f"*{mode.description}*")
            lines.append("")

            # Load each markdown file from the mode
            for fname in mode.files:
                if fname in ("quality-gate.md", "tools.md"):
                    continue  # handled in separate rules files for cleaner organization
                content = mode.load_file_content(fname)
                if content:
                    lines.append(f"### [{mode.name}] {fname.replace('.md', '').replace('-', ' ').title()}")
                    lines.append(content)
                    lines.append("")

        return "\n".join(lines)

    def _build_quality_gate_instructions(self, composed: ComposedMode) -> str:
        lines = [
            f"# Quality Gate Checklist: {composed.combined_name}",
            "",
            "Before declaring ANY task or project complete, you MUST execute the following verification cycle:",
            "",
            "1. **Requirements & Architecture Review**",
            "2. **Implementation Verification**",
            "3. **Build & Syntax Verification**",
            "4. **Automated Tests** (unit, integration, regression)",
            "5. **Security Audit** (no plaintext credentials, injection checks, input validation)",
            "6. **UI/UX & Accessibility Review** (semantic elements, responsive behavior, contrast)",
            "7. **Documentation & Changelog**",
            "",
            "### Mode-Specific Quality Gates:",
        ]
        for gate in composed.merged_quality_gates:
            lines.append(f"- [ ] {gate}")

        lines.extend([
            "",
            "### Error Policy & Reporting:",
            "Never falsely claim 'zero errors'. Classify any findings into:",
            "- `CRITICAL`: High-risk vulnerabilities, crashes, data corruption",
            "- `HIGH`: Broken core functionality, missing authentication",
            "- `MEDIUM`: UI inconsistencies, edge-case validation misses",
            "- `LOW`: Minor cosmetic issues, non-critical warnings",
            "- `INFO`: Suggestions for future enhancement",
        ])
        return "\n".join(lines)

    def _build_tools_instructions(self, composed: ComposedMode) -> str:
        lines = [
            f"# Tooling, Frameworks & SDK Reference: {composed.combined_name}",
            "",
            "Use industry-standard tools according to project requirements:",
            "",
        ]
        for mode in composed.resolved_modes:
            tool_content = mode.load_file_content("tools.md")
            if tool_content:
                lines.append(f"## {mode.name} Tooling")
                lines.append(tool_content)
                lines.append("")
        return "\n".join(lines)

    def _build_skill_md(self, composed: ComposedMode) -> str:
        return f"""---
name: ag-mode
description: >-
  Provides interactive controls and standards verification for the active mode: {composed.combined_name}.
---

# AG Mode: {composed.combined_name}

AntiGravity is currently configured with the **{composed.combined_name}** workflow.

## Guidelines & Quick Reference
- Active mode: `{composed.combined_name}`
- Mode components: `{', '.join([m.name for m in composed.resolved_modes])}`

To execute a quality gate check, inspect `.agents/rules/ag_quality_gate.md`.
To review tools and SDKs, inspect `.agents/rules/ag_tools.md`.
"""

    def _build_gemini_md(self, composed: ComposedMode) -> str:
        return f"""<!-- AG_MODE_MANAGER_START -->
# 🛡️ ACTIVE MODE: {composed.combined_name.upper()}
> Managed by AG Mode Manager | Environment: AntiGravity

You are currently operating in **{composed.combined_name}** mode.
You must adhere strictly to the guidelines defined in `.agents/rules/ag_active_mode.md`,
`.agents/rules/ag_quality_gate.md`, and `.agents/rules/ag_tools.md`.

Do not violate the quality gates, architectural patterns, UI/UX guidelines, or security boundaries.
<!-- AG_MODE_MANAGER_END -->"""

    def _update_gemini_md(self, ag_section: str) -> None:
        gemini_file = self.workspace_root / "GEMINI.md"
        existing_content = ""
        if gemini_file.exists():
            try:
                with open(gemini_file, "r", encoding="utf-8") as f:
                    existing_content = f.read()
            except Exception:
                existing_content = ""

        marker_start = "<!-- AG_MODE_MANAGER_START -->"
        marker_end = "<!-- AG_MODE_MANAGER_END -->"

        if marker_start in existing_content and marker_end in existing_content:
            idx1 = existing_content.find(marker_start)
            idx2 = existing_content.find(marker_end) + len(marker_end)
            new_content = existing_content[:idx1].strip() + "\n\n" + ag_section + "\n\n" + existing_content[idx2:].strip()
        else:
            new_content = ag_section + "\n\n" + existing_content.strip()

        with open(gemini_file, "w", encoding="utf-8") as f:
            f.write(new_content.strip() + "\n")
