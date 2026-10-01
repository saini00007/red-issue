from playwright.sync_api import sync_playwright
import sys, json

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.infinitycapital.bh/"
out = sys.argv[2] if len(sys.argv) > 2 else "/work/real_home.html"

with sync_playwright() as p:
    b = p.chromium.launch(
        headless=True,
        executable_path="/home/kali/.cache/ms-playwright/chromium-1187/chrome-linux/chrome",
        args=["--no-sandbox", "--disable-dev-shm-usage",
              "--disable-blink-features=AutomationControlled"],
    )
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900},
    )
    pg = ctx.new_page()
    r = pg.goto(url, wait_until="networkidle", timeout=90000)
    print("STATUS", r.status if r else None)
    print("TITLE", pg.title())
    html = pg.content()
    print("LEN", len(html))
    open(out, "w").write(html)
    try:
        pg.screenshot(path=out.replace(".html", ".png"), full_page=False)
    except Exception as e:
        print("SHOT FAIL", e)
    print("COOKIES", json.dumps(ctx.cookies(), indent=1)[:3000])
    b.close()
