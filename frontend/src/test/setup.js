import '@testing-library/jest-dom'
import { afterEach, beforeEach, vi } from 'vitest'

const TEST_SESSION_KEY = '__MARKETINGAI_TEST_SESSION__'
const defaultFetch = vi.fn(async () => ({
  ok: false,
  status: 401,
  headers: { get: () => 'application/json' },
  json: async () => ({ detail: 'Sessao indisponivel' }),
  text: async () => '',
}))

beforeEach(() => {
  if (typeof window !== 'undefined') {
    window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener: () => {}, removeListener: () => {} }))
    delete window[TEST_SESSION_KEY]
  }
  if (!global.fetch) {
    global.fetch = defaultFetch
  }
})

afterEach(() => {
  if (typeof window !== 'undefined') {
    delete window[TEST_SESSION_KEY]
  }
  defaultFetch.mockClear()
})
