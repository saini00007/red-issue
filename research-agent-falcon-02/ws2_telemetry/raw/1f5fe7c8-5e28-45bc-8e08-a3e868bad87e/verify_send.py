#!/usr/bin/env python3
"""Independent verification of POST /api/send provider error passthrough.
Uses the app's OWN legit contact-form shape (targets=contact) so no mail is
delivered to any third party. No abuse, no external recipients.
"""
import json, sys, requests

URL = "https://www.infinitycapital.bh/api/send"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
H = {
    "User-Agent": UA,
    "Accept": "*/*",
    "Origin": "https://www.infinitycapital.bh",
    "Referer": "https://www.infinitycapital.bh/contact",
    "Accept-Language": "en-US,en;q=0.9",
}

def legit_form(msg="verification probe - please disregard", targets="contact"):
    return {
        "fname": "Verifier", "lname": "Check", "areacode": "973", "tel": "3000000",
        "cname": "Verifier", "subject": "Verification Probe", "msg": msg,
        "check": "1", "targets": targets,
    }

def show(label, r):
    print("=" * 78)
    print(label)
    print("-" * 78)
    print("HTTP %s  %s" % (r.status_code, r.reason))
    for h in ("content-type", "content-length", "server", "x-vercel-mitigated",
              "x-powered-by", "x-matched-path", "cache-control"):
        if h in r.headers:
            print("  %-20s %s" % (h + ":", r.headers[h]))
    body = r.text
    print("  body_bytes=%d" % len(r.content))
    print("  body=%r" % (body[:1200] if body else "<EMPTY BODY>"))
    return r

s = requests.Session()

# --- Probe 1: the app's own contact-form submission (legit shape) ----------
r1 = s.post(URL, headers=H, data=legit_form(), timeout=40)
show("P1  POST /api/send  multipart form  targets=contact  (app's own contact form)", r1)

# --- Probe 2: JSON body with the same field names ---------------------------
r2 = s.post(URL, headers={**H, "Content-Type": "application/json"},
            data=json.dumps(legit_form()), timeout=40)
show("P2  POST /api/send  application/json  same fields", r2)

# --- Probe 3: missing `targets` field (claimed HTTP 500 empty body) ---------
d = legit_form(); d.pop("targets")
r3 = s.post(URL, headers=H, data=d, timeout=40)
show("P3  POST /api/send  multipart form  MISSING targets", r3)

# --- Probe 4: totally empty body -------------------------------------------
r4 = s.post(URL, headers={**H, "Content-Type": "application/json"}, data="", timeout=40)
show("P4  POST /api/send  empty body", r4)

# --- Probe 5: JSON null -----------------------------------------------------
r5 = s.post(URL, headers={**H, "Content-Type": "application/json"}, data="null", timeout=40)
show("P5  POST /api/send  body=null", r5)

# --- Probe 6: targets as integer ------------------------------------------
r6 = s.post(URL, headers={**H, "Content-Type": "application/json"},
            data=json.dumps({"fname": "V", "lname": "V", "msg": "x", "targets": 12345}),
            timeout=40)
show("P6  POST /api/send  JSON targets=12345 (number)", r6)

# --- Probe 7: unauthenticated? (no cookies, no origin at all) --------------
r7 = requests.post(URL, data=legit_form(),
                   headers={"User-Agent": UA, "Accept": "*/*"}, timeout=40)
show("P7  POST /api/send  bare, NO Origin/Referer/Cookie (pure anonymous)", r7)

summary = {
    "P1": [r1.status_code, r1.text[:600]],
    "P2": [r2.status_code, r2.text[:600]],
    "P3": [r3.status_code, r3.text[:600]],
    "P4": [r4.status_code, r4.text[:600]],
    "P5": [r5.status_code, r5.text[:600]],
    "P6": [r6.status_code, r6.text[:600]],
    "P7": [r7.status_code, r7.text[:600]],
}
with open("/work/evidence/iv_send_probe_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nWROTE /work/evidence/iv_send_probe_summary.json")
