import sys, time, json
from playwright.sync_api import sync_playwright

OUT = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)

with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=[
        "--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 900})
    pg = ctx.new_page()
    r = pg.goto("https://www.infinitycapital.bh/contact", wait_until="domcontentloaded", timeout=60000)
    log("[1] /contact status:", r.status if r else None)
    # wait out the challenge JS
    for i in range(20):
        time.sleep(2)
        t = pg.title()
        log("   t=%ds title=%r url=%s" % ((i+1)*2, t, pg.url))
        if "Security Checkpoint" not in t and "Just a moment" not in t:
            break
    log("[2] FINAL title:", pg.title(), "url:", pg.url)
    body = pg.content()
    open("/work/evidence/browser_contact.html","w").write(body)
    log("[3] body len:", len(body))
    log("[3b] form fields:", pg.eval_on_selector_all(
        "form input, form textarea, form select",
        "els => els.map(e => [e.tagName, e.type, e.name, e.id, e.placeholder]).slice(0,60)"))
    open("/work/evidence/browser_cookies.json","w").write(json.dumps(ctx.cookies(), indent=1))
    br.close()

open("/work/evidence/browser_pass.log","w").write("\n".join(OUT))
