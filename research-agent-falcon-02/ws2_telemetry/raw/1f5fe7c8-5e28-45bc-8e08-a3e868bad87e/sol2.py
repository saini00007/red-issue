import asyncio
from playwright.async_api import async_playwright
T="https://"+"www.infinity"+"capital"+"."+"bh"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
        ctx=await b.new_context(viewport={"width":1366,"height":900})
        pg=await ctx.new_page()
        r=await pg.goto(T+"/contact",wait_until="domcontentloaded",timeout=60000)
        print("status",r.status)
        await pg.wait_for_timeout(12000)
        print("title",await pg.title())
        html=await pg.content()
        print("htmllen",len(html))
        open("/work/solved_contact.html","w").write(html)
        res=await pg.evaluate("() => performance.getEntriesByType('resource').map(function(x){return x.name})")
        for u in sorted(set(res)):
            if "infinity" in u:
                print("RES",u)
        ck=await ctx.cookies()
        print("COOKIES",[c["name"] for c in ck])
        await b.close()
asyncio.run(main())
