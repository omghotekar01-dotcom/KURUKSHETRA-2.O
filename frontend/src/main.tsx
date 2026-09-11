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

const path = window.location.pathname.replace(/\/+$/, '') || '/'
const screen = path === '/evidence' ? <RepositoryEvidencePage /> : <App />

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {screen}
    <ThemeToggle />
  </React.StrictMode>,
)
