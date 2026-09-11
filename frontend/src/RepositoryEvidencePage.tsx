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

export default function RepositoryEvidencePage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([])
  const [incidentId, setIncidentId] = useState('')
  const [context, setContext] = useState<RepositoryContext | null>(null)
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
          <p>Recent GitHub commits and real unified-diff hunks are ranked against incident symptoms. Scores prioritize investigation; they never claim causal proof.</p>
        </div>
        <div className="evidence-guardrail"><ShieldCheck size={20} /><div><b>Read-only investigation</b><span>No branch, issue, PR, merge or deployment is modified from this screen.</span></div></div>
      </section>

      <section className="evidence-control-card">
        <label>
          <span>Incident</span>
          <select value={incidentId} onChange={(event) => setIncidentId(event.target.value)}>
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
                {topHunks.map((hunk, index) => (
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
                        <small>REMOVED</small>
                        {hunk.removed_lines.length === 0 ? <pre>—</pre> : hunk.removed_lines.map((line, lineIndex) => <pre key={`r-${lineIndex}`}>− {line}</pre>)}
                      </div>
                      <div className="added-lines">
                        <small>ADDED</small>
                        {hunk.added_lines.length === 0 ? <pre>—</pre> : hunk.added_lines.map((line, lineIndex) => <pre key={`a-${lineIndex}`}>+ {line}</pre>)}
                      </div>
                    </div>
                    <footer>
                      <span>Commit {hunk.commit.short_sha}</span>
                      <a href={hunk.commit.url} target="_blank" rel="noreferrer">Review full diff <ExternalLink size={13} /></a>
                    </footer>
                  </article>
                ))}
              </div>
            )}
          </section>

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
