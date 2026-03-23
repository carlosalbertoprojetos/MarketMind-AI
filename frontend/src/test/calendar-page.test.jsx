import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, renderWithProviders, userEvent, setAuthToken } from './test-utils'

const mockGetCampaigns = vi.fn()
const mockUpdateCampaign = vi.fn()
const mockNavigate = vi.fn()

vi.mock('../api/client', () => ({
  getCampaigns: (...args) => mockGetCampaigns(...args),
  updateCampaign: (...args) => mockUpdateCampaign(...args),
  stopLocalSystem: vi.fn(),
  getSummary: vi.fn().mockResolvedValue({ total_campaigns: 0, by_platform: {}, upcoming_count: 0 }),
  getCampaign: vi.fn(),
  createCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
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

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('react-big-calendar', () => ({
  Calendar: ({ events = [], onSelectEvent }) => (
    <div>
      {events.map((event) => (
        <button key={event.id} type="button" onClick={() => onSelectEvent?.(event)}>
          {event.title}
        </button>
      ))}
    </div>
  ),
  dateFnsLocalizer: () => ({}),
}))

vi.mock('react-big-calendar/lib/addons/dragAndDrop', () => ({
  default: (Component) => Component,
}))

import CalendarPage from '../pages/CalendarPage'

describe('CalendarPage', () => {
  beforeEach(() => {
    localStorage.clear()
    setAuthToken('fake-token')
    mockNavigate.mockReset()
    mockGetCampaigns.mockReset()
    mockUpdateCampaign.mockReset()
    mockGetCampaigns.mockResolvedValue({
      items: [
        {
          id: 7,
          title: 'vale',
          platform: 'instagram',
          platforms: ['instagram', 'linkedin'],
          schedule: '2026-03-21T12:00:00.000Z',
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
    })
  })

  it('abre os posts gerados da campanha ao clicar em um evento com multiplas redes', async () => {
    renderWithProviders(<CalendarPage />)
    await waitFor(() => expect(mockGetCampaigns).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: /Instagram, LinkedIn - vale/i }))

    expect(mockNavigate).toHaveBeenCalledWith('/campaign/7/preview')
  })
})
