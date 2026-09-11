import {
  Bot,
  CheckCircle2,
  ChevronRight,
  FileCode2,
  FolderLock,
  Play,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Wrench,
  XCircle,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Target = {
  id: string
  name: string
  description: string
  relative_path: string
  problem: string
  proof: string
  validator: string
}

type CommandEvidence = {
  command: string
  exit_code: number
  output: string
  passed: boolean
  duration_ms: number
}

type Diagnosis = {
  target_id: string
  status: 'BUG_CONFIRMED' | 'HEALTHY' | 'UNRESOLVED'
  summary: string
  file_path?: string | null
  line_number?: number | null
  evidence: string[]
  expected_value?: string | null
  observed_value?: string | null
  confidence: number
}

type Scan = {
  target: Target
  workspace_path: string
  files: { path: string; size_bytes: number }[]
  verification: CommandEvidence
  diagnosis: Diagnosis
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

type FixResult = {
  target: Target
  before_verification: CommandEvidence
  diagnosis: Diagnosis
  proposal: Proposal
  applied: boolean
  rolled_back: boolean
  after_verification: CommandEvidence
  final_status: 'FIXED' | 'ROLLED_BACK' | 'ALREADY_HEALTHY' | 'UNRESOLVED'
  audit: string[]
}

type ModelRuntime = {
  mode: 'LOCAL_OLLAMA' | 'GEMINI_FREE' | 'DETERMINISTIC_FALLBACK'
  provider: string
  model: string
  ready: boolean
  endpoint?: string | null
  note: string
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const payload = await response.json() as { detail?: string }
      if (payload.detail) detail = payload.detail
    } catch {
      // keep HTTP fallback
    }
    throw new Error(detail)
  }
  return response.json() as Promise<T>
}

function PassFail({ passed }: { passed: boolean }) {
  return (
    <span className={`autofix-proof ${passed ? 'pass' : 'fail'}`}>
      {passed ? <CheckCircle2 size={15} /> : <XCircle size={15} />}
      {passed ? 'PASS' : 'FAIL'}
    </span>
  )
}

function StrategyBadge({ proposal }: { proposal: Proposal }) {
  const ai = proposal.strategy === 'AI_GROUNDED'
  const label = ai ? 'AI GROUNDED PATCH' : proposal.strategy === 'DETERMINISTIC_SAFE_RULE' ? 'SAFE FALLBACK PATCH' : 'NO PATCH'
  return (
    <div className="proposal-strategy">
      <span className={ai ? 'strategy-chip ai' : 'strategy-chip safe'}>{ai ? <Bot size={13} /> : <ShieldCheck size={13} />}{label}</span>
      <small>{proposal.reasoning_provider} · {proposal.reasoning_model}</small>
    </div>
  )
}

