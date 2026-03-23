import { Suspense, lazy, useEffect } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ToastProvider, useToast } from './context/ToastContext'

const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const CreateCampaign = lazy(() => import('./pages/CreateCampaign'))
const CampaignDetail = lazy(() => import('./pages/CampaignDetail'))
const CalendarPage = lazy(() => import('./pages/CalendarPage'))
const CredentialsPage = lazy(() => import('./pages/CredentialsPage'))
const AboutPage = lazy(() => import('./pages/AboutPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const CampaignPreviewPage = lazy(() => import('./pages/CampaignPreviewPage'))
const MediaLibraryPage = lazy(() => import('./pages/MediaLibraryPage'))
const FinalContentPage = lazy(() => import('./pages/FinalContentPage'))

const AUTH_EXPIRED_EVENT = 'marketingai:auth-expired'

function PageFallback() {
  return <div className="p-6 text-sm text-gray-500 dark:text-gray-300">Carregando...</div>
}

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) {
    return <div className="p-6 text-sm text-gray-500 dark:text-gray-300">Carregando sessao...</div>
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function AuthSessionWatcher() {
  const { isAuthenticated, clearAuth } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const handleAuthExpired = (event) => {
      const message = event?.detail?.message || 'Sessao expirada. Faca login novamente.'
      if (isAuthenticated) clearAuth()
      addToast(message, 'error')
      if (location.pathname !== '/login') {
        navigate('/login', { replace: true })
      }
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
  }, [addToast, clearAuth, isAuthenticated, location.pathname, navigate])

  return null
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AuthSessionWatcher />
        <Suspense fallback={<PageFallback />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/sobre" element={<AboutPage />} />
            <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/campaign/new" element={<PrivateRoute><CreateCampaign /></PrivateRoute>} />
            <Route path="/campaign/:id" element={<PrivateRoute><CampaignDetail /></PrivateRoute>} />
            <Route path="/campaign/:id/preview" element={<PrivateRoute><CampaignPreviewPage /></PrivateRoute>} />
            <Route path="/calendar" element={<PrivateRoute><CalendarPage /></PrivateRoute>} />
            <Route path="/credentials" element={<PrivateRoute><CredentialsPage /></PrivateRoute>} />
            <Route path="/media" element={<PrivateRoute><MediaLibraryPage /></PrivateRoute>} />
            <Route path="/final-content" element={<PrivateRoute><FinalContentPage /></PrivateRoute>} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </ToastProvider>
    </AuthProvider>
  )
}
