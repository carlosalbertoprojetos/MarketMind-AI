import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, setAuthToken } from './test-utils'
import { useAuth } from '../context/AuthContext'
import { AUTH_EXPIRED_EVENT } from '../api/client'

function AuthProbe() {
  const { isAuthenticated, token } = useAuth()
  return <div>{isAuthenticated ? `logado:${token}` : 'deslogado'}</div>
}

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('remove autenticacao quando recebe evento de sessao expirada', async () => {
    setAuthToken('token-antigo')
    renderWithProviders(<AuthProbe />)

    expect(screen.getByText(/logado:token-antigo/i)).toBeInTheDocument()

    window.dispatchEvent(
      new CustomEvent(AUTH_EXPIRED_EVENT, {
        detail: { message: 'Sessao expirada. Faca login novamente.' },
      }),
    )

    await waitFor(() => {
      expect(screen.getByText(/deslogado/i)).toBeInTheDocument()
    })
    expect(localStorage.getItem('token')).toBeNull()
  })
})

