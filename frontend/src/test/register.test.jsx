import { beforeEach, describe, expect, it, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from './test-utils'
import Register from '../pages/Register'

const mockRegister = vi.fn()
const mockLogin = vi.fn()
const mockGetSession = vi.fn()
const mockLogoutSession = vi.fn()

vi.mock('../api/client', async () => {
  const actual = await vi.importActual('../api/client')
  return {
    ...actual,
    register: (...args) => mockRegister(...args),
    login: (...args) => mockLogin(...args),
    getSession: (...args) => mockGetSession(...args),
    logoutSession: (...args) => mockLogoutSession(...args),
  }
})

describe('Register', () => {
  beforeEach(() => {
    mockRegister.mockReset()
    mockLogin.mockReset()
    mockGetSession.mockReset()
    mockLogoutSession.mockReset()
    mockGetSession.mockRejectedValue(new Error('sem sessao'))
  })

  it('renderiza formulario de cadastro', () => {
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /entrar/i })).toHaveAttribute('href', '/login')
  })

  it('chama register e depois login ao enviar com sucesso', async () => {
    mockRegister.mockResolvedValueOnce({})
    mockLogin.mockResolvedValueOnce({ access_token: 'fake-token' })
    mockGetSession.mockResolvedValue({ authenticated: true, user: { id: 1, email: 'new@test.com' } })
    const user = userEvent.setup()
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    await user.type(screen.getByLabelText(/email/i), 'new@test.com')
    await user.type(screen.getByLabelText(/senha/i), 'senha123')
    await user.click(screen.getByRole('button', { name: /cadastrar/i }))
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('new@test.com', 'senha123')
    })
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('new@test.com', 'senha123')
    })
  })

  it('exibe erro quando registro falha', async () => {
    mockRegister.mockRejectedValueOnce(new Error('Email ja cadastrado'))
    const user = userEvent.setup()
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    await user.type(screen.getByLabelText(/email/i), 'dup@test.com')
    await user.type(screen.getByLabelText(/senha/i), 'senha123')
    await user.click(screen.getByRole('button', { name: /cadastrar/i }))
    await waitFor(() => {
      const errors = screen.getAllByText(/email ja cadastrado|erro ao cadastrar/i)
      expect(errors.length).toBeGreaterThanOrEqual(1)
    })
  })
})
