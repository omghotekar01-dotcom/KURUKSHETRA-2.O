import httpx
import pytest

from app.schemas.incident import VerificationOutcome
from app.schemas.patch import CIVerificationCheck
from app.services.patch_verification import (
    PatchVerificationUnavailable,
    _derive_incident_verification,
    _derive_status,
    _read_all_check_runs,
    _request,
    _validate_pr_binding,
)


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class _FakeClient:
    def __init__(self, outcomes: list[object]):
        self.outcomes = list(outcomes)
        self.calls = 0
        self.paths: list[str] = []

    def get(self, path: str):
        self.calls += 1
        self.paths.append(path)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def test_verification_read_retries_transient_transport_and_server_failures():
    request = httpx.Request("GET", "https://api.github.com/example")
    client = _FakeClient(
        [
            httpx.ConnectError("temporary network failure", request=request),
            _FakeResponse(503, {"message": "Service Unavailable"}),
            _FakeResponse(200, {"ok": True}),
        ]
    )

    assert _request(client, "/example") == {"ok": True}
    assert client.calls == 3


def test_verification_read_does_not_retry_authentication_failure():
    client = _FakeClient([_FakeResponse(401, {"message": "Bad credentials"})])

    with pytest.raises(PatchVerificationUnavailable, match="GitHub returned 401"):
        _request(client, "/example")

    assert client.calls == 1


def test_check_run_reader_collects_all_pages_before_deriving_ci_state():
    first_page = [
        {"name": f"check-{index}", "status": "completed", "conclusion": "success"}
        for index in range(100)
    ]
    final_failure = {"name": "security-final", "status": "completed", "conclusion": "failure"}
    client = _FakeClient(
        [
            _FakeResponse(200, {"total_count": 101, "check_runs": first_page}),
            _FakeResponse(200, {"total_count": 101, "check_runs": [final_failure]}),
        ]
    )

    runs = _read_all_check_runs(client, "example/repo", "abc123")

    assert len(runs) == 101
    assert runs[-1]["name"] == "security-final"
    assert client.calls == 2
    assert "per_page=100&page=1" in client.paths[0]
    assert "per_page=100&page=2" in client.paths[1]


def test_check_run_reader_fails_closed_on_incomplete_pagination():
    first_page = [
        {"name": f"check-{index}", "status": "completed", "conclusion": "success"}
        for index in range(100)
    ]
    client = _FakeClient(
        [
            _FakeResponse(200, {"total_count": 101, "check_runs": first_page}),
            _FakeResponse(200, {"total_count": 101, "check_runs": []}),
        ]
    )

    with pytest.raises(PatchVerificationUnavailable, match="pagination was incomplete"):
        _read_all_check_runs(client, "example/repo", "abc123")


def test_check_run_reader_rejects_pagination_count_drift():
    client = _FakeClient(
        [
            _FakeResponse(
                200,
                {
                    "total_count": 1,
                    "check_runs": [
                        {"name": "backend", "status": "completed", "conclusion": "success"},
                        {"name": "frontend", "status": "completed", "conclusion": "success"},
                    ],
                },
            )
        ]
    )

    with pytest.raises(PatchVerificationUnavailable, match="pagination changed"):
        _read_all_check_runs(client, "example/repo", "abc123")


def test_ci_verification_passes_when_all_checks_succeed():
    status, message = _derive_status(
        [
            CIVerificationCheck(name="backend", status="completed", conclusion="success"),
            CIVerificationCheck(name="frontend", status="completed", conclusion="success"),
        ],
        "success",
    )
    assert status == "PASS"
    assert "Human review" in message


def test_ci_verification_fails_on_failed_check():
    status, _ = _derive_status(
        [CIVerificationCheck(name="backend", status="completed", conclusion="failure")],
        "failure",
    )
    assert status == "FAIL"


def test_ci_verification_stays_pending_while_checks_run():
    status, _ = _derive_status(
        [CIVerificationCheck(name="frontend", status="in_progress", conclusion=None)],
        "pending",
    )
    assert status == "PENDING"


def test_ci_verification_reports_no_checks_instead_of_inventing_success():
    status, message = _derive_status([], "")
    assert status == "NO_CHECKS"
    assert "No completed GitHub CI" in message


def test_ci_verification_accepts_neutral_and_skipped_checks_with_successful_commit_status():
    status, _ = _derive_status(
        [
            CIVerificationCheck(name="lint", status="completed", conclusion="neutral"),
            CIVerificationCheck(name="optional", status="completed", conclusion="skipped"),
        ],
        "success",
    )
    assert status == "PASS"


def test_ci_verification_does_not_treat_only_neutral_or_skipped_checks_as_success():
    status, message = _derive_status(
        [
            CIVerificationCheck(name="lint", status="completed", conclusion="neutral"),
            CIVerificationCheck(name="optional", status="completed", conclusion="skipped"),
        ],
        "",
    )
    assert status == "PENDING"
    assert "real success signal" in message


