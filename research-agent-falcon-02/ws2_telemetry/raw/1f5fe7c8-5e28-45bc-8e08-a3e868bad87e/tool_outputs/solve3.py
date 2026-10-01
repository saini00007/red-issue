import sys
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "131" + ".0.0.0 Safari/537.36")

URLS = ["https://www.infinitycapital.bh/", "https://www.infinitycapital.bh/login",
        "https://www.infinitycapital.bh/api/", "https://www.infinitycapital.bh/404"]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, locale="en-US",
                        timezone_id="Asia/Bahrain", viewport={"width": 1440, "height": 900})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()
    for u in URLS:
        try:
            r = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
            st = r.status if r else None
        except Exception as e:
            st = "ERR %s" % str(e)[:80]
        title = pg.title()
        for i in range(25):
            if "Security Checkpoint" not in pg.title():
                break
            pg.wait_for_timeout(1000)
        print("REQ", u, "first_status", st, "| final:", pg.title()[:80], "| url", pg.url)
        body = pg.content()
        fn = "tool_outputs/pw_%s.html" % u.rstrip("/").split("/")[-1].replace(".", "_")
        if not fn.endswith(".html"):
            fn = "tool_outputs/pw_root.html"
        open(fn, "w").write(body)
        print("   body", len(body), "challenge" if "Security Checkpoint" in body else "REAL-CONTENT")
    print("cookies:", [(c["name"], c["value"][:24]) for c in ctx.cookies()])
    b.close()
