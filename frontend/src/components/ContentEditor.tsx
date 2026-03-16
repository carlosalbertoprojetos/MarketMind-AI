const variants = [
  "Short",
  "Medium",
  "Long",
  "Technical",
  "Sales"
];

export default function ContentEditor() {
  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="section-title text-xl font-semibold">Content Editor</h2>
          <p className="mt-2 text-sm text-gray-600">Edite, derive e aprove versoes em um so lugar.</p>
        </div>
        <button className="rounded-full bg-ember px-4 py-2 text-xs font-semibold text-white">
          Gerar novas variacoes
        </button>
      </div>

      <div className="mt-5 flex flex-wrap gap-2 text-xs text-gray-600">
        {["B2B SaaS", "Alto LTV", "Executivos", "Tom consultivo", "CTA suave"].map((chip) => (
          <span key={chip} className="rounded-full border border-gray-200 bg-white px-3 py-1">
            {chip}
          </span>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-gray-200 bg-white p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-gray-500">Prompt base</p>
          <textarea
            className="mt-3 h-48 w-full resize-none rounded-xl border border-gray-200 p-3 text-sm text-gray-700"
            defaultValue="Explique como o produto reduz CAC para SaaS B2B em ate 30%."
          />
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-gray-500">Preview</p>
          <div className="mt-3 space-y-3">
            {variants.map((variant) => (
              <div key={variant} className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                <p className="text-xs font-semibold text-ink">{variant} version</p>
                <p className="mt-2 text-xs text-gray-600">
                  Texto gerado em modo {variant.toLowerCase()} para social media e campanhas.
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
