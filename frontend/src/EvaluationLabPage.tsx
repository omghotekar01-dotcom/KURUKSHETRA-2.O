import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, CheckCircle2, Loader2, RefreshCw, ShieldCheck, XCircle } from 'lucide-react'
import LoadingShimmer from './LoadingShimmer'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Metric = {
  key: string
  label: string
  value: number
  passed: number
  total: number
  description: string
}

type CaseResult = {
  case_id: string
  category: string
  title: string
  passed: boolean
  expected: string
  observed: string
  details: Record<string, unknown>
}

type EvaluationReport = {
  generated_at: string
  benchmark_version: string
  deterministic: boolean
  metrics: Metric[]
  cases: CaseResult[]
  overall_score: number
  notes: string[]
}

export default function EvaluationLabPage() {
  const [report, setReport] = useState<EvaluationReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('all')

  async function runBenchmark() {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/run`)
      if (!response.ok) throw new Error('The benchmark could not be completed. Check the backend and try again.')
      setReport(await response.json())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The benchmark is temporarily unavailable.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void runBenchmark()
  }, [])

  const categories = useMemo(() => {
    if (!report) return []
    return Array.from(new Set(report.cases.map((item) => item.category)))
  }, [report])

  const visibleCases = useMemo(() => {
    if (!report) return []
    if (category === 'all') return report.cases
    return report.cases.filter((item) => item.category === category)
  }, [report, category])

  return (
    <main className="evaluation-page">
      <header className="evaluation-topbar">
        <a href="/" className="back-link"><ArrowLeft size={16} /> AI Workspace</a>
        <div className="measured-badge"><span /> MEASURED · NOT HARDCODED</div>
      </header>

      <section className="evaluation-hero">
        <div>
          <p className="evaluation-eyebrow">EVALUATION LAB</p>
          <h1>Prove the agent before asking anyone to trust it.</h1>
          <p>Repeatable benchmark incidents exercise routing, evidence retrieval, RCA grounding and action safety. Every score is computed by the backend when this page loads.</p>
        </div>
        <button type="button" onClick={() => void runBenchmark()} disabled={loading}>
          {loading ? <><Loader2 className="spin" size={16} /> Running measured checks…</> : <><RefreshCw size={16} /> Run benchmark again</>}
        </button>
      </section>

      {error && <div className="evaluation-error">{error}</div>}

      {loading && !report && (
        <section className="evaluation-loading-grid" aria-label="Running measured benchmark checks">
          <LoadingShimmer lines={4} label="Calculating measured benchmark score" />
          <LoadingShimmer lines={5} label="Checking routing and retrieval behavior" />
          <LoadingShimmer lines={5} label="Checking RCA and action safety" />
        </section>
      )}

      {report && (
        <>
          <section className={`score-hero-card ${loading ? 'is-refreshing' : ''}`}>
            <div>
              <small>Measured benchmark score</small>
              <strong>{Math.round(report.overall_score * 100)}%</strong>
              <span>Simple mean of the displayed metric ratios</span>
            </div>
            <div className="score-meta">
              <span><b>{report.cases.length}</b> benchmark checks</span>
              <span><b>{report.benchmark_version}</b> benchmark version</span>
              <span><b>{new Date(report.generated_at).toLocaleString()}</b> generated</span>
            </div>
          </section>

          {loading && (
            <section className="evaluation-refresh-strip">
              <Loader2 className="spin" size={15} /> Re-running the same benchmark contract. Existing results remain visible until the new measured report is ready.
            </section>
          )}

          <section className="metric-grid">
            {report.metrics.map((metric) => (
              <article className="metric-card" key={metric.key}>
                <div className="metric-head">
                  <span>{metric.label}</span>
                  <strong>{Math.round(metric.value * 100)}%</strong>
                </div>
                <div className="metric-bar"><span style={{ width: `${metric.value * 100}%` }} /></div>
                <p>{metric.description}</p>
                <small>{metric.passed} / {metric.total} checks passed</small>
              </article>
            ))}
          </section>

          <section className="evaluation-section">
            <div className="evaluation-section-head">
              <div>
                <h2>Benchmark evidence</h2>
                <p>Every row exposes the expected and observed system behavior.</p>
              </div>
              <select value={category} onChange={(event) => setCategory(event.target.value)}>
                <option value="all">All categories</option>
                {categories.map((item) => <option value={item} key={item}>{item}</option>)}
              </select>
            </div>

            <div className="evaluation-case-list">
              {visibleCases.map((item) => (
                <article className={item.passed ? 'evaluation-case passed' : 'evaluation-case failed'} key={item.case_id}>
                  <div className="case-status">
                    {item.passed ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                  </div>
                  <div className="case-body">
                    <div className="case-title-row">
                      <div><small>{item.category}</small><h3>{item.title}</h3></div>
                      <b>{item.passed ? 'PASS' : 'FAIL'}</b>
                    </div>
                    <div className="case-comparison">
                      <div><small>Expected</small><span>{item.expected}</span></div>
                      <div><small>Observed</small><span>{item.observed}</span></div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="evaluation-trust-card">
            <ShieldCheck size={22} />
            <div>
              <h2>Truth boundary</h2>
              {report.notes.map((note) => <p key={note}>{note}</p>)}
            </div>
          </section>
        </>
      )}
    </main>
  )
}
