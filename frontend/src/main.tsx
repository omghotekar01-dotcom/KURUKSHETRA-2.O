import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import RepositoryEvidencePage from './RepositoryEvidencePage'
import ThemeToggle from './ThemeToggle'
import './styles.css'
import './workflow.css'
import './theme.css'
import './repository-theme.css'
import './evidence-page.css'
import './source-context.css'
import './patch-proposal.css'

const path = window.location.pathname.replace(/\/+$/, '') || '/'
const evidenceMode = path === '/evidence'
const screen = evidenceMode ? <RepositoryEvidencePage /> : <App />

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {screen}
    {!evidenceMode && <a className="evidence-lab-shortcut" href="/evidence">Live Evidence Lab</a>}
    <ThemeToggle />
  </React.StrictMode>,
)
