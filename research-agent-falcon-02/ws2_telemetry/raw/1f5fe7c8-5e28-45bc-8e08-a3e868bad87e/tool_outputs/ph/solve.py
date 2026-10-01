import asyncio, json
from playwright.async_api import async_playwright
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0.36 Safari/537.36"
T = "https://www.infinitycapital.bh/?id=1&search=test&page=2"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        r = await pg.goto(T, wait_until="domcontentloaded", timeout=60000)
        print("first status", r.status)
        for i in range(30):
            await pg.wait_for_timeout(3000)
            t = await pg.title()
            c = await pg.content()
            if "Security Checkpoint" not in t and "Checkpoint" not in c[:6000]:
                print("PASSED iter", i, "title:", t); break
        else:
            print("STILL CHALLENGED title:", await pg.title())
        cks = await ctx.cookies()
        open("tool_outputs/ph/cookie.json","w").write(json.dumps(cks))
        print("cookie names:", [c["name"] for c in cks])
        html = await pg.content()
        open("tool_outputs/ph/pw.html","w").write(html)
        print("len", len(html))
        await b.close()
asyncio.run(main())
