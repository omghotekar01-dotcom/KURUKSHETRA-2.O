import { useMemo, useState } from 'react'
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  FileCode2,
  GitBranch,
  GitPullRequest,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  XCircle,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const GOLDEN_INCIDENT = {
  title: '401 errors after JWT signing change',
  description: 'Production API requests started returning unauthorized responses after a recent authentication-related change. Valid sessions fail JWT signature verification.',
  environment: 'production',
  repo: 'omghotekar01-dotcom/KURUKSHETRA-2.O',
  logs: [
    'JWT signature verification failed',
    '401 unauthorized after authentication deployment',
  ],
}

type ReadinessReport = {
  status: 'READY' | 'DEGRADED'
  checked_at: string
  mode: 'LIVE_FIRST' | 'FALLBACK_DEMO'
  checks: Record<string, boolean>
  github: {
    access_mode: string
    token_present: boolean
    gh_cli_available: boolean
  }
}

type IncidentRecord = {
  id: string
  status: string
  incident: { title: string }
  triage: {
    component: string
    owner_team: string
    severity: string
    confidence: number
  }
}

type AnalysisBundle = {
  hypotheses: Array<{
    id: string
    title: string
    confidence: number
    rationale: string
    next_diagnostic: string
  }>
  evidence: {
    matches: Array<{ id: string; component: string; issue: string; score: number }>
    no_strong_match: boolean
  }
  needs_human_investigation: boolean
}

type DiffHunk = {
  filename: string
  header: string
  added_lines: string[]
  removed_lines: string[]
  source_context: Array<{ line_number: number; content: string; in_hunk: boolean }>
  correlation_score: number
}

type CommitEvidence = {
  sha: string
  short_sha: string
  message: string
  url: string
  suspicious_hunks: DiffHunk[]
  correlation_score: number
}

type RepositoryContext = {
  repository: string
  default_branch: string
  authenticated: boolean
  source: string
  commits: CommitEvidence[]
  notes: string[]
}

type Candidate = DiffHunk & { commit: CommitEvidence }

type PatchProposal = {
  proposal_id: string
  incident_id: string
  repository: string
  base_commit: string
  file_path: string
  hunk_header: string
  strategy: string
  before_lines: string[]
  after_lines: string[]
  diff_preview: string
  rationale: string
  confidence: number
  verification_commands: string[]
  warnings: string[]
  writes_repository: boolean
}

type ExecutionResult = {
  incident_id: string
  proposal_id: string
  decision: string
  status: string
  message: string
  repository: string
  branch?: string | null
  branch_url?: string | null
  commit_sha?: string | null
  draft_pr_number?: number | null
  draft_pr_url?: string | null
  validation: Array<{ name: string; command: string; status: string; output: string }>
  incident_status: string
}

type CIVerification = {
  status: 'PASS' | 'FAIL' | 'PENDING' | 'NO_CHECKS'
  message: string
  draft_pr_number: number
  draft_pr_url?: string | null
  checks: Array<{ name: string; status: string; conclusion?: string | null; details_url?: string | null }>
}

type EvaluationReport = {
  overall_score: number
  benchmark_version: string
  cases: Array<{ passed: boolean }>
}

type DemoPhase = 'IDLE' | 'RUNNING' | 'REVIEW' | 'SAFE_STOP' | 'EXECUTED' | 'REJECTED' | 'ERROR'

type DemoStep = {
  label: string
  detail: string
  reached: boolean
  attention?: boolean
}

async function readError(response: Response) {
  try {
    const payload = await response.json()
    return payload.detail ?? JSON.stringify(payload)
  } catch {
    return response.text()
  }
}

