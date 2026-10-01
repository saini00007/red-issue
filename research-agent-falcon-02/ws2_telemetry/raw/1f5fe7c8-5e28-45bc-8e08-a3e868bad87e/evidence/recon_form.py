import asyncio, json, re
from playwright.async_api import async_playwright

OUT = "/work/evidence"
URL = "https://www.infinitycapital.bh/"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx = await b.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        pg = await ctx.new_page()
        api_calls = []
        pg.on("request", lambda r: api_calls.append(("REQ", r.method, r.url, r.post_data or "")))
        pg.on("response", lambda r: api_calls.append(("RES", r.status, r.url, "")))
        try:
            await pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print("goto err", e)
        # Vercel challenge reloads page after solving; wait for real content
        for _ in range(12):
            await pg.wait_for_timeout(2500)
            title = await pg.title()
            if "Security Checkpoint" not in title:
                break
        print("TITLE:", await pg.title())
        html = await pg.content()
        open(f"{OUT}/home_browser.html","w").write(html)
        # find any form and input names
        forms = await pg.query_selector_all("form")
        print("FORMS:", len(forms))
        for f in forms:
            print("  form action=", await f.get_attribute("action"), "method=", await f.get_attribute("method"))
            for inp in await f.query_selector_all("input, textarea, select"):
                print("    field", await inp.get_attribute("name"), "type=", await inp.get_attribute("type"))
        # search inline scripts for '/api/send'
        scripts = await pg.query_selector_all("script")
        joined = ""
        for s in scripts:
            t = await s.inner_text()
            joined += t + "\n"
        open(f"{OUT}/home_scripts.js","w").write(joined)
        for m in re.finditer(r"/api/send", joined):
            print("FOUND /api/send in inline JS at", m.start())
            print(joined[max(0,m.start()-300): m.start()+300])
        # dump any mention of 'targets'
        for m in re.finditer(r"targets", joined):
            print("FOUND 'targets' in inline JS")
            print(joined[max(0,m.start()-200): m.start()+200])
            break
        print("\n--- API/network calls seen ---")
        for c in api_calls:
            if "/api/" in c[2]:
                print(c)
        await b.close()

asyncio.run(main())
