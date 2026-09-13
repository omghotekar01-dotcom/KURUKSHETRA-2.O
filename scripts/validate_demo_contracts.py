from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = (
    (
        "Broken Bearer Authentication API",
        ROOT / "demo_targets" / "broken_auth_api",
        "app.py",
        'scheme.lower() != "token"',
        'scheme.lower() != "bearer"',
    ),
    (
        "Broken Cart Total",
        ROOT / "demo_targets" / "broken_cart_total",
        "pricing.py",
        "return sum(prices) - 1",
        "return sum(prices)",
    ),
    (
        "Broken Pagination Boundary",
        ROOT / "demo_targets" / "broken_pagination",
        "pagination.py",
        "return items[start:end - 1]",
        "return items[start:end]",
    ),
)


def run_pytest(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def tail(result: subprocess.CompletedProcess[str], limit: int = 1200) -> str:
    text = (result.stdout + "\n" + result.stderr).strip()
    return text[-limit:] if text else "(no output)"


def main() -> int:
    print("AI Agentic Bug Router - demo validator self-check")
    print(f"Python: {sys.executable}")
    print()

    try:
        import pytest  # noqa: F401
        import fastapi  # noqa: F401
        import httpx  # noqa: F401
    except ImportError as exc:
        print(f"[ENV FAIL] Missing backend dependency: {exc}")
        print("Run: backend\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt")
        return 2

    failures = 0
    for name, source_root, source_name, broken_text, fixed_text in TARGETS:
        print(f"[CHECK] {name}")
        baseline = source_root / "baseline" / f"{source_name}.txt"
        if not baseline.exists():
            print(f"  [FAIL] Missing baseline: {baseline}")
            failures += 1
            continue

        with tempfile.TemporaryDirectory(prefix="bug-router-validator-") as temp_dir:
            temp_root = Path(temp_dir) / source_root.name
            shutil.copytree(source_root, temp_root, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            temp_source = temp_root / source_name
            shutil.copy2(baseline, temp_source)

            before = temp_source.read_text(encoding="utf-8")
            if before.count(broken_text) != 1:
                print("  [FAIL] Baseline does not contain the expected unique broken signature.")
                failures += 1
                continue

            broken_result = run_pytest(temp_root)
            if broken_result.returncode != 1:
                print(f"  [FAIL] Broken baseline should produce pytest exit 1, got {broken_result.returncode}.")
                print(tail(broken_result))
                failures += 1
                continue
            print("  [PASS] Broken baseline is reproducible (expected pytest failure).")

            temp_source.write_text(before.replace(broken_text, fixed_text, 1), encoding="utf-8")
            fixed_result = run_pytest(temp_root)
            if fixed_result.returncode != 0:
                print(f"  [FAIL] Corrected copy still fails validation (exit {fixed_result.returncode}).")
                print(tail(fixed_result))
                failures += 1
                continue
            print("  [PASS] Exact repair makes the same validator pass.")
        print()

    if failures:
        print(f"VALIDATION SELF-CHECK FAILED: {failures} target(s) need attention.")
        return 1

    print("VALIDATION SELF-CHECK PASSED: all registered demo contracts reproduce FAIL -> PASS correctly.")
    print("The real demo files were not changed; validation ran only in temporary copies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
