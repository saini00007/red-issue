import sys, json, time
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.infinitycapital.bh/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/work/pw_result.json"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width":1440,"height":900},
        locale="en-US",
    )
    pg = ctx.new_page()
    pg.on("console", lambda m: print("CONSOLE:", m.type, m.text[:200]))
    resp = pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    print("initial status:", resp.status if resp else None)
    # wait for the vercel challenge to clear
    for i in range(30):
        title = pg.title()
        if "Security Checkpoint" not in title and "Just a moment" not in title:
            print("passed challenge after", i, "s; title:", title)
            break
        pg.wait_for_timeout(1000)
    else:
        print("STILL CHALLENGED; title:", pg.title())
    pg.wait_for_timeout(2500)
    html = pg.content()
    print("final url:", pg.url)
    print("final title:", pg.title())
    open("/work/page.html","w").write(html)
    print("len html", len(html))
    # dump cookies
    print("COOKIES:", json.dumps(ctx.cookies(), indent=1)[:2000])
    ctx.storage_state(path="/work/state.json")
    b.close()
