const { chromium } = require('playwright-core');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
  });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
  });
  const page = await ctx.newPage();
  const r = await page.goto('https://www.infinitycapital.bh/', { waitUntil: 'domcontentloaded', timeout: 90000 });
  console.log('status', r && r.status());
  // wait for Vercel challenge to resolve (it reloads on success)
  await page.waitForTimeout(12000);
  console.log('title:', await page.title());
  console.log('url:', page.url());
  const html = await page.content();
  fs.writeFileSync('/work/evidence/home_after_challenge.html', html);
  console.log('html len', html.length);
  const cookies = await ctx.cookies();
  console.log('COOKIES:', JSON.stringify(cookies, null, 1));
  fs.writeFileSync('/work/evidence/cookies.json', JSON.stringify(cookies, null, 1));
  // look for contact form
  const hasForm = await page.evaluate(() => !!document.querySelector('form'));
  console.log('has form on home:', hasForm);
  await page.screenshot({ path: '/work/evidence/home.png', fullPage: false });
  await browser.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
