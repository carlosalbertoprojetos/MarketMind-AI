"use client";

import Image from "next/image";

import { useI18n } from "@/i18n/I18nProvider";
import { useTheme } from "@/theme/ThemeProvider";

export default function FloatingControls() {
  const { locale, setLocale, t } = useI18n();
  const { theme, toggleTheme } = useTheme();

  const isPt = locale === "pt";
  const flagSrc = isPt ? "/flags/us.svg" : "/flags/br.svg";
  const flagAlt = isPt ? t("controls.flagUsAlt") : t("controls.flagBrAlt");
  const nextLocale = isPt ? "en" : "pt";

  return (
    <div className="fixed right-[30px] top-[80px] z-50 flex flex-col gap-3">
      <button
        type="button"
        onClick={toggleTheme}
        aria-label={t("controls.themeToggle")}
        title={t("controls.themeToggle")}
        className="flex h-11 w-11 items-center justify-center rounded-full border border-border bg-surface text-ink shadow-md transition hover:shadow-lg"
      >
        <span className="text-xs font-semibold">
          {theme === "light" ? "☀" : "☾"}
        </span>
      </button>

      <button
        type="button"
        onClick={() => setLocale(nextLocale)}
        aria-label={isPt ? t("controls.languageToggleToEn") : t("controls.languageToggleToPt")}
        title={isPt ? t("controls.languageToggleToEn") : t("controls.languageToggleToPt")}
        className="flex h-11 w-11 items-center justify-center rounded-full border border-border bg-surface shadow-md transition hover:shadow-lg"
      >
        <Image src={flagSrc} alt={flagAlt} width={22} height={22} unoptimized />
      </button>
    </div>
  );
}
