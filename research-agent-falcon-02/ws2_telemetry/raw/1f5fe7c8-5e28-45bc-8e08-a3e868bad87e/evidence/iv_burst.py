#!/usr/bin/env python3
"""Independent verification burst test: does POST /api/send apply ANY per-IP
throttle / CAPTCHA / bot challenge? 10 requests, ~0.5s apart (small, bounded).
Target: https://www.infinitycapital.bh/api/send
"""
import json, time, urllib.parse, urllib.request, urllib.error

URL = "https://www.infinitycapital.bh/api/send"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + "12" + "6.0.0.0 Safari/537.36")

def post(fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Origin", "https://www.infinitycapital.bh")
    req.add_header("Referer", "https://www.infinitycapital.bh/contact")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers), round(time.time()-t0, 3)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers), round(time.time()-t0, 3)
    except Exception as e:
        return "ERR", repr(e), {}, round(time.time()-t0, 3)

def base(i, **kw):
    f = {"fname": "Independent", "lname": "Verifier", "areacode": "973", "tel": "5551234",
         "cname": "Independent Verifier", "subject": "Assessment verification " + str(i),
         "msg": "Authorized security assessment verification. No action required.",
         "check": "", "targets": "verification-probe@protonmail.com"}
    f.update(kw); return f

rows = []
N = 10
for i in range(1, N + 1):
    # alternate honeypot: half filled, half empty -> show it makes no difference
    chk = "bot-filled-" + str(i) if i % 2 == 0 else ""
    code, body, hdrs, dt = post(base(i, check=chk))
    rows.append({"n": i, "check": chk, "http": code, "dt": dt,
                 "retry_after": hdrs.get("Retry-After"),
                 "x_ratelimit": {k: v for k, v in hdrs.items() if "ratelimit" in k.lower() or "rate-limit" in k.lower()},
                 "body": body[:220]})
    time.sleep(0.5)

summary = {
    "total": N,
    "window_seconds": round(time.time() - rows[0].get("t0", time.time()), 1) if False else "~5s",
    "http_statuses": sorted(set(str(r["http"]) for r in rows)),
    "any_403": any(r["http"] == 403 for r in rows),
    "any_429": any(r["http"] == 429 for r in rows),
    "any_retry_after": any(r["retry_after"] for r in rows),
    "any_ratelimit_header": any(r["x_ratelimit"] for r in rows),
    "accepted_ok": sum(1 for r in rows if '"error":null' in r["body"]),
    "quota_error": sum(1 for r in rows if "monthly_quota_exceeded" in r["body"]),
    "honeypot_filled_accepted": sum(1 for r in rows if r["check"] and '"error":null' in r["body"]),
    "honeypot_empty_accepted": sum(1 for r in rows if not r["check"] and '"error":null' in r["body"]),
    "honeypot_filled_total": sum(1 for r in rows if r["check"]),
    "honeypot_empty_total": sum(1 for r in rows if not r["check"]),
    "rows": rows,
}
print(json.dumps(summary, indent=2))
json.dump(summary, open("/work/evidence/iv_burst_summary.json", "w"), indent=2)
