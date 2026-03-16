export default function AIGeneratorPage() {
  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">AI Generator</h1>
        <p className="mt-2 text-sm text-gray-600">
          Dispare geracoes por agente: produto, mercado, audiencia, narrativa e campanha.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        {[
          {
            title: "Product Agent",
            text: "Analisa URLs, landing pages e docs para extrair proposta de valor."
          },
          {
            title: "Market Agent",
            text: "Mapeia concorrentes e posicionamento competitivo em tempo real."
          },
          {
            title: "Audience Agent",
            text: "Gera personas com dores, objetivos e linguagem de comunicacao."
          },
          {
            title: "Narrative Agent",
            text: "Estrutura narrativas com problem, diagnosis, solution e CTA."
          }
        ].map((card) => (
          <div key={card.title} className="card p-6">
            <h2 className="section-title text-lg font-semibold">{card.title}</h2>
            <p className="mt-3 text-sm text-gray-600">{card.text}</p>
            <button className="mt-6 inline-flex items-center justify-center rounded-full bg-ember px-4 py-2 text-sm font-semibold text-white">
              Iniciar fluxo
            </button>
          </div>
        ))}
      </section>
    </div>
  );
}