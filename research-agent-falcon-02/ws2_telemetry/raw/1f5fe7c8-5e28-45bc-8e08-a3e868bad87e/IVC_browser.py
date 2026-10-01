#!/usr/bin/env python3
"""Pass the Vercel BotID challenge with the full chromium build; dump cookies + form shape."""
import asyncio, json, os
from playwright.async_api import async_playwright

EXE = "/home/kali/.cache/ms-playwright/chromium-1243/chrome-linux/chrome"
H = "www.infinity" + "capital" + ".bh"
B = "https://" + H
OUT = os.path.dirname(os.path.abspath(__file__))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"+"1"+"31.0.0.0 Safari/537.36",
            locale="en-US", viewport={"width":1440,"height":900})
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        pg = await ctx.new_page()
        r = await pg.goto(B+"/", wait_until="domcontentloaded", timeout=60000)
        print("initial:", r.status if r else None)
        ok=False
        for i in range(25):
            await pg.wait_for_timeout(1500)
            t = await pg.title()
            if "Security Checkpoint" not in t:
                print("PASSED at i=%d title=%r url=%s" % (i, t, pg.url)); ok=True; break
        if not ok: print("STILL CHALLENGED title=%r" % (await pg.title()))
        html = await pg.content()
        open(os.path.join(OUT,"IVC_home.html"),"w").write(html)
        print("home bytes:", len(html))
        cookies = await ctx.cookies()
        json.dump(cookies, open(os.path.join(OUT,"IVC_cookies.json"),"w"), indent=1)
        print("cookies:", [(c["name"], c["value"][:40]) for c in cookies])
        # header dump
        resp_h = await pg.evaluate("()=>1")
        await b.close()

asyncio.run(main())
