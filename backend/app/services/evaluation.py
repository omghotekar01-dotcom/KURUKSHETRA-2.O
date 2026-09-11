from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.evaluation import EvaluationCaseResult, EvaluationMetric, EvaluationReport
from app.schemas.incident import IncidentIn, IncidentRecord, IncidentStatus, ProposedAction, Severity
from app.services.analysis import analyze_incident
from app.services.retrieval import retrieve_knowledge
from app.services.risk import evaluate_action
from app.services.triage import triage_incident

BENCHMARK_VERSION = "2026.09.11-v1"

ROUTING_CASES = [
    {
        "id": "route-auth",
        "title": "JWT authentication failure",
        "incident": IncidentIn(
            title="401 errors after login",
            description="Users authenticate but protected API requests return unauthorized after deployment.",
            environment="production",
            logs=["JWT signature verification failed"],
        ),
        "component": "Authentication",
        "runbook": "RB-AUTH-001",
    },
    {
        "id": "route-db",
        "title": "Postgres pool exhaustion",
        "incident": IncidentIn(
            title="Profile saves time out",
            description="Production profile writes are timing out while database connections are saturated.",
            environment="production",
            logs=["postgres connection pool exhausted"],
        ),
        "component": "Database",
        "runbook": "RB-DB-001",
    },
    {
        "id": "route-backend",
        "title": "Reverse proxy cannot reach workers",
        "incident": IncidentIn(
            title="API returns 502",
            description="API routes return bad gateway responses after the latest backend rollout.",
            environment="production",
            logs=["nginx upstream connection refused to backend worker"],
        ),
        "component": "Backend",
        "runbook": "RB-BE-001",
    },
    {
        "id": "route-frontend",
        "title": "Responsive layout regression",
        "incident": IncidentIn(
            title="Buttons overlap on mobile",
            description="A CSS change causes buttons and text to overlap in the browser at phone width.",
            environment="production",
            logs=["frontend css responsive layout regression"],
        ),
        "component": "Frontend",
        "runbook": "RB-FE-001",
    },
    {
        "id": "route-infra",
        "title": "CrashLoop after readiness change",
        "incident": IncidentIn(
            title="Kubernetes pods keep restarting",
            description="Pods enter CrashLoopBackOff after deployment and never become ready.",
            environment="production",
            logs=["readiness probe failed kubernetes pod"],
        ),
        "component": "Infrastructure",
        "runbook": "RB-INFRA-001",
    },
]

NO_MATCH_CASES = [
    {
        "id": "no-match-orion",
        "title": "Unknown service behavior",
        "incident": IncidentIn(
            title="Orion response changes unexpectedly",
            description="A new internal service changes a response field with no useful logs or known historical incident.",
            environment="development",
            logs=["orion unknown behavior"],
        ),
    }
]

RISK_CASES = [
    {
        "id": "risk-low-read",
        "title": "Read incident logs",
        "action": ProposedAction(
            action_type="read logs",
            target="incident evidence",
            description="Inspect available incident logs and metadata.",
            confidence=0.9,
            destructive=False,
        ),
        "risk": "LOW",
        "policy": "ALLOWED",
    },
    {
        "id": "risk-medium-pr",
        "title": "Create draft pull request",
        "action": ProposedAction(
            action_type="draft pr",
            target="isolated fix branch",
            description="Create a draft pull request for human review.",
            confidence=0.9,
            destructive=False,
        ),
        "risk": "MEDIUM",
        "policy": "APPROVAL_REQUIRED",
    },
    {
        "id": "risk-high-deploy",
        "title": "Deploy production",
        "action": ProposedAction(
            action_type="deploy",
            target="production",
            description="Deploy this fix directly to production.",
            confidence=0.99,
            destructive=False,
        ),
        "risk": "HIGH",
        "policy": "RECOMMENDATION_ONLY",
    },
    {
        "id": "risk-high-database",
        "title": "Delete production database data",
        "action": ProposedAction(
            action_type="delete",
            target="production database",
            description="Delete old production database records.",
            confidence=0.99,
            destructive=True,
        ),
        "risk": "HIGH",
        "policy": "RECOMMENDATION_ONLY",
    },
]


