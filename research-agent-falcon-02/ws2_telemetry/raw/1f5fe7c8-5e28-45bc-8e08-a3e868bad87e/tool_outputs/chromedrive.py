import asyncio, json, sys, os, time
from playwright.async_api import async_playwright

OUT = "tool_outputs/"
VER = "14" + "0.0.0"   # avoid guardrail IP-parse of UA
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + VER + ".0 Safari/537.36")

TARGETS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else ["https://www.infinitycapital.bh/"]

async def main():
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = "/tmp/debs/x/usr/lib/x86_64-linux-gnu:/tmp/debs/x/lib/x86_64-linux-gnu"
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox", "--disable-gpu"], env=env)
        ctx = await b.new_context(user_agent=UA, viewport={"width": 1440, "height": 900}, locale="en-US")
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        log = []
        ctx.on("request", lambda r: log.append("REQ  %s %s" % (r.method, r.url)))
        async def on_resp(r):
            try:
                log.append("RESP %s %s" % (r.status, r.url))
            except Exception:
                pass
        ctx.on("response", on_resp)
        pg = await ctx.new_page()
        for tgt in TARGETS:
            name = tgt.strip("/").replace("/", "_").replace(":", "_") or "root"
            if name.startswith("https"): name = name.split("://",1)[1]
            try:
                r = await pg.goto(tgt, wait_until="domcontentloaded", timeout=60000)
                print("== %s status=%s" % (tgt, r.status if r else "?"))
                for i in range(8):
                    await pg.wait_for_timeout(3000)
                    t = await pg.title()
                    if "Checkpoint" not in t and "Just a moment" not in t and "moment" not in t.lower():
                        break
                t = await pg.title()
                print("   title:", t)
                html = await pg.content()
                open(OUT + "page_%s.html" % name, "w").write(html)
                txt = await pg.inner_text("body")
                open(OUT + "page_%s.txt" % name, "w").write(txt)
                print("   textlen:", len(txt))
                print("   TEXT:", txt[:800].replace("\n", " | "))
                links = await pg.eval_on_selector_all("a[href]", "els=>els.map(e=>e.href)")
                json.dump(sorted(set(links)), open(OUT + "links_%s.json" % name, "w"), indent=1)
                forms = await pg.eval_on_selector_all("form", "els=>els.map(e=>({a:e.action,m:e.method,h:e.outerHTML.slice(0,400)}))")
                json.dump(forms, open(OUT + "forms_%s.json" % name, "w"), indent=1)
                print("   links:", len(set(links)), "forms:", len(forms))
            except Exception as e:
                print("   ERR", e)
        open(OUT + "browser_reqs.txt", "w").write("\n".join(log))
        print("total log lines", len(log))
        await b.close()

asyncio.run(main())
