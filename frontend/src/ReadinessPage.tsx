import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  CheckCircle2,
  GitBranch,
  Loader2,
  RefreshCw,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type ReadinessReport = {
  status: 'READY' | 'DEGRADED'
  checked_at: string
  mode: 'LIVE_FIRST' | 'FALLBACK_DEMO'
  environment: string
  checks: Record<string, boolean>
  github: {
    allowlisted_repository_count: number
    access_mode: string
    token_present: boolean
    gh_cli_allowed: boolean
    gh_cli_available: boolean
  }
  safety: {
    repository_evidence: string
    incident_secret_redaction: string
    repository_writes: string
    high_risk_actions: string
    automatic_merge: boolean
    automatic_production_deploy: boolean
  }
  notes: string[]
}

const labelFor = (key: string) => key
  .split('_')
  .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
  .join(' ')

export default function ReadinessPage() {
  const [report, setReport] = useState<ReadinessReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadReadiness() {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/readiness`)
      if (!response.ok) throw new Error(`Readiness check failed with ${response.status}`)
      setReport(await response.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to reach the readiness endpoint.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadReadiness()
  }, [])

  return (
    <main className="readiness-page">
      <header className="readiness-topbar">
        <a href="/" className="readiness-back"><ArrowLeft size={16} /> Incident Command</a>
        <button type="button" onClick={() => void loadReadiness()} disabled={loading}>
          {loading ? <><Loader2 className="spin" size={16} /> Checking…</> : <><RefreshCw size={16} /> Refresh readiness</>}
        </button>
      </header>

      <section className="readiness-hero">
        <div>
          <p>SYSTEM READINESS</p>
          <h1>Know exactly what is live before the demo starts.</h1>
          <span>Runtime mode, integration readiness and safety boundaries are reported without exposing credentials.</span>
        </div>
        {report && (
          <div className={`readiness-state ${report.status.toLowerCase()}`}>
            {report.status === 'READY' ? <CheckCircle2 size={22} /> : <TriangleAlert size={22} />}
            <div><small>Current state</small><strong>{report.status}</strong></div>
          </div>
        )}
      </section>

      {error && <div className="readiness-error"><TriangleAlert size={18} /> {error}</div>}

      {report && (
        <>
          <section className="readiness-mode-strip">
            <div><small>Operating mode</small><strong>{report.mode}</strong></div>
            <div><small>Environment</small><strong>{report.environment}</strong></div>
            <div><small>Checked</small><strong>{new Date(report.checked_at).toLocaleTimeString()}</strong></div>
            <div><small>API</small><strong>{API_BASE}</strong></div>
          </section>

          <section className="readiness-grid">
            <article className="readiness-card">
              <div className="readiness-card-title"><CheckCircle2 size={18} /> Runtime checks</div>
              <div className="readiness-check-list">
                {Object.entries(report.checks).map(([key, passed]) => (
                  <div key={key} className={passed ? 'check-row pass' : 'check-row fail'}>
                    <span>{labelFor(key)}</span>
                    <b>{passed ? 'PASS' : 'ATTENTION'}</b>
                  </div>
                ))}
              </div>
            </article>

            <article className="readiness-card">
              <div className="readiness-card-title"><GitBranch size={18} /> GitHub integration</div>
              <dl className="readiness-facts">
                <div><dt>Access mode</dt><dd>{report.github.access_mode}</dd></div>
                <div><dt>Allowlisted repos</dt><dd>{report.github.allowlisted_repository_count}</dd></div>
                <div><dt>Token configured</dt><dd>{report.github.token_present ? 'YES · value hidden' : 'NO'}</dd></div>
                <div><dt>GitHub CLI</dt><dd>{report.github.gh_cli_available ? 'AVAILABLE' : 'NOT FOUND'}</dd></div>
              </dl>
            </article>
          </section>

          <section className="readiness-safety">
            <div className="readiness-section-heading">
              <ShieldCheck size={21} />
              <div><h2>Safety boundary</h2><p>These controls remain active even when every readiness check is green.</p></div>
            </div>
            <div className="safety-grid">
              <div><small>Repository evidence</small><strong>{report.safety.repository_evidence}</strong></div>
              <div><small>Secret redaction</small><strong>{report.safety.incident_secret_redaction}</strong></div>
              <div><small>Repository writes</small><strong>{report.safety.repository_writes}</strong></div>
              <div><small>High-risk actions</small><strong>{report.safety.high_risk_actions}</strong></div>
              <div><small>Auto merge</small><strong>{report.safety.automatic_merge ? 'ENABLED' : 'DISABLED'}</strong></div>
              <div><small>Auto production deploy</small><strong>{report.safety.automatic_production_deploy ? 'ENABLED' : 'DISABLED'}</strong></div>
            </div>
          </section>

          <section className="readiness-notes">
            {report.notes.map((note) => <p key={note}>• {note}</p>)}
          </section>
        </>
      )}
    </main>
  )
}
