import {
  Activity,
  Beaker,
  Bot,
  FileSearch,
  FileUp,
  Gauge,
  GitPullRequest,
  Menu,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-react'
import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Readiness = {
  status: 'READY' | 'DEGRADED'
  mode: 'LIVE_FIRST' | 'FALLBACK_DEMO'
}

const items = [
  { href: '/', label: 'AI Workspace', icon: Bot },
  { href: '/incidents', label: 'Incident Command', icon: Activity },
  { href: '/prototype', label: 'Real AutoFix', icon: ScanSearch },
  { href: '/intake', label: 'Judge Intake', icon: FileUp },
  { href: '/demo', label: 'Judge Demo', icon: Sparkles },
  { href: '/ai', label: 'AI Reasoning Lab', icon: Bot },
  { href: '/evidence', label: 'Evidence Lab', icon: FileSearch },
  { href: '/remediate', label: 'Remediation', icon: GitPullRequest },
  { href: '/evaluation', label: 'Evaluation Lab', icon: Beaker },
  { href: '/readiness', label: 'Readiness', icon: Gauge },
]

function normalizedPath() {
  return window.location.pathname.replace(/\/+$/, '') || '/'
}

export default function AppNavigation() {
  const [open, setOpen] = useState(false)
  const [readiness, setReadiness] = useState<Readiness | null>(null)
  const path = normalizedPath()

  useEffect(() => {
    let cancelled = false
    void fetch(`${API_BASE}/api/v1/evaluation/readiness`)
      .then(async (response) => {
        if (!response.ok) return null
        return response.json() as Promise<Readiness>
      })
      .then((payload) => {
        if (!cancelled && payload) setReadiness(payload)
      })
      .catch(() => {
        if (!cancelled) setReadiness(null)
      })
    return () => { cancelled = true }
  }, [])

  return (
    <>
      <button
        className="global-nav-toggle"
        type="button"
        aria-label={open ? 'Close navigation' : 'Open navigation'}
        onClick={() => setOpen((value) => !value)}
      >
        {open ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside className={`global-nav ${open ? 'is-open' : ''}`}>
        <a className="global-nav-brand" href="/">
          <span className="global-nav-logo"><Sparkles size={17} /></span>
          <span>
            <strong>Bug Router</strong>
            <small>Agentic engineering workspace</small>
          </span>
        </a>

        <div className="global-nav-section-label">Workspace</div>
        <nav className="global-nav-links" aria-label="Application navigation">
          {items.map(({ href, label, icon: Icon }) => {
            const active = href === '/'
              ? path === '/' || path === '/workspace'
              : path === href || (href === '/prototype' && path === '/autofix')
            return (
              <a
                key={href}
                href={href}
                className={active ? 'global-nav-link active' : 'global-nav-link'}
                aria-current={active ? 'page' : undefined}
                onClick={() => setOpen(false)}
              >
                <Icon size={17} />
                <span>{label}</span>
              </a>
            )
          })}
        </nav>

        <div className="global-nav-spacer" />
        <div className="global-nav-trust">
          <div className="global-nav-trust-title"><ShieldCheck size={15} /> Human authority</div>
          <p>Live evidence first. Exact reviewed writes only. Draft PRs stay unmerged until a human decides on GitHub.</p>
        </div>
        <div className="global-nav-runtime">
          <span className={`runtime-dot ${readiness?.status === 'READY' ? 'ready' : ''}`} />
          <div>
            <strong>{readiness?.status ?? 'Checking runtime'}</strong>
            <small>{readiness?.mode === 'FALLBACK_DEMO' ? 'Fallback demo' : 'Live-first'}</small>
          </div>
        </div>
      </aside>

      {open && <button className="global-nav-backdrop" type="button" aria-label="Close navigation" onClick={() => setOpen(false)} />}
    </>
  )
}
