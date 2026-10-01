#!/usr/bin/env python3
"""Independent repro: drive real Chromium at https://www.infinitycapital.bh/
1) load /contact-us/ (pass Vercel challenge)
2) dump the form fields the site actually posts to /api/send
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

URL = "https://www.infinitycapital.bh/contact-us/"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = await b.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/" + "1" + "31.0.0.0 Safari/537.36"),
            locale="en-US",
            viewport={"width": 1440, "height": 900},
        )
        pg = await ctx.new_page()
        reqs = []
        pg.on("request", lambda r: reqs.append((r.method, r.url)))
        r = await pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        print("initial status:", r.status if r else None)
        # wait out the Vercel interstitial
        for i in range(20):
            await pg.wait_for_timeout(1500)
            t = await pg.title()
            if "Security Checkpoint" not in t:
                break
        await pg.wait_for_load_state("networkidle", timeout=60000)
        print("final title:", await pg.title())
        print("final url:", pg.url)
        html = await pg.content()
        open("/work/IVR_contact_browser.html", "w").write(html)
        print("html bytes:", len(html))

        # dump forms
        forms = await pg.evaluate("""() => Array.from(document.forms).map(f => ({
            action: f.action, method: f.method,
            fields: Array.from(f.elements).map(e => ({name: e.name, type: e.type, tag: e.tagName, id: e.id}))
        }))""")
        print("FORMS:", json.dumps(forms, indent=1)[:3000])

        # any inline script referencing /api/send
        s = await pg.evaluate("""() => Array.from(document.scripts).map(x=>x.textContent||'').join('\\n')""")
        idx = s.find("/api/send")
        if idx != -1:
            print("=== SNIPPET AROUND /api/send ===")
            print(s[max(0,idx-2500):idx+1500])
        open("/work/IVR_scripts.txt", "w").write(s)
        print("=== network requests ===")
        for m, u in reqs:
            print(m, u)
        await b.close()

asyncio.run(main())
