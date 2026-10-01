import asyncio, json
from playwright.async_api import async_playwright

OUT = "/work/verify_ind"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                                  viewport={"width":1440,"height":900})
        pg = await ctx.new_page()
        api_log = []
        pg.on("response", lambda r: api_log.append((r.status, r.url)))
        await pg.goto("https://www.infinitycapital.bh/contact", wait_until="domcontentloaded", timeout=90000)
        # wait for challenge to clear (page title change / real content)
        try:
            await pg.wait_for_function("() => !document.title.includes('Security Checkpoint')", timeout=60000)
        except Exception as e:
            print("challenge wait:", e)
        await pg.wait_for_timeout(5000)
        print("TITLE:", await pg.title())
        html = await pg.content()
        open(f"{OUT}/pw_contact.html","w").write(html)
        await pg.screenshot(path=f"{OUT}/pw_contact.png", full_page=False)
        # dump cookies
        cookies = await ctx.cookies()
        json.dump(cookies, open(f"{OUT}/pw_cookies.json","w"), indent=1)
        print("COOKIES:", json.dumps([c['name'] for c in cookies]))
        # capture the contact form HTML
        forms = await pg.evaluate("""() => {
            return Array.from(document.querySelectorAll('form')).map(f => f.outerHTML.slice(0,4000));
        }""")
        open(f"{OUT}/pw_forms.json","w").write(json.dumps(forms, indent=1))
        print("FORMS:", len(forms))
        json.dump(api_log, open(f"{OUT}/pw_resps.json","w"), indent=1)
        await b.close()

asyncio.run(main())
