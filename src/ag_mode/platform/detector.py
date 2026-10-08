"""Platform and architecture detection.

Detects OS (Windows, Linux, macOS), architecture (x64, ARM64),
terminal capabilities (color, mouse support, UTF-8), and environment.
"""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlatformInfo:
    os_name: str           # "Windows", "Linux", "Darwin" (macOS)
    display_os: str       # "Windows", "Linux", "macOS"
    arch: str              # "x64", "arm64", "x86", "other"
    python_version: str
    is_windows: bool
    is_linux: bool
    is_macos: bool
    has_vt100: bool
    has_mouse_support: bool
    has_unicode: bool
    shell_name: str


def detect_architecture() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64", "x64"):
        return "x64"
    elif machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("i386", "i686", "x86"):
        return "x86"
    return machine


def detect_shell() -> str:
    if sys.platform == "win32":
        if "PSModulePath" in os.environ:
            return "PowerShell"
        return "cmd"
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif "fish" in shell:
        return "fish"
    return shell or "sh"


def detect_platform() -> PlatformInfo:
    os_system = platform.system()
    display_os = "macOS" if os_system == "Darwin" else os_system
    is_win = os_system == "Windows"
    is_lin = os_system == "Linux"
    is_mac = os_system == "Darwin"

    # Terminal capabilities
    has_unicode = True
    if is_win:
        # Check if running in modern Windows Terminal or ConEmu
        wt = "WT_SESSION" in os.environ or "ConEmuPID" in os.environ or "TERM_PROGRAM" in os.environ
        has_vt100 = wt or sys.getwindowsversion().major >= 10
    else:
        has_vt100 = True

    # Mouse support is supported in Windows Terminal, xterm, modern emulators
    has_mouse = bool(os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM") or not is_win)

    return PlatformInfo(
        os_name=os_system,
        display_os=display_os,
        arch=detect_architecture(),
        python_version=platform.python_version(),
        is_windows=is_win,
        is_linux=is_lin,
        is_macos=is_mac,
        has_vt100=has_vt100,
        has_mouse_support=has_mouse,
        has_unicode=has_unicode,
        shell_name=detect_shell(),
    )
