import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  Bot,
  CheckCircle2,
  GitBranch,
  Loader2,
  RefreshCw,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react'
import LoadingShimmer from './LoadingShimmer'

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
    write_probe: {
      repository: string
      authenticated: boolean
      auth_source: string
      write_access: boolean
      status: string
      reason: string
    }
  }
  model: {
    mode: string
    provider: string
    model: string
    ready: boolean
    connected: boolean
    latency_ms: number
    note: string
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
      const response = await fetch(`${API_BASE}/api/v1/evaluation/readiness?probe_integrations=true`)
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
        <a href="/" className="readiness-back"><ArrowLeft size={16} /> AI Workspace</a>
        <button type="button" onClick={() => void loadReadiness()} disabled={loading}>
          {loading ? <><Loader2 className="spin" size={16} /> Probing live integrations…</> : <><RefreshCw size={16} /> Test live integrations</>}
        </button>
      </header>

      <section className="readiness-hero">
        <div>
          <p>SYSTEM READINESS</p>
          <h1>Know exactly what is live before the demo starts.</h1>
          <span>This page performs real, read-only connectivity checks for the configured AI runtime (local Qwen or Gemini fallback) and GitHub access without exposing credentials or creating repository resources.</span>
        </div>
        {report && (
          <div className={`readiness-state ${report.status.toLowerCase()}`}>
            {report.status === 'READY' ? <CheckCircle2 size={22} /> : <TriangleAlert size={22} />}
            <div><small>Core state</small><strong>{report.status}</strong></div>
          </div>
        )}
      </section>

      {error && <div className="readiness-error"><TriangleAlert size={18} /> {error}</div>}

      {loading && !report && (
        <section className="readiness-grid">
          <LoadingShimmer lines={5} label="Checking runtime readiness" />
          <LoadingShimmer lines={5} label="Probing GitHub and AI runtime" />
        </section>
      )}

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
              <div className="readiness-card-title"><Bot size={18} /> AI reasoning runtime</div>
              <dl className="readiness-facts">
                <div><dt>Provider</dt><dd>{report.model.provider}</dd></div>
                <div><dt>Model</dt><dd>{report.model.model}</dd></div>
                <div><dt>Live inference</dt><dd>{report.model.connected ? 'CONNECTED' : 'NOT CONNECTED'}</dd></div>
                <div><dt>Probe latency</dt><dd>{report.model.connected ? `${report.model.latency_ms} ms` : '—'}</dd></div>
              </dl>
              <p className={report.model.connected ? 'integration-note integration-pass' : 'integration-note integration-attention'}>{report.model.note}</p>
            </article>

            <article className="readiness-card">
              <div className="readiness-card-title"><GitBranch size={18} /> GitHub remediation access</div>
              <dl className="readiness-facts">
                <div><dt>Repository</dt><dd>{report.github.write_probe.repository}</dd></div>
                <div><dt>Auth source</dt><dd>{report.github.write_probe.auth_source}</dd></div>
                <div><dt>GitHub CLI</dt><dd>{report.github.gh_cli_available ? 'AVAILABLE' : 'NOT FOUND'}</dd></div>
                <div><dt>Push permission</dt><dd>{report.github.write_probe.write_access ? 'VERIFIED' : report.github.write_probe.status}</dd></div>
              </dl>
              <p className={report.github.write_probe.write_access ? 'integration-note integration-pass' : 'integration-note integration-attention'}>{report.github.write_probe.reason}</p>
              {!report.github.write_probe.write_access && <code className="readiness-command">gh auth status  →  gh auth login</code>}
            </article>
          </section>

          <section className="readiness-grid readiness-grid-secondary">
            <article className="readiness-card">
              <div className="readiness-card-title"><CheckCircle2 size={18} /> Core runtime checks</div>
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
              <div className="readiness-card-title"><GitBranch size={18} /> GitHub configuration</div>
              <dl className="readiness-facts">
                <div><dt>Access mode</dt><dd>{report.github.access_mode}</dd></div>
                <div><dt>Allowlisted repos</dt><dd>{report.github.allowlisted_repository_count}</dd></div>
                <div><dt>Token configured</dt><dd>{report.github.token_present ? 'YES · value hidden' : 'NO'}</dd></div>
                <div><dt>CLI auth allowed</dt><dd>{report.github.gh_cli_allowed ? 'YES' : 'NO'}</dd></div>
              </dl>
            </article>
          </section>

          <section className="readiness-safety">
            <div className="readiness-section-heading">
              <ShieldCheck size={21} />
              <div><h2>Safety boundary</h2><p>These controls remain active regardless of whether Qwen, Gemini or deterministic fallback is currently providing reasoning.</p></div>
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