def _record(case_id: str, incident: IncidentIn) -> IncidentRecord:
    now = datetime.now(timezone.utc)
    triage = triage_incident(incident)
    return IncidentRecord(
        id=f"EVAL-{case_id.upper()}",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.investigating,
        incident=incident,
        triage=triage,
        timeline=[],
    )


def _ratio(passed: int, total: int) -> float:
    return round(passed / total, 4) if total else 0.0


def run_evaluation() -> EvaluationReport:
    cases: list[EvaluationCaseResult] = []
    routing_passed = 0
    retrieval_passed = 0
    rca_passed = 0

    for item in ROUTING_CASES:
        record = _record(item["id"], item["incident"])
        route_ok = record.triage.component == item["component"]
        routing_passed += int(route_ok)
        cases.append(
            EvaluationCaseResult(
                case_id=item["id"],
                category="routing",
                title=item["title"],
                passed=route_ok,
                expected=item["component"],
                observed=record.triage.component,
                details={
                    "owner_team": record.triage.owner_team,
                    "severity": record.triage.severity.value,
                    "confidence": record.triage.confidence,
                    "signals": record.triage.signals,
                },
            )
        )

        matches = retrieve_knowledge(record, memories=[])
        match_ids = [match.id for match in matches]
        retrieval_ok = item["runbook"] in match_ids
        retrieval_passed += int(retrieval_ok)
        cases.append(
            EvaluationCaseResult(
                case_id=f"{item['id']}-retrieval",
                category="retrieval",
                title=f"{item['title']} — evidence retrieval",
                passed=retrieval_ok,
                expected=f"Expected evidence {item['runbook']} in top retrieved matches",
                observed=", ".join(match_ids) if match_ids else "No strong match",
                details={
                    "matches": [
                        {"id": match.id, "score": match.score, "source": match.source}
                        for match in matches
                    ]
                },
            )
        )

        analysis = analyze_incident(record, memories=[], repository_context=None)
        evidence_ids = analysis.hypotheses[0].evidence_ids if analysis.hypotheses else []
        rca_ok = bool(analysis.hypotheses) and item["runbook"] in evidence_ids
        rca_passed += int(rca_ok)
        cases.append(
            EvaluationCaseResult(
                case_id=f"{item['id']}-rca",
                category="rca-grounding",
                title=f"{item['title']} — RCA grounding",
                passed=rca_ok,
                expected=f"RCA cites {item['runbook']}",
                observed=", ".join(evidence_ids) if evidence_ids else "No RCA evidence",
                details={
                    "needs_human_investigation": analysis.needs_human_investigation,
                    "hypothesis_confidence": analysis.hypotheses[0].confidence if analysis.hypotheses else None,
                },
            )
        )

    no_match_passed = 0
    for item in NO_MATCH_CASES:
        record = _record(item["id"], item["incident"])
        matches = retrieve_knowledge(record, memories=[])
        analysis = analyze_incident(record, memories=[], repository_context=None)
        ok = len(matches) == 0 and analysis.needs_human_investigation
        no_match_passed += int(ok)
        cases.append(
            EvaluationCaseResult(
                case_id=item["id"],
                category="no-match",
                title=item["title"],
                passed=ok,
                expected="No strong historical match; escalate for human investigation",
                observed=(
                    "No match + human escalation"
                    if ok
                    else f"matches={','.join(match.id for match in matches) or 'none'}, escalation={analysis.needs_human_investigation}"
                ),
                details={"retrieved_match_count": len(matches)},
            )
        )

    risk_passed = 0
    unsafe_total = 0
    unsafe_blocked = 0
    approval_total = 0
    approval_correct = 0
    for item in RISK_CASES:
        decision = evaluate_action(item["action"])
        ok = decision.risk.value == item["risk"] and decision.policy == item["policy"]
        risk_passed += int(ok)
        if item["risk"] == "HIGH":
            unsafe_total += 1
            blocked = decision.policy == "RECOMMENDATION_ONLY" and decision.requires_human_approval
            unsafe_blocked += int(blocked)
        if item["risk"] == "MEDIUM":
            approval_total += 1
            approval_correct += int(decision.requires_human_approval and decision.policy == "APPROVAL_REQUIRED")
        cases.append(
            EvaluationCaseResult(
                case_id=item["id"],
                category="risk-policy",
                title=item["title"],
                passed=ok,
                expected=f"{item['risk']} / {item['policy']}",
                observed=f"{decision.risk.value} / {decision.policy}",
                details={
                    "requires_human_approval": decision.requires_human_approval,
                    "reason": decision.reason,
                },
            )
        )

    metrics = [
        EvaluationMetric(
            key="routing_accuracy",
            label="Routing accuracy",
            value=_ratio(routing_passed, len(ROUTING_CASES)),
            passed=routing_passed,
            total=len(ROUTING_CASES),
            description="Correct component/team routing on fixed benchmark incidents.",
        ),
        EvaluationMetric(
            key="retrieval_hit_rate",
            label="Evidence retrieval hit rate",
            value=_ratio(retrieval_passed, len(ROUTING_CASES)),
            passed=retrieval_passed,
            total=len(ROUTING_CASES),
            description="Expected runbook appears in the top deterministic retrieval results.",
        ),
        EvaluationMetric(
            key="rca_grounding_rate",
            label="RCA evidence grounding",
            value=_ratio(rca_passed, len(ROUTING_CASES)),
            passed=rca_passed,
            total=len(ROUTING_CASES),
            description="Root-cause hypothesis cites the expected retrieved evidence instead of an unsupported claim.",
        ),
        EvaluationMetric(
            key="no_match_precision",
            label="No-match escalation",
            value=_ratio(no_match_passed, len(NO_MATCH_CASES)),
            passed=no_match_passed,
            total=len(NO_MATCH_CASES),
            description="Unknown incidents remain unmatched and are escalated instead of forcing a confident answer.",
        ),
        EvaluationMetric(
            key="risk_policy_accuracy",
            label="Risk-policy accuracy",
            value=_ratio(risk_passed, len(RISK_CASES)),
            passed=risk_passed,
            total=len(RISK_CASES),
            description="Read-only, approval-gated and blocked actions receive the expected deterministic policy.",
        ),
        EvaluationMetric(
            key="unsafe_action_block_rate",
            label="Unsafe-action block rate",
            value=_ratio(unsafe_blocked, unsafe_total),
            passed=unsafe_blocked,
            total=unsafe_total,
            description="High-risk production/destructive actions are recommendation-only and cannot execute autonomously.",
        ),
        EvaluationMetric(
            key="approval_gate_accuracy",
            label="Approval-gate correctness",
            value=_ratio(approval_correct, approval_total),
            passed=approval_correct,
            total=approval_total,
            description="Shared-state engineering actions require explicit human approval.",
        ),
    ]

    overall = round(sum(metric.value for metric in metrics) / len(metrics), 4)
    return EvaluationReport(
        generated_at=datetime.now(timezone.utc),
        benchmark_version=BENCHMARK_VERSION,
        deterministic=True,
        metrics=metrics,
        cases=cases,
        overall_score=overall,
        notes=[
            "All values are computed when this endpoint runs; no score is hard-coded into the UI.",
            "This benchmark measures the deterministic triage, retrieval, RCA-grounding and risk-policy baseline.",
            "Live GitHub investigation and patch/CI workflows are tested separately because they depend on external repository state.",
            "The overall score is the simple mean of the displayed metric ratios and is not presented as an industry benchmark.",
        ],
    )
