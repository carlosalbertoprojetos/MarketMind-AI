import { test, expect, type APIRequestContext, type Page } from "@playwright/test";

const email = process.env.E2E_EMAIL ?? "admin@marketmind.ai";
const password = process.env.E2E_PASSWORD ?? "secret";
const apiBase = process.env.E2E_API_BASE_URL ?? "http://localhost:8003/api/v1";

async function signIn(page: Page, request: APIRequestContext) {
  const response = await request.post(`${apiBase}/auth/login`, {
    data: { email, password }
  });
  if (!response.ok()) {
    throw new Error(`Auth failed with status ${response.status()}`);
  }
  const payload = (await response.json()) as { access_token: string; refresh_token: string };
  await page.addInitScript(
    ([accessToken, refreshToken]) => {
      window.localStorage.setItem("marketmind.access_token", accessToken);
      window.localStorage.setItem("marketmind.refresh_token", refreshToken);
    },
    [payload.access_token, payload.refresh_token]
  );
}

test("login and dashboard loads", async ({ page, request }) => {
  await signIn(page, request);
  await page.goto("/");

  await expect(
    page.getByText(/dashboard de inteligencia autonoma|autonomous intelligence dashboard/i)
  ).toBeVisible();
});

test("theme and language toggles update document", async ({ page, request }) => {
  await signIn(page, request);
  await page.goto("/");

  const initialTheme = await page.evaluate(() => document.documentElement.dataset.theme);
  await page.getByLabel(/alternar tema|toggle theme/i).click();
  const nextTheme = await page.evaluate(() => document.documentElement.dataset.theme);
  expect(nextTheme).not.toEqual(initialTheme);

  const initialLang = await page.evaluate(() => document.documentElement.lang);
  await page.getByLabel(/mudar para|switch to/i).click();
  const nextLang = await page.evaluate(() => document.documentElement.lang);
  expect(nextLang).not.toEqual(initialLang);
});
