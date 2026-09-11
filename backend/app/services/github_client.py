from __future__ import annotations

import os
import shutil
import subprocess

import httpx

DEFAULT_REPOSITORY = "omghotekar01-dotcom/KURUKSHETRA-2.O"
GITHUB_API = "https://api.github.com"


def normalize_repo(value: str) -> str:
    normalized = value.strip().removesuffix(".git").strip("/")
    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if normalized.lower().startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    return normalized.strip("/")


def configured_repository() -> str:
    return normalize_repo(os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))


def _cli_auth_allowed() -> bool:
    return os.getenv("ALLOW_GH_CLI_AUTH", "true").strip().lower() not in {"0", "false", "no", "off"}


def github_token() -> str | None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token

    if not _cli_auth_allowed() or shutil.which("gh") is None:
        return None

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    return result.stdout.strip() or None


def github_auth_source() -> str:
    """Return credential provenance only; never return the credential value."""
    if os.getenv("GITHUB_TOKEN", "").strip():
        return "ENV_TOKEN"
    if _cli_auth_allowed() and shutil.which("gh") is not None and github_token():
        return "GH_CLI"
    return "NONE"


def github_headers(*, token: str | None = None) -> dict[str, str]:
    resolved = token if token is not None else github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "kurukshetra-incident-command",
    }
    if resolved:
        headers["Authorization"] = f"Bearer {resolved}"
    return headers


def repository_allowed(repository: str) -> bool:
    requested = normalize_repo(repository)
    configured = configured_repository()
    raw_allowlist = os.getenv("GITHUB_ALLOWED_REPOSITORIES", "").strip()
    allowed = {configured}
    if raw_allowlist:
        allowed.update(normalize_repo(item) for item in raw_allowlist.split(",") if item.strip())
    return requested in allowed


def github_write_readiness(repository: str | None = None) -> dict[str, object]:
    """Actively verify authenticated push permission without performing a write.

    This intentionally uses a read-only repository metadata request. GitHub's
    authenticated repository payload includes the caller's permission flags, so
    we can explain why remediation writes would be blocked without creating a
    branch, commit, PR, or exposing the token.
    """
    target = normalize_repo(repository or configured_repository())
    allowed = bool(target) and repository_allowed(target)
    if not allowed:
        return {
            "repository": target,
            "authenticated": False,
            "auth_source": "NONE",
            "write_access": False,
            "status": "BLOCKED",
            "reason": "Repository is not in the configured write allowlist.",
        }

    token = github_token()
    source = "ENV_TOKEN" if os.getenv("GITHUB_TOKEN", "").strip() else ("GH_CLI" if token else "NONE")
    if not token:
        return {
            "repository": target,
            "authenticated": False,
            "auth_source": source,
            "write_access": False,
            "status": "AUTH_REQUIRED",
            "reason": "No GitHub write credential is available. Run gh auth login or configure a local token with repository write permission.",
        }

    try:
        response = httpx.get(
            f"{GITHUB_API}/repos/{target}",
            headers=github_headers(token=token),
            timeout=6.0,
            follow_redirects=True,
        )
    except httpx.HTTPError as exc:
        return {
            "repository": target,
            "authenticated": True,
            "auth_source": source,
            "write_access": False,
            "status": "UNREACHABLE",
            "reason": f"GitHub permission probe could not complete ({type(exc).__name__}).",
        }

    if response.status_code >= 400:
        return {
            "repository": target,
            "authenticated": response.status_code not in {401},
            "auth_source": source,
            "write_access": False,
            "status": "DENIED",
            "reason": f"GitHub permission probe returned HTTP {response.status_code}.",
        }

    try:
        payload = response.json()
    except ValueError:
        payload = {}
    permissions = payload.get("permissions") if isinstance(payload, dict) else None
    push = bool(permissions.get("push")) if isinstance(permissions, dict) else False
    return {
        "repository": target,
        "authenticated": True,
        "auth_source": source,
        "write_access": push,
        "status": "READY" if push else "READ_ONLY",
        "reason": (
            "Authenticated GitHub permission probe confirms push access for the allowlisted repository."
            if push
            else "Authentication works, but GitHub did not report push permission for this repository."
        ),
    }
