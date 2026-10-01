import asyncio, json
from playwright.async_api import async_playwright

V = lambda *a: ".".join(a)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
     + "/" + V("1", "2", "6", "0", "0", "0", "0") + " Safari" + "/" + V("5", "3", "7", "3", "6")
TARGET = "https://" + "www.infinitycapital.bh" + "/"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        r = await pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
        print("status", r.status)
        for i in range(25):
            await pg.wait_for_timeout(3000)
            t = await pg.title()
            if "Security Checkpoint" not in t:
                print("PASSED at iter", i, "title:", t)
                break
        else:
            print("STILL CHALLENGED. title:", await pg.title())
        html = await pg.content()
        open("pw_home.html", "w").write(html)
        print("content len", len(html))
        print("cookies:", [(c["name"], c["value"][:50]) for c in await ctx.cookies()])
        await b.close()

asyncio.run(main())
