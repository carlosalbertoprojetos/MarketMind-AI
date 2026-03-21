import { beforeEach, describe, expect, it, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders } from './test-utils'
import { useAuth } from '../context/AuthContext'
import { AUTH_EXPIRED_EVENT } from '../api/client'

const mockGetSession = vi.fn()
const mockLogoutSession = vi.fn()

vi.mock('../api/client', async () => {
  const actual = await vi.importActual('../api/client')
  return {
    ...actual,
    getSession: (...args) => mockGetSession(...args),
    logoutSession: (...args) => mockLogoutSession(...args),
  }
})

function AuthProbe() {
  const { isAuthenticated, token, isLoading } = useAuth()
  if (isLoading) return <div>carregando</div>
  return <div>{isAuthenticated ? `logado:${token}` : 'deslogado'}</div>
}

describe('AuthContext', () => {
  beforeEach(() => {
    mockGetSession.mockReset()
    mockLogoutSession.mockReset()
  })

  it('remove autenticacao quando recebe evento de sessao expirada', async () => {
    mockGetSession.mockResolvedValueOnce({ authenticated: true, user: { id: 1, email: 'teste@exemplo.com' } })
    renderWithProviders(<AuthProbe />)

    await waitFor(() => {
      expect(screen.getByText(/logado:session/i)).toBeInTheDocument()
    })

    window.dispatchEvent(
      new CustomEvent(AUTH_EXPIRED_EVENT, {
        detail: { message: 'Sessao expirada. Faca login novamente.' },
      }),
    )

    await waitFor(() => {
      expect(screen.getByText(/deslogado/i)).toBeInTheDocument()
    })
  })
})
