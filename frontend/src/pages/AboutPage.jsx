import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Sobre o MarketingAI</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Sistema SaaS de geração automática de campanhas de marketing a partir de qualquer URL, pronto para múltiplas redes sociais.
        </p>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">O que o MarketingAI faz</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
            <li>Pré-visualização de posts a partir de uma URL (scraping + IA)</li>
            <li>Adaptação de texto e imagens por rede (Instagram, Facebook, LinkedIn, Twitter, TikTok)</li>
            <li>Calendário de campanhas com agendamento e lembretes</li>
            <li>Exportação em ZIP com imagens e legendas por plataforma</li>
            <li>Credenciais salvas para sites que exigem login</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Tecnologias</h2>
          <p className="text-gray-700 dark:text-gray-300 text-sm">
            Backend FastAPI, frontend React (Vite + TailwindCSS), pipeline de IA com scraping (Playwright), NLP e geração de imagens. Autenticação JWT, rate limiting e testes automatizados (pytest + Vitest).
          </p>
        </section>

        <p className="text-sm text-gray-500 dark:text-gray-400">
          Projeto SocialOne / MarketMind AI.
        </p>

        <div className="mt-8">
          <Link to="/" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
            ← Voltar ao início
          </Link>
        </div>
      </main>
    </div>
  )
}
