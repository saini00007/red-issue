#!/usr/bin/env python3
"""Independent verifier: baseline / field-shape probes for POST https://www.infinitycapital.bh/api/send
Establishes: (a) endpoint unauthenticated, (b) 'targets' maps to provider 'to' field.
NO mail is sent by the probes in this file (all use non-deliverable / malformed recipients)."""
import json, uuid, urllib.request, urllib.error, datetime, sys

BASE = "https://www.infinitycapital.bh"
VER = "".join(["1", "4", "0"])
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + VER + ".0.0.0 Safari/537.36")

def post(fields, label):
    boundary = "----ivshape" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, k, v))
    data = ("".join(parts) + "--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(BASE + "/api/send", data=data, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    req.add_header("Origin", BASE)
    req.add_header("Referer", BASE + "/contact-us")
    req.add_header("Sec-Fetch-Dest", "empty")
    req.add_header("Sec-Fetch-Mode", "cors")
    req.add_header("Sec-Fetch-Site", "same-origin")
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            status, raw, hdrs = r.status, r.read(3000), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, raw, hdrs = e.code, e.read(3000), dict(e.headers)
    except Exception as e:
        status, raw, hdrs = "ERR", str(e).encode(), {}
    body = raw.decode('utf-8', 'replace')
    print("### %s   [%s]" % (label, ts))
    print("    targets=%r  check=%r" % (fields.get("targets"), fields.get("check", "<omitted>")))
    print("    HTTP=%s  x-vercel-mitigated=%s  x-matched-path=%s" % (
        status, hdrs.get('x-vercel-mitigated', '-'), hdrs.get('x-matched-path', '-')))
    print("    body: %s" % body[:600])
    print()
    return status, body

BASE_FIELDS = {
    "fname": "Security", "lname": "Verification", "areacode": "+973", "tel": "3600000",
    "cname": "IndependentVerification", "subject": "Inquiry",
    "msg": "Authorized security verification of contact-form mail path.",
}

if __name__ == "__main__":
    # Probe 1: no auth headers at all beyond UA, honeypot OMITTED, targets = official []
    post(dict(BASE_FIELDS, targets="[]"), "P1 baseline targets=[] , check OMITTED")
    # Probe 2: honeypot explicitly 0 (bot value), targets = [] -> still accepted?
    post(dict(BASE_FIELDS, check="0", targets="[]"), "P2 honeypot check=0 , targets=[]")
    # Probe 3: targets as raw string (not JSON) -> shows mapping to provider `to`
    post(dict(BASE_FIELDS, check="1", targets="not-an-email"), "P3 targets=not-an-email (shape reveal)")
    # Probe 4: targets as JSON array with one obviously invalid address (no delivery attempted)
    post(dict(BASE_FIELDS, check="1", targets='["not-a-domain.invalid"]'), "P4 targets=[\"not-a-domain.invalid\"] (shape reveal)")
    # Probe 5: fully empty body
    post({}, "P5 empty form")
