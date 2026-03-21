import { describe, it, expect, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders } from './test-utils'
import Login from '../pages/Login'
import Register from '../pages/Register'
import NotFoundPage from '../pages/NotFoundPage'
import { AuthProvider } from '../context/AuthContext'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

// Testes de rotas sem carregar App inteiro (evita importar Calendar e outras libs pesadas)
describe('Rotas e páginas públicas', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('Login: mostra formulário ao acessar', () => {
    renderWithProviders(<Login />, { initialEntries: ['/login'] })
    expect(screen.getByRole('heading', { name: /MarketingAI/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
  })

  it('Register: mostra formulário ao acessar', () => {
    renderWithProviders(<Register />, { initialEntries: ['/register'] })
    expect(screen.getByRole('heading', { name: /MarketingAI/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument()
  })

  it('NotFoundPage: exibe 404 e link para Login quando não logado', () => {
    renderWithProviders(
      <Routes>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>,
      { initialEntries: ['/rota-inexistente'] }
    )
    expect(screen.getByText(/404/)).toBeInTheDocument()
    expect(screen.getByText(/página não encontrada/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /ir para o login/i })).toBeInTheDocument()
  })
})
