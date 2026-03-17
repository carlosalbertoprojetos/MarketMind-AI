"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

import {
  defaultLocale,
  formatMessage,
  resolveKey,
  translations,
  type Locale
} from "./i18n";

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  messages: Record<string, unknown>;
};

const I18nContext = createContext<I18nContextValue | null>(null);
const STORAGE_KEY = "marketmind.locale";

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = window.localStorage.getItem(STORAGE_KEY) as Locale | null;
    const browser = navigator.language.toLowerCase();
    const resolved =
      stored === "en" || stored === "pt"
        ? stored
        : browser.startsWith("pt")
          ? "pt"
          : "en";
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLocale(resolved);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(STORAGE_KEY, locale);
    document.documentElement.lang = locale === "pt" ? "pt-BR" : "en";
  }, [locale]);

  const messages = translations[locale];

  const value = useMemo<I18nContextValue>(() => {
    const t = (key: string, vars?: Record<string, string | number>) => {
      const resolved = resolveKey(messages, key);
      if (typeof resolved === "string") {
        return formatMessage(resolved, vars);
      }
      return key;
    };
    return { locale, setLocale, t, messages };
  }, [locale, messages]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return ctx;
}
