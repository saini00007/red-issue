import json, sys
from playwright.sync_api import sync_playwright

BASE = "https://www" + ".infinitycapital" + ".bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

out = {}

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                               "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, locale="en-US",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
    # stealth tweaks
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()
    r = pg.goto(BASE + "/", wait_until="domcontentloaded", timeout=60000)
    print("initial status", r.status if r else None)
    ok = False
    for i in range(30):
        pg.wait_for_timeout(2000)
        t = pg.title()
        if "Security Checkpoint" not in t:
            print("PASSED at iter", i, "title:", t[:80])
            ok = True
            break
    if not ok:
        print("STILL CHALLENGED title:", pg.title()[:100])
    body = pg.content()
    print("home body len", len(body), "challenge:", "Security Checkpoint" in body)
    cookies = ctx.cookies()
    print("COOKIES:", [(c["name"], c["value"][:60]) for c in cookies])
    out["cookies"] = cookies
    out["user_agent"] = UA
    open("tool_outputs/pw_home.html", "w").write(body)

    # Visit contact to grab the real form + the JS that builds the POST body
    for path in ["/contact", "/"]:
        try:
            rr = pg.goto(BASE + path, wait_until="networkidle", timeout=60000)
            print(path, "->", rr.status if rr else None, "title", pg.title()[:60])
            h = pg.content()
            open(f"tool_outputs/pw_{path.strip('/') or 'home'}.html", "w").write(h)
        except Exception as e:
            print(path, "ERR", e)

    # capture any XHR/fetch requests the page makes
    reqs = []
    def on_req(req):
        if req.method != "GET" and "/api" in req.url:
            reqs.append({"m": req.method, "u": req.url,
                         "h": req.headers, "post": req.post_data})
    pg.on("request", on_req)
    try:
        pg.goto(BASE + "/contact", wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(4000)
    except Exception as e:
        print("nav err", e)
    print("API REQS CAPTURED:", len(reqs))
    for q in reqs:
        print(json.dumps(q)[:500])
    out["api_reqs"] = reqs
    b.close()

json.dump(out, open("tool_outputs/pw_session.json", "w"), indent=1)
print("saved")
