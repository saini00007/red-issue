#!/usr/bin/env python3
"""Solve the Vercel BotID Security Checkpoint in a real browser, then dump cookies
so that curl/sqlmap can replay requests to query-parameterised paths."""
import sys, json, time
from playwright.sync_api import sync_playwright

URLS = sys.argv[1:] or ["https://www.infinitycapital.bh/"]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US",
    )
    for u in URLS:
        pg = ctx.new_page()
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print("GOTO_ERR", u, e)
        # let the checkpoint JS run
        for _ in range(20):
            time.sleep(1)
            try:
                title = pg.title()
            except Exception:
                continue
            if "Checkpoint" not in title and "Just a moment" not in title:
                break
        pg.wait_for_timeout(3000)
        print("TITLE", u, "->", pg.title())
        print("URL", pg.url)
        print("BODYLEN", len(pg.content()))
        pg.close()
    cookies = ctx.cookies()
    out = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    print("COOKIE_HEADER:", out)
    json.dump(cookies, open("/work/cookies.json", "w"), indent=1)
    b.close()
