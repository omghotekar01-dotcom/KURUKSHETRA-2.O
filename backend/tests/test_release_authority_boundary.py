from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = ROOT / "backend" / "app"
FRONTEND_SRC = ROOT / "frontend" / "src"

FORBIDDEN_ROUTE_TERMS = {"merge", "deploy"}
FORBIDDEN_CALL_NAMES = {
    "merge_pull_request",
    "merge_pr",
    "deploy_production",
    "production_deploy",
}
FORBIDDEN_FRONTEND_ENDPOINT_MARKERS = (
    '/merge"',
    "/merge'",
    "/merge`",
    "/merge?",
    "/merge/",
    '/deploy"',
    "/deploy'",
    "/deploy`",
    "/deploy?",
    "/deploy/",
)


def _python_files() -> list[Path]:
    return sorted(BACKEND_APP.rglob("*.py"))


def _route_paths(tree: ast.AST) -> list[tuple[str, str]]:
    routes: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not decorator.args:
                continue
            function = decorator.func
            if not isinstance(function, ast.Attribute):
                continue
            if function.attr.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            first = decorator.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                routes.append((node.name, first.value))
    return routes


def _called_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            names.add(function.id)
        elif isinstance(function, ast.Attribute):
            names.add(function.attr)
    return names


def _contains_forbidden_frontend_endpoint(source: str) -> bool:
    normalized = source.lower()
    return any(marker in normalized for marker in FORBIDDEN_FRONTEND_ENDPOINT_MARKERS)


def test_backend_exposes_no_merge_or_deploy_route() -> None:
    violations: list[str] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for function_name, route in _route_paths(tree):
            normalized = route.lower()
            if any(term in normalized for term in FORBIDDEN_ROUTE_TERMS):
                violations.append(f"{path.relative_to(ROOT)}:{function_name} -> {route}")

    assert violations == [], "Release authority boundary violated by routes: " + "; ".join(violations)


def test_backend_contains_no_known_merge_or_production_deploy_executor() -> None:
    violations: list[str] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        forbidden = sorted(_called_names(tree) & FORBIDDEN_CALL_NAMES)
        if forbidden:
            violations.append(f"{path.relative_to(ROOT)} -> {', '.join(forbidden)}")

    assert violations == [], "Release authority boundary violated by executor calls: " + "; ".join(violations)


def test_judge_facing_remediation_stops_at_draft_pr() -> None:
    remediation = (FRONTEND_SRC / "PatchRemediationPage.tsx").read_text(encoding="utf-8")
    judge_demo = (FRONTEND_SRC / "JudgeDemoPage.tsx").read_text(encoding="utf-8")

    assert "Draft PR" in remediation
    assert "Draft PR" in judge_demo
    assert "never merges or deploys" in remediation.lower() or "merge and deployment stay outside" in remediation.lower()
    assert not _contains_forbidden_frontend_endpoint(remediation)
    assert not _contains_forbidden_frontend_endpoint(judge_demo)
