import json, time, sys
from playwright.sync_api import sync_playwright
BASE="https://www.infinitycapital.bh"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
EXE="/home/kali/.cache/ms-playwright/chromium-1243/chrome-linux/chrome"
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path=EXE,args=["--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled"])
    ctx=b.new_context(user_agent=UA,locale="en-US",viewport={"width":1440,"height":900})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg=ctx.new_page()
    r=pg.goto(BASE+"/",wait_until="domcontentloaded",timeout=90000)
    ok=False
    for i in range(30):
        pg.wait_for_timeout(2000)
        t=pg.title()
        if "Security Checkpoint" not in t:
            print("PASSED iter",i,"title:",t[:80]); ok=True; break
    if not ok:
        print("STILL CHALLENGED", pg.title()[:80])
    body=pg.content()
    open("tool_outputs/solved_home.html","w").write(body)
    ck=ctx.cookies()
    print("COOKIES:",[(c["name"],c["value"][:90]) for c in ck])
    json.dump([{"name":c["name"],"value":c["value"],"domain":c["domain"],"path":c["path"]} for c in ck],open("cookies_now.json","w"),indent=1)
    b.close()
