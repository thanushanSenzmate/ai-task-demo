import { Page, expect } from "@playwright/test";

export const CREDENTIALS = { username: "admin", password: "password123" };

/** Log in through the UI and wait for the task manager view to appear. */
export async function login(page: Page) {
  await page.goto("/");
  // If a previous session is restored, the app view may already be visible.
  const appView = page.locator("#appView");
  if (await appView.isVisible()) return;
  await page.locator("#username").fill(CREDENTIALS.username);
  await page.locator("#password").fill(CREDENTIALS.password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(appView).toBeVisible();
}

/** Delete every task via the API so each test starts from a clean slate. */
export async function clearTasks(page: Page) {
  const tasks: { id: number }[] = await page.evaluate(async () => {
    const res = await fetch("/tasks");
    return res.ok ? res.json() : [];
  });
  for (const t of tasks) {
    await page.evaluate((id) => fetch("/tasks/" + id, { method: "DELETE" }), t.id);
  }
}

/** Collect console errors emitted by the page for smoke assertions. */
export function trackConsoleErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  page.on("pageerror", (err) => errors.push(err.message));
  return errors;
}
