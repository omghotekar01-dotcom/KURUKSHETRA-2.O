import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Database,
  FileSearch,
  GitBranch,
  Layers3,
  Loader2,
  Network,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const LIVE_REPO = 'omghotekar01-dotcom/KURUKSHETRA-2.O'

type Scenario = {
  id: string
  name: string
  component: string
  problem: string
  proof: string
  incident: {
    title: string
    description: string
    environment: string
    repo: string | null
    logs: string[]
  }
}

type AgentTrace = {
  mode: 'LLM_RAG' | 'DETERMINISTIC_RAG'
  provider: string
  model: string
  retrieval_sources: string[]
  grounded: boolean
  fallback_reason?: string | null
}

type Analysis = {
  incident_id: string
  evidence: {
    matches: Array<{
      id: string
      component: string
      issue: string
      fix: string
      source: string
      score: number
    }>
    no_strong_match: boolean
  }
  repository_context?: null | {
    repository: string
    default_branch: string
    source: string
    commits: Array<{
      short_sha: string
      message: string
      correlation_score: number
      suspicious_hunks: Array<{ filename: string; header: string; correlation_score: number }>
    }>
    notes: string[]
  }
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
    risk?: { risk: string; policy: string; requires_human_approval: boolean } | null
  }
  needs_human_investigation: boolean
  agent_trace?: AgentTrace | null
}

type Incident = {
  id: string
  status: string
  triage: {
    component: string
    owner_team: string
    severity: string
    confidence: number
    signals: string[]
  }
}

const scenarios: Scenario[] = [
  {
    id: 'auth-regression',
    name: 'JWT authentication regression',
    component: 'Authentication',
    problem: 'Users can sign in, but protected API requests immediately fail after an auth-related deployment.',
    proof: 'Show routing, RAG retrieval, live repository correlation, RCA, bounded remediation and verification plan.',
    incident: {
      title: '401 errors after JWT signing change',
      description: 'Production users authenticate successfully, but protected API requests return unauthorized after a recent signing configuration change.',
      environment: 'production',
      repo: LIVE_REPO,
      logs: ['JWT signature verification failed', '401 unauthorized after authentication deployment'],
    },
  },
  {
    id: 'database-regression',
    name: 'Database pool exhaustion',
    component: 'Database',
    problem: 'Write requests fail under peak traffic while database connections time out and recover intermittently.',
    proof: 'Show database routing, relevant runbook retrieval, evidence-grounded diagnosis and measured uncertainty.',
    incident: {
      title: 'Profile writes fail during peak traffic',
      description: 'Production profile updates return HTTP 500 when traffic spikes. Requests recover after connection timeouts.',
      environment: 'production',
      repo: LIVE_REPO,
      logs: ['sqlalchemy.exc.TimeoutError: QueuePool limit reached', 'PostgreSQL connection pool exhausted'],
    },
  },
  {
    id: 'frontend-contract',
    name: 'Frontend API contract break',
    component: 'Frontend',
    problem: 'A dashboard view stops rendering after an API response field changes in a recent release.',
    proof: 'Show code-aware repository evidence, hunk ranking and a verification plan tied to the affected user flow.',
    incident: {
      title: 'Incident dashboard fails after API response change',
      description: 'The incident detail screen renders an empty state after the backend response shape changed. Other pages still load.',
      environment: 'production',
      repo: LIVE_REPO,
      logs: ['TypeError: cannot read properties of undefined', 'frontend incident detail response contract mismatch'],
    },
  },
  {
    id: 'infra-health',
    name: 'Infrastructure health regression',
    component: 'Infrastructure',
    problem: 'A service repeatedly restarts after rollout because health checks fail under resource pressure.',
    proof: 'Show infra routing, rollout evidence, safety policy and the rule that production actions are never autonomous.',
    incident: {
      title: 'API workers restart after rollout',
      description: 'New replicas enter a restart loop after deployment and readiness checks begin failing under load.',
      environment: 'production',
      repo: LIVE_REPO,
      logs: ['readiness probe failed', 'worker restart loop', 'container memory pressure'],
    },
  },
  {
    id: 'unknown-safe-stop',
    name: 'Unknown service safe-stop',
    component: 'Unclassified',
    problem: 'A new service returns inconsistent payloads with no trusted historical context or useful repository attachment.',
    proof: 'Show that the agent refuses to invent a confident RCA or patch when retrieval and evidence are insufficient.',
    incident: {
      title: 'Orion payload changes intermittently',
      description: 'A newly introduced Orion service changes response fields unpredictably with no established runbook or repository context.',
      environment: 'staging',
      repo: null,
      logs: ['response schema changed unexpectedly'],
    },
  },
]

