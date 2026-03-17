"use client";

import CampaignBoard from "@/components/CampaignBoard";
import { useI18n } from "@/i18n/I18nProvider";

export default function CampaignsPage() {
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">{t("campaigns.title")}</h1>
        <p className="mt-2 text-sm text-muted-2">
          {t("campaigns.subtitle")}
        </p>
      </header>
      <CampaignBoard />
    </div>
  );
}
