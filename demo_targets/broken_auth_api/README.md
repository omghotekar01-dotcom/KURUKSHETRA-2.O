# Broken Auth API — real AutoFix demo target

This folder is intentionally broken so the KURUKSHETRA prototype can demonstrate a real failure → diagnosis → source edit → verification loop.

## The defect

Clients use the standard HTTP header:

```text
Authorization: Bearer demo-valid-token
```

`app.py` incorrectly accepts the `Token` scheme instead of `Bearer`, so a valid protected request returns HTTP 401.

## Prove it manually

From this directory, using the same Python environment as the backend:

```bash
python -m pytest -q
```

Before repair, `test_valid_bearer_token_authenticates` fails. After the platform applies the bounded fix, the same command passes all tests.

You can also launch the target manually:

```bash
uvicorn app:app --port 9010
```

Then call `/profile` with `Authorization: Bearer demo-valid-token`.

## Reset for another judge demo

Use the product's **Reset broken target** button on `/prototype`. It restores the checked-in broken baseline and reruns the validator, so the next demonstration begins from a genuine failing state again.

This target is deliberately simple enough for judges to understand in seconds, but every proof surface is real: source code, failing test, diff, file write and post-fix test result.
