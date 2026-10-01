const {chromium} = require('playwright');
const fs = require('fs');
const EXE = process.env.HOME + '/.cache/ms-playwright/chromium-1187/chrome-linux/chrome';
(async () => {
  const b = await chromium.launch({
    executablePath: EXE,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
  });
  const ctx = await b.newContext({
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: {width: 1366, height: 900},
    locale: 'en-US',
  });
  const pg = await ctx.newPage();
  await pg.goto('https://www.infinitycapital.bh/contact', {waitUntil: 'domcontentloaded', timeout: 60000});
  let solved = false;
  for (let i = 0; i < 45; i++) {
    await pg.waitForTimeout(1000);
    const html = await pg.content();
    if (!html.includes('Security Checkpoint')) { console.log('SOLVED after ' + (i+1) + 's'); solved = true; break; }
  }
  if (!solved) console.log('STILL CHALLENGED url=' + pg.url());
  const cookies = await ctx.cookies();
  console.log('COOKIES=' + JSON.stringify(cookies.map(c => ({name:c.name, value:c.value.slice(0,200), domain:c.domain}))));
  const st = await ctx.storageState();
  fs.writeFileSync(process.env.WORK_PATH + '/solved_state.json', JSON.stringify(st, null, 1));
  fs.writeFileSync(process.env.WORK_PATH + '/solved.html', await pg.content());
  console.log('TITLE=' + (await pg.title()));

  // fire real API calls from inside the solved page context
  const probe = await pg.evaluate(async () => {
    const out = {};
    const doPost = async (path, body) => {
      try {
        const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
        out[path] = {status: r.status, body: (await r.text()).slice(0, 800)};
      } catch (e) { out[path] = {err: e.message}; }
    };
    await doPost('/api/send', {fname:'VAPT', lname:'Probe', areacode:'+973', tel:'3600000', cname:'vapt-tester', subject:'Inquiry', msg:'Authorized VAPT test message.'});
    return out;
  });
  console.log('API=' + JSON.stringify(probe, null, 1));
  await b.close();
})().catch(e => { console.log('FATAL', e.message); process.exit(1); });
