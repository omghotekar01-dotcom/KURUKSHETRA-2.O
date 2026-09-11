from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"


def _run(command: list[str], cwd: Path) -> None:
    print(f"> {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def _npm_command(*args: str) -> list[str]:
    if os.name == "nt":
        return ["cmd", "/d", "/s", "/c", "npm", *args]
    return [shutil.which("npm") or "npm", *args]


def main() -> int:
    env_file = ROOT / ".env"
    env_example = ROOT / ".env.example"
    if not env_file.exists():
        shutil.copy2(env_example, env_file)
        print("Created .env from .env.example. Add private credentials only to .env; it is git-ignored.")

    if not VENV.exists():
        print("Creating backend virtual environment...")
        _run([sys.executable, "-m", "venv", str(VENV)], ROOT)

    python = _venv_python()
    if not python.exists():
        raise SystemExit("Virtual environment creation failed: backend/.venv Python is missing.")

    print("Installing pinned backend dependencies...")
    _run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements.txt"], BACKEND)

    lockfile = FRONTEND / "package-lock.json"
    if not lockfile.exists():
        raise SystemExit("frontend/package-lock.json is missing; refusing an unpinned frontend install.")

    print("Installing locked frontend dependency tree...")
    _run(_npm_command("ci", "--no-audit", "--no-fund"), FRONTEND)

    print("Bootstrap complete.")
    print(f"Backend Python: {python}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
