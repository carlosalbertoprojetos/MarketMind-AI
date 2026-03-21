import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from './test-utils'
import Register from '../pages/Register'

const mockRegister = vi.fn()
const mockLogin = vi.fn()

vi.mock('../api/client', () => ({
  register: (...args) => mockRegister(...args),
  login: (...args) => mockLogin(...args),
}))

describe('Register', () => {
  beforeEach(() => {
    localStorage.clear()
    mockRegister.mockReset()
    mockLogin.mockReset()
  })

  it('renderiza formulário de cadastro', () => {
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /entrar/i })).toHaveAttribute('href', '/login')
  })

  it('chama register e depois login ao enviar com sucesso', async () => {
    mockRegister.mockResolvedValueOnce({})
    mockLogin.mockResolvedValueOnce({ access_token: 'fake-token' })
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
    mockRegister.mockRejectedValueOnce(new Error('Email já cadastrado'))
    const user = userEvent.setup()
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    await user.type(screen.getByLabelText(/email/i), 'dup@test.com')
    await user.type(screen.getByLabelText(/senha/i), 'senha123')
    await user.click(screen.getByRole('button', { name: /cadastrar/i }))
    await waitFor(() => {
      const errors = screen.getAllByText(/email já cadastrado|erro ao cadastrar/i)
      expect(errors.length).toBeGreaterThanOrEqual(1)
    })
  })
})
