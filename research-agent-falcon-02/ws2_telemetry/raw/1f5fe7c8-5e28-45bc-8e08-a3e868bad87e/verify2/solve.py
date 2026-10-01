import asyncio, json, os
from playwright.async_api import async_playwright

OUT = "/work/verify2"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage"])
        ctx = await b.new_context(user_agent=UA, viewport={"width":1440,"height":900},
                                  locale="en-US")
        pg = await ctx.new_page()
        r = await pg.goto("https://www.infinitycapital.bh/contact", wait_until="domcontentloaded", timeout=90000)
        print("initial status:", r.status if r else None)
        try:
            await pg.wait_for_function(
                "() => !document.title.includes('Security Checkpoint')", timeout=60000)
            print("challenge cleared")
        except Exception as e:
            print("challenge wait err:", e)
        await pg.wait_for_timeout(6000)
        print("TITLE:", await pg.title())
        open(f"{OUT}/solved_contact.html","w").write(await pg.content())
        cookies = await ctx.cookies()
        json.dump(cookies, open(f"{OUT}/cookies.json","w"), indent=1)
        print("COOKIE NAMES:", [c["name"] for c in cookies])
        # Extract the real form structure
        forms = await pg.evaluate("""() => Array.from(document.querySelectorAll('form')).map(f=>f.outerHTML.slice(0,6000))""")
        json.dump(forms, open(f"{OUT}/forms.json","w"), indent=1)
        print("FORMS:", len(forms))
        await pg.screenshot(path=f"{OUT}/contact.png")
        json.dump([c for c in cookies], open(f"{OUT}/cookies_jar.txt","w"))
        await b.close()

asyncio.run(main())
