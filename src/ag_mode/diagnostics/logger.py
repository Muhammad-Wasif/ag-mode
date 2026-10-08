"""Diagnostic logging system for AG Mode Manager.

Provides sanitized logging to dedicated log files:
- installer.log
- activation.log
- integration.log
- error.log
- diagnostics.log
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from ag_mode.config import get_logs_dir
from ag_mode.security.sanitizer import sanitize_text


class DiagnosticLogger:
    """Sanitized structured logger for AG Mode Manager."""

    LOG_FILES = {
        "installer": "installer.log",
        "activation": "activation.log",
        "integration": "integration.log",
        "error": "error.log",
        "diagnostics": "diagnostics.log",
    }

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or get_logs_dir()
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _write_entry(self, log_type: str, level: str, message: str, context: Optional[dict] = None) -> None:
        filename = self.LOG_FILES.get(log_type, "diagnostics.log")
        log_file = self.logs_dir / filename
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        clean_msg = sanitize_text(message)
        clean_ctx = sanitize_text(str(context)) if context else ""
        entry = f"[{now}] [{level.upper()}] {clean_msg}"
        if clean_ctx:
            entry += f" | context: {clean_ctx}"
        entry += "\n"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def info(self, log_type: str, message: str, context: Optional[dict] = None) -> None:
        self._write_entry(log_type, "INFO", message, context)

    def warning(self, log_type: str, message: str, context: Optional[dict] = None) -> None:
        self._write_entry(log_type, "WARN", message, context)

    def error(self, log_type: str, message: str, context: Optional[dict] = None) -> None:
        self._write_entry(log_type, "ERROR", message, context)
        # Also duplicate to error.log if not already error
        if log_type != "error":
            self._write_entry("error", "ERROR", f"[{log_type}] {message}", context)

    def success(self, log_type: str, message: str, context: Optional[dict] = None) -> None:
        self._write_entry(log_type, "SUCCESS", message, context)

    def get_recent_logs(self, log_type: str, max_lines: int = 50) -> list[str]:
        filename = self.LOG_FILES.get(log_type, "diagnostics.log")
        log_file = self.logs_dir / filename
        if not log_file.exists():
            return []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [line.strip() for line in lines[-max_lines:]]
        except Exception:
            return []


# Global singleton instance
logger = DiagnosticLogger()
