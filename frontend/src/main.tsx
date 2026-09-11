import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import RepositoryEvidencePage from './RepositoryEvidencePage'
import PatchRemediationPage from './PatchRemediationPage'
import EvaluationLabPage from './EvaluationLabPage'
import ReadinessPage from './ReadinessPage'
import JudgeDemoPage from './JudgeDemoPage'
import ThemeToggle from './ThemeToggle'
import './styles.css'
import './workflow.css'
import './theme.css'
import './repository-theme.css'
import './evidence-page.css'
import './source-context.css'
import './patch-proposal.css'
import './remediation-page.css'
import './remediation-ci.css'
import './evaluation-page.css'
import './readiness-page.css'
import './judge-demo.css'

const path = window.location.pathname.replace(/\/+$/, '') || '/'
const evidenceMode = path === '/evidence'
const remediationMode = path === '/remediate'
const evaluationMode = path === '/evaluation'
const readinessMode = path === '/readiness'
const judgeMode = path === '/demo'
const screen = judgeMode
  ? <JudgeDemoPage />
  : readinessMode
    ? <ReadinessPage />
    : evaluationMode
      ? <EvaluationLabPage />
      : remediationMode
        ? <PatchRemediationPage />
        : evidenceMode
          ? <RepositoryEvidencePage />
          : <App />

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {screen}
    {!evidenceMode && !remediationMode && !evaluationMode && !readinessMode && !judgeMode && <>
      <a className="judge-mode-shortcut" href="/demo">Judge Mode</a>
      <a className="evidence-lab-shortcut" href="/evidence">Live Evidence Lab</a>
      <a className="evidence-lab-shortcut remediation-shortcut" href="/remediate">Remediation Studio</a>
      <a className="evidence-lab-shortcut evaluation-shortcut" href="/evaluation">Evaluation Lab</a>
    </>}
    <ThemeToggle />
  </React.StrictMode>,
)
