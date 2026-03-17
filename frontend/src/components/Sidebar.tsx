"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/auth/AuthProvider";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n/I18nProvider";

export default function Sidebar() {
  const pathname = usePathname();
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [workspaceName, setWorkspaceName] = useState("Brand Lab");

  const navItems = [
    { label: t("nav.dashboard"), href: "/" },
    { label: t("nav.campaigns"), href: "/campaigns" },
    { label: t("nav.content"), href: "/content" },
    { label: t("nav.generator"), href: "/generator" },
    { label: t("nav.calendar"), href: "/calendar" },
    { label: t("nav.analytics"), href: "/analytics" }
  ];

  useEffect(() => {
    if (!accessToken) return;
    let alive = true;
    void (async () => {
      try {
        const workspaces = await apiFetch<Array<{ id: string; name: string }>>(
          "/workspaces",
          {},
          accessToken
        );
        if (alive && workspaces.length) {
          setWorkspaceName(workspaces[0].name);
        }
      } catch {
        if (alive) {
          setWorkspaceName("Brand Lab");
        }
      }
    })();
    return () => {
      alive = false;
    };
  }, [accessToken]);

  return (
    <aside className="flex flex-col justify-between bg-smoke px-6 py-8 text-haze">
      <div className="space-y-10">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-haze/60">{t("app.name")}</p>
          <h2 className="mt-3 font-display text-2xl font-semibold">{t("app.tagline")}</h2>
          <div className="mt-4 flex items-center gap-2 text-[11px] text-haze/70">
            <span className="h-2 w-2 rounded-full bg-success" />
            {t("sidebar.status")}
          </div>
        </div>

        <nav className="space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "block rounded-full border px-4 py-2 text-sm transition",
                pathname === item.href
                  ? "border-haze/50 bg-surface/10 text-haze"
                  : "border-transparent text-haze/80 hover:border-haze/30 hover:text-haze"
              ].join(" ")}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="space-y-3 text-xs text-haze/70">
        <p>{t("sidebar.workspace", { name: workspaceName })}</p>
        <p>{t("sidebar.plan", { plan: "Enterprise" })}</p>
        <button className="w-full rounded-full border border-haze/30 px-4 py-2 text-left text-xs text-haze/80">
          {t("sidebar.settings")}
        </button>
      </div>
    </aside>
  );
}
