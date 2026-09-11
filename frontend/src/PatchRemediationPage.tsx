import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, CheckCircle2, ExternalLink, FileCode2, GitPullRequest, Loader2, ShieldCheck, XCircle } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type IncidentSummary = {
  id: string
  title: string
  status: string
  severity: string
  component: string
}

type DiffHunk = {
  filename: string
  header: string
  added_lines: string[]
  removed_lines: string[]
  matched_terms: string[]
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
  commits: CommitEvidence[]
}

type PatchProposal = {
  proposal_id: string
  incident_id: string
  repository: string
  base_commit: string
  file_path: string
  hunk_header: string
  strategy: string
  line_start: number
  before_lines: string[]
  after_lines: string[]
  diff_preview: string
  rationale: string
  confidence: number
  verification_commands: string[]
  warnings: string[]
  writes_repository: boolean
}

type ValidationCheck = {
  name: string
  command: string
  status: string
  exit_code?: number | null
  output: string
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
  validation: ValidationCheck[]
  incident_status: string
}

type Candidate = DiffHunk & { commit: CommitEvidence }

async function readError(response: Response) {
  try {
    const payload = await response.json()
    return payload.detail ?? JSON.stringify(payload)
  } catch {
    return response.text()
  }
}

export default function PatchRemediationPage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([])
  const [incidentId, setIncidentId] = useState('')
  const [context, setContext] = useState<RepositoryContext | null>(null)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [proposal, setProposal] = useState<PatchProposal | null>(null)
  const [result, setResult] = useState<ExecutionResult | null>(null)
  const [reviewer, setReviewer] = useState('human-reviewer')
  const [note, setNote] = useState('Reviewed exact before/after replacement and validation gate.')
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    void (async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/incidents?limit=50`)
        if (!response.ok) return
        const payload: IncidentSummary[] = await response.json()
        setIncidents(payload)
        if (payload.length) setIncidentId(payload[0].id)
      } catch {
        setError('Backend unavailable. Start FastAPI on port 8000.')
      }
    })()
  }, [])

  const eligibleCandidates = useMemo(() => {
    if (!context) return [] as Candidate[]
    return context.commits
      .flatMap((commit) => commit.suspicious_hunks.map((hunk) => ({ ...hunk, commit })))
      .filter((hunk) => hunk.added_lines.length > 0 && hunk.source_context.length > 0)
      .sort((a, b) => b.correlation_score - a.correlation_score)
  }, [context])

  async function inspect() {
    if (!incidentId) return
    setLoading('inspect')
    setError('')
    setContext(null)
    setCandidate(null)
    setProposal(null)
    setResult(null)
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/repository-context`)
      if (!response.ok) throw new Error(await readError(response))
      const payload: RepositoryContext = await response.json()
      setContext(payload)
      const best = payload.commits
        .flatMap((commit) => commit.suspicious_hunks.map((hunk) => ({ ...hunk, commit })))
        .filter((hunk) => hunk.added_lines.length > 0 && hunk.source_context.length > 0)
        .sort((a, b) => b.correlation_score - a.correlation_score)[0]
      setCandidate(best ?? null)
      if (!best) setError('No safe patch candidate has both exact added lines and bounded current source context. Refresh evidence or choose another incident.')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Live repository inspection failed.')
    } finally {
      setLoading('')
    }
  }

  async function prepareProposal() {
    if (!incidentId || !candidate) return
    setLoading('proposal')
    setError('')
    setProposal(null)
    setResult(null)
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/patch-proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          commit_sha: candidate.commit.sha,
          filename: candidate.filename,
          hunk_header: candidate.header,
        }),
      })
      if (!response.ok) throw new Error(await readError(response))
      setProposal(await response.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Patch proposal failed.')
    } finally {
      setLoading('')
    }
  }

  async function decide(decision: 'APPROVE' | 'REJECT') {
    if (!incidentId || !proposal) return
    setLoading(decision === 'APPROVE' ? 'approve' : 'reject')
    setError('')
    setResult(null)
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/patch-decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, proposal, reviewer, note }),
      })
      if (!response.ok) throw new Error(await readError(response))
      setResult(await response.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Patch decision failed.')
    } finally {
      setLoading('')
    }
  }

  return (
    <main className="remediation-page">
      <header className="remediation-topbar">
        <a href="/evidence"><ArrowLeft size={16} /> Evidence Lab</a>
        <span><ShieldCheck size={14} /> HUMAN-GATED LIVE REMEDIATION</span>
      </header>

      <section className="remediation-hero">
        <p>REMEDIATION STUDIO</p>
        <h1>Turn repository evidence into a tested draft pull request.</h1>
        <div>Nothing is written until you approve the exact proposal. Approval creates an isolated branch, applies only the reviewed replacement, runs deterministic checks, and opens a <b>draft</b> PR only when the checks pass.</div>
      </section>

      <section className="remediation-card remediation-controls">
        <label>
          <span>Incident</span>
          <select value={incidentId} onChange={(event) => { setIncidentId(event.target.value); setContext(null); setCandidate(null); setProposal(null); setResult(null) }}>
            <option value="">Select incident</option>
            {incidents.map((incident) => <option value={incident.id} key={incident.id}>{incident.id} · {incident.component} · {incident.title}</option>)}
          </select>
        </label>
        <button onClick={() => void inspect()} disabled={!incidentId || Boolean(loading)}>
          {loading === 'inspect' ? <><Loader2 className="spin" size={15} /> Inspecting live GitHub…</> : <><FileCode2 size={15} /> Find safest patch candidate</>}
        </button>
      </section>

      {error && <div className="remediation-error">{error}</div>}

      {context && (
        <section className="remediation-card live-context-strip">
          <div><small>Repository</small><b>{context.repository}</b></div>
          <div><small>Base branch</small><b>{context.default_branch}</b></div>
          <div><small>Authentication</small><b>{context.authenticated ? 'Authenticated read' : 'Public read'}</b></div>
          <div><small>Eligible candidates</small><b>{eligibleCandidates.length}</b></div>
        </section>
      )}

      {candidate && !proposal && (
        <section className="remediation-card candidate-card">
          <div className="remediation-heading">
            <div><FileCode2 size={18} /><span><b>Top bounded candidate</b><small>Review the repository evidence before generating a replacement.</small></span></div>
            <strong>{Math.round(candidate.correlation_score * 100)}%</strong>
          </div>
          <code>{candidate.filename}</code>
          <p>{candidate.commit.short_sha} · {candidate.commit.message}</p>
          <div className="candidate-diff">
            <div><small>ORIGINAL COMMIT REMOVED</small>{candidate.removed_lines.map((line, i) => <pre key={i}>− {line}</pre>)}</div>
            <div><small>ORIGINAL COMMIT ADDED</small>{candidate.added_lines.map((line, i) => <pre key={i}>+ {line}</pre>)}</div>
          </div>
          <button className="primary-remediation" onClick={() => void prepareProposal()} disabled={Boolean(loading)}>
            {loading === 'proposal' ? <><Loader2 className="spin" size={15} /> Revalidating exact source…</> : 'Generate exact reviewable proposal'}
          </button>
        </section>
      )}

      {proposal && (
        <section className="remediation-card proposal-review-card">
          <div className="remediation-heading">
            <div><ShieldCheck size={18} /><span><b>Exact proposal awaiting your decision</b><small>{proposal.proposal_id} · no write has happened yet</small></span></div>
            <strong>{Math.round(proposal.confidence * 100)}%</strong>
          </div>

          <div className="proposal-facts">
            <span><small>File</small><b>{proposal.file_path}</b></span>
            <span><small>Investigated commit</small><b>{proposal.base_commit.slice(0, 12)}</b></span>
            <span><small>Start line</small><b>{proposal.line_start}</b></span>
            <span><small>Strategy</small><b>{proposal.strategy}</b></span>
          </div>

          <p>{proposal.rationale}</p>
          <div className="candidate-diff approved-preview">
            <div><small>CURRENT LINES</small>{proposal.before_lines.map((line, i) => <pre key={i}>− {line}</pre>)}</div>
            <div><small>APPROVED REPLACEMENT CANDIDATE</small>{proposal.after_lines.length ? proposal.after_lines.map((line, i) => <pre key={i}>+ {line}</pre>) : <pre>(delete selected lines)</pre>}</div>
          </div>
          <div className="full-diff"><small>EXACT DIFF PREVIEW</small><pre>{proposal.diff_preview}</pre></div>

          <div className="validation-plan">
            <b>Validation gate before draft PR</b>
            {proposal.verification_commands.map((command) => <code key={command}>{command}</code>)}
          </div>

          <div className="review-fields">
            <label><span>Reviewer</span><input value={reviewer} onChange={(event) => setReviewer(event.target.value)} /></label>
            <label><span>Review note</span><input value={note} onChange={(event) => setNote(event.target.value)} /></label>
          </div>

          <div className="approval-warning"><ShieldCheck size={16} /><span><b>Approve means a real GitHub write.</b> The backend will revalidate the proposal first, create an isolated `incident-fix/...` branch, apply only these exact lines, run checks, and create a DRAFT PR only if validation passes. It will never merge or deploy.</span></div>

          <div className="decision-row">
            <button className="reject-button" onClick={() => void decide('REJECT')} disabled={Boolean(loading)}>
              {loading === 'reject' ? <Loader2 className="spin" size={15} /> : <XCircle size={15} />} Reject proposal
            </button>
            <button className="approve-button" onClick={() => void decide('APPROVE')} disabled={Boolean(loading) || reviewer.trim().length < 2}>
              {loading === 'approve' ? <><Loader2 className="spin" size={15} /> Applying + running checks…</> : <><GitPullRequest size={15} /> Approve, validate & create draft PR</>}
            </button>
          </div>
          {loading === 'approve' && <div className="long-running-note">Real validation can take a few minutes, especially for a frontend build. Keep this page open.</div>}
        </section>
      )}

      {result && (
        <section className={`remediation-card execution-result result-${result.status.toLowerCase()}`}>
          <div className="remediation-heading">
            <div>{result.status === 'DRAFT_PR_CREATED' ? <CheckCircle2 size={20} /> : result.status === 'REJECTED' ? <XCircle size={20} /> : <ShieldCheck size={20} />}<span><b>{result.status.replaceAll('_', ' ')}</b><small>{result.message}</small></span></div>
          </div>

          {(result.branch || result.draft_pr_url) && <div className="result-links">
            {result.branch_url && <a href={result.branch_url} target="_blank" rel="noreferrer">Open isolated fix branch <ExternalLink size={13} /></a>}
            {result.draft_pr_url && <a className="pr-link" href={result.draft_pr_url} target="_blank" rel="noreferrer"><GitPullRequest size={14} /> Open Draft PR #{result.draft_pr_number} <ExternalLink size={13} /></a>}
          </div>}

          {result.validation.length > 0 && <div className="validation-results">
            <h3>Real validation results</h3>
            {result.validation.map((check, index) => (
              <article key={`${check.name}-${index}`} className={check.status === 'PASS' ? 'check-pass' : 'check-fail'}>
                <div>{check.status === 'PASS' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}<b>{check.name}</b><span>{check.status}</span></div>
                <code>{check.command}</code>
                {check.output && <pre>{check.output}</pre>}
              </article>
            ))}
          </div>}
        </section>
      )}
    </main>
  )
}
