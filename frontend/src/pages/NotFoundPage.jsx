import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'

export default function NotFoundPage() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-lg mx-auto px-6 py-16 text-center">
        <p className="text-6xl font-bold text-gray-200 dark:text-gray-700 select-none">404</p>
        <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">Página não encontrada</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          A URL que você acessou não existe ou foi movida.
        </p>
        <div className="mt-8">
          {isAuthenticated ? (
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-lg bg-primary-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-600"
            >
              Ir para o Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-600"
            >
              Ir para o Login
            </Link>
          )}
        </div>
      </main>
    </div>
  )
}
