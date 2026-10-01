#!/usr/bin/env python3
"""Single-shot unauthenticated probe of POST /api/send.
Sends ONE form-urlencoded request, captures status + body.
Defaults to targets=info@infinitycapital.bh (the site's own configured mailbox).
"""
import sys, json, urllib.request, urllib.error, urllib.parse, time

TARGET = sys.argv[1] if len(sys.argv) > 1 else "info@infinitycapital.bh"
BASE = "https://www.infinitycapital.bh/api/send"

fields = {
    "fname": "Independent",
    "lname": "Verifier",
    "areacode": "+973",
    "tel": "0000000",
    "cname": "Security Review",
    "subject": "Investment Opportunities",
    "msg": "Independent verification message - please disregard.",
    "check": "on",
    "targets": TARGET,
}
body = urllib.parse.urlencode(fields).encode()
req = urllib.request.Request(BASE, data=body, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
req.add_header("Accept", "*/*")
req.add_header("Origin", "https://www.infinitycapital.bh")
req.add_header("Referer", "https://www.infinitycapital.bh/contact")

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        code, hdrs, data = r.status, dict(r.headers), r.read()
except urllib.error.HTTPError as e:
    code, hdrs, data = e.code, dict(e.headers), e.read()
except Exception as e:
    code, hdrs, data = -1, {}, str(e).encode()

print("REQUEST BODY:", body.decode())
print("HTTP STATUS :", code, " (%.1fs)" % (time.time()-t0))
print("--- RESPONSE HEADERS ---")
for k, v in hdrs.items():
    print(f"{k}: {v}")
print("--- RESPONSE BODY ---")
print(data.decode(errors="replace")[:2000])
