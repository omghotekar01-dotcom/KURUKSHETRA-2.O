import os
import shutil
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.evaluation import EvaluationReport
from app.services.evaluation import run_evaluation

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


def _env_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@router.get("/run", response_model=EvaluationReport)
def evaluation_run() -> EvaluationReport:
    return run_evaluation()


@router.get("/readiness")
def system_readiness() -> dict:
    """Expose demo-safe readiness facts without returning credentials or secret values."""
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    demo_mode = _env_enabled("DEMO_MODE")
    repository_allowlist = [
        item.strip()
        for item in os.getenv("GITHUB_ALLOWED_REPOSITORIES", "").split(",")
        if item.strip()
    ]
    database_path = os.getenv("INCIDENT_DB_PATH", "data/incidents.db").strip()
    token_configured = bool(os.getenv("GITHUB_TOKEN", "").strip())
    gh_cli_allowed = _env_enabled("ALLOW_GH_CLI_AUTH", "true")
    gh_cli_available = shutil.which("gh") is not None

    required_checks = {
        "database_path_configured": bool(database_path),
        "repository_allowlist_configured": bool(repository_allowlist),
        "live_mode_default": not demo_mode,
    }
    status = "READY" if all(required_checks.values()) else "DEGRADED"

    if token_configured:
        github_access_mode = "TOKEN_CONFIGURED"
    elif gh_cli_allowed and gh_cli_available:
        github_access_mode = "GH_CLI_AVAILABLE"
    else:
        github_access_mode = "PUBLIC_READ_ONLY_OR_AUTH_REQUIRED_FOR_WRITES"

    return {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "FALLBACK_DEMO" if demo_mode else "LIVE_FIRST",
        "environment": app_env,
        "checks": required_checks,
        "github": {
            "allowlisted_repository_count": len(repository_allowlist),
            "access_mode": github_access_mode,
            "token_present": token_configured,
            "gh_cli_allowed": gh_cli_allowed,
            "gh_cli_available": gh_cli_available,
        },
        "safety": {
            "repository_evidence": "UNTRUSTED_DATA_ONLY",
            "incident_secret_redaction": "ENABLED",
            "repository_writes": "EXPLICIT_HUMAN_APPROVAL_REQUIRED",
            "high_risk_actions": "RECOMMENDATION_ONLY",
            "automatic_merge": False,
            "automatic_production_deploy": False,
        },
        "notes": [
            "Readiness never returns token or credential values.",
            "Repository text, issues, diffs and logs are evidence; they are not executable instructions.",
            "A green readiness state does not bypass approval, CI or human runtime verification.",
        ],
    }
