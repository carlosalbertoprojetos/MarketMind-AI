import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { createCampaign, updateCampaign, previewFromUrl, getCredentials, createCredentials, deleteCredentials, exportCampaignZip } from '../api/client'
import Navbar from '../components/Navbar'
import PostPreviewCard from '../components/PostPreviewCard'
import { useToast } from '../context/ToastContext'

const PLATFORM_OPTIONS = [
  { value: 'instagram', label: 'Instagram' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'X' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'facebook', label: 'Facebook' },
]

const ALL_MARKETING_PLATFORMS = PLATFORM_OPTIONS.map((item) => item.value)

function getPlatformLabel(value) {
  return PLATFORM_OPTIONS.find((item) => item.value === value)?.label || value
}

function normalizePlatform(value) {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'x') return 'twitter'
  return normalized
}

function sanitizePlatforms(values) {
  const seen = new Set()
  return (values || [])
    .map((value) => normalizePlatform(value))
    .filter((value) => ALL_MARKETING_PLATFORMS.includes(value))
    .filter((value) => {
      if (seen.has(value)) return false
      seen.add(value)
      return true
    })
}

function getRequestedPlatforms(platforms) {
  const sanitized = sanitizePlatforms(platforms)
  return sanitized.length > 0 ? sanitized : ALL_MARKETING_PLATFORMS
}

