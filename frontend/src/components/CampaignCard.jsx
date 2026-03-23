import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { buildPrefetchHandlers } from '../utils/routePrefetch'

function getCampaignPlatforms(campaign) {
  if (Array.isArray(campaign?.platforms) && campaign.platforms.length > 0) return campaign.platforms
  return campaign?.platform ? [campaign.platform] : []
}

/**
 * Card de campanha para listagem no dashboard. Clique leva à página de detalhe.
 */
export default function CampaignCard({ campaign, onDelete, onDuplicate }) {
  const scheduleStr = campaign.schedule
    ? format(new Date(campaign.schedule), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
    : 'Não agendada'
  const platforms = getCampaignPlatforms(campaign)
  const detailPrefetchProps = buildPrefetchHandlers(['campaignDetail', 'campaignPreview'])

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 shadow-sm hover:border-primary-500 dark:hover:border-primary-500 hover:shadow transition flex flex-col">
      <Link to={`/campaign/${campaign.id}`} {...detailPrefetchProps} className="flex-1 block text-left">
        <h3 className="font-medium text-gray-900 dark:text-white">{campaign.title}</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{campaign.content || '—'}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
          {platforms.length > 0 ? platforms.map((item) => (
            <span key={item} className="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">{item}</span>
          )) : null}
          <span>{scheduleStr}</span>
        </div>
      </Link>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {onDuplicate && (
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); onDuplicate(campaign); }}
            className="text-xs text-primary-600 dark:text-primary-400 hover:underline"
          >
            Duplicar
          </button>
        )}
        {onDelete && (
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); onDelete(campaign); }}
            className="text-xs text-red-600 dark:text-red-400 hover:underline"
          >
            Excluir
          </button>
        )}
      </div>
    </div>
  )
}
