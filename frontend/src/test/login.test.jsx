import { beforeEach, describe, expect, it, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from './test-utils'
import Login from '../pages/Login'

const mockLogin = vi.fn()
const mockGetSession = vi.fn()
const mockLogoutSession = vi.fn()

vi.mock('../api/client', async () => {
  const actual = await vi.importActual('../api/client')
  return {
    ...actual,
    login: (...args) => mockLogin(...args),
    getSession: (...args) => mockGetSession(...args),
    logoutSession: (...args) => mockLogoutSession(...args),
  }
})

describe('Login', () => {
  beforeEach(() => {
    mockLogin.mockReset()
    mockGetSession.mockReset()
    mockLogoutSession.mockReset()
    mockGetSession.mockRejectedValue(new Error('sem sessao'))
  })

  it('renderiza formulario de login', () => {
    renderWithProviders(<Login />, { initialEntries: ['/login'] })
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /cadastre-se/i })).toHaveAttribute('href', '/register')
  })

  it('exibe erro quando login falha', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Email ou senha incorretos'))
    const user = userEvent.setup()
    renderWithProviders(<Login />, { initialEntries: ['/login'] })
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/senha/i), 'senha123')
    await user.click(screen.getByRole('button', { name: /entrar/i }))
    await waitFor(() => {
      const errors = screen.getAllByText(/email ou senha incorretos|erro ao entrar/i)
      expect(errors.length).toBeGreaterThanOrEqual(1)
    })
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'senha123')
  })

  it('chama login com email e senha ao enviar', async () => {
    mockLogin.mockResolvedValueOnce({ access_token: 'fake-token' })
    mockGetSession.mockResolvedValue({ authenticated: true, user: { id: 1, email: 'user@test.com' } })
    const user = userEvent.setup()
    renderWithProviders(<Login />, { initialEntries: ['/login'] })
    await user.type(screen.getByLabelText(/email/i), 'user@test.com')
    await user.type(screen.getByLabelText(/senha/i), 'secret')
    await user.click(screen.getByRole('button', { name: /entrar/i }))
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'secret')
    })
  })
})
