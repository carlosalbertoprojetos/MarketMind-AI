const stages = [
  {
    title: "Awareness",
    color: "bg-ember/10",
    items: ["Manifesto de marca", "Serie de insights", "Video teaser"]
  },
  {
    title: "Education",
    color: "bg-moss/10",
    items: ["Carrossel didatico", "Aula rapida", "Checklist"]
  },
  {
    title: "Solution",
    color: "bg-amber-100",
    items: ["Case study", "Demo narrada", "Thread tecnica"]
  },
  {
    title: "Proof",
    color: "bg-slate-100",
    items: ["Depoimentos", "Metricas de resultado", "Press release"]
  },
  {
    title: "Conversion",
    color: "bg-emerald-100",
    items: ["Oferta limitada", "Email sequence", "CTA de agenda"]
  }
];

export default function CampaignBoard() {
  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">Campaign Board</h2>
        <button className="rounded-full bg-smoke px-4 py-2 text-xs font-semibold text-haze">
          Nova campanha
        </button>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-5">
        {stages.map((stage) => (
          <div key={stage.title} className={`rounded-2xl p-4 ${stage.color}`}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink">{stage.title}</h3>
              <span className="rounded-full bg-white/70 px-2 py-1 text-[10px] text-gray-500">
                {stage.items.length} itens
              </span>
            </div>
            <ul className="mt-3 space-y-2">
              {stage.items.map((item) => (
                <li key={item} className="rounded-xl bg-white/80 px-3 py-2 text-xs text-gray-600">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
