import { useEffect, useMemo, useState } from 'react'
import Navbar from '../components/Navbar'
import { getCampaigns, getCampaignAssets, getCampaignGenerations, exportSelectedCampaignAssetsZip, deleteSelectedCampaignAssets, BASE } from '../api/client'
import { useToast } from '../context/ToastContext'

const PLATFORM_OPTIONS = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'X' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'youtube', label: 'YouTube' },
]

function toAbsoluteMediaUrl(path) {
  if (!path) return ''
  const normalizedBase = String(BASE || '').replace(/\/$/, '')
  return `${normalizedBase}/${path}`.replace('/api//', '/api/')
}

function getCampaignPlatforms(campaign) {
  if (Array.isArray(campaign?.platforms) && campaign.platforms.length > 0) return campaign.platforms
  return campaign?.platform ? [campaign.platform] : []
}

function formatCampaignLabel(campaign) {
  const platforms = getCampaignPlatforms(campaign)
  if (!platforms.length) return campaign.title
  return `${campaign.title} (${platforms.join(', ')})`
}

export default function MediaLibraryPage() {
  const { addToast } = useToast()
  const [campaigns, setCampaigns] = useState([])
  const [selectedCampaignId, setSelectedCampaignId] = useState('')
  const [assets, setAssets] = useState([])
  const [generations, setGenerations] = useState([])
  const [sourceUrl, setSourceUrl] = useState('')
  const [kindFilter, setKindFilter] = useState('')
  const [platformFilter, setPlatformFilter] = useState('')
  const [selectedCampaignPlatforms, setSelectedCampaignPlatforms] = useState([])
  const [generatedFrom, setGeneratedFrom] = useState('')
  const [generatedTo, setGeneratedTo] = useState('')
  const [loadingCampaigns, setLoadingCampaigns] = useState(true)
  const [loadingAssets, setLoadingAssets] = useState(false)
  const [exportingSelected, setExportingSelected] = useState(false)
  const [deletingSelected, setDeletingSelected] = useState(false)
  const [selectedPaths, setSelectedPaths] = useState([])
  const [brokenPaths, setBrokenPaths] = useState([])
  const [error, setError] = useState('')

  const visibleCampaigns = useMemo(() => {
    if (!selectedCampaignPlatforms.length) return campaigns
    return campaigns.filter((campaign) => getCampaignPlatforms(campaign).some((item) => selectedCampaignPlatforms.includes(item)))
  }, [campaigns, selectedCampaignPlatforms])

  useEffect(() => {
    const load = async () => {
      setLoadingCampaigns(true)
      setError('')
      try {
        const data = await getCampaigns(100, 0, { platforms: selectedCampaignPlatforms })
        const list = data.items ?? []
        setCampaigns(list)
        if (!list.length) {
          setSelectedCampaignId('')
        } else if (!list.some((item) => String(item.id) === String(selectedCampaignId))) {
          setSelectedCampaignId(String(list[0].id))
        }
      } catch (e) {
        setError(e.message || 'Erro ao carregar campanhas')
      } finally {
        setLoadingCampaigns(false)
      }
    }
    load()
  }, [selectedCampaignPlatforms, selectedCampaignId])

  useEffect(() => {
    if (!selectedCampaignId) {
      setAssets([])
      setSourceUrl('')
      setGenerations([])
      return
    }
    const loadAssets = async () => {
      setLoadingAssets(true)
      setError('')
      try {
        const [assetsData, generationsData] = await Promise.all([
          getCampaignAssets(selectedCampaignId, {
            kind: kindFilter,
            platform: platformFilter,
            generatedFrom,
            generatedTo,
          }),
          getCampaignGenerations(selectedCampaignId),
        ])
        setAssets(assetsData.assets || [])
        setBrokenPaths([])
        setSelectedPaths([])
        setSourceUrl(assetsData.source_url || '')
        setGenerations(generationsData.generations || [])
      } catch (e) {
        const msg = e.message || 'Erro ao carregar biblioteca de mídia'
        setError(msg)
        addToast(msg, 'error')
      } finally {
        setLoadingAssets(false)
      }
    }
    loadAssets()
  }, [selectedCampaignId, kindFilter, platformFilter, generatedFrom, generatedTo, addToast])

  const toggleCampaignPlatform = (value) => {
    setSelectedCampaignPlatforms((current) => (
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value]
    ))
  }

  const clearCampaignPlatformFilters = () => setSelectedCampaignPlatforms([])

  const toggleAssetSelection = (path) => {
    setSelectedPaths((prev) => (prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]))
  }

  const selectAllVisible = () => {
    setSelectedPaths(assets.map((a) => a.path))
  }

  const clearSelection = () => {
    setSelectedPaths([])
  }

  const markAssetAsBroken = (path) => {
    setBrokenPaths((prev) => (prev.includes(path) ? prev : [...prev, path]))
  }

  const handleExportSelected = async () => {
    if (!selectedCampaignId || selectedPaths.length === 0) return
    setExportingSelected(true)
    try {
      await exportSelectedCampaignAssetsZip(selectedCampaignId, selectedPaths)
      addToast('Download do ZIP dos selecionados iniciado.')
    } catch (e) {
      const msg = e.message || 'Erro ao exportar ativos selecionados'
      addToast(msg, 'error')
    } finally {
      setExportingSelected(false)
    }
  }

  const handleDeleteSelected = async () => {
    if (!selectedCampaignId || selectedPaths.length === 0) return
    if (!window.confirm(`Excluir ${selectedPaths.length} ativo(s) selecionado(s)?`)) return
    setDeletingSelected(true)
    try {
      const response = await deleteSelectedCampaignAssets(selectedCampaignId, selectedPaths)
      setAssets((prev) => prev.filter((asset) => !selectedPaths.includes(asset.path)))
      setSelectedPaths([])
      addToast(`${response.deleted_count || 0} ativo(s) excluido(s).`)
    } catch (e) {
      const msg = e.message || 'Erro ao excluir ativos selecionados'
      addToast(msg, 'error')
    } finally {
      setDeletingSelected(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Biblioteca de mídia</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Repositório dos ativos visuais gerados por campanha a partir da URL informada.
        </p>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm mb-6">
          <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/30">
            <div className="mb-2 flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Filtrar campanhas por redes</span>
              <button type="button" onClick={clearCampaignPlatformFilters} className="text-xs text-primary-600 dark:text-primary-400 hover:underline">
                Limpar
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {PLATFORM_OPTIONS.map((option) => {
                const active = selectedCampaignPlatforms.includes(option.value)
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => toggleCampaignPlatform(option.value)}
                    aria-pressed={active}
                    className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${active ? 'border-primary-500 bg-primary-50 text-primary-700 dark:border-primary-400 dark:bg-primary-950/30 dark:text-primary-200' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700'}`}
                  >
                    {option.label}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-3 items-end">
            <div className="xl:col-span-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                Campanha
              </label>
              {loadingCampaigns ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Carregando campanhas...</p>
              ) : visibleCampaigns.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma campanha encontrada para as redes selecionadas.</p>
              ) : (
                <select
                  value={selectedCampaignId}
                  onChange={(e) => setSelectedCampaignId(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                >
                  {visibleCampaigns.map((c) => (
                    <option key={c.id} value={c.id}>{formatCampaignLabel(c)}</option>
                  ))}
                </select>
              )}
            </div>
            <div className="xl:col-span-3">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-2">Tipo</label>
              <select
                value={kindFilter}
                onChange={(e) => setKindFilter(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option value="">Todos</option>
                <option value="generated">Geradas</option>
                <option value="screenshot">Screenshots</option>
              </select>
            </div>
            <div className="xl:col-span-3">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-2">Plataforma do ativo</label>
              <select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option value="">Todas</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">X</option>
                <option value="tiktok">TikTok</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>
          </div>

          {sourceUrl && (
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 break-all">
              URL fonte da campanha: {sourceUrl}
            </p>
          )}

          <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-3 items-end">
            <div className="lg:col-span-3">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">De (geração)</label>
              <input
                type="date"
                value={generatedFrom}
                onChange={(e) => setGeneratedFrom(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div className="lg:col-span-3">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Até (geração)</label>
              <input
                type="date"
                value={generatedTo}
                onChange={(e) => setGeneratedTo(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div className="lg:col-span-6 text-xs text-gray-500 dark:text-gray-400 self-end flex flex-wrap items-center justify-between gap-3">
              <span>{assets.length} ativo(s) encontrado(s)</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleExportSelected}
                  disabled={exportingSelected || selectedPaths.length === 0}
                  className="text-xs rounded border border-primary-400 dark:border-primary-500 px-2 py-1 text-primary-700 dark:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 disabled:opacity-50"
                >
                  {exportingSelected ? 'Exportando...' : `ZIP selecionados (${selectedPaths.length})`}
                </button>
                <button
                  type="button"
                  onClick={handleDeleteSelected}
                  disabled={deletingSelected || selectedPaths.length === 0}
                  className="text-xs rounded border border-red-300 dark:border-red-700 px-2 py-1 text-red-700 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50"
                >
                  {deletingSelected ? 'Excluindo...' : `Excluir selecionados (${selectedPaths.length})`}
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>}

        {loadingAssets ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando ativos...</p>
        ) : (
          <>
            {assets.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400">
                Nenhum ativo ainda para esta campanha. Gere os posts da campanha primeiro.
              </p>
            ) : (
              <>
                <div className="mb-3 flex items-center gap-2 text-xs">
                  <button
                    type="button"
                    onClick={selectAllVisible}
                    className="rounded border border-gray-300 dark:border-gray-600 px-2 py-1 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Selecionar todos visíveis
                  </button>
                  <button
                    type="button"
                    onClick={clearSelection}
                    className="rounded border border-gray-300 dark:border-gray-600 px-2 py-1 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Limpar seleção
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                  {assets.map((asset) => {
                    const isBroken = brokenPaths.includes(asset.path)
                    return (
                      <div
                        key={asset.path}
                        className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden shadow-sm"
                      >
                        <a href={toAbsoluteMediaUrl(asset.url)} target="_blank" rel="noreferrer" className="block">
                          {isBroken ? (
                            <div className="w-full h-40 flex items-center justify-center bg-gray-100 px-3 text-center text-xs text-gray-500 dark:bg-gray-700 dark:text-gray-300">
                              Nao foi possivel renderizar esta midia. Clique para abrir o arquivo diretamente.
                            </div>
                          ) : (
                            <img
                              src={toAbsoluteMediaUrl(asset.url)}
                              alt={asset.path}
                              className="w-full h-40 object-cover bg-gray-100 dark:bg-gray-700"
                              loading="lazy"
                              onError={() => markAssetAsBroken(asset.path)}
                            />
                          )}
                        </a>
                        <div className="p-2">
                          <p className="text-[11px] text-gray-700 dark:text-gray-200 truncate">{asset.path}</p>
                          <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase mt-1">
                            {asset.kind}{asset.platform ? ` · ${asset.platform}` : ''}
                          </p>
                          {asset.generated_at && (
                            <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-1">
                              {new Date(asset.generated_at).toLocaleString('pt-BR')}
                            </p>
                          )}
                          <label className="mt-2 inline-flex items-center gap-1 text-[11px] text-gray-600 dark:text-gray-300">
                            <input
                              type="checkbox"
                              checked={selectedPaths.includes(asset.path)}
                              onChange={() => toggleAssetSelection(asset.path)}
                            />
                            Selecionar
                          </label>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </>
            )}
            <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
              <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Histórico de gerações</h2>
              {generations.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma geração registrada ainda.</p>
              ) : (
                <ul className="space-y-2">
                  {generations.map((g) => (
                    <li key={`${g.generated_at}-${g.source_url}`} className="text-xs text-gray-600 dark:text-gray-300 border-b border-gray-100 dark:border-gray-700 pb-2">
                      <p><strong>Data:</strong> {new Date(g.generated_at).toLocaleString('pt-BR')}</p>
                      <p className="break-all"><strong>URL:</strong> {g.source_url}</p>
                      <p><strong>Posts:</strong> {g.post_count} · <strong>Ativos:</strong> {g.asset_count}</p>
                      <p><strong>Redes:</strong> {g.platforms?.length ? g.platforms.join(', ') : 'nao informado'}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
