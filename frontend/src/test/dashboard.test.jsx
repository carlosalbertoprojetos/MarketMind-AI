import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, setAuthToken, userEvent } from './test-utils'
import Dashboard from '../pages/Dashboard'

const mockGetCampaigns = vi.fn()
const mockGetSummary = vi.fn()
const mockGetSavedFinalContentRuns = vi.fn()
const mockStopLocalSystem = vi.fn()

vi.mock('../api/client', () => ({
  getCampaigns: (...args) => mockGetCampaigns(...args),
  getSummary: (...args) => mockGetSummary(...args),
  getSavedFinalContentRuns: (...args) => mockGetSavedFinalContentRuns(...args),
  stopLocalSystem: (...args) => mockStopLocalSystem(...args),
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

describe('Dashboard', () => {
  beforeEach(() => {
    localStorage.clear()
    mockGetCampaigns.mockReset()
    mockGetSummary.mockReset()
    mockGetSavedFinalContentRuns.mockReset()
    mockStopLocalSystem.mockReset()
    mockGetCampaigns.mockResolvedValue({ items: [], total: 0, limit: 12, offset: 0 })
    mockGetSummary.mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 })
    mockGetSavedFinalContentRuns.mockResolvedValue({ items: [], total: 0, limit: 4, offset: 0 })
    mockStopLocalSystem.mockResolvedValue({ status: 'stopping' })
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

  it('exibe filtros e seletor de itens por pagina', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())
    expect(screen.getByPlaceholderText(/buscar por titulo/i)).toBeInTheDocument()
    expect(screen.getByText(/itens por pagina/i)).toBeInTheDocument()
    expect(screen.getByText(/filtrar por redes/i)).toBeInTheDocument()
  })

  it('filtra campanhas por multiplas redes sociais', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalledTimes(1))

    await userEvent.click(screen.getByRole('button', { name: /^instagram$/i }))
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenLastCalledWith(12, 0, expect.objectContaining({ platforms: ['instagram'] })))

    await userEvent.click(screen.getByRole('button', { name: /^linkedin$/i }))
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenLastCalledWith(12, 0, expect.objectContaining({ platforms: ['instagram', 'linkedin'] })))
  })

  it('exibe mensagem quando nao ha campanhas', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())
    expect(screen.getByText(/nenhuma campanha ainda/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /criar primeira campanha/i })).toBeInTheDocument()
  })

  it('exibe atalhos para conteudos salvos no dashboard', async () => {
    setAuthToken('fake-token')
    mockGetSavedFinalContentRuns.mockResolvedValue({
      items: [{ id: 7, title: 'Tema salvo', created_at: '2026-03-21T18:00:00Z', platforms: ['instagram', 'linkedin'], post_count: 2 }],
      total: 1,
      limit: 4,
      offset: 0,
    })
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(screen.getByText(/tema salvo/i)).toBeInTheDocument())
    expect(screen.getByRole('link', { name: /tema salvo/i })).toHaveAttribute('href', '/final-content?saved=7')
    expect(screen.getByText(/total salvo: 1/i)).toBeInTheDocument()
  })

  it('aciona a parada local pelo botao de energia no dashboard', async () => {
    setAuthToken('fake-token')
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderWithProviders(<Dashboard />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())
    await userEvent.click(screen.getByRole('button', { name: /encerrar sistema local/i }))
    await waitFor(() => expect(mockStopLocalSystem).toHaveBeenCalled())
  })
})
