import { describe, it, expect, beforeEach, vi } from 'vitest'
import { waitFor, screen, renderWithProviders, userEvent, setAuthToken } from './test-utils'
import CreateCampaign from '../pages/CreateCampaign'

const mockPreviewFromUrl = vi.fn()
const mockExportCampaignZip = vi.fn()
const mockGetCredentials = vi.fn()
const mockCreateCredentials = vi.fn()
const mockDeleteCredentials = vi.fn()
const mockCreateCampaign = vi.fn()
const mockUpdateCampaign = vi.fn()

vi.mock('../api/client', () => ({
  createCampaign: (...args) => mockCreateCampaign(...args),
  updateCampaign: (...args) => mockUpdateCampaign(...args),
  previewFromUrl: (...args) => mockPreviewFromUrl(...args),
  getCredentials: (...args) => mockGetCredentials(...args),
  createCredentials: (...args) => mockCreateCredentials(...args),
  deleteCredentials: (...args) => mockDeleteCredentials(...args),
  exportCampaignZip: (...args) => mockExportCampaignZip(...args),
  getCampaigns: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 12, offset: 0 }),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
  getSession: vi.fn(),
  logoutSession: vi.fn(),
}))

describe('CreateCampaign', () => {
  beforeEach(() => {
    localStorage.clear()
    setAuthToken('fake-token')
    mockPreviewFromUrl.mockReset()
    mockExportCampaignZip.mockReset()
    mockGetCredentials.mockReset()
    mockCreateCredentials.mockReset()
    mockDeleteCredentials.mockReset()
    mockCreateCampaign.mockReset()
    mockUpdateCampaign.mockReset()
    mockGetCredentials.mockResolvedValue([])
    mockPreviewFromUrl.mockResolvedValue({ posts: [] })
    mockExportCampaignZip.mockResolvedValue(undefined)
    mockCreateCredentials.mockResolvedValue({ id: 1, site_name: 'Portal', login_url: 'https://portal.com/login' })
  })

  it('envia preview respeitando a plataforma selecionada', async () => {
    renderWithProviders(<CreateCampaign />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())

    await userEvent.type(screen.getByLabelText(/url do site\/produto/i), 'https://example.com')
    await userEvent.selectOptions(screen.getByLabelText(/plataforma/i), 'tiktok')
    await userEvent.click(screen.getByText(/visualizar posts/i))

    await waitFor(() => expect(mockPreviewFromUrl).toHaveBeenCalled())
    expect(mockPreviewFromUrl).toHaveBeenCalledWith(
      'https://example.com',
      'https://example.com',
      ['tiktok'],
      expect.objectContaining({ targetPlatform: 'tiktok' }),
    )
  })

  it('salva credencial sem depender de form aninhado', async () => {
    renderWithProviders(<CreateCampaign />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: /\+ nova/i }))
    await userEvent.type(document.getElementById('new-cred-site'), 'Portal Fechado')
    await userEvent.type(document.getElementById('new-cred-url'), 'https://portal.com/login')
    await userEvent.type(document.getElementById('new-cred-user'), 'carlos')
    await userEvent.type(document.getElementById('new-cred-pass'), 'secret')
    await userEvent.click(screen.getByRole('button', { name: /^salvar$/i }))

    await waitFor(() => expect(mockCreateCredentials).toHaveBeenCalledWith('Portal Fechado', 'https://portal.com/login', 'carlos', 'secret'))
  })
})