export default function JudgeDemoPage() {
  const [phase, setPhase] = useState<DemoPhase>('IDLE')
  const [busy, setBusy] = useState(false)
  const [currentAction, setCurrentAction] = useState('Ready for a controlled read-only run.')
  const [error, setError] = useState('')
  const [safeStopReason, setSafeStopReason] = useState('')
  const [readiness, setReadiness] = useState<ReadinessReport | null>(null)
  const [incident, setIncident] = useState<IncidentRecord | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisBundle | null>(null)
  const [context, setContext] = useState<RepositoryContext | null>(null)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [proposal, setProposal] = useState<PatchProposal | null>(null)
  const [execution, setExecution] = useState<ExecutionResult | null>(null)
  const [ci, setCi] = useState<CIVerification | null>(null)
  const [evaluation, setEvaluation] = useState<EvaluationReport | null>(null)
  const [liveWriteArmed, setLiveWriteArmed] = useState(false)
  const [copied, setCopied] = useState(false)

  const topHypothesis = analysis?.hypotheses?.[0] ?? null
  const benchmarkPasses = evaluation?.cases.filter((item) => item.passed).length ?? 0

  const steps = useMemo<DemoStep[]>(() => [
    {
      label: 'System readiness',
      detail: readiness ? `${readiness.status} · ${readiness.mode}` : 'Runtime, integration and safety preflight',
      reached: Boolean(readiness),
      attention: readiness?.status === 'DEGRADED',
    },
    {
      label: 'Incident intake + routing',
      detail: incident ? `${incident.triage.component} → ${incident.triage.owner_team}` : 'Create a real auditable incident',
      reached: Boolean(incident),
    },
    {
      label: 'Evidence-backed RCA',
      detail: topHypothesis ? `${topHypothesis.title} · ${Math.round(topHypothesis.confidence * 100)}%` : 'Historical evidence + diagnosis',
      reached: Boolean(analysis),
      attention: Boolean(analysis?.needs_human_investigation),
    },
    {
      label: 'Live GitHub evidence',
      detail: context ? `${context.commits.length} commit(s) inspected · ${context.default_branch}` : 'Commits, diffs and bounded source context',
      reached: Boolean(context),
      attention: phase === 'SAFE_STOP' && Boolean(incident),
    },
    {
      label: 'Exact patch proposal',
      detail: proposal ? `${proposal.strategy} · ${proposal.file_path}` : 'No repository write at this stage',
      reached: Boolean(proposal),
      attention: phase === 'SAFE_STOP',
    },
    {
      label: 'Human approval gate',
      detail: execution ? `${execution.decision} · ${execution.status}` : proposal ? 'Waiting for explicit human decision' : 'Locked until an exact proposal exists',
      reached: Boolean(execution),
    },
    {
      label: 'Validation + Draft PR + CI',
      detail: ci ? `${ci.status} · ${ci.checks.length} check(s)` : execution?.draft_pr_number ? `Draft PR #${execution.draft_pr_number}` : 'Never auto-merge or auto-deploy',
      reached: Boolean(ci) || Boolean(execution?.draft_pr_number),
      attention: ci?.status === 'FAIL' || ci?.status === 'NO_CHECKS',
    },
  ], [readiness, incident, analysis, topHypothesis, context, proposal, execution, ci, phase])

  function resetDemo() {
    setPhase('IDLE')
    setBusy(false)
    setCurrentAction('Ready for a controlled read-only run.')
    setError('')
    setSafeStopReason('')
    setReadiness(null)
    setIncident(null)
    setAnalysis(null)
    setContext(null)
    setCandidate(null)
    setProposal(null)
    setExecution(null)
    setCi(null)
    setEvaluation(null)
    setLiveWriteArmed(false)
    setCopied(false)
  }

  async function fetchEvaluation() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/run`)
      if (response.ok) setEvaluation(await response.json())
    } catch {
      // Evaluation is a proof surface; failure must not falsify the live incident flow.
    }
  }

  async function prepareRepositoryProposal(incidentId: string) {
    setCurrentAction('Inspecting live GitHub commits, diffs and source context…')
    const repositoryResponse = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/repository-context`)
    if (!repositoryResponse.ok) {
      throw new Error(`Repository evidence unavailable: ${await readError(repositoryResponse)}`)
    }

    const repositoryContext: RepositoryContext = await repositoryResponse.json()
    setContext(repositoryContext)

    const bestCandidate = repositoryContext.commits
      .flatMap((commit) => commit.suspicious_hunks.map((hunk) => ({ ...hunk, commit })))
      .filter((hunk) => hunk.added_lines.length > 0 && hunk.source_context.length > 0)
      .sort((a, b) => b.correlation_score - a.correlation_score)[0]

    if (!bestCandidate) {
      setCandidate(null)
      setSafeStopReason('Live evidence was collected, but no exact suspicious hunk has both added lines and bounded source context. The agent stopped instead of inventing a patch.')
      setPhase('SAFE_STOP')
      setCurrentAction('Safe stop: evidence is insufficient for an exact patch.')
      return
    }

    setCandidate(bestCandidate)
    setCurrentAction('Revalidating the strongest candidate and preparing an exact no-write patch proposal…')
    const proposalResponse = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/patch-proposal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        commit_sha: bestCandidate.commit.sha,
        filename: bestCandidate.filename,
        hunk_header: bestCandidate.header,
      }),
    })

    if (!proposalResponse.ok) {
      setSafeStopReason(`Patch proposal was refused after fresh revalidation: ${await readError(proposalResponse)}`)
      setPhase('SAFE_STOP')
      setCurrentAction('Safe stop: the candidate became stale, ambiguous or unsafe.')
      return
    }

    setProposal(await proposalResponse.json())
    setPhase('REVIEW')
    setCurrentAction('Exact patch proposal is ready. Repository writes remain locked until a human explicitly arms and approves them.')
  }

  async function runGoldenDemo() {
    resetDemo()
    setBusy(true)
    setPhase('RUNNING')
    setCurrentAction('Checking runtime readiness…')

    try {
      const readinessResponse = await fetch(`${API_BASE}/api/v1/evaluation/readiness`)
      if (!readinessResponse.ok) throw new Error(`Readiness endpoint failed with ${readinessResponse.status}`)
      const readinessPayload: ReadinessReport = await readinessResponse.json()
      setReadiness(readinessPayload)

      setCurrentAction('Creating the golden authentication incident…')
      const incidentResponse = await fetch(`${API_BASE}/api/v1/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(GOLDEN_INCIDENT),
      })
      if (!incidentResponse.ok) throw new Error(await readError(incidentResponse))
      const created: IncidentRecord = await incidentResponse.json()
      setIncident(created)

      setCurrentAction('Running triage, historical retrieval and root-cause analysis…')
      const analysisResponse = await fetch(`${API_BASE}/api/v1/incidents/${created.id}/analyze`, { method: 'POST' })
      if (!analysisResponse.ok) throw new Error(await readError(analysisResponse))
      setAnalysis(await analysisResponse.json())

      void fetchEvaluation()

      try {
        await prepareRepositoryProposal(created.id)
      } catch (repositoryError) {
        setSafeStopReason(repositoryError instanceof Error ? repositoryError.message : 'Live GitHub evidence is unavailable.')
        setPhase('SAFE_STOP')
        setCurrentAction('Safe stop: live repository evidence could not be verified.')
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Judge Mode could not complete the golden flow.')
      setPhase('ERROR')
      setCurrentAction('Demo stopped. No hidden success was reported.')
    } finally {
      setBusy(false)
    }
  }

  async function retryEvidence() {
    if (!incident) return
    setBusy(true)
    setError('')
    setSafeStopReason('')
    setContext(null)
    setCandidate(null)
    setProposal(null)
    setExecution(null)
    setCi(null)
    setLiveWriteArmed(false)
    setPhase('RUNNING')
    try {
      await prepareRepositoryProposal(incident.id)
    } catch (requestError) {
      setSafeStopReason(requestError instanceof Error ? requestError.message : 'Live repository evidence is unavailable.')
      setPhase('SAFE_STOP')
      setCurrentAction('Safe stop: live repository evidence could not be verified.')
    } finally {
      setBusy(false)
    }
  }

  async function decide(decision: 'APPROVE' | 'REJECT') {
    if (!incident || !proposal) return
    if (decision === 'APPROVE' && !liveWriteArmed) return

    setBusy(true)
    setError('')
    setCurrentAction(decision === 'APPROVE'
      ? 'Human approval received. Revalidating exact state, validating the patch and creating only an isolated Draft PR if green…'
      : 'Recording the human rejection without writing the proposed patch…')

    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incident.id}/patch-decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          proposal,
          reviewer: 'judge-mode-human',
          note: decision === 'APPROVE'
            ? 'Explicitly armed and approved from Judge Mode after reviewing the exact proposal.'
            : 'Rejected from Judge Mode to demonstrate the human-control boundary.',
        }),
      })
      if (!response.ok) throw new Error(await readError(response))
      const result: ExecutionResult = await response.json()
      setExecution(result)
      setPhase(decision === 'APPROVE' ? 'EXECUTED' : 'REJECTED')
      setCurrentAction(result.message)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The human decision could not be recorded.')
      setPhase('ERROR')
      setCurrentAction('Decision failed closed. No success was assumed.')
    } finally {
      setBusy(false)
    }
  }

  async function verifyCI() {
    if (!incident) return
    setBusy(true)
    setError('')
    setCurrentAction('Reading real GitHub check-runs and commit status…')
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incident.id}/patch-verification`)
      if (!response.ok) throw new Error(await readError(response))
      const result: CIVerification = await response.json()
      setCi(result)
      setCurrentAction(result.message)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'GitHub CI verification failed.')
      setCurrentAction('CI status is unavailable. Missing checks are not treated as success.')
    } finally {
      setBusy(false)
    }
  }

  async function copyIncidentId() {
    if (!incident) return
    try {
      await navigator.clipboard.writeText(incident.id)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1600)
    } catch {
      setCopied(false)
    }
  }

  return (
    <main className="judge-page">
      <header className="judge-topbar">
        <a href="/" className="judge-back"><ArrowLeft size={16} /> Incident Command</a>
        <div className="judge-top-actions">
          <a href="/readiness"><ShieldCheck size={15} /> Readiness</a>
          <a href="/evaluation"><Activity size={15} /> Evaluation Lab</a>
        </div>
      </header>

      <section className="judge-hero">
        <div>
          <p className="judge-eyebrow"><Sparkles size={14} /> JUDGE MODE · CONTROLLED GOLDEN FLOW</p>
          <h1>From bug report to a review-ready fix — without hiding the safety gates.</h1>
          <p>One guided path demonstrates routing, evidence, RCA, exact patch review and optional live remediation. The default run is read-only through patch proposal; repository writes require a second explicit human action.</p>
          <div className="judge-hero-actions">
            <button className="judge-primary" type="button" onClick={() => void runGoldenDemo()} disabled={busy}>
              {busy && phase === 'RUNNING' ? <><Loader2 className="spin" size={17} /> Running golden flow…</> : <><Activity size={17} /> Start golden demo</>}
            </button>
            <button className="judge-secondary" type="button" onClick={resetDemo} disabled={busy}>
              <RefreshCw size={16} /> Reset view
            </button>
          </div>
        </div>

        <aside className="judge-trust-card">
          <span className={readiness?.mode === 'FALLBACK_DEMO' ? 'judge-mode-badge fallback' : 'judge-mode-badge live'}>
            {readiness?.mode ?? 'NOT CHECKED'}
          </span>
          <div><small>Backend API</small><strong>{API_BASE}</strong></div>
          <div><small>Repository write</small><strong>{proposal && liveWriteArmed ? 'ARMED BY HUMAN' : 'LOCKED BY DEFAULT'}</strong></div>
          <div><small>Auto merge/deploy</small><strong>DISABLED</strong></div>
        </aside>
      </section>

      <section className="judge-status-strip">
        <div className={`judge-phase ${phase.toLowerCase()}`}>
          {busy ? <Loader2 className="spin" size={17} /> : phase === 'ERROR' ? <XCircle size={17} /> : phase === 'SAFE_STOP' ? <TriangleAlert size={17} /> : <CheckCircle2 size={17} />}
          <span>{phase.replace('_', ' ')}</span>
        </div>
        <p>{currentAction}</p>
        {incident && <button type="button" onClick={() => void copyIncidentId()}>{copied ? 'Copied' : `Incident ${incident.id}`}</button>}
      </section>

      {error && <div className="judge-alert error"><XCircle size={18} /><div><b>Stopped without claiming success</b><span>{error}</span></div></div>}
      {safeStopReason && <div className="judge-alert warning"><TriangleAlert size={18} /><div><b>Fail-closed result</b><span>{safeStopReason}</span></div><button type="button" onClick={() => void retryEvidence()} disabled={busy}><RefreshCw size={15} /> Retry live evidence</button></div>}

      <section className="judge-grid">
        <article className="judge-card judge-flow-card">
          <div className="judge-card-title"><Activity size={18} /> Golden-flow progress</div>
          <div className="judge-step-list">
            {steps.map((step, index) => (
              <div className={`judge-step ${step.reached ? 'reached' : ''} ${step.attention ? 'attention' : ''}`} key={step.label}>
                <span className="judge-step-number">{step.reached ? <CheckCircle2 size={16} /> : index + 1}</span>
                <div><b>{step.label}</b><small>{step.detail}</small></div>
              </div>
            ))}
          </div>
        </article>

        <article className="judge-card judge-proof-card">
          <div className="judge-card-title"><ShieldCheck size={18} /> Proof surfaces</div>
          <div className="judge-proof-grid">
            <div><small>Readiness</small><strong>{readiness?.status ?? '—'}</strong><span>{readiness?.mode ?? 'Run demo first'}</span></div>
            <div><small>Routing</small><strong>{incident?.triage.component ?? '—'}</strong><span>{incident?.triage.owner_team ?? 'Awaiting incident'}</span></div>
            <div><small>RCA</small><strong>{topHypothesis ? `${Math.round(topHypothesis.confidence * 100)}%` : '—'}</strong><span>{topHypothesis?.title ?? 'Awaiting analysis'}</span></div>
            <div><small>Benchmark</small><strong>{evaluation ? `${Math.round(evaluation.overall_score * 100)}%` : '—'}</strong><span>{evaluation ? `${benchmarkPasses}/${evaluation.cases.length} checks · ${evaluation.benchmark_version}` : 'Measured separately'}</span></div>
          </div>
          <div className="judge-proof-links">
            <a href="/evidence"><GitBranch size={15} /> Open Evidence Lab</a>
            <a href="/evaluation"><Activity size={15} /> Open measured benchmark</a>
            <a href="/readiness"><ShieldCheck size={15} /> Open readiness report</a>
          </div>
        </article>
      </section>

      {(analysis || context || proposal) && (
        <section className="judge-grid judge-detail-grid">
          <article className="judge-card">
            <div className="judge-card-title"><GitBranch size={18} /> Evidence + root cause</div>
            {topHypothesis ? (
              <div className="judge-rca">
                <div className="judge-rca-head"><b>{topHypothesis.title}</b><span>{Math.round(topHypothesis.confidence * 100)}%</span></div>
                <p>{topHypothesis.rationale}</p>
                <small>Next diagnostic: {topHypothesis.next_diagnostic}</small>
              </div>
            ) : <p className="judge-muted">No hypothesis was forced from insufficient evidence.</p>}

            {candidate && (
              <div className="judge-candidate">
                <small>Strongest exact code candidate</small>
                <b>{candidate.filename}</b>
                <code>{candidate.commit.short_sha} · {candidate.header}</code>
                <span>Correlation {Math.round(candidate.correlation_score * 100)}% · guidance, not causal proof</span>
                <a href={candidate.commit.url} target="_blank" rel="noreferrer">View real commit <ExternalLink size={13} /></a>
              </div>
            )}
          </article>

          <article className="judge-card">
            <div className="judge-card-title"><FileCode2 size={18} /> Exact patch review</div>
            {proposal ? (
              <>
                <div className="judge-proposal-meta">
                  <div><small>Proposal</small><strong>{proposal.proposal_id}</strong></div>
                  <div><small>File</small><strong>{proposal.file_path}</strong></div>
                  <div><small>Confidence</small><strong>{Math.round(proposal.confidence * 100)}%</strong></div>
                  <div><small>Writes now?</small><strong>{proposal.writes_repository ? 'YES' : 'NO'}</strong></div>
                </div>
                <pre className="judge-diff">{proposal.diff_preview}</pre>
                <p className="judge-muted">{proposal.rationale}</p>
              </>
            ) : <p className="judge-muted">An exact patch appears only after fresh live evidence passes the fail-closed checks.</p>}
          </article>
        </section>
      )}

      {proposal && !execution && (
        <section className="judge-gate">
          <div className="judge-gate-heading">
            <ShieldCheck size={24} />
            <div><p>HUMAN APPROVAL BOUNDARY</p><h2>The read-only demo ends here unless a human deliberately arms repository writes.</h2></div>
          </div>
          <p>Approval may create a real deterministic <code>incident-fix/…</code> branch and a <b>Draft</b> PR after validation. It still cannot merge or deploy production.</p>
          <label className="judge-arm-control">
            <input type="checkbox" checked={liveWriteArmed} onChange={(event) => setLiveWriteArmed(event.target.checked)} />
            <span><b>Arm live remediation</b><small>I reviewed the exact patch above and understand that approval performs a real bounded repository write.</small></span>
          </label>
          <div className="judge-gate-actions">
            <button className="judge-reject" type="button" onClick={() => void decide('REJECT')} disabled={busy}><XCircle size={16} /> Reject proposal</button>
            <button className="judge-primary" type="button" onClick={() => void decide('APPROVE')} disabled={busy || !liveWriteArmed}>
              {busy ? <Loader2 className="spin" size={16} /> : <ShieldCheck size={16} />} Approve & validate live remediation
            </button>
          </div>
        </section>
      )}

      {execution && (
        <section className="judge-card judge-result-card">
          <div className="judge-card-title"><GitPullRequest size={19} /> Human decision result</div>
          <div className="judge-result-grid">
            <div><small>Decision</small><strong>{execution.decision}</strong></div>
            <div><small>Status</small><strong>{execution.status}</strong></div>
            <div><small>Branch</small><strong>{execution.branch ?? 'No branch written'}</strong></div>
            <div><small>Draft PR</small><strong>{execution.draft_pr_number ? `#${execution.draft_pr_number}` : 'Not created'}</strong></div>
          </div>
          <p>{execution.message}</p>
          <div className="judge-result-actions">
            {execution.draft_pr_url && <a href={execution.draft_pr_url} target="_blank" rel="noreferrer"><GitPullRequest size={15} /> Open real Draft PR <ExternalLink size={13} /></a>}
            {execution.draft_pr_number && <button type="button" onClick={() => void verifyCI()} disabled={busy}><RefreshCw size={15} /> Check live CI status</button>}
          </div>
        </section>
      )}

      {ci && (
        <section className={`judge-card judge-ci ${ci.status.toLowerCase()}`}>
          <div className="judge-card-title"><ShieldCheck size={19} /> Real GitHub CI · {ci.status}</div>
          <p>{ci.message}</p>
          <div className="judge-ci-checks">
            {ci.checks.map((check) => (
              <div key={`${check.name}-${check.details_url ?? ''}`}>
                <span>{check.name}</span><b>{check.conclusion ?? check.status}</b>
                {check.details_url && <a href={check.details_url} target="_blank" rel="noreferrer"><ExternalLink size={13} /></a>}
              </div>
            ))}
          </div>
          <p className="judge-truth">CI PASS means configured checks passed. It does not auto-merge, deploy production, or claim the production incident is resolved.</p>
        </section>
      )}

      <footer className="judge-footer">
        <span>Live evidence is treated as untrusted data and recognized credential patterns are redacted before UI exposure.</span>
        <span>Reset only clears this presentation view; previously created incidents remain in the audit history.</span>
      </footer>
    </main>
  )
}
