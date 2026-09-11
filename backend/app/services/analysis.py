from __future__ import annotations

from app.schemas.incident import (
    AnalysisBundle,
    EvidenceBundle,
    IncidentRecord,
    ProposedAction,
    RemediationPlan,
    RepositoryContext,
    ResolutionMemory,
    RootCauseHypothesis,
)
from app.services.github_client import configured_repository
from app.services.retrieval import retrieve_knowledge
from app.services.risk import evaluate_action


NEXT_DIAGNOSTIC = {
    "Authentication": "Compare the runtime signing/auth configuration with the latest deployment configuration.",
    "Database": "Inspect connection saturation, query plan, and recent schema/configuration changes.",
    "Backend": "Check application worker health, upstream connectivity, and recent backend changes.",
    "Frontend": "Reproduce the regression at the affected viewport and compare the latest UI changes.",
    "Infrastructure": "Inspect workload events, health checks, resource pressure, and the latest rollout.",
}

VERIFICATION = {
    "Authentication": "Run an authenticated request and confirm the protected endpoint returns the expected success response.",
    "Database": "Repeat the failing database-backed request and confirm latency/errors return to the expected range.",
    "Backend": "Call the health endpoint through the normal proxy path and verify the failing API request succeeds.",
    "Frontend": "Reproduce the affected user flow at the failing viewport and verify the visual regression is gone.",
    "Infrastructure": "Confirm healthy replicas remain stable and the affected service passes its health checks.",
}


def _best_repository_commit(repository_context: RepositoryContext | None):
    if repository_context is None or not repository_context.commits:
        return None
    candidate = repository_context.commits[0]
    return candidate if candidate.correlation_score >= 0.12 else None


def _best_diff_hunk(repository_candidate):
    if repository_candidate is None or not repository_candidate.suspicious_hunks:
        return None
    candidate = repository_candidate.suspicious_hunks[0]
    return candidate if candidate.correlation_score >= 0.12 else None


def _ownership_context(repository_context: RepositoryContext | None) -> tuple[str, str | None]:
    if repository_context is None or not repository_context.suggested_owners:
        return "", None
    owners = ", ".join(repository_context.suggested_owners[:6])
    source = repository_context.ownership_source or "repository ownership metadata"
    note = (
        f" Repository ownership metadata from {source} suggests {owners} as routing/review candidates for the highest-ranked changed files. "
        "Ownership metadata is advisory and does not grant authorization."
    )
    step = f"Route code review/investigation to repository owner candidate(s): {owners}."
    return note, step


def _github_issue_action(record: IncidentRecord, confidence: float) -> ProposedAction:
    target = record.incident.repo or configured_repository()
    return ProposedAction(
        action_type="create github issue",
        target=target,
        description=(
            "Create a GitHub incident issue containing the evidence-backed RCA, approved remediation, "
            "repository and diff evidence, and verification plan for human tracking."
        ),
        confidence=confidence,
        destructive=False,
    )


