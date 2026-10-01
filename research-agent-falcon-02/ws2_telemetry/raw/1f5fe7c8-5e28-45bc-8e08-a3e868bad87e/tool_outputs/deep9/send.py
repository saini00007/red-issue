#!/usr/bin/env python3
"""deep9 probe: does POST /api/send really relay? Confirm/rep the floor finding.
Uses retry-until-real-fetch (Vercel checkpoint is probabilistic)."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from real import fetch, save, OUT

body = json.dumps({"name": "deep9", "email": "probe@localhost", "message": "probe-message"})
st, b, h = fetch("/api/send", "POST", body)
print("STATUS", st)
if h: print(h[:900])
if b: print("LEN", len(b)); print(b[:600])

# also test the unauth open-relay shape from the prior finding: attacker-chosen recipient
for k in ("to", "recipient", "email", "receiver", "send_to", "dest"):
    payload = json.dumps({"name": "deep9", "message": "probe", k: "probe@localhost"})
    st2, b2, _ = fetch("/api/send", "POST", payload, tries=6)
    print(k, "->", st2, (b2 or b"")[:200])
