const days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"];

export default function CalendarView() {
  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">Agenda Semanal</h2>
        <div className="flex gap-2">
          <button className="rounded-full border border-gray-200 bg-ember px-3 py-1 text-xs text-white">
            Semana
          </button>
          <button className="rounded-full border border-gray-200 px-3 py-1 text-xs">Mes</button>
        </div>
      </div>

      <div className="mt-6 grid gap-3 lg:grid-cols-7">
        {days.map((day) => (
          <div key={day} className="rounded-2xl border border-gray-200 bg-white p-3">
            <p className="text-xs font-semibold text-ink">{day}</p>
            <div className="mt-3 space-y-2">
              <div className="rounded-xl bg-ember/10 p-2 text-[11px] text-ink">
                Post LinkedIn
              </div>
              <div className="rounded-xl bg-moss/10 p-2 text-[11px] text-ink">
                Reels IG
              </div>
              <div className="rounded-xl bg-slate-100 p-2 text-[11px] text-ink">
                Email nurture
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
