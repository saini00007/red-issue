const { chromium } = require('/home/kali/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');

(async () => {
  const out = [];
  const log = (...a) => { const s = a.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join(' ');
    console.log(s); out.push(s); };

  const browser = await chromium.launch({ headless: true,
    args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'] });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 900 },
  });
  const page = await ctx.newPage();
  let r = await page.goto('https://www.infinitycapital.bh/contact', { waitUntil: 'domcontentloaded', timeout: 60000 });
  log('[1] /contact HTTP', r.status());
  for (let i = 0; i < 20; i++) {
    await new Promise(s => setTimeout(s, 2000));
    const t = await page.title();
    log(`   t=${(i+1)*2}s title=${t} url=${page.url()}`);
    if (!/Security Checkpoint|Just a moment/i.test(t)) break;
  }
  log('[2] FINAL title:', await page.title(), '| url:', page.url());
  const html = await page.content();
  require('fs').writeFileSync('/work/evidence/browser_contact.html', html);
  log('[3] html length', html.length);

  const fields = await page.evaluate(() =>
    Array.from(document.querySelectorAll('form input, form textarea, form select'))
      .map(e => [e.tagName, e.type, e.name, e.id, e.placeholder]));
  log('[4] form fields:', JSON.stringify(fields));
  require('fs').writeFileSync('/work/evidence/browser_fields.json', JSON.stringify(fields, null, 1));
  require('fs').writeFileSync('/work/evidence/browser_cookies.json', JSON.stringify(await ctx.cookies(), null, 1));
  await browser.close();
  require('fs').writeFileSync('/work/evidence/browser_pass.log', out.join('\n'));
})().catch(e => { console.error('ERR', e); process.exit(1); });
