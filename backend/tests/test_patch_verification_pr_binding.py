import pytest

from app.services.patch_verification import PatchVerificationUnavailable, _validate_pr_binding


def _bound_pr(*, state: str = "open", draft: bool = True, head_sha: str = "abc123") -> dict:
    return {
        "number": 17,
        "state": state,
        "draft": draft,
        "head": {
            "sha": head_sha,
            "ref": "incident-fix/inc-test123-patch-abc123",
            "repo": {"full_name": "example/repo"},
        },
        "base": {"ref": "main", "repo": {"full_name": "example/repo"}},
    }


def test_validate_pr_binding_accepts_matching_open_draft_pr() -> None:
    _validate_pr_binding(
        _bound_pr(),
        commit_sha="abc123",
        draft_pr_number=17,
    )


def test_validate_pr_binding_rejects_closed_pr() -> None:
    with pytest.raises(PatchVerificationUnavailable, match="no longer open"):
        _validate_pr_binding(
            _bound_pr(state="closed"),
            commit_sha="abc123",
            draft_pr_number=17,
        )
