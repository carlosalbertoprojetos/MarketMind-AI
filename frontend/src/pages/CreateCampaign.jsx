import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { createCampaign, updateCampaign, previewFromUrl, getCredentials, createCredentials, deleteCredentials, exportCampaignZip } from '../api/client'
import Navbar from '../components/Navbar'
import PostPreviewCard from '../components/PostPreviewCard'
import { useToast } from '../context/ToastContext'

const ALL_MARKETING_PLATFORMS = ['instagram', 'facebook', 'linkedin', 'twitter', 'tiktok']

function getRequestedPlatforms(platform) {
  const normalized = String(platform || '').trim().toLowerCase()
  return normalized ? [normalized] : ALL_MARKETING_PLATFORMS
}


function parseUrlFromContent(content) {
  if (!content) return ''
  const s = String(content).trim()
  // Formato original usado no app: `URL: https://...`
  if (s.toUpperCase().startsWith('URL:')) return s.slice(4).trim()
  // Caso o backend/registro tenha guardado só a URL sem prefixo
  if (/^https?:\/\//i.test(s)) return s
  // Caso venha dentro de texto: "... URL: https://..."
  const m = s.match(/URL:\s*(\S+)/i)
  if (m?.[1]) return m[1]
  return ''
}

/**
 * Monta o texto salvo em `content` garantindo que a URL do campo dedicado fique persistida.
 * Evita perder a URL quando o usuário também preenche "Conteúdo / notas" (antes `content || url` ignorava a URL).
 */
function mergeUrlIntoPersistedContent(rawContent, urlFieldValue) {
  const u = String(urlFieldValue ?? '').trim()
  let body = String(rawContent ?? '').trim()

  if (body) {
    const lines = body.split(/\r?\n/)
    body = lines
      .filter((line) => {
        const t = line.trim()
        if (!t) return true
        if (/^URL:/i.test(t)) return false
        if (/^https?:\/\//i.test(t)) return false
        return true
      })
      .join('\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim()
  }

  if (!u) {
    return body || null
  }
  return body ? `URL: ${u}\n\n${body}` : `URL: ${u}`
}

/**
 * Formulário para criar ou editar campanha. Em edição (state.editCampaign), preenche e envia PATCH.
 */
export default function CreateCampaign() {
  const navigate = useNavigate()
  const location = useLocation()
  const { addToast } = useToast()
  const editCampaign = location.state?.editCampaign
  const [campaignId, setCampaignId] = useState(editCampaign?.id ?? null)
  const [url, setUrl] = useState(() => parseUrlFromContent(editCampaign?.content))
  const [title, setTitle] = useState(editCampaign?.title ?? '')
  const [content, setContent] = useState(editCampaign?.content ?? '')
  const [platform, setPlatform] = useState(editCampaign?.platform ?? '')
  const [schedule, setSchedule] = useState(editCampaign?.schedule ? new Date(editCampaign.schedule).toISOString().slice(0, 16) : '')
  const [loginUrl, setLoginUrl] = useState('')
  const [loginUser, setLoginUser] = useState('')
  const [loginPass, setLoginPass] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [credentialsList, setCredentialsList] = useState([])
  const [selectedCredentialId, setSelectedCredentialId] = useState('')
  const [showAddCred, setShowAddCred] = useState(false)
  const [newCredSite, setNewCredSite] = useState('')
  const [newCredUrl, setNewCredUrl] = useState('')
  const [newCredUser, setNewCredUser] = useState('')
  const [newCredPass, setNewCredPass] = useState('')
  const [exportLoading, setExportLoading] = useState(false)
  const [maxCrawlPages, setMaxCrawlPages] = useState(5)

  useEffect(() => {
    getCredentials().then(setCredentialsList).catch(() => {})
  }, [])

  const handlePreview = async () => {
    if (!url.trim()) { setError('Informe a URL para gerar a pré-visualização.'); return }
    setPreview(null)
    setError('')
    setPreviewLoading(true)
    try {
      const opts = selectedCredentialId
        ? { credentialsId: parseInt(selectedCredentialId, 10), maxCrawlPages, targetPlatform: platform || undefined }
        : { loginUrl: loginUrl || undefined, loginUsername: loginUser || undefined, loginPassword: loginPass || undefined, maxCrawlPages, targetPlatform: platform || undefined }
      const data = await previewFromUrl(url, title || url, getRequestedPlatforms(platform), opts)
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
      setNewCredSite(''); setNewCredUrl(''); setNewCredUser(''); setNewCredPass('')
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
    if (!url.trim()) { setError('Informe a URL para gerar o pacote.'); return }
    setError('')
    setExportLoading(true)
    try {
      const opts = selectedCredentialId
        ? { credentialsId: parseInt(selectedCredentialId, 10), maxCrawlPages, targetPlatform: platform || undefined }
        : { loginUrl: loginUrl || undefined, loginUsername: loginUser || undefined, loginPassword: loginPass || undefined, maxCrawlPages, targetPlatform: platform || undefined }
      await exportCampaignZip(url, title || url, getRequestedPlatforms(platform), opts)
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
    const mergedContent = mergeUrlIntoPersistedContent(content, url)
    const payload = {
      title: title || (url ? `Campanha: ${url}` : 'Nova campanha'),
      content: mergedContent,
      platform: platform || null,
      schedule: schedule ? new Date(schedule).toISOString() : null,
    }
    try {
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
      <main className="max-w-2xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{campaignId ? 'Editar campanha' : 'Nova campanha'}</h1>
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-200">URL do site/produto</label>
            <input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Opcional. Será usada para extrair conteúdo e gerar campanhas (Etapa 4+).</p>
          </div>
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Título da campanha</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Lançamento App X"
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Conteúdo / notas</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="platform" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Plataforma</label>
            <select
              id="platform"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Selecione</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="linkedin">LinkedIn</option>
              <option value="twitter">Twitter/X</option>
              <option value="tiktok">TikTok</option>
            </select>
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
            <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-200">Credenciais para login na URL (opcional)</summary>
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
                    <label htmlFor="new-cred-user" className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">Usu?rio</label>
                    <input id="new-cred-user" type="text" value={newCredUser} onChange={(e) => setNewCredUser(e.target.value)} placeholder="Usu?rio" className="block w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-2 py-1.5 text-sm text-gray-900 dark:text-gray-100" />
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
              <p className="text-xs text-gray-500 dark:text-gray-400">Ou digite manualmente (não salvo):</p>
              <input type="url" value={loginUrl} onChange={(e) => setLoginUrl(e.target.value)} placeholder="URL de login" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
              <input type="text" value={loginUser} onChange={(e) => setLoginUser(e.target.value)} placeholder="Usuário" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
              <input type="password" value={loginPass} onChange={(e) => setLoginPass(e.target.value)} placeholder="Senha" className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100" disabled={!!selectedCredentialId} />
            </div>
          </details>
          <div>
            <label htmlFor="maxCrawlPages" className="block text-sm font-medium text-gray-700 dark:text-gray-200">
              Páginas a visitar (links do mesmo site)
            </label>
            <input
              id="maxCrawlPages"
              type="number"
              min={1}
              max={20}
              value={maxCrawlPages}
              onChange={(e) => setMaxCrawlPages(Math.min(20, Math.max(1, parseInt(e.target.value, 10) || 1)))}
              className="mt-1 w-24 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-gray-100"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              O robô segue links internos e gera posts por página (mais páginas = mais tempo e mais créditos de IA se usar imagens DALL·E).
            </p>
          </div>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <div className="flex gap-2 flex-wrap">
            <button
              type="button"
              onClick={handlePreview}
              disabled={previewLoading || !url.trim()}
              className="border border-primary-500 text-primary-600 dark:text-primary-400 px-4 py-2 rounded-lg hover:bg-primary-50 disabled:opacity-50"
            >
              {previewLoading ? 'Gerando…' : 'Pré-visualizar posts'}
            </button>
            <button
              type="button"
              onClick={handleExportZip}
              disabled={exportLoading || !url.trim()}
              className="border border-gray-300 dark:border-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 dark:hover:bg-gray-800"
            >
              {exportLoading ? 'Gerando ZIP…' : 'Baixar pacote (ZIP)'}
            </button>
          </div>
          {preview && (
            <div className="mt-4 space-y-4">
              <h2 className="font-semibold text-gray-900 dark:text-white">Pré-visualização por rede</h2>
              {preview.error && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/30 p-3 text-sm text-amber-900 dark:text-amber-100">
                  <strong>Pipeline:</strong> {preview.error}
                  <p className="mt-1 text-xs opacity-90">
                    Dica: muitos sites falhavam com timeout no modo antigo; atualize o backend e tente de novo. Confira Playwright (<code className="bg-black/10 px-1 rounded">playwright install chromium</code>) e reinicie o uvicorn.
                  </p>
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
              {loading ? (campaignId ? 'Salvando…' : 'Criando…') : (campaignId ? 'Salvar' : 'Criar campanha')}
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
