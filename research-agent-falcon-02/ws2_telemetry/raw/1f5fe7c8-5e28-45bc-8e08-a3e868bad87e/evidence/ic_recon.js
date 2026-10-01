const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const ctx = await b.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
    locale: 'en-US',
  });
  const page = await ctx.newPage();

  const captured = [];
  page.on('request', r => {
    if (r.url().includes('/api/send')) {
      captured.push({ method: r.method(), url: r.url(), headers: r.headers(), postData: r.postData() });
    }
  });

  await page.goto('https://www.infinitycapital.bh/contact', { waitUntil: 'networkidle', timeout: 90000 });
  console.log('TITLE:', await page.title());
  console.log('URL  :', page.url());

  // dump CMS-provided `targets` from the Next.js RSC payload embedded in the page
  const embedded = await page.content();
  const m = embedded.match(/targets[^,]{0,200}/g);
  console.log('EMBEDDED targets occurrences:', JSON.stringify(m));

  // Try to locate the React props blob holding the contact settings
  const settings = await page.evaluate(() => {
    const out = [];
    const scan = (node, depth) => {
      if (depth > 6 || !node) return;
      for (const k of Object.keys(node)) {
        try {
          if (node[k] && typeof node[k] === 'object') scan(node[k], depth + 1);
        } catch (e) {}
      }
      if (node.targets) out.push(node.targets);
      if (node.email) out.push({ email: node.email, tel1: node.tel1 });
    };
    for (const k of Object.keys(window)) {
      if (k.startsWith('__NEXT')) {
        try { scan(window[k], 0); } catch (e) {}
      }
    }
    return out;
  });
  console.log('SETTINGS:', JSON.stringify(settings));

  await page.screenshot({ path: '/work/evidence/contact_page.png', fullPage: false });
  console.log('CAPTURED_REQUESTS:', JSON.stringify(captured, null, 2));
  await b.close();
})().catch(e => { console.error('ERR', e); process.exit(1); });
