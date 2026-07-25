import { test, expect } from "@playwright/test";
import { CREDENTIALS, trackConsoleErrors } from "./helpers";

test.describe("Login view", () => {
  test("login page loads without console errors and shows the sign-in form", async ({ page }) => {
    const errors = trackConsoleErrors(page);
    await page.goto("/");
    await expect(page.locator("#loginView")).toBeVisible();
    await expect(page.getByRole("heading", { name: "AI Task Manager" })).toBeVisible();
    await expect(page.locator("#username")).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
    // The app intentionally probes GET /profile on load to restore an existing
    // session; when logged out this returns 401 and the browser logs it as a
    // resource error. That is expected behaviour, so it is filtered out here.
    const unexpected = errors.filter((e) => !/401|UNAUTHORIZED/i.test(e));
    expect(unexpected, `Console errors found: ${unexpected.join("; ")}`).toHaveLength(0);
  });

  test("user can sign in with valid credentials and reach the task manager", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill(CREDENTIALS.username);
    await page.locator("#password").fill(CREDENTIALS.password);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#appView")).toBeVisible();
    await expect(page.locator("#loginView")).toBeHidden();
    await expect(page.locator("#userBadge")).toHaveText(CREDENTIALS.username);
  });

  test("user sees an 'Invalid credentials' error when signing in with a wrong password", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill(CREDENTIALS.username);
    await page.locator("#password").fill("wrong-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#loginError")).toBeVisible();
    await expect(page.locator("#loginError")).toHaveText("Invalid credentials");
    await expect(page.locator("#appView")).toBeHidden();
  });

  test("user sees an error when submitting the login form with empty fields", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill("");
    await page.locator("#password").fill("");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#loginError")).toBeVisible();
    await expect(page.locator("#loginError")).toHaveText("Username and password required");
  });

  test("user sees an error when signing in with a non-existent username", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill("no-such-user");
    await page.locator("#password").fill("whatever");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#loginError")).toBeVisible();
    await expect(page.locator("#loginError")).toHaveText("Invalid credentials");
  });

  test("a previous error message is cleared when the user retries signing in", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill(CREDENTIALS.username);
    await page.locator("#password").fill("wrong-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#loginError")).toBeVisible();
    await page.locator("#password").fill(CREDENTIALS.password);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#appView")).toBeVisible();
    await expect(page.locator("#loginError")).toBeHidden();
  });

  test("session is restored on page reload so a logged-in user skips the login form", async ({ page }) => {
    await page.goto("/");
    await page.locator("#username").fill(CREDENTIALS.username);
    await page.locator("#password").fill(CREDENTIALS.password);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.locator("#appView")).toBeVisible();
    await page.reload();
    await expect(page.locator("#appView")).toBeVisible();
    await expect(page.locator("#loginView")).toBeHidden();
  });
});
