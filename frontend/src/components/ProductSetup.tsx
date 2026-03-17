"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type Workspace = { id: string; name: string; slug: string };
type Brand = { id: string; name: string; workspace_id: string };
type Product = { id: string; name: string };

export default function ProductSetup() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [workspaceName, setWorkspaceName] = useState("Main Workspace");
  const [brandName, setBrandName] = useState("MarketMind");
  const [productName, setProductName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadAll = useCallback(async () => {
    if (!accessToken) return;
    const [workspaceData, brandData, productData] = await Promise.all([
      apiFetch<Workspace[]>("/workspaces", {}, accessToken),
      apiFetch<Brand[]>("/brands", {}, accessToken),
      apiFetch<Product[]>("/products", {}, accessToken)
    ]);
    setWorkspaces(workspaceData);
    setBrands(brandData);
    setProducts(productData);
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken) return;
    void loadAll();
  }, [accessToken, loadAll]);

  const primaryWorkspace = workspaces[0];
  const primaryBrand = useMemo(
    () => brands.find((brand) => brand.workspace_id === primaryWorkspace?.id) ?? brands[0],
    [brands, primaryWorkspace]
  );

  const handleCreate = async () => {
    if (!accessToken || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      let workspaceId = primaryWorkspace?.id ?? null;
      if (!workspaceId) {
        if (!workspaceName.trim()) {
          setMessage(t("productSetup.missingWorkspace"));
          return;
        }
        const workspace = await apiFetch<Workspace>(
          "/workspaces",
          {
            method: "POST",
            body: JSON.stringify({
              name: workspaceName.trim(),
              slug: slugify(workspaceName)
            })
          },
          accessToken
        );
        workspaceId = workspace.id;
      }

      let brandId = primaryBrand?.id ?? null;
      if (!brandId) {
        if (!brandName.trim()) {
          setMessage(t("productSetup.missingBrand"));
          return;
        }
        const brand = await apiFetch<Brand>(
          "/brands",
          {
            method: "POST",
            body: JSON.stringify({
              workspace_id: workspaceId,
              name: brandName.trim(),
              website_url: websiteUrl.trim() || null
            })
          },
          accessToken
        );
        brandId = brand.id;
      }

      if (!productName.trim()) {
        setMessage(t("productSetup.missingProduct"));
        return;
      }

      await apiFetch(
        "/products",
        {
          method: "POST",
          body: JSON.stringify({
            brand_id: brandId,
            name: productName.trim(),
            website_url: websiteUrl.trim() || null
          })
        },
        accessToken
      );
      setProductName("");
      setWebsiteUrl("");
      await loadAll();
      setMessage(t("productSetup.created"));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("productSetup.title")}</h2>
        <span className="text-xs text-muted">
          {t("productSetup.count", { count: products.length })}
        </span>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-border bg-surface-2 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">{t("productSetup.workspace")}</p>
          <p className="mt-2 text-sm text-ink">
            {primaryWorkspace?.name ?? t("productSetup.none")}
          </p>
          {!primaryWorkspace && (
            <input
              className="mt-3 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
              placeholder={t("productSetup.workspacePlaceholder")}
              value={workspaceName}
              onChange={(event) => setWorkspaceName(event.target.value)}
            />
          )}
        </div>
        <div className="rounded-2xl border border-border bg-surface-2 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-muted">{t("productSetup.brand")}</p>
          <p className="mt-2 text-sm text-ink">
            {primaryBrand?.name ?? t("productSetup.none")}
          </p>
          {!primaryBrand && (
            <input
              className="mt-3 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
              placeholder={t("productSetup.brandPlaceholder")}
              value={brandName}
              onChange={(event) => setBrandName(event.target.value)}
            />
          )}
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[2fr_1fr]">
        <input
          className="rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
          placeholder={t("productSetup.productPlaceholder")}
          value={productName}
          onChange={(event) => setProductName(event.target.value)}
        />
        <input
          className="rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
          placeholder={t("productSetup.websitePlaceholder")}
          value={websiteUrl}
          onChange={(event) => setWebsiteUrl(event.target.value)}
        />
      </div>

      {message && (
        <div className="mt-4 rounded-2xl border border-border bg-surface-2 p-3 text-xs text-muted-2">
          {message}
        </div>
      )}

      <button
        type="button"
        onClick={handleCreate}
        className="mt-4 rounded-full bg-ember px-4 py-2 text-xs font-semibold text-on-accent"
        disabled={busy}
      >
        {busy ? t("productSetup.creating") : t("productSetup.create")}
      </button>
    </section>
  );
}

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
