from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"


@dataclass
class Check:
    name: str
    command: list[str]
    cwd: Path


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def _npm_command(*args: str) -> list[str]:
    if os.name == "nt":
        return ["cmd", "/d", "/s", "/c", "npm", *args]
    return [shutil.which("npm") or "npm", *args]


def _run(check: Check) -> bool:
    print(f"\n== {check.name} ==")
    print(f"> {' '.join(check.command)}")
    result = subprocess.run(check.command, cwd=check.cwd, check=False)
    if result.returncode == 0:
        print(f"[PASS] {check.name}")
        return True
    print(f"[FAIL] {check.name} (exit {result.returncode})")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Agentic Bug Router clean-clone acceptance")
    parser.add_argument("--bootstrap", action="store_true", help="Install dependencies before running acceptance checks.")
    args = parser.parse_args()

    if args.bootstrap:
        code = subprocess.run([sys.executable, str(ROOT / "scripts" / "bootstrap.py")], cwd=ROOT, check=False).returncode
        if code != 0:
            return code

    python = _venv_python()
    if not python.exists():
        print("[FAIL] backend/.venv is missing. Run: python scripts/bootstrap.py")
        return 1

    checks = [
        Check("backend compile", [str(python), "-m", "compileall", "-q", "app", "tests"], BACKEND),
        Check("backend test suite", [str(python), "-m", "pytest", "-q"], BACKEND),
        Check("frontend production build", _npm_command("run", "build"), FRONTEND),
    ]

    passed = 0
    for check in checks:
        if _run(check):
            passed += 1
        else:
            break

    print(f"\nAcceptance summary: {passed}/{len(checks)} checks passed")
    if passed != len(checks):
        return 1

    print("CLEAN-CLONE ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
