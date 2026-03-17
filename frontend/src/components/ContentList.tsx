"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type ContentItem = {
  id: string;
  title: string | null;
  content_type: string;
  brief: string | null;
  updated_at?: string;
};

export default function ContentList({ refreshKey = 0 }: { refreshKey?: number }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    setLoading(true);
    void (async () => {
      try {
        const data = await apiFetch<ContentItem[]>("/content-items", {}, accessToken);
        if (alive) {
          setItems(data);
        }
      } finally {
        if (alive) {
          setLoading(false);
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken, refreshKey]);

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("contentList.title")}</h2>
        <span className="text-xs text-muted">
          {t("contentList.items", { count: items.length })}
        </span>
      </div>
      <div className="mt-4 space-y-3">
        {loading && items.length === 0 ? (
          <div className="rounded-2xl border border-border bg-surface-2 p-4 text-sm text-muted">
            {t("contentList.loading")}
          </div>
        ) : items.length === 0 ? (
          <div className="rounded-2xl border border-border bg-surface-2 p-4 text-sm text-muted">
            {t("contentList.empty")}
          </div>
        ) : (
          items.map((item) => (
            <div key={item.id} className="rounded-2xl border border-border bg-surface-2 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-ink">
                  {item.title ?? t("contentList.untitled")}
                </p>
                <span className="rounded-full bg-surface px-2 py-1 text-[10px] uppercase text-muted">
                  {item.content_type.replace("_", " ")}
                </span>
              </div>
              {item.brief && <p className="mt-2 text-xs text-muted-2">{item.brief}</p>}
            </div>
          ))
        )}
      </div>
    </section>
  );
}
