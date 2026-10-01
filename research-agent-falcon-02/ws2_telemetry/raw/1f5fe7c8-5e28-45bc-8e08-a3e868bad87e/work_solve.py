import sys
from playwright.sync_api import sync_playwright

url = "https://www.infinitycapital.bh/"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    try:
        r = pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        print("initial status", r.status if r else None)
    except Exception as e:
        print("goto err", e)
    # wait for the challenge JS to solve and redirect
    for i in range(20):
        pg.wait_for_timeout(1000)
        try:
            t = pg.title()
        except Exception:
            t = "?"
        if i % 4 == 0:
            print(i, "title:", t[:70])
    print("FINAL title:", pg.title()[:120])
    print("FINAL url:", pg.url)
    body = pg.content()
    open("tool_outputs/pw_body.html","w").write(body)
    print("body len", len(body))
    print("has checkpoint:", "Security Checkpoint" in body)
    print("cookies:", ctx.cookies())
    pg.screenshot(path="tool_outputs/pw_home.png", full_page=False)
    b.close()
