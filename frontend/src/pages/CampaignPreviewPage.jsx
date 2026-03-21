import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import PostPreviewCard from '../components/PostPreviewCard'
import { generateCampaignFromSavedUrl } from '../api/client'
import { useToast } from '../context/ToastContext'

export default function CampaignPreviewPage() {
  const { id } = useParams()
  const { addToast } = useToast()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)

  const runGeneration = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await generateCampaignFromSavedUrl(id)
      setPreview(data)
      if (data.error) addToast(data.error, 'error')
      else addToast('Posts gerados com base na URL da campanha.')
    } catch (e) {
      const msg = e.message || 'Erro ao gerar preview da campanha'
      setError(msg)
      addToast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runGeneration()
  }, [id])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-5xl mx-auto p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Posts gerados da campanha</h1>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={runGeneration}
              disabled={loading}
              className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50"
            >
              {loading ? 'Gerando...' : 'Gerar novamente'}
            </button>
            <Link
              to={`/campaign/${id}`}
              className="border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Voltar
            </Link>
          </div>
        </div>

        {loading ? (
          <p className="text-gray-500 dark:text-gray-400">Processando URL e gerando conteúdo...</p>
        ) : error ? (
          <p className="text-red-600 dark:text-red-400">{error}</p>
        ) : !preview ? (
          <p className="text-gray-500 dark:text-gray-400">Nenhum resultado de geração.</p>
        ) : (
          <>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 break-all">
              URL base: {preview.url || '-'}
            </p>
            {preview.error && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/30 p-3 text-sm text-amber-900 dark:text-amber-100 mb-4">
                <strong>Erro:</strong> {preview.error}
              </div>
            )}
            {!preview.error && (!preview.posts || preview.posts.length === 0) && (
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Nenhum post retornado. Gere novamente ou confira a URL salva na campanha e o backend (Playwright / pipeline).
              </p>
            )}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {preview.posts?.map((post, i) => (
                <PostPreviewCard key={`${post.platform}-${i}-${post.source_page_url || ''}`} post={post} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
