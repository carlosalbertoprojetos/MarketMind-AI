import { useState, useEffect } from 'react'
import { getCredentials, createCredentials, deleteCredentials } from '../api/client'
import Navbar from '../components/Navbar'
import { useToast } from '../context/ToastContext'

export default function CredentialsPage() {
  const { addToast } = useToast()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [siteName, setSiteName] = useState('')
  const [loginUrl, setLoginUrl] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitLoading, setSubmitLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getCredentials()
      setList(data ?? [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!siteName.trim()) {
      setError('Informe o nome do site.')
      return
    }
    setError('')
    setSubmitLoading(true)
    try {
      const c = await createCredentials(
        siteName.trim(),
        loginUrl.trim() || undefined,
        username.trim() || undefined,
        password || undefined
      )
      setList((prev) => [...prev, c])
      setSiteName('')
      setLoginUrl('')
      setUsername('')
      setPassword('')
      addToast('Credencial salva.')
    } catch (err) {
      const msg = err.message || 'Erro ao salvar credencial'
      setError(msg)
      addToast(msg, 'error')
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleDelete = async (cred) => {
    if (!window.confirm(`Remover a credencial "${cred.site_name}"?`)) return
    try {
      await deleteCredentials(cred.id)
      setList((prev) => prev.filter((c) => c.id !== cred.id))
      addToast('Credencial removida.')
    } catch (err) {
      const msg = err.message || 'Erro ao remover'
      setError(msg)
      addToast(msg, 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Credenciais</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Salve credenciais de login para usar em pré-visualizações e exportação de campanhas (sites que exigem login).
        </p>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Nova credencial</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Nome do site *</label>
              <input
                type="text"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                placeholder="Ex: Meu Portal"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">URL de login</label>
              <input
                type="url"
                value={loginUrl}
                onChange={(e) => setLoginUrl(e.target.value)}
                placeholder="https://..."
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Usuário</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Opcional"
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Senha</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Opcional"
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={submitLoading}
              className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50"
            >
              {submitLoading ? 'Salvando…' : 'Salvar credencial'}
            </button>
          </form>
        </div>

        {error && (
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        )}

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white p-4 border-b border-gray-200 dark:border-gray-700">Credenciais salvas</h2>
          {loading ? (
            <p className="p-6 text-gray-500 dark:text-gray-400">Carregando…</p>
          ) : list.length === 0 ? (
            <p className="p-6 text-gray-500 dark:text-gray-400">Nenhuma credencial. Adicione uma acima para usar em pré-visualizações e exportação.</p>
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {list.map((c) => (
                <li key={c.id} className="flex items-center justify-between gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-gray-900 dark:text-white truncate">{c.site_name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{c.login_url || '—'}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-300 mt-0.5">
                      {c.has_username && 'Usuário · '}
                      {c.has_password && 'Senha'}
                      {!c.has_username && !c.has_password && '—'}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDelete(c)}
                    className="shrink-0 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 text-sm font-medium"
                  >
                    Excluir
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
