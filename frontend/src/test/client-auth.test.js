import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AUTH_EXPIRED_EVENT, getSummary } from '../api/client'

describe('api client auth handling', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem('token', 'expired-token')
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      headers: {
        get: () => 'application/json',
      },
      json: async () => ({ detail: 'Token invalido ou expirado' }),
      text: async () => '',
    })
  })

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('limpa o token salvo e dispara evento quando a API retorna 401', async () => {
    const handler = vi.fn()
    window.addEventListener(AUTH_EXPIRED_EVENT, handler)

    await expect(getSummary()).rejects.toThrow(/token invalido ou expirado/i)

    expect(localStorage.getItem('token')).toBeNull()
    expect(handler).toHaveBeenCalledTimes(1)

    window.removeEventListener(AUTH_EXPIRED_EVENT, handler)
  })
})

