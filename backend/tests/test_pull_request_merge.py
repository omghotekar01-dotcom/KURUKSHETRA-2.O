import pytest

from app.services.pull_request_merge import (
    PatchMergeUnavailable,
    _require_matching_open_pr,
    _require_merge_confirmation,
)


def test_merge_requires_exact_human_confirmation():
    _require_merge_confirmation("MERGE")
    _require_merge_confirmation(" merge ")

    with pytest.raises(PatchMergeUnavailable, match="exactly MERGE"):
        _require_merge_confirmation("YES")


def test_merge_rejects_closed_pull_request():
    with pytest.raises(PatchMergeUnavailable, match="no longer open"):
        _require_matching_open_pr(
            {"state": "closed", "head": {"sha": "abc123"}},
            expected_commit_sha="abc123",
        )


def test_merge_rejects_head_sha_change_after_review():
    with pytest.raises(PatchMergeUnavailable, match="head changed"):
        _require_matching_open_pr(
            {"state": "open", "head": {"sha": "new-sha"}},
            expected_commit_sha="reviewed-sha",
        )


def test_merge_accepts_only_exact_open_reviewed_head():
    _require_matching_open_pr(
        {"state": "open", "head": {"sha": "reviewed-sha"}},
        expected_commit_sha="reviewed-sha",
    )
