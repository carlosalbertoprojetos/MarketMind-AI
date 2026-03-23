import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getCampaigns, getSummary, deleteCampaign, createCampaign, getSavedFinalContentRuns } from '../api/client'
import CampaignCard from '../components/CampaignCard'
import Navbar from '../components/Navbar'
import { buildPrefetchHandlers, preloadRoutesWhenIdle } from '../utils/routePrefetch'
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
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'X' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'youtube', label: 'YouTube' },
]

function formatSavedDate(value) {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString('pt-BR')
  } catch {
    return String(value)
  }
}

const SORT_OPTIONS = [
  { value: 'created_at_desc', label: 'Mais recentes' },
  { value: 'created_at_asc', label: 'Mais antigas' },
  { value: 'schedule_asc', label: 'Agendamento (proximos primeiro)' },
  { value: 'schedule_desc', label: 'Agendamento (ultimos primeiro)' },
]

export default function Dashboard() {
  const { addToast } = useToast()
  const [campaigns, setCampaigns] = useState([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [summary, setSummary] = useState(null)
  const [savedContents, setSavedContents] = useState([])
  const [savedContentsTotal, setSavedContentsTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPlatforms, setSelectedPlatforms] = useState([])
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState('created_at_desc')
  const [pageSize, setPageSize] = useState(() => getStoredPageSize())
  const searchDebounceRef = useRef(false)


  const createCampaignPrefetchProps = buildPrefetchHandlers(['createCampaign'])
  const finalContentPrefetchProps = buildPrefetchHandlers(['finalContent'])

  const load = async (pageOffset = 0) => {
    setLoading(true)
    setError('')
    try {
      const filters = { platforms: selectedPlatforms, search: search || undefined, sort }
      const [data, sum, saved] = await Promise.all([
        getCampaigns(pageSize, pageOffset, filters),
        getSummary(),
        getSavedFinalContentRuns(4).catch(() => ({ items: [] })),
      ])
      setCampaigns(data.items ?? data)
      setTotal(data.total ?? 0)
      setOffset(data.offset ?? pageOffset)
      setSummary(sum)
      setSavedContents(saved.items || [])
      setSavedContentsTotal(saved.total || 0)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(0)
  }, [selectedPlatforms, sort, pageSize])


  useEffect(() => {
    return preloadRoutesWhenIdle(['createCampaign', 'finalContent', 'calendar', 'media'])
  }, [])

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

  const togglePlatform = (value) => {
    setSelectedPlatforms((current) => (
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value]
    ))
  }

  const clearPlatformFilters = () => setSelectedPlatforms([])

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
      addToast('Campanha excluida.')
    } catch (e) {
      addToast(e.message || 'Erro ao excluir', 'error')
    }
  }

  const handleDuplicate = async (campaign) => {
    try {
      const copy = await createCampaign({
        title: `${campaign.title} (copia)`,
        content: campaign.content || null,
        platform: campaign.platform || campaign.platforms?.[0] || null,
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
      <main className="max-w-7xl mx-auto p-6">
        <div className="flex items-center justify-between gap-3 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Minhas campanhas</h1>
          <div className="flex items-center gap-2">
            <Link
              to="/campaign/new"
              {...createCampaignPrefetchProps}
              className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600"
            >
              Nova campanha
            </Link>
          </div>
        </div>
        {summary && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                <p className="text-sm text-gray-500 dark:text-gray-400">Total de campanhas</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_campaigns}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                <p className="text-sm text-gray-500 dark:text-gray-400">Por plataforma</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {Object.entries(summary.by_platform).length
                    ? Object.entries(summary.by_platform).map(([k, v]) => `${k}: ${v}`).join(' - ')
                    : '-'}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                <p className="text-sm text-gray-500 dark:text-gray-400">Proximas 24h</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.upcoming_count}</p>
              </div>
            </div>
            <section className="mb-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Ultimos conteudos salvos</h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Acesse rapidamente os posts ja gerados no Studio IA. Total salvo: {savedContentsTotal}.</p>
                </div>
                <Link to="/final-content" {...finalContentPrefetchProps} className="text-sm font-medium text-primary-600 hover:underline dark:text-primary-400">Abrir Studio IA</Link>
              </div>
              {savedContents.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum conteudo salvo ainda.</p>
              ) : (
                <div className="grid gap-3 md:grid-cols-2">
                  {savedContents.map((item) => (
                    <Link
                      key={item.id}
                      to={`/final-content?saved=${item.id}`}
                      {...finalContentPrefetchProps}
                      className="rounded-lg border border-gray-200 p-3 transition hover:border-primary-500 dark:border-gray-700"
                    >
                      <div className="font-medium text-gray-900 dark:text-white">{item.title || item.theme || `Conteudo #${item.id}`}</div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">{formatSavedDate(item.created_at)}</div>
                      <div className="mt-2 text-xs text-gray-600 dark:text-gray-300">{item.platforms?.join(', ') || 'sem plataformas'}</div>
                      <div className="mt-1 text-xs text-gray-600 dark:text-gray-300">Posts: {item.post_count}</div>
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
        <div className="mb-4 flex flex-wrap items-start gap-3">
          <div className="rounded-lg border border-gray-200 bg-white px-3 py-3 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="mb-2 flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Filtrar por redes</span>
              <button type="button" onClick={clearPlatformFilters} className="text-xs text-primary-600 dark:text-primary-400 hover:underline">
                Limpar
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
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
          <input
            type="search"
            placeholder="Buscar por titulo..."
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
            <span>Itens por pagina</span>
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
          <p className="text-gray-500 dark:text-gray-400">Carregando...</p>
        ) : campaigns.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400">
            Nenhuma campanha ainda. Crie uma a partir de uma URL para gerar conteudo para redes sociais.
            <Link to="/campaign/new" {...createCampaignPrefetchProps} className="block mt-4 text-primary-600 dark:text-primary-400 hover:underline">
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
                  Mostrando {from} - {to} de {total}
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
                    Proxima
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
