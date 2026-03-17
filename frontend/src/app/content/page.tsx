"use client";

import { useState } from "react";

import ContentEditor from "@/components/ContentEditor";
import ContentList from "@/components/ContentList";
import ProductAnalysisPanel from "@/components/ProductAnalysisPanel";
import ProductSetup from "@/components/ProductSetup";
import { useI18n } from "@/i18n/I18nProvider";

export default function ContentStudioPage() {
  const { t } = useI18n();
  const [refreshKey, setRefreshKey] = useState(0);
  const [suggestedBrief, setSuggestedBrief] = useState<string | undefined>(undefined);

  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">{t("contentStudio.title")}</h1>
        <p className="mt-2 text-sm text-muted-2">
          {t("contentStudio.subtitle")}
        </p>
      </header>
      <ProductSetup />
      <ProductAnalysisPanel onBriefReady={setSuggestedBrief} onContentGenerated={() => setRefreshKey((prev) => prev + 1)} />
      <ContentEditor
        suggestedBrief={suggestedBrief}
        onGenerated={() => setRefreshKey((prev) => prev + 1)}
      />
      <ContentList refreshKey={refreshKey} />
    </div>
  );
}
