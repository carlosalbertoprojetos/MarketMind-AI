import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { getCampaigns, getCampaignAssets, getCampaignGenerations, exportCampaignAssetsZip, exportSelectedCampaignAssetsZip, BASE } from '../api/client'
import { useToast } from '../context/ToastContext'

function toAbsoluteMediaUrl(path) {
  if (!path) return ''
  const normalizedBase = String(BASE || '').replace(/\/$/, '')
  return `${normalizedBase}/${path}`.replace('/api//', '/api/')
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
  const [generatedFrom, setGeneratedFrom] = useState('')
  const [generatedTo, setGeneratedTo] = useState('')
  const [loadingCampaigns, setLoadingCampaigns] = useState(true)
  const [loadingAssets, setLoadingAssets] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportingSelected, setExportingSelected] = useState(false)
  const [selectedPaths, setSelectedPaths] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoadingCampaigns(true)
      setError('')
      try {
        const data = await getCampaigns(100, 0)
        const list = data.items ?? []
        setCampaigns(list)
        if (list.length > 0) setSelectedCampaignId(String(list[0].id))
      } catch (e) {
        setError(e.message || 'Erro ao carregar campanhas')
      } finally {
        setLoadingCampaigns(false)
      }
    }
    load()
  }, [])

  useEffect(() => {
    if (!selectedCampaignId) {
      setAssets([])
      setSourceUrl('')
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
        const data = assetsData
        setAssets(data.assets || [])
        setSelectedPaths([])
        setSourceUrl(data.source_url || '')
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
  }, [selectedCampaignId, kindFilter, platformFilter, generatedFrom, generatedTo])

  const handleExportFiltered = async () => {
    if (!selectedCampaignId) return
    setExporting(true)
    try {
      await exportCampaignAssetsZip(selectedCampaignId, {
        kind: kindFilter,
        platform: platformFilter,
        generatedFrom,
        generatedTo,
      })
      addToast('Download do ZIP iniciado.')
    } catch (e) {
      const msg = e.message || 'Erro ao exportar ativos filtrados'
      addToast(msg, 'error')
    } finally {
      setExporting(false)
    }
  }

  const toggleAssetSelection = (path) => {
    setSelectedPaths((prev) => (prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]))
  }

  const selectAllVisible = () => {
    setSelectedPaths(assets.map((a) => a.path))
  }

  const clearSelection = () => {
    setSelectedPaths([])
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-6xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Biblioteca de mídia</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Repositório dos ativos visuais gerados por campanha a partir da URL informada.
        </p>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            Campanha
          </label>
          {loadingCampaigns ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Carregando campanhas...</p>
          ) : (
            <select
              value={selectedCampaignId}
              onChange={(e) => setSelectedCampaignId(e.target.value)}
              className="w-full md:w-[360px] rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
            >
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
          )}
          {sourceUrl && (
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 break-all">
              URL fonte da campanha: {sourceUrl}
            </p>
          )}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Tipo</label>
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
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Plataforma</label>
              <select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option value="">Todas</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter/X</option>
                <option value="tiktok">TikTok</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">De (geração)</label>
              <input
                type="date"
                value={generatedFrom}
                onChange={(e) => setGeneratedFrom(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Até (geração)</label>
              <input
                type="date"
                value={generatedTo}
                onChange={(e) => setGeneratedTo(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              />
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 self-end flex items-center justify-between gap-3">
              <span>{assets.length} ativo(s) encontrado(s)</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleExportFiltered}
                  disabled={exporting || assets.length === 0}
                  className="text-xs rounded border border-gray-300 dark:border-gray-600 px-2 py-1 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  {exporting ? 'Exportando...' : 'Baixar ZIP filtrado'}
                </button>
                <button
                  type="button"
                  onClick={handleExportSelected}
                  disabled={exportingSelected || selectedPaths.length === 0}
                  className="text-xs rounded border border-primary-400 dark:border-primary-500 px-2 py-1 text-primary-700 dark:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 disabled:opacity-50"
                >
                  {exportingSelected ? 'Exportando...' : `ZIP selecionados (${selectedPaths.length})`}
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>}

        {loadingAssets ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando ativos...</p>
        ) : assets.length === 0 ? (
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
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {assets.map((asset) => (
                <div
                  key={asset.path}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden shadow-sm"
                >
                  <a href={toAbsoluteMediaUrl(asset.url)} target="_blank" rel="noreferrer">
                    <img
                      src={toAbsoluteMediaUrl(asset.url)}
                      alt={asset.path}
                      className="w-full h-40 object-cover bg-gray-100 dark:bg-gray-700"
                      loading="lazy"
                    />
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
              ))}
            </div>
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
