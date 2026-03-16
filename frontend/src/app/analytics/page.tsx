import AnalyticsCharts from "@/components/AnalyticsCharts";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">Analytics</h1>
        <p className="mt-2 text-sm text-gray-600">
          Metricas de engajamento, CTR e crescimento por canal.
        </p>
      </header>
      <AnalyticsCharts />
    </div>
  );
}