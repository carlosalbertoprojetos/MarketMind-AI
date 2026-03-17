import { defineConfig } from "@playwright/test";

const shouldStart = process.env.E2E_START_SERVER === "true";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    viewport: { width: 1280, height: 720 }
  },
  webServer: shouldStart
    ? {
        command: "npm run dev -- --port 3000",
        url: "http://localhost:3000",
        reuseExistingServer: true,
        timeout: 120_000
      }
    : undefined
});
