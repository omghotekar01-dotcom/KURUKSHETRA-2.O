# Judge Demo Runbook

Project: **AI Agentic Bug Router**  
Tagline: **From bug report to verified fix.**

This runbook keeps the live demo truthful, fast and recoverable. Prefer the **read-only golden path** first. Only perform a real repository write when the exact proposal has already been reviewed and there is enough time to inspect the resulting Draft PR.

## 0. Before judges arrive

From repository root on Windows:

```powershell
git config gc.auto 0
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Wait for:

```text
Acceptance summary: 4/4 checks passed
CLEAN-CLONE ACCEPTANCE: PASS
RELEASE-CANDIDATE ACCEPTANCE: PASS
```

Then wait for the launcher to print backend/frontend health and `READY`. Use the **actual URLs printed by the launcher** because ports are selected dynamically when defaults are occupied.

Open these tabs in advance:

1. Judge Mode `/demo`
2. Dashboard `/`
3. System Readiness `/readiness`
4. Evidence Lab `/evidence`
5. Remediation Studio `/remediate`
6. Evaluation Lab `/evaluation`
7. GitHub repository / Draft PR page

Do not put tokens, `.env` contents or private credentials on screen.

## 1. 20-second opening

> “AI Agentic Bug Router takes a software bug, routes it to the right technical area, investigates the actual GitHub repository, ranks real commit/diff evidence — including stack-trace file hints — prepares an exact safety-gated patch, and only after human approval validates it on an isolated branch and can create a Draft PR. We never auto-merge or auto-deploy.”

Then show **System Readiness**.

Point out:

- LIVE_FIRST vs FALLBACK_DEMO
- READY / DEGRADED
- repository allowlist status
- credentials are never displayed
- repository writes require explicit human approval
- auto merge = disabled
- auto production deploy = disabled

## 2. Primary golden path — safe/read-only

### A. Create the incident

Use a concise realistic incident with the real repository attached.

Example:

```text
Title:
401 errors after today's deployment

Description:
Production users can log in, but protected API requests immediately return unauthorized responses.

Environment:
production

Repository:
omghotekar01-dotcom/KURUKSHETRA-2.O

