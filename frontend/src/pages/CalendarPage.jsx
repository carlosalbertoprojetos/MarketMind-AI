import { useState, useCallback, useEffect } from 'react'
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

/**
 * Calendário visual tipo Google Calendar.
 * Eventos = campanhas com schedule; drag-and-drop para reorganizar data/hora.
 */
export default function CalendarPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [platformFilter, setPlatformFilter] = useState('')  // '' = todas

  const loadCampaigns = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getCampaigns()
      const list = data.items ?? data
      const evts = list
        .filter((c) => c.schedule)
        .filter((c) => !platformFilter || (c.platform && c.platform.toLowerCase() === platformFilter.toLowerCase()))
        .map((c) => ({
          id: c.id,
          title: [c.platform, c.title].filter(Boolean).join(' · '),
          start: new Date(c.schedule),
          end: new Date(new Date(c.schedule).getTime() + 60 * 60 * 1000),
          resource: c,
        }))
      setEvents(evts)
    } finally {
      setLoading(false)
    }
  }, [platformFilter])

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

  const handleSelectSlot = () => {
    // Opcional: abrir modal para criar evento no slot
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Calendário de postagens</h1>
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
          >
            <option value="">Todas as redes</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="linkedin">LinkedIn</option>
            <option value="twitter">Twitter</option>
            <option value="tiktok">TikTok</option>
          </select>
        </div>
        {loading ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando…</p>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 h-[600px]">
            <DnDCalendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              titleAccessor="title"
              onEventDrop={handleEventDrop}
              onSelectSlot={handleSelectSlot}
              selectable
              resizable={false}
              draggableAccessor={() => true}
              messages={{
                next: 'Próximo',
                previous: 'Anterior',
                today: 'Hoje',
                month: 'Mês',
                week: 'Semana',
                day: 'Dia',
                agenda: 'Agenda',
                date: 'Data',
                time: 'Hora',
                event: 'Evento',
                noEventsInRange: 'Nenhuma postagem agendada neste período.',
              }}
            />
          </div>
        )}
      </main>
    </div>
  )
}
