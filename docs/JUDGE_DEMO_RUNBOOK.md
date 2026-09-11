# Judge Demo Runbook

Project: **AI Agentic Bug Router**  
Tagline: **From bug report to verified fix.**

This runbook is the frozen presentation sequence for the hackathon release candidate. The primary demo starts in dedicated **Judge Mode** at `/demo`. Judge Mode intentionally keeps repository writes locked while it runs the golden incident through readiness, routing, RCA, live GitHub evidence and exact patch review.

## 0. Before judges arrive

From the repository root on Windows:

```powershell
git config gc.auto 0
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

`verify.bat` must end with the release-candidate gates passing. Wait for `start.bat` to print:

```text
Backend health: PASS
Frontend health: PASS
READY
```

Use the **actual URLs printed by the launcher** because ports are selected dynamically when defaults are occupied.

Open these tabs in advance:

1. **Judge Mode `/demo`**
2. System Readiness `/readiness`
3. Engineering Evidence Lab `/evidence`
4. Evaluation Lab `/evaluation`
5. Remediation Studio `/remediate` as an operator fallback
6. GitHub repository / Draft PR page only if a live-write demo is planned

Do not put tokens, `.env` contents or private credentials on screen.

## 1. 20-second opening

> “AI Agentic Bug Router takes a software bug, routes it to the right technical area, investigates the actual GitHub repository, ranks evidence for the likely root cause, prepares an exact patch, and — only after human approval — validates it on an isolated branch and can create a Draft PR. We never auto-merge or auto-deploy.”

Open `/demo` and point out the top safety state:

- current backend/API target
- LIVE_FIRST vs FALLBACK_DEMO
- repository write = **LOCKED BY DEFAULT**
- auto merge/deploy = **DISABLED**

## 2. Run the controlled golden flow

Click **Start golden demo**.

Judge Mode creates the prepared authentication incident and automatically runs the safe read-only stages:

```text
readiness
→ incident intake + routing
→ historical evidence
→ RCA
→ live GitHub investigation
→ strongest bounded code candidate
→ exact patch proposal
→ HUMAN APPROVAL BOUNDARY
```

The golden incident describes JWT signature failures and 401 responses after an authentication-related change.

While it runs, explain:

> “The page is not replaying a hard-coded success animation. These stages call our actual backend APIs. If GitHub evidence is missing, stale or ambiguous, the flow visibly stops instead of pretending it found a safe patch.”

Point out the progress rail, routing result, RCA confidence, benchmark proof card and links to the independent Evidence/Readiness/Evaluation surfaces.

## 3. Evidence + RCA

When live repository evidence is available, show:

- actual GitHub repository
- correlated commit SHA/link
- suspicious exact file/hunk
- bounded source context
- correlation score
- RCA rationale and next diagnostic

Say:

> “Correlation is investigation guidance, not proof of causation. Repository text is treated as untrusted data, and recognized credential patterns are redacted before UI exposure.”

If no strong historical or repository match exists, do not force one. A visible `SAFE STOP` is a correct system outcome.

## 4. Exact patch review — still no write

If the live evidence supports a candidate, Judge Mode shows:

- proposal ID
- file path
- exact base state
- strategy
- confidence
- diff preview
- rationale
- `writes now? NO`

Say:

> “The exact patch is reviewable before any repository write. The default Judge Mode run stops at this human-control boundary.”

If the system refuses to generate a patch, say:

> “That is fail-closed behavior. The agent will not invent a patch when live evidence cannot support an exact bounded change.”

## 5. Optional live remediation

Only continue when all of these are true:

- GitHub authentication works locally;
- you understand the exact displayed patch;
- the patch is safe to demonstrate;
- there is time to inspect the resulting Draft PR;
- you intentionally want to demonstrate a real repository write.

The approval button remains disabled until a human explicitly checks:

**Arm live remediation**

Then click **Approve & validate live remediation**.

Expected sequence:

```text
explicit HUMAN APPROVE
→ fresh proposal/file revalidation
→ deterministic incident-fix branch
→ exact approved replacement
→ fresh-clone deterministic validation
→ Draft PR only if green
```

The page then shows decision status, branch, optional Draft PR link and a **Check live CI status** action.

Never merge the demo PR during judging.

### Demonstrating rejection instead

You can click **Reject proposal** without arming writes. This records the human decision and demonstrates that the agent does not override the reviewer.

## 6. Live CI verification

When a Draft PR exists, click **Check live CI status**.

Explain:

- PASS — configured checks passed; human review/runtime verification still required
- FAIL — checks failed; incident escalates
- PENDING — checks are still running
- NO_CHECKS — absence of checks is not success

Say:

> “Even PASS does not auto-merge, auto-deploy or claim production recovery.”

## 7. Evaluation + Readiness proof

Open `/evaluation` to show:

- benchmark version
- measured numerator/denominator for each metric
- individual expected-vs-observed cases
- intentional no-match behavior
- high-risk actions remaining blocked/recommendation-only

If the displayed deterministic benchmark is 100%, say:

> “That is 100% on this displayed deterministic benchmark, not a claim of 100% real-world bug-fixing accuracy.”

Open `/readiness` if a judge asks about runtime configuration or safety controls. It reports configuration state without returning credential values.

## 8. Strong 15-second close

> “Most tools stop at an alert, an explanation or a code suggestion. Our workflow connects routing, live repository evidence, an exact reviewable patch, human approval, deterministic validation, Draft PR creation and real CI verification — while keeping the final merge and production decision with the engineer.”

## Recovery playbook

### Judge Mode shows `SAFE STOP`

Read the reason on screen. If it is a transient GitHub/network problem, use **Retry live evidence**. If the evidence is genuinely missing or ambiguous, keep the fail-closed result and explain it; do not force automation.

### Browser says `Failed to fetch`

Stop and restart only launcher-managed services:

```powershell
.\stop.bat
.\start.bat
```

Use the exact new Dashboard/Judge Mode URLs printed by the launcher. Do not manually guess ports.

### GitHub network/API unavailable

- keep the local incident lifecycle, Readiness and Evaluation Lab available;
- if emergency deterministic fixtures are enabled, keep them visibly labeled **SIMULATED/DEMO**;
- never describe fallback data as live GitHub evidence.

### GitHub authentication unavailable

Public read-only evidence may still work. Live remediation writes must fail visibly with `AUTH_REQUIRED` rather than pretend success.

Check local authentication with:

```powershell
gh auth status
```

Never paste a token into chat, source code, issues or screenshots.

### CI remains pending

Show PENDING honestly. The workflow is asynchronous. Do not claim PASS until GitHub reports PASS.

### Ports are occupied

Run `start.bat` normally. The Windows launcher automatically selects fallback backend/frontend ports. Use the URLs it prints.

## Demo rules

- Never show/paste a real token.
- Never merge a demo Draft PR.
- Never deploy production code from the demo.
- Never claim correlation proves causation.
- Never claim deterministic benchmark score is universal accuracy.
- Never claim a fallback fixture is live data.
- Never bypass the **Arm live remediation** control to make the demo flashier.
- Prefer fail-closed behavior over forcing a false result.

## Final pre-demo checklist

```text
[ ] git pull completed on agent-build-core
[ ] verify.bat → 4/4 release-candidate acceptance PASS
[ ] start.bat says READY
[ ] Judge Mode /demo opens
[ ] /readiness opens and any DEGRADED reason is understood
[ ] /evaluation opens
[ ] /evidence opens
[ ] golden demo reaches the truthful furthest safe stage
[ ] GitHub authenticated only if optional live write is planned
[ ] no tokens / .env contents visible
[ ] team knows who speaks during each stage
[ ] optional demo Draft PR will NOT be merged
```

## Frozen validation reference

Release-candidate executable snapshot:

`b6e4959971b08adcf53fa83b9f98fd8c6aca0f6a`

GitHub Actions run:

`#358` / `34595268159`

Confirmed on that snapshot: backend compile PASS, **59 backend tests / 0 failures**, frontend production build PASS, Windows clean bootstrap PASS, release-candidate contract PASS, and clean-clone acceptance **4/4 PASS**.
