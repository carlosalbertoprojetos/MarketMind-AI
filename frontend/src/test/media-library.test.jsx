import { describe, it, expect, beforeEach, vi } from 'vitest'
import { waitFor, screen, renderWithProviders, userEvent } from './test-utils'
import MediaLibraryPage from '../pages/MediaLibraryPage'

const mockGetCampaigns = vi.fn()
const mockGetCampaignAssets = vi.fn()
const mockGetCampaignGenerations = vi.fn()
const mockExportSelectedCampaignAssetsZip = vi.fn()
const mockDeleteSelectedCampaignAssets = vi.fn()

vi.mock('../api/client', () => ({
  BASE: 'http://localhost:8003/api',
  getCampaigns: (...args) => mockGetCampaigns(...args),
  getCampaignAssets: (...args) => mockGetCampaignAssets(...args),
  getCampaignGenerations: (...args) => mockGetCampaignGenerations(...args),
  exportSelectedCampaignAssetsZip: (...args) => mockExportSelectedCampaignAssetsZip(...args),
  deleteSelectedCampaignAssets: (...args) => mockDeleteSelectedCampaignAssets(...args),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getSavedFinalContentRuns: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 4, offset: 0 }),
  stopLocalSystem: vi.fn(),
  getCampaign: vi.fn(),
  updateCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
  createCampaign: vi.fn(),
  getCredentials: vi.fn(),
  createCredentials: vi.fn(),
  deleteCredentials: vi.fn(),
  previewFromUrl: vi.fn(),
  exportCampaignZip: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
  getSession: vi.fn(),
  logoutSession: vi.fn(),
}))

describe('MediaLibraryPage', () => {
  beforeEach(() => {
    mockGetCampaigns.mockReset()
    mockGetCampaignAssets.mockReset()
    mockGetCampaignGenerations.mockReset()
    mockExportSelectedCampaignAssetsZip.mockReset()
    mockDeleteSelectedCampaignAssets.mockReset()
    mockGetCampaigns.mockResolvedValue({
      items: [
        { id: 1, title: 'Campanha A', platform: 'instagram', platforms: ['instagram', 'linkedin'] },
        { id: 2, title: 'Campanha B', platform: 'tiktok', platforms: ['tiktok'] },
      ],
      total: 2,
      limit: 100,
      offset: 0,
    })
    mockGetCampaignAssets.mockResolvedValue({ assets: [], source_url: 'https://example.com' })
    mockGetCampaignGenerations.mockResolvedValue({ generations: [{ generated_at: '2026-03-22T10:00:00Z', source_url: 'https://example.com', post_count: 2, asset_count: 3, platforms: ['instagram', 'linkedin'] }] })
  })

  it('filtra campanhas da biblioteca por multiplas redes e exibe redes no historico', async () => {
    renderWithProviders(<MediaLibraryPage />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalledWith(100, 0, { platforms: [] }))
    await waitFor(() => expect(mockGetCampaignAssets).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: /^instagram$/i }))
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenLastCalledWith(100, 0, { platforms: ['instagram'] }))

    await userEvent.click(screen.getByRole('button', { name: /^linkedin$/i }))
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenLastCalledWith(100, 0, { platforms: ['instagram', 'linkedin'] }))

    expect(screen.getByText(/redes:/i)).toBeInTheDocument()
    expect(screen.getAllByText(/instagram, linkedin/i).length).toBeGreaterThan(0)
  })
})
