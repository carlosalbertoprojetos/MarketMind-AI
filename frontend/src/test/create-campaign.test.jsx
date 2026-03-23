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

  it('envia preview usando apenas as URLs explicitamente informadas e as plataformas selecionadas', async () => {
    renderWithProviders(<CreateCampaign />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())

    await userEvent.type(screen.getByLabelText(/url principal/i), 'https://example.com')
    await userEvent.type(screen.getByLabelText(/urls adicionais/i), 'https://example.com/precos\nhttps://example.com/faq')
    await userEvent.selectOptions(screen.getByLabelText(/^rede social$/i), 'instagram')
    await userEvent.click(screen.getByRole('button', { name: /adicionar rede/i }))
    await userEvent.selectOptions(screen.getByLabelText(/^rede social$/i), 'tiktok')
    await userEvent.click(screen.getByRole('button', { name: /adicionar rede/i }))
    await userEvent.click(screen.getByText(/pre-visualizar posts/i))

    await waitFor(() => expect(mockPreviewFromUrl).toHaveBeenCalled())
    expect(mockPreviewFromUrl).toHaveBeenCalledWith(
      'https://example.com',
      'https://example.com',
      ['instagram', 'tiktok'],
      expect.objectContaining({
        sourceUrls: ['https://example.com/precos', 'https://example.com/faq'],
        followInternalLinks: false,
        captureScrollSections: true,
      }),
    )
    expect(mockPreviewFromUrl.mock.calls[0][3].targetPlatform).toBeUndefined()
  })

  it('permite adicionar, editar e remover redes sociais', async () => {
    renderWithProviders(<CreateCampaign />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: /adicionar rede/i }))
    expect(screen.getAllByText('Instagram').length).toBeGreaterThan(0)

    await userEvent.click(screen.getByRole('button', { name: /editar/i }))
    await userEvent.selectOptions(screen.getByLabelText(/^rede social$/i), 'youtube')
    await userEvent.click(screen.getByRole('button', { name: /salvar rede/i }))
    expect(screen.getAllByText('YouTube').length).toBeGreaterThan(0)

    await userEvent.click(screen.getByRole('button', { name: /excluir/i }))
    expect(screen.getByText(/nenhuma rede selecionada/i)).toBeInTheDocument()
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

  it('persiste e restaura URLs adicionais e plataformas na campanha', async () => {
    const editCampaign = {
      id: 9,
      title: 'Campanha existente',
      content: 'URL: https://example.com\n\nADDITIONAL_URLS:\nhttps://example.com/precos\nhttps://example.com/faq\nEND_ADDITIONAL_URLS\n\nPLATFORMS:\ninstagram\nyoutube\nEND_PLATFORMS\n\nNotas internas',
      platform: 'instagram',
      schedule: null,
    }

    renderWithProviders(<CreateCampaign />, {
      initialEntries: [{ pathname: '/campaign/new', state: { editCampaign } }],
    })

    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())
    expect(screen.getByLabelText(/url principal/i)).toHaveValue('https://example.com')
    expect(screen.getByLabelText(/urls adicionais/i)).toHaveValue('https://example.com/precos\nhttps://example.com/faq')
    expect(screen.getAllByText('Instagram').length).toBeGreaterThan(0)
    expect(screen.getAllByText('YouTube').length).toBeGreaterThan(0)
    expect(screen.getByLabelText(/conteudo \/ notas/i)).toHaveValue('Notas internas')
  })

  it('salva URLs adicionais e plataformas no conteudo persistido da campanha', async () => {
    mockCreateCampaign.mockResolvedValue({ id: 11 })

    renderWithProviders(<CreateCampaign />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())

    await userEvent.type(screen.getByLabelText(/url principal/i), 'https://example.com')
    await userEvent.type(screen.getByLabelText(/urls adicionais/i), 'https://example.com/precos\nhttps://example.com/faq')
    await userEvent.type(screen.getByLabelText(/conteudo \/ notas/i), 'Notas internas')
    await userEvent.click(screen.getByRole('button', { name: /adicionar rede/i }))
    await userEvent.selectOptions(screen.getByLabelText(/^rede social$/i), 'linkedin')
    await userEvent.click(screen.getByRole('button', { name: /adicionar rede/i }))
    await userEvent.click(screen.getByRole('button', { name: /^criar campanha$/i }))

    await waitFor(() => expect(mockCreateCampaign).toHaveBeenCalled())
    expect(mockCreateCampaign).toHaveBeenCalledWith(expect.objectContaining({
      platform: 'instagram',
      content: 'URL: https://example.com\n\nADDITIONAL_URLS:\nhttps://example.com/precos\nhttps://example.com/faq\nEND_ADDITIONAL_URLS\n\nPLATFORMS:\ninstagram\nlinkedin\nEND_PLATFORMS\n\nNotas internas',
    }))
  })
})
