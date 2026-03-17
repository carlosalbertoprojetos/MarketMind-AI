
"use client";

import { useAuth } from "@/auth/AuthProvider";
import { useI18n } from "@/i18n/I18nProvider";

export default function TopNavbar() {
  const { t } = useI18n();
  const { user, logout } = useAuth();
  const roleLabel = user?.is_superuser ? t("topbar.roleAdmin") : t("topbar.roleUser");
  const emailLabel = user?.email ?? t("topbar.userEmail");

  return (
    <header className="flex flex-col gap-4 px-8 py-6 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-muted">{t("app.autonomousMarketing")}</p>
        <h1 className="section-title text-xl font-semibold">{t("app.controlRoom")}</h1>
      </div>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="flex items-center gap-2 rounded-full border border-border bg-surface px-4 py-2 text-sm text-muted-2 shadow-sm">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-2">{t("topbar.search")}</span>
          <input
            className="w-40 bg-transparent text-sm text-ink outline-none"
            placeholder={t("topbar.searchPlaceholder")}
            aria-label={t("topbar.searchPlaceholder")}
          />
        </div>
        <div className="flex items-center gap-3">
          <button className="rounded-full border border-border px-4 py-2 text-sm text-muted-2">
            {t("topbar.syncNow")}
          </button>
          <button className="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-on-accent">
            {t("topbar.newCampaign")}
          </button>
        </div>
        <div className="flex items-center gap-3 rounded-full bg-surface px-4 py-2 shadow">
          <div className="h-8 w-8 rounded-full bg-ember" />
          <div>
            <p className="text-xs font-semibold text-ink">{roleLabel}</p>
            <p className="text-[11px] text-muted">{emailLabel}</p>
          </div>
          <button
            type="button"
            onClick={logout}
            className="rounded-full border border-border px-3 py-1 text-[11px] text-muted-2"
          >
            {t("topbar.logout")}
          </button>
        </div>
      </div>
    </header>
  );
}
