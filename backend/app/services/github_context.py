from __future__ import annotations

import base64
import binascii
import os
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx

from app.schemas.incident import (
    IncidentRecord,
    RepositoryCommitEvidence,
    RepositoryContext,
    RepositoryDiffHunkEvidence,
    RepositoryFileChange,
    RepositoryIssueEvidence,
    RepositorySourceLine,
)
from app.services.github_client import GITHUB_API, github_headers, github_token, normalize_repo, repository_allowed


class GitHubContextUnavailable(RuntimeError):
    pass


STOPWORDS = {
    "after",
    "again",
    "against",
    "and",
    "api",
    "are",
    "but",
    "can",
    "could",
    "error",
    "errors",
    "fail",
    "failed",
    "failure",
    "for",
    "from",
    "get",
    "has",
    "have",
    "into",
    "issue",
    "latest",
    "not",
    "our",
    "production",
    "request",
    "response",
    "service",
    "that",
    "the",
    "this",
    "today",
    "user",
    "users",
    "with",
}


def _tokens(text: str) -> set[str]:
    # Split code/path punctuation and snake_case so log terms such as "jwt"
    # can match identifiers such as "jwt_signing_key" and paths like auth/jwt.py.
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) >= 3 and token not in STOPWORDS
    }


def _incident_tokens(record: IncidentRecord) -> set[str]:
    return _tokens(
        " ".join(
            [
                record.incident.title,
                record.incident.description,
                " ".join(record.incident.logs),
                record.triage.component,
                record.triage.summary,
                " ".join(record.triage.signals),
            ]
        )
    )


def _token_score(incident_tokens: set[str], candidate_tokens: set[str], *, multiplier: float = 2.5) -> tuple[float, list[str]]:
    if not incident_tokens or not candidate_tokens:
        return 0.0, []
    overlap = sorted(incident_tokens & candidate_tokens)
    if not overlap:
        return 0.0, []
    denominator = max(3, min(10, len(incident_tokens)))
    score = round(min(1.0, (len(overlap) / denominator) * multiplier), 3)
    return score, overlap[:10]


def _parse_patch_hunks(record: IncidentRecord, filename: str, patch: str) -> list[RepositoryDiffHunkEvidence]:
    if not patch:
        return []

    incident_tokens = _incident_tokens(record)
    hunks: list[RepositoryDiffHunkEvidence] = []
    header = ""
    added: list[str] = []
    removed: list[str] = []

    def flush() -> None:
        nonlocal header, added, removed
        if not header:
            return
        candidate_tokens = _tokens(" ".join([filename, header, *added, *removed]))
        score, matched_terms = _token_score(incident_tokens, candidate_tokens, multiplier=3.2)
        hunks.append(
            RepositoryDiffHunkEvidence(
                filename=filename,
                header=header[:240],
                added_lines=added[:10],
                removed_lines=removed[:10],
                matched_terms=matched_terms,
                correlation_score=score,
            )
        )
        added = []
        removed = []

    for raw_line in patch.splitlines():
        if raw_line.startswith("@@"):
            flush()
            header = raw_line
            continue
        if not header:
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            added.append(raw_line[1:][:260])
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            removed.append(raw_line[1:][:260])

    flush()
    hunks.sort(key=lambda item: item.correlation_score, reverse=True)
    return hunks[:4]


def _new_hunk_start(header: str) -> int | None:
    match = re.search(r"\+(\d+)(?:,\d+)?", header)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:  # pragma: no cover - regex guarantees digits
        return None


def _fetch_source_context(
    client: httpx.Client,
    repository: str,
    commit_sha: str,
    hunk: RepositoryDiffHunkEvidence,
) -> list[RepositorySourceLine]:
    start_line = _new_hunk_start(hunk.header)
    if start_line is None:
        return []

    encoded_path = quote(hunk.filename, safe="/")
    try:
        response = client.get(
            f"/repos/{repository}/contents/{encoded_path}",
            params={"ref": commit_sha},
        )
        if response.status_code != 200:
            return []
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return []

    if payload.get("type") != "file" or payload.get("encoding") != "base64" or not payload.get("content"):
        return []

    try:
        source = base64.b64decode(payload["content"], validate=False).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return []

    source_lines = source.splitlines()
    if not source_lines:
        return []

    window_start = max(1, start_line - 5)
    window_end = min(len(source_lines), start_line + max(10, len(hunk.added_lines) + 6))
    changed_span_end = start_line + max(1, len(hunk.added_lines)) - 1

    return [
        RepositorySourceLine(
            line_number=line_number,
            content=source_lines[line_number - 1][:320],
            in_hunk=start_line <= line_number <= changed_span_end,
        )
        for line_number in range(window_start, window_end + 1)
    ]


def _correlation_score(
    record: IncidentRecord,
    message: str,
    filenames: list[str],
    suspicious_hunks: list[RepositoryDiffHunkEvidence] | None = None,
) -> float:
    incident_tokens = _incident_tokens(record)
    candidate_tokens = _tokens(" ".join([message, *filenames]))
    base_score, _ = _token_score(incident_tokens, candidate_tokens)

    if suspicious_hunks:
        top_hunk = suspicious_hunks[0].correlation_score
        return round(max(base_score, min(1.0, top_hunk * 0.95)), 3)
    return base_score


