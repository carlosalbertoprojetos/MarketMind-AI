"use client";

import ProductAnalysisPanel from "@/components/ProductAnalysisPanel";
import { useI18n } from "@/i18n/I18nProvider";

export default function AIGeneratorPage() {
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">{t("generator.title")}</h1>
        <p className="mt-2 text-sm text-muted-2">
          {t("generator.subtitle")}
        </p>
      </header>

      <ProductAnalysisPanel />

      <section className="grid gap-6 lg:grid-cols-2">
        {[
          {
            title: t("generator.cards.product.title"),
            text: t("generator.cards.product.text")
          },
          {
            title: t("generator.cards.market.title"),
            text: t("generator.cards.market.text")
          },
          {
            title: t("generator.cards.audience.title"),
            text: t("generator.cards.audience.text")
          },
          {
            title: t("generator.cards.narrative.title"),
            text: t("generator.cards.narrative.text")
          }
        ].map((card) => (
          <div key={card.title} className="card p-6">
            <h2 className="section-title text-lg font-semibold">{card.title}</h2>
            <p className="mt-3 text-sm text-muted-2">{card.text}</p>
            <button className="mt-6 inline-flex items-center justify-center rounded-full bg-ember px-4 py-2 text-sm font-semibold text-on-accent">
              {t("generator.startFlow")}
            </button>
          </div>
        ))}
      </section>
    </div>
  );
}
