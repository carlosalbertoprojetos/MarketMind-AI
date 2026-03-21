import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
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
              <Link to="/calendar" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendario</Link>
              <Link to="/credentials" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
              <Link to="/media" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Midia</Link>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-4">
              <Link to="/sobre" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
              <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
              <Link to="/register" className="bg-primary-500 text-white px-3 py-1.5 rounded hover:bg-primary-600">Cadastrar</Link>
            </div>
          )}
          <button
            type="button"
            onClick={toggleTheme}
            className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm"
            title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
            aria-label="Alternar tema"
          >
            {theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
          </button>
          {isAuthenticated && (
            <button
              type="button"
              onClick={handleLogout}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              aria-label="Sair"
              title="Sair"
            >
              Sair
            </button>
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
                <Link to="/" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Dashboard</Link>
                <Link to="/sobre" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/calendar" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Calendario</Link>
                <Link to="/credentials" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Credenciais</Link>
                <Link to="/media" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Midia</Link>
                <button type="button" onClick={handleLogout} className="text-left text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sair</button>
              </>
            ) : (
              <>
                <Link to="/sobre" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Sobre</Link>
                <Link to="/login" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Entrar</Link>
                <Link to="/register" onClick={closeMobileMenu} className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Cadastrar</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
