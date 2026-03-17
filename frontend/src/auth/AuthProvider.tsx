"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError, apiFetch } from "@/lib/api";

type User = {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_superuser: boolean;
};

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

type AuthContextValue = {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const ACCESS_KEY = "marketmind.access_token";
const REFRESH_KEY = "marketmind.refresh_token";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const storedAccess = window.localStorage.getItem(ACCESS_KEY);
    const storedRefresh = window.localStorage.getItem(REFRESH_KEY);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAccessToken(storedAccess);
    setRefreshToken(storedRefresh);
    setLoading(false);
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(ACCESS_KEY);
      window.localStorage.removeItem(REFRESH_KEY);
    }
  }, []);

  const refreshMe = useCallback(
    async (tokenOverride?: string | null) => {
      const token = tokenOverride ?? accessToken;
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const profile = await apiFetch<User>("/users/me", {}, token);
        setUser(profile);
      } catch (err) {
        setUser(null);
        if (err instanceof ApiError && err.status === 401) {
          logout();
        }
      }
    },
    [accessToken, logout]
  );

  useEffect(() => {
    if (!accessToken) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setUser(null);
      return;
    }
    void refreshMe();
  }, [accessToken, refreshMe]);

  const login = useCallback(
    async (email: string, password: string) => {
      setError(null);
      const payload = await apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setAccessToken(payload.access_token);
      setRefreshToken(payload.refresh_token);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(ACCESS_KEY, payload.access_token);
        window.localStorage.setItem(REFRESH_KEY, payload.refresh_token);
      }
      await refreshMe(payload.access_token);
    },
    [refreshMe]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken,
      refreshToken,
      user,
      loading,
      error,
      login,
      logout,
      refreshMe
    }),
    [accessToken, refreshToken, user, loading, error, login, logout, refreshMe]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
