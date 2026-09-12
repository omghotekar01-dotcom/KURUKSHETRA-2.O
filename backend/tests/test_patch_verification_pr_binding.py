import pytest

from app.services.patch_verification import PatchVerificationUnavailable, _validate_pr_binding


def test_validate_pr_binding_accepts_matching_open_pr() -> None:
    _validate_pr_binding(
        {"number": 17, "state": "open", "head": {"sha": "abc123"}},
        commit_sha="abc123",
        draft_pr_number=17,
    )


def test_validate_pr_binding_rejects_closed_pr() -> None:
    with pytest.raises(PatchVerificationUnavailable, match="no longer open"):
        _validate_pr_binding(
            {"number": 17, "state": "closed", "head": {"sha": "abc123"}},
            commit_sha="abc123",
            draft_pr_number=17,
        )
