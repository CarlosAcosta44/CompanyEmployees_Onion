"""Guardrails para evitar que el nucleo vuelva a depender de detalles externos."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = PROJECT_ROOT / "app" / "domain"
FORBIDDEN_IMPORT_PREFIXES = (
    "app.api",
    "app.infrastructure",
    "fastapi",
    "pydantic",
    "sqlalchemy",
)


def test_domain_does_not_import_outer_layers_or_frameworks() -> None:
    violations: list[str] = []

    for path in DOMAIN_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue

            for module in modules:
                if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    violations.append(f"{path.relative_to(PROJECT_ROOT)} importa {module}")

    assert not violations, "\n".join(violations)
