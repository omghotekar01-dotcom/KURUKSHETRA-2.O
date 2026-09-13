from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
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


def _run_result(command: list[str], cwd: Path) -> int:
    print(f"> {' '.join(command)}")
    return subprocess.run(command, cwd=cwd, check=False).returncode


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def _npm_command(*args: str) -> list[str]:
    if os.name == "nt":
        return ["cmd", "/d", "/s", "/c", "npm", *args]
    return [shutil.which("npm") or "npm", *args]


def _stop_tracked_services() -> None:
    """Stop only services launched by this repository before replacing dependencies."""
    if os.name != "nt":
        return

    stop_script = ROOT / "scripts" / "stop.ps1"
    if not stop_script.exists():
        return

    print("Stopping tracked local project services before frontend dependency install...")
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(stop_script),
        ],
        cwd=ROOT,
        check=False,
    )


def _stop_project_node_processes() -> None:
    """Best-effort cleanup for untracked Node/Vite processes rooted in this checkout."""
    if os.name != "nt":
        return

    escaped_root = str(ROOT).replace("'", "''")
    script = (
        f"$root = '{escaped_root}'; "
        "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" -ErrorAction SilentlyContinue | "
        "Where-Object { $_.CommandLine -and $_.CommandLine -like ('*' + $root + '*') } | "
        "ForEach-Object { "
        "Write-Host ('Stopping project Node process PID ' + $_.ProcessId); "
        "Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue "
        "}"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        cwd=ROOT,
        check=False,
    )


def _install_frontend_dependencies() -> None:
    command = _npm_command("ci", "--no-audit", "--no-fund")

    _stop_tracked_services()
    code = _run_result(command, FRONTEND)
    if code == 0:
        return

    if os.name != "nt":
        raise SystemExit(code)

    # On Windows, Vite/Rolldown native bindings stay locked while an old dev server is alive.
    # Stop only Node processes whose command line belongs to this checkout, then retry npm ci.
    print("Frontend install failed on Windows. Releasing project-owned Node/Vite file locks and retrying once...")
    _stop_project_node_processes()
    time.sleep(1.5)

    retry_code = _run_result(command, FRONTEND)
    if retry_code != 0:
        print()
        print("[FAIL] Locked or inaccessible frontend dependencies could not be repaired automatically.")
        print("Close any terminal/editor task still running this project's Vite server, then run verify.bat again.")
        print("If this checkout is inside OneDrive, also make sure OneDrive is not actively locking frontend\\node_modules.")
        raise SystemExit(retry_code)


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

    constraints = BACKEND / "constraints.txt"
    if not constraints.exists():
        raise SystemExit("backend/constraints.txt is missing; refusing an unconstrained backend install.")

    print("Installing pinned and constrained backend dependency tree...")
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            "requirements.txt",
            "-c",
            "constraints.txt",
        ],
        BACKEND,
    )

    lockfile = FRONTEND / "package-lock.json"
    if not lockfile.exists():
        raise SystemExit("frontend/package-lock.json is missing; refusing an unpinned frontend install.")

    print("Installing locked frontend dependency tree...")
    _install_frontend_dependencies()

    print("Bootstrap complete.")
    print(f"Backend Python: {python}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
