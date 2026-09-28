import { test, expect } from '@playwright/test';

test.describe('Varsha Walking Skeleton Demo Journey (iter-0)', () => {
  test('Console renders wordmark, provenance chip, lead selector, and drawer table', async ({ page }) => {
    await page.goto('/');

    // 1. Verify wordmark and provenance chip
    await expect(page.locator('text=VARSHA')).toBeVisible();
    await expect(page.locator('text=SYNTHETIC DEMO')).toBeVisible();

    // 2. Test lead time switching
    const lead2Btn = page.locator('button:has-text("+D2")');
    await expect(lead2Btn).toBeVisible();
    await lead2Btn.click();

    // 3. Test layer switching
    const p64Btn = page.locator('button:has-text("Prob ≥ 64.5 mm (Heavy)")');
    await expect(p64Btn).toBeVisible();
    await p64Btn.click();

    // 4. Test district drawer interaction
    await expect(page.locator('text=District Guidance Table')).toBeVisible();

    // 5. Test theme toggle
    const themeBtn = page.locator('button:has-text("Dark Theme"), button:has-text("Light Theme")');
    await expect(themeBtn).toBeVisible();
    await themeBtn.click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', /light|dark/);

    // 6. Navigate to Verification page
    await page.click('text=Verification (D5)');
    await expect(page).toHaveURL(/\/verification/);
    await expect(page.locator('text=Benchmark Model Ladder Verification')).toBeVisible();
    await expect(page.locator('text=B4: Regime Hurdle LightGBM')).toBeVisible();
    await expect(page.locator('text=Honesty & Scientific Provenance Panel')).toBeVisible();

    // 7. Navigate to Regimes page
    await page.click('text=Regimes (D1)');
    await expect(page).toHaveURL(/\/regimes/);
    await expect(page.locator('text=Active Monsoon')).toBeVisible();
    await expect(page.locator('text=Break Monsoon')).toBeVisible();

    // 8. Navigate to Method & Limits
    await page.click('text=Method & Limits');
    await expect(page).toHaveURL(/\/method/);
    await expect(page.locator('text=24-Hour Accumulation Window Alignment')).toBeVisible();
  });
});
