import asyncio, json, sys
from playwright.async_api import async_playwright

TARGET = "https://www" + "." + "infinitycapital" + "." + "bh" + "/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + ".".join(["131","0","0","0"]) + " Safari/537.36"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(user_agent=UA, viewport={"width":1366,"height":900})
        page = await ctx.new_page()
        log = []
        page.on("request", lambda r: log.append(("REQ", r.method, r.url)))
        page.on("response", lambda r: log.append(("RES", r.status, r.url)))
        try:
            await page.goto(TARGET, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print("goto:", e)
        await page.wait_for_timeout(6000)
        html = await page.content()
        open("pw_home.html","w").write(html)
        print("TITLE:", await page.title())
        print("URL:", page.url)
        print("LEN:", len(html))
        print("COOKIES:", json.dumps(await ctx.cookies()))
        for row in log:
            print(*row)
        await b.close()

asyncio.run(main())
