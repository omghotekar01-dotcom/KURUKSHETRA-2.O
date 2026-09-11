import { Activity, GitBranch, History, ShieldCheck, Sparkles } from 'lucide-react'

const stages = ['Intake', 'Triage', 'Evidence', 'RCA', 'Remediation', 'Approval', 'Verification']

export default function App() {
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
      </aside>

      <section className="content">
        <header>
          <div>
            <p className="eyebrow">KURUKSHETRA 2.0 · WORKING BUILD</p>
            <h1>Evidence-backed incident response</h1>
            <p className="muted">Investigate, propose, approve and verify in one auditable workflow.</p>
          </div>
          <span className="status">● Demo-ready architecture</span>
        </header>

        <section className="stage-row">
          {stages.map((stage, i) => <div key={stage} className={i < 3 ? 'stage active' : 'stage'}><span>{i + 1}</span>{stage}</div>)}
        </section>

        <section className="grid">
          <article className="panel hero-panel">
            <div className="panel-title"><span>Incident #K-042</span><span className="pill high">HIGH</span></div>
            <h2>401 errors after today&apos;s deployment</h2>
            <p className="muted">Production users can authenticate, but API requests immediately return unauthorized responses.</p>
            <div className="facts">
              <div><small>Component</small><strong>Authentication</strong></div>
              <div><small>Owner</small><strong>auth-team</strong></div>
              <div><small>Confidence</small><strong>87%</strong></div>
            </div>
          </article>

          <article className="panel">
            <div className="panel-title">Evidence</div>
            <ul className="evidence-list">
              <li><b>Runbook match</b><span>JWT rotation mismatch · 0.86</span></li>
              <li><b>Recent change</b><span>Auth config updated 18 min ago</span></li>
              <li><b>Log signal</b><span>signature verification failed</span></li>
            </ul>
          </article>

          <article className="panel">
            <div className="panel-title">Top hypothesis</div>
            <h3>JWT signing secret mismatch after deployment</h3>
            <p className="muted">Two independent signals support the same failure mode. Verification is still required before resolution.</p>
            <div className="confidence"><span style={{ width: '84%' }} /></div>
            <small>84% combined confidence</small>
          </article>

          <article className="panel action-panel">
            <div className="panel-title">Proposed action <span className="pill medium">APPROVAL REQUIRED</span></div>
            <p>Open a draft remediation PR and run non-production authentication tests.</p>
            <div className="button-row"><button className="secondary">Reject</button><button className="primary">Review action</button></div>
          </article>
        </section>
      </section>
    </main>
  )
}
