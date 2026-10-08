"""Command Line Interface (CLI) for AG Mode Manager.

Provides interactive TUI launch when called without arguments,
as well as comprehensive subcommands for automation, scripting, and CI/CD.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 console encoding on Windows to prevent charmap UnicodeEncodeError
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ag_mode import __app_name__, __version__
from ag_mode.config import ActiveModeState, AppConfig, find_workspace_root
from ag_mode.core.composer import ModeComposer
from ag_mode.core.custom_mode import custom_mode_manager
from ag_mode.core.registry import mode_registry
from ag_mode.diagnostics.logger import logger
from ag_mode.installer.installer import install as run_install
from ag_mode.installer.repair import repair as run_repair
from ag_mode.installer.uninstaller import uninstall as run_uninstall
from ag_mode.integration.adapter import AntiGravityAdapter
from ag_mode.integration.backup import backup_manager
from ag_mode.integration.detector import detect_antigravity
from ag_mode.platform.detector import detect_platform
from ag_mode.tui.app import launch_tui

console = Console(force_terminal=True, legacy_windows=False)


def print_banner() -> None:
    banner = f"[bold green]{__app_name__}[/] [cyan]v{__version__}[/] - AntiGravity Mode, Rules & Quality-Control System"
    console.print(Panel(banner, border_style="green", expand=False))


def cmd_list(args: argparse.Namespace) -> None:
    print_banner()
    categories = [args.category] if args.category else mode_registry.get_categories()

    for cat in categories:
        numbered = mode_registry.get_numbered_modes(cat)
        if not numbered:
            continue
        table = Table(title=f"Category: [bold yellow]{cat}[/]", border_style="dim", expand=True)
        table.add_column("#", style="cyan", width=4, justify="right")
        table.add_column("ID", style="bold green", width=22)
        table.add_column("Mode Name", style="white", width=28)
        table.add_column("Description", style="dim")

        for num, mode in numbered:
            custom_tag = " [italic cyan](Custom)[/]" if mode.is_custom else ""
            table.add_row(str(num), mode.id, mode.name + custom_tag, mode.description)

        console.print(table)
        console.print()


def cmd_status(args: argparse.Namespace) -> None:
    print_banner()
    ws = find_workspace_root(Path(args.workspace) if args.workspace else None)
    state = ActiveModeState.load(ws)
    env = detect_antigravity(ws)

    table = Table(title="Environment & Mode Status", border_style="green")
    table.add_column("Property", style="cyan", width=24)
    table.add_column("Value", style="white")

    if state:
        table.add_row("Active Mode", f"[bold green]● {state.mode_name}[/]")
        table.add_row("Mode ID", state.mode_id)
        table.add_row("Scope", state.scope)
        table.add_row("Activated At", state.activated_at)
        if state.dependencies:
            table.add_row("Dependencies", ", ".join(state.dependencies))
        if state.composed_with:
            table.add_row("Composed With", ", ".join(state.composed_with))
    else:
        table.add_row("Active Mode", "[dim]None (Standard AntiGravity defaults)[/]")

    table.add_row("Workspace Root", str(ws))
    table.add_row("AntiGravity Detected", "[green]Yes[/]" if env.detected else "[yellow]No (Stand-alone mode)[/]")
    if env.version:
        table.add_row("AntiGravity Surface", env.version)
    if env.supported_mechanisms:
        table.add_row("Supported Integrations", ", ".join(env.supported_mechanisms))

    console.print(table)


def cmd_activate(args: argparse.Namespace) -> None:
    print_banner()
    ws = find_workspace_root(Path(args.workspace) if args.workspace else None)
    adapter = AntiGravityAdapter(ws)

    console.print(f"[bold cyan]Activating mode:[/] [bold green]{args.mode_id}[/] in [yellow]{ws}[/]...")
    res = adapter.activate_mode(args.mode_id, composed_with=args.compose, scope=args.scope)

    for step in res.get("steps", []):
        if "✓" in step:
            console.print(f"[green]{step}[/]")
        else:
            console.print(f"[yellow]{step}[/]")

    if res.get("success"):
        console.print(f"\n[bold green]✓ {res['mode_name']} Mode is now active in AntiGravity.[/]")
    else:
        console.print(f"\n[bold red]✕ Activation failed:[/] {res.get('error')}")
        sys.exit(1)


def cmd_deactivate(args: argparse.Namespace) -> None:
    print_banner()
    ws = find_workspace_root(Path(args.workspace) if args.workspace else None)
    adapter = AntiGravityAdapter(ws)
    adapter.deactivate_mode()
    console.print(f"[green]✓ Active mode deactivated and workspace cleaned in:[/] {ws}")


def cmd_search(args: argparse.Namespace) -> None:
    print_banner()
    results = mode_registry.search(args.query, category=args.category)
    if not results:
        console.print(f"[yellow]No modes matching query '{args.query}'.[/]")
        return

    table = Table(title=f"Search Results for '[bold cyan]{args.query}[/]' ({len(results)} found)", border_style="cyan")
    table.add_column("ID", style="bold green", width=22)
    table.add_column("Category", style="yellow", width=24)
    table.add_column("Name", style="white", width=28)
    table.add_column("Description", style="dim")

    for m in results:
        table.add_row(m.id, m.category, m.name, m.description)

    console.print(table)


def cmd_compose(args: argparse.Namespace) -> None:
    print_banner()
    composer = ModeComposer(mode_registry)
    try:
        composed = composer.compose(args.modes)
        console.print(f"[bold green]Composed Mode:[/] {composed.combined_name}")
        console.print(f"Modes included: {', '.join([m.name for m in composed.resolved_modes])}")
        console.print(f"Quality gates merged: {len(composed.merged_quality_gates)}")
        if composed.conflicts:
            console.print("\n[yellow]Potential Conflicts / Policies Handled:[/]")
            for c in composed.conflicts:
                console.print(f" - [bold]{c.category}:[/] {c.description} -> {c.suggested_resolution}")
    except Exception as e:
        console.print(f"[bold red]Failed to compose modes:[/] {e}")
        sys.exit(1)


def cmd_custom(args: argparse.Namespace) -> None:
    print_banner()
    if args.custom_action == "create":
        mode = custom_mode_manager.create_mode(
            name=args.name,
            description=args.desc or f"Custom mode for {args.name}",
            category=args.category or "General",
        )
        console.print(f"[bold green]✓ Custom mode created successfully![/]")
        console.print(f"Name: [white]{mode.name}[/]")
        console.print(f"ID: [cyan]{mode.id}[/]")
        console.print(f"Directory: [yellow]{mode.directory}[/]")
    elif args.custom_action == "list":
        custom_modes = custom_mode_manager.list_custom_modes()
        if not custom_modes:
            console.print("[dim]No custom modes created yet.[/]")
            return
        table = Table(title="Custom Modes", border_style="cyan")
        table.add_column("ID", style="green")
        table.add_column("Name", style="white")
        table.add_column("Category", style="yellow")
        table.add_column("Path", style="dim")
        for m in custom_modes:
            table.add_row(m.id, m.name, m.category, str(m.directory))
        console.print(table)
    elif args.custom_action == "delete":
        if custom_mode_manager.delete_custom_mode(args.mode_id):
            console.print(f"[green]✓ Deleted custom mode:[/] {args.mode_id}")
        else:
            console.print(f"[red]Failed to delete custom mode:[/] {args.mode_id}")


def cmd_repair(args: argparse.Namespace) -> None:
    print_banner()
    ws = find_workspace_root(Path(args.workspace) if args.workspace else None)
    res = run_repair(ws)
    for act in res["actions"]:
        console.print(f"[green]{act}[/]")
    for warn in res["warnings"]:
        console.print(f"[yellow]{warn}[/]")
    console.print("\n[bold green]✓ Application repair and verification complete.[/]")


def cmd_rollback(args: argparse.Namespace) -> None:
    print_banner()
    succ = backup_manager.rollback(args.snapshot)
    if succ:
        console.print("[bold green]✓ Rollback completed successfully.[/]")
    else:
        console.print("[bold red]✕ Rollback failed. Check diagnostic logs.[/]")
        sys.exit(1)


def cmd_uninstall(args: argparse.Namespace) -> None:
    print_banner()
    ws = find_workspace_root(Path(args.workspace) if args.workspace else None)
    res = run_uninstall(ws, remove_all_appdata=args.all)
    for act in res["actions"]:
        console.print(f"[green]{act}[/]")


def cmd_doctor(args: argparse.Namespace) -> None:
    print_banner()
    platform_info = detect_platform()
    ws = find_workspace_root()
    env = detect_antigravity(ws)

    table = Table(title="AG Mode Manager - Health & Diagnostics", border_style="green")
    table.add_column("Check", style="cyan", width=25)
    table.add_column("Status", style="bold white")

    table.add_row("Operating System", f"{platform_info.display_os} ({platform_info.arch})")
    table.add_row("Python Runtime", platform_info.python_version)
    table.add_row("Shell", platform_info.shell_name)
    table.add_row("Terminal VT100 / UTF-8", "✓ Supported" if platform_info.has_vt100 else "Limited")
    table.add_row("Mouse Support", "✓ Enabled" if platform_info.has_mouse_support else "Keyboard only fallback")
    table.add_row("AntiGravity Detected", "✓ Detected" if env.detected else "Standalone mode")
    if env.version:
        table.add_row("AntiGravity Surface", env.version)
    table.add_row("Workspace Root", str(ws))
    table.add_row("Registry Modes Count", str(len(mode_registry.modes)))

    console.print(table)


def cmd_logs(args: argparse.Namespace) -> None:
    print_banner()
    recent = logger.get_recent_logs(args.type, max_lines=args.lines)
    if not recent:
        console.print(f"[dim]No logs found in {args.type}.log[/]")
        return
    console.print(f"[bold cyan]Recent logs from {args.type}.log:[/]")
    for line in recent:
        console.print(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ag-mode",
        description="AG Mode Manager: Selectable working mode system for AntiGravity.",
    )
    parser.add_argument("--version", action="version", version=f"{__app_name__} {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list
    p_list = subparsers.add_parser("list", help="List available categories and modes")
    p_list.add_argument("--category", "-c", help="Filter by category")

    # status
    p_status = subparsers.add_parser("status", help="Show active mode and environment details")
    p_status.add_argument("--workspace", "-w", help="Target workspace path")

    # activate
    p_activate = subparsers.add_parser("activate", help="Activate a specific mode")
    p_activate.add_argument("mode_id", help="ID of the mode to activate (e.g. web, android, data-science)")
    p_activate.add_argument("--compose", "-m", nargs="+", help="Additional modes to compose with")
    p_activate.add_argument("--scope", choices=["workspace", "session", "global"], default="workspace")
    p_activate.add_argument("--workspace", "-w", help="Target workspace path")

    # deactivate / reset
    p_deact = subparsers.add_parser("deactivate", help="Deactivate active mode")
    p_deact.add_argument("--workspace", "-w", help="Target workspace path")
    p_reset = subparsers.add_parser("reset", help="Reset active mode in workspace")
    p_reset.add_argument("--workspace", "-w", help="Target workspace path")

    # search
    p_search = subparsers.add_parser("search", help="Search modes by keyword")
    p_search.add_argument("query", help="Keyword or mode name")
    p_search.add_argument("--category", "-c", help="Filter by category")

    # compose
    p_compose = subparsers.add_parser("compose", help="Compose multiple modes together")
    p_compose.add_argument("modes", nargs="+", help="Mode IDs to compose (e.g. web cybersecurity)")

    # custom
    p_custom = subparsers.add_parser("custom", help="Manage custom modes")
    custom_sub = p_custom.add_subparsers(dest="custom_action", required=True)
    c_create = custom_sub.add_parser("create", help="Create a new custom mode")
    c_create.add_argument("name", help="Name of custom mode (e.g. 'UET Data Science')")
    c_create.add_argument("--desc", help="Description")
    c_create.add_argument("--category", default="General", help="Category")
    custom_sub.add_parser("list", help="List custom modes")
    c_del = custom_sub.add_parser("delete", help="Delete a custom mode")
    c_del.add_argument("mode_id", help="Mode ID to delete")

    # repair
    p_repair = subparsers.add_parser("repair", help="Repair application and validate mode registry")
    p_repair.add_argument("--workspace", "-w", help="Target workspace path")

    # rollback
    p_rollback = subparsers.add_parser("rollback", help="Rollback workspace to previous backup snapshot")
    p_rollback.add_argument("--snapshot", "-s", help="Specific snapshot ID")

    # uninstall
    p_uninst = subparsers.add_parser("uninstall", help="Safely remove AG Mode Manager integration")
    p_uninst.add_argument("--all", action="store_true", help="Also remove application data directory")
    p_uninst.add_argument("--workspace", "-w", help="Target workspace path")

    # doctor / diagnostics
    subparsers.add_parser("doctor", help="Run environment and integration diagnostics")

    # logs
    p_logs = subparsers.add_parser("logs", help="View sanitized logs")
    p_logs.add_argument("--type", default="activation", choices=["installer", "activation", "integration", "error", "diagnostics"])
    p_logs.add_argument("--lines", "-n", type=int, default=30)

    # installer
    subparsers.add_parser("install", help="Run installation procedure")

    args = parser.parse_args()

    # If no subcommand passed, launch interactive TUI!
    if not args.command:
        launch_tui()
        return

    if args.command == "list":
        cmd_list(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "activate":
        cmd_activate(args)
    elif args.command in ("deactivate", "reset"):
        cmd_deactivate(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "compose":
        cmd_compose(args)
    elif args.command == "custom":
        cmd_custom(args)
    elif args.command == "repair":
        cmd_repair(args)
    elif args.command == "rollback":
        cmd_rollback(args)
    elif args.command == "uninstall":
        cmd_uninstall(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    elif args.command == "logs":
        cmd_logs(args)
    elif args.command == "install":
        res = run_install()
        for msg in res["messages"]:
            console.print(msg)


if __name__ == "__main__":
    main()
