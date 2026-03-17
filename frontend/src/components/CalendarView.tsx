"use client";

import { useI18n } from "@/i18n/I18nProvider";

export default function CalendarView() {
  const { t, messages } = useI18n();
  const days =
    ((messages.calendar as Record<string, unknown>)?.["daysShort"] as string[]) ?? [];
  const items =
    ((messages.calendar as Record<string, unknown>)?.["items"] as string[]) ?? [];

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("calendar.weeklyTitle")}</h2>
        <div className="flex gap-2">
          <button className="rounded-full border border-border bg-ember px-3 py-1 text-xs text-on-accent">
            {t("calendar.week")}
          </button>
          <button className="rounded-full border border-border px-3 py-1 text-xs">
            {t("calendar.month")}
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-3 lg:grid-cols-7">
        {days.map((day) => (
          <div key={day} className="rounded-2xl border border-border bg-surface p-3">
            <p className="text-xs font-semibold text-ink">{day}</p>
            <div className="mt-3 space-y-2">
              <div className="rounded-xl bg-ember/10 p-2 text-[11px] text-ink">
                {items[0]}
              </div>
              <div className="rounded-xl bg-moss/10 p-2 text-[11px] text-ink">
                {items[1]}
              </div>
              <div className="rounded-xl bg-surface-2 p-2 text-[11px] text-ink">
                {items[2]}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
