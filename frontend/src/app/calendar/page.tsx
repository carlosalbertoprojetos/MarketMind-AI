"use client";

import CalendarView from "@/components/CalendarView";
import { useI18n } from "@/i18n/I18nProvider";

export default function CalendarPage() {
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">{t("calendar.title")}</h1>
        <p className="mt-2 text-sm text-muted-2">
          {t("calendar.subtitle")}
        </p>
      </header>
      <CalendarView />
    </div>
  );
}
