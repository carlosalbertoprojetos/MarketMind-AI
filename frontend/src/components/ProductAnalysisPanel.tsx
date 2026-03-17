"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type Product = { id: string; name: string };
type AnalysisResponse = { product_id: string; extracted_data: Record<string, unknown> };
type ContentItem = { id: string };
type Persona = { id: string; name: string };
type Narrative = {
  problem: string;
  diagnosis: string;
  solution: string;
  demonstration: string;
  social_proof: string;
  cta: string;
  angles: string[];
};
type PipelineRun = {
  id: string;
  status: string;
  created_at: string;
  output_payload?: { content_item_ids?: string[] };
};

type Props = {
  onBriefReady?: (brief: string) => void;
  onContentGenerated?: (content: ContentItem) => void;
};

export default function ProductAnalysisPanel({ onBriefReady, onContentGenerated }: Props) {
  const { t, messages } = useI18n();
  const { accessToken } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState<string>("");
  const [urls, setUrls] = useState("");
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [brief, setBrief] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contentType, setContentType] = useState("linkedin_post");
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState<Record<string, string>>({});
  const [pipelinePersonas, setPipelinePersonas] = useState<Persona[]>([]);
  const [pipelineNarrative, setPipelineNarrative] = useState<Narrative | null>(null);
  const [pipelineContent, setPipelineContent] = useState<Record<string, string> | null>(null);
  const [pipelineRuns, setPipelineRuns] = useState<PipelineRun[]>([]);

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

  const parseSources = useCallback(() => {
    return urls
      .split(/\n|,/)
      .map((entry) => entry.trim())
      .filter(Boolean);
  }, [urls]);

  const loadRuns = useCallback(async () => {
    if (!accessToken || !productId) return;
    const runs = await apiFetch<PipelineRun[]>(
      `/ai/pipeline/runs?product_id=${productId}`,
      {},
      accessToken
    );
    setPipelineRuns(runs);
  }, [accessToken, productId]);

  useEffect(() => {
    if (!accessToken || !productId) return;
    void loadRuns();
  }, [accessToken, productId, loadRuns]);

  const handleAnalyze = async () => {
    if (!accessToken || !productId || busy) return;
    const sources = parseSources();
    if (!sources.length) {
      setError(t("analysis.noUrls"));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await apiFetch<AnalysisResponse>(
        "/ai/product/analyze",
        {
          method: "POST",
          body: JSON.stringify({ product_id: productId, sources })
        },
        accessToken
      );
      setAnalysis(response.extracted_data);
      const nextBrief = buildBrief(response.extracted_data, sources);
      setBrief(nextBrief);
      onBriefReady?.(nextBrief);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const runPipeline = async () => {
    if (!accessToken || !productId || pipelineRunning) return;
    setPipelineRunning(true);
    setError(null);
    setPipelineSteps({
      analyze: "pending",
      audience: "pending",
      narrative: "pending",
      content: "pending"
    });
    try {
      const sources = parseSources();
      if (!sources.length) {
        setError(t("analysis.noUrls"));
        setPipelineRunning(false);
        return;
      }
      const response = await apiFetch<{
        steps: Record<string, string>;
        output?: {
          narrative?: Narrative;
          personas?: string[];
        };
        content_item_ids: string[];
      }>(
        "/ai/pipeline/run",
        {
          method: "POST",
          body: JSON.stringify({
            product_id: productId,
            sources,
            brief: brief || t("analysis.defaultBrief")
          })
        },
        accessToken
      );
      setPipelineSteps(response.steps ?? {});
      setPipelineNarrative(response.output?.narrative ?? null);
      if (response.output?.personas?.length) {
        setPipelinePersonas(
          response.output.personas.map((id) => ({ id, name: id.slice(0, 8) }))
        );
      }
      if (response.content_item_ids?.length) {
        setPipelineContent({ title: t("analysis.contentGenerated"), short_version: response.content_item_ids.join(", ") });
      }
      await loadRuns();
      onContentGenerated?.({ id: response.content_item_ids?.[0] ?? "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setPipelineSteps((prev) => ({ ...prev, content: "error" }));
    } finally {
      setPipelineRunning(false);
    }
  };

  const handleGenerate = async () => {
    if (!accessToken || !productId || busy) return;
    if (!brief) {
      setError(t("analysis.noBrief"));
      return;
    }
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
      onContentGenerated?.(content);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("analysis.title")}</h2>
        <span className="text-xs text-muted">{t("analysis.subtitle")}</span>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <div>
          <label className="text-xs text-muted">{t("analysis.productLabel")}</label>
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
          <label className="text-xs text-muted">{t("analysis.contentType")}</label>
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

      <div className="mt-4">
        <label className="text-xs text-muted">{t("analysis.urlsLabel")}</label>
        <textarea
          className="mt-2 h-28 w-full resize-none rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
          placeholder={t("analysis.urlsPlaceholder")}
          value={urls}
          onChange={(event) => setUrls(event.target.value)}
        />
      </div>

      {error && (
        <div className="mt-4 rounded-2xl border border-border bg-surface-2 p-3 text-xs text-muted-2">
          {error}
        </div>
      )}

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={handleAnalyze}
          className="rounded-full bg-ember px-4 py-2 text-xs font-semibold text-on-accent"
          disabled={busy || !productId}
        >
          {busy ? t("analysis.analyzing") : t("analysis.analyze")}
        </button>
        <button
          type="button"
          onClick={handleGenerate}
          className="rounded-full border border-border px-4 py-2 text-xs text-muted-2"
          disabled={busy || !brief}
        >
          {t("analysis.generate")}
        </button>
        <button
          type="button"
          onClick={runPipeline}
          className="rounded-full border border-ember px-4 py-2 text-xs text-ember"
          disabled={pipelineRunning || !productId}
        >
          {pipelineRunning ? t("analysis.pipelineRunning") : t("analysis.runPipeline")}
        </button>
      </div>

      {analysis && (
        <div className="mt-6 rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-ink">{t("analysis.resultsTitle")}</p>
            <button
              type="button"
              onClick={() => onBriefReady?.(brief)}
              className="text-xs text-ember underline"
            >
              {t("analysis.useBrief")}
            </button>
          </div>
          <pre className="mt-3 whitespace-pre-wrap break-words text-[11px] text-muted-2">
            {JSON.stringify(analysis, null, 2)}
          </pre>
        </div>
      )}

      {(pipelineRunning || pipelineSteps.analyze) && (
        <div className="mt-6 rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
          <p className="text-xs font-semibold text-ink">{t("analysis.pipelineTitle")}</p>
          <ul className="mt-3 space-y-2">
            {[
              ["analyze", t("analysis.stepAnalyze")],
              ["audience", t("analysis.stepAudience")],
              ["narrative", t("analysis.stepNarrative")],
              ["content", t("analysis.stepContent")]
            ].map(([key, label]) => (
              <li key={key} className="flex items-center justify-between">
                <span>{label}</span>
                <span className="text-[10px] uppercase text-muted">
                  {pipelineSteps[key] ?? "pending"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {pipelineRuns.length > 0 && (
        <div className="mt-6 rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
          <p className="text-xs font-semibold text-ink">{t("analysis.runsTitle")}</p>
          <ul className="mt-3 space-y-2">
            {pipelineRuns.map((run) => (
              <li key={run.id} className="flex items-center justify-between">
                <span>{new Date(run.created_at).toLocaleString()}</span>
                <span className="text-[10px] uppercase text-muted">{run.status}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {(pipelinePersonas.length > 0 || pipelineNarrative || pipelineContent) && (
        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
            <p className="text-xs font-semibold text-ink">{t("analysis.personasTitle")}</p>
            <ul className="mt-2 space-y-2">
              {pipelinePersonas.map((persona) => (
                <li key={persona.id} className="rounded-lg border border-border bg-surface px-2 py-1">
                  {persona.name}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
            <p className="text-xs font-semibold text-ink">{t("analysis.narrativeTitle")}</p>
            {pipelineNarrative ? (
              <div className="mt-2 space-y-2">
                <p>{pipelineNarrative.problem}</p>
                <p>{pipelineNarrative.solution}</p>
                <p className="text-[11px] text-muted">{pipelineNarrative.cta}</p>
              </div>
            ) : (
              <p className="mt-2">{t("analysis.narrativeEmpty")}</p>
            )}
          </div>
          <div className="rounded-2xl border border-border bg-surface-2 p-4 text-xs text-muted-2">
            <p className="text-xs font-semibold text-ink">{t("analysis.contentTitle")}</p>
            {pipelineContent ? (
              <div className="mt-2 space-y-2">
                <p className="text-xs font-semibold">{pipelineContent.title}</p>
                <p>{pipelineContent.short_version}</p>
              </div>
            ) : (
              <p className="mt-2">{t("analysis.contentEmpty")}</p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

function buildBrief(extracted: Record<string, unknown>, sources: string[]) {
  const summary = JSON.stringify(extracted, null, 2);
  return [
    "Use a analise abaixo para gerar conteudo de marketing:",
    `Fontes: ${sources.join(", ")}`,
    summary
  ].join("\n");
}
