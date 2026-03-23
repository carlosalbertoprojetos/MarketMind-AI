import { useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import {
  deleteSavedFinalContentRun,
  exportFinalContentPipeline,
  getSavedFinalContentRun,
  getSavedFinalContentRuns,
  publishFinalContentPipeline,
  runFinalContentPipeline,
} from '../api/client'
import { useToast } from '../context/ToastContext'

const PLATFORM_OPTIONS = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'x', label: 'X' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'facebook', label: 'Facebook' },
]

function formatDate(value) {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString('pt-BR')
  } catch {
    return String(value)
  }
}

function getPlatformLabel(platform) {
  if ((platform || '').toLowerCase() === 'twitter') return 'X'
  return PLATFORM_OPTIONS.find((item) => item.value === platform)?.label || platform || '-'
}

function getResultPlatforms(result) {
  const values = Array.isArray(result?.platforms) && result.platforms.length
    ? result.platforms
    : (result?.outputs || []).map((item) => item.platform)
  return [...new Set(values.filter(Boolean).map((item) => String(item).toLowerCase()))]
}

function PlatformBadge({ platform }) {
  return (
    <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-200">
      {getPlatformLabel(platform)}
    </span>
  )
}

export default function FinalContentPage() {
  const location = useLocation()
  const { addToast } = useToast()
  const [theme, setTheme] = useState('')
  const [objective, setObjective] = useState('branding')
  const [audience, setAudience] = useState('')
  const [platforms, setPlatforms] = useState(PLATFORM_OPTIONS.map((item) => item.value))
  const [style, setStyle] = useState('modern')
  const [loading, setLoading] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [savedLoading, setSavedLoading] = useState(true)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [publishResults, setPublishResults] = useState([])
  const [savedItems, setSavedItems] = useState([])
  const [savedTotal, setSavedTotal] = useState(0)
  const [activeSavedId, setActiveSavedId] = useState(null)
  const [savedSearch, setSavedSearch] = useState('')
  const [savedPlatforms, setSavedPlatforms] = useState([])
  const [savedCreatedFrom, setSavedCreatedFrom] = useState('')
  const [savedCreatedTo, setSavedCreatedTo] = useState('')

  const resultPlatforms = useMemo(() => getResultPlatforms(result), [result])

  const togglePlatform = (platform) => {
    setPlatforms((prev) => prev.includes(platform) ? prev.filter((item) => item !== platform) : [...prev, platform])
  }

  const toggleSavedPlatform = (platform) => {
    setSavedPlatforms((prev) => prev.includes(platform) ? prev.filter((item) => item !== platform) : [...prev, platform])
  }

  const ensureValid = () => {
    if (!theme.trim() || !audience.trim()) {
      setError('Informe tema e publico.')
      return false
    }
    if (!platforms.length) {
      setError('Selecione ao menos uma plataforma.')
      return false
    }
    setError('')
    return true
  }

  const buildOpts = () => ({ platforms, style })

  const applyResult = (data, toastMessage) => {
    setResult(data)
    setPublishResults(data.publish_results || [])
    setActiveSavedId(data.saved_content_id || data.id || null)
    if (data.theme) setTheme(data.theme)
    if (data.objective) setObjective(data.objective)
    if (data.audience) setAudience(data.audience)
    if (data.platforms?.length) setPlatforms(data.platforms)
    if (data.style) setStyle(data.style)
    if (toastMessage) addToast(toastMessage)
  }

  const loadSavedItems = async (preferredId = null, overrideFilters = null) => {
    setSavedLoading(true)
    try {
      const filters = overrideFilters || {
        search: savedSearch,
        platforms: savedPlatforms,
        createdFrom: savedCreatedFrom,
        createdTo: savedCreatedTo,
      }
      const data = await getSavedFinalContentRuns(20, filters)
      const items = data.items || []
      setSavedItems(items)
      setSavedTotal(data.total || 0)
      const currentVisibleId = items.some((item) => item.id === activeSavedId) ? activeSavedId : null
      const targetId = preferredId || currentVisibleId || items[0]?.id || null
      if (targetId) {
        const detail = await getSavedFinalContentRun(targetId)
        applyResult(detail)
      } else if (!preferredId) {
        setResult(null)
        setPublishResults([])
        setActiveSavedId(null)
      }
    } catch (e) {
      if (preferredId) {
        setError(e.message || 'Erro ao carregar conteudos salvos')
      }
    } finally {
      setSavedLoading(false)
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const preferredIdRaw = params.get('saved')
    const preferredId = preferredIdRaw ? Number(preferredIdRaw) : null
    loadSavedItems(Number.isFinite(preferredId) ? preferredId : null)
  }, [location.search, savedSearch, savedPlatforms, savedCreatedFrom, savedCreatedTo])

  const handleGenerate = async () => {
    if (!ensureValid()) return
    setLoading(true)
    setPublishResults([])
    try {
      const data = await runFinalContentPipeline(theme, objective, audience, buildOpts())
      applyResult(data, 'Conteudo gerado e salvo.')
      await loadSavedItems(data.saved_content_id)
    } catch (e) {
      setError(e.message || 'Erro ao executar pipeline final')
      addToast(e.message || 'Erro ao executar pipeline final', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    if (!ensureValid()) return
    setExporting(true)
    try {
      await exportFinalContentPipeline(theme, objective, audience, buildOpts())
      addToast('Exportacao iniciada.')
    } catch (e) {
      setError(e.message || 'Erro ao exportar pipeline final')
      addToast(e.message || 'Erro ao exportar pipeline final', 'error')
    } finally {
      setExporting(false)
    }
  }

  const handlePublish = async () => {
    if (!ensureValid()) return
    setPublishing(true)
    try {
      const data = await publishFinalContentPipeline(theme, objective, audience, buildOpts())
      applyResult(data, 'Publicacao processada e salva.')
      await loadSavedItems(data.saved_content_id)
    } catch (e) {
      setError(e.message || 'Erro ao publicar pipeline final')
      addToast(e.message || 'Erro ao publicar pipeline final', 'error')
    } finally {
      setPublishing(false)
    }
  }

  const openSavedRun = async (id) => {
    try {
      const data = await getSavedFinalContentRun(id)
      applyResult(data)
    } catch (e) {
      setError(e.message || 'Erro ao abrir conteudo salvo')
      addToast(e.message || 'Erro ao abrir conteudo salvo', 'error')
    }
  }

  const removeSavedRun = async (id) => {
    if (!window.confirm('Remover este conteudo salvo?')) return
    try {
      await deleteSavedFinalContentRun(id)
      if (activeSavedId === id) {
        setResult(null)
        setPublishResults([])
        setActiveSavedId(null)
      }
      await loadSavedItems()
      addToast('Conteudo salvo removido.')
    } catch (e) {
      setError(e.message || 'Erro ao remover conteudo salvo')
      addToast(e.message || 'Erro ao remover conteudo salvo', 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Studio de Conteudo Final</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">Gera conteudo completo por plataforma, salva cada execucao e permite reabrir posts ja produzidos sem recalcular.</p>
        </div>

        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Tema</label>
            <input value={theme} onChange={(e) => setTheme(e.target.value)} className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100" placeholder="Ex: Gestao comercial com IA" />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Objetivo</label>
              <select value={objective} onChange={(e) => setObjective(e.target.value)} className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100">
                <option value="branding">Branding</option>
                <option value="engajamento">Engajamento</option>
                <option value="conversao">Conversao</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Publico</label>
              <input value={audience} onChange={(e) => setAudience(e.target.value)} className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100" placeholder="Ex: times de vendas e operacao" />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Plataformas</label>
              <div role="group" aria-label="Selecionar plataformas para gerar" className="mt-2 flex flex-wrap gap-2">
                {PLATFORM_OPTIONS.map((option) => {
                  const active = platforms.includes(option.value)
                  return (
                    <button key={option.value} type="button" onClick={() => togglePlatform(option.value)} className={`rounded-full border px-3 py-1.5 text-sm ${active ? 'border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-950/30 dark:text-primary-300' : 'border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-200'}`}>
                      {option.label}
                    </button>
                  )
                })}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">Estilo visual</label>
              <select value={style} onChange={(e) => setStyle(e.target.value)} className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100">
                <option value="modern">Modern</option>
                <option value="editorial">Editorial</option>
                <option value="bold">Bold</option>
                <option value="minimal">Minimal</option>
              </select>
            </div>
          </div>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={handleGenerate} disabled={loading} className="rounded-lg bg-primary-500 px-4 py-2 text-white hover:bg-primary-600 disabled:opacity-50">{loading ? 'Gerando...' : 'Gerar e salvar conteudo'}</button>
            <button type="button" onClick={handleExport} disabled={exporting} className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700">{exporting ? 'Exportando...' : 'Exportar ZIP'}</button>
            <button type="button" onClick={handlePublish} disabled={publishing} className="rounded-lg border border-emerald-500 px-4 py-2 text-emerald-700 hover:bg-emerald-50 disabled:opacity-50 dark:text-emerald-300 dark:hover:bg-emerald-950/30">{publishing ? 'Publicando...' : 'Publicar e salvar'}</button>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
          <aside className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Conteudos salvos</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Total: {savedTotal}</p>
              </div>
              {savedLoading && <span className="text-xs text-gray-500 dark:text-gray-400">Carregando...</span>}
            </div>
            <div className="mt-4 grid gap-3">
              <input
                value={savedSearch}
                onChange={(e) => setSavedSearch(e.target.value)}
                placeholder="Buscar por tema ou publico"
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/30">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-200">Filtrar salvos por redes</span>
                  <button type="button" onClick={() => setSavedPlatforms([])} className="text-xs text-primary-600 hover:underline dark:text-primary-400">Limpar</button>
                </div>
                <div role="group" aria-label="Filtrar salvos por redes" className="flex flex-wrap gap-2">
                  {PLATFORM_OPTIONS.map((option) => {
                    const active = savedPlatforms.includes(option.value)
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleSavedPlatform(option.value)}
                        aria-pressed={active}
                        className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${active ? 'border-primary-500 bg-primary-50 text-primary-700 dark:border-primary-400 dark:bg-primary-950/30 dark:text-primary-200' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700'}`}
                      >
                        {option.label}
                      </button>
                    )
                  })}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={savedCreatedFrom}
                  onChange={(e) => setSavedCreatedFrom(e.target.value)}
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                />
                <input
                  type="date"
                  value={savedCreatedTo}
                  onChange={(e) => setSavedCreatedTo(e.target.value)}
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
            <div className="mt-4 space-y-3">
              {savedItems.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum conteudo salvo ainda.</p>
              ) : savedItems.map((item) => (
                <div key={item.id} className={`rounded-lg border p-3 ${activeSavedId === item.id ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/20' : 'border-gray-200 dark:border-gray-700'}`}>
                  <button type="button" onClick={() => openSavedRun(item.id)} className="w-full text-left">
                    <div className="font-medium text-gray-900 dark:text-white">{item.title || item.theme || `Conteudo #${item.id}`}</div>
                    <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">{formatDate(item.created_at)}</div>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {(item.platforms || []).length ? item.platforms.map((platform) => (
                        <PlatformBadge key={`${item.id}-${platform}`} platform={platform} />
                      )) : <span className="text-xs text-gray-500 dark:text-gray-400">sem plataformas</span>}
                    </div>
                    <div className="mt-2 text-xs text-gray-600 dark:text-gray-300">Posts: {item.post_count}</div>
                  </button>
                  <button type="button" onClick={() => removeSavedRun(item.id)} className="mt-3 text-xs text-red-600 hover:text-red-700 dark:text-red-400">Excluir</button>
                </div>
              ))}
            </div>
          </aside>

          <div className="space-y-6">
            {result && (
              <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800 text-sm text-gray-600 dark:text-gray-300">
                <div className="flex flex-wrap gap-4">
                  <p><strong>ID salvo:</strong> #{result.saved_content_id || result.id || '-'}</p>
                  <p><strong>Salvo em:</strong> {formatDate(result.saved_at)}</p>
                  <p><strong>Tema:</strong> {result.theme}</p>
                </div>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <strong className="text-gray-700 dark:text-gray-200">Plataformas:</strong>
                  {resultPlatforms.length ? resultPlatforms.map((platform) => (
                    <PlatformBadge key={`result-${platform}`} platform={platform} />
                  )) : <span>-</span>}
                </div>
              </section>
            )}

            {result && (
              <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Sugestoes de Testes A/B</h2>
                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  {result.ab_test_suggestions?.map((item) => (
                    <div key={`${item.platform}-${item.hypothesis}`} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">{getPlatformLabel(item.platform)}</div>
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{item.hypothesis}</p>
                      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400"><strong>Metrica:</strong> {item.success_metric}</p>
                      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400"><strong>Variante A:</strong> {item.variant_a}</p>
                      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400"><strong>Variante B:</strong> {item.variant_b}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {result && (
              <div className="grid gap-4 xl:grid-cols-2">
                {result.outputs?.map((item) => (
                  <article key={`${result.saved_content_id || result.id || 'current'}-${item.platform}`} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800 space-y-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{getPlatformLabel(item.platform)}</h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Formato: {item.content_format}</p>
                      </div>
                      <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-200">{item.visual_decision?.selected_mode || 'n/a'}</span>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Hooks</h3>
                      <ul className="mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-200">
                        {item.hooks?.map((hook) => <li key={hook}>- {hook}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Conteudo completo</h3>
                      <p className="mt-2 whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm text-gray-700 dark:bg-gray-900/40 dark:text-gray-200">{item.full_content}</p>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">CTA</h3>
                        <ul className="mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-200">
                          {item.cta_options?.map((cta) => <li key={cta}>- {cta}</li>)}
                        </ul>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">Variacoes A/B</h3>
                        <ul className="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-200">
                          {item.ab_variations?.map((variation) => <li key={variation.label}><strong>{variation.label}:</strong> {variation.text}</li>)}
                        </ul>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Prompt de imagem</h3>
                      <p className="mt-2 whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm text-gray-700 dark:bg-gray-900/40 dark:text-gray-200">{item.image_prompt}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white">Estrutura narrativa</h3>
                      <pre className="mt-2 overflow-auto rounded-lg bg-gray-50 p-3 text-xs text-gray-700 dark:bg-gray-900/40 dark:text-gray-200">{JSON.stringify(item.narrative_structure, null, 2)}</pre>
                    </div>
                  </article>
                ))}
              </div>
            )}

            {publishResults.length > 0 && (
              <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Resultados de publicacao</h2>
                <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {publishResults.map((item) => (
                    <div key={`${item.platform}-${item.external_id || item.provider}`} className="rounded-lg border border-gray-200 p-4 text-sm dark:border-gray-700">
                      <div className="font-medium text-gray-900 dark:text-white">{getPlatformLabel(item.platform)}</div>
                      <div className="mt-1 text-gray-600 dark:text-gray-300">Status: {item.status}</div>
                      <div className="mt-1 text-gray-600 dark:text-gray-300">Provider: {item.provider}</div>
                      {item.error && <div className="mt-1 text-red-600 dark:text-red-400">Erro: {item.error}</div>}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
