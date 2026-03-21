/**
 * Cliente HTTP para a API MarketingAI.
 * Base URL: /api quando usando proxy do Vite (dev) ou variavel VITE_API_URL.
 */
export const BASE = import.meta.env.VITE_API_URL || '/api'
export const AUTH_EXPIRED_EVENT = 'marketingai:auth-expired'

let authExpiryNoticeDispatched = false

function readStoredToken() {
  try {
    return localStorage.getItem('token')
  } catch {
    return null
  }
}

function clearStoredToken() {
  try {
    localStorage.removeItem('token')
  } catch {
    // noop
  }
}

export function markAuthSessionActive() {
  authExpiryNoticeDispatched = false
}

function getToken() {
  return readStoredToken()
}

function getHeaders(includeAuth = true, extraHeaders = {}) {
  const headers = { 'Content-Type': 'application/json', ...extraHeaders }
  if (includeAuth) {
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }
  return headers
}

async function parseErrorResponse(res) {
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    const data = await res.json().catch(() => ({}))
    return data.detail || data.message || ''
  }
  const text = await res.text().catch(() => '')
  return text.trim()
}

function dispatchAuthExpired(detail) {
  if (authExpiryNoticeDispatched || typeof window === 'undefined') return
  authExpiryNoticeDispatched = true
  window.dispatchEvent(
    new CustomEvent(AUTH_EXPIRED_EVENT, {
      detail: {
        message: detail || 'Sessao expirada. Faca login novamente.',
      },
    }),
  )
}

async function ensureOk(res, fallbackMessage, authAware = true) {
  if (res.ok) return res

  const detail = (await parseErrorResponse(res)) || fallbackMessage
  if (authAware && res.status === 401) {
    clearStoredToken()
    dispatchAuthExpired(detail)
  }

  throw new Error(detail || fallbackMessage)
}

async function requestJson(path, options = {}, { auth = true, fallbackMessage = 'Erro na requisicao' } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: getHeaders(auth, options.headers),
  })
  await ensureOk(res, fallbackMessage, auth)
  return res.json()
}

async function requestVoid(path, options = {}, { auth = true, fallbackMessage = 'Erro na requisicao' } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: getHeaders(auth, options.headers),
  })
  await ensureOk(res, fallbackMessage, auth)
}

async function requestBlob(path, options = {}, { auth = true, fallbackMessage = 'Erro na requisicao' } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: getHeaders(auth, options.headers),
  })
  await ensureOk(res, fallbackMessage, auth)
  return res.blob()
}

function downloadBlob(blob, filename) {
  const objectUrl = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = objectUrl
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(objectUrl)
}

export async function register(email, password) {
  return requestJson('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, {
    auth: false,
    fallbackMessage: 'Erro ao registrar',
  })
}

export async function login(email, password) {
  const data = await requestJson('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, {
    auth: false,
    fallbackMessage: 'Email ou senha incorretos',
  })
  markAuthSessionActive()
  return data
}

/** Lista campanhas paginadas. Retorna { items, total, limit, offset }. */
export async function getCampaigns(limit = 50, offset = 0, filters = {}) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
  if (filters.platform != null && filters.platform !== '') params.set('platform', String(filters.platform))
  if (filters.search != null && String(filters.search).trim() !== '') params.set('search', String(filters.search).trim())
  if (filters.sort != null && filters.sort !== '') params.set('sort', String(filters.sort))
  return requestJson(`/user/campaigns?${params}`, {}, { fallbackMessage: 'Falha ao carregar campanhas' })
}

/** Resumo do dashboard: total, por plataforma, proximas 24h. */
export async function getSummary() {
  return requestJson('/user/summary', {}, { fallbackMessage: 'Falha ao carregar resumo' })
}

export async function createCampaign(data) {
  return requestJson('/campaign', {
    method: 'POST',
    body: JSON.stringify(data),
  }, {
    fallbackMessage: 'Erro ao criar campanha',
  })
}

export async function getCampaign(id) {
  return requestJson(`/campaign/${id}`, {}, { fallbackMessage: 'Campanha nao encontrada' })
}

