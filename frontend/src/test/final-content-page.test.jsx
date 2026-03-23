import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderWithProviders, screen, userEvent, waitFor, within, setAuthToken } from './test-utils'

const mockGetSavedFinalContentRuns = vi.fn()
const mockGetSavedFinalContentRun = vi.fn()

vi.mock('../api/client', () => ({
  deleteSavedFinalContentRun: vi.fn(),
  exportFinalContentPipeline: vi.fn(),
  getSavedFinalContentRun: (...args) => mockGetSavedFinalContentRun(...args),
  getSavedFinalContentRuns: (...args) => mockGetSavedFinalContentRuns(...args),
  publishFinalContentPipeline: vi.fn(),
  runFinalContentPipeline: vi.fn(),
  stopLocalSystem: vi.fn(),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getCampaigns: vi.fn(),
  getSession: vi.fn(),
  logoutSession: vi.fn(),
}))

import FinalContentPage from '../pages/FinalContentPage'

describe('FinalContentPage', () => {
  beforeEach(() => {
    setAuthToken('fake-token')
    mockGetSavedFinalContentRuns.mockReset()
    mockGetSavedFinalContentRun.mockReset()
    mockGetSavedFinalContentRuns.mockResolvedValue({
      items: [
        { id: 9, title: 'Execucao 9', platforms: ['instagram', 'linkedin'], post_count: 2, created_at: '2026-03-22T10:00:00Z' },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    })
    mockGetSavedFinalContentRun.mockResolvedValue({
      id: 9,
      saved_content_id: 9,
      saved_at: '2026-03-22T10:00:00Z',
      theme: 'Tema',
      objective: 'branding',
      audience: 'Publico',
      platforms: ['instagram', 'linkedin'],
      outputs: [],
      ab_test_suggestions: [],
      publish_results: [],
    })
  })

  it('filtra conteudos salvos por multiplas redes', async () => {
    renderWithProviders(<FinalContentPage />)
    await waitFor(() => expect(mockGetSavedFinalContentRuns).toHaveBeenCalled())

    const savedFilters = screen.getByRole('group', { name: /Filtrar salvos por redes/i })
    await userEvent.click(within(savedFilters).getByRole('button', { name: 'Instagram' }))
    await userEvent.click(within(savedFilters).getByRole('button', { name: 'LinkedIn' }))

    await waitFor(() => {
      expect(mockGetSavedFinalContentRuns).toHaveBeenLastCalledWith(20, expect.objectContaining({
        platforms: ['instagram', 'linkedin'],
      }))
    })

    expect(screen.getAllByText('Instagram').length).toBeGreaterThan(0)
    expect(screen.getAllByText('LinkedIn').length).toBeGreaterThan(0)
  })
})
