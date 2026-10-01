#!/usr/bin/env python3
"""Step 1: baseline - send to the site's OWN address (info@... as shipped in the page config)."""
import json, urllib.request, urllib.parse, uuid, sys

URL = "https://www.infinitycapital.bh/api/send"
OWN = "info@" + "infinitycapital.bh"   # the only value present in the site's own /contact config

def post(fields, hdrs=None):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36")
    req.add_header("Origin", "https://www.infinitycapital.bh")
    req.add_header("Referer", "https://www.infinitycapital.bh/contact")
    for k, v in (hdrs or {}).items():
        req.add_header(k, v)
    try:
        r = urllib.request.urlopen(req, timeout=45)
        return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, {}, "EXC: %r" % (e,)

tag = "VERIFIER-" + uuid.uuid4().hex[:10]
fields = {
    "fname": "Independent", "lname": "Verifier",
    "areacode": "+973", "tel": "17100005",
    "cname": "Security Audit", "subject": "Investment Opportunities",
    "msg": "Baseline control request %s - please ignore, authorized security verification of the contact endpoint." % tag,
    "check": "", "targets": OWN,
}
st, h, b = post(fields)
print("BASELINE (targets = site's own address)")
print("status:", st)
print("body:", repr(b[:2000]))
print(json.dumps({k: v for k, v in fields.items()}, indent=1))
