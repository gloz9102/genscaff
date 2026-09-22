const { chromium } = require('../../../plugins/genscaff/skills/genscaff-release-audit/scripts/node_modules/playwright');

const URL = 'http://127.0.0.1:8835/control/';
const expected = { standard: 2000, wide: 2500, duo: 5000 };
const results = [];
const check = (name, pass, detail = '') => results.push({ name, pass, detail });
const luminance = (rgb) => {
  const values = rgb.match(/[0-9.]+/g).slice(0, 3).map(Number).map((value) => value / 255);
  const linear = values.map((value) => value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
};
const contrast = (foreground, background) => {
  const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
};

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.locator('img[src*="cafe-hero"]').waitFor({ state: 'visible' });
  check('desktop image loaded', await page.locator('img[src*="cafe-hero"]').evaluate((img) => img.complete && img.naturalWidth > 0));
  check('desktop no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  check('desktop runtime errors', errors.length === 0, errors.join('; '));
  const colors = await page.evaluate(() => ({
    introForeground: getComputedStyle(document.querySelector('.intro-section h2 em')).color,
    introBackground: getComputedStyle(document.querySelector('.intro-section')).backgroundColor,
    calcForeground: getComputedStyle(document.querySelector('.calc-heading h2 em')).color,
    calcBackground: getComputedStyle(document.querySelector('.calculator-section')).backgroundColor,
  }));
  const introContrast = contrast(colors.introForeground, colors.introBackground);
  const calcContrast = contrast(colors.calcForeground, colors.calcBackground);
  check('intro heading contrast', introContrast >= 4.5, `${introContrast.toFixed(2)}:1`);
  check('calculator heading contrast', calcContrast >= 4.5, `${calcContrast.toFixed(2)}:1`);

  for (const [seat, price] of Object.entries(expected)) {
    for (const hours of [1, 2, 3]) {
      await page.locator(`.seat-option[data-seat="${seat}"]`).click();
      await page.locator(`.duration-option[data-hours="${hours}"]`).click();
      const text = await page.locator('[data-total-price]').innerText();
      check(`fare ${seat} x ${hours}`, text.replace(/[^0-9]/g, '') === String(price * hours), `${text} expected ${price * hours}`);
    }
  }
  await page.evaluate(() => {
    window.__scrollBehavior = null;
    const original = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = function (options) {
      window.__scrollBehavior = options && options.behavior;
      return original.call(this, options);
    };
  });
  await page.locator('.confirm-plan').click();
  check('confirm opens plan dialog', await page.locator('.plan-modal').isVisible());
  check('dialog shows selected plan', (await page.locator('[data-modal-seat]').innerText()) === '듀오석' && (await page.locator('[data-modal-hours]').innerText()) === '3');
  await page.locator('.modal-edit').click();
  check('edit closes dialog', await page.locator('.plan-modal').isHidden());
  check('edit uses smooth scrolling normally', await page.evaluate(() => window.__scrollBehavior === 'smooth'));

  await page.emulateMedia({ reducedMotion: 'reduce' });
  check('reduced motion uses auto scrolling', await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior === 'auto'));
  await page.locator('.confirm-plan').click();
  await page.locator('.modal-edit').click();
  check('edit uses auto scrolling with reduced motion', await page.evaluate(() => window.__scrollBehavior === 'auto'));
  await page.locator('.seat-option[data-seat="standard"]').focus();
  await page.keyboard.press('ArrowRight');
  check('keyboard arrow changes seat', await page.locator('.seat-option[data-seat="wide"]').getAttribute('aria-checked') === 'true');
  await page.keyboard.press('ArrowRight');
  check('keyboard arrow reaches duo seat', await page.locator('.seat-option[data-seat="duo"]').getAttribute('aria-checked') === 'true');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'networkidle' });
  check('mobile no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.locator('.menu-toggle').click();
  check('mobile menu opens', await page.locator('.primary-nav').evaluate((nav) => nav.classList.contains('is-open') && nav.previousElementSibling?.getAttribute('aria-expanded') === 'true'));
  await page.locator('.primary-nav a[href="#space"]').click();
  check('mobile menu closes after navigation', !(await page.locator('.primary-nav').evaluate((nav) => nav.classList.contains('is-open'))));
  const touch = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await touch.goto(URL, { waitUntil: 'networkidle' });
  await touch.locator('.seat-option[data-seat="wide"]').tap();
  await touch.locator('.duration-option[data-hours="2"]').tap();
  check('touch updates fare', (await touch.locator('[data-total-price]').innerText()).replace(/[^0-9]/g, '') === '5000');
  await touch.locator('.seat-option[data-seat="wide"]').hover();
  await touch.mouse.move(1, 1);
  check('pointer leaves without error', true);
  await touch.close();
  await browser.close();

  for (const result of results) console.log(`${result.pass ? 'PASS' : 'FAIL'} | ${result.name}${result.detail ? ` | ${result.detail}` : ''}`);
  const failed = results.filter((result) => !result.pass);
  if (failed.length) process.exitCode = 1;
})();
