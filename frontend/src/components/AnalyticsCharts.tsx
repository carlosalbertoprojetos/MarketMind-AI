"use client";

import { useEffect, useMemo, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type AnalyticsSummary = {
  engagement_rate: number;
  ctr: number;
  growth: number;
};

type AnalyticsEvent = {
  id: string;
  event_type: string;
  occurred_at: string;
};

export default function AnalyticsCharts() {
  const { t, messages } = useI18n();
  const { accessToken } = useAuth();
  const days = useMemo(
    () => ((messages.calendar as Record<string, unknown>)?.["daysShort"] as string[]) ?? [],
    [messages]
  );
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [series, setSeries] = useState(() =>
    days.map((day) => ({ name: day, engagement: 0, ctr: 0 }))
  );

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    void (async () => {
      try {
        const [summaryData, events] = await Promise.all([
          apiFetch<AnalyticsSummary>("/ai/analytics/summary", {}, accessToken),
          apiFetch<AnalyticsEvent[]>("/analytics/events", {}, accessToken)
        ]);
        if (!alive) return;
        setSummary(summaryData);
        setSeries(buildSeries(days, events));
      } catch {
        if (alive) {
          setSeries(days.map((day) => ({ name: day, engagement: 0, ctr: 0 })));
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken, days]);

  const cards = useMemo(
    () => [
      {
        label: t("analytics.cards.engagement"),
        value: summary ? `${summary.engagement_rate.toFixed(1)}%` : "0%"
      },
      {
        label: t("analytics.cards.ctr"),
        value: summary ? `${summary.ctr.toFixed(1)}%` : "0%"
      },
      {
        label: t("analytics.cards.growth"),
        value: summary ? `+${summary.growth.toFixed(1)}%` : "0%"
      }
    ],
    [summary, t]
  );

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("analytics.weeklyTitle")}</h2>
        <p className="text-xs text-muted">{t("analytics.weeklySubtitle")}</p>
      </div>
      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        {cards.map((item) => (
          <div key={item.label} className="rounded-2xl border border-border bg-surface-2 p-4">
            <p className="text-xs text-muted">{item.label}</p>
            <p className="section-title mt-2 text-lg font-semibold text-ink">{item.value}</p>
          </div>
        ))}
      </div>
      <div className="mt-6 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
            <XAxis dataKey="name" stroke="var(--chart-axis)" />
            <YAxis stroke="var(--chart-axis)" />
            <Tooltip />
            <Line type="monotone" dataKey="engagement" stroke="rgb(var(--color-accent))" strokeWidth={2} />
            <Line type="monotone" dataKey="ctr" stroke="rgb(var(--color-accent-2))" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function buildSeries(days: string[], events: AnalyticsEvent[]) {
  const totals = new Array(7).fill(0);
  const engaged = new Array(7).fill(0);
  const clicked = new Array(7).fill(0);

  events.forEach((event) => {
    const date = new Date(event.occurred_at);
    const jsDay = date.getDay();
    const index = (jsDay + 6) % 7;
    totals[index] += 1;
    if (event.event_type === "post_engaged") {
      engaged[index] += 1;
    }
    if (event.event_type === "post_clicked") {
      clicked[index] += 1;
    }
  });

  return days.map((day, index) => {
    const total = totals[index] || 0;
    const engagement = total ? (engaged[index] / total) * 100 : 0;
    const ctr = total ? (clicked[index] / total) * 100 : 0;
    return {
      name: day,
      engagement: Number(engagement.toFixed(1)),
      ctr: Number(ctr.toFixed(1))
    };
  });
}
