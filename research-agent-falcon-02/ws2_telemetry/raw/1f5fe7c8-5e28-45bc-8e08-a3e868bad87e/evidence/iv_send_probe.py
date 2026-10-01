#!/usr/bin/env python3
"""Independent verification: no anti-automation / rate limiting on POST /api/send
Target: https://www.infinitycapital.bh/api/send  (in scope)
Authorized security assessment verification. Sends only benign form data.
"""
import json, time, urllib.parse, urllib.request, urllib.error, ssl, sys

URL = "https://www.infinitycapital.bh/api/send"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "12" + "6.0.0.0 Safari/537.36")

def post(fields, timeout=40):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Origin", "https://www.infinitycapital.bh")
    req.add_header("Referer", "https://www.infinitycapital.bh/contact")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
            hdrs = dict(r.headers)
            code = r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        hdrs = dict(e.headers)
        code = e.code
    except Exception as e:
        return {"code": "ERR", "body": repr(e), "hdrs": {}, "dt": time.time()-t0}
    return {"code": code, "body": body, "hdrs": hdrs, "dt": round(time.time()-t0, 3)}

def base(**kw):
    f = {
        "fname": "Independent",
        "lname": "Verifier",
        "areacode": "973",
        "tel": "5551234",
        "cname": "Independent Verifier",
        "subject": "Security assessment verification",
        "msg": "Authorized security assessment verification request. No action required.",
        "check": "",
        "targets": "verification-probe@protonmail.com",
    }
    f.update(kw)
    return f

if __name__ == "__main__":
    out = {"target": URL, "note": "single benign probe, no flood"}
    out["A_honeypot_empty"] = post(base())
    time.sleep(3)
    out["B_honeypot_filled"] = post(base(check="1"))
    time.sleep(3)
    out["C_honeypot_bogus"] = post(base(check="iam-a-bot-" + str(int(time.time()))))
    print(json.dumps(out, indent=2)[:6000])
    with open("/work/evidence/iv_honeypot_probe.json", "w") as fh:
        json.dump(out, fh, indent=2)
