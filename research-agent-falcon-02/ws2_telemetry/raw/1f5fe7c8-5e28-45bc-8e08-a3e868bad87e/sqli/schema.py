#!/usr/bin/env python3
"""Probe the in-scope /api/send contact endpoint to map its input schema.
Sends one request per field-shape and prints the JSON error body, which the
endpoint returns differentially (real oracle for injection testing).
"""
import json, urllib.request, uuid, sys

URL = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

def post(fields):
    b = "----ic" + uuid.uuid4().hex
    body = "".join(
        f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n"
        for k, v in fields.items()
    ).encode() + f"--{b}--\r\n".encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={b}")
    req.add_header("User-Agent", UA)
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()

BASE = {
    "fname": "ICMARK1", "lname": "Tester", "areacode": "+973",
    "tel": "3612345", "cname": "Acme Test", "subject": "Business enquiry",
    "msg": "Hello authorized VAPT test.", "check": "",
    "targets": '["info@infinitycapital.bh"]',
}

CASES = json.load(open(sys.argv[1]))
for name, over in CASES:
    f = dict(BASE); f.update(over)
    code, data = post(f)
    print(f"### {name} -> HTTP {code} :: {data[:400].decode(errors='replace')}")
