#!/usr/bin/env python3
"""Send the in-scope contact form to /api/send with arbitrary field values.
Usage: python3 sendform.py outfile KEY=VAL KEY=VAL ...
Special key: RAWFILE=/path -> send that file as the whole multipart body (prebuilt).
"""
import sys, json, urllib.request, urllib.parse, uuid, os

HOST = "https://www.infinitycapital.bh"
URL = HOST + "/api/send"

def build(fields):
    b = "----ic" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    parts.append(f"--{b}--\r\n")
    return b, "".join(parts).encode()

outfile = sys.argv[1] if len(sys.argv) > 1 else "out.h"
fields = {
    "fname": "ICMARK1", "lname": "Tester", "areacode": "+973",
    "tel": "3612345", "cname": "Acme Test", "subject": "Business enquiry",
    "msg": "Hello authorized VAPT test.", "check": "",
    "targets": '["info@infinitycapital.bh"]',
}
for a in sys.argv[2:]:
    k, _, v = a.partition("=")
    fields[k] = v

b, body = build(fields)
req = urllib.request.Request(URL, data=body, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={b}")
req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36")
try:
    r = urllib.request.urlopen(req, timeout=30)
    code, hdrs, data = r.status, r.headers, r.read()
except urllib.error.HTTPError as e:
    code, hdrs, data = e.code, e.headers, e.read()
except Exception as e:
    print("ERR", e); sys.exit(1)

with open(outfile, "wb") as f:
    f.write(f"HTTP {code}\n".encode())
    for k, v in hdrs.items():
        f.write(f"{k}: {v}\n".encode())
    f.write(b"\n")
    f.write(data)
print("HTTP", code, "len", len(data), "body:", data[:300])
