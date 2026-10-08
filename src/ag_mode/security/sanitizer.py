"""Security utilities and secret sanitizer.

Protects credentials, tokens, API keys, and validates file paths
to prevent directory traversal and accidental overwriting of sensitive
AntiGravity system files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Pattern


# Patterns for known credential and secret formats
SECRET_PATTERNS: List[tuple[str, Pattern[str]]] = [
    ("GEMINI_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{30,40}")),
    ("OPENAI_KEY", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}")),
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GITHUB_PAT", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("BEARER_TOKEN", re.compile(r"Bearer\s+eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN\s+[A-Z\s]+PRIVATE\s+KEY-----[\s\S]+?-----END\s+[A-Z\s]+PRIVATE\s+KEY-----")),
    ("PASSWORD_PARAM", re.compile(r"(password|secret|token|passwd|pwd)\s*[=:]\s*['\"][^'\"]+['\"]", re.IGNORECASE)),
    ("URI_CREDENTIALS", re.compile(r"://[^:\s]+:[^@\s]+@")),
]


def sanitize_text(text: str) -> str:
    """Scrub sensitive credentials and secrets from text before logging or saving."""
    if not text:
        return text

    sanitized = text
    for name, pattern in SECRET_PATTERNS:
        if name == "URI_CREDENTIALS":
            sanitized = pattern.sub("://***:***@", sanitized)
        elif name == "PASSWORD_PARAM":
            sanitized = pattern.sub(r"\1=***", sanitized)
        elif name == "PRIVATE_KEY":
            sanitized = pattern.sub("[REDACTED PRIVATE KEY]", sanitized)
        elif name == "BEARER_TOKEN":
            sanitized = pattern.sub("Bearer [REDACTED JWT]", sanitized)
        else:
            sanitized = pattern.sub(f"[REDACTED_{name}]", sanitized)

    return sanitized


# Disallowed system and AntiGravity internal paths from modification
PROTECTED_PATTERNS = [
    r"[/\\]System32[/\\]",
    r"[/\\]etc[/\\]shadow",
    r"[/\\]etc[/\\]passwd",
    r"[/\\]\.gemini[/\\]antigravity-ide[/\\]bin",
    r"[/\\]\.gemini[/\\]antigravity-ide[/\\]core",
]


def is_safe_path(target_path: Path, allowed_roots: List[Path]) -> bool:
    """Verify that target_path is within allowed_roots and not matching protected system paths."""
    resolved = target_path.resolve()
    resolved_str = str(resolved)

    for pattern in PROTECTED_PATTERNS:
        if re.search(pattern, resolved_str, re.IGNORECASE):
            return False

    # Check if target is inside at least one allowed root
    for root in allowed_roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue

    return False
