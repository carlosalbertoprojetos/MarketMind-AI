import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { stopLocalSystem } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'
import { buildPrefetchHandlers } from '../utils/routePrefetch'

function PowerButtonIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2v10" />
      <path d="M5.2 5.2a9 9 0 1 0 13.6 0" />
    </svg>
  )
}

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </svg>
  )
}

export default function Navbar() {
  const { isAuthenticated } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const { addToast } = useToast()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [stoppingLocal, setStoppingLocal] = useState(false)

  const showLocalStopButton = useMemo(() => {
    if (typeof window === 'undefined') return false
    return isAuthenticated && ((import.meta.env.MODE === 'test') || (import.meta.env.VITE_MARKETINGAI_LOCAL_CONTROL === '1' && ['127.0.0.1', 'localhost'].includes(window.location.hostname)))
  }, [isAuthenticated])

  const handleStopLocal = async () => {
    if (!window.confirm('Encerrar backend e frontend locais agora?')) return
    setStoppingLocal(true)
    try {
      await stopLocalSystem()
      addToast('Encerramento local iniciado.')
      setMobileOpen(false)
    } catch (e) {
      addToast(e.message || 'Nao foi possivel encerrar o sistema local', 'error')
      setStoppingLocal(false)
      return
    }
    window.setTimeout(() => {
      setStoppingLocal(false)
    }, 4000)
  }

  const closeMobileMenu = () => setMobileOpen(false)

  const dashboardPrefetchProps = buildPrefetchHandlers(['dashboard'])
  const aboutPrefetchProps = buildPrefetchHandlers(['about'])
  const calendarPrefetchProps = buildPrefetchHandlers(['calendar'])
  const credentialsPrefetchProps = buildPrefetchHandlers(['credentials'])
  const mediaPrefetchProps = buildPrefetchHandlers(['media'])
  const finalContentPrefetchProps = buildPrefetchHandlers(['finalContent'])
  const loginPrefetchProps = buildPrefetchHandlers(['login'])
  const registerPrefetchProps = buildPrefetchHandlers(['register'])

  const isDarkTheme = theme === 'dark'
  const themeTitle = isDarkTheme ? 'Ativar modo claro' : 'Ativar modo escuro'

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="mx-auto max-w-6xl flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold text-primary-600 dark:text-primary-400">
          MarketingAI
        </Link>
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-4">
              <Link to="/" {...dashboardPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Dashboard</Link>
              <Link to="/sobre" {...aboutPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
              <Link to="/calendar" {...calendarPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendario</Link>
              <Link to="/credentials" {...credentialsPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
              <Link to="/media" {...mediaPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Midia</Link>
              <Link to="/final-content" {...finalContentPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Studio IA</Link>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-4">
              <Link to="/sobre" {...aboutPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
              <Link to="/login" {...loginPrefetchProps} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
              <Link to="/register" {...registerPrefetchProps} className="bg-primary-500 text-white px-3 py-1.5 rounded hover:bg-primary-600">Cadastrar</Link>
            </div>
          )}
          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
            title={themeTitle}
            aria-label="Alternar tema"
          >
            {isDarkTheme ? <SunIcon /> : <MoonIcon />}
          </button>
          {showLocalStopButton && (
            <div className="hidden md:flex items-center gap-2">
              <div className="group relative">
                <button
                  type="button"
                  onClick={handleStopLocal}
                  disabled={stoppingLocal}
                  title="Encerrar sistema local"
                  aria-label="Encerrar sistema local"
                  className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-red-300 bg-white text-red-600 shadow-sm transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-red-800 dark:bg-gray-800 dark:text-red-400 dark:hover:bg-red-950/30"
                >
                  <PowerButtonIcon />
                </button>
                <div className="pointer-events-none absolute right-0 top-12 z-10 hidden w-56 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs text-gray-700 shadow-lg group-hover:block dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200">
                  Encerra backend e frontend locais usando o stop.bat.
                </div>
              </div>
            </div>
          )}
          <button
            type="button"
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden inline-flex items-center justify-center rounded border border-gray-300 dark:border-gray-600 p-1.5 text-gray-600 dark:text-gray-300"
            aria-label="Abrir menu"
            title="Menu"
          >
            Menu
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden mt-3 border-t border-gray-200 dark:border-gray-700 pt-3">
          <div className="flex flex-col gap-2 text-sm">
            {isAuthenticated ? (
              <>
                <Link to="/" {...dashboardPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Dashboard</Link>
                <Link to="/sobre" {...aboutPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/calendar" {...calendarPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendario</Link>
                <Link to="/credentials" {...credentialsPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
                <Link to="/media" {...mediaPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Midia</Link>
                <Link to="/final-content" {...finalContentPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Studio IA</Link>
                {showLocalStopButton && (
                  <button type="button" onClick={handleStopLocal} className="text-left text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300">
                    Encerrar sistema local
                  </button>
                )}
              </>
            ) : (
              <>
                <Link to="/sobre" {...aboutPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/login" {...loginPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
                <Link to="/register" {...registerPrefetchProps} onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Cadastrar</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
