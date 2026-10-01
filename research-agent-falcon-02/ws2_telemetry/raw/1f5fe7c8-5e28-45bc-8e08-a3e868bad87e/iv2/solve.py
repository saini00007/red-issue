import json, time, sys
from playwright.sync_api import sync_playwright

OUT = "/work/iv2"
URL = "https://www.infinitycapital.bh/contact-us/"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
    ])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900},
        locale="en-US",
    )
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()
    try:
        r = pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        print("initial status:", r.status if r else None)
    except Exception as e:
        print("goto err:", e)
    # wait for challenge to resolve
    for i in range(20):
        time.sleep(2)
        t = pg.title()
        if "Security Checkpoint" not in t and "Just a moment" not in t:
            print("challenge cleared at iter", i, "title:", t)
            break
        print("iter", i, "title:", t)
    try:
        pg.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    print("FINAL TITLE:", pg.title())
    print("FINAL URL:", pg.url)
    html = pg.content()
    open(OUT + "/browser_contact.html", "w").write(html)
    print("html size:", len(html))
    cookies = ctx.cookies()
    open(OUT + "/cookies.json", "w").write(json.dumps(cookies, indent=2))
    for c in cookies:
        print("COOKIE:", c["name"], "=", c["value"][:80], "domain=", c["domain"])
    b.close()
