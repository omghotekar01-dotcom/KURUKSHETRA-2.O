from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.schemas.incident import (
    IncidentRecord,
    RepositoryCommitEvidence,
    RepositoryContext,
    RepositoryDiffHunkEvidence,
    RepositoryFileChange,
    RepositoryIssueEvidence,
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

    commits.sort(key=lambda commit: (commit.correlation_score, commit.authored_at or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)

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
        "Repository context is read-only; no GitHub resource is modified during investigation.",
        "GitHub may omit patch text for binary files or very large diffs; missing patch text is treated as unavailable evidence, never invented.",
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
