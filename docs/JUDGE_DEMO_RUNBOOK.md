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
.\setup-local-ai.bat
.\start.bat
```

`setup-local-ai.bat` must finish its real Qwen inference warm-up when the live local-model demo is intended. Do not describe Qwen as live merely because it is installed.

Wait for:

```text
Acceptance summary: 4/4 checks passed
CLEAN-CLONE ACCEPTANCE: PASS
RELEASE-CANDIDATE ACCEPTANCE: PASS
```

Then wait for the launcher to print backend/frontend health and `READY`. Use the **actual URLs printed by the launcher** because ports are selected dynamically when defaults are occupied.

Open these tabs in advance:

1. AI Workspace `/`
2. Judge Mode `/demo`
3. Incident Command `/incidents`
4. System Readiness `/readiness`
5. Real AutoFix `/prototype`
6. Judge Intake `/intake`
7. Evidence Lab `/evidence`
8. Remediation Studio `/remediate`
9. Evaluation Lab `/evaluation`
10. GitHub repository / Draft PR page

Do not put tokens, `.env` contents or private credentials on screen.

## 1. 20-second opening — AI Workspace

Start on `/`.

Recommended line:

> “AI Agentic Bug Router is an evidence-first engineering agent. Give it a bug description, attach source/tests or point it at an allowlisted GitHub repository, and it routes the incident, retrieves engineering knowledge, investigates real code evidence, prepares an exact reviewable patch and proves the result before a human-controlled handoff.”

Point out:

- conversational bug composer;
- optional source/test attachments;
- GitHub repository field;
- production/staging/development context;
- Trusted tests opt-in;
- LIVE_FIRST / fallback label;
- **Test live integrations**.

Click **Test live integrations** before making any live-model or live-write claim. The result should distinguish:

- Qwen installed/reachable vs a real successful inference probe;
- GitHub authentication vs actual push permission for the allowlisted repository.

Say:

> “We probe the integrations rather than assuming configuration equals connectivity. The permission check is read-only; it creates no GitHub resource.”

## 2. Strongest 60-second proof — Real AutoFix

Open `/prototype`.

Use the Bearer Authentication target first.

```text
Reset broken target
→ 1. Scan + reproduce
→ show BEFORE = FAIL
→ show source/test-grounded root cause
→ 2. Preview exact fix
→ show exact diff and provider/fallback label
→ 3. Auto Fix + Verify
→ show AFTER = PASS
```

Say:

> “This folder is an independent broken application. We are not feeding the UI a fake error string. The same real pytest contract fails before the edit and passes afterward; failed validation would restore the original source.”

If Ollama is unavailable, the built-in deterministic safe rule is a truthful fallback for these registered proof targets. Do not label that fallback as Qwen.

## 3. Judge-supplied challenge — files + Qwen

Open `/intake` or use the AI Workspace with files attached.

For the dedicated Intake page, click **Test Qwen now** first. Require a live model-call success before saying Qwen is active.

Recommended rehearsal files:

`calc.py`

```python
def add(a, b):
    return a - b
```

`test_calc.py`

```python
from calc import add

def test_add():
    assert add(2, 3) == 5
