import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import BugWorkspacePage from './BugWorkspacePage'
import TestLabPage from './TestLabPage'
import RepositoryEvidencePage from './RepositoryEvidencePage'
import PatchRemediationPage from './PatchRemediationPage'
import EvaluationLabPage from './EvaluationLabPage'
import ReadinessPage from './ReadinessPage'
import JudgeDemoPage from './JudgeDemoPage'
import AgentIntelligencePage from './AgentIntelligencePage'
import AutofixPrototypePage from './AutofixPrototypePage'
import JudgeIntakePage from './JudgeIntakePage'
import AppNavigation from './AppNavigation'
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
import './app-navigation.css'
import './agent-intelligence.css'
import './autofix-prototype.css'
import './autofix-strategy.css'
import './judge-intake.css'
import './bug-workspace.css'
import './workspace-depth.css'
import './test-lab.css'
import './apple-polish.css'
import './dark-polish.css'
import './busy-polish.css'
import './purple-product-system.css'
import './async-state-polish.css'

const path = window.location.pathname.replace(/\/+$/, '') || '/'
const screen = path === '/' || path === '/workspace'
  ? <BugWorkspacePage />
  : path === '/test'
    ? <TestLabPage />
    : path === '/incidents'
      ? <App />
      : path === '/demo'
        ? <JudgeDemoPage />
        : path === '/prototype' || path === '/autofix'
          ? <AutofixPrototypePage />
          : path === '/intake'
            ? <JudgeIntakePage />
            : path === '/ai'
              ? <AgentIntelligencePage />
              : path === '/readiness'
                ? <ReadinessPage />
                : path === '/evaluation'
                  ? <EvaluationLabPage />
                  : path === '/remediate'
                    ? <PatchRemediationPage />
                    : path === '/evidence'
                      ? <RepositoryEvidencePage />
                      : <BugWorkspacePage />

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div className="global-app-shell">
      <AppNavigation />
      <div className="global-app-main">
        {screen}
      </div>
    </div>
    <ThemeToggle />
  </React.StrictMode>,
)