Logs / signals:
JWT signature verification failed
```

Click **Create & investigate incident**.

Explain:

> “The router classifies the incident, maps it to the configured technical owner, checks verified historical knowledge and separately investigates live repository evidence.”

If a repository CODEOWNERS file matches the ranked changed files, point out the owner hint and say:

> “That is a repository routing/review suggestion, not authorization to modify or merge code.”

### B. Show routing and RCA

Point out:

- component/team
- severity
- confidence
- historical evidence if a strong match exists
- no-match escalation if the system does not have enough evidence

Say:

> “We prefer an explicit no-match over a confident fake answer.”

### C. Show Engineering Evidence Lab

Open `/evidence`.

Show:

- actual GitHub repository
- commit SHA and links
- changed files
- ranked diff hunks
- bounded source context
- stack-trace/file-path ranking note when present
- CODEOWNERS routing/review hints when present
- correlation score
- evidence/truth-boundary notes

Say:

> “Correlation helps investigation; we do not call it proof of causation.”

If repository text contains a prompt-like instruction or credential-shaped value, point out that it is treated as **untrusted evidence** and recognized credentials are redacted before display.

## 3. Patch proposal — still no write

Open `/remediate` and select the incident.

Generate the safest available proposal only when a bounded live candidate is available.

Before approving anything, show:

- proposal ID
- repository and exact base commit
- file path and hunk
- before/after lines
- diff preview
- confidence
- warnings
- verification commands
- patch correlation safety threshold

Say:

> “Up to this point, the system has not changed the repository. The exact patch is visible before any write.”

If the system says no safe proposal is available, **do not fight it**. Explain:

> “That is fail-closed behavior. Weak correlation, stale source or unsupported evidence does not become an automatic patch.”

That is a valid demo outcome.

## 4. Optional live-write path

Only do this if GitHub auth is working, the exact proposal is safe to demonstrate, the file change is understood, and there is enough time to inspect the Draft PR afterward.

Click the explicit approval action.

Expected sequence:

```text
Human APPROVE
→ fresh proposal/file revalidation
→ deterministic incident-fix branch
→ exact approved replacement
→ trusted deterministic validation
→ Draft PR only if green
```

Frontend remediation validates with locked `npm ci` + build. Backend Python validates with compile + pytest. Unsupported executable/configuration file types fail closed until a trusted validator exists.

Show the branch / Draft PR link.

Then deliberately click the same approval again only if you want to demonstrate idempotency. The expected behavior is reuse of the same exact remediation state — not a second branch/commit/PR.

Never merge the demo PR during judging.

## 5. Live CI verification

After a Draft PR exists, use **Check live CI status** in Remediation Studio.

Explain the states:

- PASS — configured checks passed; still requires human/runtime verification
- FAIL — checks failed; incident verification derives FAIL and escalates
- PENDING — checks are still running; evidence is inconclusive
- NO_CHECKS — absence of checks is not success

Say:

> “CI state becomes auditable incident evidence. Even PASS does not auto-merge or claim that production recovered.”

## 6. Evaluation Lab

Open `/evaluation`.

Show that:

- benchmark version is visible;
- every expected vs observed case is visible;
- score values are calculated by the backend at run time;
- unknown-service case must remain unmatched;
- unsafe production/destructive actions must remain blocked/recommendation-only.

If the benchmark is 100%, say:

> “That is 100% on this displayed deterministic benchmark, not a claim of 100% real-world bug-fixing accuracy.”

## 7. Strong 15-second close

> “The useful part is not just that the system can propose a fix. It connects routing, live repository evidence, exact reviewable changes, human approval, deterministic validation, Draft PR creation and real CI evidence — and it knows when not to act if the evidence or validator is not strong enough.”

## Recovery playbook

### Browser says `Failed to fetch`

```powershell
.\stop.bat
.\start.bat
```

Use the exact Dashboard/API URLs printed by the launcher. The launcher automatically chooses free backend/frontend ports and injects the selected API URL into Vite.

### GitHub network/API unavailable

- Keep the incident lifecycle and local Evaluation Lab available.
- If emergency deterministic fixtures are used, keep the UI/voice explanation explicitly labeled **SIMULATED/DEMO**.
- Never describe fallback data as live GitHub evidence.

### GitHub authentication unavailable

Read-only evidence may still work for public repositories. Live remediation writes must return `AUTH_REQUIRED` / fail visibly rather than pretending success.

Do not paste a token into chat, source files or screenshots. Authenticate locally with GitHub CLI if needed:

```powershell
gh auth status
```

### No safe patch candidate

Treat it as an intentional fail-closed result. Show Evidence Lab + RCA and explain that weak correlation, stale source, ambiguity or unavailable validation prevents unsafe automation.

### CI remains pending

Show PENDING honestly. Do not claim PASS until GitHub reports PASS.

## Demo rules

- Never show/paste a real token.
- Never merge a demo Draft PR.
- Never deploy production code from the demo.
- Never claim correlation proves causation.
- Never claim deterministic benchmark score is universal accuracy.
- Never claim a fallback fixture is live data.
- Prefer fail-closed behavior over forcing a flashy but false result.

## Final pre-demo checklist

```text
[ ] git pull completed on agent-build-core
[ ] verify.bat: 4/4 PASS
[ ] start.bat says READY
[ ] /readiness is READY or DEGRADED reason is understood
[ ] /demo opens
[ ] Dashboard opens
[ ] Evidence Lab opens
[ ] Remediation Studio opens
[ ] Evaluation Lab opens
[ ] one realistic incident was rehearsed
[ ] GitHub logged in only if live-write demo is planned
[ ] no tokens / .env contents visible
[ ] team knows who speaks during each stage
[ ] optional demo Draft PR will NOT be merged
```
