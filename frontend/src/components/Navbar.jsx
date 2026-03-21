import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    setMobileOpen(false)
    navigate('/login')
  }

  const closeMobileMenu = () => setMobileOpen(false)

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="mx-auto max-w-6xl flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold text-primary-600 dark:text-primary-400">
          MarketingAI
        </Link>
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-4">
              <Link to="/" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Dashboard</Link>
              <Link to="/sobre" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
              <Link to="/calendar" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendário</Link>
              <Link to="/credentials" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
              <Link to="/media" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Mídia</Link>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-4">
              <Link to="/sobre" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
              <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
              <Link to="/register" className="bg-primary-500 text-white px-3 py-1.5 rounded hover:bg-primary-600">
                Cadastrar
              </Link>
            </div>
          )}
          {isAuthenticated ? (
            <>
              <button
                type="button"
                onClick={toggleTheme}
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm"
                title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
                aria-label="Alternar tema"
              >
                {theme === 'dark' ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
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
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79Z" />
                  </svg>
                )}
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                aria-label="Sair"
                title="Sair"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={toggleTheme}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm"
              title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
              aria-label="Alternar tema"
            >
              {theme === 'dark' ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
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
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79Z" />
                </svg>
              )}
            </button>
          )}
          <button
            type="button"
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden inline-flex items-center justify-center rounded border border-gray-300 dark:border-gray-600 p-1.5 text-gray-600 dark:text-gray-300"
            aria-label="Abrir menu"
            title="Menu"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="18"
              height="18"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              {mobileOpen ? (
                <>
                  <path d="M18 6 6 18" />
                  <path d="m6 6 12 12" />
                </>
              ) : (
                <>
                  <path d="M3 6h18" />
                  <path d="M3 12h18" />
                  <path d="M3 18h18" />
                </>
              )}
            </svg>
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden mt-3 border-t border-gray-200 dark:border-gray-700 pt-3">
          <div className="flex flex-col gap-2 text-sm">
            {isAuthenticated ? (
              <>
                <Link to="/" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Dashboard</Link>
                <Link to="/sobre" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/calendar" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendário</Link>
                <Link to="/credentials" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
                <Link to="/media" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Mídia</Link>
              </>
            ) : (
              <>
                <Link to="/sobre" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/login" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
                <Link to="/register" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Cadastrar</Link>
              </>
            )}
            <button
              type="button"
              onClick={toggleTheme}
              className="text-left text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm"
              title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
              aria-label="Alternar tema"
            >
              {theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
            </button>
          </div>
        </div>
      )}
    </nav>
  )
}
