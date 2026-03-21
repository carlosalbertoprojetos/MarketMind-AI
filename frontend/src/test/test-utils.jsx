import React from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { ToastProvider } from '../context/ToastContext'
import { ThemeProvider } from '../context/ThemeContext'

/**
 * Renderiza componente com ThemeProvider, AuthProvider, ToastProvider e MemoryRouter.
 * @param {React.ReactElement} ui
 * @param {{ initialEntries?: string[], initialIndex?: number }} options
 */
export function renderWithProviders(ui, { initialEntries = ['/'], initialIndex = 0 } = {}) {
  function Wrapper({ children }) {
    return (
      <ThemeProvider>
        <AuthProvider>
          <ToastProvider>
            <MemoryRouter initialEntries={initialEntries} initialIndex={initialIndex}>
              {children}
            </MemoryRouter>
          </ToastProvider>
        </AuthProvider>
      </ThemeProvider>
    )
  }
  return render(ui, { wrapper: Wrapper })
}

/**
 * Define token no localStorage e renderiza (para simular usuário logado).
 */
export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('token', token)
  } else {
    localStorage.removeItem('token')
  }
}

export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
