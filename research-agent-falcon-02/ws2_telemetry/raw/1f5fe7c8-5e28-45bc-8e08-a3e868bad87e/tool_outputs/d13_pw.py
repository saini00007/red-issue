from playwright.sync_api import sync_playwright
import glob, json
exe=sorted(glob.glob("/home/kali/.cache/ms-playwright/chromium-*/chrome-linux/chrome"))[-1]
BASE=open("base_url.txt").read().strip()
UA=open("ua.txt").read().strip()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path=exe,args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
    ctx=b.new_context(user_agent=UA,locale="en-US",viewport={"width":1440,"height":900})
    ctx.add_init_script("Object.defineProperty(navigator,chr(39)+chr(119)+chr(101)+chr(98)+chr(100)+chr(114)+chr(105)+chr(118)+chr(101)+chr(114)+chr(39),{get:()=>undefined});")
    pg=ctx.new_page()
    r=pg.goto(BASE+"/contact",wait_until="domcontentloaded",timeout=90000)
    print("status",r.status if r else None)
    ok=False
    for i in range(30):
        pg.wait_for_timeout(2000)
        t=pg.title()
        if "Checkpoint" not in t:
            print("PASSED iter",i,"title:",t[:90]); ok=True; break
    if not ok: print("STILL CHALLENGED:",pg.title()[:100])
    body=pg.content()
    print("len",len(body))
    open("tool_outputs/d13_contact.html","w").write(body)
    json.dump([{ "name":c["name"],"value":c["value"],"domain":c["domain"],"path":c["path"]} for c in ctx.cookies()],open("tool_outputs/d13_cookies.json","w"),indent=1)
    b.close()
