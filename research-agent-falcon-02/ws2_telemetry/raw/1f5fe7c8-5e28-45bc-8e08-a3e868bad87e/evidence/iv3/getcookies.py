#!/usr/bin/env python3
"""Use a real headless Chromium to pass the Vercel Security Checkpoint and export cookies."""
import json, sys, time
from playwright.sync_api import sync_playwright

TARGET = "https://www.infinitycapital.bh/contact"
OUT = "/work/evidence/iv3/cookies.json"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--no-sandbox", "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        locale="en-US", viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    r = pg.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
    print("initial status:", r.status if r else None)
    # wait for challenge to clear
    for i in range(40):
        title = pg.title()
        body = pg.content()
        if "Security Checkpoint" not in title and "Vercel Security Checkpoint" not in body:
            print("challenge cleared after", i, "s; title=", title)
            break
        time.sleep(1)
    else:
        print("still challenged; title=", pg.title())
    time.sleep(3)
    cookies = ctx.cookies()
    with open(OUT, "w") as f:
        json.dump(cookies, f, indent=1)
    print("cookies:", json.dumps(cookies))
    open("/work/evidence/iv3/pg_contact.html", "w").write(pg.content())
    pg.screenshot(path="/work/evidence/iv3/pg_contact.png", full_page=False)
    b.close()
