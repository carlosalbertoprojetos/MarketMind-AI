import { beforeEach, describe, expect, it, vi } from 'vitest'
import { Route, Routes } from 'react-router-dom'
import { renderWithProviders, screen, waitFor, setAuthToken } from './test-utils'

const mockGetSavedCampaignPreview = vi.fn()
const mockGenerateCampaignFromSavedUrl = vi.fn()
const mockAddToast = vi.fn()

vi.mock('../api/client', () => ({
  getSavedCampaignPreview: (...args) => mockGetSavedCampaignPreview(...args),
  generateCampaignFromSavedUrl: (...args) => mockGenerateCampaignFromSavedUrl(...args),
  stopLocalSystem: vi.fn(),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getSession: vi.fn(),
  logoutSession: vi.fn(),
}))

vi.mock('../components/PostPreviewCard', () => ({
  default: ({ post }) => <div>{post.title}</div>,
}))

vi.mock('../context/ToastContext', async () => {
  const actual = await vi.importActual('../context/ToastContext')
  return {
    ...actual,
    useToast: () => ({ addToast: mockAddToast }),
  }
})

import CampaignPreviewPage from '../pages/CampaignPreviewPage'

describe('CampaignPreviewPage', () => {
  beforeEach(() => {
    setAuthToken('fake-token')
    mockAddToast.mockReset()
    mockGetSavedCampaignPreview.mockReset()
    mockGenerateCampaignFromSavedUrl.mockReset()
  })

  it('gera automaticamente quando ainda nao existe preview salvo', async () => {
    mockGetSavedCampaignPreview.mockRejectedValue(new Error('Nenhum post salvo para esta campanha'))
    mockGenerateCampaignFromSavedUrl.mockResolvedValue({
      url: 'https://exemplo.com',
      saved_content_id: 12,
      saved_at: '2026-03-22T12:00:00Z',
      posts: [{ platform: 'instagram', title: 'Post gerado' }],
    })

    renderWithProviders(
      <Routes>
        <Route path="/campaign/:id/preview" element={<CampaignPreviewPage />} />
      </Routes>,
      { initialEntries: ['/campaign/1/preview'] },
    )

    await waitFor(() => expect(mockGenerateCampaignFromSavedUrl).toHaveBeenCalledWith('1'))
    expect(await screen.findByText('Post gerado')).toBeInTheDocument()
    expect(mockAddToast).toHaveBeenCalledWith('Nao havia posts salvos. Geramos e salvamos agora.')
  })
})