async function responseDetail(response: Response) {
  try {
    const payload = await response.json()
    return payload.detail ?? JSON.stringify(payload)
  } catch {
    return response.text()
  }
}

export default function AgentIntelligencePage() {
  const [scenarioId, setScenarioId] = useState(scenarios[0].id)
  const [incident, setIncident] = useState<Incident | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const scenario = useMemo(
    () => scenarios.find((item) => item.id === scenarioId) ?? scenarios[0],
    [scenarioId],
  )
  const topHypothesis = analysis?.hypotheses[0] ?? null
  const topCommit = analysis?.repository_context?.commits[0] ?? null
  const agentMode = analysis?.agent_trace?.mode ?? 'DETERMINISTIC_RAG'

  async function runScenario() {
    setBusy(true)
    setError('')
    setIncident(null)
    setAnalysis(null)
    try {
      const incidentResponse = await fetch(`${API_BASE}/api/v1/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario.incident),
      })
      if (!incidentResponse.ok) throw new Error(await responseDetail(incidentResponse))
      const created: Incident = await incidentResponse.json()
      setIncident(created)

      const analysisResponse = await fetch(`${API_BASE}/api/v1/incidents/${created.id}/analyze`, { method: 'POST' })
      if (!analysisResponse.ok) throw new Error(await responseDetail(analysisResponse))
      setAnalysis(await analysisResponse.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to run the agent scenario.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="ai-lab-page">
      <header className="ai-lab-hero">
        <div>
          <p className="eyebrow">AGENT INTELLIGENCE · RAG + LIVE CODE EVIDENCE</p>
          <h1>See how the agent reaches an engineering decision</h1>
          <p className="ai-lab-subtitle">
            The model is not allowed to reason from vibes. It retrieves verified knowledge, correlates live repository evidence,
            synthesizes an RCA, passes actions through policy, and falls back deterministically when an LLM is unavailable.
          </p>
        </div>
        <div className="ai-mode-badge"><BrainCircuit size={17} /> {analysis ? agentMode.replace('_', ' + ') : 'Evidence-first agent'}</div>
      </header>

      <section className="ai-architecture-strip" aria-label="Agent architecture">
        <div><Sparkles size={17} /><strong>1. Triage</strong><span>classify + route</span></div>
        <ArrowRight size={16} />
        <div><Database size={17} /><strong>2. RAG</strong><span>runbooks + verified memory</span></div>
        <ArrowRight size={16} />
        <div><GitBranch size={17} /><strong>3. Repo evidence</strong><span>commits + diffs + source</span></div>
        <ArrowRight size={16} />
        <div><Bot size={17} /><strong>4. RCA synthesis</strong><span>LLM if configured</span></div>
        <ArrowRight size={16} />
        <div><ShieldCheck size={17} /><strong>5. Policy gate</strong><span>human authority</span></div>
      </section>

      <section className="ai-lab-grid">
        <aside className="ai-scenario-panel">
          <div className="ai-section-heading">
            <span>Judge scenarios</span>
            <small>Pick one problem to demonstrate</small>
          </div>
          <div className="ai-scenario-list">
            {scenarios.map((item) => (
              <button
                key={item.id}
                type="button"
                className={scenarioId === item.id ? 'ai-scenario active' : 'ai-scenario'}
                onClick={() => setScenarioId(item.id)}
                disabled={busy}
              >
                <span>{item.name}</span>
                <small>{item.component}</small>
              </button>
            ))}
          </div>

          <div className="ai-problem-card">
            <span className="ai-card-kicker">Problem shown to judges</span>
            <h2>{scenario.name}</h2>
            <p>{scenario.problem}</p>
            <div className="ai-proof-box">
              <FileSearch size={16} />
              <span><b>What this proves:</b> {scenario.proof}</span>
            </div>
          </div>

          <button className="ai-run-button" type="button" onClick={runScenario} disabled={busy}>
            {busy ? <><Loader2 size={17} className="spin" /> Agent investigating…</> : <><Sparkles size={17} /> Run this incident</>}
          </button>
          {error && <div className="ai-error"><AlertTriangle size={16} /> {error}</div>}
        </aside>

        <section className="ai-results">
          {!incident && !analysis && (
            <div className="ai-empty-state">
              <BrainCircuit size={38} />
              <h2>Ready to demonstrate the agent</h2>
              <p>Select a problem on the left and run it. Every result below comes from the backend workflow, not hard-coded scores.</p>
            </div>
          )}

          {incident && (
            <article className="ai-result-card">
              <div className="ai-result-title"><span>01 · Triage & routing</span><CheckCircle2 size={17} /></div>
              <div className="ai-metric-grid">
                <div><small>Component</small><strong>{incident.triage.component}</strong></div>
                <div><small>Owner</small><strong>{incident.triage.owner_team}</strong></div>
                <div><small>Severity</small><strong>{incident.triage.severity}</strong></div>
                <div><small>Confidence</small><strong>{Math.round(incident.triage.confidence * 100)}%</strong></div>
              </div>
            </article>
          )}

          {analysis && (
            <>
              <article className="ai-result-card">
                <div className="ai-result-title"><span>02 · Retrieval-augmented context</span><Database size={17} /></div>
                {analysis.evidence.no_strong_match ? (
                  <div className="ai-safe-stop"><AlertTriangle size={17} /> No strong knowledge match. The agent keeps uncertainty explicit instead of inventing a remembered fix.</div>
                ) : (
                  <div className="ai-evidence-list">
                    {analysis.evidence.matches.map((match) => (
                      <div key={match.id} className="ai-evidence-row">
                        <div><strong>{match.id} · {match.issue}</strong><small>{match.source} · {match.component}</small></div>
                        <span>{Math.round(match.score * 100)}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </article>

              <article className="ai-result-card">
                <div className="ai-result-title"><span>03 · Live repository evidence</span><GitBranch size={17} /></div>
                {topCommit ? (
                  <div className="ai-repo-proof">
                    <div><small>Repository</small><strong>{analysis.repository_context?.repository}</strong></div>
                    <div><small>Top commit</small><strong>{topCommit.short_sha} · {topCommit.message}</strong></div>
                    <div><small>Correlation</small><strong>{Math.round(topCommit.correlation_score * 100)}%</strong></div>
                    <p>Correlation ranks investigation targets; it is not presented as proof of causation.</p>
                  </div>
                ) : (
                  <div className="ai-safe-stop"><Network size={17} /> No verified repository candidate was available. RAG/RCA remains separate from live code evidence.</div>
                )}
              </article>

              <article className="ai-result-card ai-reasoning-card">
                <div className="ai-result-title"><span>04 · Agent RCA synthesis</span><Bot size={17} /></div>
                <div className="ai-agent-trace">
                  <span className={agentMode === 'LLM_RAG' ? 'ai-trace-live' : 'ai-trace-fallback'}>{agentMode === 'LLM_RAG' ? 'LLM + RAG ACTIVE' : 'DETERMINISTIC RAG FALLBACK'}</span>
                  <small>{analysis.agent_trace?.provider ?? 'deterministic'} · {analysis.agent_trace?.model ?? 'evidence-rules-v1'}</small>
                </div>
                {topHypothesis ? (
                  <>
                    <h2>{topHypothesis.title}</h2>
                    <div className="ai-confidence">RCA confidence · {Math.round(topHypothesis.confidence * 100)}%</div>
                    <p>{topHypothesis.rationale}</p>
                    <div className="ai-next-check"><b>Next diagnostic</b><span>{topHypothesis.next_diagnostic}</span></div>
                  </>
                ) : (
                  <div className="ai-safe-stop"><AlertTriangle size={17} /> Evidence did not justify a root-cause hypothesis. Human investigation is required.</div>
                )}
                {analysis.agent_trace?.fallback_reason && <p className="ai-fallback-note">LLM fallback reason: {analysis.agent_trace.fallback_reason}</p>}
              </article>

              <article className="ai-result-card">
                <div className="ai-result-title"><span>05 · Safe solution path</span><ShieldCheck size={17} /></div>
                {analysis.remediation ? (
                  <>
                    <h3>{analysis.remediation.summary}</h3>
                    <ol className="ai-solution-list">
                      {analysis.remediation.steps.map((step) => <li key={step}>{step}</li>)}
                    </ol>
                    <div className="ai-verification"><b>Verification before resolution</b><span>{analysis.remediation.verification}</span></div>
                    <p className="ai-policy-line">Policy: {analysis.remediation.risk?.policy ?? 'review required'} · human approval {analysis.remediation.risk?.requires_human_approval ? 'required' : 'still available'}</p>
                  </>
                ) : (
                  <div className="ai-safe-stop"><AlertTriangle size={17} /> SAFE STOP — no remediation is generated without sufficient evidence.</div>
                )}
              </article>
            </>
          )}
        </section>
      </section>

      <section className="ai-judge-script">
        <Layers3 size={20} />
        <div>
          <strong>One-line judge explanation</strong>
          <p>“We combine verified incident memory and runbook RAG with live GitHub code evidence; an LLM can synthesize only that grounded context, while deterministic routing, risk policy, approval and verification remain authoritative.”</p>
        </div>
      </section>
    </main>
  )
}
