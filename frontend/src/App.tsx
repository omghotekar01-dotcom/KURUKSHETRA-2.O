import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  GitBranch,
  Github,
  History,
  Loader2,
  ShieldCheck,
  Sparkles,
  XCircle,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const stages = ['Intake', 'Triage', 'Evidence', 'RCA', 'Remediation', 'Approval', 'Verification']

type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
type IncidentStatus = 'NEW' | 'TRIAGING' | 'INVESTIGATING' | 'RCA_READY' | 'REMEDIATION_READY' | 'AWAITING_APPROVAL' | 'EXECUTING' | 'VERIFYING' | 'RESOLVED' | 'ESCALATED'
type ProposedAction = { action_type: string; target: string; description: string; confidence: number; destructive: boolean }
type RiskDecision = { risk: 'LOW' | 'MEDIUM' | 'HIGH'; policy: string; reason: string; requires_human_approval: boolean }

type IncidentRecord = {
  id: string
  status: IncidentStatus
  created_at: string
  updated_at: string
  incident: {
    title: string
    description: string
    environment: string
    repo?: string | null
    logs: string[]
  }
  triage: {
    component: string
    owner_team: string
    severity: Severity
    confidence: number
    summary: string
    signals: string[]
  }
  timeline: Array<{
    timestamp: string
    stage: string
    message: string
    metadata: Record<string, unknown>
  }>
}

type KnowledgeMatch = {
  id: string
  component: string
  issue: string
  fix: string
  source: string
  score: number
}

type EvidenceBundle = {
  incident_id: string
  matches: KnowledgeMatch[]
  no_strong_match: boolean
}

type RepositoryFileChange = {
  filename: string
  status: string
  additions: number
  deletions: number
  changes: number
}

type RepositoryCommitEvidence = {
  sha: string
  short_sha: string
  message: string
  author: string
  authored_at?: string | null
  url: string
  files: RepositoryFileChange[]
  correlation_score: number
}

type RepositoryContext = {
  repository: string
  default_branch: string
  fetched_at: string
  authenticated: boolean
  source: string
  commits: RepositoryCommitEvidence[]
  open_issues: Array<{
    number: number
    title: string
    state: string
    url: string
    labels: string[]
  }>
  notes: string[]
}

type AnalysisBundle = {
  incident_id: string
  evidence: EvidenceBundle
  repository_context?: RepositoryContext | null
  hypotheses: Array<{
    id: string
    title: string
    confidence: number
    evidence_ids: string[]
    rationale: string
    next_diagnostic: string
  }>
  remediation: null | {
    summary: string
    steps: string[]
    verification: string
    proposed_action: ProposedAction | null
    risk: RiskDecision | null
  }
  needs_human_investigation: boolean
}

type ApprovalResult = {
  incident_id: string
  decision: 'APPROVE' | 'REJECT'
  risk: RiskDecision
  execution: null | {
    action_id: string
    incident_id: string
    action_type: string
    target: string
    status: string
    mode: string
    message: string
    external_url?: string | null
  }
  incident_status: IncidentStatus
}

type VerificationResult = {
  incident_id: string
  outcome: 'PASS' | 'FAIL' | 'INCONCLUSIVE'
  incident_status: IncidentStatus
  message: string
}

type IncidentSummary = {
  id: string
  title: string
  status: IncidentStatus
  severity: Severity
  component: string
  owner_team: string
  created_at: string
  updated_at: string
}

const emptyForm = {
  title: '401 errors after today\'s deployment',
  description: 'Production users can authenticate, but API requests immediately return unauthorized responses.',
  environment: 'production',
  repo: 'omghotekar01-dotcom/KURUKSHETRA-2.O',
  logs: 'JWT signature verification failed',
}

