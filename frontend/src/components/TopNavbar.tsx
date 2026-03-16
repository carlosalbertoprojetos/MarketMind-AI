export default function TopNavbar() {
  return (
    <header className="flex flex-col gap-4 px-8 py-6 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-gray-500">Autonomous Marketing Intelligence</p>
        <h1 className="section-title text-xl font-semibold">MarketMind Control Room</h1>
      </div>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-600 shadow-sm">
          <span className="text-xs uppercase tracking-[0.2em] text-gray-400">Search</span>
          <input
            className="w-40 bg-transparent text-sm text-ink outline-none"
            placeholder="Buscar insights"
          />
        </div>
        <div className="flex items-center gap-3">
          <button className="rounded-full border border-gray-200 px-4 py-2 text-sm text-gray-600">
            Sync agora
          </button>
          <button className="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-white">
            Nova campanha
          </button>
        </div>
        <div className="flex items-center gap-3 rounded-full bg-white px-4 py-2 shadow">
          <div className="h-8 w-8 rounded-full bg-ember" />
          <div>
            <p className="text-xs font-semibold text-ink">Admin</p>
            <p className="text-[11px] text-gray-500">admin@marketmind.ai</p>
          </div>
        </div>
      </div>
    </header>
  );
}