def test_ci_verification_passes_with_success_check_even_without_combined_status():
    status, _ = _derive_status(
        [
            CIVerificationCheck(name="backend", status="completed", conclusion="success"),
            CIVerificationCheck(name="optional", status="completed", conclusion="skipped"),
        ],
        "",
    )
    assert status == "PASS"


def test_green_combined_status_cannot_mask_completed_check_without_conclusion():
    status, message = _derive_status(
        [
            CIVerificationCheck(name="backend", status="completed", conclusion="success"),
            CIVerificationCheck(name="security", status="completed", conclusion=None),
        ],
        "success",
    )
    assert status == "PENDING"
    assert "no terminal conclusion" in message


def test_unknown_check_state_fails_closed_even_when_combined_status_is_green():
    status, message = _derive_status(
        [CIVerificationCheck(name="external-gate", status="unknown", conclusion=None)],
        "success",
    )
    assert status == "PENDING"
    assert "recognized terminal state" in message


def test_unrecognized_terminal_conclusion_fails_closed():
    status, message = _derive_status(
        [CIVerificationCheck(name="vendor-gate", status="completed", conclusion="vendor_specific")],
        "success",
    )
    assert status == "PENDING"
    assert "unrecognized conclusion" in message


def test_pr_binding_accepts_exact_recorded_remediation_commit():
    _validate_pr_binding(
        {"number": 17, "state": "open", "draft": True, "head": {"sha": "ABCDEF1234567890"}},
        commit_sha="abcdef1234567890",
        draft_pr_number=17,
    )


def test_pr_binding_rejects_ready_for_review_pr_even_when_head_matches():
    with pytest.raises(PatchVerificationUnavailable, match="no longer a Draft PR"):
        _validate_pr_binding(
            {"number": 17, "state": "open", "draft": False, "head": {"sha": "aaaaaaaaaaaaaaaa"}},
            commit_sha="aaaaaaaaaaaaaaaa",
            draft_pr_number=17,
        )


def test_pr_binding_rejects_changed_pr_head():
    with pytest.raises(PatchVerificationUnavailable, match="head changed"):
        _validate_pr_binding(
            {"number": 17, "state": "open", "draft": True, "head": {"sha": "bbbbbbbbbbbbbbbb"}},
            commit_sha="aaaaaaaaaaaaaaaa",
            draft_pr_number=17,
        )


def test_pr_binding_rejects_missing_head_sha():
    with pytest.raises(PatchVerificationUnavailable, match="head commit"):
        _validate_pr_binding(
            {"number": 17, "state": "open", "draft": True, "head": {}},
            commit_sha="aaaaaaaaaaaaaaaa",
            draft_pr_number=17,
        )


def test_pr_binding_rejects_wrong_pr_number():
    with pytest.raises(PatchVerificationUnavailable, match="expected Draft PR #17"):
        _validate_pr_binding(
            {"number": 18, "state": "open", "draft": True, "head": {"sha": "aaaaaaaaaaaaaaaa"}},
            commit_sha="aaaaaaaaaaaaaaaa",
            draft_pr_number=17,
        )


def test_pr_binding_rejects_closed_pr_even_when_head_matches():
    with pytest.raises(PatchVerificationUnavailable, match="no longer open"):
        _validate_pr_binding(
            {"number": 17, "state": "closed", "draft": True, "head": {"sha": "aaaaaaaaaaaaaaaa"}},
            commit_sha="aaaaaaaaaaaaaaaa",
            draft_pr_number=17,
        )


def test_failed_ci_derives_failed_incident_verification_without_runtime_confirmation():
    outcome, evidence, runtime_required = _derive_incident_verification(
        status="FAIL",
        repository="example/repo",
        commit_sha="abcdef1234567890",
        draft_pr_number=17,
        checks=[CIVerificationCheck(name="backend", status="completed", conclusion="failure")],
    )

    assert outcome is VerificationOutcome.failed
    assert runtime_required is False
    assert "Draft PR #17" in evidence
    assert "backend=failure" in evidence


def test_passing_ci_is_structured_evidence_but_never_auto_resolves_incident():
    outcome, evidence, runtime_required = _derive_incident_verification(
        status="PASS",
        repository="example/repo",
        commit_sha="abcdef1234567890",
        draft_pr_number=17,
        checks=[CIVerificationCheck(name="backend", status="completed", conclusion="success")],
    )

    assert outcome is None
    assert runtime_required is True
    assert "CI=PASS" in evidence
    assert "backend=success" in evidence


def test_pending_ci_derives_inconclusive_evidence_and_keeps_runtime_gate():
    outcome, evidence, runtime_required = _derive_incident_verification(
        status="PENDING",
        repository="example/repo",
        commit_sha="abcdef1234567890",
        draft_pr_number=17,
        checks=[CIVerificationCheck(name="frontend", status="in_progress", conclusion=None)],
    )

    assert outcome is VerificationOutcome.inconclusive
    assert runtime_required is True
    assert "frontend=in_progress" in evidence
