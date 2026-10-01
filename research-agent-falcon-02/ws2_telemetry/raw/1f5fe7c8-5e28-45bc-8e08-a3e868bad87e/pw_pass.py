import asyncio, json
from playwright.async_api import async_playwright
TARGET="https://www.infinitycapital.bh/"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx=await b.new_context(user_agent=UA)
        pg=await ctx.new_page()
        r=await pg.goto(TARGET,wait_until="domcontentloaded",timeout=60000)
        print("status",r.status)
        for i in range(20):
            await pg.wait_for_timeout(2500)
            t=await pg.title()
            if "Security Checkpoint" not in t:
                print("PASSED iter",i,"title:",t); break
        else:
            print("STILL CHALLENGED:",await pg.title())
        html=await pg.content()
        open("pw2_home.html","w").write(html)
        print("len",len(html))
        cks=await ctx.cookies()
        print("cookies",[(c["name"],c["value"][:60]) for c in cks])
        json.dump([{"name":c["name"],"value":c["value"],"domain":c["domain"],"path":c["path"]} for c in cks],open("pw2_cookies.json","w"),indent=1)
        await b.close()
asyncio.run(main())
