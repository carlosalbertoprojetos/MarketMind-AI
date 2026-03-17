"use client";

import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type Product = {
  id: string;
  name: string;
};

type ContentItem = {
  title: string | null;
  short_version: string | null;
  medium_version: string | null;
  long_version: string | null;
  technical_version: string | null;
  sales_version: string | null;
};

export default function ContentEditor({
  onGenerated,
  suggestedBrief
}: {
  onGenerated?: () => void;
  suggestedBrief?: string;
}) {
  const { t, messages } = useI18n();
  const { accessToken } = useAuth();
  const variants = useMemo(
    () =>
      ((messages.contentEditor as Record<string, unknown>)?.["variants"] as string[]) ??
      [],
    [messages]
  );
  const chips = useMemo(
    () =>
      ((messages.contentEditor as Record<string, unknown>)?.["chips"] as string[]) ??
      [],
    [messages]
  );
  const contentTypes = useMemo(() => {
    const mapped =
      ((messages.contentEditor as Record<string, unknown>)?.[
        "contentTypes"
      ] as Record<string, string>) ?? {};
    if (Object.keys(mapped).length) {
      return mapped;
    }
    return {
      linkedin_post: "LinkedIn",
      instagram_post: "Instagram",
      x_thread: "X",
      youtube_script: "YouTube",
      carousel: "Carousel",
      email_campaign: "Email"
    };
  }, [messages]);

  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState<string>("");
  const [contentType, setContentType] = useState<string>("linkedin_post");
  const [brief, setBrief] = useState<string>(t("contentEditor.basePromptText"));
  const [appliedBrief, setAppliedBrief] = useState<string | null>(null);
  const [generated, setGenerated] = useState<ContentItem | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    void (async () => {
      try {
        const data = await apiFetch<Product[]>("/products", {}, accessToken);
        if (!alive) return;
        setProducts(data);
        if (data.length && !productId) {
          setProductId(data[0].id);
        }
      } catch (err) {
        if (alive) {
          setError(err instanceof Error ? err.message : String(err));
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken, productId]);

  useEffect(() => {
    if (!brief) {
      setBrief(t("contentEditor.basePromptText"));
    }
  }, [t, brief]);

  useEffect(() => {
    if (suggestedBrief && suggestedBrief !== appliedBrief) {
      setBrief(suggestedBrief);
      setAppliedBrief(suggestedBrief);
    }
  }, [suggestedBrief, appliedBrief]);

  const handleGenerate = async () => {
    if (!accessToken || !productId || busy) return;
    setBusy(true);
    setError(null);
    try {
      const content = await apiFetch<ContentItem>(
        "/ai/content/generate",
        {
          method: "POST",
          body: JSON.stringify({
            product_id: productId,
            content_type: contentType,
            brief
          })
        },
        accessToken
      );
      setGenerated(content);
      onGenerated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const previewVariants = useMemo(() => {
    if (!generated) return null;
    return [
      { label: t("contentEditor.variantLabel", { variant: variants[0] ?? "" }), value: generated.short_version },
      { label: t("contentEditor.variantLabel", { variant: variants[1] ?? "" }), value: generated.medium_version },
      { label: t("contentEditor.variantLabel", { variant: variants[2] ?? "" }), value: generated.long_version },
      { label: t("contentEditor.variantLabel", { variant: variants[3] ?? "" }), value: generated.technical_version },
      { label: t("contentEditor.variantLabel", { variant: variants[4] ?? "" }), value: generated.sales_version }
    ];
  }, [generated, t, variants]);

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="section-title text-xl font-semibold">{t("contentEditor.title")}</h2>
          <p className="mt-2 text-sm text-muted-2">{t("contentEditor.subtitle")}</p>
        </div>
        <button
          type="button"
          onClick={handleGenerate}
          className="rounded-full bg-ember px-4 py-2 text-xs font-semibold text-on-accent"
          disabled={busy || !productId}
        >
          {busy ? t("contentEditor.generating") : t("contentEditor.generateVariations")}
        </button>
      </div>

      <div className="mt-5 flex flex-wrap gap-2 text-xs text-muted-2">
        {chips.map((chip) => (
          <span key={chip} className="rounded-full border border-border bg-surface px-3 py-1">
            {chip}
          </span>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-surface p-4">
          <div className="flex flex-col gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-muted">{t("contentEditor.basePrompt")}</p>
              <textarea
                className="mt-3 h-48 w-full resize-none rounded-xl border border-border p-3 text-sm text-ink"
                value={brief}
                onChange={(event) => setBrief(event.target.value)}
              />
            </div>
            <div className="grid gap-3 lg:grid-cols-2">
              <div>
                <p className="text-xs text-muted">{t("contentEditor.product")}</p>
                {products.length === 0 && (
                  <p className="mt-2 text-xs text-muted-2">{t("contentEditor.noProducts")}</p>
                )}
                <select
                  className="mt-2 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
                  value={productId}
                  onChange={(event) => setProductId(event.target.value)}
                >
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <p className="text-xs text-muted">{t("contentEditor.contentType")}</p>
                <select
                  className="mt-2 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
                  value={contentType}
                  onChange={(event) => setContentType(event.target.value)}
                >
                  {Object.entries(contentTypes).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">{t("contentEditor.preview")}</p>
          {error && (
            <div className="mt-3 rounded-xl border border-border bg-surface-2 p-3 text-xs text-muted-2">
              {error}
            </div>
          )}
          <div className="mt-3 space-y-3">
            {previewVariants
              ? previewVariants.map((variant, index) => (
                  <div key={`${variant.label}-${index}`} className="rounded-xl border border-border bg-surface-2 p-3">
                    <p className="text-xs font-semibold text-ink">{variant.label}</p>
                    <p className="mt-2 text-xs text-muted-2">{variant.value}</p>
                  </div>
                ))
              : variants.map((variant) => (
                  <div key={variant} className="rounded-xl border border-border bg-surface-2 p-3">
                    <p className="text-xs font-semibold text-ink">
                      {t("contentEditor.variantLabel", { variant })}
                    </p>
                    <p className="mt-2 text-xs text-muted-2">
                      {t("contentEditor.variantText", { variant: variant.toLowerCase() })}
                    </p>
                  </div>
                ))}
          </div>
        </div>
      </div>
    </section>
  );
}
