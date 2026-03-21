import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { getSession, logoutSession } from '../api/client'

const AuthContext = createContext(null)
const AUTH_EXPIRED_EVENT = 'marketingai:auth-expired'
const TEST_SESSION_KEY = '__MARKETINGAI_TEST_SESSION__'

function readTestSession() {
  if (typeof window === 'undefined' || import.meta.env.MODE !== 'test') return null
  return window[TEST_SESSION_KEY] || null
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const clearAuth = useCallback(() => {
    if (typeof window !== 'undefined' && import.meta.env.MODE === 'test') {
      delete window[TEST_SESSION_KEY]
    }
    setIsAuthenticated(false)
    setUser(null)
    setIsLoading(false)
  }, [])

  const refreshSession = useCallback(async () => {
    const testSession = readTestSession()
    if (testSession) {
      setIsAuthenticated(true)
      setUser(testSession.user ?? null)
      setIsLoading(false)
      return true
    }

    try {
      const session = await getSession()
      setIsAuthenticated(Boolean(session?.authenticated))
      setUser(session?.user ?? null)
      setIsLoading(false)
      return Boolean(session?.authenticated)
    } catch {
      clearAuth()
      return false
    }
  }, [clearAuth])

  const setToken = useCallback((newToken) => {
    if (newToken) {
      setIsAuthenticated(true)
      setIsLoading(false)
      return
    }
    clearAuth()
  }, [clearAuth])

  const logout = useCallback(async () => {
    try {
      await logoutSession()
    } catch {
      // sessao local ainda precisa ser encerrada
    }
    clearAuth()
  }, [clearAuth])

  useEffect(() => {
    let active = true

    refreshSession().catch(() => {
      if (active) clearAuth()
    })

    const handleAuthExpired = () => {
      if (!active) return
      clearAuth()
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    return () => {
      active = false
      window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    }
  }, [clearAuth, refreshSession])

  const value = useMemo(() => ({
    token: isAuthenticated ? 'session' : null,
    setToken,
    logout,
    isAuthenticated,
    user,
    setUser,
    clearAuth,
    refreshSession,
    isLoading,
  }), [clearAuth, isAuthenticated, isLoading, logout, refreshSession, setToken, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
