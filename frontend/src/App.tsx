import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Activity, AlertCircle, GitBranch, History, Loader2, ShieldCheck, Sparkles } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const stages = ['Intake', 'Triage', 'Evidence', 'RCA', 'Remediation', 'Approval', 'Verification']

type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
type IncidentStatus = 'NEW' | 'TRIAGING' | 'INVESTIGATING' | 'RCA_READY' | 'REMEDIATION_READY' | 'AWAITING_APPROVAL' | 'EXECUTING' | 'VERIFYING' | 'RESOLVED' | 'ESCALATED'

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
  logs: 'JWT signature verification failed',
}

export default function App() {
  const [form, setForm] = useState(emptyForm)
  const [incident, setIncident] = useState<IncidentRecord | null>(null)
  const [recent, setRecent] = useState<IncidentSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const activeStageCount = useMemo(() => (incident ? 2 : 1), [incident])

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

  async function submitIncident(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE}/api/v1/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
          environment: form.environment,
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
      await loadRecent()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to create incident.')
    } finally {
      setLoading(false)
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
              <small>{item.component} · {item.severity}</small>
            </button>
          ))}
        </div>
      </aside>

      <section className="content">
        <header>
          <div>
            <p className="eyebrow">KURUKSHETRA 2.0 · WORKING BUILD</p>
            <h1>Evidence-backed incident response</h1>
            <p className="muted">Start with a real incident. The system stores the case, triages it and builds an auditable timeline.</p>
          </div>
          <span className="status">● API-connected build</span>
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
              <input
                value={form.title}
                onChange={(event) => setForm({ ...form, title: event.target.value })}
                minLength={3}
                maxLength={160}
                required
              />
            </label>
            <label>
              <span>Description</span>
              <textarea
                rows={5}
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
                minLength={5}
                required
              />
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
            <button className="primary submit-button" disabled={loading}>
              {loading ? <><Loader2 className="spin" size={16} /> Analyzing…</> : 'Create & triage incident'}
            </button>
          </form>

          <section className="result-stack">
            {incident ? (
              <>
                <article className="panel hero-panel">
                  <div className="panel-title">
                    <span>{incident.id}</span>
                    <span className={`pill ${incident.triage.severity.toLowerCase()}`}>{incident.triage.severity}</span>
                  </div>
                  <h2>{incident.incident.title}</h2>
                  <p className="muted">{incident.incident.description}</p>
                  <div className="facts">
                    <div><small>Component</small><strong>{incident.triage.component}</strong></div>
                    <div><small>Owner</small><strong>{incident.triage.owner_team}</strong></div>
                    <div><small>Confidence</small><strong>{Math.round(incident.triage.confidence * 100)}%</strong></div>
                  </div>
                </article>

                <article className="panel">
                  <div className="panel-title">Investigation timeline</div>
                  <ul className="timeline-list">
                    {incident.timeline.map((event) => (
                      <li key={`${event.timestamp}-${event.stage}`}>
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
                <h2>Ready for the first incident</h2>
                <p className="muted">Submit an incident to create a persisted case, deterministic triage result and audit timeline.</p>
              </article>
            )}
          </section>
        </section>
      </section>
    </main>
  )
}
