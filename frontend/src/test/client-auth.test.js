import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AUTH_EXPIRED_EVENT, getSummary } from '../api/client'

describe('api client auth handling', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
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
  })

  it('dispara evento quando a API retorna 401', async () => {
    const handler = vi.fn()
    window.addEventListener(AUTH_EXPIRED_EVENT, handler)

    await expect(getSummary()).rejects.toThrow(/token invalido ou expirado/i)

    expect(handler).toHaveBeenCalledTimes(1)
    expect(global.fetch).toHaveBeenCalledWith('/api/user/summary', expect.objectContaining({ credentials: 'include' }))

    window.removeEventListener(AUTH_EXPIRED_EVENT, handler)
  })
})
