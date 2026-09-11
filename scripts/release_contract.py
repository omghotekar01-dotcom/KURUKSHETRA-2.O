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
        "frontend/src/BugWorkspacePage.tsx",
        "frontend/src/AppNavigation.tsx",
        "frontend/src/LoadingShimmer.tsx",
        "frontend/src/bug-workspace.css",
        "frontend/src/workspace-depth.css",
        "frontend/src/apple-polish.css",
        "frontend/src/dark-polish.css",
        "frontend/src/busy-polish.css",
        "frontend/src/purple-product-system.css",
        "frontend/src/async-state-polish.css",
        "frontend/src/JudgeDemoPage.tsx",
        "frontend/src/judge-demo.css",
        "frontend/src/JudgeIntakePage.tsx",
        "frontend/src/judge-intake.css",
        "frontend/src/AutofixPrototypePage.tsx",
        "frontend/src/ReadinessPage.tsx",
        "frontend/src/EvaluationLabPage.tsx",
        "frontend/src/PatchRemediationPage.tsx",
        "backend/app/services/workspace_intake.py",
        "backend/app/services/model_runtime.py",
        "backend/tests/test_workspace_intake.py",
        "backend/tests/test_model_runtime_probe.py",
        "backend/tests/test_github_write_readiness.py",
        "backend/tests/test_readiness_integrations.py",
        "docs/AI_WORKSPACE_UX.md",
        "docs/JUDGE_DEMO_RUNBOOK.md",
        "docs/JUDGE_SUPPLIED_INTAKE.md",
        "docs/SECURITY_READINESS_MILESTONE.md",
        "docs/IMPLEMENTATION_PROGRESS.md",
        "scripts/start.ps1",
        "scripts/start.sh",
        "setup-local-ai.bat",
    ]

    passed = True
    for relative in required_files:
        passed &= check((ROOT / relative).is_file(), f"required release artifact exists: {relative}")

    main_tsx = (ROOT / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")
    route_contracts = {
        "AI Workspace is the root product surface": "path === '/' || path === '/workspace'",
        "Incident Command remains available at /incidents": "path === '/incidents'",
        "Judge Mode route /demo": "path === '/demo'",
        "Real AutoFix route /prototype": "path === '/prototype'",
        "Judge Intake route /intake": "path === '/intake'",
        "AI Reasoning route /ai": "path === '/ai'",
        "Readiness route /readiness": "path === '/readiness'",
        "Evaluation route /evaluation": "path === '/evaluation'",
        "Evidence route /evidence": "path === '/evidence'",
        "Remediation route /remediate": "path === '/remediate'",
    }
    for label, marker in route_contracts.items():
        passed &= check(marker in main_tsx, label)

    style_contracts = {
        "AI Workspace depth layer is wired": "./workspace-depth.css" in main_tsx,
        "light Apple-style polish is wired": "./apple-polish.css" in main_tsx,
        "premium dark polish is wired": "./dark-polish.css" in main_tsx,
        "global operation shimmer is wired": "./busy-polish.css" in main_tsx,
        "white and purple product system is wired": "./purple-product-system.css" in main_tsx,
        "shared async loading polish is wired": "./async-state-polish.css" in main_tsx,
    }
    for label, condition in style_contracts.items():
        passed &= check(condition, label)

    navigation_page = (ROOT / "frontend" / "src" / "AppNavigation.tsx").read_text(encoding="utf-8")
    navigation_contracts = {
        "desktop navigation can collapse": "global-nav-collapse" in navigation_page and "navCollapsed" in navigation_page,
        "collapsed navigation persists locally": "bug-router-nav-collapsed" in navigation_page,
        "navigation keeps human authority visible": "Human authority" in navigation_page,
    }
    for label, condition in navigation_contracts.items():
        passed &= check(condition, label)

    workspace_page = (ROOT / "frontend" / "src" / "BugWorkspacePage.tsx").read_text(encoding="utf-8")
    workspace_contracts = {
        "AI Workspace accepts drag/drop file evidence": "onDrop" in workspace_page and "Attach files" in workspace_page,
        "AI Workspace accepts a GitHub repository": "GitHub repository" in workspace_page and "owner/repository" in workspace_page,
        "AI Workspace exposes trusted-test opt-in": "Trusted tests" in workspace_page,
        "AI Workspace exposes live integration proof": "Test live integrations" in workspace_page and "probe_integrations=true" in workspace_page,
        "AI Workspace live model label is probe-backed": "readiness?.model?.connected" in workspace_page and "installed · test live" in workspace_page,
        "AI Workspace preserves explicit reviewed apply": "Apply reviewed patch + verify" in workspace_page,
        "AI Workspace links live evidence to remediation": 'href="/evidence"' in workspace_page and 'href="/remediate"' in workspace_page,
    }
    for label, condition in workspace_contracts.items():
        passed &= check(condition, label)

    judge_page = (ROOT / "frontend" / "src" / "JudgeDemoPage.tsx").read_text(encoding="utf-8")
    judge_contracts = {
        "Judge Mode defaults repository writes to locked": "useState(false)" in judge_page and "LOCKED BY DEFAULT" in judge_page,
        "Judge Mode requires explicit approval": "patch-decision" in judge_page and "Arm live remediation" in judge_page,
        "Judge Mode can surface real CI": "patch-verification" in judge_page,
        "Judge Mode exposes fail-closed behavior": "SAFE_STOP" in judge_page and "Fail-closed result" in judge_page,
    }
    for label, condition in judge_contracts.items():
        passed &= check(condition, label)

    intake_page = (ROOT / "frontend" / "src" / "JudgeIntakePage.tsx").read_text(encoding="utf-8")
    intake_contracts = {
        "Judge Intake accepts attached files": 'type="file"' in intake_page,
        "Judge Intake exposes explicit trusted-test opt-in": "Trusted test execution" in intake_page,
        "Judge Intake exposes live Qwen probe": "Test Qwen now" in intake_page,
        "Judge Intake requires preview before apply": "Preview grounded AI fix" in intake_page and "Apply reviewed patch + verify" in intake_page,
        "Judge Intake surfaces RAG evidence": "Retrieved engineering knowledge" in intake_page,
    }
    for label, condition in intake_contracts.items():
        passed &= check(condition, label)

    readiness_page = (ROOT / "frontend" / "src" / "ReadinessPage.tsx").read_text(encoding="utf-8")
    readiness_contracts = {
        "Readiness performs active no-write integration probes": "probe_integrations=true" in readiness_page,
        "Readiness surfaces live Qwen inference": "Live inference" in readiness_page,
        "Readiness surfaces GitHub push permission": "Push permission" in readiness_page,
        "Readiness provides safe GitHub CLI recovery": "gh auth status" in readiness_page and "gh auth login" in readiness_page,
    }
    for label, condition in readiness_contracts.items():
        passed &= check(condition, label)

    evaluation_page = (ROOT / "frontend" / "src" / "EvaluationLabPage.tsx").read_text(encoding="utf-8")
    passed &= check("LoadingShimmer" in evaluation_page and "measured benchmark" in evaluation_page.lower(), "Evaluation Lab shows truthful measured loading placeholders")

    workspace_router = (ROOT / "backend" / "app" / "routers" / "workspace.py").read_text(encoding="utf-8")
    backend_intake_contracts = {
        "Backend exposes model inference probe": '/model-runtime/probe' in workspace_router,
        "Backend exposes isolated intake creation": '@router.post("/intake"' in workspace_router,
        "Backend exposes intake preview": '/intake/{session_id}/proposal' in workspace_router,
        "Backend exposes one-time intake apply": '/intake/{session_id}/apply' in workspace_router,
    }
    for label, condition in backend_intake_contracts.items():
        passed &= check(condition, label)

    model_runtime = (ROOT / "backend" / "app" / "services" / "model_runtime.py").read_text(encoding="utf-8")
    passed &= check("/api/tags" in model_runtime and "/api/chat" in model_runtime, "local Qwen supports native Ollama fallback")

    local_ai_setup = (ROOT / "setup-local-ai.bat").read_text(encoding="utf-8")
    passed &= check("ConvertTo-Json -InputObject $payload -Depth 8" in local_ai_setup, "Windows Qwen warm-up serializes without a CMD-escaped PowerShell pipeline")
    passed &= check("^| ConvertTo-Json" not in local_ai_setup, "Windows Qwen warm-up does not leak CMD pipe escaping into PowerShell")
    passed &= check("Invoke-RestMethod" in local_ai_setup and "/api/chat" in local_ai_setup, "Windows Qwen warm-up performs a real local inference request")

    evaluation_router = (ROOT / "backend" / "app" / "routers" / "evaluation.py").read_text(encoding="utf-8")
    passed &= check("probe_integrations" in evaluation_router and "github_write_readiness" in evaluation_router, "readiness exposes active no-write integration probes")

    github_client = (ROOT / "backend" / "app" / "services" / "github_client.py").read_text(encoding="utf-8")
    passed &= check("permissions" in github_client and '"push"' in github_client and "write_access" in github_client, "GitHub write readiness verifies push permission before remediation")

    lock_path = ROOT / "frontend" / "package-lock.json"
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        passed &= check(lock.get("lockfileVersion") == 3, "frontend lockfile v3 is committed")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    passed &= check("never auto-merges" in readme.lower() or "never auto-merge" in readme.lower(), "README states no automatic merge")
    passed &= check("agent-build-core" in readme, "README identifies active implementation branch")
    passed &= check("AI Workspace" in readme and "/incidents" in readme, "README documents the final product navigation")

    ps_launcher = (ROOT / "scripts" / "start.ps1").read_text(encoding="utf-8")
    sh_launcher = (ROOT / "scripts" / "start.sh").read_text(encoding="utf-8")
    for label, marker in {
        "Windows launcher exposes AI Workspace": "AI Workspace",
        "Windows launcher exposes Incident Command": "/incidents",
        "Windows launcher exposes Real AutoFix": "/prototype",
        "Windows launcher exposes Judge Intake": "/intake",
        "Windows launcher exposes Judge Mode": "/demo",
    }.items():
        passed &= check(marker in ps_launcher, label)
    for label, marker in {
        "Unix launcher exposes AI Workspace": "AI Workspace",
        "Unix launcher exposes Incident Command": "/incidents",
        "Unix launcher exposes Real AutoFix": "/prototype",
        "Unix launcher exposes Judge Intake": "/intake",
        "Unix launcher exposes Judge Mode": "/demo",
    }.items():
        passed &= check(marker in sh_launcher, label)

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
