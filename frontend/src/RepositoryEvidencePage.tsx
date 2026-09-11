import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, ExternalLink, FileCode2, GitBranch, Loader2, Search, ShieldCheck } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type IncidentSummary = {
  id: string
  title: string
  status: string
  severity: string
  component: string
  owner_team: string
  updated_at: string
}

type DiffHunk = {
  filename: string
  header: string
  added_lines: string[]
  removed_lines: string[]
  matched_terms: string[]
  source_context: Array<{
    line_number: number
    content: string
    in_hunk: boolean
  }>
  correlation_score: number
}

type CommitEvidence = {
  sha: string
  short_sha: string
  message: string
  author: string
  authored_at?: string | null
  url: string
  files: Array<{
    filename: string
    status: string
    additions: number
    deletions: number
    changes: number
  }>
  suspicious_hunks: DiffHunk[]
  correlation_score: number
}

type RepositoryContext = {
  repository: string
  default_branch: string
  fetched_at: string
  authenticated: boolean
  source: string
  commits: CommitEvidence[]
  open_issues: Array<{
    number: number
    title: string
    state: string
    url: string
    labels: string[]
  }>
  notes: string[]
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

export default function RepositoryEvidencePage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([])
  const [incidentId, setIncidentId] = useState('')
  const [context, setContext] = useState<RepositoryContext | null>(null)
  const [proposal, setProposal] = useState<PatchProposal | null>(null)
  const [proposalLoadingKey, setProposalLoadingKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    void loadIncidents()
  }, [])

  async function loadIncidents() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents?limit=30`)
      if (!response.ok) return
      const payload: IncidentSummary[] = await response.json()
      setIncidents(payload)
      if (payload.length > 0) setIncidentId((current) => current || payload[0].id)
    } catch {
      setError('Backend is unavailable. Start the FastAPI service and retry.')
    }
  }

  async function inspectRepository() {
    if (!incidentId) return
    setLoading(true)
    setError('')
    setContext(null)
    setProposal(null)
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/repository-context`)
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || `Repository investigation failed with ${response.status}`)
      }
      setContext(await response.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Repository investigation failed.')
    } finally {
      setLoading(false)
    }
  }

  async function preparePatchProposal(hunk: DiffHunk, commit: CommitEvidence) {
    if (!incidentId) return
    const key = `${commit.sha}:${hunk.filename}:${hunk.header}`
    setProposalLoadingKey(key)
    setProposal(null)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents/${incidentId}/patch-proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          commit_sha: commit.sha,
          filename: hunk.filename,
          hunk_header: hunk.header,
        }),
      })
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || `Patch proposal failed with ${response.status}`)
      }
      setProposal(await response.json())
      window.setTimeout(() => document.getElementById('patch-proposal')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 40)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Patch proposal failed.')
    } finally {
      setProposalLoadingKey('')
    }
  }

  const topHunks = useMemo(() => {
    if (!context) return []
    return context.commits
      .flatMap((commit) => commit.suspicious_hunks.map((hunk) => ({ ...hunk, commit })))
      .sort((a, b) => b.correlation_score - a.correlation_score)
      .slice(0, 8)
  }, [context])

  return (
    <main className="evidence-page">
      <header className="evidence-topbar">
        <a className="back-link" href="/"><ArrowLeft size={16} /> Incident Command</a>
        <div className="live-evidence-badge"><span /> LIVE READ-ONLY GITHUB EVIDENCE</div>
      </header>

      <section className="evidence-hero">
        <div>
          <p className="evidence-eyebrow">ENGINEERING EVIDENCE LAB</p>
          <h1>Trace an incident to the exact code changes worth inspecting.</h1>
          <p>Recent GitHub commits, real unified-diff hunks and bounded source context are ranked against incident symptoms. Scores prioritize investigation; they never claim causal proof.</p>
        </div>
        <div className="evidence-guardrail"><ShieldCheck size={20} /><div><b>Read-only investigation</b><span>Patch proposals are previews only. No branch, file, PR, merge or deployment is modified from this screen.</span></div></div>
      </section>

      <section className="evidence-control-card">
        <label>
          <span>Incident</span>
          <select value={incidentId} onChange={(event) => { setIncidentId(event.target.value); setProposal(null) }}>
            <option value="">Select an incident</option>
            {incidents.map((incident) => (
              <option key={incident.id} value={incident.id}>{incident.id} · {incident.component} · {incident.title}</option>
            ))}
          </select>
        </label>
        <button type="button" onClick={() => void inspectRepository()} disabled={!incidentId || loading}>
          {loading ? <><Loader2 className="spin" size={16} /> Inspecting GitHub…</> : <><Search size={16} /> Inspect live repository</>}
        </button>
      </section>

      {error && <div className="evidence-error">{error}</div>}

      {context && (
        <>
          <section className="repo-overview-card">
            <div><small>Repository</small><strong>{context.repository}</strong></div>
            <div><small>Default branch</small><strong>{context.default_branch}</strong></div>
            <div><small>GitHub access</small><strong>{context.authenticated ? 'Authenticated' : 'Public read-only'}</strong></div>
            <div><small>Evidence source</small><strong>{context.source}</strong></div>
          </section>

          <section className="evidence-section">
            <div className="section-heading">
              <div><span className="section-icon"><GitBranch size={17} /></span><div><h2>Correlated commits</h2><p>Recent commits ranked against the active incident.</p></div></div>
              <b>{context.commits.length} inspected</b>
            </div>
            <div className="commit-evidence-grid">
              {context.commits.map((commit, index) => (
                <article className={index === 0 ? 'commit-evidence-card top-commit' : 'commit-evidence-card'} key={commit.sha}>
                  <div className="commit-rank"><span>#{index + 1}</span><b>{Math.round(commit.correlation_score * 100)}%</b></div>
                  <code>{commit.short_sha}</code>
                  <h3>{commit.message}</h3>
                  <p>{commit.author} · {commit.files.length} changed file{commit.files.length === 1 ? '' : 's'} · {commit.suspicious_hunks.length} ranked hunk{commit.suspicious_hunks.length === 1 ? '' : 's'}</p>
                  <div className="changed-file-list">
                    {commit.files.slice(0, 6).map((file) => (
                      <span key={file.filename}>{file.filename}<small>+{file.additions} −{file.deletions}</small></span>
                    ))}
                  </div>
                  <a href={commit.url} target="_blank" rel="noreferrer">Open commit on GitHub <ExternalLink size={13} /></a>
                </article>
              ))}
            </div>
          </section>

          <section className="evidence-section">
            <div className="section-heading">
              <div><span className="section-icon"><FileCode2 size={17} /></span><div><h2>Ranked diff hunks</h2><p>The exact code regions with the strongest symptom overlap.</p></div></div>
              <b>{topHunks.length} surfaced</b>
            </div>

            {topHunks.length === 0 ? (
              <div className="no-hunks">GitHub did not return usable patch hunks for these recent commits. No diff evidence was invented.</div>
            ) : (
              <div className="hunk-stack">
                {topHunks.map((hunk, index) => {
                  const proposalKey = `${hunk.commit.sha}:${hunk.filename}:${hunk.header}`
                  return (
                    <article className="hunk-card" key={`${hunk.commit.sha}-${hunk.filename}-${hunk.header}-${index}`}>
                      <div className="hunk-topline">
                        <div><span>#{index + 1}</span><strong>{hunk.filename}</strong></div>
                        <b>{Math.round(hunk.correlation_score * 100)}% hunk correlation</b>
                      </div>
                      <code className="hunk-header">{hunk.header}</code>
                      {hunk.matched_terms.length > 0 && (
                        <div className="matched-term-row">Matched incident terms: {hunk.matched_terms.map((term) => <span key={term}>{term}</span>)}</div>
                      )}
                      <div className="diff-preview">
                        <div className="removed-lines">
                          <small>REMOVED BY ORIGINAL COMMIT</small>
                          {hunk.removed_lines.length === 0 ? <pre>—</pre> : hunk.removed_lines.map((line, lineIndex) => <pre key={`r-${lineIndex}`}>− {line}</pre>)}
                        </div>
                        <div className="added-lines">
                          <small>ADDED BY ORIGINAL COMMIT</small>
                          {hunk.added_lines.length === 0 ? <pre>—</pre> : hunk.added_lines.map((line, lineIndex) => <pre key={`a-${lineIndex}`}>+ {line}</pre>)}
                        </div>
                      </div>
                      {hunk.source_context.length > 0 && (
                        <div className="source-context-block">
                          <div className="source-context-title"><FileCode2 size={14} /><b>Source context at commit {hunk.commit.short_sha}</b><span>bounded read</span></div>
                          <div className="source-code-window">
                            {hunk.source_context.map((line) => (
                              <div className={line.in_hunk ? 'source-line source-line-active' : 'source-line'} key={line.line_number}>
                                <span>{line.line_number}</span><code>{line.content || ' '}</code>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <footer>
                        <span>Commit {hunk.commit.short_sha}</span>
                        <div className="hunk-actions">
                          {hunk.source_context.length > 0 && hunk.added_lines.length > 0 && (
                            <button
                              type="button"
                              className="patch-proposal-button"
                              disabled={proposalLoadingKey === proposalKey}
                              onClick={() => void preparePatchProposal(hunk, hunk.commit)}
                            >
                              {proposalLoadingKey === proposalKey ? <><Loader2 className="spin" size={13} /> Preparing…</> : <><FileCode2 size={13} /> Prepare patch proposal</>}
                            </button>
                          )}
                          <a href={hunk.commit.url} target="_blank" rel="noreferrer">Review full diff <ExternalLink size={13} /></a>
                        </div>
                      </footer>
                    </article>
                  )
                })}
              </div>
            )}
          </section>

          {proposal && (
            <section className="evidence-section patch-proposal-section" id="patch-proposal">
              <div className="section-heading">
                <div><span className="section-icon"><ShieldCheck size={17} /></span><div><h2>Bounded patch proposal</h2><p>Exact before/after replacement prepared for human review. Repository writes remain disabled.</p></div></div>
                <b>{Math.round(proposal.confidence * 100)}% proposal confidence</b>
              </div>

              <div className="proposal-meta-grid">
                <div><small>Proposal</small><strong>{proposal.proposal_id}</strong></div>
                <div><small>File</small><strong>{proposal.file_path}</strong></div>
                <div><small>Base commit</small><strong>{proposal.base_commit.slice(0, 12)}</strong></div>
                <div><small>Start line</small><strong>{proposal.line_start}</strong></div>
              </div>

              <div className="proposal-readonly-banner"><ShieldCheck size={16} /><div><b>NO REPOSITORY WRITE</b><span>This stage only prepares a reviewable candidate. No branch or file has been changed.</span></div></div>

              <p className="proposal-rationale">{proposal.rationale}</p>

              <div className="proposal-before-after">
                <div>
                  <small>CURRENT LINES</small>
                  {proposal.before_lines.length === 0 ? <pre>—</pre> : proposal.before_lines.map((line, index) => <pre key={`before-${index}`}>− {line}</pre>)}
                </div>
                <div>
                  <small>PROPOSED REPLACEMENT</small>
                  {proposal.after_lines.length === 0 ? <pre>(delete the selected current lines)</pre> : proposal.after_lines.map((line, index) => <pre key={`after-${index}`}>+ {line}</pre>)}
                </div>
              </div>

              <div className="proposal-diff-block">
                <small>DIFF PREVIEW</small>
                <pre>{proposal.diff_preview}</pre>
              </div>

              <div className="proposal-verification">
                <b>Checks required before a draft PR may be created</b>
                {proposal.verification_commands.map((command) => <code key={command}>{command}</code>)}
              </div>

              <div className="proposal-warning-list">
                {proposal.warnings.map((warning) => <span key={warning}>• {warning}</span>)}
              </div>
            </section>
          )}

          {context.open_issues.length > 0 && (
            <section className="evidence-section">
              <div className="section-heading"><div><span className="section-icon"><ExternalLink size={17} /></span><div><h2>Open repository issues</h2><p>Current tracking context from the same repository.</p></div></div></div>
              <div className="open-issue-grid">
                {context.open_issues.map((issue) => (
                  <a href={issue.url} target="_blank" rel="noreferrer" key={issue.number}><b>#{issue.number}</b><span>{issue.title}</span><ExternalLink size={13} /></a>
                ))}
              </div>
            </section>
          )}

          <div className="evidence-notes">
            {context.notes.map((note) => <span key={note}>• {note}</span>)}
          </div>
        </>
      )}
    </main>
  )
}
