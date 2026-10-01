#!/usr/bin/env python3
"""
Independent verification of the contact-form submission endpoint on the public
website https://www.infinitycapital.bh/

Purpose: determine whether the server-side handler enforces ANY anti-automation
control (rate limit / throttle / CAPTCHA / token / consent-field evaluation).

We deliberately send a SMALL, slow, controlled number of requests from a single
source.  We do NOT attempt to exhaust the tenant's monthly quota, because doing
so would be a destructive availability attack against a third party.
"""
import json
import ssl
import sys
import time
import urllib.request
import urllib.error

BASE = "https://www.infinitycapital.bh/api/send"
CONTACT = "https://www.infinitycapital.bh/contact"
TARGETS = json.dumps(["info@infinitycapital.bh"])
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

ctx = ssl.create_default_context()


def build_fields(tag, check_value):
    # Field names taken verbatim from the site's own client bundle
    # (_next/static/chunks/275-*.js -> FormData.set(...)).
    return {
        "fname": "Verifier",
        "lname": "Probe",
        "areacode": "+973",
        "tel": "1710000",
        "cname": "Independent Verification",
        "subject": "Investment Opportunities",
        "msg": "Security verification of public contact endpoint (tag=%s)." % tag,
        "check": check_value,
        "targets": TARGETS,
    }


def post(tag, check_value, extra=None, note=""):
    fields = build_fields(tag, check_value)
    if extra:
        fields.update(extra)
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        BASE,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.infinitycapital.bh",
            "Referer": CONTACT,
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
        },
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            code = r.status
            hdrs = dict(r.headers)
            data = r.read(4000).decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        code = e.code
        hdrs = dict(e.headers)
        data = e.read(4000).decode("utf8", "replace")
    except Exception as e:  # noqa
        code = -1
        hdrs = {}
        data = "TRANSPORT-ERROR: %r" % (e,)
    dt = time.time() - t0
    interesting = {k: v for k, v in hdrs.items()
                   if k.lower() in ("retry-after", "x-ratelimit-limit", "x-ratelimit-remaining",
                                    "ratelimit-limit", "ratelimit-remaining", "set-cookie",
                                    "x-vercel-id", "server")}
    return {"tag": tag, "check": check_value, "note": note, "http": code,
            "t": round(dt, 2), "headers": interesting, "body": data[:600]}


results = []

# --- Step 1: is the endpoint reachable anonymously at all? -------------------
print("[1] Anonymous baseline submission ...")
r1 = post("A-normal", "true", note="normal submission, consent checkbox checked")
results.append(r1)
print("   ->", r1["http"], r1["body"][:200])

time.sleep(2)

# --- Step 2: consent/honeypot field EMPTY (bots never check a box) -----------
print("[2] Submission with 'check' field omitted/empty ...")
r2 = post("B-empty-check", "", note="check field sent as empty string")
results.append(r2)
print("   ->", r2["http"], r2["body"][:200])

time.sleep(2)

# --- Step 3: consent field set to an obviously non-UI value -----------------
print("[3] Submission with 'check'=1 (non-UI value) ...")
r3 = post("C-check-1", "1", note="check field = 1")
results.append(r3)
print("   ->", r3["http"], r3["body"][:200])

time.sleep(2)

# --- Step 4: attacker-controlled recipient (open relay test, no exfil) ------
print("[4] Submission with client-supplied 'targets' overridden to an external address ...")
r4 = post("D-relay", "true",
          extra={"targets": json.dumps(["security-recon-audit@example.com"])},
          note="targets overridden by client -> tests server-side trust of recipient")
results.append(r4)
print("   ->", r4["http"], r4["body"][:200])

# --- Step 5: no Origin/Referer/Session at all (pure script, no browser) -----
print("[5] Submission with NO Origin, NO Referer, NO cookies, no CSRF token ...")
fields = build_fields("E-noorigin", "true")
body = urllib.parse.urlencode(fields).encode()
req = urllib.request.Request(BASE, data=body, method="POST", headers={
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "python-urllib/3 (no browser, no session)",
})
try:
    with urllib.request.urlopen(req, timeout=25, context=ctx) as rr:
        r5 = {"tag": "E-noorigin", "check": "true", "http": rr.status,
              "t": 0, "headers": {}, "body": rr.read(2000).decode("utf8", "replace")[:600],
              "note": "no Origin/Referer/cookie/CSRF token"}
except urllib.error.HTTPError as e:
    r5 = {"tag": "E-noorigin", "check": "true", "http": e.code, "t": 0, "headers": {},
          "body": e.read(2000).decode("utf8", "replace")[:600],
          "note": "no Origin/Referer/cookie/CSRF token"}
results.append(r5)
print("   ->", r5["http"], r5["body"][:200])

# --- Step 6: small controlled burst -> is there ANY per-IP throttle? --------
print("[6] Controlled burst: 8 more requests, 1.0s apart (testing for 429/403) ...")
burst = []
for i in range(8):
    rr = post("F-burst-%d" % i, "true", note="burst")
    burst.append(rr)
    print("   burst %d -> HTTP %s  %s" % (i + 1, rr["http"], rr["body"][:120]))
    results.append(rr)
    time.sleep(1.0)

summary = {
    "total_requests_sent": len(results),
    "http_codes": [r["http"] for r in results],
    "accepted_2xx": sum(1 for r in results if 200 <= r["http"] < 300),
    "throttled_429": sum(1 for r in results if r["http"] == 429),
    "forbidden_403": sum(1 for r in results if r["http"] == 403),
    "results": results,
}
print("\n===== SUMMARY =====")
print(json.dumps(summary, indent=2)[:4000])
with open("/work/evidence/probe_results.json", "w") as f:
    json.dump(summary, f, indent=2)
