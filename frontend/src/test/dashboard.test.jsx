import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, setAuthToken } from './test-utils'
import Dashboard from '../pages/Dashboard'

const mockGetCampaigns = vi.fn()
const mockGetSummary = vi.fn()

vi.mock('../api/client', () => ({
  getCampaigns: (...args) => mockGetCampaigns(...args),
  getSummary: (...args) => mockGetSummary(...args),
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
}))

describe('Dashboard', () => {
  beforeEach(() => {
    localStorage.clear()
    mockGetCampaigns.mockReset()
    mockGetSummary.mockReset()
    mockGetCampaigns.mockResolvedValue({ items: [], total: 0, limit: 12, offset: 0 })
    mockGetSummary.mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 })
  })

  it('exibe Dashboard e chama getCampaigns e getSummary', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => {
      expect(mockGetCampaigns).toHaveBeenCalled()
      expect(mockGetSummary).toHaveBeenCalled()
    })
    expect(screen.getByText(/minhas campanhas/i)).toBeInTheDocument()
    const novaCampanhaLinks = screen.getAllByRole('link', { name: /nova campanha/i })
    expect(novaCampanhaLinks.length).toBeGreaterThanOrEqual(1)
  })

  it('exibe filtros e seletor de itens por página', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())
    expect(screen.getByPlaceholderText(/buscar por título/i)).toBeInTheDocument()
    expect(screen.getByText(/itens por página/i)).toBeInTheDocument()
  })

  it('exibe mensagem quando não há campanhas', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())
    expect(screen.getByText(/nenhuma campanha ainda/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /criar primeira campanha/i })).toBeInTheDocument()
  })
})
