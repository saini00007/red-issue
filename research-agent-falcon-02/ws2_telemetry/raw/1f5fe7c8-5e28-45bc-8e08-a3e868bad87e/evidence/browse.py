import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.infinitycapital.bh/"
out = sys.argv[2] if len(sys.argv) > 2 else "page"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    log = []
    ctx.on("request", lambda r: log.append(r.method + " " + r.url))
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    try:
        pg.mouse.move(600, 400)
        pg.wait_for_timeout(2000)
        pg.mouse.move(700, 450)
    except Exception:
        pass
    pg.wait_for_timeout(4000)
    print("TITLE:", pg.title())
    print("URL:", pg.url)
    print("BODY:", pg.inner_text("body")[:600].replace("\n", " | "))
    open(out + ".html", "w").write(pg.content())
    open(out + "_requests.txt", "w").write("\n".join(log))
    print("REQCOUNT:", len(log))
    for line in log:
        if "/api/" in line or line.endswith(".js"):
            print("REQ", line)
    ctx.storage_state(path="state.json")
    b.close()
