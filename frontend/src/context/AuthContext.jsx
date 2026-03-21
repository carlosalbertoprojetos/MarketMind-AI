import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)
const AUTH_EXPIRED_EVENT = 'marketingai:auth-expired'

function readStoredToken() {
  try {
    return localStorage.getItem('token')
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(readStoredToken)
  const [user, setUser] = useState(null)

  const setToken = useCallback((newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken)
      setTokenState(newToken)
      return
    }

    localStorage.removeItem('token')
    setTokenState(null)
    setUser(null)
  }, [])

  const logout = useCallback(() => setToken(null), [setToken])

  useEffect(() => {
    const handleAuthExpired = () => {
      setToken(null)
    }

    const handleStorage = (event) => {
      if (event.key !== 'token') return
      setTokenState(event.newValue)
      if (!event.newValue) setUser(null)
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
    window.addEventListener('storage', handleStorage)

    return () => {
      window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
      window.removeEventListener('storage', handleStorage)
    }
  }, [setToken])

  const isAuthenticated = !!token

  const value = {
    token,
    setToken,
    logout,
    isAuthenticated,
    user,
    setUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

