"use client";

import { useEffect, useMemo, useState } from "react";

import CampaignBoard from "@/components/CampaignBoard";
import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type AnalyticsSummary = {
  engagement_rate: number;
  ctr: number;
  growth: number;
};

type Campaign = {
  id: string;
};

type ContentItem = {
  id: string;
};

export default function DashboardPage() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [campaignCount, setCampaignCount] = useState(0);
  const [contentCount, setContentCount] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    setLoading(true);
    void (async () => {
      try {
        const [campaigns, contentItems, analytics] = await Promise.all([
          apiFetch<Campaign[]>("/campaigns", {}, accessToken),
          apiFetch<ContentItem[]>("/content-items", {}, accessToken),
          apiFetch<AnalyticsSummary>("/ai/analytics/summary", {}, accessToken)
        ]);
        if (!alive) return;
        setCampaignCount(campaigns.length);
        setContentCount(contentItems.length);
        setSummary(analytics);
      } finally {
        if (alive) {
          setLoading(false);
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken]);

  const stats = useMemo(
    () => [
      {
        label: t("dashboard.stats.activeCampaigns"),
        value: campaignCount,
        helper: t("dashboard.stats.activeCampaignsHelper")
      },
      {
        label: t("dashboard.stats.publishedContent"),
        value: contentCount,
        helper: t("dashboard.stats.publishedContentHelper")
      },
      {
        label: t("dashboard.stats.attributedRevenue"),
        value: summary ? `${summary.growth.toFixed(1)}%` : "0%",
        helper: t("dashboard.stats.attributedRevenueHelper")
      }
    ],
    [campaignCount, contentCount, summary, t]
  );

  return (
    <div className="space-y-8">
      <section className="card p-8 fade-in">
        <p className="text-sm uppercase tracking-[0.2em] text-moss">{t("app.tagline")}</p>
        <h1 className="section-title mt-3 text-3xl font-semibold">
          {t("dashboard.title")}
        </h1>
        <p className="mt-3 text-base text-muted-2">
          {t("dashboard.subtitle")}
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {stats.map((item) => (
          <div key={item.label} className="card p-6 fade-in">
            <p className="text-sm text-muted">{item.label}</p>
            <p className="section-title mt-3 text-2xl font-semibold text-ink">
              {loading ? "..." : item.value}
            </p>
            <p className="mt-2 text-sm text-muted">{item.helper}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <CampaignBoard />
        <div className="card p-6 fade-in">
          <h2 className="section-title text-xl font-semibold">{t("dashboard.insightsTitle")}</h2>
          <div className="mt-4 space-y-4 text-sm text-muted-2">
            <div className="rounded-2xl border border-border bg-surface-2 p-4">
              {t("dashboard.insights.one", {
                engagement: summary?.engagement_rate.toFixed(1) ?? "0.0"
              })}
            </div>
            <div className="rounded-2xl border border-border bg-surface-2 p-4">
              {t("dashboard.insights.two", { ctr: summary?.ctr.toFixed(1) ?? "0.0" })}
            </div>
            <div className="rounded-2xl border border-border bg-surface-2 p-4">
              {t("dashboard.insights.three", {
                growth: summary?.growth.toFixed(1) ?? "0.0"
              })}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
