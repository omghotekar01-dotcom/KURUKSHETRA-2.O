# Release Candidate Freeze

Project: **AI Agentic Bug Router**  
Tagline: **From bug report to verified fix.**  
Date: **11 September 2026**

## Scope status

The planned **hackathon MVP implementation scope is complete** on the release-candidate snapshot recorded below.

“Complete” here means the agreed hackathon product path, safety controls, reproducible setup, judge-facing proof surfaces and release checks are implemented and have passed automated acceptance. It does **not** mean the software is universally bug-free, enterprise-production hardened or capable of solving every class of software defect.

## Frozen executable snapshot

Implementation branch: `agent-build-core`

Validated executable code head: `b6e4959971b08adcf53fa83b9f98fd8c6aca0f6a`

GitHub Actions validation: **run #358**, run ID `34595268159`.

```text
Backend compile:                       PASS
Backend tests:                         59 passed, 0 failures
Frontend locked dependency install:    PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax:               PASS
Windows strict environment preflight:  PASS
Windows fresh bootstrap:               PASS
Release candidate contract:            PASS
Clean-clone acceptance:                4/4 PASS
Release-candidate acceptance:          PASS
```

The Windows run rebuilt the project from a clean Git checkout before executing acceptance. Commits after `b6e495...` in this closure pass update README/runbook/status documentation only; they do not change the frozen executable behavior.

## Release-candidate contract

`scripts/release_contract.py` is part of the acceptance gate. It verifies critical release artifacts/routes, Judge Mode's locked-by-default write state, explicit human approval, fail-closed behavior, real CI hook, npm lockfile v3, launcher Judge Mode links, README safety statements and that `.env` is not tracked.

## Completed release scope

```text
Incident intake + persistence
→ deterministic triage / owner routing
→ historical runbook + verified-resolution retrieval
→ live allowlisted GitHub investigation
→ commit / file / diff / bounded source evidence
→ evidence-backed RCA
→ exact no-write patch proposal
→ explicit human approval / rejection
→ deterministic retry-safe remediation identity
→ isolated incident-fix branch
→ exact approved replacement
→ deterministic fresh-clone validation
→ Draft PR only after green validation
→ real GitHub CI status verification
→ human runtime verification
→ verified-resolution memory
```

Judge/operator proof surfaces:

```text
/demo       Judge Mode golden flow
/readiness  runtime + safety readiness
/evidence   live repository evidence
/remediate  operator remediation studio
/evaluation measured deterministic benchmark
```

Reliability/security scope includes dynamic local ports, locked frontend dependencies, clean-clone bootstrap, idempotent remediation reuse, stale/conflicting-state rejection, recognized credential redaction, untrusted-repository-evidence handling and prompt-like instruction warnings.

## Judge Mode safety boundary

Judge Mode is deliberately **read-only through exact patch proposal**. A real repository write requires reviewing the exact patch, explicitly enabling **Arm live remediation**, and then explicitly approving the bounded write. Even then, the system writes only to an isolated remediation branch, validates it, and may create a **Draft PR**. It does not merge or deploy.

A missing/stale/ambiguous candidate produces `SAFE_STOP` instead of a fabricated patch.

## Final local rehearsal

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\HACKATHON\KURUKSHETRA-2.O
git config gc.auto 0
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Expected release gate:

```text
Acceptance summary: 4/4 checks passed
CLEAN-CLONE ACCEPTANCE: PASS
RELEASE-CANDIDATE ACCEPTANCE: PASS
```

Use the exact URLs printed by `start.bat`. Open **Judge Mode `/demo`** first.

## Submission promotion is intentionally separate

At this freeze point, implementation is still on `agent-build-core`, Draft PR #1 targets `develop`, and `main` remains untouched by design. Final branch promotion happens only after the team runs the local rehearsal and explicitly approves the final submission step.

## Truth boundaries / intentionally out of scope

The hackathon release does not claim universal real-world accuracy, causal proof from commit correlation, a custom trained ML model, automatic production recovery, auto merge/deployment, enterprise distributed locking, complete DLP/universal prompt-injection prevention, fully hashed transitive Python locking, or semantic patch synthesis for every code/file type.

Those are future engineering directions, not missing promises from this hackathon MVP.

## Freeze rule

From this point until submission, prefer **bug fixes, local rehearsal, screenshots and documentation corrections only**. Do not add speculative features that can destabilize the validated golden path.

**Feature freeze status: ACTIVE. No planned hackathon MVP feature work remains.**
