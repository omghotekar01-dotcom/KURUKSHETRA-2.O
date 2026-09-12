import {
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  FileCode2,
  FileUp,
  GitBranch,
  GitPullRequest,
  Loader2,
  Paperclip,
  RefreshCw,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  TestTube2,
  X,
  XCircle,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent, DragEvent } from 'react'
import LoadingShimmer from './LoadingShimmer'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const DEFAULT_REPO = 'omghotekar01-dotcom/KURUKSHETRA-2.O'

type ModelRuntime = {
  mode: 'LOCAL_OLLAMA' | 'GEMINI_FREE' | 'DETERMINISTIC_FALLBACK'
  provider: string
  model: string
  ready: boolean
  note: string
}

type ModelProbe = {
  connected: boolean
  provider: string
  model: string
  latency_ms: number
  reply: string
  note: string
}

type Readiness = {
  status: 'READY' | 'DEGRADED'
  mode: 'LIVE_FIRST' | 'FALLBACK_DEMO'
  github: {
    access_mode: string
    gh_cli_available: boolean
    write_probe?: {
      status: string
      write_access: boolean
      reason: string
      auth_source: string
    }
  }
  model?: {
    connected: boolean
    model: string
    provider: string
    latency_ms: number
    note: string
  }
}

type Upload = { path: string; content: string; size: number }

type IntakeState = {
  session_id: string
  files: { path: string; size_bytes: number }[]
  knowledge: Array<{
    id: string
    component: string
    issue: string
    fix: string
    score: number
  }>
  before_verification: {
    command: string
    exit_code: number
    output: string
    passed: boolean
  }
  execution_mode: 'STATIC_ONLY' | 'TRUSTED_PYTEST'
  safe_boundary: string
}

type Proposal = {
  target_id: string
  file_path: string
  summary: string
  diff: string
  confidence: number
  strategy: 'AI_GROUNDED' | 'DETERMINISTIC_SAFE_RULE' | 'NONE'
  reasoning_provider: string
  reasoning_model: string
  fallback_reason?: string | null
}

type IntakeResult = {
  final_status: 'VERIFIED_FIXED' | 'STATIC_CHECK_PASSED' | 'ROLLED_BACK'
  applied: boolean
  rolled_back: boolean
  after_verification: {
    command: string
    exit_code: number
    output: string
    passed: boolean
  }
  audit: string[]
}

type IncidentAnalysis = {
  incidentId: string
  component: string
  owner: string
  severity: string
  confidence: number
  hypothesis?: {
    title: string
    confidence: number
    rationale: string
    next_diagnostic: string
  }
  repository?: {
    repository: string
    default_branch: string
    commits: Array<{
      short_sha: string
      message: string
      correlation_score: number
    }>
  } | null
  noStrongMatch: boolean
  retrievalCount: number
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const payload = await response.json() as { detail?: string }
      if (payload.detail) detail = payload.detail
    } catch {
      // Keep HTTP fallback.
    }
    throw new Error(detail)
  }
  return response.json() as Promise<T>
}

