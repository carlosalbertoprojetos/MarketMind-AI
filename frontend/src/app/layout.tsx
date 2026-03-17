import "./globals.css";
import AuthGate from "@/auth/AuthGate";
import Sidebar from "@/components/Sidebar";
import TopNavbar from "@/components/TopNavbar";
import AppProviders from "@/providers/AppProviders";

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" data-theme="light" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AppProviders>
          <AuthGate>
            <div className="app-shell">
              <Sidebar />
              <div className="min-h-screen bg-transparent">
                <TopNavbar />
                <main className="px-8 pb-12">
                  {children}
                </main>
              </div>
            </div>
          </AuthGate>
        </AppProviders>
      </body>
    </html>
  );
}