function parseAdditionalUrls(value) {
  return Array.from(
    new Set(
      String(value || '')
        .split(/\r?\n/)
        .map((item) => item.trim())
        .filter((item) => /^https?:\/\//i.test(item)),
    ),
  )
}

function parseCampaignContent(rawContent) {
  const raw = String(rawContent ?? '').trim()
  if (!raw) {
    return { primaryUrl: '', additionalUrlsText: '', credentialId: '', platforms: [], notes: '' }
  }

  let body = raw
  let primaryUrl = ''
  const lines = body.split(/\r?\n/)
  if (lines[0] && /^URL:/i.test(lines[0].trim())) {
    primaryUrl = lines.shift().replace(/^URL:/i, '').trim()
    body = lines.join('\n').trim()
  }

  let additionalUrlsText = ''
  const additionalUrlsPattern = /(?:^|\n)ADDITIONAL_URLS:\s*\n([\s\S]*?)\nEND_ADDITIONAL_URLS(?:\n|$)/i
  const additionalUrlsMatch = body.match(additionalUrlsPattern)
  if (additionalUrlsMatch) {
    additionalUrlsText = parseAdditionalUrls(additionalUrlsMatch[1]).join('\n')
    body = body.replace(additionalUrlsPattern, '\n').replace(/\n{3,}/g, '\n\n').trim()
  }

  let platforms = []
  const platformsPattern = /(?:^|\n)PLATFORMS:\s*\n([\s\S]*?)\nEND_PLATFORMS(?:\n|$)/i
  const platformsMatch = body.match(platformsPattern)
  if (platformsMatch) {
    platforms = sanitizePlatforms(platformsMatch[1].split(/\r?\n/))
    body = body.replace(platformsPattern, '\n').replace(/\n{3,}/g, '\n\n').trim()
  }

  let credentialId = ''
  const credentialMatch = body.match(/(?:^|\n)CREDENTIALS_ID:\s*(\d+)(?:\n|$)/i)
  if (credentialMatch) {
    credentialId = credentialMatch[1]
    body = body.replace(/(?:^|\n)CREDENTIALS_ID:\s*\d+(?:\n|$)/i, '\n').replace(/\n{3,}/g, '\n\n').trim()
  }

  return {
    primaryUrl,
    additionalUrlsText,
    credentialId,
    platforms,
    notes: body,
  }
}

function serializeCampaignContent(rawNotes, primaryUrl, additionalUrlsValue, credentialIdValue, platformsValue) {
  const notes = String(rawNotes ?? '').trim()
  const urlValue = String(primaryUrl ?? '').trim()
  const additionalUrls = parseAdditionalUrls(additionalUrlsValue)
  const credentialId = String(credentialIdValue ?? '').trim()
  const platforms = sanitizePlatforms(platformsValue)
  const parts = []

  if (urlValue) {
    parts.push(`URL: ${urlValue}`)
  }

  if (additionalUrls.length > 0) {
    parts.push(`ADDITIONAL_URLS:\n${additionalUrls.join('\n')}\nEND_ADDITIONAL_URLS`)
  }

  if (platforms.length > 0) {
    parts.push(`PLATFORMS:\n${platforms.join('\n')}\nEND_PLATFORMS`)
  }

  if (credentialId) {
    parts.push(`CREDENTIALS_ID: ${credentialId}`)
  }

  if (notes) {
    parts.push(notes)
  }

  return parts.join('\n\n') || null
}

export default function CreateCampaign() {
  const navigate = useNavigate()
  const location = useLocation()
  const { addToast } = useToast()
  const editCampaign = location.state?.editCampaign
  const campaignId = editCampaign?.id ?? null
  const initialCampaignContent = parseCampaignContent(editCampaign?.content)
  const [url, setUrl] = useState(() => initialCampaignContent.primaryUrl)
  const [title, setTitle] = useState(editCampaign?.title ?? '')
  const [content, setContent] = useState(initialCampaignContent.notes)
  const [selectedPlatforms, setSelectedPlatforms] = useState(() => sanitizePlatforms(initialCampaignContent.platforms.length > 0 ? initialCampaignContent.platforms : [editCampaign?.platform]))
  const [platformDraft, setPlatformDraft] = useState('instagram')
  const [editingPlatformIndex, setEditingPlatformIndex] = useState(null)
  const [schedule, setSchedule] = useState(editCampaign?.schedule ? new Date(editCampaign.schedule).toISOString().slice(0, 16) : '')
  const [loginUrl, setLoginUrl] = useState('')
  const [loginUser, setLoginUser] = useState('')
  const [loginPass, setLoginPass] = useState('')
  const [additionalUrlsText, setAdditionalUrlsText] = useState(initialCampaignContent.additionalUrlsText)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [credentialsList, setCredentialsList] = useState([])
  const [selectedCredentialId, setSelectedCredentialId] = useState(() => initialCampaignContent.credentialId)
  const [showAddCred, setShowAddCred] = useState(false)
  const [newCredSite, setNewCredSite] = useState('')
  const [newCredUrl, setNewCredUrl] = useState('')
  const [newCredUser, setNewCredUser] = useState('')
  const [newCredPass, setNewCredPass] = useState('')
  const [exportLoading, setExportLoading] = useState(false)

  useEffect(() => {
    getCredentials().then(setCredentialsList).catch(() => {})
  }, [])

  const buildCollectionOptions = () => {
    const sourceUrls = parseAdditionalUrls(additionalUrlsText)
    const requestedPlatforms = getRequestedPlatforms(selectedPlatforms)
    const baseOptions = {
      sourceUrls,
      maxCrawlPages: Math.max(1, 1 + sourceUrls.length),
      maxCrawlDepth: 0,
      followInternalLinks: false,
      captureScrollSections: true,
      targetPlatform: requestedPlatforms.length === 1 ? requestedPlatforms[0] : undefined,
    }
    if (selectedCredentialId) {
      return { ...baseOptions, credentialsId: parseInt(selectedCredentialId, 10) }
    }
    return {
      ...baseOptions,
      loginUrl: loginUrl || undefined,
      loginUsername: loginUser || undefined,
      loginPassword: loginPass || undefined,
    }
  }

  const handleAddOrUpdatePlatform = () => {
    const normalized = normalizePlatform(platformDraft)
    if (!ALL_MARKETING_PLATFORMS.includes(normalized)) {
      setError('Selecione uma rede social valida.')
      return
    }

    setSelectedPlatforms((current) => {
      const next = [...current]
      if (editingPlatformIndex != null) {
        next[editingPlatformIndex] = normalized
      } else {
        next.push(normalized)
      }
      return sanitizePlatforms(next)
    })
    setPlatformDraft('instagram')
    setEditingPlatformIndex(null)
    setError('')
  }

  const handleEditPlatform = (index) => {
    setPlatformDraft(selectedPlatforms[index] || 'instagram')
    setEditingPlatformIndex(index)
  }

  const handleDeletePlatform = (index) => {
    setSelectedPlatforms((current) => current.filter((_, itemIndex) => itemIndex !== index))
    if (editingPlatformIndex === index) {
      setPlatformDraft('instagram')
      setEditingPlatformIndex(null)
    }
  }

  const handlePreview = async () => {
    if (!url.trim()) {
      setError('Informe a URL para gerar a pre-visualizacao.')
      return
    }
    setPreview(null)
    setError('')
    setPreviewLoading(true)
    try {
      const requestedPlatforms = getRequestedPlatforms(selectedPlatforms)
      const data = await previewFromUrl(url, title || url, requestedPlatforms, buildCollectionOptions())
      setPreview(data)
    } catch (err) {
      setError(err.message || 'Erro ao gerar preview')
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleAddCredential = async (e) => {
    e?.preventDefault?.()
    if (!newCredSite.trim()) return
    try {
      const c = await createCredentials(newCredSite, newCredUrl || undefined, newCredUser || undefined, newCredPass || undefined)
      setCredentialsList((prev) => [...prev, c])
      setShowAddCred(false)
      setNewCredSite('')
      setNewCredUrl('')
      setNewCredUser('')
      setNewCredPass('')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteCredential = async (id) => {
    if (!window.confirm('Remover esta credencial?')) return
    try {
      await deleteCredentials(id)
      setCredentialsList((prev) => prev.filter((c) => c.id !== id))
      if (selectedCredentialId === String(id)) setSelectedCredentialId('')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleExportZip = async () => {
    if (!url.trim()) {
      setError('Informe a URL para gerar o pacote.')
      return
    }
    setError('')
    setExportLoading(true)
    try {
      const requestedPlatforms = getRequestedPlatforms(selectedPlatforms)
      await exportCampaignZip(url, title || url, requestedPlatforms, buildCollectionOptions())
    } catch (err) {
      setError(err.message || 'Erro ao exportar')
    } finally {
      setExportLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let credentialIdToPersist = selectedCredentialId
      if (!credentialIdToPersist && (loginUrl.trim() || loginUser.trim() || loginPass.trim())) {
        const createdCredential = await createCredentials(
          title || url || 'Credencial da campanha',
          loginUrl || undefined,
          loginUser || undefined,
          loginPass || undefined,
        )
        credentialIdToPersist = String(createdCredential.id)
        setSelectedCredentialId(credentialIdToPersist)
        setCredentialsList((prev) => (prev.some((item) => item.id === createdCredential.id) ? prev : [...prev, createdCredential]))
      }

      const platformsToPersist = getRequestedPlatforms(selectedPlatforms)
      const mergedContent = serializeCampaignContent(content, url, additionalUrlsText, credentialIdToPersist, platformsToPersist)
      const payload = {
        title: title || (url ? `Campanha: ${url}` : 'Nova campanha'),
        content: mergedContent,
        platform: platformsToPersist[0] || null,
        schedule: schedule ? new Date(schedule).toISOString() : null,
      }
      if (campaignId) {
        await updateCampaign(campaignId, payload)
        addToast('Campanha atualizada.')
        navigate(`/campaign/${campaignId}`)
      } else {
        await createCampaign(payload)
        addToast('Campanha criada.')
        navigate('/')
      }
    } catch (err) {
      const msg = err.message || (campaignId ? 'Erro ao atualizar campanha' : 'Erro ao criar campanha')
      setError(msg)
      addToast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{campaignId ? 'Editar campanha' : 'Nova campanha'}</h1>
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-200">URL principal</label>
            <input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Informe aqui a primeira tela de negocio que deseja analisar. Nao use a tela de login como fonte de conteudo. O sistema coleta apenas esta pagina e as URLs adicionais informadas por voce.</p>
          </div>
          <div>
            <label htmlFor="additional-urls" className="block text-sm font-medium text-gray-700 dark:text-gray-200">URLs adicionais (uma por linha)</label>
            <textarea
              id="additional-urls"
              value={additionalUrlsText}
              onChange={(e) => setAdditionalUrlsText(e.target.value)}
              rows={4}
              placeholder={`https://site.com/precos\nhttps://site.com/produto`}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Use este campo quando quiser compilar varias telas especificas. Em landing pages longas, o sistema captura secoes rolando a propria pagina.</p>
          </div>
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Titulo da campanha</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Lancamento App X"
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Conteudo / notas</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
            <div>
              <p className="block text-sm font-medium text-gray-700 dark:text-gray-200">Redes sociais</p>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Adicione uma ou mais redes. Cada item pode ser editado ou removido antes de salvar a campanha.</p>
            </div>
            <div className="flex gap-2 flex-col sm:flex-row sm:items-end">
              <div className="flex-1">
                <label htmlFor="platform-draft" className="block text-xs font-medium text-gray-700 dark:text-gray-200">Rede social</label>
                <select
                  id="platform-draft"
                  value={platformDraft}
                  onChange={(e) => setPlatformDraft(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                >
                  {PLATFORM_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                onClick={handleAddOrUpdatePlatform}
                className="rounded-lg border border-primary-500 px-4 py-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950/30"
              >
                {editingPlatformIndex != null ? 'Salvar rede' : 'Adicionar rede'}
              </button>
            </div>
            <div className="space-y-2">
              {selectedPlatforms.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma rede selecionada. Se voce nao adicionar nenhuma, o sistema gera conteudo para todas as plataformas suportadas.</p>
              ) : selectedPlatforms.map((item, index) => (
                <div key={`${item}-${index}`} className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{getPlatformLabel(item)}</span>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => handleEditPlatform(index)} className="text-xs rounded border border-gray-300 dark:border-gray-600 px-2 py-1 text-gray-700 dark:text-gray-200">Editar</button>
                    <button type="button" onClick={() => handleDeletePlatform(index)} className="text-xs rounded border border-red-300 px-2 py-1 text-red-600 dark:border-red-700 dark:text-red-300">Excluir</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <label htmlFor="schedule" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Agendar para</label>
            <input
              id="schedule"
              type="datetime-local"
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <details className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-200">Credenciais e URL de login (opcional)</summary>
            <div className="mt-3 space-y-2">
              <div className="flex gap-2 items-center">
                <select
                  value={selectedCredentialId}
                  onChange={(e) => setSelectedCredentialId(e.target.value)}
                  className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 flex-1"
                >
                  <option value="">Usar credenciais manuais abaixo</option>
                  {credentialsList.map((c) => (
                    <option key={c.id} value={c.id}>{c.site_name} ({c.login_url})</option>
                  ))}
                </select>
                <button type="button" onClick={() => setShowAddCred(true)} className="text-sm text-primary-600 dark:text-primary-400">+ Nova</button>
              </div>
              {credentialsList.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {credentialsList.map((c) => (
                    <button key={c.id} type="button" onClick={() => handleDeleteCredential(c.id)} className="text-xs text-red-600 dark:text-red-400 underline">
                      Remover {c.site_name}
                    </button>
                  ))}
                </div>
              )}
              {showAddCred && (
                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded space-y-3 border border-gray-200 dark:border-gray-700">
                  <div>
                    <label htmlFor="new-cred-site" className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">Nome</label>
                    <input id="new-cred-site" type="text" value={newCredSite} onChange={(e) => setNewCredSite(e.target.value)} placeholder="Nome (ex: Meu Site)" className="block w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-sm text-gray-900 dark:text-gray-100" required />
                  </div>
                  <div>
                    <label htmlFor="new-cred-url" className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">URL de login</label>
                    <input id="new-cred-url" type="url" value={newCredUrl} onChange={(e) => setNewCredUrl(e.target.value)} placeholder="URL de login" className="block w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-sm text-gray-900 dark:text-gray-100" />
                  </div>
                  <div>
                    <label htmlFor="new-cred-user" className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">Usuario</label>
                    <input id="new-cred-user" type="text" value={newCredUser} onChange={(e) => setNewCredUser(e.target.value)} placeholder="Usuario" className="block w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-sm text-gray-900 dark:text-gray-100" />
                  </div>
                  <div>
                    <label htmlFor="new-cred-pass" className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">Senha</label>
                    <input id="new-cred-pass" type="password" value={newCredPass} onChange={(e) => setNewCredPass(e.target.value)} placeholder="Senha" className="block w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-sm text-gray-900 dark:text-gray-100" />
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={handleAddCredential} className="bg-primary-500 text-white px-2 py-1 rounded text-sm">Salvar</button>
                    <button type="button" onClick={() => setShowAddCred(false)} className="border border-gray-300 dark:border-gray-600 px-2 py-1 rounded text-sm text-gray-700 dark:text-gray-200">Cancelar</button>
                  </div>
                </div>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400">Ou digite manualmente. A URL de login serve apenas para autenticacao; a coleta usa a URL principal e as URLs adicionais.</p>
              <input type="url" value={loginUrl} onChange={(e) => setLoginUrl(e.target.value)} placeholder="URL de login (ex: /acessar/)" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
              <input type="text" value={loginUser} onChange={(e) => setLoginUser(e.target.value)} placeholder="Usuario" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
              <input type="password" value={loginPass} onChange={(e) => setLoginPass(e.target.value)} placeholder="Senha" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
            </div>
          </details>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <div className="rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-900 dark:border-sky-900/50 dark:bg-sky-950/30 dark:text-sky-100">
            O modo atual coleta apenas as telas explicitamente informadas. Se a URL principal for uma landing page longa, o sistema rola a pagina e captura secoes e imagens da mesma tela.
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              type="button"
              onClick={handlePreview}
              disabled={previewLoading || !url.trim()}
              className="border border-primary-500 text-primary-600 dark:text-primary-400 px-4 py-2 rounded-lg hover:bg-primary-50 disabled:opacity-50"
            >
              {previewLoading ? 'Gerando...' : 'Pre-visualizar posts'}
            </button>
            <button
              type="button"
              onClick={handleExportZip}
              disabled={exportLoading || !url.trim()}
              className="border border-gray-300 dark:border-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 dark:hover:bg-gray-800"
            >
              {exportLoading ? 'Gerando ZIP...' : 'Baixar pacote (ZIP)'}
            </button>
          </div>
          {preview && (
            <div className="mt-4 space-y-4">
              <h2 className="font-semibold text-gray-900 dark:text-white">Pre-visualizacao por rede</h2>
              {preview.error && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/30 p-3 text-sm text-amber-900 dark:text-amber-100">
                  <strong>Pipeline:</strong> {preview.error}
                </div>
              )}
              {!preview.error && (!preview.posts || preview.posts.length === 0) && (
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Nenhum post foi retornado. Verifique o aviso acima ou os logs do backend.
                </p>
              )}
              <div className="grid gap-4 sm:grid-cols-2">
                {preview.posts?.map((post, i) => (
                  <PostPreviewCard key={`${post.platform}-${i}-${post.source_page_url || ''}`} post={post} />
                ))}
              </div>
            </div>
          )}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50"
            >
              {loading ? (campaignId ? 'Salvando...' : 'Criando...') : (campaignId ? 'Salvar' : 'Criar campanha')}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="border border-gray-300 dark:border-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Cancelar
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