export default function BugWorkspacePage() {
  const [prompt, setPrompt] = useState('')
  const [repo, setRepo] = useState(DEFAULT_REPO)
  const [environment, setEnvironment] = useState('production')
  const [uploads, setUploads] = useState<Upload[]>([])
  const [trustedTests, setTrustedTests] = useState(false)
  const [runtime, setRuntime] = useState<ModelRuntime | null>(null)
  const [probe, setProbe] = useState<ModelProbe | null>(null)
  const [readiness, setReadiness] = useState<Readiness | null>(null)
  const [intake, setIntake] = useState<IntakeState | null>(null)
  const [proposal, setProposal] = useState<Proposal | null>(null)
  const [intakeResult, setIntakeResult] = useState<IntakeResult | null>(null)
  const [incidentAnalysis, setIncidentAnalysis] = useState<IncidentAnalysis | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const pageRef = useRef<HTMLElement>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api<ModelRuntime>('/api/v1/autofix/model-runtime'),
      api<Readiness>('/api/v1/evaluation/readiness'),
    ]).then(([model, ready]) => {
      if (cancelled) return
      setRuntime(model)
      setReadiness(ready)
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : 'Unable to load runtime status.')
    })

    const onPointerMove = (event: PointerEvent) => {
      const root = pageRef.current
      if (!root || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
      const x = (event.clientX / window.innerWidth - 0.5) * 2
      const y = (event.clientY / window.innerHeight - 0.5) * 2
      root.style.setProperty('--parallax-x', `${x * 14}px`)
      root.style.setProperty('--parallax-y', `${y * 10}px`)
    }
    const onScroll = () => pageRef.current?.style.setProperty('--scroll-shift', `${Math.min(window.scrollY * 0.08, 34)}px`)
    window.addEventListener('pointermove', onPointerMove, { passive: true })
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      cancelled = true
      window.removeEventListener('pointermove', onPointerMove)
      window.removeEventListener('scroll', onScroll)
    }
  }, [])

  async function collectFiles(files: File[]) {
    setError('')
    const selected = files.slice(0, 12)
    const next: Upload[] = []
    for (const file of selected) {
      if (file.size > 256_000) {
        setError(`${file.name} is larger than the 256 KB per-file safety limit.`)
        continue
      }
      try {
        next.push({ path: file.name, content: await file.text(), size: file.size })
      } catch {
        setError(`${file.name} could not be read as text.`)
      }
    }
    setUploads(next)
    resetResults()
  }

  function resetResults() {
    setIntake(null)
    setProposal(null)
    setIntakeResult(null)
    setIncidentAnalysis(null)
  }

  async function onFiles(event: ChangeEvent<HTMLInputElement>) {
    await collectFiles(Array.from(event.target.files ?? []))
  }

  async function onDrop(event: DragEvent<HTMLElement>) {
    event.preventDefault()
    setDragActive(false)
    await collectFiles(Array.from(event.dataTransfer.files ?? []))
  }

  async function testIntegrations() {
    setBusy('integrations')
    setError('')
    try {
      const [ready, model] = await Promise.all([
        api<Readiness>('/api/v1/evaluation/readiness?probe_integrations=true'),
        api<ModelRuntime>('/api/v1/autofix/model-runtime'),
      ])
      setReadiness(ready)
      setRuntime(model)
      if (ready.model) {
        setProbe({
          connected: ready.model.connected,
          provider: ready.model.provider,
          model: ready.model.model,
          latency_ms: ready.model.latency_ms,
          reply: '',
          note: ready.model.note,
        })
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Integration test failed.')
    } finally {
      setBusy('')
    }
  }

  async function investigate() {
    if (prompt.trim().length < 8) return
    setBusy('investigate')
    setError('')
    resetResults()
    try {
      if (uploads.length > 0) {
        const session = await api<IntakeState>('/api/v1/autofix/intake', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            problem: prompt.trim(),
            trusted_test_execution: trustedTests,
            files: uploads.map(({ path, content }) => ({ path, content })),
          }),
        })
        setIntake(session)
        return
      }

      if (!repo.trim()) throw new Error('Attach source files or enter an allowlisted GitHub repository.')
      const incident = await api<{
        id: string
        triage: { component: string; owner_team: string; severity: string; confidence: number }
      }>('/api/v1/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: prompt.trim().split(/\n|\./)[0].slice(0, 150) || 'Engineering incident',
          description: prompt.trim(),
          environment,
          repo: repo.trim(),
          logs: [],
        }),
      })
      const analysis = await api<{
        evidence: { matches: unknown[]; no_strong_match: boolean }
        hypotheses: Array<{ title: string; confidence: number; rationale: string; next_diagnostic: string }>
        repository_context?: null | {
          repository: string
          default_branch: string
          commits: Array<{ short_sha: string; message: string; correlation_score: number }>
        }
      }>(`/api/v1/incidents/${incident.id}/analyze`, { method: 'POST' })
      setIncidentAnalysis({
        incidentId: incident.id,
        component: incident.triage.component,
        owner: incident.triage.owner_team,
        severity: incident.triage.severity,
        confidence: incident.triage.confidence,
        hypothesis: analysis.hypotheses[0],
        repository: analysis.repository_context ?? null,
        noStrongMatch: analysis.evidence.no_strong_match,
        retrievalCount: analysis.evidence.matches.length,
      })
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Investigation failed.')
    } finally {
      setBusy('')
    }
  }

  async function previewFix() {
    if (!intake) return
    setBusy('proposal')
    setError('')
    setProposal(null)
    setIntakeResult(null)
    try {
      setProposal(await api<Proposal>(`/api/v1/autofix/intake/${intake.session_id}/proposal`, { method: 'POST' }))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to prepare a grounded proposal.')
    } finally {
      setBusy('')
    }
  }

  async function applyFix() {
    if (!intake || !proposal || proposal.strategy === 'NONE') return
    setBusy('apply')
    setError('')
    try {
      const result = await api<IntakeResult>(`/api/v1/autofix/intake/${intake.session_id}/apply`, { method: 'POST' })
      setIntakeResult(result)
      setProposal(null)
    } catch (reason) {
      setProposal(null)
      setError(reason instanceof Error ? reason.message : 'Apply failed. Generate a fresh preview before retrying.')
    } finally {
      setBusy('')
    }
  }

  const liveModel = probe?.connected ?? readiness?.model?.connected ?? false
  const modelStatusLabel = liveModel
    ? `${probe?.model ?? readiness?.model?.model ?? runtime?.model ?? 'Model'} live`
    : runtime?.mode === 'LOCAL_OLLAMA' && runtime.ready
      ? `${runtime.model} installed · test live`
      : 'Model fallback safe'
  const githubWrite = readiness?.github.write_probe
  const canInvestigate = prompt.trim().length >= 8 && !busy

  return (
    <main
      className={`bug-workspace-page ${dragActive ? 'is-dragging' : ''}`}
      ref={pageRef}
      onDragOver={(event) => { event.preventDefault(); setDragActive(true) }}
      onDragLeave={(event) => { if (event.currentTarget === event.target) setDragActive(false) }}
      onDrop={(event) => void onDrop(event)}
    >
      <div className="workspace-aurora workspace-aurora-a" />
      <div className="workspace-aurora workspace-aurora-b" />
      <div className="workspace-orbit orbit-a" />
      <div className="workspace-orbit orbit-b" />

      <section className="workspace-hero">
        <div className="workspace-kicker"><Sparkles size={14} /> EVIDENCE-FIRST ENGINEERING AGENT</div>
        <h1>What broke?</h1>
        <p>Describe the symptom, attach the code or point us at GitHub. The agent will investigate first, show its evidence, and keep every write behind review.</p>

        <div className="workspace-status-row">
          <span className={`workspace-status ${readiness?.mode === 'FALLBACK_DEMO' ? 'warning' : 'live'}`}>
            <span /> {readiness?.mode === 'FALLBACK_DEMO' ? 'Fallback demo' : 'Live-first'}
          </span>
          <span className={`workspace-status ${liveModel ? 'live' : 'muted'}`}>
            <Bot size={13} /> {modelStatusLabel}
          </span>
          <button className="workspace-inline-action" type="button" onClick={() => void testIntegrations()} disabled={!!busy}>
            {busy === 'integrations' ? <Loader2 size={13} className="spin" /> : <RefreshCw size={13} />} Test live integrations
          </button>
        </div>
      </section>

      <section className="workspace-stage">
        <div className="workspace-composer glass-surface">
          <textarea
            value={prompt}
            onChange={(event) => { setPrompt(event.target.value); resetResults() }}
            placeholder="Describe the bug, expected behavior, observed behavior, logs, reproduction steps…"
            rows={6}
            aria-label="Describe the engineering problem"
          />

          {uploads.length > 0 && (
            <div className="workspace-file-chips">
              {uploads.map((file) => (
                <span key={file.path}><FileCode2 size={13} /> {file.path}<button type="button" onClick={() => { setUploads((items) => items.filter((item) => item.path !== file.path)); resetResults() }} aria-label={`Remove ${file.path}`}><X size={12} /></button></span>
              ))}
            </div>
          )}

          <div className="workspace-repo-row">
            <GitBranch size={16} />
            <input value={repo} onChange={(event) => { setRepo(event.target.value); resetResults() }} placeholder="owner/repository" aria-label="GitHub repository" />
            <select value={environment} onChange={(event) => setEnvironment(event.target.value)} aria-label="Environment">
              <option value="production">Production</option>
              <option value="staging">Staging</option>
              <option value="development">Development</option>
            </select>
          </div>

          <div className="workspace-composer-toolbar">
            <div className="workspace-tools">
              <button type="button" onClick={() => fileInput.current?.click()}><Paperclip size={16} /> Attach files</button>
              <input ref={fileInput} type="file" multiple hidden accept=".py,.js,.jsx,.ts,.tsx,.json,.yaml,.yml,.toml,.md,.txt" onChange={(event) => void onFiles(event)} />
              <span className="source-pill"><GitBranch size={14} /> GitHub</span>
              <span className="source-pill"><BrainCircuit size={14} /> RAG</span>
              <label className="workspace-trust-toggle" title="Only enable for Python tests you trust">
                <input type="checkbox" checked={trustedTests} onChange={(event) => { setTrustedTests(event.target.checked); resetResults() }} />
                <TestTube2 size={14} /> Trusted tests
              </label>
            </div>
            <button className="workspace-send" type="button" onClick={() => void investigate()} disabled={!canInvestigate} aria-label="Investigate bug">
              {busy === 'investigate' ? <Loader2 size={18} className="spin" /> : <ArrowRight size={19} />}
            </button>
          </div>
        </div>

        <aside className="workspace-context glass-surface">
          <div className="workspace-context-heading"><Sparkles size={16} /><div><small>LIVE CONTEXT</small><strong>Agent workspace</strong></div></div>
          <div className="workspace-context-item"><span>Model</span><strong>{runtime?.model ?? 'Checking…'}</strong><small>{probe ? (probe.connected ? `Live inference · ${probe.latency_ms} ms` : probe.note) : runtime?.ready && runtime.mode !== 'DETERMINISTIC_FALLBACK' ? 'Installed/reachable. Test live integrations to prove inference.' : runtime?.note ?? 'Checking local runtime'}</small></div>
          <div className="workspace-context-item"><span>GitHub</span><strong>{githubWrite?.status ?? readiness?.github.access_mode ?? 'Checking…'}</strong><small>{githubWrite?.reason ?? 'Read-only investigation is available before approval. Test integrations to verify push permission.'}</small></div>
          <div className="workspace-context-item"><span>Files</span><strong>{uploads.length ? `${uploads.length} attached` : 'Optional'}</strong><small>Judge files stay inside an isolated temporary workspace.</small></div>
          <div className="workspace-safety"><ShieldCheck size={15} /><span>No auto-merge. No production deploy. Exact reviewed writes only.</span></div>
        </aside>
      </section>

      {dragActive && <div className="workspace-drop-overlay"><FileUp size={28} /><strong>Drop source + test files here</strong><span>Up to 12 bounded text/code files</span></div>}

      {error && <div className="workspace-alert error"><XCircle size={17} /><span>{error}</span></div>}

      {busy === 'investigate' && (
        <section className="workspace-result-shell">
          <div className="workspace-result-heading"><Loader2 size={17} className="spin" /> Investigating evidence, not guessing…</div>
          <div className="workspace-loading-grid"><LoadingShimmer lines={5} label="Investigating engineering evidence" /><LoadingShimmer lines={4} label="Retrieving engineering context" /></div>
        </section>
      )}

      {incidentAnalysis && (
        <section className="workspace-result-shell">
          <div className="workspace-result-heading"><CheckCircle2 size={18} /> Repository investigation ready <span>{incidentAnalysis.incidentId}</span></div>
          <div className="workspace-result-grid">
            <article className="workspace-result-card">
              <small>TRIAGE</small><h2>{incidentAnalysis.component}</h2>
              <div className="workspace-metrics"><span><b>{incidentAnalysis.severity}</b> severity</span><span><b>{Math.round(incidentAnalysis.confidence * 100)}%</b> confidence</span></div>
              <p>Owner route: <strong>{incidentAnalysis.owner}</strong></p>
            </article>
            <article className="workspace-result-card">
              <small>RCA HYPOTHESIS</small>
              <h2>{incidentAnalysis.hypothesis?.title ?? 'Evidence is insufficient for a confident RCA'}</h2>
              <p>{incidentAnalysis.hypothesis?.rationale ?? 'The agent stopped instead of inventing a cause.'}</p>
              {incidentAnalysis.hypothesis && <div className="workspace-next-check"><SearchCheck size={14} /><span>{incidentAnalysis.hypothesis.next_diagnostic}</span></div>}
            </article>
            <article className="workspace-result-card wide">
              <small>LIVE GITHUB EVIDENCE</small>
              {incidentAnalysis.repository?.commits?.length ? (
                <div className="workspace-commit-list">{incidentAnalysis.repository.commits.slice(0, 3).map((commit) => <div key={commit.short_sha}><code>{commit.short_sha}</code><span>{commit.message}</span><b>{Math.round(commit.correlation_score * 100)}%</b></div>)}</div>
              ) : <p>No verified repository candidate was returned. No fake GitHub evidence was inserted.</p>}
              <div className="workspace-result-actions"><a href="/evidence">Open Evidence Lab <ArrowRight size={14} /></a><a href="/remediate">Review remediation <GitPullRequest size={14} /></a></div>
            </article>
          </div>
        </section>
      )}

      {intake && (
        <section className="workspace-result-shell">
          <div className="workspace-result-heading"><FileCode2 size={18} /> Isolated file investigation <span>{intake.session_id}</span></div>
          <div className="workspace-result-grid">
            <article className="workspace-result-card">
              <small>BASELINE</small><h2 className={intake.before_verification.passed ? 'result-pass' : 'result-fail'}>{intake.before_verification.passed ? 'PASS' : 'FAIL'}</h2>
              <code>{intake.before_verification.command}</code>
              <pre className="workspace-terminal">{intake.before_verification.output}</pre>
              <p>{intake.execution_mode === 'TRUSTED_PYTEST' ? 'Trusted functional test mode' : 'Static-only safety mode'}</p>
            </article>
            <article className="workspace-result-card">
              <small>RAG</small><h2>{intake.knowledge.length ? `${intake.knowledge.length} knowledge match${intake.knowledge.length === 1 ? '' : 'es'}` : 'No strong match'}</h2>
              {intake.knowledge.slice(0, 3).map((hit) => <div className="workspace-rag-hit" key={hit.id}><span>{hit.id} · {hit.component}</span><b>{Math.round(hit.score * 100)}%</b><small>{hit.issue}</small></div>)}
              {!intake.knowledge.length && <p>No historical match was forced. Qwen still receives the bounded source/test evidence.</p>}
            </article>
          </div>
          {!intakeResult && <div className="workspace-result-actions"><button type="button" onClick={() => void previewFix()} disabled={!!busy}>{busy === 'proposal' ? <Loader2 size={15} className="spin" /> : <Bot size={15} />} Preview grounded AI fix</button><a href="/intake">Open full Judge Intake <ArrowRight size={14} /></a></div>}
        </section>
      )}

      {busy === 'proposal' && <section className="workspace-result-shell"><LoadingShimmer lines={5} label="Qwen is preparing a bounded patch" /></section>}

      {proposal && (
        <section className="workspace-result-shell proposal-shell">
          <div className="workspace-result-heading"><Bot size={18} /> Exact patch review <span>{proposal.reasoning_provider} · {proposal.reasoning_model}</span></div>
          <div className="workspace-proposal-meta"><span>{proposal.strategy}</span><span>{Math.round(proposal.confidence * 100)}% bounded confidence</span><span>{proposal.file_path}</span></div>
          <p>{proposal.summary}</p>
          {proposal.fallback_reason && <div className="workspace-alert warning"><ShieldCheck size={15} /> {proposal.fallback_reason}</div>}
          {proposal.diff ? <pre className="workspace-diff">{proposal.diff}</pre> : <div className="workspace-empty">No safe patch was generated. Nothing will be written.</div>}
          {proposal.diff && proposal.strategy !== 'NONE' && <div className="workspace-approval-row"><span><ShieldCheck size={15} /> Applying changes only the isolated uploaded copy.</span><button type="button" onClick={() => void applyFix()} disabled={!!busy}>{busy === 'apply' ? <Loader2 size={15} className="spin" /> : <CheckCircle2 size={15} />} Apply reviewed patch + verify</button></div>}
        </section>
      )}

      {busy === 'apply' && <section className="workspace-result-shell"><LoadingShimmer lines={4} label="Applying exact reviewed patch and running validator" /></section>}

      {intakeResult && (
        <section className={`workspace-final ${intakeResult.final_status === 'ROLLED_BACK' ? 'fail' : 'pass'}`}>
          {intakeResult.final_status === 'ROLLED_BACK' ? <XCircle size={28} /> : <CheckCircle2 size={28} />}
          <div><small>FINAL STATE</small><h2>{intakeResult.final_status.replaceAll('_', ' ')}</h2><p>{intakeResult.final_status === 'VERIFIED_FIXED' ? 'The same trusted failing test passed after the exact reviewed patch.' : intakeResult.final_status === 'STATIC_CHECK_PASSED' ? 'Static validation passed. Functional recovery is intentionally not claimed without a trusted failing test.' : 'Validation failed and the isolated file was restored.'}</p></div>
        </section>
      )}

      <section className="workspace-capability-strip">
        <div><GitBranch size={17} /><span><b>Live GitHub evidence</b><small>Commits, diffs, files and issues</small></span></div>
        <div><BrainCircuit size={17} /><span><b>Grounded reasoning</b><small>RAG + bounded model synthesis</small></span></div>
        <div><ShieldCheck size={17} /><span><b>Human authority</b><small>Review before every meaningful write</small></span></div>
      </section>
    </main>
  )
}