export default function AutofixPrototypePage() {
  const [targets, setTargets] = useState<Target[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [runtime, setRuntime] = useState<ModelRuntime | null>(null)
  const [scan, setScan] = useState<Scan | null>(null)
  const [proposal, setProposal] = useState<Proposal | null>(null)
  const [result, setResult] = useState<FixResult | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  const selected = useMemo(
    () => targets.find((target) => target.id === selectedId) ?? targets[0],
    [selectedId, targets],
  )

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api<Target[]>('/api/v1/autofix/targets'),
      api<ModelRuntime>('/api/v1/autofix/model-runtime'),
    ]).then(([targetPayload, runtimePayload]) => {
      if (cancelled) return
      setTargets(targetPayload)
      setSelectedId(targetPayload[0]?.id ?? '')
      setRuntime(runtimePayload)
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : 'Unable to load AutoFix runtime')
    })
    return () => { cancelled = true }
  }, [])

  async function runAction<T>(name: string, path: string, setter: (value: T) => void) {
    if (!selected) return
    setBusy(name)
    setError('')
    try {
      const payload = await api<T>(path, { method: 'POST' })
      setter(payload)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Operation failed')
    } finally {
      setBusy('')
    }
  }

  async function reset() {
    setProposal(null)
    setResult(null)
    await runAction<Scan>('reset', `/api/v1/autofix/${selected.id}/reset`, setScan)
  }

  async function scanWorkspace() {
    setProposal(null)
    setResult(null)
    await runAction<Scan>('scan', `/api/v1/autofix/${selected.id}/scan`, setScan)
  }

  async function previewFix() {
    setProposal(null)
    setResult(null)
    await runAction<Proposal>('proposal', `/api/v1/autofix/${selected.id}/proposal`, setProposal)
  }

  async function autoFix() {
    await runAction<FixResult>('apply', `/api/v1/autofix/${selected.id}/apply`, (payload) => {
      setResult(payload)
      setProposal(payload.proposal)
    })
  }

  function selectTarget(targetId: string) {
    setSelectedId(targetId)
    setScan(null)
    setProposal(null)
    setResult(null)
    setError('')
  }

  const providerLabel = runtime?.mode === 'LOCAL_OLLAMA'
    ? 'Local Ollama'
    : runtime?.mode === 'GEMINI_FREE'
      ? 'Gemini free tier'
      : 'Deterministic verifier'

  const canPreview = !!scan && !scan.verification.passed && scan.diagnosis.status === 'BUG_CONFIRMED' && !result
  const canApply = !!proposal && proposal.strategy !== 'NONE' && !!proposal.diff && !result

  return (
    <main className="autofix-page">
      <section className="autofix-hero">
        <div>
          <span className="autofix-kicker"><Sparkles size={14} /> REAL AUTOFIX PROTOTYPE</span>
          <h1>Break it. Scan it. Repair the real files. Prove it.</h1>
          <p>
            This is not a simulated chat response. The platform opens an allowlisted local project, runs its real tests,
            traces the failing contract to source code, edits the exact file, reruns the same validator and rolls back automatically if verification fails.
          </p>
        </div>
        <div className="autofix-runtime-card">
          <span className={`runtime-orb ${runtime?.ready ? 'ready' : ''}`}><Bot size={19} /></span>
          <div>
            <small>AI runtime · ₹0 required</small>
            <strong>{providerLabel}</strong>
            <span>{runtime?.model ?? 'checking...'}</span>
          </div>
        </div>
      </section>

      <section className="autofix-pipeline" aria-label="AutoFix pipeline">
        {[
          ['01', 'Scan workspace'],
          ['02', 'Run failing tests'],
          ['03', 'Ground diagnosis'],
          ['04', 'Patch exact file'],
          ['05', 'Rerun validator'],
          ['06', 'Prove or rollback'],
        ].map(([index, label], position, all) => (
          <div className="autofix-pipeline-step" key={index}>
            <span>{index}</span><strong>{label}</strong>
            {position < all.length - 1 && <ChevronRight size={14} />}
          </div>
        ))}
      </section>

      <section className="autofix-grid top-grid">
        <article className="autofix-card target-card">
          <div className="autofix-card-heading">
            <div><span className="eyebrow">LIVE TARGET</span><h2>{selected?.name ?? 'Loading target'}</h2></div>
            <FolderLock size={22} />
          </div>
          {targets.length > 1 && (
            <select value={selectedId} onChange={(event) => selectTarget(event.target.value)}>
              {targets.map((target) => <option value={target.id} key={target.id}>{target.name}</option>)}
            </select>
          )}
          <p>{selected?.description}</p>
          <div className="autofix-fact"><span>Broken behavior</span><strong>{selected?.problem}</strong></div>
          <div className="autofix-fact"><span>Proof contract</span><strong>{selected?.proof}</strong></div>
          <div className="autofix-path"><FileCode2 size={15} /> {selected?.relative_path}</div>
        </article>

        <article className="autofix-card runtime-card">
          <div className="autofix-card-heading">
            <div><span className="eyebrow">ZERO-COST AI</span><h2>{providerLabel}</h2></div>
            <Bot size={22} />
          </div>
          <p>{runtime?.note ?? 'Checking local model runtime...'}</p>
          <div className="runtime-lines">
            <div><span>Mode</span><strong>{runtime?.mode ?? 'CHECKING'}</strong></div>
            <div><span>Model</span><strong>{runtime?.model ?? '—'}</strong></div>
            <div><span>Ready</span><strong>{runtime?.ready ? 'YES' : 'NO / FALLBACK SAFE'}</strong></div>
          </div>
          <div className="autofix-security-note"><ShieldCheck size={16} /> Model text cannot execute arbitrary shell commands.</div>
        </article>
      </section>

      <section className="autofix-actionbar">
        <button onClick={reset} disabled={!selected || !!busy} className="secondary"><RefreshCw size={16} /> Reset broken target</button>
        <button onClick={scanWorkspace} disabled={!selected || !!busy}><ScanSearch size={16} /> {busy === 'scan' ? 'Scanning…' : '1. Scan + reproduce'}</button>
        <button onClick={previewFix} disabled={!canPreview || !!busy} className="secondary"><Wrench size={16} /> {busy === 'proposal' ? 'Reasoning…' : '2. Preview exact fix'}</button>
        <button onClick={autoFix} disabled={!canApply || !!busy} className="primary"><Play size={16} /> {busy === 'apply' ? 'Repairing + verifying…' : '3. Auto Fix + Verify'}</button>
      </section>

      {error && <div className="autofix-error"><XCircle size={17} /> {error}</div>}

      {scan && (
        <section className="autofix-grid evidence-grid">
          <article className="autofix-card proof-card">
            <div className="autofix-card-heading">
              <div><span className="eyebrow">BEFORE</span><h2>Real validator result</h2></div>
              <PassFail passed={scan.verification.passed} />
            </div>
            <div className="command-line"><TerminalSquare size={14} /> {scan.verification.command}</div>
            <pre>{scan.verification.output}</pre>
          </article>

          <article className="autofix-card diagnosis-card">
            <div className="autofix-card-heading">
              <div><span className="eyebrow">ROOT CAUSE</span><h2>{scan.diagnosis.status.replaceAll('_', ' ')}</h2></div>
              <span className="confidence">{Math.round(scan.diagnosis.confidence * 100)}%</span>
            </div>
            <p className="diagnosis-summary">{scan.diagnosis.summary}</p>
            {scan.diagnosis.file_path && (
              <div className="culprit-file"><FileCode2 size={17} /><strong>{scan.diagnosis.file_path}</strong><span>line {scan.diagnosis.line_number ?? '?'}</span></div>
            )}
            <ul>{scan.diagnosis.evidence.map((item) => <li key={item}>{item}</li>)}</ul>
            <div className="autofix-security-note"><FolderLock size={16} /> {scan.safe_boundary}</div>
          </article>
        </section>
      )}

      {proposal && proposal.diff && (
        <section className="autofix-card diff-card">
          <div className="autofix-card-heading">
            <div>
              <span className="eyebrow">EXACT PATCH</span>
              <h2>{proposal.file_path}</h2>
              <StrategyBadge proposal={proposal} />
            </div>
            <span className="confidence">{Math.round(proposal.confidence * 100)}%</span>
          </div>
          <p>{proposal.summary}</p>
          {proposal.fallback_reason && <div className="proposal-fallback"><ShieldCheck size={14} /> {proposal.fallback_reason}</div>}
          <pre className="diff-output">{proposal.diff}</pre>
        </section>
      )}

      {result && (
        <section className={`autofix-final ${result.final_status === 'FIXED' ? 'success' : 'warning'}`}>
          <div className="final-icon">{result.final_status === 'FIXED' ? <CheckCircle2 size={30} /> : <XCircle size={30} />}</div>
          <div className="final-copy">
            <span>VERIFICATION RESULT</span>
            <h2>{result.final_status === 'FIXED' ? 'Problem fixed and proven by the same test suite.' : result.final_status.replaceAll('_', ' ')}</h2>
            <p>The platform only reports FIXED after the post-edit validator exits successfully.</p>
          </div>
          <div className="before-after">
            <div><small>BEFORE</small><PassFail passed={result.before_verification.passed} /><span>exit {result.before_verification.exit_code}</span></div>
            <ChevronRight size={22} />
            <div><small>AFTER</small><PassFail passed={result.after_verification.passed} /><span>exit {result.after_verification.exit_code}</span></div>
          </div>
        </section>
      )}

      {result && (
        <section className="autofix-grid evidence-grid">
          <article className="autofix-card proof-card">
            <div className="autofix-card-heading"><div><span className="eyebrow">AFTER</span><h2>Verification output</h2></div><PassFail passed={result.after_verification.passed} /></div>
            <div className="command-line"><TerminalSquare size={14} /> {result.after_verification.command}</div>
            <pre>{result.after_verification.output}</pre>
          </article>
          <article className="autofix-card audit-card">
            <div className="autofix-card-heading"><div><span className="eyebrow">AUDIT TRAIL</span><h2>What actually happened</h2></div><ShieldCheck size={21} /></div>
            <ol>{result.audit.map((item, index) => <li key={`${index}-${item}`}><span>{index + 1}</span>{item}</li>)}</ol>
          </article>
        </section>
      )}
    </main>
  )
}
