import json, sys, time
from playwright.sync_api import sync_playwright

URL = "https://www.infinitycapital.bh/contact"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled","--no-sandbox"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width":1366,"height":900},
        locale="en-US",
    )
    pg = ctx.new_page()
    r = pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    print("initial status:", r.status if r else None)
    # wait for challenge to resolve / page to render
    for i in range(20):
        time.sleep(1)
        t = pg.title()
        if "Security Checkpoint" not in t:
            break
    print("title after wait:", pg.title())
    print("final url:", pg.url)
    html = pg.content()
    print("html len:", len(html))
    open("/work/ver_browser_contact.html","w").write(html)
    print("has form inputs:", ("fname" in html))
    cookies = ctx.cookies()
    print("cookies:", json.dumps([{c["name"]:c["value"][:24] for c in cookies}], indent=1))
    ctx.storage_state(path="/work/ver_state.json")
    b.close()
