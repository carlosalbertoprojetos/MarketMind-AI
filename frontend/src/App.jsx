import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ToastProvider, useToast } from './context/ToastContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CreateCampaign from './pages/CreateCampaign'
import CampaignDetail from './pages/CampaignDetail'
import CalendarPage from './pages/CalendarPage'
import CredentialsPage from './pages/CredentialsPage'
import AboutPage from './pages/AboutPage'
import NotFoundPage from './pages/NotFoundPage'
import CampaignPreviewPage from './pages/CampaignPreviewPage'
import MediaLibraryPage from './pages/MediaLibraryPage'

const AUTH_EXPIRED_EVENT = 'marketingai:auth-expired'

/** Rotas protegidas: redireciona para /login se nao autenticado. */
function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function AuthSessionWatcher() {
  const { isAuthenticated, logout } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const handleAuthExpired = (event) => {
      const message = event?.detail?.message || 'Sessao expirada. Faca login novamente.'
      if (isAuthenticated) logout()
      addToast(message, 'error')
      if (location.pathname !== '/login') {
        navigate('/login', { replace: true })
      }
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
  }, [addToast, isAuthenticated, location.pathname, logout, navigate])

  return null
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AuthSessionWatcher />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/sobre" element={<AboutPage />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/campaign/new"
            element={
              <PrivateRoute>
                <CreateCampaign />
              </PrivateRoute>
            }
          />
          <Route
            path="/campaign/:id"
            element={
              <PrivateRoute>
                <CampaignDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/campaign/:id/preview"
            element={
              <PrivateRoute>
                <CampaignPreviewPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/calendar"
            element={
              <PrivateRoute>
                <CalendarPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/credentials"
            element={
              <PrivateRoute>
                <CredentialsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/media"
            element={
              <PrivateRoute>
                <MediaLibraryPage />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  )
}

