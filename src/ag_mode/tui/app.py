"""Interactive Terminal User Interface for AG Mode Manager.

Implements the complete interactive workflow:
- Main Category Screen
- Category -> Modes Screen (with scrolling and dynamic numbering)
- Dynamic Search Modes Screen
- Mode Confirmation Popup ([ Yes ] [ No ])
- Step-by-step activation with visual progress
- Active Mode overview & mode switching
- Settings, Diagnostics, Repair, and Safe Uninstall dialogs
- Full keyboard (^/v/<-/→/Enter/Esc/Tab) and mouse support.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    DynamicContainer,
    Float,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Dialog, Button, Label

from ag_mode.config import ActiveModeState, AppConfig, find_workspace_root
from ag_mode.core.registry import CATEGORIES, ModeMetadata, mode_registry
from ag_mode.diagnostics.logger import logger
from ag_mode.installer.repair import repair as run_repair
from ag_mode.installer.uninstaller import uninstall as run_uninstall
from ag_mode.integration.adapter import AntiGravityAdapter
from ag_mode.integration.detector import detect_antigravity


TUI_STYLE = Style.from_dict({
    "header": "bold #00ff88",
    "subtitle": "#888888",
    "active_indicator": "bold #00ff88",
    "inactive_indicator": "#666666",
    "menu_item": "#cccccc",
    "menu_item.selected": "reverse #00ff88 bold",
    "action_item": "#00d4ff",
    "action_item.selected": "reverse #00d4ff bold",
    "danger_item": "#ff4444",
    "danger_item.selected": "reverse #ff4444 bold",
    "category": "#ffbb00 bold",
    "search_prompt": "bold #00d4ff",
    "search_input": "#ffffff bold",
    "dialog": "bg:#111111 #ffffff",
    "dialog.body": "bg:#1a1a1a #dddddd",
    "dialog.border": "#00ff88",
    "button": "#ffffff bg:#333333",
    "button.focused": "reverse #00ff88 bold",
    "status": "#888888",
    "keybind": "#00d4ff bold",
})


class ModeManagerTUI:
    """Terminal UI application state and screen renderer."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or find_workspace_root()
        self.adapter = AntiGravityAdapter(self.workspace_root)
        self.config = AppConfig.load()
        self.active_state = ActiveModeState.load(self.workspace_root)

        # UI state
        self.current_screen = "MAIN"  # 'MAIN', 'CATEGORY_MODES', 'SEARCH', 'CONFIRM', 'ACTIVATING', 'SETTINGS'
        self.selected_category_index = 0
        self.selected_mode_index = 0
        self.search_query = ""
        self.selected_category: Optional[str] = None
        self.target_mode: Optional[ModeMetadata] = None
        self.confirm_choice = True  # True = Yes, False = No
        self.activation_log: List[str] = []
        self.activation_done = False
        self.search_results: List[ModeMetadata] = []
        self.settings_index = 0

        # Build main categories + actions list
        self.categories = list(CATEGORIES)
        self.main_options = (
            [("cat", c) for c in self.categories]
            + [("action", "[/] Search Modes"), ("action", "[S] Settings"), ("action", "[X] Exit")]
        )

        self.kb = KeyBindings()
        self._setup_keybindings()

    def _setup_keybindings(self) -> None:
        kb = self.kb

        @kb.add("c-c")
        @kb.add("q")
        def _exit(event):
            if self.current_screen in ("MAIN", "ACTIVATING", "SETTINGS"):
                event.app.exit()
            else:
                self.current_screen = "MAIN"
                event.app.invalidate()

        @kb.add("escape")
        def _back(event):
            if self.current_screen == "CONFIRM":
                self.current_screen = "CATEGORY_MODES" if self.selected_category else "MAIN"
            elif self.current_screen in ("CATEGORY_MODES", "SEARCH", "SETTINGS"):
                self.current_screen = "MAIN"
            elif self.current_screen == "ACTIVATING":
                event.app.exit()
            else:
                event.app.exit()
            event.app.invalidate()

        @kb.add("up")
        def _up(event):
            if self.current_screen == "MAIN":
                if self.selected_category_index > 0:
                    self.selected_category_index -= 1
            elif self.current_screen in ("CATEGORY_MODES", "SEARCH"):
                if self.selected_mode_index > 0:
                    self.selected_mode_index -= 1
            elif self.current_screen == "SETTINGS":
                if self.settings_index > 0:
                    self.settings_index -= 1
            event.app.invalidate()

        @kb.add("down")
        def _down(event):
            if self.current_screen == "MAIN":
                if self.selected_category_index < len(self.main_options) - 1:
                    self.selected_category_index += 1
            elif self.current_screen == "CATEGORY_MODES":
                modes = mode_registry.get_by_category(self.selected_category or "")
                # Modes + Back option
                total = len(modes) + 1
                if self.selected_mode_index < total - 1:
                    self.selected_mode_index += 1
            elif self.current_screen == "SEARCH":
                if self.selected_mode_index < len(self.search_results) - 1:
                    self.selected_mode_index += 1
            elif self.current_screen == "SETTINGS":
                if self.settings_index < 4:
                    self.settings_index += 1
            event.app.invalidate()

        @kb.add("left")
        @kb.add("right")
        @kb.add("tab")
        def _toggle_confirm(event):
            if self.current_screen == "CONFIRM":
                self.confirm_choice = not self.confirm_choice
                event.app.invalidate()

        @kb.add("enter")
        def _enter(event):
            if self.current_screen == "MAIN":
                item_type, val = self.main_options[self.selected_category_index]
                if item_type == "cat":
                    self.selected_category = val
                    self.selected_mode_index = 0
                    self.current_screen = "CATEGORY_MODES"
                elif val == "[/] Search Modes":
                    self.search_query = ""
                    self.search_results = list(mode_registry.modes.values())[:15]
                    self.selected_mode_index = 0
                    self.current_screen = "SEARCH"
                elif val == "[S] Settings":
                    self.settings_index = 0
                    self.current_screen = "SETTINGS"
                elif val == "[X] Exit":
                    event.app.exit()

            elif self.current_screen == "CATEGORY_MODES":
                modes = mode_registry.get_by_category(self.selected_category or "")
                if self.selected_mode_index < len(modes):
                    self.target_mode = modes[self.selected_mode_index]
                    self.confirm_choice = True
                    self.current_screen = "CONFIRM"
                else:
                    # Back selected
                    self.current_screen = "MAIN"

            elif self.current_screen == "SEARCH":
                if self.search_results and self.selected_mode_index < len(self.search_results):
                    self.target_mode = self.search_results[self.selected_mode_index]
                    self.confirm_choice = True
                    self.current_screen = "CONFIRM"

            elif self.current_screen == "CONFIRM":
                if self.confirm_choice and self.target_mode:
                    self.current_screen = "ACTIVATING"
                    self._execute_activation(event.app)
                else:
                    self.current_screen = "CATEGORY_MODES" if self.selected_category else "MAIN"

            elif self.current_screen == "ACTIVATING":
                # Close after activation
                event.app.exit()

            elif self.current_screen == "SETTINGS":
                self._handle_settings_enter(event)

            event.app.invalidate()

        # Handle keyboard typing for dynamic search
        @kb.add("<any>")
        def _type_search(event):
            if self.current_screen == "SEARCH":
                char = event.data
                if char.isprintable():
                    self.search_query += char
                    self.search_results = mode_registry.search(self.search_query)
                    self.selected_mode_index = 0
                    event.app.invalidate()

        @kb.add("backspace")
        def _backspace_search(event):
            if self.current_screen == "SEARCH":
                if self.search_query:
                    self.search_query = self.search_query[:-1]
                    self.search_results = mode_registry.search(self.search_query)
                    self.selected_mode_index = 0
                    event.app.invalidate()

    def _execute_activation(self, app) -> None:
        """Run activation steps and update UI."""
        if not self.target_mode:
            return

        self.activation_log = [f"Activating {self.target_mode.name}..."]
        app.invalidate()

        res = self.adapter.activate_mode(self.target_mode.id, scope='global')
        self.activation_log.extend(res["steps"])
        if res.get("success"):
            self.activation_log.append(f"\n{self.target_mode.name} Mode is now active.")
            self.activation_done = True
            # Reload from global scope so header banner updates to the new mode immediately
            self.active_state = ActiveModeState.load(None) or ActiveModeState.load(self.workspace_root)
        else:
            self.activation_log.append(f"\n[X] Activation error: {res.get('error', 'Unknown failure')}")
            self.activation_done = True
        app.invalidate()

    def _handle_settings_enter(self, event) -> None:
        if self.settings_index == 0:
            # Repair
            res = run_repair(self.workspace_root)
            self.activation_log = ["=== REPAIR REPORT ==="] + res["actions"] + res["warnings"]
            self.current_screen = "ACTIVATING"
        elif self.settings_index == 1:
            # Reset active mode
            self.adapter.deactivate_mode()
            self.active_state = None
            self.activation_log = ["[OK] Active mode deactivated and reset to default."]
            self.current_screen = "ACTIVATING"
        elif self.settings_index == 2:
            # Rollback
            from ag_mode.integration.backup import backup_manager
            succ = backup_manager.rollback()
            self.activation_log = [f"Rollback status: {'Successful' if succ else 'Failed'}"]
            self.current_screen = "ACTIVATING"
        elif self.settings_index == 3:
            # Safe Uninstall
            res = run_uninstall(self.workspace_root)
            self.activation_log = ["=== UNINSTALL REPORT ==="] + res["actions"]
            self.active_state = None
            self.current_screen = "ACTIVATING"
        elif self.settings_index == 4:
            # Back
            self.current_screen = "MAIN"

    def _render_content(self) -> FormattedText:
        text: List[Tuple[str, str]] = []

        # Header
        text.append(("class:header", "+--------------------------------------------------------------------------+\n"))
        text.append(("class:header", "|                           AG MODE MANAGER                                |\n"))
        text.append(("class:subtitle", "|                      AntiGravity Environment                             |\n"))
        text.append(("class:header", "+--------------------------------------------------------------------------+\n"))

        # Active Mode Banner
        active_name = self.active_state.mode_name if self.active_state else "None"
        indicator = "*" if self.active_state else "o"
        ind_style = "class:active_indicator" if self.active_state else "class:inactive_indicator"
        text.append(("class:status", "| Active Mode: "))
        text.append((ind_style, f"{indicator} {active_name:<55}"))
        text.append(("class:status", "|\n"))
        text.append(("class:header", "+--------------------------------------------------------------------------+\n"))

        if self.current_screen == "MAIN":
            text.append(("", "|  Select a Category:                                                      |\n"))
            text.append(("", "|                                                                          |\n"))
            for idx, (itype, val) in enumerate(self.main_options):
                is_sel = (idx == self.selected_category_index)
                prefix = "  > " if is_sel else "    "
                style = "class:menu_item.selected" if is_sel else ("class:action_item" if itype == "action" else "class:menu_item")
                line_str = f"{prefix}{val:<66}"
                text.append(("class:header", "|"))
                text.append((style, line_str[:68]))
                text.append(("class:header", "|\n"))

        elif self.current_screen == "CATEGORY_MODES":
            cat = self.selected_category or "Development"
            text.append(("class:category", f"|  [>] {cat.upper()} MODES:                                                   |\n"))
            text.append(("", "|                                                                          |\n"))
            modes = mode_registry.get_by_category(cat)

            # Viewport scrolling: display max 12 items at a time
            viewport_size = 12
            total_items = len(modes) + 1  # modes + [Back]
            start_idx = max(0, min(self.selected_mode_index - viewport_size // 2, total_items - viewport_size))
            end_idx = min(total_items, start_idx + viewport_size)

            for idx in range(start_idx, end_idx):
                is_sel = (idx == self.selected_mode_index)
                prefix = "  > " if is_sel else "    "
                style = "class:menu_item.selected" if is_sel else "class:menu_item"

                if idx < len(modes):
                    m = modes[idx]
                    num_str = f"[{idx+1:02d}]"
                    item_line = f"{prefix}{num_str} {m.name:<60}"
                else:
                    item_line = f"{prefix}<- Back to Categories"

                text.append(("class:header", "|"))
                text.append((style, f"{item_line:<74}"[:74]))
                text.append(("class:header", "|\n"))

        elif self.current_screen == "SEARCH":
            text.append(("class:search_prompt", "|  [/] SEARCH MODES                                                         |\n"))
            q_disp = self.search_query if self.search_query else "_"
            text.append(("", f"|  Search: {q_disp:<63} |\n"))
            text.append(("", "|--------------------------------------------------------------------------|\n"))

            if not self.search_results:
                text.append(("", "|    No matching modes found. Try another keyword.                         |\n"))
            else:
                viewport_size = 10
                start_idx = max(0, min(self.selected_mode_index - viewport_size // 2, len(self.search_results) - viewport_size))
                end_idx = min(len(self.search_results), start_idx + viewport_size)

                for idx in range(start_idx, end_idx):
                    m = self.search_results[idx]
                    is_sel = (idx == self.selected_mode_index)
                    prefix = "  > " if is_sel else "    "
                    style = "class:menu_item.selected" if is_sel else "class:menu_item"
                    line = f"{prefix}{m.name} ({m.category})"
                    text.append(("class:header", "|"))
                    text.append((style, f"{line:<74}"[:74]))
                    text.append(("class:header", "|\n"))

        elif self.current_screen == "CONFIRM":
            m_name = self.target_mode.name if self.target_mode else "Selected Mode"
            text.append(("", "|                                                                          |\n"))
            text.append(("class:header", "|   +------------------------------------------------------------------+   |\n"))
            text.append(("class:header", f"|   |  Activate Mode: {m_name:<49}|   |\n"))
            text.append(("class:header", "|   |                                                                  |   |\n"))
            text.append(("class:header", "|   |  Load its connected rules, tools, and quality gates?             |   |\n"))
            text.append(("class:header", "|   |                                                                  |   |\n"))
            yes_style = "class:button.focused" if self.confirm_choice else "class:button"
            no_style = "class:button.focused" if not self.confirm_choice else "class:button"
            text.append(("class:header", "|   |              "))
            text.append((yes_style, "  [ YES ]  "))
            text.append(("class:header", "        "))
            text.append((no_style, "  [ NO ]  "))
            text.append(("class:header", "                 |   |\n"))
            text.append(("class:header", "|   +------------------------------------------------------------------+   |\n"))
            text.append(("", "|                                                                          |\n"))

        elif self.current_screen == "ACTIVATING":
            text.append(("class:header", "|  Execution Status:                                                       |\n"))
            for line in self.activation_log:
                clean_l = line.strip()
                style = "class:active_indicator" if "[OK]" in clean_l else "class:menu_item"
                text.append(("class:header", "|  "))
                text.append((style, f"{clean_l:<72}"[:72]))
                text.append(("class:header", "|\n"))
            text.append(("", "|                                                                          |\n"))
            text.append(("class:keybind", "|  Press [Enter] or [Q] to close. AntiGravity will continue with this mode. |\n"))

        elif self.current_screen == "SETTINGS":
            text.append(("class:category", "|  [S] SYSTEM SETTINGS & MAINTENANCE:                                        |\n"))
            text.append(("", "|                                                                          |\n"))
            settings_opts = [
                "1. Repair Application & Validate Registry",
                "2. Reset / Deactivate Current Mode",
                "3. Rollback to Previous Backup Snapshot",
                "4. Uninstall AG Mode Manager Integration (Safe)",
                "<- Back to Main Menu",
            ]
            for idx, opt in enumerate(settings_opts):
                is_sel = (idx == self.settings_index)
                prefix = "  > " if is_sel else "    "
                style = "class:menu_item.selected" if is_sel else ("class:danger_item" if "Uninstall" in opt else "class:menu_item")
                line_str = f"{prefix}{opt:<66}"
                text.append(("class:header", "|"))
                text.append((style, line_str[:74]))
                text.append(("class:header", "|\n"))

        # Footer
        text.append(("class:header", "+--------------------------------------------------------------------------+\n"))
        text.append(("class:status", "| [^v] Navigate   [Enter] Select   [Esc] Back   [/] Search   [Q] Quit      |\n"))
        text.append(("class:header", "+--------------------------------------------------------------------------+\n"))

        return FormattedText(text)

    def run(self) -> None:
        """Launch the interactive TUI application."""
        content_control = FormattedTextControl(
            text=self._render_content,
            focusable=True,
            show_cursor=False,
        )
        body = Window(content=content_control, height=D())
        layout = Layout(body)

        app: Application[Any] = Application(
            layout=layout,
            key_bindings=self.kb,
            style=TUI_STYLE,
            full_screen=False,
            mouse_support=True,
        )
        app.run()


def launch_tui(workspace_root: Optional[Path] = None) -> None:
    tui = ModeManagerTUI(workspace_root)
    tui.run()


if __name__ == "__main__":
    launch_tui()
