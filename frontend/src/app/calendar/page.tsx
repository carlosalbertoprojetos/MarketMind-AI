import CalendarView from "@/components/CalendarView";

export default function CalendarPage() {
  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">Calendar</h1>
        <p className="mt-2 text-sm text-gray-600">
          Agenda inteligente com visao semanal e mensal. Drag and drop pronto para evoluir.
        </p>
      </header>
      <CalendarView />
    </div>
  );
}