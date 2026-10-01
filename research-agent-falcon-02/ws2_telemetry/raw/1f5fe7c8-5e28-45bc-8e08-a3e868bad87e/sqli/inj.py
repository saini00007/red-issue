#!/usr/bin/env python3
"""Injection differential harness for the in-scope /api/send endpoint.

Sends one request per case, records (http_code, body, elapsed_ms) to a JSONL log.
Compares each case against the paired baseline to spot true/false/boolean,
error-based, or time-based oracles.
"""
import json, sys, time, uuid, urllib.request

URL = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

def post(fields, ctype="multipart"):
    if ctype == "multipart":
        b = "----ic" + uuid.uuid4().hex
        body = "".join(
            f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n"
            for k, v in fields.items()
        ).encode() + f"--{b}--\r\n".encode()
        hdr = f"multipart/form-data; boundary={b}"
    else:
        from urllib.parse import urlencode
        body = urlencode(fields).encode()
        hdr = "application/x-www-form-urlencoded"
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", hdr)
    req.add_header("User-Agent", UA)
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45)
        code, data = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, data = e.code, e.read()
    except Exception as e:
        code, data = 0, str(e).encode()
    return code, data, int((time.time() - t0) * 1000)

BASE = {
    "fname": "ICMARK1", "lname": "Tester", "areacode": "+973",
    "tel": "3612345", "cname": "Acme Test", "subject": "Business enquiry",
    "msg": "Hello authorized VAPT test.", "check": "",
    "targets": "delivered@resend.dev",
}
FIELDS = ["fname", "lname", "cname", "subject", "msg", "tel", "areacode", "check", "targets"]

if __name__ == "__main__":
    cases = json.load(open(sys.argv[1]))
    log = sys.argv[2]
    ctype = sys.argv[3] if len(sys.argv) > 3 else "multipart"
    with open(log, "a") as lf:
        for name, over in cases:
            f = dict(BASE); f.update(over)
            code, data, ms = post(f, ctype)
            rec = {"case": name, "http": code, "ms": ms,
                   "body": data[:300].decode(errors="replace"), "over": over}
            lf.write(json.dumps(rec) + "\n")
            lf.flush()
            print(f"{name:34s} http={code} {ms:6d}ms :: {rec['body'][:150]}")