export default function App() {
  const [form, setForm] = useState(emptyForm)
  const [incident, setIncident] = useState<IncidentRecord | null>(null)
  const [recent, setRecent] = useState<IncidentSummary[]>([])
  const [analysis, setAnalysis] = useState<AnalysisBundle | null>(null)
  const [approval, setApproval] = useState<ApprovalResult | null>(null)
  const [verification, setVerification] = useState<VerificationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [workflowBusy, setWorkflowBusy] = useState(false)
  const [error, setError] = useState('')

  const activeStageCount = useMemo(() => {
    if (incident?.status === 'RESOLVED' || incident?.status === 'VERIFYING') return 7
    if (approval) return 6
    if (analysis?.remediation) return 5
    if (analysis?.hypotheses.length) return 4
    if (analysis) return 3
    return incident ? 2 : 1
  }, [incident, analysis, approval])

  useEffect(() => {
    void loadRecent()
  }, [])

  async function loadRecent() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents?limit=5`)
      if (!response.ok) return
      setRecent(await response.json())
    } catch {
      // The intake view remains usable even when the backend is offline.
    }
  }

  async function refreshIncident(incidentId: string) {
    const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}`)
    if (response.ok) setIncident(await response.json())
  }

  async function submitIncident(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setAnalysis(null)
    setApproval(null)
    setVerification(null)

    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
          environment: form.environment,
          repo: form.repo.trim() || null,
          logs: form.logs
            .split('\n')
            .map((line) => line.trim())
            .filter(Boolean),
        }),
      })

      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || `Request failed with ${response.status}`)
      }

      const created: IncidentRecord = await response.json()
      setIncident(created)

      const analysisResponse = await fetch(`${API_BASE}/api/v1/incidents/${created.id}/analyze`, { method: 'POST' })
      if (!analysisResponse.ok) {
        const detail = await analysisResponse.text()
        throw new Error(detail || `Analysis failed with ${analysisResponse.status}`)
      }

      const bundle: AnalysisBundle = await analysisResponse.json()
      setAnalysis(bundle)
      await refreshIncident(created.id)
      await loadRecent()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to create incident.')
    } finally {
      setLoading(false)
    }
  }

  async function decideAction(decision: 'APPROVE' | 'REJECT') {
    const action = analysis?.remediation?.proposed_action
    if (!incident || !action) return

    setWorkflowBusy(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incident.id}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          action,
          reviewer: 'Hackathon operator',
          note: decision === 'APPROVE' ? 'Approved from the incident command dashboard.' : 'Rejected from the incident command dashboard.',
        }),
      })
      if (!response.ok) throw new Error(await response.text())
      setApproval(await response.json())
      await refreshIncident(incident.id)
      await loadRecent()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to record approval decision.')
    } finally {
      setWorkflowBusy(false)
    }
  }

  async function verify(outcome: 'PASS' | 'FAIL' | 'INCONCLUSIVE') {
    if (!incident) return

    setWorkflowBusy(true)
    setError('')
    try {
      const evidence = outcome === 'PASS'
        ? analysis?.remediation?.verification ?? 'Verification check completed successfully.'
        : 'Verification did not confirm the expected remediation outcome.'
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incident.id}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ outcome, evidence, checked_by: 'dashboard-verifier' }),
      })
      if (!response.ok) throw new Error(await response.text())
      setVerification(await response.json())
      await refreshIncident(incident.id)
      await loadRecent()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to record verification result.')
    } finally {
      setWorkflowBusy(false)
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Sparkles size={18} /> Incident Command</div>
        <nav>
          <button className="nav-active"><Activity size={16} /> Live Incident</button>
          <button><History size={16} /> Incidents</button>
          <button><GitBranch size={16} /> Evidence</button>
          <button><ShieldCheck size={16} /> Evaluation Lab</button>
        </nav>

        <div className="recent-block">
          <small>Recent incidents</small>
          {recent.length === 0 && <span className="recent-empty">No saved incidents yet</span>}
          {recent.map((item) => (
            <button key={item.id} className="recent-item" type="button">
              <span>{item.title}</span>
              <small>{item.component} · {item.severity} · {item.status}</small>
            </button>
          ))}
        </div>
      </aside>

      <section className="content">
        <header>
          <div>
            <p className="eyebrow">KURUKSHETRA 2.0 · LIVE-FIRST MVP</p>
            <h1>Evidence-backed incident response</h1>
            <p className="muted">Investigate live repository context, authorize bounded actions and verify outcomes through one auditable workflow.</p>
          </div>
          <span className="status">● Live-first build</span>
        </header>

        <section className="stage-row">
          {stages.map((stage, i) => (
            <div key={stage} className={i < activeStageCount ? 'stage active' : 'stage'}>
              <span>{i + 1}</span>{stage}
            </div>
          ))}
        </section>

        <section className="workspace-grid">
          <form className="panel intake-panel" onSubmit={submitIncident}>
            <div className="panel-title">New incident</div>
            <label>
              <span>Title</span>
              <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} minLength={3} maxLength={160} required />
            </label>
            <label>
              <span>Description</span>
              <textarea rows={5} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} minLength={5} required />
            </label>
            <label>
              <span>GitHub repository</span>
              <input
                value={form.repo}
                onChange={(event) => setForm({ ...form, repo: event.target.value })}
                placeholder="owner/repository"
                autoComplete="off"
              />
              <small className="field-help">Used for read-only live commit/file/issue investigation. The configured allowlist is enforced by the backend.</small>
            </label>
            <div className="form-row">
              <label>
                <span>Environment</span>
                <select value={form.environment} onChange={(event) => setForm({ ...form, environment: event.target.value })}>
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </label>
              <label>
                <span>Logs / signals</span>
                <input value={form.logs} onChange={(event) => setForm({ ...form, logs: event.target.value })} />
              </label>
            </div>
            {error && <div className="error-box"><AlertCircle size={16} /> {error}</div>}
            <button className="primary submit-button" disabled={loading || workflowBusy}>
              {loading ? <><Loader2 className="spin" size={16} /> Investigating live context…</> : 'Create & investigate incident'}
            </button>
          </form>

          <section className="result-stack">
            {incident ? (
              <>
                <article className="panel hero-panel">
                  <div className="panel-title">
                    <span>{incident.id}</span>
                    <div className="status-group">
                      <span className={`pill ${incident.triage.severity.toLowerCase()}`}>{incident.triage.severity}</span>
                      <span className="state-pill">{incident.status}</span>
                    </div>
                  </div>
                  <h2>{incident.incident.title}</h2>
                  <p className="muted">{incident.incident.description}</p>
                  <div className="facts">
                    <div><small>Component</small><strong>{incident.triage.component}</strong></div>
                    <div><small>Owner</small><strong>{incident.triage.owner_team}</strong></div>
                    <div><small>Confidence</small><strong>{Math.round(incident.triage.confidence * 100)}%</strong></div>
                  </div>
                </article>

                {analysis && (
                  <article className="panel">
                    <div className="panel-title">Historical evidence <span className="baseline-tag">knowledge memory</span></div>
                    {analysis.evidence.no_strong_match ? (
                      <p className="muted">No sufficiently relevant historical knowledge match was found. Repository evidence is evaluated independently instead of forcing a remembered fix.</p>
                    ) : (
                      <ul className="match-list">
                        {analysis.evidence.matches.map((match) => (
                          <li key={match.id}>
                            <div className="match-head"><b>{match.id} · {match.component}</b><span>{Math.round(match.score * 100)}%</span></div>
                            <p>{match.issue}</p>
                            <small>Known response: {match.fix}</small>
                          </li>
                        ))}
                      </ul>
                    )}
                  </article>
                )}

                {analysis?.repository_context ? (
                  <article className="panel repository-panel">
                    <div className="panel-title">
                      <span className="repo-title"><Github size={16} /> Live GitHub repository evidence</span>
                      <span className="live-badge">LIVE</span>
                    </div>
                    <div className="repo-summary">
                      <div><small>Repository</small><strong>{analysis.repository_context.repository}</strong></div>
                      <div><small>Branch</small><strong>{analysis.repository_context.default_branch}</strong></div>
                      <div><small>Access</small><strong>{analysis.repository_context.authenticated ? 'Authenticated' : 'Public read-only'}</strong></div>
                    </div>

                    <div className="repo-section-title">Recent commits ranked by incident correlation</div>
                    <div className="commit-list">
                      {analysis.repository_context.commits.slice(0, 4).map((commit) => (
                        <a className="commit-card" key={commit.sha} href={commit.url} target="_blank" rel="noreferrer">
                          <div className="commit-card-head">
                            <code>{commit.short_sha}</code>
                            <span>{Math.round(commit.correlation_score * 100)}% correlation</span>
                          </div>
                          <strong>{commit.message}</strong>
                          <small>{commit.author} · {commit.files.length} changed file{commit.files.length === 1 ? '' : 's'}</small>
                          {commit.files.length > 0 && (
                            <div className="file-chip-row">
                              {commit.files.slice(0, 5).map((file) => <span key={file.filename}>{file.filename}</span>)}
                            </div>
                          )}
                        </a>
                      ))}
                    </div>

                    {analysis.repository_context.open_issues.length > 0 && (
                      <>
                        <div className="repo-section-title">Related open repository issues</div>
                        <div className="issue-link-list">
                          {analysis.repository_context.open_issues.slice(0, 4).map((issue) => (
                            <a href={issue.url} target="_blank" rel="noreferrer" key={issue.number}>
                              <span>#{issue.number} · {issue.title}</span><ExternalLink size={13} />
                            </a>
                          ))}
                        </div>
                      </>
                    )}
                    <p className="evidence-disclaimer">Correlation highlights where to investigate first. It does not label a commit as the root cause without verification.</p>
                  </article>
                ) : incident.incident.repo && analysis ? (
                  <article className="panel repository-panel repository-unavailable">
                    <div className="panel-title"><span className="repo-title"><Github size={16} /> Live GitHub repository evidence</span></div>
                    <p className="muted">Live repository context was unavailable for this analysis. The workflow did not fabricate repository evidence; check the incident timeline for the exact provider/policy failure.</p>
                  </article>
                ) : null}

                {analysis?.hypotheses[0] && (
                  <article className="panel analysis-panel">
                    <div className="panel-title">Top root-cause hypothesis <span className="confidence-chip">{Math.round(analysis.hypotheses[0].confidence * 100)}%</span></div>
                    <h3>{analysis.hypotheses[0].title}</h3>
                    <p className="muted">{analysis.hypotheses[0].rationale}</p>
                    <div className="next-check"><b>Next diagnostic</b><span>{analysis.hypotheses[0].next_diagnostic}</span></div>
                  </article>
                )}

                {analysis?.remediation && (
                  <article className="panel remediation-panel">
                    <div className="panel-title">Remediation plan {analysis.remediation.risk && <span className={`pill ${analysis.remediation.risk.risk.toLowerCase()}`}>{analysis.remediation.risk.risk} RISK</span>}</div>
                    <p>{analysis.remediation.summary}</p>
                    <ol className="plan-list">
                      {analysis.remediation.steps.map((step) => <li key={step}>{step}</li>)}
                    </ol>
                    <div className="verification-box"><b>Verification</b><span>{analysis.remediation.verification}</span></div>
                    {analysis.remediation.risk && <small className="policy-note">Policy: {analysis.remediation.risk.policy} · {analysis.remediation.risk.reason}</small>}

                    {incident.status === 'REMEDIATION_READY' && analysis.remediation.proposed_action && (
                      <div className="approval-box">
                        <div>
                          <b>Exact bounded action</b>
                          <span>{analysis.remediation.proposed_action.description}</span>
                        </div>
                        <div className="button-row">
                          <button type="button" className="secondary danger-button" disabled={workflowBusy} onClick={() => void decideAction('REJECT')}>Reject</button>
                          <button type="button" className="primary" disabled={workflowBusy} onClick={() => void decideAction('APPROVE')}>
                            {workflowBusy ? 'Executing…' : 'Approve & execute'}
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                )}

                {approval?.execution && (
                  <article className="panel action-result-panel">
                    <div className="panel-title">Action result <span className="state-pill">{approval.execution.mode}</span></div>
                    <div className="action-result-line"><CheckCircle2 size={18} /><div><b>{approval.execution.status}</b><span>{approval.execution.message}</span></div></div>
                    <small className="policy-note">Action ID: {approval.execution.action_id} · Target: {approval.execution.target}</small>
                    {approval.execution.external_url && (
                      <a className="external-action-link" href={approval.execution.external_url} target="_blank" rel="noreferrer">
                        Open created GitHub resource <ExternalLink size={14} />
                      </a>
                    )}
                  </article>
                )}

                {incident.status === 'VERIFYING' && (
                  <article className="panel verification-panel">
                    <div className="panel-title">Independent verification</div>
                    <p className="muted">Execution alone never closes the incident. Record the outcome of the defined verification check.</p>
                    <div className="button-row verification-actions">
                      <button type="button" className="secondary" disabled={workflowBusy} onClick={() => void verify('INCONCLUSIVE')}>Inconclusive</button>
                      <button type="button" className="secondary danger-button" disabled={workflowBusy} onClick={() => void verify('FAIL')}><XCircle size={15} /> Fail</button>
                      <button type="button" className="primary" disabled={workflowBusy} onClick={() => void verify('PASS')}><CheckCircle2 size={15} /> Pass</button>
                    </div>
                  </article>
                )}

                {verification && (
                  <article className={`panel final-result ${verification.outcome === 'PASS' ? 'success-result' : 'failure-result'}`}>
                    <div className="panel-title">Verification outcome</div>
                    <h3>{verification.outcome} · {verification.incident_status}</h3>
                    <p>{verification.message}</p>
                  </article>
                )}

                <article className="panel">
                  <div className="panel-title">Investigation timeline</div>
                  <ul className="timeline-list">
                    {incident.timeline.map((event, index) => (
                      <li key={`${event.timestamp}-${event.stage}-${index}`}>
                        <b>{event.stage}</b>
                        <span>{event.message}</span>
                      </li>
                    ))}
                  </ul>
                </article>
              </>
            ) : (
              <article className="panel empty-panel">
                <Sparkles size={28} />
                <h2>Ready for the first live incident</h2>
                <p className="muted">Submit an incident with a GitHub repository to create a persisted case, collect live repository evidence and build an auditable RCA workflow.</p>
              </article>
            )}
          </section>
        </section>
      </section>
    </main>
  )
}
