from app.schemas.incident import ProposedAction, RiskLevel
from app.services.risk import evaluate_action


def test_high_risk_action_is_never_auto_executed():
    result = evaluate_action(
        ProposedAction(
            action_type="deploy",
            target="production",
            description="Deploy generated fix to production",
            confidence=0.98,
        )
    )
    assert result.risk == RiskLevel.high
    assert result.policy == "RECOMMENDATION_ONLY"
    assert result.requires_human_approval is True


def test_low_risk_read_only_action_can_be_allowed():
    result = evaluate_action(
        ProposedAction(
            action_type="read",
            target="runbook",
            description="Retrieve matching historical incident",
            confidence=0.9,
        )
    )
    assert result.risk == RiskLevel.low
    assert result.policy == "ALLOWED"
    assert result.requires_human_approval is False
