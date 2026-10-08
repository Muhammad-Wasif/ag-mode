"""Context Intelligence & Project Inspector.

Inspects workspace to detect languages, frameworks, existing architecture,
and identifies specialized project types (e.g. e-commerce, LMS, library management,
SaaS, dashboard) to tailor instructions without context bloat.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


PROJECT_TYPE_SIGNATURES = {
    "ecommerce": ["cart", "checkout", "product", "stripe", "order", "inventory", "shop"],
    "lms": ["course", "lesson", "quiz", "student", "teacher", "enrollment", "grade"],
    "library_management": ["book", "isbn", "borrow", "circulation", "catalog", "author"],
    "hospital_management": ["patient", "doctor", "appointment", "medical", "prescription", "clinic"],
    "crm": ["lead", "customer", "contact", "deal", "pipeline", "sales"],
    "dashboard": ["metrics", "charts", "analytics", "stats", "kpi", "overview"],
    "saas": ["subscription", "billing", "tenant", "organization", "plan", "pricing"],
    "portfolio": ["projects", "about", "skills", "resume", "showcase", "contact"],
    "documentation": ["docs", "guide", "tutorial", "api-reference", "docusaurus", "mkdocs"],
}


@dataclass
class ProjectInspection:
    is_existing_project: bool
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)
    has_tests: bool = False
    has_git: bool = False
    detected_types: List[str] = field(default_factory=list)
    summary: str = "Empty workspace"


def inspect_workspace(workspace_root: Path) -> ProjectInspection:
    """Analyze the workspace to detect existing technologies, frameworks, and project types."""
    if not workspace_root.exists() or not workspace_root.is_dir():
        return ProjectInspection(is_existing_project=False)

    languages: List[str] = []
    frameworks: List[str] = []
    package_managers: List[str] = []
    has_git = (workspace_root / ".git").exists()

    # Look for key indicator files
    pkg_json = workspace_root / "package.json"
    req_txt = workspace_root / "requirements.txt"
    pyproj = workspace_root / "pyproject.toml"
    cargo = workspace_root / "Cargo.toml"
    go_mod = workspace_root / "go.mod"
    pom_xml = workspace_root / "pom.xml"
    gradle = workspace_root / "build.gradle" or workspace_root / "build.gradle.kts"
    dockerfile = workspace_root / "Dockerfile" or workspace_root / "docker-compose.yml"

    is_existing = any([pkg_json.exists(), req_txt.exists(), pyproj.exists(), cargo.exists(), go_mod.exists(), pom_xml.exists(), gradle.exists()])

    if pkg_json.exists():
        languages.append("JavaScript/TypeScript")
        package_managers.append("npm/yarn/pnpm")
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "react" in deps:
                frameworks.append("React")
            if "next" in deps:
                frameworks.append("Next.js")
            if "vue" in deps:
                frameworks.append("Vue")
            if "express" in deps:
                frameworks.append("Express")
            if "tailwindcss" in deps:
                frameworks.append("TailwindCSS")
        except Exception:
            pass

    if req_txt.exists() or pyproj.exists():
        languages.append("Python")
        package_managers.append("pip")
        if req_txt.exists():
            try:
                with open(req_txt, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                if "fastapi" in content:
                    frameworks.append("FastAPI")
                if "django" in content:
                    frameworks.append("Django")
                if "flask" in content:
                    frameworks.append("Flask")
                if "torch" in content or "tensorflow" in content:
                    frameworks.append("Deep Learning / PyTorch / TF")
                if "pandas" in content:
                    frameworks.append("Data Science / Pandas")
            except Exception:
                pass

    if cargo.exists():
        languages.append("Rust")
        package_managers.append("Cargo")

    if go_mod.exists():
        languages.append("Go")
        package_managers.append("Go Modules")

    # Check for tests
    has_tests = any([
        (workspace_root / "tests").exists(),
        (workspace_root / "test").exists(),
        (workspace_root / "__tests__").exists(),
        any(workspace_root.glob("test_*.py")),
        any(workspace_root.glob("*.test.ts")),
        any(workspace_root.glob("*.test.js")),
    ])

    # Infer project type from file names and directory names
    detected_types: List[str] = []
    file_and_dir_names = [p.name.lower() for p in workspace_root.iterdir() if not p.name.startswith(".")]
    joined_names = " ".join(file_and_dir_names)

    for ptype, sigs in PROJECT_TYPE_SIGNATURES.items():
        if any(sig in joined_names for sig in sigs):
            detected_types.append(ptype)

    summary_parts = []
    if is_existing:
        summary_parts.append(f"Existing project with {', '.join(languages) if languages else 'unidentified language'}")
        if frameworks:
            summary_parts.append(f"Frameworks: {', '.join(frameworks)}")
        if detected_types:
            summary_parts.append(f"Inferred project type: {', '.join(detected_types)}")
    else:
        summary_parts.append("New/uninitialized project workspace")

    return ProjectInspection(
        is_existing_project=is_existing,
        languages=languages,
        frameworks=frameworks,
        package_managers=package_managers,
        has_tests=has_tests,
        has_git=has_git,
        detected_types=detected_types,
        summary="; ".join(summary_parts),
    )
