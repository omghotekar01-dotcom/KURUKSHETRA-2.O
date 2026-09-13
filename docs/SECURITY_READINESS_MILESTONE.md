# Security & Readiness Milestone

Status: **IMPLEMENTED + CI VERIFIED**  
Date: 2026-09-12  
Project: **AI Agentic Bug Router**

## What changed

### Judge-facing System Readiness

A `GET /api/v1/evaluation/readiness` endpoint and `/readiness` UI report runtime state without returning credential values.

The surface reports:

- `READY` / `DEGRADED`
- `LIVE_FIRST` / `FALLBACK_DEMO`
- database-path configuration
- repository allowlist configuration
- GitHub access mode without exposing a token
- whether GitHub CLI is available
- human-approval requirement for repository writes
- high-risk action policy
- explicit `automatic_merge = false`
- explicit `automatic_production_deploy = false`

The local launcher prints the readiness URL alongside Dashboard, Evidence Lab, Remediation Studio and Evaluation Lab.

### Secret redaction before persistence/display

Incident title, description, environment and log lines are sanitized for recognized credential patterns before they enter the normal persisted incident flow.

The deterministic redactor covers common examples including:

- GitHub token families (`ghp_...`, `github_pat_...` and related prefixes)
- Bearer authorization values
- AWS access-key identifiers
- quoted credential-like assignments such as API keys, tokens, secrets and passwords
- unquoted credential-like assignments such as `password=value` and `authorization=Bearer ...`

Credential key names may remain visible for debugging/auditability, but recognized values are replaced with `[REDACTED]`. The readiness endpoint never reports the value of a configured GitHub credential.

### Repository evidence is untrusted data

GitHub commit messages, issue titles/labels, diff lines and bounded source snippets are treated as evidence only — never as executable instructions.

Before repository evidence reaches the UI/agent synthesis layer:

- recognized credential patterns are redacted;
- prompt-like instruction phrases are detected deterministically;
- broader instruction-shaped evidence is classified into audit signals such as instruction override attempts, fabricated verification requests, repository-authority escalation requests, secret-disclosure requests and safety-bypass requests;
- a visible repository-context note is added when prompt-like text is observed;
- the text still remains evidence for human inspection rather than becoming an instruction to the agent.

The detector is audit/defense-in-depth only. Matching text does not gain command authority, and the LLM system instruction independently requires repository text, logs, diffs and runbooks to be treated as untrusted data.

### Regression found and fixed during this hardening pass

The first implementation of unquoted-assignment redaction accidentally normalized an already-redacted quoted assignment such as `api_key='[REDACTED]'` into the unquoted shape `api_key=[REDACTED]`. That was harmless to secrecy but broke the existing deterministic output contract and its regression test.

The unquoted matcher now explicitly excludes quote-prefixed values, preserving the established quoted-redaction shape while still covering truly unquoted credentials. CI caught this before documentation/promotion; no failing head was treated as verified.

## Existing safety boundary remains unchanged

```text
READ / RETRIEVE / CLASSIFY
        ↓
LOW-RISK autonomous analysis
        ↓
PATCH PROPOSAL (NO WRITE)
        ↓
HUMAN APPROVAL REQUIRED
        ↓
ISOLATED deterministic fix branch
        ↓
VALIDATION
        ↓
DRAFT PR only if green
        ↓
REAL GITHUB CI
        ↓
EXTERNAL HUMAN REVIEW / MERGE
        ↓
RUNTIME / HUMAN VERIFICATION
```

The system still does **not** automatically merge, deploy to production, execute destructive database operations, mutate IAM/secrets or run unrestricted production shell commands.

## Latest validation proof

GitHub Actions **Build and test #811** / run ID `34656898448` on executable security-hardening head:

`92a34ca4295c04e2a153c5bc8cf3b91919ef57f9`

completed successfully on 2026-09-11 UTC / 2026-09-12 IST.

```text
Backend compile:                       PASS
Backend tests:                         118 passed, 2 dependency warnings, 0 failures
Frontend locked npm install:           PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax validation:    PASS
Windows stale/reused PID safety test:  PASS
Windows strict environment preflight:  PASS
Windows clean-checkout bootstrap:      PASS
Windows clean-clone acceptance:        PASS
Overall workflow:                      PASS
```

The added regression coverage includes:

- unquoted credential assignment redaction;
- quoted-redaction output-shape preservation;
- broader adversarial evidence containing safety-override language;
- fabricated test-success requests;
- repository merge/approval escalation language;
- secret/environment disclosure requests;
- the prior incident/repository credential-redaction and prompt-like instruction tests.

The two Python warnings are dependency deprecations from FastAPI/Starlette test infrastructure and are not test failures.

## Truth boundary

- Redaction is deterministic best-effort protection for recognized credential patterns, not a replacement for secret-scanning/DLP infrastructure.
- Prompt-injection detection is an audit signal and defense-in-depth layer, not a claim of universal prompt-injection prevention.
- Repository evidence can still be malicious or misleading; it remains untrusted input.
- A green readiness result means required local configuration checks passed; it does not bypass approval, CI or human verification.
- Passing CI confirms configured checks passed for the remediation commit; it does not prove production recovery.
- Draft PR creation remains the final in-product repository-write stage; merge/deploy remain outside the product workflow.
