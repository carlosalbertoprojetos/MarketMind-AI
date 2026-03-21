import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { getCampaign, deleteCampaign, createCampaign } from '../api/client'
import Navbar from '../components/Navbar'
import { useToast } from '../context/ToastContext'

/** Página de detalhe de uma campanha: título, conteúdo, plataforma, agendamento; ações Editar e Excluir. */
export default function CampaignDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [campaign, setCampaign] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [duplicating, setDuplicating] = useState(false)

  useEffect(() => {
    getCampaign(id)
      .then(setCampaign)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!window.confirm(`Excluir a campanha "${campaign?.title}"?`)) return
    try {
      await deleteCampaign(id)
      addToast('Campanha excluída.')
      navigate('/')
    } catch (e) {
      addToast(e.message || 'Erro ao excluir', 'error')
    }
  }

  const handleDuplicate = async () => {
    if (!campaign) return
    setDuplicating(true)
    try {
      const copy = await createCampaign({
        title: `${campaign.title} (cópia)`,
        content: campaign.content || null,
        platform: campaign.platform || null,
        schedule: null,
      })
      addToast('Campanha duplicada.')
      navigate(`/campaign/${copy.id}`)
    } catch (e) {
      addToast(e.message || 'Erro ao duplicar', 'error')
    } finally {
      setDuplicating(false)
    }
  }

  const scheduleStr = campaign?.schedule
    ? format(new Date(campaign.schedule), "EEEE, d 'de' MMMM 'de' yyyy 'às' HH:mm", { locale: ptBR })
    : null

  if (loading) return <div className="min-h-screen bg-gray-50 dark:bg-gray-900"><Navbar /><main className="max-w-2xl mx-auto p-6"><p className="text-gray-500 dark:text-gray-400">Carregando…</p></main></div>
  if (error || !campaign) return <div className="min-h-screen bg-gray-50 dark:bg-gray-900"><Navbar /><main className="max-w-2xl mx-auto p-6"><p className="text-red-600 dark:text-red-400">{error || 'Campanha não encontrada.'}</p><Link to="/" className="text-primary-600 dark:text-primary-400">Voltar ao dashboard</Link></main></div>

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-2xl mx-auto p-6">
        <div className="mb-4">
          <Link to="/" className="text-sm text-primary-600 dark:text-primary-400 hover:underline">← Voltar ao dashboard</Link>
        </div>
        <article className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-100 dark:border-gray-700">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{campaign.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              {campaign.platform && (
                <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{campaign.platform}</span>
              )}
              {scheduleStr && <span>Agendada: {scheduleStr}</span>}
            </div>
          </div>
          <div className="p-6">
            <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Conteúdo</h2>
            <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{campaign.content || '—'}</div>
          </div>
          <div className="p-6 bg-gray-50 dark:bg-gray-900/30 flex flex-wrap gap-3">
            <Link
              to="/campaign/new"
              state={{ editCampaign: campaign }}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
            >
              Editar
            </Link>
            <Link
              to={`/campaign/${campaign.id}/preview`}
              className="px-4 py-2 border border-primary-500 text-primary-600 dark:text-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20"
            >
              Ver posts gerados
            </Link>
            <button
              type="button"
              onClick={handleDuplicate}
              disabled={duplicating}
              className="px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              {duplicating ? 'Duplicando…' : 'Duplicar'}
            </button>
            <button
              type="button"
              onClick={handleDelete}
              className="px-4 py-2 border border-red-300 dark:border-red-900/50 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              Excluir
            </button>
          </div>
        </article>
      </main>
    </div>
  )
}
