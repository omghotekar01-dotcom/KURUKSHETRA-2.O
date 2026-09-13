from __future__ import annotations

import argparse
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return result.returncode, (result.stdout or result.stderr).strip()


def _npm_command(*args: str) -> list[str]:
    if os.name == "nt":
        return ["cmd", "/d", "/s", "/c", "npm", *args]
    return [shutil.which("npm") or "npm", *args]


def _parse_major(version: str) -> int | None:
    match = re.search(r"(\d+)", version)
    return int(match.group(1)) if match else None


def _port_is_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Agentic Bug Router environment preflight")
    parser.add_argument("--strict", action="store_true", help="Require the tested Python 3.11 runtime.")
    parser.add_argument("--ci", action="store_true", help="CI-friendly output; do not treat occupied ports as warnings.")
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []

    print("AI Agentic Bug Router — environment preflight")
    print(f"Project: {ROOT}")

    py = sys.version_info
    if py < (3, 11):
        failures.append(f"Python 3.11+ is required; found {py.major}.{py.minor}.{py.micro}.")
    elif args.strict and (py.major, py.minor) != (3, 11):
        failures.append(
            f"The reproducible MVP runtime is Python 3.11.x; found {py.major}.{py.minor}.{py.micro}. "
            "Use Python 3.11 for the acceptance path."
        )
    else:
        print(f"[PASS] Python {py.major}.{py.minor}.{py.micro}")

    for tool in ("git", "node", "npm"):
        if shutil.which(tool) is None:
            failures.append(f"Required tool is missing from PATH: {tool}")

    if shutil.which("git"):
        code, output = _run([shutil.which("git") or "git", "--version"])
        if code == 0:
            print(f"[PASS] {output}")
        else:
            failures.append("git exists but could not be executed.")

    if shutil.which("node"):
        code, node_version = _run([shutil.which("node") or "node", "--version"])
        node_major = _parse_major(node_version)
        if code != 0 or node_major is None:
            failures.append("Node.js exists but its version could not be read.")
        elif not 22 <= node_major < 25:
            failures.append(f"Node.js 22–24 is required for the tested frontend toolchain; found {node_version}.")
        else:
            print(f"[PASS] Node {node_version}")

    if shutil.which("npm"):
        code, npm_version = _run(_npm_command("--version"))
        npm_major = _parse_major(npm_version)
        if code != 0 or npm_major is None:
            failures.append("npm exists but its version could not be read.")
        elif not 10 <= npm_major < 12:
            failures.append(f"npm 10–11 is required; found {npm_version}.")
        else:
            print(f"[PASS] npm {npm_version}")

    required_paths = [
        ROOT / "backend" / "requirements.txt",
        ROOT / "frontend" / "package.json",
        ROOT / ".env.example",
    ]
    for path in required_paths:
        if not path.exists():
            failures.append(f"Required project file is missing: {path.relative_to(ROOT)}")

    env_path = ROOT / ".env"
    if env_path.exists():
        print("[PASS] Local .env present")
    else:
        warnings.append(".env is not present yet; bootstrap will copy .env.example without adding secrets.")

    gh = shutil.which("gh")
    if gh:
        code, output = _run([gh, "--version"])
        if code == 0:
            print(f"[PASS] {output.splitlines()[0]}")
        auth_code, _ = _run([gh, "auth", "status"])
        if auth_code == 0:
            print("[PASS] GitHub CLI authentication available for live write actions")
        else:
            warnings.append("GitHub CLI is installed but not authenticated; live remediation writes will require GITHUB_TOKEN or gh auth login.")
    else:
        warnings.append("GitHub CLI is optional for read-only use, but live remediation validation needs gh + git on the demo machine.")

    if not args.ci:
        for port, name in ((8000, "backend"), (5173, "frontend")):
            if _port_is_open(port):
                warnings.append(f"Port {port} is already in use ({name}); the launcher will try to reuse or report the existing service.")
            else:
                print(f"[PASS] Port {port} available")

    for warning in warnings:
        print(f"[WARN] {warning}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        print(f"Preflight failed with {len(failures)} blocking issue(s).")
        return 1

    print("Preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
