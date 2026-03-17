"use client";

import { AuthProvider } from "@/auth/AuthProvider";
import FloatingControls from "@/components/FloatingControls";
import { I18nProvider } from "@/i18n/I18nProvider";
import { ThemeProvider } from "@/theme/ThemeProvider";

export default function AppProviders({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider>
      <I18nProvider>
        <AuthProvider>
          {children}
          <FloatingControls />
        </AuthProvider>
      </I18nProvider>
    </ThemeProvider>
  );
}
