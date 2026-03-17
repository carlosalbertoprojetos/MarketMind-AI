"use client";

import { useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

const REQUIRE_AUTH = process.env.NEXT_PUBLIC_REQUIRE_AUTH !== "false";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { accessToken, loading } = useAuth();
  const { t } = useI18n();

  if (!REQUIRE_AUTH) {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted">
        {t("auth.loading")}
      </div>
    );
  }

  if (!accessToken) {
    return <AuthPanel />;
  }

  return <>{children}</>;
}

function AuthPanel() {
  const { t } = useI18n();
  const { login, error } = useAuth();
  const demoEmail = process.env.NEXT_PUBLIC_DEMO_EMAIL ?? "";
  const demoPassword = process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? "";
  const demoOrg = process.env.NEXT_PUBLIC_DEMO_ORG ?? "MarketMind";
  const [email, setEmail] = useState(demoEmail);
  const [password, setPassword] = useState(demoPassword);
  const [orgName, setOrgName] = useState(demoOrg);
  const [orgSlug, setOrgSlug] = useState(slugify(demoOrg));
  const [fullName, setFullName] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [mode, setMode] = useState<"login" | "register" | "reset" | "resetConfirm">("login");
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [resetInfo, setResetInfo] = useState<string | null>(null);

  const title = useMemo(() => {
    if (mode === "register") return t("auth.registerTitle");
    if (mode === "reset" || mode === "resetConfirm") return t("auth.resetTitle");
    return t("auth.title");
  }, [mode, t]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);
    setBusy(true);
    try {
      if (mode === "register") {
        await apiFetch("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            organization_name: orgName.trim(),
            organization_slug: orgSlug.trim(),
            full_name: fullName.trim() || null,
            email: email.trim(),
            password
          })
        });
        await login(email.trim(), password);
      } else if (mode === "reset") {
        const response = await apiFetch<{ reset_token?: string }>("/auth/forgot-password", {
          method: "POST",
          body: JSON.stringify({ email: email.trim() })
        });
        setResetInfo(t("auth.resetSent"));
        if (response?.reset_token) {
          setResetToken(response.reset_token);
          setMode("resetConfirm");
        }
      } else if (mode === "resetConfirm") {
        await apiFetch("/auth/reset-password", {
          method: "POST",
          body: JSON.stringify({ token: resetToken.trim(), new_password: newPassword })
        });
        setResetInfo(t("auth.resetSuccess"));
        setMode("login");
      } else {
        await login(email.trim(), password);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-smoke px-6">
      <form onSubmit={handleSubmit} className="card w-full max-w-md space-y-6 p-8">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted">
            {t("auth.heading")}
          </p>
          <h1 className="section-title mt-3 text-2xl font-semibold">{title}</h1>
          <p className="mt-2 text-sm text-muted-2">{t("auth.subtitle")}</p>
        </div>

        {mode === "register" && (
          <>
            <div className="space-y-3">
              <label className="block text-xs text-muted" htmlFor="org-name">
                {t("auth.orgName")}
              </label>
              <input
                id="org-name"
                type="text"
                className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
                value={orgName}
                onChange={(event) => {
                  const next = event.target.value;
                  setOrgName(next);
                  setOrgSlug(slugify(next));
                }}
                required
              />
            </div>
            <div className="space-y-3">
              <label className="block text-xs text-muted" htmlFor="org-slug">
                {t("auth.orgSlug")}
              </label>
              <input
                id="org-slug"
                type="text"
                className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
                value={orgSlug}
                onChange={(event) => setOrgSlug(event.target.value)}
                required
              />
            </div>
            <div className="space-y-3">
              <label className="block text-xs text-muted" htmlFor="full-name">
                {t("auth.fullName")}
              </label>
              <input
                id="full-name"
                type="text"
                className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
              />
            </div>
          </>
        )}

        <div className="space-y-3">
          <label className="block text-xs text-muted" htmlFor="login-email">
            {t("auth.email")}
          </label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>

        {mode !== "reset" && (
          <div className="space-y-3">
            <label className="block text-xs text-muted" htmlFor="login-password">
              {mode === "resetConfirm" ? t("auth.newPassword") : t("auth.password")}
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
              value={mode === "resetConfirm" ? newPassword : password}
              onChange={(event) =>
                mode === "resetConfirm"
                  ? setNewPassword(event.target.value)
                  : setPassword(event.target.value)
              }
              required
            />
          </div>
        )}

        {mode === "resetConfirm" && (
          <div className="space-y-3">
            <label className="block text-xs text-muted" htmlFor="reset-token">
              {t("auth.resetToken")}
            </label>
            <input
              id="reset-token"
              type="text"
              className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink"
              value={resetToken}
              onChange={(event) => setResetToken(event.target.value)}
              required
            />
          </div>
        )}

        {(message || error || resetInfo) && (
          <div className="rounded-xl border border-border bg-surface-2 p-3 text-xs text-muted-2">
            {message || error || resetInfo}
          </div>
        )}

        <button
          type="submit"
          className="w-full rounded-full bg-ember px-4 py-2 text-sm font-semibold text-on-accent"
          disabled={busy}
        >
          {busy
            ? t("auth.loading")
            : mode === "register"
              ? t("auth.registerCta")
              : mode === "reset"
                ? t("auth.resetCta")
                : mode === "resetConfirm"
                  ? t("auth.resetConfirmCta")
                : t("auth.cta")}
        </button>

        <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-muted-2">
          {mode === "login" && (
            <>
              <button type="button" onClick={() => setMode("register")} className="underline">
                {t("auth.createAccount")}
              </button>
              <button type="button" onClick={() => setMode("reset")} className="underline">
                {t("auth.forgotPassword")}
              </button>
            </>
          )}
          {mode !== "login" && (
            <button type="button" onClick={() => setMode("login")} className="underline">
              {t("auth.backToLogin")}
            </button>
          )}
        </div>
      </form>
    </div>
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
