from __future__ import annotations

import os
from hashlib import sha256

from app.schemas.incident import (
    IncidentRecord,
    PatchProposal,
    PatchProposalRequest,
    RepositoryCommitEvidence,
    RepositoryContext,
    RepositoryDiffHunkEvidence,
)


class PatchProposalUnavailable(RuntimeError):
    pass


def _find_selected_hunk(
    context: RepositoryContext,
    request: PatchProposalRequest,
) -> tuple[RepositoryCommitEvidence, RepositoryDiffHunkEvidence]:
    commit = next((item for item in context.commits if item.sha == request.commit_sha), None)
    if commit is None:
        raise PatchProposalUnavailable("Selected commit is not present in the current live repository evidence.")

    hunk = next(
        (
            item
            for item in commit.suspicious_hunks
            if item.filename == request.filename and item.header == request.hunk_header
        ),
        None,
    )
    if hunk is None:
        raise PatchProposalUnavailable("Selected diff hunk is not present in the current live repository evidence.")
    return commit, hunk


def _minimum_correlation() -> float:
    try:
        raw = float(os.getenv("PATCH_PROPOSAL_MIN_CORRELATION", "0.18"))
    except ValueError:
        raw = 0.18
    return max(0.0, min(1.0, raw))


def _sequence_start(source_lines: list[str], target_lines: list[str]) -> int | None:
    if not target_lines or len(target_lines) > len(source_lines):
        return None
    for index in range(0, len(source_lines) - len(target_lines) + 1):
        if source_lines[index : index + len(target_lines)] == target_lines:
            return index
    return None


def _verification_commands(filename: str) -> list[str]:
    lowered = filename.lower()
    if lowered.startswith("frontend/") or lowered.endswith((".ts", ".tsx", ".js", ".jsx")):
        return [
            "cd frontend && npm ci --no-audit --no-fund && npm run build",
        ]
    if lowered.startswith("backend/") or lowered.endswith(".py"):
        return [
            "cd backend && python -m compileall -q app tests",
            "cd backend && python -m pytest -q",
        ]
    return [
        "Run the repository's normal targeted tests for the changed file.",
        "Run the repository's full build or regression suite before opening a PR.",
    ]


def _diff_preview(filename: str, before_lines: list[str], after_lines: list[str], line_start: int) -> str:
    body: list[str] = [
        f"--- a/{filename}",
        f"+++ b/{filename}",
        f"@@ bounded proposal near line {line_start} @@",
    ]
    body.extend(f"-{line}" for line in before_lines)
    body.extend(f"+{line}" for line in after_lines)
    return "\n".join(body)


def build_patch_proposal(
    incident: IncidentRecord,
    context: RepositoryContext,
    request: PatchProposalRequest,
) -> PatchProposal:
    commit, hunk = _find_selected_hunk(context, request)

    minimum_correlation = _minimum_correlation()
    if hunk.correlation_score < minimum_correlation:
        raise PatchProposalUnavailable(
            f"The selected hunk is only {hunk.correlation_score:.0%} correlated with the incident; "
            f"the safety threshold is {minimum_correlation:.0%}. Investigate manually or collect stronger evidence."
        )

    # This stage is intentionally conservative. It proposes only a mechanical
    # reversal of a suspicious hunk that GitHub says is currently present at the
    # selected commit. No repository mutation happens here.
    if not hunk.added_lines:
        raise PatchProposalUnavailable(
            "A safe exact proposal cannot be prepared because this hunk has no current added-line sequence to replace."
        )
    if not hunk.source_context:
        raise PatchProposalUnavailable(
            "A safe exact proposal cannot be prepared because bounded source context is unavailable for this hunk."
        )

    source_contents = [line.content for line in hunk.source_context]
    local_index = _sequence_start(source_contents, hunk.added_lines)
    if local_index is None:
        raise PatchProposalUnavailable(
            "The current source context no longer contains the exact added-line sequence from this diff hunk. Refresh live evidence before proposing a patch."
        )

    line_start = hunk.source_context[local_index].line_number
    before_lines = list(hunk.added_lines)
    after_lines = list(hunk.removed_lines)
    proposal_seed = "|".join(
        [incident.id, context.repository, commit.sha, hunk.filename, hunk.header, *before_lines, "=>", *after_lines]
    )
    proposal_id = f"PATCH-{sha256(proposal_seed.encode('utf-8')).hexdigest()[:12].upper()}"

    confidence = round(min(0.78, 0.36 + (hunk.correlation_score * 0.38) + (0.05 if hunk.matched_terms else 0.0)), 2)
    matched = ", ".join(hunk.matched_terms) if hunk.matched_terms else "the active incident symptoms"
    rationale = (
        f"This proposal is a bounded revert candidate derived from the exact GitHub diff for commit {commit.short_sha}. "
        f"The selected hunk in {hunk.filename} correlated with {matched}. It replaces only the current lines introduced "
        "by that hunk with the lines GitHub reports were removed. This is a reviewable hypothesis, not proof that the change caused the incident."
    )

    warnings = [
        "No branch or repository file has been modified by generating this proposal.",
        f"The hunk passed the configured minimum incident-correlation gate ({minimum_correlation:.0%}).",
        "The proposal mechanically reverts one suspicious hunk; it may not represent the best final fix.",
        "A human must review the exact before/after lines before any write is allowed.",
        "The next stage must apply the proposal on an isolated branch and pass deterministic checks before a draft PR can be created.",
    ]

    return PatchProposal(
        proposal_id=proposal_id,
        incident_id=incident.id,
        repository=context.repository,
        base_commit=commit.sha,
        file_path=hunk.filename,
        hunk_header=hunk.header,
        line_start=line_start,
        before_lines=before_lines,
        after_lines=after_lines,
        diff_preview=_diff_preview(hunk.filename, before_lines, after_lines, line_start),
        rationale=rationale,
        confidence=confidence,
        verification_commands=_verification_commands(hunk.filename),
        warnings=warnings,
        writes_repository=False,
    )