```

Bug report:

```text
The add function returns the wrong result. add(2, 3) should return 5, but the current implementation subtracts the second argument instead of adding it. Use the supplied pytest test as the functional contract. Find the smallest safe code change and verify it.
```

For your own rehearsal files, enable **Trusted test execution**.

Expected sequence:

```text
Analyze files + retrieve RAG
→ baseline trusted pytest FAIL
→ Preview grounded AI fix
→ inspect exact diff
→ Apply reviewed patch + verify
→ same trusted pytest PASS
→ VERIFIED_FIXED
```

Without trusted functional tests, a successful static result must remain `STATIC_CHECK_PASSED`; do not call it verified functional recovery.

## 4. Primary incident-routing path

Open Incident Command at `/incidents`.

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

### Show routing and RCA

Point out:

- component/team;
- severity;
- confidence;
- historical evidence if a strong match exists;
- no-match escalation if the system does not have enough evidence;
- top RCA hypothesis;
- next diagnostic.

Say:

> “We prefer an explicit no-match over a confident fake answer. RCA remains a hypothesis until the defined diagnostics and validators strengthen it.”

## 5. Engineering Evidence Lab

Open `/evidence` and select the incident.

Show:

- actual GitHub repository;
- commit SHA and links;
- changed files;
- ranked diff hunks;
- bounded source context;
- stack-trace/file-path ranking note when present;
- CODEOWNERS routing/review hints when present;
- correlation score;
- evidence/truth-boundary notes.

Say:

> “Correlation helps investigation; we do not call it proof of causation.”

If repository text contains a prompt-like instruction or credential-shaped value, point out that it is treated as **untrusted evidence** and recognized credentials are redacted before display.

## 6. Patch proposal — still no write

From `/evidence`, use **Prepare safety-gated patch**, or open `/remediate` and select the same incident.

Generate the safest available proposal only when a bounded live candidate is available.

Before approving anything, show:

- proposal ID;
- repository and exact base commit;
- file path and hunk;
- before/after lines;
- diff preview;
- confidence;
- warnings;
- verification commands;
- patch correlation safety threshold.

Say:

> “Up to this point, the system has not changed the repository. The exact patch is visible before any write.”

If the system says no safe proposal is available, **do not fight it**. Explain:

> “That is fail-closed behavior. Weak correlation, stale source or unsupported evidence does not become an automatic patch.”

That is a valid demo outcome.

## 7. Optional live-write path

Before attempting the live write, open `/readiness` and click **Test live integrations**.

For GitHub you want:

```text
repository allowlisted
GitHub CLI / credential available
push permission VERIFIED
```

If push permission is not verified, use the page's local guidance:

```powershell
gh auth status
gh auth login
```

Do not paste a token into the UI or chat.

Only continue when GitHub auth is working, the exact proposal is safe to demonstrate, the file change is understood, and there is enough time to inspect the Draft PR afterward.

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

**Never merge the demo PR from the product.** The product intentionally has no automatic merge/deploy. Open the Draft PR and explain that final merge remains a deliberate human GitHub action after review.

## 8. Live CI verification

After a Draft PR exists, use **Check live CI status** in Remediation Studio or Judge Mode.

Explain the states:

- PASS — configured checks passed; still requires human/runtime verification;
- FAIL — checks failed; incident verification derives FAIL and escalates;
- PENDING — checks are still running; evidence is inconclusive;
- NO_CHECKS — absence of checks is not success.

Say:

> “CI state becomes auditable incident evidence. Even PASS does not auto-merge or claim that production recovered.”

## 9. AI Reasoning Lab

Open `/ai`.

Use **JWT authentication regression** to show:

```text
Triage
→ RAG
→ live repository evidence
→ RCA synthesis
→ policy gate
```

Then use **Unknown service safe-stop** to show that the system can refuse a confident RCA/remediation when evidence is insufficient.

Recommended line:

> “Agentic does not mean reckless. A production engineering agent also needs a strong stop condition.”

## 10. Evaluation Lab

Open `/evaluation`.

Show that:

- benchmark version is visible;
- every expected vs observed case is visible;
- score values are calculated by the backend at run time;
- unknown-service case must remain unmatched;
- unsafe production/destructive actions must remain blocked/recommendation-only.

If the benchmark is 100%, say:

> “That is 100% on this displayed deterministic benchmark, not a claim of 100% real-world bug-fixing accuracy.”

## 11. Judge Mode — compact end-to-end backup

Open `/demo` if judging time becomes short or you need one guided summary screen.

**Start golden demo** performs the controlled read-only path through:

```text
readiness
→ incident
→ triage + retrieval
→ RCA
→ live GitHub evidence
→ strongest bounded candidate
→ exact NO-WRITE patch proposal
```

The default run stops at the human approval boundary. Repository writes require **Arm live remediation** and another explicit approval.

Use Judge Mode as a guided summary, but use `/prototype`, `/intake`, `/evidence` and `/remediate` when a technical judge asks for the underlying proof.

## 12. Strong 15-second close

> “The useful part is not just that the system can propose a fix. It connects natural-language incident intake, routing, live repository evidence, exact reviewable changes, human approval, deterministic validation, Draft PR creation and real CI evidence — and it knows when not to act if the evidence or validator is not strong enough.”

## Recovery playbook

### Browser says `Failed to fetch`

```powershell
.\stop.bat
.\start.bat
```

Use the exact Workspace/API URLs printed by the launcher. The launcher automatically chooses free backend/frontend ports and injects the selected API URL into Vite.

### Qwen says installed but not live

Run:

```powershell
.\setup-local-ai.bat
```

Require its real inference warm-up to pass. Then open `/readiness` and click **Test live integrations**, or `/intake` and click **Test Qwen now**.

The backend supports both Ollama's OpenAI-compatible routes and native `/api/tags` / `/api/chat` fallback.

### GitHub read works but write fails

Open `/readiness` and **Test live integrations**. Check the read-only permission probe.

Then locally:

```powershell
gh auth status
gh auth login
```

A successful remediation requires push permission to the configured allowlisted repository. Public read access alone is not write authority.

### GitHub network/API unavailable

- Keep the local AutoFix, Judge Intake and Evaluation Lab available.
- If emergency deterministic fixtures are used, keep the UI/voice explanation explicitly labeled **SIMULATED/DEMO**.
- Never describe fallback data as live GitHub evidence.

### GitHub authentication unavailable

Read-only evidence may still work for public repositories. Live remediation writes must return `AUTH_REQUIRED` / fail visibly rather than pretending success.

Do not paste a token into chat, source files or screenshots.

### No safe patch candidate

Treat it as an intentional fail-closed result. Show Evidence Lab + RCA and explain that weak correlation, stale source, ambiguity or unavailable validation prevents unsafe automation.

### CI remains pending

Show PENDING honestly. Do not claim PASS until GitHub reports PASS.

## Demo rules

- Never show/paste a real token.
- Never merge a demo Draft PR from the product.
- Never deploy production code from the demo.
- Never claim correlation proves causation.
- Never claim deterministic benchmark score is universal accuracy.
- Never claim a fallback fixture is live data.
- Never call Qwen live without an inference probe.
- Prefer fail-closed behavior over forcing a flashy but false result.

## Final pre-demo checklist

```text
[ ] git pull completed on agent-build-core
[ ] verify.bat: acceptance PASS
[ ] setup-local-ai.bat: real Qwen inference warm-up PASS if Qwen demo is planned
[ ] start.bat says READY
[ ] /readiness active probe result is understood
[ ] / workspace opens and integrations can be probed
[ ] /prototype authentication target rehearsed FAIL → PASS
[ ] /intake trusted calc example rehearsed when live Qwen is intended
[ ] /incidents opens
[ ] /evidence opens
[ ] /remediate opens
[ ] /evaluation opens
[ ] /demo golden flow rehearsed
[ ] GitHub push permission VERIFIED only if live-write demo is planned
[ ] no tokens / .env contents visible
[ ] optional demo Draft PR will NOT be auto-merged
```
