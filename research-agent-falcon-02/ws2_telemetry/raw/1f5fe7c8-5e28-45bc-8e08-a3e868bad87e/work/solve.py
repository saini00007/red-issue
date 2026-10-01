import asyncio, json, sys
from playwright.async_api import async_playwright

TARGET = "https://www.infinitycapital.bh/"

async def main():
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width":1440,"height":900},
        )
        page = await ctx.new_page()
        try:
            r = await page.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
            print("initial status:", r.status if r else None)
        except Exception as e:
            print("goto err:", e)
        # Vercel checkpoint auto-solves in ~1-2s; wait
        for i in range(20):
            await page.wait_for_timeout(1500)
            t = await page.title()
            print("t=%ds title=%r url=%s" % ((i+1)*1.5, t, page.url))
            if "Checkpoint" not in t and "403" not in t and "Forbidden" not in t:
                break
        html = await page.content()
        open("work/browser_home.html","w").write(html)
        out["title"] = await page.title()
        out["url"] = page.url
        out["html_len"] = len(html)
        cookies = await ctx.cookies()
        out["cookies"] = cookies
        # header format for curl
        hdrs = "; ".join("%s=%s" % (c["name"], c["value"]) for c in cookies)
        out["cookie_header"] = hdrs
        # try a few paths and dump status
        for path in ["/api/","/login","/_next/image?url=http%3A%2F%2F127.0.0.1%2Fx.png&w=128&q=75","/404"]:
            try:
                resp = await page.goto("https://www.infinitycapital.bh"+path, wait_until="domcontentloaded", timeout=30000)
                print(path, "->", resp.status if resp else None, (resp.headers.get("content-type") if resp else None))
            except Exception as e:
                print(path, "err", e)
        open("work/browser_state.json","w").write(json.dumps(out, indent=1))
        await b.close()
    print("COOKIE:", out.get("cookie_header","")[:400])

asyncio.run(main())
