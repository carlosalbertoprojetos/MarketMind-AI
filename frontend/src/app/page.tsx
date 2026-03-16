import CampaignBoard from "@/components/CampaignBoard";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <section className="card p-8 fade-in">
        <p className="text-sm uppercase tracking-[0.2em] text-moss">Content Intelligence OS</p>
        <h1 className="section-title mt-3 text-3xl font-semibold">
          Dashboard de Inteligencia Autonoma
        </h1>
        <p className="mt-3 text-base text-gray-600">
          Visao geral das campanhas, performance e operacoes da plataforma MarketMind-IA.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {[
          { label: "Campanhas ativas", value: "8", helper: "+2 esta semana" },
          { label: "Conteudos publicados", value: "124", helper: "CTR medio 4.2%" },
          { label: "Receita atribuida", value: "R$ 214k", helper: "Ultimos 30 dias" }
        ].map((item) => (
          <div key={item.label} className="card p-6 fade-in">
            <p className="text-sm text-gray-500">{item.label}</p>
            <p className="section-title mt-3 text-2xl font-semibold text-ink">{item.value}</p>
            <p className="mt-2 text-sm text-gray-500">{item.helper}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <CampaignBoard />
        <div className="card p-6 fade-in">
          <h2 className="section-title text-xl font-semibold">AI Insights</h2>
          <div className="mt-4 space-y-4 text-sm text-gray-600">
            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
              Melhor janela para LinkedIn: 09:30 - 11:00 (alta conversao).
            </div>
            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
              Narrativa com prova social gerou +18% de CTR nesta semana.
            </div>
            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
              Priorize carrossel educativo para leads de alto LTV.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
