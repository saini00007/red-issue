import json, time, sys
from playwright.sync_api import sync_playwright

OUT = "/work/evidence/IVFY"
import os
os.makedirs(OUT, exist_ok=True)

CASES = [
    ("get_api_send", "GET", None, None),
    ("post_empty_obj", "POST", {}, "application/json"),
    ("post_targets_reserved", "POST", {"targets": ["probe@invalid.test"], "message": "independent verification probe"}, "application/json"),
    ("post_null", "POST", None, "application/json"),
    ("post_targets_int", "POST", {"targets": 12345}, "application/json"),
    ("post_xml", "POST", "<a>hi</a>", "application/xml"),
    ("post_text", "POST", "hello", "text/plain"),
]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    print("visiting site...")
    pg.goto("https://www.infinitycapital.bh/", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    try:
        pg.wait_for_load_state("networkidle", timeout=20000)
    except Exception as e:
        print("networkidle:", e)
    print("url after challenge:", pg.url)
    print("title:", pg.title())
    pg.screenshot(path=f"{OUT}/site.png", full_page=False)
    cookies = ctx.cookies()
    print("cookie names:", [c["name"] for c in cookies])
    with open(f"{OUT}/cookies.json","w") as f:
        json.dump(cookies, f, indent=1)

    results = {}
    for name, method, payload, ctype in CASES:
        if payload is None and ctype == "application/json":
            body = "null"
        elif isinstance(payload, str):
            body = payload
        elif payload is None:
            body = None
        else:
            body = json.dumps(payload)
        hdrs = {"Accept":"*/*"}
        if ctype:
            hdrs["Content-Type"] = ctype
        print("="*70)
        print("CASE:", name, method, "body=", repr(body))
        try:
            r = ctx.request.fetch("https://www.infinitycapital.bh/api/send", method=method, data=body, headers=hdrs, timeout=45000, max_redirects=0)
            txt = r.text()
            print("status:", r.status)
            print("hdrs:", json.dumps({k:v for k,v in r.headers.items()}, indent=1)[:800])
            print("body(%d bytes):" % len(txt), repr(txt[:900]))
            results[name] = {"method":method,"req":body,"status":r.status,"headers":dict(r.headers),"body":txt}
        except Exception as e:
            print("ERR:", e)
            results[name] = {"error": str(e)}
        pg.wait_for_timeout(1500)

    with open(f"{OUT}/results.json","w") as f:
        json.dump(results, f, indent=1)
    print("saved", f"{OUT}/results.json")
    ctx.close()
    b.close()
