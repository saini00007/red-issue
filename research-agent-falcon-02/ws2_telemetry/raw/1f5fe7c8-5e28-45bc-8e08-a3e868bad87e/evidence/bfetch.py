import sys, json
from playwright.sync_api import sync_playwright

URL = "https://www.infinitycapital.bh/contact"
OUT = "/work/evidence"

def log(*a):
    print(*a, flush=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width":1400,"height":1000})
    pg = ctx.new_page()

    def on_resp(r):
        u = r.url
        if "/api/" in u:
            log(f"[APIRESSP] {r.status} {u}")
            try:
                log("   body:", r.text()[:500])
            except Exception as e:
                log("   body-err:", e)

    pg.on("response", on_resp)

    log("goto", URL)
    try:
        pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        log("goto-exc:", e)

    # wait out the vercel challenge reload loop
    for i in range(20):
        t = pg.title()
        if "Security Checkpoint" not in t:
            log(f"challenge cleared at poll {i}, title={t!r}")
            break
        pg.wait_for_timeout(1500)
    else:
        log("STILL CHALLENGED, title=", pg.title())

    log("final title:", pg.title())
    pg.screenshot(path=f"{OUT}/bf_contact.png", full_page=False)
    with open(f"{OUT}/bf_contact.html","w") as f:
        f.write(pg.content())
    log("cookies:", json.dumps(ctx.cookies())[:800])

    # dump any form fields
    forms = pg.eval_on_selector_all("form", """els => els.map(e => ({
        action: e.action, method: e.method, id: e.id,
        inputs: Array.from(e.querySelectorAll('input,textarea,select,button')).map(x => ({
           tag:x.tagName, name:x.name, type:x.type, id:x.id, required:x.required
        }))
    }))""")
    log("FORMS:", json.dumps(forms, indent=1)[:3000])

    ctx.storage_state(path=f"{OUT}/bf_state.json")
    b.close()
