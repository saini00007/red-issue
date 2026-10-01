#!/usr/bin/env python3
"""Independent verification: recipient control on POST /api/send"""
import json, sys, time, urllib.request, urllib.error

API = "https://www.infinitycapital.bh/api/send"

def post(fields, label, timeout=45):
    """multipart/form-data POST"""
    b = "----VFY%s" % (str(time.time()).replace(".", ""))
    parts = []
    for k, v in fields.items():
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (b, k, v)).encode())
    body = b"".join(parts) + ("--%s--\r\n" % b).encode()
    req = urllib.request.Request(API, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % b)
    req.add_header("Origin", "https://www.infinitycapital.bh")
    req.add_header("Referer", "https://www.infinitycapital.bh/contact")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        code, txt, hdrs = r.status, r.read().decode("utf8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        code, txt, hdrs = e.code, e.read().decode("utf8", "replace"), dict(e.headers)
    except Exception as e:
        code, txt, hdrs = 0, "EXC:%s" % e, {}
    dt = round(time.time() - t0, 2)
    print("[%s] HTTP %s (%.2fs)\n  %s" % (label, code, dt, txt.strip()[:600]))
    return {"label": label, "code": code, "body": txt.strip(), "sec": dt,
            "xvercel": hdrs.get("x-vercel-id", "")}

if __name__ == "__main__":
    print(json.dumps(post({"foo": "bar"}, "probe"), indent=1))