def _request_json(client: httpx.Client, path: str, *, params: dict[str, Any] | None = None) -> Any:
    try:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GitHubContextUnavailable(f"GitHub context request failed: {type(exc).__name__}") from exc


def collect_repository_context(
    record: IncidentRecord,
    *,
    max_commits: int | None = None,
    max_issues: int | None = None,
) -> RepositoryContext:
    repository = normalize_repo(record.incident.repo or "")
    if not repository:
        raise GitHubContextUnavailable("No repository is attached to this incident.")
    if not repository_allowed(repository):
        raise GitHubContextUnavailable("Repository is not in the configured GitHub allowlist.")

    commit_limit = max(1, min(max_commits or int(os.getenv("GITHUB_CONTEXT_MAX_COMMITS", "5")), 10))
    issue_limit = max(1, min(max_issues or int(os.getenv("GITHUB_CONTEXT_MAX_ISSUES", "5")), 10))
    token = github_token()

    with httpx.Client(
        base_url=GITHUB_API,
        headers=github_headers(token=token),
        timeout=10.0,
        follow_redirects=True,
    ) as client:
        repository_payload = _request_json(client, f"/repos/{repository}")
        commits_payload = _request_json(
            client,
            f"/repos/{repository}/commits",
            params={"per_page": commit_limit},
        )
        issues_payload = _request_json(
            client,
            f"/repos/{repository}/issues",
            params={"state": "open", "per_page": issue_limit * 2, "sort": "updated"},
        )

        commits: list[RepositoryCommitEvidence] = []
        for item in commits_payload[:commit_limit]:
            sha = item.get("sha", "")
            if not sha:
                continue
            detail = _request_json(client, f"/repos/{repository}/commits/{sha}")
            raw_files = detail.get("files", [])[:12]
            files = [
                RepositoryFileChange(
                    filename=file.get("filename", "unknown"),
                    status=file.get("status", "modified"),
                    additions=int(file.get("additions", 0) or 0),
                    deletions=int(file.get("deletions", 0) or 0),
                    changes=int(file.get("changes", 0) or 0),
                )
                for file in raw_files
            ]
            suspicious_hunks: list[RepositoryDiffHunkEvidence] = []
            for file in raw_files:
                suspicious_hunks.extend(
                    _parse_patch_hunks(
                        record,
                        file.get("filename", "unknown"),
                        file.get("patch", "") or "",
                    )
                )
            suspicious_hunks.sort(key=lambda hunk: hunk.correlation_score, reverse=True)
            suspicious_hunks = suspicious_hunks[:6]

            commit_info = detail.get("commit", {})
            author_info = commit_info.get("author", {}) or {}
            message = str(commit_info.get("message", "")).split("\n", 1)[0]
            filenames = [file.filename for file in files]
            commits.append(
                RepositoryCommitEvidence(
                    sha=sha,
                    short_sha=sha[:7],
                    message=message or "No commit message",
                    author=author_info.get("name") or (detail.get("author") or {}).get("login") or "unknown",
                    authored_at=author_info.get("date"),
                    url=detail.get("html_url") or item.get("html_url") or f"https://github.com/{repository}/commit/{sha}",
                    files=files,
                    suspicious_hunks=suspicious_hunks,
                    correlation_score=_correlation_score(record, message, filenames, suspicious_hunks),
                )
            )

        commits.sort(
            key=lambda commit: (commit.correlation_score, commit.authored_at or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )

        # Source reads are deliberately bounded: only the two highest-ranked hunks
        # from the highest-ranked commit receive surrounding source context.
        if commits:
            top_commit = commits[0]
            for hunk in top_commit.suspicious_hunks[:2]:
                hunk.source_context = _fetch_source_context(client, repository, top_commit.sha, hunk)

    open_issues: list[RepositoryIssueEvidence] = []
    for item in issues_payload:
        if "pull_request" in item:
            continue
        open_issues.append(
            RepositoryIssueEvidence(
                number=int(item.get("number", 0)),
                title=item.get("title", "Untitled issue"),
                state=item.get("state", "open"),
                url=item.get("html_url", f"https://github.com/{repository}/issues"),
                labels=[label.get("name", "") for label in item.get("labels", []) if label.get("name")],
            )
        )
        if len(open_issues) >= issue_limit:
            break

    notes = [
        "Commit and diff-hunk correlation are deterministic relevance signals, not proof of causation.",
        "Repository context and source-context collection are read-only; no GitHub resource is modified during investigation.",
        "Source context is bounded to the highest-ranked hunks to control latency and API usage.",
        "GitHub may omit patch/content data for binary or very large files; unavailable evidence is never invented.",
    ]
    if not commits:
        notes.append("No recent commits were returned by GitHub.")

    return RepositoryContext(
        repository=repository,
        default_branch=repository_payload.get("default_branch", "main"),
        fetched_at=datetime.now(timezone.utc),
        authenticated=bool(token),
        source="github-live",
        commits=commits,
        open_issues=open_issues,
        notes=notes,
    )
