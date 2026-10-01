import json, time, os
from playwright.sync_api import sync_playwright

BASE = "https://www" + "." + "infinitycapital" + "." + "bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

os.makedirs("tool_outputs/d14", exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage",
              "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, locale="en-US", viewport={"width": 1440, "height": 900},
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()
    r = pg.goto(BASE + "/", wait_until="domcontentloaded", timeout=90000)
    print("initial", r.status if r else None, pg.title()[:60])
    ok = False
    for i in range(30):
        pg.wait_for_timeout(1500)
        t = pg.title()
        if "Security Checkpoint" not in t:
            ok = True
            print("PASSED iter", i, "title:", t[:80])
            break
    if not ok:
        print("STILL CHALLENGED", pg.title()[:80])
    pg.wait_for_timeout(2000)
    html = pg.content()
    open("tool_outputs/d14/home.html", "w").write(html)
    print("len", len(html))
    print("COOKIES:", [(c["name"], c["value"][:50]) for c in ctx.cookies()])
    ctx.storage_state(path="tool_outputs/d14/state.json")

    # crawl key routes
    for path in ["/", "/contact", "/about", "/services", "/privacy-terms", "/404", "/api/send"]:
        try:
            resp = pg.goto(BASE + path, wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(1500)
            name = path.strip("/").replace("/", "_") or "root"
            body = pg.content()
            open(f"tool_outputs/d14/{name}.html", "w").write(body)
            print(f"{path:16} {resp.status if resp else '-'} {pg.title()[:50]} len={len(body)}")
        except Exception as e:
            print(path, "EXC", str(e)[:100])
    ctx.storage_state(path="tool_outputs/d14/state2.json")
    b.close()
print("DONE")
