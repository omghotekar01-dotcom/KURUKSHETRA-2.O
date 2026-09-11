from app.schemas.incident import VerificationOutcome
from app.schemas.patch import CIVerificationCheck
from app.services.patch_verification import _derive_incident_verification, _derive_status


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


def test_ci_verification_accepts_neutral_and_skipped_checks_without_failure():
    status, _ = _derive_status(
        [
            CIVerificationCheck(name="lint", status="completed", conclusion="neutral"),
            CIVerificationCheck(name="optional", status="completed", conclusion="skipped"),
        ],
        "success",
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
