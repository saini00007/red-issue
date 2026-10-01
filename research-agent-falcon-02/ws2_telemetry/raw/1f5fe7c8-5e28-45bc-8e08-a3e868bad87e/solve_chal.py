import asyncio, json, sys
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx = await b.new_context()
        pg = await ctx.new_page()
        await pg.goto("https://www.infinitycapital.bh/contact", wait_until="domcontentloaded", timeout=60000)
        # wait for the challenge to resolve
        for i in range(40):
            await pg.wait_for_timeout(1000)
            t = pg.url
            body = await pg.content()
            if "Security Checkpoint" not in body:
                print("CHALLENGE SOLVED after", i+1, "s url=", t)
                break
        else:
            print("STILL CHALLENGED url=", pg.url)
        cookies = await ctx.cookies()
        print("COOKIES:", json.dumps(cookies, indent=1))
        st = await ctx.storage_state()
        open("/work/solved_state.json","w").write(json.dumps(st, indent=1))
        open("/work/solved.html","w").write(await pg.content())
        # now fire the real form submit via fetch in page context (bypasses CORS/challenge)
        res = await pg.evaluate("""async () => {
          const r = await fetch('/api/send', {method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({fname:'VAPT',lname:'Probe',areacode:'+973',tel:'3600000',cname:'vapt-tester',subject:'Inquiry',msg:'Authorized VAPT test.'})});
          return {status:r.status, body:(await r.text()).slice(0,2000)};
        }""")
        print("API_SEND:", json.dumps(res))
        await b.close()

asyncio.run(main())
