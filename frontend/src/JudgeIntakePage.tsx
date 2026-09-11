import {
  Bot,
  CheckCircle2,
  FileCode2,
  FileUp,
  FlaskConical,
  Play,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  XCircle,
} from 'lucide-react'
import { ChangeEvent, useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type CommandEvidence = {
  command: string
  exit_code: number
  output: string
  passed: boolean
  duration_ms: number
}

type ModelRuntime = {
  mode: 'LOCAL_OLLAMA' | 'GEMINI_FREE' | 'DETERMINISTIC_FALLBACK'
  provider: string
  model: string
  ready: boolean
  endpoint?: string | null
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

type KnowledgeHit = {
  id: string
  component: string
  issue: string
  fix: string
  source: string
  score: number
}

type IntakeState = {
  session_id: string
  problem: string
  files: { path: string; size_bytes: number }[]
  knowledge: KnowledgeHit[]
  before_verification: CommandEvidence
  execution_mode: 'STATIC_ONLY' | 'TRUSTED_PYTEST'
  model_runtime: ModelRuntime
  safe_boundary: string
}

type Proposal = {
  target_id: string
  file_path: string
  summary: string
  before: string
  after: string
  diff: string
  confidence: number
  writes_files: boolean
  strategy: 'AI_GROUNDED' | 'DETERMINISTIC_SAFE_RULE' | 'NONE'
  reasoning_provider: string
  reasoning_model: string
  fallback_reason?: string | null
}

type IntakeResult = {
  state: IntakeState
  proposal: Proposal
  applied: boolean
  rolled_back: boolean
  after_verification: CommandEvidence
  final_status: 'VERIFIED_FIXED' | 'STATIC_CHECK_PASSED' | 'ROLLED_BACK'
  patched_files: Record<string, string>
  audit: string[]
}

type Upload = { path: string; content: string; size: number }

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

function VerificationBadge({ evidence }: { evidence: CommandEvidence }) {
  return (
    <span className={`judge-status-chip ${evidence.passed ? 'pass' : 'fail'}`}>
      {evidence.passed ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
      {evidence.passed ? 'PASS' : 'FAIL'}
    </span>
  )
}

export default function JudgeIntakePage() {
  const [runtime, setRuntime] = useState<ModelRuntime | null>(null)
  const [probe, setProbe] = useState<ModelProbe | null>(null)
  const [problem, setProblem] = useState('')
  const [uploads, setUploads] = useState<Upload[]>([])
  const [trusted, setTrusted] = useState(false)
  const [intake, setIntake] = useState<IntakeState | null>(null)
  const [proposal, setProposal] = useState<Proposal | null>(null)
  const [result, setResult] = useState<IntakeResult | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    void api<ModelRuntime>('/api/v1/autofix/model-runtime')
      .then(setRuntime)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Unable to load model runtime'))
  }, [])

  async function probeModel() {
    setBusy('probe')
    setError('')
    try {
      const payload = await api<ModelProbe>('/api/v1/autofix/model-runtime/probe', { method: 'POST' })
      setProbe(payload)
      const refreshed = await api<ModelRuntime>('/api/v1/autofix/model-runtime')
      setRuntime(refreshed)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Model probe failed')
    } finally {
      setBusy('')
    }
  }

  async function onFiles(event: ChangeEvent<HTMLInputElement>) {
    setError('')
    const selected = Array.from(event.target.files ?? []).slice(0, 12)
    const next: Upload[] = []
    for (const file of selected) {
      if (file.size > 256_000) {
        setError(`${file.name} is larger than the 256 KB per-file intake limit.`)
        continue
      }
      const withRelative = file as File & { webkitRelativePath?: string }
      const path = withRelative.webkitRelativePath || file.name
      try {
        next.push({ path, content: await file.text(), size: file.size })
      } catch {
        setError(`${file.name} could not be read as text.`)
      }
    }
    setUploads(next)
    setIntake(null)
    setProposal(null)
    setResult(null)
  }

  async function createSession() {
    if (problem.trim().length < 8 || uploads.length === 0) return
    setBusy('intake')
    setError('')
    setIntake(null)
    setProposal(null)
    setResult(null)
    try {
      const payload = await api<IntakeState>('/api/v1/autofix/intake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem: problem.trim(),
          trusted_test_execution: trusted,
          files: uploads.map(({ path, content }) => ({ path, content })),
        }),
      })
      setIntake(payload)
      setRuntime(payload.model_runtime)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to create judge intake session')
    } finally {
      setBusy('')
    }
  }

  async function preview() {
    if (!intake) return
    setBusy('proposal')
    setError('')
    setProposal(null)
    setResult(null)
    try {
      const payload = await api<Proposal>(`/api/v1/autofix/intake/${intake.session_id}/proposal`, { method: 'POST' })
      setProposal(payload)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to generate grounded proposal')
    } finally {
      setBusy('')
    }
  }

  async function apply() {
    if (!intake || !proposal || proposal.strategy === 'NONE') return
    setBusy('apply')
    setError('')
    try {
      const payload = await api<IntakeResult>(`/api/v1/autofix/intake/${intake.session_id}/apply`, { method: 'POST' })
      setResult(payload)
      setProposal(null)
    } catch (reason) {
      setProposal(null)
      setResult(null)
      setError(reason instanceof Error ? reason.message : 'Apply failed; generate a fresh preview')
    } finally {
      setBusy('')
    }
  }

  const modelConnected = probe?.connected ?? (runtime?.mode !== 'DETERMINISTIC_FALLBACK' && runtime?.ready === true)
  const canCreate = problem.trim().length >= 8 && uploads.length > 0 && !busy
  const canApply = !!proposal && proposal.strategy !== 'NONE' && !!proposal.diff && !result

  return (
    <main className="judge-intake-page">
      <section className="judge-intake-hero">
        <div>
          <span className="judge-kicker"><Sparkles size={14} /> JUDGE-SUPPLIED BUG INTAKE</span>
          <h1>Give us your bug. Give us your files. Make the agent prove its work.</h1>
          <p>
            Type a real problem statement and attach source/test files. The system creates an isolated copy, retrieves relevant engineering knowledge,
            calls the configured local/free model, previews an exact bounded patch, and only writes after review.
          </p>
        </div>
        <div className={`judge-model-proof ${modelConnected ? 'connected' : ''}`}>
          <Bot size={20} />
          <div>
            <small>MODEL PATH</small>
            <strong>{runtime?.provider ?? 'checking…'}</strong>
            <span>{runtime?.model ?? '—'}</span>
          </div>
          <button type="button" onClick={probeModel} disabled={!!busy}>
            {busy === 'probe' ? 'Probing…' : 'Test Qwen now'}
          </button>
        </div>
      </section>

      {probe && (
        <section className={`judge-probe-result ${probe.connected ? 'pass' : 'fail'}`}>
          {probe.connected ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
          <div>
            <strong>{probe.connected ? 'Live model call succeeded' : 'Live model call unavailable'}</strong>
            <span>{probe.provider} · {probe.model} · {probe.latency_ms} ms{probe.reply ? ` · reply: ${probe.reply}` : ''}</span>
            <p>{probe.note}</p>
          </div>
        </section>
      )}

      <section className="judge-intake-grid">
        <article className="judge-panel judge-input-panel">
          <div className="judge-panel-title"><SearchCheck size={19} /><div><small>01 · BUG REPORT</small><h2>Describe the failure</h2></div></div>
          <textarea
            value={problem}
            onChange={(event) => {
              setProblem(event.target.value)
              setIntake(null)
              setProposal(null)
              setResult(null)
            }}
            placeholder="Example: Valid Bearer authentication returns 401. The included test expects HTTP 200 for demo-valid-token. Find the smallest code fix and prove it with the supplied test."
            rows={7}
          />
          <div className="judge-helper">Be concrete: expected behavior, observed behavior, error/log, and which test or endpoint demonstrates it.</div>
        </article>

        <article className="judge-panel judge-upload-panel">
          <div className="judge-panel-title"><UploadCloud size={19} /><div><small>02 · FILE EVIDENCE</small><h2>Attach source + tests</h2></div></div>
          <label className="judge-dropzone">
            <FileUp size={26} />
            <strong>Select up to 12 text/code files</strong>
            <span>.py · .js · .jsx · .ts · .tsx · .json · .yaml · .toml · .md · .txt · max 256 KB each</span>
            <input
              type="file"
              multiple
              accept=".py,.js,.jsx,.ts,.tsx,.json,.yaml,.yml,.toml,.md,.txt"
              onChange={onFiles}
            />
          </label>
          <div className="judge-files">
            {uploads.length === 0 && <span>No files selected yet.</span>}
            {uploads.map((file) => (
              <div key={file.path}><FileCode2 size={14} /><strong>{file.path}</strong><span>{Math.ceil(file.size / 1024)} KB</span></div>
            ))}
          </div>
          <label className="judge-trust-toggle">
            <input type="checkbox" checked={trusted} onChange={(event) => setTrusted(event.target.checked)} />
            <span><strong>Trusted test execution</strong><small>Run uploaded Python `test_*.py` with pytest. Enable only for files you trust.</small></span>
          </label>
        </article>
      </section>

      <section className="judge-actionbar">
        <button type="button" onClick={createSession} disabled={!canCreate}>
          <FlaskConical size={16} /> {busy === 'intake' ? 'Creating isolated workspace…' : '1. Analyze files + retrieve RAG'}
        </button>
        <button type="button" className="secondary" onClick={preview} disabled={!intake || !!busy || !!result}>
          <Bot size={16} /> {busy === 'proposal' ? 'Qwen reasoning…' : '2. Preview grounded AI fix'}
        </button>
        <button type="button" className="primary" onClick={apply} disabled={!canApply || !!busy}>
          <Play size={16} /> {busy === 'apply' ? 'Applying + verifying…' : '3. Apply reviewed patch + verify'}
        </button>
      </section>

      {error && <div className="judge-error"><XCircle size={17} /> {error}</div>}

      {intake && (
        <section className="judge-intake-grid">
          <article className="judge-panel">
            <div className="judge-panel-title"><FlaskConical size={19} /><div><small>BASELINE</small><h2>Verification evidence</h2></div><VerificationBadge evidence={intake.before_verification} /></div>
            <div className="judge-meta-row"><span>Session</span><strong>{intake.session_id}</strong></div>
            <div className="judge-meta-row"><span>Mode</span><strong>{intake.execution_mode}</strong></div>
            <code className="judge-command">{intake.before_verification.command}</code>
            <pre className="judge-terminal">{intake.before_verification.output}</pre>
            <div className="judge-safety"><ShieldCheck size={15} /> {intake.safe_boundary}</div>
          </article>

          <article className="judge-panel">
            <div className="judge-panel-title"><SearchCheck size={19} /><div><small>RAG</small><h2>Retrieved engineering knowledge</h2></div></div>
            {intake.knowledge.length === 0 ? (
              <div className="judge-empty">No strong runbook match. The agent will not pretend RAG found one.</div>
            ) : intake.knowledge.map((hit) => (
              <div className="judge-rag-hit" key={hit.id}>
                <div><strong>{hit.id} · {hit.component}</strong><span>{Math.round(hit.score * 100)}% match</span></div>
                <p>{hit.issue}</p>
                <small>{hit.fix}</small>
              </div>
            ))}
          </article>
        </section>
      )}

      {proposal && (
        <section className="judge-panel judge-proposal">
          <div className="judge-panel-title"><Bot size={19} /><div><small>REVIEWED PATCH</small><h2>{proposal.strategy === 'AI_GROUNDED' ? 'Grounded model proposal' : 'No safe generic proposal'}</h2></div></div>
          <div className="judge-proposal-meta">
            <span>{proposal.reasoning_provider}</span><span>{proposal.reasoning_model}</span><span>{Math.round(proposal.confidence * 100)}% bounded confidence</span>
          </div>
          <p>{proposal.summary}</p>
          {proposal.fallback_reason && <div className="judge-safety"><ShieldCheck size={15} /> {proposal.fallback_reason}</div>}
          {proposal.diff ? <pre className="judge-terminal diff">{proposal.diff}</pre> : <div className="judge-empty">No file will be changed. Connect Qwen/Ollama or provide stronger evidence.</div>}
        </section>
      )}

      {result && (
        <section className={`judge-final ${result.final_status === 'ROLLED_BACK' ? 'fail' : 'pass'}`}>
          <div>{result.final_status === 'ROLLED_BACK' ? <XCircle size={30} /> : <CheckCircle2 size={30} />}</div>
          <div>
            <small>FINAL STATE</small>
            <h2>{result.final_status.replaceAll('_', ' ')}</h2>
            <p>
              {result.final_status === 'VERIFIED_FIXED'
                ? 'A trusted failing pytest contract passed after the exact reviewed patch.'
                : result.final_status === 'STATIC_CHECK_PASSED'
                  ? 'The isolated copy was patched and static checks pass. Functional recovery is not claimed without a failing trusted test.'
                  : 'The candidate failed verification and the original uploaded file was restored.'}
            </p>
          </div>
          <VerificationBadge evidence={result.after_verification} />
        </section>
      )}

      {result && (
        <section className="judge-intake-grid">
          <article className="judge-panel">
            <div className="judge-panel-title"><FlaskConical size={19} /><div><small>AFTER</small><h2>Validator output</h2></div></div>
            <code className="judge-command">{result.after_verification.command}</code>
            <pre className="judge-terminal">{result.after_verification.output}</pre>
          </article>
          <article className="judge-panel">
            <div className="judge-panel-title"><ShieldCheck size={19} /><div><small>AUDIT</small><h2>What the agent actually did</h2></div></div>
            <ol className="judge-audit">{result.audit.map((entry, index) => <li key={`${index}-${entry}`}><span>{index + 1}</span>{entry}</li>)}</ol>
          </article>
        </section>
      )}
    </main>
  )
}
