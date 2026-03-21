import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getCampaigns, getSummary, deleteCampaign, createCampaign } from '../api/client'
import CampaignCard from '../components/CampaignCard'
import Navbar from '../components/Navbar'
import { useToast } from '../context/ToastContext'

const PAGE_SIZE_OPTIONS = [12, 24, 50]
const DEFAULT_PAGE_SIZE = 12
const STORAGE_KEY_PAGE_SIZE = 'marketingai_dashboard_page_size'

function getStoredPageSize() {
  try {
    const v = parseInt(localStorage.getItem(STORAGE_KEY_PAGE_SIZE), 10)
    return PAGE_SIZE_OPTIONS.includes(v) ? v : DEFAULT_PAGE_SIZE
  } catch {
    return DEFAULT_PAGE_SIZE
  }
}

const PLATFORM_OPTIONS = [
  { value: '', label: 'Todas as plataformas' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'tiktok', label: 'TikTok' },
]
const SORT_OPTIONS = [
  { value: 'created_at_desc', label: 'Mais recentes' },
  { value: 'created_at_asc', label: 'Mais antigas' },
  { value: 'schedule_asc', label: 'Agendamento (próximos primeiro)' },
  { value: 'schedule_desc', label: 'Agendamento (últimos primeiro)' },
]

export default function Dashboard() {
  const { addToast } = useToast()
  const [campaigns, setCampaigns] = useState([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [platform, setPlatform] = useState('')
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState('created_at_desc')
  const [pageSize, setPageSize] = useState(() => getStoredPageSize())
  const searchDebounceRef = useRef(false)

  const load = async (pageOffset = 0) => {
    setLoading(true)
    setError('')
    try {
      const filters = { platform: platform || undefined, search: search || undefined, sort }
      const [data, sum] = await Promise.all([
        getCampaigns(pageSize, pageOffset, filters),
        getSummary(),
      ])
      setCampaigns(data.items ?? data)
      setTotal(data.total ?? 0)
      setOffset(data.offset ?? pageOffset)
      setSummary(sum)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(0)
  }, [platform, sort, pageSize])

  useEffect(() => {
    if (!searchDebounceRef.current) {
      searchDebounceRef.current = true
      return
    }
    const t = setTimeout(() => load(0), 300)
    return () => clearTimeout(t)
  }, [search])

  const from = total === 0 ? 0 : offset + 1
  const to = Math.min(offset + pageSize, total)

  const handlePageSizeChange = (e) => {
    const v = parseInt(e.target.value, 10)
    if (PAGE_SIZE_OPTIONS.includes(v)) {
      setPageSize(v)
      try {
        localStorage.setItem(STORAGE_KEY_PAGE_SIZE, String(v))
      } catch (_) {}
    }
  }

  const goPrev = () => {
    const prev = Math.max(0, offset - pageSize)
    load(prev)
  }
  const goNext = () => {
    if (offset + pageSize < total) load(offset + pageSize)
  }

  const handleDelete = async (campaign) => {
    if (!window.confirm(`Excluir campanha "${campaign.title}"?`)) return
    try {
      await deleteCampaign(campaign.id)
      const sum = await getSummary()
      setSummary(sum)
      setTotal((t) => Math.max(0, t - 1))
      setCampaigns((prev) => prev.filter((c) => c.id !== campaign.id))
      if (campaigns.length <= 1 && offset > 0) load(Math.max(0, offset - pageSize))
      addToast('Campanha excluída.')
    } catch (e) {
      addToast(e.message || 'Erro ao excluir', 'error')
    }
  }

  const handleDuplicate = async (campaign) => {
    try {
      const copy = await createCampaign({
        title: `${campaign.title} (cópia)`,
        content: campaign.content || null,
        platform: campaign.platform || null,
        schedule: null,
      })
      addToast('Campanha duplicada.')
      setCampaigns((prev) => [copy, ...prev])
      setTotal((t) => t + 1)
      if (summary) setSummary({ ...summary, total_campaigns: summary.total_campaigns + 1 })
    } catch (e) {
      addToast(e.message || 'Erro ao duplicar', 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Minhas campanhas</h1>
          <Link
            to="/campaign/new"
            className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600"
          >
            Nova campanha
          </Link>
        </div>
        {summary && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <p className="text-sm text-gray-500 dark:text-gray-400">Total de campanhas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_campaigns}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <p className="text-sm text-gray-500 dark:text-gray-400">Por plataforma</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {Object.entries(summary.by_platform).length
                  ? Object.entries(summary.by_platform).map(([k, v]) => `${k}: ${v}`).join(' · ')
                  : '—'}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
              <p className="text-sm text-gray-500 dark:text-gray-400">Próximas 24h</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.upcoming_count}</p>
            </div>
          </div>
        )}
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {PLATFORM_OPTIONS.map((o) => (
              <option key={o.value || 'all'} value={o.value}>{o.label}</option>
            ))}
          </select>
          <input
            type="search"
            placeholder="Buscar por título..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="min-w-[180px] rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <span>Itens por página</span>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {PAGE_SIZE_OPTIONS.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
        </div>
        {error && (
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        )}
        {loading ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando…</p>
        ) : campaigns.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400">
            Nenhuma campanha ainda. Crie uma a partir de uma URL para gerar conteúdo para redes sociais.
            <Link to="/campaign/new" className="block mt-4 text-primary-600 dark:text-primary-400 hover:underline">
              Criar primeira campanha
            </Link>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2">
              {campaigns.map((c) => (
                <CampaignCard
                  key={c.id}
                  campaign={c}
                  onDelete={handleDelete}
                  onDuplicate={handleDuplicate}
                />
              ))}
            </div>
            {total > pageSize && (
              <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-gray-200 dark:border-gray-700 pt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Mostrando {from}–{to} de {total}
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={goPrev}
                    disabled={offset === 0}
                    className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 disabled:pointer-events-none disabled:opacity-50"
                  >
                    Anterior
                  </button>
                  <button
                    type="button"
                    onClick={goNext}
                    disabled={offset + pageSize >= total}
                    className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 disabled:pointer-events-none disabled:opacity-50"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