export async function updateCampaign(id, data) {
  return requestJson(`/campaign/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }, {
    fallbackMessage: 'Erro ao atualizar campanha',
  })
}

export async function deleteCampaign(id) {
  return requestVoid(`/campaign/${id}`, {
    method: 'DELETE',
  }, {
    fallbackMessage: 'Erro ao remover campanha',
  })
}

/** Gera pre-visualizacao de posts a partir da URL. */
export async function previewFromUrl(url, campaignTitle, platforms = ['instagram', 'facebook', 'linkedin'], opts = {}) {
  const body = {
    url,
    campaign_title: campaignTitle,
    platforms,
    target_platform: opts.targetPlatform ?? null,
    objective: opts.objective ?? 'branding',
    max_crawl_pages: opts.maxCrawlPages ?? 5,
    max_crawl_depth: opts.maxCrawlDepth ?? 2,
    credentials_id: opts.credentialsId ?? null,
    login_url: opts.loginUrl ?? null,
    login_username: opts.loginUsername ?? null,
    login_password: opts.loginPassword ?? null,
  }
  return requestJson('/campaign/preview', {
    method: 'POST',
    body: JSON.stringify(body),
  }, {
    fallbackMessage: 'Erro ao gerar preview',
  })
}

export async function getCredentials() {
  return requestJson('/credentials', {}, { fallbackMessage: 'Falha ao carregar credenciais' })
}

export async function createCredentials(siteName, loginUrl, username, password) {
  return requestJson('/credentials', {
    method: 'POST',
    body: JSON.stringify({
      site_name: siteName,
      login_url: loginUrl || null,
      username: username || null,
      password: password || null,
    }),
  }, {
    fallbackMessage: 'Erro ao salvar credencial',
  })
}

export async function deleteCredentials(id) {
  return requestVoid(`/credentials/${id}`, {
    method: 'DELETE',
  }, {
    fallbackMessage: 'Erro ao remover credencial',
  })
}

/** Gera e baixa o pacote ZIP (imagens + textos por plataforma). */
export async function exportCampaignZip(url, campaignTitle, platforms = ['instagram', 'facebook', 'linkedin'], opts = {}) {
  const body = {
    url,
    campaign_title: campaignTitle,
    platforms,
    target_platform: opts.targetPlatform ?? null,
    objective: opts.objective ?? 'branding',
    max_crawl_pages: opts.maxCrawlPages ?? 5,
    max_crawl_depth: opts.maxCrawlDepth ?? 2,
    credentials_id: opts.credentialsId ?? null,
    login_url: opts.loginUrl ?? null,
    login_username: opts.loginUsername ?? null,
    login_password: opts.loginPassword ?? null,
  }
  const blob = await requestBlob('/campaign/export', {
    method: 'POST',
    body: JSON.stringify(body),
  }, {
    fallbackMessage: 'Erro ao gerar pacote',
  })
  downloadBlob(blob, 'marketingai-pacote.zip')
}

export async function runAutonomousPipeline(url, campaignTitle, targetPlatform, opts = {}) {
  const body = {
    url,
    campaign_title: campaignTitle,
    platforms: [targetPlatform],
    target_platform: targetPlatform,
    objective: opts.objective ?? 'branding',
    max_crawl_pages: opts.maxCrawlPages ?? 5,
    max_crawl_depth: opts.maxCrawlDepth ?? 2,
    credentials_id: opts.credentialsId ?? null,
    login_url: opts.loginUrl ?? null,
    login_username: opts.loginUsername ?? null,
    login_password: opts.loginPassword ?? null,
  }
  return requestJson('/campaign/orchestrate', {
    method: 'POST',
    body: JSON.stringify(body),
  }, {
    fallbackMessage: 'Erro ao executar pipeline autonomo',
  })
}

export async function runMultiAgentPipeline(url, campaignTitle, targetPlatform, opts = {}) {
  const body = {
    url,
    campaign_title: campaignTitle,
    platforms: [targetPlatform],
    target_platform: targetPlatform,
    objective: opts.objective ?? 'branding',
    max_crawl_pages: opts.maxCrawlPages ?? 5,
    max_crawl_depth: opts.maxCrawlDepth ?? 2,
    credentials_id: opts.credentialsId ?? null,
    login_url: opts.loginUrl ?? null,
    login_username: opts.loginUsername ?? null,
    login_password: opts.loginPassword ?? null,
  }
  return requestJson('/campaign/multi-agent', {
    method: 'POST',
    body: JSON.stringify(body),
  }, {
    fallbackMessage: 'Erro ao executar pipeline multi-agente',
  })
}

/** Gera posts de uma campanha usando a URL salva nela. */
export async function generateCampaignFromSavedUrl(campaignId) {
  return requestJson(`/campaign/${campaignId}/generate`, {
    method: 'POST',
  }, {
    fallbackMessage: 'Erro ao gerar posts da campanha',
  })
}

/** Lista ativos de midia gerados de uma campanha. */
export async function getCampaignAssets(campaignId, filters = {}) {
  const params = new URLSearchParams()
  if (filters.kind) params.set('kind', filters.kind)
  if (filters.platform) params.set('platform', filters.platform)
  if (filters.generatedFrom) params.set('generated_from', filters.generatedFrom)
  if (filters.generatedTo) params.set('generated_to', filters.generatedTo)
  const qs = params.toString()
  return requestJson(`/campaign/${campaignId}/assets${qs ? `?${qs}` : ''}`, {}, {
    fallbackMessage: 'Erro ao carregar ativos da campanha',
  })
}

/** Lista historico de geracoes da campanha. */
export async function getCampaignGenerations(campaignId) {
  return requestJson(`/campaign/${campaignId}/generations`, {}, {
    fallbackMessage: 'Erro ao carregar historico da campanha',
  })
}

/** Baixa ZIP com os ativos filtrados da campanha. */
export async function exportCampaignAssetsZip(campaignId, filters = {}) {
  const params = new URLSearchParams()
  if (filters.kind) params.set('kind', filters.kind)
  if (filters.platform) params.set('platform', filters.platform)
  if (filters.generatedFrom) params.set('generated_from', filters.generatedFrom)
  if (filters.generatedTo) params.set('generated_to', filters.generatedTo)
  const qs = params.toString()
  const blob = await requestBlob(`/campaign/${campaignId}/assets/export${qs ? `?${qs}` : ''}`, {}, {
    fallbackMessage: 'Erro ao exportar ativos',
  })
  downloadBlob(blob, 'marketingai-assets-filtrados.zip')
}

/** Baixa ZIP com ativos selecionados manualmente da campanha. */
export async function exportSelectedCampaignAssetsZip(campaignId, paths = []) {
  const blob = await requestBlob(`/campaign/${campaignId}/assets/export-selected`, {
    method: 'POST',
    body: JSON.stringify({ paths }),
  }, {
    fallbackMessage: 'Erro ao exportar ativos selecionados',
  })
  downloadBlob(blob, 'marketingai-assets-selecionados.zip')
}