def analyze_incident(
    record: IncidentRecord,
    memories: list[ResolutionMemory] | None = None,
    repository_context: RepositoryContext | None = None,
) -> AnalysisBundle:
    matches = retrieve_knowledge(record, memories=memories)
    evidence = EvidenceBundle(
        incident_id=record.id,
        matches=matches,
        no_strong_match=len(matches) == 0,
    )
    repository_candidate = _best_repository_commit(repository_context)
    diff_candidate = _best_diff_hunk(repository_candidate)
    ownership_note, ownership_step = _ownership_context(repository_context)

    if not matches and repository_candidate is None:
        return AnalysisBundle(
            incident_id=record.id,
            evidence=evidence,
            repository_context=repository_context,
            hypotheses=[],
            remediation=None,
            needs_human_investigation=True,
        )

    if matches:
        top = matches[0]
        supporting = matches[:2]
        confidence = min(0.92, round(0.48 + (top.score * 0.5), 2))
        evidence_ids = [match.id for match in supporting]
        rationale = (
            f"The strongest knowledge match is {top.id} ({top.score:.0%}, source: {top.source}) "
            f"and it aligns with the incident's {record.triage.component} triage signals."
        )
        next_diagnostic = NEXT_DIAGNOSTIC.get(
            record.triage.component,
            "Collect one more direct diagnostic signal before taking a consequential action.",
        )

        if repository_candidate is not None:
            evidence_ids.append(f"GH-COMMIT-{repository_candidate.short_sha}")
            confidence = min(0.94, round(confidence + repository_candidate.correlation_score * 0.08, 2))
            changed_files = ", ".join(file.filename for file in repository_candidate.files[:4]) or "no file list returned"
            rationale += (
                f" Live GitHub evidence also identifies recent commit {repository_candidate.short_sha} "
                f"('{repository_candidate.message}') with a {repository_candidate.correlation_score:.0%} "
                f"incident-correlation signal across changed files: {changed_files}. "
                "This is supporting evidence, not proof of causation."
            )
            next_diagnostic = (
                f"Inspect commit {repository_candidate.short_sha} and reproduce the failure against its changed files "
                "before accepting the root-cause hypothesis."
            )

        if diff_candidate is not None:
            evidence_ids.append(f"GH-HUNK-{repository_candidate.short_sha}-{diff_candidate.filename}")
            confidence = min(0.95, round(confidence + diff_candidate.correlation_score * 0.05, 2))
            terms = ", ".join(diff_candidate.matched_terms[:6]) or "incident-related terms"
            rationale += (
                f" The most relevant live diff hunk is in {diff_candidate.filename} ({diff_candidate.header}) "
                f"with a {diff_candidate.correlation_score:.0%} hunk-correlation signal and matched terms: {terms}. "
                "The hunk is prioritized for inspection; it is not automatically declared faulty."
            )
            next_diagnostic = (
                f"Inspect the ranked diff hunk in {diff_candidate.filename} at {diff_candidate.header}, reproduce the failure, "
                "and compare behavior with the parent revision before preparing a patch."
            )

        rationale += ownership_note
        hypothesis = RootCauseHypothesis(
            id="HYP-001",
            title=top.issue,
            confidence=confidence,
            evidence_ids=evidence_ids,
            rationale=rationale,
            next_diagnostic=next_diagnostic,
        )
        remediation_summary = top.fix
        remediation_steps = [
            "Confirm the top hypothesis with the next diagnostic check.",
            top.fix,
        ]
        if ownership_step:
            remediation_steps.append(ownership_step)
        remediation_steps.extend(
            [
                "Create a tracked GitHub incident issue after explicit human approval.",
                "Run the defined verification before marking the incident resolved.",
            ]
        )
    else:
        assert repository_candidate is not None
        confidence = round(min(0.72, 0.42 + repository_candidate.correlation_score * 0.3), 2)
        changed_files = ", ".join(file.filename for file in repository_candidate.files[:5]) or "the files changed by the commit"
        evidence_ids = [f"GH-COMMIT-{repository_candidate.short_sha}"]
        rationale = (
            f"No sufficiently strong historical runbook match was found, but live GitHub evidence shows commit "
            f"{repository_candidate.short_sha} with a {repository_candidate.correlation_score:.0%} correlation "
            f"signal to the incident across {changed_files}. The system treats this as a candidate, not a confirmed cause."
        )
        next_diagnostic = (
            f"Review the diff for commit {repository_candidate.short_sha}, reproduce the incident on the parent revision, "
            "and compare behavior before making a code change."
        )

        if diff_candidate is not None:
            evidence_ids.append(f"GH-HUNK-{repository_candidate.short_sha}-{diff_candidate.filename}")
            confidence = round(min(0.78, confidence + diff_candidate.correlation_score * 0.08), 2)
            terms = ", ".join(diff_candidate.matched_terms[:6]) or "incident-related terms"
            rationale += (
                f" Its highest-ranked diff hunk is {diff_candidate.filename} {diff_candidate.header}, "
                f"scoring {diff_candidate.correlation_score:.0%} against the incident and matching: {terms}."
            )
            next_diagnostic = (
                f"Inspect {diff_candidate.filename} at {diff_candidate.header}, reproduce the failure against the current and "
                "parent revisions, and confirm whether that exact change alters the failing behavior."
            )

        rationale += ownership_note
        hypothesis = RootCauseHypothesis(
            id="HYP-REPO-001",
            title=f"Recent code change may be related: {repository_candidate.message}",
            confidence=confidence,
            evidence_ids=evidence_ids,
            rationale=rationale,
            next_diagnostic=next_diagnostic,
        )
        remediation_summary = (
            f"Investigate commit {repository_candidate.short_sha} and isolate the smallest reversible change that restores "
            "the failing behavior; do not revert or deploy automatically."
        )
        remediation_steps = [
            f"Inspect commit {repository_candidate.short_sha} and the correlated changed files.",
            "Inspect the highest-ranked diff hunk before touching unrelated files.",
            "Reproduce the failure on the current revision and compare with the previous revision.",
        ]
        if ownership_step:
            remediation_steps.append(ownership_step)
        remediation_steps.extend(
            [
                "Prepare the smallest bounded correction only after the hypothesis is confirmed.",
                "Create a tracked GitHub incident issue after explicit human approval.",
                "Run the defined verification before marking the incident resolved.",
            ]
        )

    action = _github_issue_action(record, hypothesis.confidence)
    risk = evaluate_action(action)
    remediation = RemediationPlan(
        summary=remediation_summary,
        steps=remediation_steps,
        verification=VERIFICATION.get(
            record.triage.component,
            "Repeat the original failing workflow and confirm the expected behavior is restored.",
        ),
        proposed_action=action,
        risk=risk,
    )

    return AnalysisBundle(
        incident_id=record.id,
        evidence=evidence,
        repository_context=repository_context,
        hypotheses=[hypothesis],
        remediation=remediation,
        needs_human_investigation=False,
    )
