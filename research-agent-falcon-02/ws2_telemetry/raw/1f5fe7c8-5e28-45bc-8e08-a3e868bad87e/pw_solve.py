import json, sys, time
from playwright.sync_api import sync_playwright

BASE = "https://www" + "." + "infinitycapital" + "." + "bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
EXE = "/home/kali/.cache/ms-playwright/chromium-1187/chrome-linux/chrome"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=EXE,
        args=["--no-sandbox", "--disable-dev-shm-usage",
              "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, locale="en-US", viewport={"width":1440,"height":900},
        extra_http_headers={"Accept-Language":"en-US,en;q=0.9"})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()
    r = pg.goto(BASE + "/", wait_until="domcontentloaded", timeout=90000)
    print("initial status", r.status if r else None)
    ok = False
    for i in range(25):
        pg.wait_for_timeout(2000)
        t = pg.title()
        if "Security Checkpoint" not in t:
            print("PASSED at iter", i, "title:", t[:80]); ok = True; break
    if not ok:
        print("STILL CHALLENGED title:", pg.title()[:100])
    body = pg.content()
    print("len", len(body), "challenge:", "Security Checkpoint" in body)
    open("tool_outputs/pw_live_home.html","w").write(body)
    ck = ctx.cookies()
    print("COOKIES:", [(c["name"], c["value"][:70]) for c in ck])
    json.dump([{"name":c["name"],"value":c["value"],"domain":c["domain"],"path":c["path"]} for c in ck],
              open("tool_outputs/pw_cookies.json","w"), indent=1)
    b.close()
