import os, json, time
from playwright.sync_api import sync_playwright

OUT="tool_outputs/d13_browser"
os.makedirs(OUT, exist_ok=True)

URLS = [
 "https://www.infinitycapital.bh/",
 "https://www.infinitycapital.bh/contact",
 "https://www.infinitycapital.bh/404",
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(viewport={"width":1366,"height":900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    for u in URLS:
        pg = ctx.new_page()
        seen=set()
        def on_resp(r):
            if r.url.startswith("https://www.infinitycapital.bh") and len(seen)<400:
                seen.add(r.request.method+" "+r.url+" "+str(r.status))
        pg.on("response", on_resp)
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(u,"GOTO ERR",str(e)[:80])
        for _ in range(8):
            time.sleep(1.2)
        name=u.rstrip('/').split('/')[-1] or 'home'
        title=pg.title()
        body=pg.content()
        open(f"{OUT}/{name}.html","w").write(body)
        open(f"{OUT}/{name}.net.txt","w").write("\n".join(sorted(seen)))
        print(f"=== {u} title={title!r} len={len(body)} resp={len(seen)}")
        for s in sorted(seen)[:60]:
            print("   ",s)
        pg.close()
    b.close()
