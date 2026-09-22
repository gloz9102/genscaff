import { chromium } from '../../../plugins/genscaff/skills/genscaff-release-audit/scripts/node_modules/playwright/index.mjs';

const baseUrl = 'http://127.0.0.1:8835/standard/';
const results = [];
const record = (name, pass, detail) => results.push({ name, pass, detail });

async function inspectPage(page, label) {
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.locator('img').first().waitFor({ state: 'visible' });
  await page.screenshot({ path: `evidence-${label}.png`, fullPage: true });
  const data = await page.evaluate(() => ({
    width: document.documentElement.scrollWidth,
    viewport: window.innerWidth,
    imageComplete: [...document.images].every((img) => img.complete && img.naturalWidth > 0),
    bodyHeight: document.body.scrollHeight,
  }));
  record(`${label} render`, consoleErrors.length === 0 && pageErrors.length === 0, `console=${consoleErrors.length}, page=${pageErrors.length}, body=${data.bodyHeight}px`);
  record(`${label} image`, data.imageComplete, `natural image loaded=${data.imageComplete}`);
  record(`${label} no horizontal overflow`, data.width <= data.viewport + 1, `scrollWidth=${data.width}, viewport=${data.viewport}`);
  return { consoleErrors, pageErrors, data };
}

async function checkPlanner(page) {
  const prices = { standard: 2000, wide: 2500, duo: 5000 };
  for (const [seat, rate] of Object.entries(prices)) {
    await page.locator(`input[name="seat"][value="${seat}"]`).check({ force: true });
    for (const duration of [1, 2, 3]) {
      await page.locator(`input[name="duration"][value="${duration}"]`).check({ force: true });
      const text = await page.locator('#total-price').textContent();
      const expected = `${(rate * duration).toLocaleString('ko-KR')}원`;
      record(`price ${seat} x ${duration}`, text === expected, `expected=${expected}, observed=${text}`);
    }
  }
  await page.locator('input[name="seat"][value="wide"]').check({ force: true });
  await page.locator('input[name="duration"][value="2"]').check({ force: true });
  await page.getByRole('button', { name: /방문 계획 확인/ }).click();
  const confirmationVisible = await page.locator('#plan-confirmation').isVisible();
  const confirmationText = await page.locator('#confirmed-plan').textContent();
  const confirmationPrice = await page.locator('#confirmed-price').textContent();
  record('plan confirmation', confirmationVisible && confirmationText === '와이드석 · 2시간' && confirmationPrice === '5,000원', `visible=${confirmationVisible}, plan=${confirmationText}, price=${confirmationPrice}`);
  await page.getByRole('button', { name: '수정하기' }).click();
  record('plan edit recovery', !(await page.locator('#plan-confirmation').isVisible()) && await page.locator('input[name="seat"]').first().evaluate((el) => document.activeElement === el), 'confirmation hidden and focus returned to seat choice');
}

async function checkKeyboard(page) {
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.locator('body').press('Tab');
  const firstFocus = await page.evaluate(() => ({ tag: document.activeElement?.tagName, text: document.activeElement?.textContent?.trim().slice(0, 30) }));
  const focusVisible = await page.evaluate(() => {
    const el = document.activeElement;
    if (!el) return false;
    const style = getComputedStyle(el);
    return style.outlineStyle !== 'none' && style.outlineWidth !== '0px';
  });
  record('keyboard first focus', focusVisible, `${firstFocus.tag}:${firstFocus.text}`);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.locator('.menu-toggle').focus();
  await page.keyboard.press('Enter');
  record('mobile menu keyboard trigger', await page.locator('#primary-nav').evaluate((el) => el.classList.contains('is-open')), 'Enter opened nav state');
  await page.keyboard.press('Escape');
  record('escape menu close', !(await page.locator('#primary-nav').evaluate((el) => el.classList.contains('is-open'))), 'Escape closes nav state');
}

async function checkHoverAndTouch() {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await desktop.goto(baseUrl, { waitUntil: 'networkidle' });
  const target = desktop.locator('.button-primary').first();
  const before = await target.evaluate((el) => getComputedStyle(el).backgroundColor);
  await target.hover();
  await desktop.waitForTimeout(240);
  const over = await target.evaluate((el) => getComputedStyle(el).backgroundColor);
  await desktop.mouse.move(10, 10);
  await desktop.waitForTimeout(240);
  const after = await target.evaluate((el) => getComputedStyle(el).backgroundColor);
  record('hover and pointer-out', over === 'rgb(241, 193, 124)' && before !== over && over !== after, `before=${before}, over=${over}, out=${after}`);
  await desktop.close();

  const touch = await browser.newPage({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  await touch.goto(baseUrl, { waitUntil: 'networkidle' });
  await touch.getByRole('button', { name: '메뉴 열기' }).tap();
  const menuOpen = await touch.locator('#primary-nav').evaluate((el) => el.classList.contains('is-open'));
  record('touch menu', menuOpen, 'tap opened mobile nav');
  await touch.close();
}

let browser;
try {
  browser = await chromium.launch({ headless: true });
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await inspectPage(desktop, 'desktop');
  await checkPlanner(desktop);
  await checkKeyboard(desktop);
  await desktop.close();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await inspectPage(mobile, 'mobile');
  const menuState = await mobile.locator('.menu-toggle').getAttribute('aria-expanded');
  record('mobile menu initial', menuState === 'false', `aria-expanded=${menuState}`);
  await mobile.close();

  const reduced = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await reduced.emulateMedia({ reducedMotion: 'reduce' });
  await reduced.goto(baseUrl, { waitUntil: 'networkidle' });
  const motion = await reduced.locator('body').evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches);
  record('reduced motion', motion, `media query=${motion}`);
  await reduced.close();
  await checkHoverAndTouch();
} finally {
  await browser?.close();
}

for (const result of results) console.log(`${result.pass ? 'PASS' : 'FAIL'} | ${result.name} | ${result.detail}`);
const failed = results.filter((result) => !result.pass);
if (failed.length) process.exitCode = 1;
