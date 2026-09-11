from app.schemas.patch import CIVerificationCheck
from app.services.patch_verification import _derive_status


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
