"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

type Campaign = {
  id: string;
  name: string;
  stage: string;
  status: string;
};

const stageOrder = ["awareness", "education", "solution", "proof", "conversion"] as const;
const stageTones: Record<string, string> = {
  awareness: "bg-moss/10 border-moss/40 text-moss",
  education: "bg-sky/10 border-sky/40 text-sky",
  solution: "bg-ember/10 border-ember/40 text-ember",
  proof: "bg-plum/10 border-plum/40 text-plum",
  conversion: "bg-ink/10 border-ink/40 text-ink"
};

export default function CampaignBoard() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCampaigns = useCallback(async () => {
    if (!accessToken) return;
    const data = await apiFetch<Campaign[]>("/campaigns", {}, accessToken);
    setCampaigns(data);
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    setLoading(true);
    void (async () => {
      try {
        if (!alive) return;
        await loadCampaigns();
      } finally {
        if (alive) {
          setLoading(false);
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken, loadCampaigns]);

  const handleCreate = async () => {
    if (!accessToken || creating) return;
    setCreating(true);
    setError(null);
    try {
      const [workspaces, products] = await Promise.all([
        apiFetch<Array<{ id: string; name: string }>>("/workspaces", {}, accessToken),
        apiFetch<Array<{ id: string; name: string }>>("/products", {}, accessToken)
      ]);
      if (!workspaces.length || !products.length) {
        setError(t("campaignBoard.missingPrerequisites"));
        return;
      }
      const payload = {
        workspace_id: workspaces[0].id,
        product_id: products[0].id,
        name: `Campaign ${new Date().toISOString().slice(0, 10)}`,
        objective: t("campaignBoard.defaultObjective"),
        stage: "awareness"
      };
      await apiFetch("/campaigns", { method: "POST", body: JSON.stringify(payload) }, accessToken);
      await loadCampaigns();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setCreating(false);
    }
  };

  const grouped = useMemo(() => {
    const map = new Map<string, Campaign[]>();
    stageOrder.forEach((stage) => map.set(stage, []));
    campaigns.forEach((campaign) => {
      if (!map.has(campaign.stage)) {
        map.set(campaign.stage, []);
      }
      map.get(campaign.stage)?.push(campaign);
    });
    return map;
  }, [campaigns]);

  return (
    <section className="card p-6 fade-in">
      <div className="flex items-center justify-between">
        <h2 className="section-title text-xl font-semibold">{t("campaignBoard.title")}</h2>
        <button
          type="button"
          onClick={handleCreate}
          className="rounded-full bg-ember px-4 py-2 text-xs font-semibold text-on-accent"
          disabled={creating}
        >
          {creating ? t("campaignBoard.creating") : t("campaignBoard.newCampaign")}
        </button>
      </div>
      {error && (
        <div className="mt-4 rounded-2xl border border-border bg-surface-2 p-3 text-xs text-muted-2">
          {error}
        </div>
      )}
      <div className="mt-6 grid gap-4 lg:grid-cols-5">
        {stageOrder.map((stage) => {
          const items = grouped.get(stage) ?? [];
          return (
            <div
              key={stage}
              className={`rounded-2xl border p-4 ${stageTones[stage] ?? "border-border"}`}
            >
              <div className="flex items-center justify-between text-xs font-semibold uppercase">
                <span>{t(`campaignBoard.stages.${stage}`)}</span>
                <span className="rounded-full bg-white/20 px-2 py-1 text-[10px]">
                  {t("campaignBoard.items", { count: items.length })}
                </span>
              </div>
              <div className="mt-4 space-y-3 text-xs">
                {loading && items.length === 0 ? (
                  <div className="rounded-xl border border-white/30 bg-white/10 p-2 text-center">
                    {t("campaignBoard.loading")}
                  </div>
                ) : items.length === 0 ? (
                  <div className="rounded-xl border border-white/30 bg-white/10 p-2 text-center">
                    {t("campaignBoard.empty")}
                  </div>
                ) : (
                  items.map((item) => (
                    <div key={item.id} className="rounded-xl border border-white/30 bg-white/10 p-2">
                      <p className="text-xs font-semibold text-ink">{item.name}</p>
                      <p className="mt-1 text-[10px] uppercase opacity-70">{item.status}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
