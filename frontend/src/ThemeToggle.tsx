import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'

type Theme = 'light' | 'dark'

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  const saved = window.localStorage.getItem('incident-command-theme')
  return saved === 'dark' ? 'dark' : 'light'
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.style.colorScheme = theme
    window.localStorage.setItem('incident-command-theme', theme)
  }, [theme])

  return (
    <div className="theme-switcher" role="group" aria-label="Color theme">
      <button
        type="button"
        className={theme === 'light' ? 'theme-option active' : 'theme-option'}
        onClick={() => setTheme('light')}
        aria-pressed={theme === 'light'}
        title="Use light theme"
      >
        <Sun size={15} />
        <span>Light</span>
      </button>
      <button
        type="button"
        className={theme === 'dark' ? 'theme-option active' : 'theme-option'}
        onClick={() => setTheme('dark')}
        aria-pressed={theme === 'dark'}
        title="Use dark theme"
      >
        <Moon size={15} />
        <span>Dark</span>
      </button>
    </div>
  )
}
