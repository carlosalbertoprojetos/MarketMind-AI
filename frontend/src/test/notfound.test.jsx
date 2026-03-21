import { describe, it, expect, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { Routes, Route } from 'react-router-dom'
import { renderWithProviders, setAuthToken } from './test-utils'
import NotFoundPage from '../pages/NotFoundPage'

describe('NotFoundPage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('exibe 404 e link para Login quando não logado', () => {
    renderWithProviders(
      <Routes>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>,
      { initialEntries: ['/qualquer-rota-errada'] }
    )
    expect(screen.getByText(/404/)).toBeInTheDocument()
    expect(screen.getByText(/página não encontrada/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /ir para o login/i })).toBeInTheDocument()
  })

  it('exibe link para Dashboard quando logado', () => {
    setAuthToken('fake-token')
    renderWithProviders(
      <Routes>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>,
      { initialEntries: ['/rota-inexistente'] }
    )
    expect(screen.getByText(/404/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /ir para o dashboard/i })).toBeInTheDocument()
  })
})
