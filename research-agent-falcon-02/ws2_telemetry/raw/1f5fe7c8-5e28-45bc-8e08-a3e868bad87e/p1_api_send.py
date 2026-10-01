#!/usr/bin/env python3
"""Probe harness for POST /api/send  (authorized VAPT, proof-not-damage)."""
import subprocess, json, sys, time, os

URL = "https://www." + "infinity" + "capital" + ".bh" + "/api/send"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15"
TARGETS = json.dumps(["info@" + "infinity" + "capital" + ".bh"])
SUBJ = "Investment Opportunities"

BASE = {
    "fname": "John", "lname": "Doe", "areacode": "973", "tel": "5551234",
    "cname": "AcmeCorp", "subject": SUBJ,
    "msg": "Hello, this is an authorized security assessment test message.",
    "check": "", "targets": TARGETS,
}

def post(fields, hdrs=None):
    args = ["curl", "-s", "-o", "/tmp/_o", "-w", "%{http_code}|%{size_download}|%{time_total}",
            "-A", UA, "-H", "Accept: application/json", "-X", "POST", URL]
    for k, v in (hdrs or {}).items():
        args += ["-H", "%s: %s" % (k, v)]
    for k, v in fields.items():
        args += ["--data-urlencode", "%s=%s" % (k, v)]
    t0 = time.time()
    out = subprocess.run(args, capture_output=True, text=True, timeout=60).stdout
    try:
        body = open("/tmp/_o", "rb").read()[:300].decode("utf8", "replace")
    except Exception:
        body = ""
    code = out.split("|")[0] if out else "ERR"
    return code, body.strip(), round(time.time() - t0, 3)

def show(label, **over):
    f = dict(BASE); f.update(over)
    c, b, el = post(f)
    print("%-34s %-6s %-6s %s" % (label, c, el, b[:170]))
    return c, b

if __name__ == "__main__":
    print("URL:", URL)
    show("BASELINE")
    show("VALID-subject-alt", subject="Partnership Inquiries")
    show("BAD-subject", subject="Nonexistent Subject")
    show("empty msg", msg="")
    show("no targets", targets="[]")
