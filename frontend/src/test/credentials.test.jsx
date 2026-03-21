import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, setAuthToken } from './test-utils'
import CredentialsPage from '../pages/CredentialsPage'

const mockGetCredentials = vi.fn()
const mockCreateCredentials = vi.fn()
const mockDeleteCredentials = vi.fn()

vi.mock('../api/client', () => ({
  getCredentials: (...args) => mockGetCredentials(...args),
  createCredentials: (...args) => mockCreateCredentials(...args),
  deleteCredentials: (...args) => mockDeleteCredentials(...args),
  getCampaigns: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 12, offset: 0 }),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getCampaign: vi.fn(),
  updateCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
  createCampaign: vi.fn(),
  previewFromUrl: vi.fn(),
  exportCampaignZip: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
}))

describe('CredentialsPage', () => {
  beforeEach(() => {
    localStorage.clear()
    mockGetCredentials.mockReset()
    mockCreateCredentials.mockReset()
    mockDeleteCredentials.mockReset()
    mockGetCredentials.mockResolvedValue([])
  })

  it('exibe página de credenciais e lista vazia', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<CredentialsPage />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())
    expect(screen.getByRole('heading', { name: 'Credenciais', level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/nova credencial/i)).toBeInTheDocument()
    expect(screen.getByText(/nenhuma credencial/i)).toBeInTheDocument()
  })

  it('exibe formulário para nova credencial', async () => {
    setAuthToken('fake-token')
    renderWithProviders(<CredentialsPage />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())
    expect(screen.getByPlaceholderText(/meu portal/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/https/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /salvar credencial/i })).toBeInTheDocument()
  })

  it('lista credenciais quando a API retorna dados', async () => {
    mockGetCredentials.mockResolvedValueOnce([
      { id: 1, site_name: 'Meu Site', login_url: 'https://site.com/login', has_username: true, has_password: true },
    ])
    setAuthToken('fake-token')
    renderWithProviders(<CredentialsPage />)
    await waitFor(() => expect(mockGetCredentials).toHaveBeenCalled())
    expect(screen.getByText('Meu Site')).toBeInTheDocument()
    expect(screen.getByText('https://site.com/login')).toBeInTheDocument()
  })
})
