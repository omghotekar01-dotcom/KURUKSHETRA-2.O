from __future__ import annotations

import base64
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

from app.schemas.incident import ApprovalDecision, IncidentRecord, IncidentStatus, PatchProposal
from app.schemas.patch import PatchExecutionResult, ValidationCheck
from app.services.github_client import GITHUB_API, github_headers, github_token, normalize_repo, repository_allowed


class PatchExecutionError(RuntimeError):
    pass


_CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".cpp", ".c", ".cc", ".cs"}
_CONFIG_OR_SCRIPT_EXTENSIONS = {".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf", ".xml", ".sh", ".ps1", ".bat", ".cmd", ".tf", ".hcl"}
_TEXT_ONLY_EXTENSIONS = {".md", ".txt", ".rst"}
_SPECIAL_EXECUTABLE_NAMES = {"dockerfile", "makefile", "jenkinsfile", "procfile"}


def _api(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    try:
        response = client.request(method, path, json=json, params=params)
    except httpx.HTTPError as exc:
        raise PatchExecutionError(f"GitHub request failed: {type(exc).__name__}") from exc
    if response.status_code >= 400:
        detail = ""
        try:
            payload = response.json()
            detail = str(payload.get("message", ""))[:240]
        except ValueError:
            detail = response.text[:240]
        raise PatchExecutionError(f"GitHub returned {response.status_code}: {detail or 'request failed'}")
    if response.status_code == 204 or not response.content:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise PatchExecutionError("GitHub returned a non-JSON response.") from exc


def _optional_get(client: httpx.Client, path: str, *, params: dict[str, Any] | None = None) -> Any | None:
    try:
        return _api(client, "GET", path, params=params)
    except PatchExecutionError as exc:
        if "GitHub returned 404" in str(exc):
            return None
        raise


def _decode_content(payload: dict[str, Any]) -> str:
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise PatchExecutionError("Target path is not a normal UTF-8 GitHub file.")
    try:
        return base64.b64decode(payload.get("content", ""), validate=False).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise PatchExecutionError("Target file is not valid UTF-8 text.") from exc


def _sequence_starts(lines: list[str], target: list[str]) -> list[int]:
    if not target or len(target) > len(lines):
        return []
    return [index for index in range(len(lines) - len(target) + 1) if lines[index : index + len(target)] == target]


def _replace_exact_sequence(source: str, before: list[str], after: list[str]) -> str:
    lines = source.splitlines()
    matches = _sequence_starts(lines, before)
    if len(matches) != 1:
        if not matches:
            raise PatchExecutionError("Approved current-line sequence is no longer present on the default branch. Refresh evidence.")
        raise PatchExecutionError("Approved current-line sequence appears more than once; refusing an ambiguous write.")
    index = matches[0]
    replaced = [*lines[:index], *after, *lines[index + len(before) :]]
    trailing_newline = source.endswith("\n")
    rendered = "\n".join(replaced)
    return rendered + ("\n" if trailing_newline else "")


def _branch_name(incident_id: str, proposal_id: str) -> str:
    incident = re.sub(r"[^a-z0-9-]+", "-", incident_id.lower()).strip("-")[-32:]
    proposal = re.sub(r"[^a-z0-9-]+", "-", proposal_id.lower()).strip("-")[-18:]
    return f"incident-fix/{incident}-{proposal}"


def patch_idempotency_key(incident_id: str, proposal: PatchProposal) -> str:
    fingerprint = "\n".join(
        [
            incident_id,
            proposal.proposal_id,
            proposal.repository,
            proposal.base_commit,
            proposal.file_path,
            proposal.hunk_header,
            "\n".join(proposal.before_lines),
            "\n".join(proposal.after_lines),
        ]
    )
    return f"REM-{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:20].upper()}"


def _validation_plan(file_path: str) -> list[tuple[str, str, list[str], int]] | None:
    lowered = file_path.lower()
    suffix = Path(lowered).suffix
    filename = Path(lowered).name
    npm = shutil.which("npm") or "npm"

    # Lockfile-aware frontend validation is reproducible; never mutate the lock
    # during remediation validation.
    if lowered.endswith(("package.json", "package-lock.json")):
        return [
            ("frontend dependencies", "frontend", [npm, "ci", "--no-audit", "--no-fund"], 180),
            ("frontend production build", "frontend", [npm, "run", "build"], 180),
        ]
    if lowered.startswith("frontend/") or suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return [
            ("frontend dependencies", "frontend", [npm, "ci", "--no-audit", "--no-fund"], 180),
            ("frontend production build", "frontend", [npm, "run", "build"], 180),
        ]
    if lowered.startswith("backend/") or lowered.endswith(".py"):
        return [
            ("backend compile", "backend", [sys.executable, "-m", "compileall", "-q", "app", "tests"], 90),
            ("backend tests", "backend", [sys.executable, "-m", "pytest", "-q"], 180),
        ]
    if suffix in _TEXT_ONLY_EXTENSIONS:
        return []

    # Configuration, automation and unsupported executable/code changes must
    # never get a green Draft PR merely because exact content was re-read.
    if suffix in _CODE_EXTENSIONS or suffix in _CONFIG_OR_SCRIPT_EXTENSIONS or filename in _SPECIAL_EXECUTABLE_NAMES:
        return None

    # Unknown file types fail closed. Only explicitly safe text documentation
    # receives the no-executable-validator path above.
    return None


def _run_command(name: str, command: list[str], cwd: Path, timeout: int) -> ValidationCheck:
    display = " ".join(command)
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ValidationCheck(name=name, command=display, status="FAIL", output=str(exc)[:4000])
    output = (result.stdout + "\n" + result.stderr).strip()[-4000:]
    return ValidationCheck(
        name=name,
        command=display,
        status="PASS" if result.returncode == 0 else "FAIL",
        exit_code=result.returncode,
        output=output,
    )


def _run_local_validation(repository: str, branch: str, file_path: str) -> list[ValidationCheck]:
    plan = _validation_plan(file_path)
    if plan is None:
        return [
            ValidationCheck(
                name="validator availability",
                command="n/a",
                status="FAIL",
                output="No trusted deterministic validator is configured for this code/configuration type; draft PR creation is blocked.",
            )
        ]
    if not plan:
        return [
            ValidationCheck(
                name="non-code change gate",
                command="exact GitHub content verification",
                status="PASS",
                output="The approved documentation/text replacement was re-read from the isolated branch. No executable code check is required for this explicitly safe file type.",
            )
        ]

    gh = shutil.which("gh")
    git = shutil.which("git")
    if gh is None or git is None:
        return [
            ValidationCheck(
                name="local validation workspace",
                command="gh repo clone",
                status="FAIL",
                output="GitHub CLI and git are required for real local validation before a draft PR can be opened.",
            )
        ]

    checks: list[ValidationCheck] = []
    with tempfile.TemporaryDirectory(prefix="kurukshetra-fix-") as temp:
        workspace = Path(temp) / "workspace"
        clone = _run_command(
            "clone isolated fix branch",
            [gh, "repo", "clone", repository, str(workspace), "--", "--branch", branch, "--depth", "1"],
            Path(temp),
            120,
        )
        checks.append(clone)
        if clone.status != "PASS":
            return checks

        for name, relative_cwd, command, timeout in plan:
            cwd = workspace / relative_cwd
            if not cwd.exists():
                checks.append(
                    ValidationCheck(
                        name=name,
                        command=" ".join(command),
                        status="FAIL",
                        output=f"Validation directory does not exist: {relative_cwd}",
                    )
                )
                break
            check = _run_command(name, command, cwd, timeout)
            checks.append(check)
            if check.status != "PASS":
                break
    return checks


def _draft_pr_body(incident: IncidentRecord, proposal: PatchProposal, branch: str, checks: list[ValidationCheck]) -> str:
    validation_lines = "\n".join(
        f"- {'✅' if check.status == 'PASS' else '❌'} **{check.name}** — `{check.command}`" for check in checks
    )
    return f"""## Incident remediation candidate

Incident: `{incident.id}` — {incident.incident.title}

This draft PR was created only after explicit human approval of patch proposal `{proposal.proposal_id}`.

### Evidence and proposal
- Repository: `{proposal.repository}`
- Investigated commit: `{proposal.base_commit}`
- File: `{proposal.file_path}`
- Strategy: `{proposal.strategy}`
- Proposal confidence: {proposal.confidence:.0%}
- Fix branch: `{branch}`

### Rationale
{proposal.rationale}

### Validation gate
{validation_lines}

### Safety boundary
This PR is **draft-only**. It was not merged or deployed automatically. Commit/hunk correlation is investigation guidance, not proof of causation. A human reviewer must inspect the diff and decide whether to merge.
"""


def _find_existing_pr(prs: list[dict[str, Any]], branch: str) -> dict[str, Any] | None:
    for pr in prs:
        head = pr.get("head") or {}
        if head.get("ref") == branch:
            return pr
    return None


def execute_approved_patch(incident: IncidentRecord, proposal: PatchProposal) -> PatchExecutionResult:
    repository = normalize_repo(proposal.repository)
    idempotency_key = patch_idempotency_key(incident.id, proposal)
    if not repository or not repository_allowed(repository):
        return PatchExecutionResult(
            incident_id=incident.id,
            proposal_id=proposal.proposal_id,
            decision=ApprovalDecision.approve,
            status="BLOCKED",
            message="Repository is not in the configured GitHub write allowlist.",
            repository=repository or proposal.repository,
            incident_status=IncidentStatus.escalated,
            idempotency_key=idempotency_key,
        )

    token = github_token()
    if not token:
        return PatchExecutionResult(
            incident_id=incident.id,
            proposal_id=proposal.proposal_id,
            decision=ApprovalDecision.approve,
            status="AUTH_REQUIRED",
            message="Live GitHub credentials are required before an approved patch can create a branch or draft PR.",
            repository=repository,
            incident_status=IncidentStatus.escalated,
            idempotency_key=idempotency_key,
        )

    encoded_path = quote(proposal.file_path, safe="/")
    branch = _branch_name(incident.id, proposal.proposal_id)
    branch_reused = False
    pr_reused = False

    try:
        with httpx.Client(base_url=GITHUB_API, headers=github_headers(token=token), timeout=20.0, follow_redirects=True) as client:
            repo_payload = _api(client, "GET", f"/repos/{repository}")
            default_branch = repo_payload.get("default_branch", "main")
            ref_payload = _api(client, "GET", f"/repos/{repository}/git/ref/heads/{quote(default_branch, safe='')}")
            base_head = ref_payload["object"]["sha"]

            file_payload = _api(client, "GET", f"/repos/{repository}/contents/{encoded_path}", params={"ref": default_branch})
            current_source = _decode_content(file_payload)
            updated_source = _replace_exact_sequence(current_source, proposal.before_lines, proposal.after_lines)

            branch_ref = _optional_get(
                client,
                f"/repos/{repository}/git/ref/heads/{quote(branch, safe='')}",
            )
            commit_sha: str | None = None

            if branch_ref is None:
                try:
                    _api(
                        client,
                        "POST",
                        f"/repos/{repository}/git/refs",
                        json={"ref": f"refs/heads/{branch}", "sha": base_head},
                    )
                    branch_ref = _optional_get(
                        client,
                        f"/repos/{repository}/git/ref/heads/{quote(branch, safe='')}",
                    )
                    if branch_ref is None:
                        raise PatchExecutionError("GitHub created the remediation branch but it could not be re-read safely.")
                except PatchExecutionError as exc:
                    if "GitHub returned 422" not in str(exc):
                        raise
                    branch_ref = _optional_get(
                        client,
                        f"/repos/{repository}/git/ref/heads/{quote(branch, safe='')}",
                    )
                    if branch_ref is None:
                        raise
                    branch_reused = True
            else:
                branch_reused = True

            branch_file = _api(
                client,
                "GET",
                f"/repos/{repository}/contents/{encoded_path}",
                params={"ref": branch},
            )
            branch_source = _decode_content(branch_file)

            if branch_source == updated_source:
                commit_sha = (branch_ref or {}).get("object", {}).get("sha")
            elif branch_source == current_source and (branch_ref or {}).get("object", {}).get("sha") == base_head:
                write_payload = _api(
                    client,
                    "PUT",
                    f"/repos/{repository}/contents/{encoded_path}",
                    json={
                        "message": f"fix: apply approved remediation for {incident.id}",
                        "content": base64.b64encode(updated_source.encode("utf-8")).decode("ascii"),
                        "sha": branch_file["sha"],
                        "branch": branch,
                    },
                )
                commit_sha = (write_payload.get("commit") or {}).get("sha")
            else:
                raise PatchExecutionError(
                    "Deterministic remediation branch already exists with different content; refusing a duplicate or ambiguous write."
                )

            written_payload = _api(
                client,
                "GET",
                f"/repos/{repository}/contents/{encoded_path}",
                params={"ref": branch},
            )
            written_source = _decode_content(written_payload)
            if written_source != updated_source:
                raise PatchExecutionError("GitHub branch content did not match the exact approved replacement after write.")

        validation = [
            ValidationCheck(
                name="approved patch integrity",
                command="re-read exact file from isolated GitHub branch",
                status="PASS",
                output=f"Exact approved replacement confirmed on {branch}.",
            )
        ]
        validation.extend(_run_local_validation(repository, branch, proposal.file_path))
        if any(check.status != "PASS" for check in validation):
            return PatchExecutionResult(
                incident_id=incident.id,
                proposal_id=proposal.proposal_id,
                decision=ApprovalDecision.approve,
                status="VALIDATION_FAILED",
                message="Patch is isolated on the deterministic fix branch, but validation failed. No pull request was created.",
                repository=repository,
                branch=branch,
                branch_url=f"https://github.com/{repository}/tree/{branch}",
                commit_sha=commit_sha,
                validation=validation,
                incident_status=IncidentStatus.escalated,
                reused=branch_reused,
                idempotency_key=idempotency_key,
            )

        owner = repository.split("/", 1)[0]
        with httpx.Client(base_url=GITHUB_API, headers=github_headers(token=token), timeout=20.0, follow_redirects=True) as client:
            prs = _api(
                client,
                "GET",
                f"/repos/{repository}/pulls",
                params={"state": "all", "head": f"{owner}:{branch}", "base": default_branch, "per_page": 20},
            )
            existing_pr = _find_existing_pr(prs or [], branch)
            if existing_pr is not None:
                if existing_pr.get("state") != "open":
                    raise PatchExecutionError(
                        "A remediation pull request for this exact proposal already exists but is closed. Review it before retrying."
                    )
                pr = existing_pr
                pr_reused = True
            else:
                pr = _api(
                    client,
                    "POST",
                    f"/repos/{repository}/pulls",
                    json={
                        "title": f"[Draft][{incident.id}] {incident.incident.title[:80]}",
                        "head": branch,
                        "base": default_branch,
                        "body": _draft_pr_body(incident, proposal, branch, validation),
                        "draft": True,
                    },
                )

        reused = branch_reused or pr_reused
        message = (
            "Existing remediation branch/PR was safely reused for this exact approved proposal; no duplicate GitHub resource was created."
            if reused
            else "Approved patch passed the configured validation gate and a draft pull request was created for human review."
        )
        return PatchExecutionResult(
            incident_id=incident.id,
            proposal_id=proposal.proposal_id,
            decision=ApprovalDecision.approve,
            status="DRAFT_PR_CREATED",
            message=message,
            repository=repository,
            branch=branch,
            branch_url=f"https://github.com/{repository}/tree/{branch}",
            commit_sha=commit_sha,
            draft_pr_number=pr.get("number"),
            draft_pr_url=pr.get("html_url"),
            validation=validation,
            incident_status=IncidentStatus.verifying,
            reused=reused,
            idempotency_key=idempotency_key,
        )
    except PatchExecutionError as exc:
        return PatchExecutionResult(
            incident_id=incident.id,
            proposal_id=proposal.proposal_id,
            decision=ApprovalDecision.approve,
            status="FAILED",
            message=str(exc),
            repository=repository,
            incident_status=IncidentStatus.escalated,
            idempotency_key=idempotency_key,
        )
