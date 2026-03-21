import { useState, useEffect, useRef } from 'react'
import { BASE } from '../api/client'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  const headers = {}
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

export default function PostPreviewCard({ post }) {
  const [imageBlobUrls, setImageBlobUrls] = useState([])
  const [imagePreviewNote, setImagePreviewNote] = useState(null)
  const blobUrlsRef = useRef([])

  useEffect(() => {
    if (!post.image_urls?.length) {
      setImageBlobUrls([])
      setImagePreviewNote(
        post.image_paths?.length
          ? 'As imagens foram geradas, mas o link de pre-visualizacao nao esta disponivel. Use exportar ativos ou gere novamente.'
          : 'Nenhuma imagem foi gerada. Verifique capturas do site, OPENAI_API_KEY e MARKETINGAI_IMAGE_SOURCE.'
      )
      return
    }

    setImagePreviewNote(null)
    const urls = post.image_urls.map((url) => `${BASE}/${url}`)
    let cancelled = false

    Promise.all(
      urls.map((url) => fetch(url, { headers: getAuthHeaders() }).then((response) => (response.ok ? response.blob() : null)))
    ).then((blobs) => {
      if (cancelled) return
      blobUrlsRef.current.forEach((url) => URL.revokeObjectURL(url))
      const nextBlobUrls = blobs.filter(Boolean).map((blob) => URL.createObjectURL(blob))
      blobUrlsRef.current = nextBlobUrls
      setImageBlobUrls(nextBlobUrls)
      if (nextBlobUrls.length === 0 && post.image_urls?.length) {
        setImagePreviewNote('Nao foi possivel carregar a pre-visualizacao. Confira a sessao e gere novamente.')
      }
    })

    return () => {
      cancelled = true
      blobUrlsRef.current.forEach((url) => URL.revokeObjectURL(url))
      blobUrlsRef.current = []
    }
  }, [post.image_urls?.join(','), post.image_paths?.join(',')])

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      {(post.screen_label || post.screen_type) && (
        <div className="mb-2 flex flex-wrap gap-2">
          {post.screen_label ? (
            <span className="rounded-full bg-primary-50 px-2 py-1 text-xs font-medium text-primary-700 dark:bg-primary-950/40 dark:text-primary-300">
              {post.screen_label}
            </span>
          ) : null}
          {post.screen_type ? (
            <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-200">
              {post.screen_type}
            </span>
          ) : null}
        </div>
      )}

      {(post.source_page_url || post.page_title) && (
        <p className="mb-1 break-all text-xs text-gray-500 dark:text-gray-400">
          {post.page_title ? (
            <span className="font-medium text-gray-600 dark:text-gray-300">{post.page_title} · </span>
          ) : null}
          {post.source_page_url ? <span>{post.source_page_url}</span> : null}
        </p>
      )}

      <div className="mb-2 flex items-center justify-between">
        <span className="rounded bg-gray-100 px-2 py-1 text-sm font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-200">
          {post.platform}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Horarios sugeridos: {post.suggested_times?.join(', ')}
        </span>
      </div>

      <h3 className="font-medium text-gray-900 dark:text-white">{post.title || '-'}</h3>
      {post.strategy_summary ? (
        <p className="mt-2 text-xs text-gray-600 dark:text-gray-300">
          Estrategia: {post.strategy_summary}
        </p>
      ) : null}

      {imageBlobUrls.length > 0 ? (
        <div className="mt-2 flex flex-wrap gap-2">
          {imageBlobUrls.map((src, index) => (
            <img key={index} src={src} alt="" className="h-24 w-auto rounded object-cover" />
          ))}
        </div>
      ) : (
        imagePreviewNote && (
          <p className="mt-2 rounded border border-amber-200 bg-amber-50 px-2 py-1.5 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100">
            {imagePreviewNote}
          </p>
        )
      )}

      <div className="mt-3 rounded-lg border border-gray-100 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/60">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Legenda / texto da postagem
        </p>
        <p className="mt-1 whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
          {(post.text || '').trim() || (
            <span className="text-amber-700 dark:text-amber-300">
              Sem corpo de legenda neste post. Gere novamente ou confira o texto capturado do site.
            </span>
          )}
        </p>
        {post.hashtags?.length > 0 && (
          <p className="mt-2 text-xs font-medium text-primary-600 dark:text-primary-400">
            {post.hashtags.join(' ')}
          </p>
        )}
      </div>

      {post.steps?.length > 0 && (
        <details className="mt-3">
          <summary className="cursor-pointer text-sm font-medium text-primary-600 dark:text-primary-400">
            Passo a passo para publicar
          </summary>
          <ol className="mt-2 list-inside list-decimal space-y-1 text-sm text-gray-600 dark:text-gray-300">
            {post.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </details>
      )}
    </div>
  )
}
