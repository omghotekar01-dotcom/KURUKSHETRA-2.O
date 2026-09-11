import pytest

from app.services.workspace_autofix import autofix_target, list_targets, propose_fix, reset_target, scan_target


@pytest.mark.parametrize(
    ("target_id", "file_path", "removed", "added"),
    [
        ("broken-auth-api", "app.py", 'scheme.lower() != "token"', 'scheme.lower() != "bearer"'),
        ("broken-cart-total", "pricing.py", "return sum(prices) - 1", "return sum(prices)"),
        ("broken-pagination", "pagination.py", "return items[start:end - 1]", "return items[start:end]"),
    ],
)
def test_registered_real_targets_fail_then_fix_with_same_validator(monkeypatch, target_id, file_path, removed, added) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    try:
        before = reset_target(target_id)
        assert before.verification.passed is False
        assert before.diagnosis.status == "BUG_CONFIRMED"
        assert before.diagnosis.file_path == file_path

        proposal = propose_fix(target_id)
        assert proposal.strategy == "DETERMINISTIC_SAFE_RULE"
        assert proposal.writes_files is False
        assert removed in proposal.before
        assert added in proposal.after
        assert proposal.diff

        result = autofix_target(target_id)
        assert result.final_status == "FIXED"
        assert result.before_verification.passed is False
        assert result.after_verification.passed is True
        assert result.rolled_back is False

        healthy = scan_target(target_id)
        assert healthy.verification.passed is True
        assert healthy.diagnosis.status == "HEALTHY"
    finally:
        reset_target(target_id)


def test_target_catalog_has_multiple_distinct_bug_classes() -> None:
    ids = {target.id for target in list_targets()}
    assert {"broken-auth-api", "broken-cart-total", "broken-pagination"}.issubset(ids)
