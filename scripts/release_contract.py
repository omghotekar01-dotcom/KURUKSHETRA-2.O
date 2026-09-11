from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(condition: bool, message: str) -> bool:
    prefix = "PASS" if condition else "FAIL"
    print(f"[{prefix}] {message}")
    return condition


def main() -> int:
    required_files = [
        "README.md",
        ".env.example",
        ".github/workflows/build.yml",
        "frontend/package-lock.json",
        "frontend/src/JudgeDemoPage.tsx",
        "frontend/src/judge-demo.css",
        "frontend/src/ReadinessPage.tsx",
        "frontend/src/EvaluationLabPage.tsx",
        "frontend/src/PatchRemediationPage.tsx",
        "docs/JUDGE_DEMO_RUNBOOK.md",
        "docs/SECURITY_READINESS_MILESTONE.md",
        "docs/IMPLEMENTATION_PROGRESS.md",
        "scripts/start.ps1",
        "scripts/start.sh",
    ]

    passed = True
    for relative in required_files:
        passed &= check((ROOT / relative).is_file(), f"required release artifact exists: {relative}")

    main_tsx = (ROOT / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")
    route_contracts = {
        "Judge Mode route /demo": "path === '/demo'",
        "Readiness route /readiness": "path === '/readiness'",
        "Evaluation route /evaluation": "path === '/evaluation'",
        "Evidence route /evidence": "path === '/evidence'",
        "Remediation route /remediate": "path === '/remediate'",
    }
    for label, marker in route_contracts.items():
        passed &= check(marker in main_tsx, label)

    judge_page = (ROOT / "frontend" / "src" / "JudgeDemoPage.tsx").read_text(encoding="utf-8")
    judge_contracts = {
        "Judge Mode defaults repository writes to locked": "useState(false)" in judge_page and "LOCKED BY DEFAULT" in judge_page,
        "Judge Mode requires explicit approval": "patch-decision" in judge_page and "Arm live remediation" in judge_page,
        "Judge Mode can surface real CI": "patch-verification" in judge_page,
        "Judge Mode exposes fail-closed behavior": "SAFE_STOP" in judge_page and "Fail-closed result" in judge_page,
    }
    for label, condition in judge_contracts.items():
        passed &= check(condition, label)

    lock_path = ROOT / "frontend" / "package-lock.json"
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        passed &= check(lock.get("lockfileVersion") == 3, "frontend lockfile v3 is committed")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    passed &= check("never auto-merges" in readme.lower() or "never auto-merge" in readme.lower(), "README states no automatic merge")
    passed &= check("agent-build-core" in readme, "README identifies active implementation branch")

    ps_launcher = (ROOT / "scripts" / "start.ps1").read_text(encoding="utf-8")
    sh_launcher = (ROOT / "scripts" / "start.sh").read_text(encoding="utf-8")
    passed &= check("/demo" in ps_launcher, "Windows launcher exposes Judge Mode")
    passed &= check("/demo" in sh_launcher, "Unix launcher exposes Judge Mode")

    tracked_env = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".env"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    passed &= check(not tracked_env, ".env is not tracked by Git")

    print()
    if passed:
        print("RELEASE CANDIDATE CONTRACT: PASS")
        return 0

    print("RELEASE CANDIDATE CONTRACT: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
