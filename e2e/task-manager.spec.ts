import { test, expect } from "@playwright/test";
import { login, clearTasks, trackConsoleErrors } from "./helpers";

test.describe("Task manager view", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearTasks(page);
    await page.reload();
    await expect(page.locator("#appView")).toBeVisible();
  });

  test("task manager loads without console errors and shows the header, task form and empty state", async ({ page }) => {
    const errors = trackConsoleErrors(page);
    await page.reload();
    await expect(page.locator("#appView")).toBeVisible();
    await expect(page.locator("#userBadge")).toHaveText("admin");
    await expect(page.getByRole("button", { name: "Logout" })).toBeVisible();
    await expect(page.locator("#taskTitle")).toBeVisible();
    await expect(page.getByRole("button", { name: "Add" })).toBeVisible();
    await expect(page.locator("#emptyState")).toBeVisible();
    await expect(page.locator("#emptyState")).toContainText("No tasks yet");
    expect(errors, `Console errors found: ${errors.join("; ")}`).toHaveLength(0);
  });

  test("user can create a new task and see it appear in the task list", async ({ page }) => {
    await page.locator("#taskTitle").fill("Buy groceries");
    await page.getByRole("button", { name: "Add" }).click();
    const item = page.locator("#taskList .list-group-item");
    await expect(item).toHaveCount(1);
    await expect(item).toContainText("Buy groceries");
    await expect(page.locator("#emptyState")).toBeHidden();
    // input is cleared after successful creation
    await expect(page.locator("#taskTitle")).toHaveValue("");
  });

  test("submitting the task form with an empty title does not create a task", async ({ page }) => {
    await page.locator("#taskTitle").fill("   ");
    await page.getByRole("button", { name: "Add" }).click();
    await expect(page.locator("#taskList .list-group-item")).toHaveCount(0);
  });

  test("user can mark a task as completed and it is shown struck through", async ({ page }) => {
    await page.locator("#taskTitle").fill("Finish report");
    await page.getByRole("button", { name: "Add" }).click();
    const item = page.locator("#taskList .list-group-item");
    await expect(item).toHaveCount(1);
    await item.locator("input[type=checkbox]").check();
    await expect(item.locator("span")).toHaveClass(/text-decoration-line-through/);
    await expect(item.locator("input[type=checkbox]")).toBeChecked();
  });

  test("user can un-complete a completed task and the strikethrough is removed", async ({ page }) => {
    await page.locator("#taskTitle").fill("Water plants");
    await page.getByRole("button", { name: "Add" }).click();
    const item = page.locator("#taskList .list-group-item");
    await item.locator("input[type=checkbox]").check();
    await expect(item.locator("span")).toHaveClass(/text-decoration-line-through/);
    await item.locator("input[type=checkbox]").uncheck();
    await expect(item.locator("span")).not.toHaveClass(/text-decoration-line-through/);
  });

  test("user can delete a task and the empty state reappears when the list is empty", async ({ page }) => {
    await page.locator("#taskTitle").fill("Temporary task");
    await page.getByRole("button", { name: "Add" }).click();
    const item = page.locator("#taskList .list-group-item");
    await expect(item).toHaveCount(1);
    await item.getByRole("button", { name: "Delete" }).click();
    await expect(page.locator("#taskList .list-group-item")).toHaveCount(0);
    await expect(page.locator("#emptyState")).toBeVisible();
  });

  test("multiple tasks can be created and are all listed", async ({ page }) => {
    for (const title of ["Task one", "Task two", "Task three"]) {
      await page.locator("#taskTitle").fill(title);
      await page.getByRole("button", { name: "Add" }).click();
      await expect(page.locator("#taskList .list-group-item", { hasText: title })).toBeVisible();
    }
    await expect(page.locator("#taskList .list-group-item")).toHaveCount(3);
  });

  test("task titles containing HTML are rendered as text, not injected markup (XSS check)", async ({ page }) => {
    const payload = '<img src=x onerror="window.__xss=1">';
    await page.locator("#taskTitle").fill(payload);
    await page.getByRole("button", { name: "Add" }).click();
    const item = page.locator("#taskList .list-group-item");
    await expect(item).toHaveCount(1);
    await expect(item.locator("span")).toHaveText(payload);
    const xss = await page.evaluate(() => (window as any).__xss);
    expect(xss, "XSS payload executed").toBeUndefined();
  });

  test("tasks persist across a page reload", async ({ page }) => {
    await page.locator("#taskTitle").fill("Persistent task");
    await page.getByRole("button", { name: "Add" }).click();
    await expect(page.locator("#taskList .list-group-item")).toHaveCount(1);
    await page.reload();
    await expect(page.locator("#appView")).toBeVisible();
    await expect(page.locator("#taskList .list-group-item", { hasText: "Persistent task" })).toBeVisible();
  });

  test("user can log out and is returned to the login form", async ({ page }) => {
    await page.getByRole("button", { name: "Logout" }).click();
    await expect(page.locator("#loginView")).toBeVisible();
    await expect(page.locator("#appView")).toBeHidden();
    // Session is really gone: reloading keeps the login form visible.
    await page.reload();
    await expect(page.locator("#loginView")).toBeVisible();
  });
});
