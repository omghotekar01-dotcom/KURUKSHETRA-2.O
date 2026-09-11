from __future__ import annotations

import os
import shutil
import subprocess

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


def github_token() -> str | None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token

    allow_cli = os.getenv("ALLOW_GH_CLI_AUTH", "true").strip().lower() not in {"0", "false", "no", "off"}
    if not allow_cli or shutil.which("gh") is None:
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
