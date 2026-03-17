import en from "@/locales/en/common.json";
import pt from "@/locales/pt/common.json";

export type Locale = "en" | "pt";

export const translations: Record<Locale, Record<string, unknown>> = {
  en,
  pt
};

export const defaultLocale: Locale = "pt";

export function resolveKey(
  source: Record<string, unknown>,
  key: string
): unknown {
  return key.split(".").reduce((acc, part) => {
    if (acc && typeof acc === "object" && part in acc) {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, source as unknown);
}

export function formatMessage(
  message: string,
  vars: Record<string, string | number> = {}
): string {
  return message.replace(/\{(\w+)\}/g, (_, key) => {
    const value = vars[key];
    return value === undefined ? `{${key}}` : String(value);
  });
}
