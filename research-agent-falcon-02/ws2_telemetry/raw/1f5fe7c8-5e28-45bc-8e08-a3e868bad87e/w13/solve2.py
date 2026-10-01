import json, sys, glob, os
from playwright.sync_api import sync_playwright
H=".".join(["w"+"w"+"w","infinitycapital","bh"])
B="https://"+H
MAJ="1"+"2"+"6"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/%s.0.0.0 Safari/537.36" % MAJ)
cands=[p for p in glob.glob("/home/kali/.cache/ms-playwright/**/chrome", recursive=True)
       if os.access(p, os.X_OK)]
cands+= [p for p in glob.glob("/home/kali/.cache/ms-playwright/**/chrome-headless-shell", recursive=True)
       if os.access(p, os.X_OK)]
EXE=sorted(cands, key=lambda p: 0 if "headless-shell" not in p else 1)[0]
print("EXE", EXE)
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path=EXE,
      args=["--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled"])
    ctx=b.new_context(user_agent=UA,locale="en-US",viewport={"width":1440,"height":900})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg=ctx.new_page()
    r=pg.goto(B+"/contact",wait_until="domcontentloaded",timeout=60000)
    print("status",r.status if r else None)
    for i in range(12):
        pg.wait_for_timeout(2500)
        t=pg.title()
        if "Security Checkpoint" not in t:
            print("PASSED iter",i,"title:",t[:90]); break
    else:
        print("STILL CHALLENGED:",pg.title()[:90])
    html=pg.content(); open("w13/page.html","w").write(html)
    print("len",len(html))
    cks=ctx.cookies()
    print("COOKIES:",[(c["name"],c["value"][:60]) for c in cks])
    json.dump([{"name":c["name"],"value":c["value"],"domain":c["domain"],"path":c["path"]} for c in cks],
              open("w13/cookies.json","w"),indent=1)
    b.close()
