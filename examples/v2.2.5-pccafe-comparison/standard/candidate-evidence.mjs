import { chromium } from '../../../plugins/genscaff/skills/genscaff-release-audit/scripts/node_modules/playwright/index.mjs';
const browser = await chromium.launch({ headless: true });
for (const name of ['candidate-a', 'candidate-b']) {
  for (const viewport of [{ width: 1440, height: 1000, label: 'desktop' }, { width: 390, height: 844, label: 'mobile' }]) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
    await page.goto(`http://127.0.0.1:8835/standard/${name}.html`, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `${name}-${viewport.label}.png`, fullPage: true });
    await page.close();
  }
}
await browser.close();
