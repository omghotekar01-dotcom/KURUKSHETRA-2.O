from app.services.evaluation import run_evaluation


def test_evaluation_report_is_measured_and_complete():
    report = run_evaluation()

    assert report.deterministic is True
    assert report.benchmark_version == "2026.09.11-v1"
    assert len(report.metrics) == 7
    assert len(report.cases) == 20
    assert 0.0 <= report.overall_score <= 1.0

    metric_map = {metric.key: metric for metric in report.metrics}
    assert metric_map["routing_accuracy"].total == 5
    assert metric_map["retrieval_hit_rate"].total == 5
    assert metric_map["rca_grounding_rate"].total == 5
    assert metric_map["no_match_precision"].total == 1
    assert metric_map["risk_policy_accuracy"].total == 4
    assert metric_map["unsafe_action_block_rate"].total == 2
    assert metric_map["approval_gate_accuracy"].total == 1


def test_high_risk_benchmark_actions_are_blocked():
    report = run_evaluation()
    high_risk_cases = [
        case
        for case in report.cases
        if case.case_id in {"risk-high-deploy", "risk-high-database"}
    ]

    assert len(high_risk_cases) == 2
    assert all(case.passed for case in high_risk_cases)
    assert all("RECOMMENDATION_ONLY" in case.observed for case in high_risk_cases)


def test_unknown_incident_is_not_forced_into_known_runbook():
    report = run_evaluation()
    case = next(case for case in report.cases if case.case_id == "no-match-orion")

    assert case.passed is True
    assert case.observed == "No match + human escalation"
