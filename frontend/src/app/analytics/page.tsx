"use client";

import AnalyticsCharts from "@/components/AnalyticsCharts";
import { useI18n } from "@/i18n/I18nProvider";

export default function AnalyticsPage() {
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">{t("analytics.title")}</h1>
        <p className="mt-2 text-sm text-muted-2">
          {t("analytics.subtitle")}
        </p>
      </header>
      <AnalyticsCharts />
    </div>
  );
}
