import json, subprocess

BASE = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# IANA reserved documentation domain - non-routable, not a real mailbox.
EXT = "probe" + "@" + "ex" + "ample" + ".com"
SITE = "info" + "@" + "inf" + "inity" + "capital" + ".bh"

def send(label, body, ctype="application/x-www-form-urlencoded", extra=None):
    if ctype == "application/x-www-form-urlencoded":
        data = "&".join("%s=%s" % (k, v) for k, v in body.items())
    else:
        data = json.dumps(body)
    cmd = ["curl", "-s", "-i", "-X", "POST", BASE,
           "-H", "Content-Type: " + ctype, "-H", "User-Agent: " + UA,
           "-H", "Accept: */*", "--data-raw", data, "--max-time", "30"]
    if extra:
        cmd[4:4] = extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout or ""
    status = out.split("\n", 1)[0].strip() if out else "NO_RESPONSE"
    body_txt = out.split("\r\n\r\n", 1)[-1] if out else (r.stderr or "")[:300]
    print("### %s" % label)
    print("REQ   targets=%r ctype=%s" % (body.get("targets"), ctype))
    print("STATUS: %s" % status)
    print("BODY : %s" % body_txt.strip()[:400])
    print("-" * 70)
    return status, body_txt

base = dict(fname="Verifier", lname="Check", areacode="000", tel="0000000",
            cname="Verifier", subject="Verifier probe", msg="Independent verification body",
            check="on")

b1 = dict(base); b1["targets"] = EXT
send("T1 external recipient, form-encoded, NO cookies, NO Origin, NO Referer", b1)

b2 = dict(base); b2["targets"] = "QA Tester <" + EXT + ">"; b2["subject"] = "Verifier probe B"
send("T2 'Name <external>' recipient form", b2)

b3 = dict(base); b3["targets"] = SITE; b3["subject"] = "Verifier probe C control"
send("T3 CONTROL -> site own inbox", b3)

b4 = dict(base); b4["targets"] = [EXT, SITE]; b4["subject"] = "Verifier probe D"
send("T4 targets as JSON array [external, site]", b4, ctype="application/json")
