from app.services.workspace_ai import _extract_json


def test_qwen_think_block_before_json_is_accepted() -> None:
    payload = _extract_json(
        '<think>I should inspect the exact failing contract first.</think>\n'
        '{"file_path":"calc.py","search":"return a - b","replace":"return a + b","explanation":"match the supplied test"}'
    )
    assert payload["file_path"] == "calc.py"
    assert payload["search"] == "return a - b"


def test_json_can_be_extracted_from_small_transport_wrapper() -> None:
    payload = _extract_json(
        'Final structured answer:\n{"file_path":"app.py","search":"old","replace":"new","explanation":"bounded"}'
    )
    assert payload["replace"] == "new"
