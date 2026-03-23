import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import { getCampaigns, updateCampaign } from '../api/client'
import Navbar from '../components/Navbar'

const locales = { 'pt-BR': ptBR }
const DnDCalendar = withDragAndDrop(Calendar)
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
})
const PLATFORM_OPTIONS = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'X' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'youtube', label: 'YouTube' },
]

function getCampaignPlatforms(campaign) {
  if (Array.isArray(campaign?.platforms) && campaign.platforms.length > 0) return campaign.platforms
  return campaign?.platform ? [campaign.platform] : []
}

function getPlatformLabel(platform) {
  return PLATFORM_OPTIONS.find((item) => item.value === platform)?.label || platform || '-'
}

export default function CalendarPage() {
  const navigate = useNavigate()
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPlatforms, setSelectedPlatforms] = useState([])

  const loadCampaigns = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getCampaigns()
      const list = data.items ?? data
      const evts = list
        .filter((c) => c.schedule)
        .filter((c) => !selectedPlatforms.length || getCampaignPlatforms(c).some((item) => selectedPlatforms.includes(item.toLowerCase())))
        .map((c) => {
          const platforms = getCampaignPlatforms(c)
          return {
            id: c.id,
            title: [platforms.map(getPlatformLabel).join(', '), c.title].filter(Boolean).join(' - '),
            start: new Date(c.schedule),
            end: new Date(new Date(c.schedule).getTime() + 60 * 60 * 1000),
            resource: c,
          }
        })
      setEvents(evts)
    } finally {
      setLoading(false)
    }
  }, [selectedPlatforms])

  useEffect(() => {
    loadCampaigns()
  }, [loadCampaigns])

  const handleEventDrop = async ({ event, start }) => {
    try {
      await updateCampaign(event.id, { schedule: start.toISOString() })
      setEvents((prev) =>
        prev.map((e) =>
          e.id === event.id
            ? { ...e, start, end: new Date(start.getTime() + 60 * 60 * 1000) }
            : e
        )
      )
    } catch (err) {
      alert(err.message)
    }
  }

  const handleSelectEvent = (event) => {
    if (!event?.id) return
    navigate(`/campaign/${event.id}/preview`)
  }

  const togglePlatform = (platform) => {
    setSelectedPlatforms((current) => (
      current.includes(platform)
        ? current.filter((item) => item !== platform)
        : [...current, platform]
    ))
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Calendario de postagens</h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Clique em um evento para abrir os posts gerados daquela campanha.</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white px-3 py-3 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="mb-2 flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Filtrar por redes</span>
              <button type="button" onClick={() => setSelectedPlatforms([])} className="text-xs text-primary-600 hover:underline dark:text-primary-400">
                Limpar
              </button>
            </div>
            <div role="group" aria-label="Filtrar calendario por redes" className="flex flex-wrap gap-2">
              {PLATFORM_OPTIONS.map((option) => {
                const active = selectedPlatforms.includes(option.value)
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => togglePlatform(option.value)}
                    aria-pressed={active}
                    className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${active ? 'border-primary-500 bg-primary-50 text-primary-700 dark:border-primary-400 dark:bg-primary-950/30 dark:text-primary-200' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700'}`}
                  >
                    {option.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
        {loading ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando...</p>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 h-[600px]">
            <DnDCalendar
              localizer={localizer}
              culture="pt-BR"
              events={events}
              startAccessor="start"
              endAccessor="end"
              titleAccessor="title"
              onEventDrop={handleEventDrop}
              onSelectEvent={handleSelectEvent}
              onSelectSlot={() => {}}
              selectable
              resizable={false}
              draggableAccessor={() => true}
              messages={{
                next: 'Proximo',
                previous: 'Anterior',
                today: 'Hoje',
                month: 'Mes',
                week: 'Semana',
                day: 'Dia',
                agenda: 'Agenda',
                date: 'Data',
                time: 'Hora',
                event: 'Evento',
                allDay: 'Dia inteiro',
                work_week: 'Semana util',
                showMore: (total) => `+${total} mais`,
                noEventsInRange: 'Nenhuma postagem agendada neste periodo.',
              }}
            />
          </div>
        )}
      </main>
    </div>
  )
}
