from __future__ import annotations

from app.schemas.incident import ProposedAction, RiskDecision, RiskLevel


HIGH_RISK_TOKENS = (
    "merge",
    "deploy",
    "production database",
    "delete",
    "drop table",
    "iam",
    "rotate secret",
    "restart production",
)
MEDIUM_RISK_TOKENS = (
    "create branch",
    "create github issue",
    "create issue",
    "github issue",
    "apply patch",
    "draft pr",
    "pull request",
    "run test",
    "send slack",
    "send email",
)


def evaluate_action(action: ProposedAction) -> RiskDecision:
    haystack = f"{action.action_type} {action.target} {action.description}".lower()

    if action.destructive or any(token in haystack for token in HIGH_RISK_TOKENS):
        return RiskDecision(
            risk=RiskLevel.high,
            policy="RECOMMENDATION_ONLY",
            reason="The action can directly change a protected or production resource.",
            requires_human_approval=True,
        )

    if any(token in haystack for token in MEDIUM_RISK_TOKENS):
        return RiskDecision(
            risk=RiskLevel.medium,
            policy="APPROVAL_REQUIRED",
            reason="The action changes shared engineering state but remains bounded and reversible.",
            requires_human_approval=True,
        )

    if action.confidence < 0.5:
        return RiskDecision(
            risk=RiskLevel.medium,
            policy="INVESTIGATE_MORE",
            reason="Confidence is too low for unattended execution.",
            requires_human_approval=True,
        )

    return RiskDecision(
        risk=RiskLevel.low,
        policy="ALLOWED",
        reason="The action is read-only or low-impact and sufficiently confident.",
        requires_human_approval=False,
    )