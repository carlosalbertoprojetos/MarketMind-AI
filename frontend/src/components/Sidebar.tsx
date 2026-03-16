"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Dashboard", href: "/" },
  { label: "Campaign Manager", href: "/campaigns" },
  { label: "Content Studio", href: "/content" },
  { label: "AI Generator", href: "/generator" },
  { label: "Calendar", href: "/calendar" },
  { label: "Analytics", href: "/analytics" }
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col justify-between bg-smoke px-6 py-8 text-haze">
      <div className="space-y-10">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-haze/60">MarketMind-IA</p>
          <h2 className="mt-3 font-display text-2xl font-semibold">Content Intelligence OS</h2>
          <div className="mt-4 flex items-center gap-2 text-[11px] text-haze/70">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Operacao autonoma ativa
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
                  ? "border-haze/50 bg-white/10 text-white"
                  : "border-transparent text-haze/80 hover:border-haze/30 hover:text-white"
              ].join(" ")}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="space-y-3 text-xs text-haze/70">
        <p>Workspace: Brand Lab</p>
        <p>Plano: Enterprise</p>
        <button className="w-full rounded-full border border-haze/30 px-4 py-2 text-left text-xs text-haze/80">
          Configuracoes
        </button>
      </div>
    </aside>
  );
}
