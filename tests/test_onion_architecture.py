"""Guardrails de dependencias entre capas (Onion Architecture)."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LAYER_RULES: dict[str, tuple[str, ...]] = {
    "domain": (
        "app.api",
        "app.infrastructure",
        "app.composition_root",
        "fastapi",
        "pydantic",
        "sqlalchemy",
    ),
    "application": (
        "app.api",
        "app.infrastructure",
        "app.composition_root",
        "fastapi",
        "sqlalchemy",
    ),
    "api": (
        "app.infrastructure",
    ),
}


def _collect_import_violations(layer_name: str, forbidden_prefixes: tuple[str, ...]) -> list[str]:
    layer_root = PROJECT_ROOT / "app" / layer_name
    if not layer_root.exists():
        return []

    violations: list[str] = []
    for path in layer_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue

            for module in modules:
                if module.startswith(forbidden_prefixes):
                    violations.append(f"{path.relative_to(PROJECT_ROOT)} importa {module}")
    return violations


def test_domain_does_not_import_outer_layers_or_frameworks() -> None:
    violations = _collect_import_violations("domain", LAYER_RULES["domain"])
    assert not violations, "\n".join(violations)


def test_application_does_not_import_api_infrastructure_or_frameworks() -> None:
    violations = _collect_import_violations("application", LAYER_RULES["application"])
    assert not violations, "\n".join(violations)


def test_api_does_not_import_infrastructure_directly() -> None:
    violations = _collect_import_violations("api", LAYER_RULES["api"])
    assert not violations, "\n".join(violations)


def test_composition_root_is_the_only_assembler() -> None:
    """El ensamblaje concreto vive en composition_root, no disperso en controladores."""
    composition_root = PROJECT_ROOT / "app" / "composition_root.py"
    assert composition_root.exists()

    controllers = list((PROJECT_ROOT / "app" / "api" / "controllers").glob("*.py"))
    for controller in controllers:
        tree = ast.parse(controller.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.infrastructure"):
                raise AssertionError(f"{controller.name} importa infraestructura directamente.")
