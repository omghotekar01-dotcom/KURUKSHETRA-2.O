# Security & Readiness Milestone

Status: **IMPLEMENTED + CI VERIFIED**  
Date: 2026-09-11  
Project: **AI Agentic Bug Router**

## What changed

### Judge-facing System Readiness

A new `GET /api/v1/evaluation/readiness` endpoint and `/readiness` UI report the runtime state without returning credential values.

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

Incident title, description, environment and log lines are sanitized for obvious credential patterns before they enter the normal persisted incident flow.

The deterministic redactor covers common examples including:

- GitHub token families (`ghp_...`, `github_pat_...` and related prefixes)
- Bearer authorization values
- AWS access-key identifiers
- quoted credential-like assignments such as API keys, tokens, secrets and passwords

The product never reports the value of a configured GitHub credential through the readiness endpoint.

### Repository evidence is untrusted data

GitHub commit messages, issue titles/labels, diff lines and bounded source snippets are treated as evidence only — never as executable instructions.

Before repository evidence reaches the UI:

- obvious credential patterns are redacted;
- prompt-like instruction phrases are detected deterministically;
- a visible repository-context note is added when prompt-like text is observed;
- the text still remains evidence for human inspection rather than becoming an instruction to the agent.

This is a defense-in-depth boundary, not a claim that a simple marker detector solves every possible prompt-injection technique.

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
HUMAN REVIEW / RUNTIME VERIFICATION
```

The system still does **not** automatically merge, deploy to production, execute destructive database operations, mutate IAM/secrets or run unrestricted production shell commands.

## Latest validation proof

GitHub Actions run **#335** / run ID `34594076848` on implementation head `1a9197cece79f5b3b1e59826ff99ae09f5b54864` completed successfully.

```text
Backend compile:                      PASS
Backend tests:                        59 passed, 0 failures
Frontend locked npm install:          PASS
Frontend TypeScript/Vite build:       PASS
Windows launcher syntax validation:   PASS
Windows strict environment preflight: PASS
Windows clean-checkout bootstrap:     PASS
Windows clean-clone acceptance:       PASS
```

The added regression coverage includes incident secret redaction, readiness response secrecy/policy state, prompt-like untrusted-instruction detection and repository diff credential redaction.

## Truth boundary

- Redaction is deterministic best-effort protection for recognized credential patterns, not a replacement for secret-scanning infrastructure.
- Repository evidence can still be malicious or misleading; it is treated as untrusted input.
- A green readiness result means required local configuration checks passed; it does not bypass approval, CI or human verification.
- Passing CI confirms configured checks passed; it does not prove production recovery.
