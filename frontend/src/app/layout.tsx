import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import TopNavbar from "@/components/TopNavbar";

export const metadata: Metadata = {
  title: "MarketMind-IA",
  description: "Content Intelligence OS"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="app-shell">
          <Sidebar />
          <div className="min-h-screen bg-transparent">
            <TopNavbar />
            <main className="px-8 pb-12">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}