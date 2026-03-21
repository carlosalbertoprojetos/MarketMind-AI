import React from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { ToastProvider } from '../context/ToastContext'
import { ThemeProvider } from '../context/ThemeContext'

const TEST_SESSION_KEY = '__MARKETINGAI_TEST_SESSION__'

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

export function setAuthToken(token, user = { id: 1, email: 'teste@exemplo.com' }) {
  if (token) {
    window[TEST_SESSION_KEY] = { token, user }
    return
  }
  delete window[TEST_SESSION_KEY]
}

export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
