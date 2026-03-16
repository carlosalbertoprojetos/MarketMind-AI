"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

const data = [
  { name: "Seg", engagement: 64, ctr: 3.1 },
  { name: "Ter", engagement: 71, ctr: 3.4 },
  { name: "Qua", engagement: 68, ctr: 3.2 },
  { name: "Qui", engagement: 75, ctr: 3.7 },
  { name: "Sex", engagement: 82, ctr: 4.1 },
  { name: "Sab", engagement: 77, ctr: 3.9 },
  { name: "Dom", engagement: 69, ctr: 3.3 }
];

export default function AnalyticsCharts() {
  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">Performance semanal</h2>
        <p className="text-xs text-gray-500">Engajamento e CTR</p>
      </div>
      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        {[
          { label: "Engajamento medio", value: "72%" },
          { label: "CTR medio", value: "3.7%" },
          { label: "Crescimento", value: "+12%" }
        ].map((item) => (
          <div key={item.label} className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
            <p className="text-xs text-gray-500">{item.label}</p>
            <p className="section-title mt-2 text-lg font-semibold text-ink">{item.value}</p>
          </div>
        ))}
      </div>
      <div className="mt-6 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip />
            <Line type="monotone" dataKey="engagement" stroke="#e05a3b" strokeWidth={2} />
            <Line type="monotone" dataKey="ctr" stroke="#3c6f5d" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
