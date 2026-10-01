#!/usr/bin/env python3
"""
Independent verification: missing anti-automation (rate limit / CAPTCHA / honeypot
enforcement) on POST /api/send of https://www.infinitycapital.bh/
Authorized, benign, non-spam test submissions. One real-looking message.
"""
import json, ssl, sys, time, urllib.request, urllib.error, urllib.parse

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
HDRS = {
    "User-Agent": UA,
    "Origin": BASE,
    "Referer": BASE + "/contact",
    "Accept": "*/*",
}
CTX = ssl.create_default_context()

def build(fields):
    # multipart/form-data, exactly the shape the client JS produces
    boundary = "----verifyBoundary7f3a91c4e2"
    parts = []
    for k, v in fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{k}"\r\n\r\n'
            f"{v}\r\n"
        )
    body = ("".join(parts) + f"--{boundary}--\r\n").encode()
    h = dict(HDRS)
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    return body, h

def send(fields, timeout=25):
    body, h = build(fields)
    req = urllib.request.Request(BASE + "/api/send", data=body, headers=h, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace"), round(time.time()-t0, 2)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace"), round(time.time()-t0, 2)
    except Exception as e:
        return None, {}, f"ERROR: {type(e).__name__}: {e}", round(time.time()-t0, 2)

def base_msg(i):
    return ("Authorized security verification of anti-automation controls on this "
            f"public contact endpoint (sequence {i}). No marketing content. Please ignore.")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    out = []

    def rec(label, fields):
        st, hd, bd, el = send(fields)
        rec_ = {"label": label, "status": st, "elapsed_s": el, "body": bd[:600],
                "retry_after": hd.get("Retry-After") or hd.get("retry-after"),
                "ratelimit": {k: v for k, v in hd.items() if "ratelimit" in k.lower() or "rate-limit" in k.lower()},
                "server": hd.get("server"), "x_vercel_cache": hd.get("x-vercel-cache")}
        out.append(rec_)
        print(json.dumps(rec_, ensure_ascii=False))
        return st, bd

    if mode == "baseline":
        # 1) honeypot EMPTY (what a bot would send / field absent)
        rec("honeypot_empty", {
            "fname": "Verify", "lname": "Tester", "areacode": "+973", "tel": "3612345",
            "cname": "Independent Verification", "subject": "Investment Opportunities",
            "msg": base_msg(1), "check": "", "targets": "info@infinitycapital.bh"})
        time.sleep(2)
        # 2) honeypot FILLED (what a naive human bot that scrapes the DOM would send)
        rec("honeypot_filled", {
            "fname": "Verify", "lname": "Tester", "areacode": "+973", "tel": "3612345",
            "cname": "Independent Verification", "subject": "Investment Opportunities",
            "msg": base_msg(2), "check": "on", "targets": "info@infinitycapital.bh"})
        time.sleep(2)
        # 3) honeypot ABSENT entirely
        rec("honeypot_absent", {
            "fname": "Verify", "lname": "Tester", "areacode": "+973", "tel": "3612345",
            "cname": "Independent Verification", "subject": "Investment Opportunities",
            "msg": base_msg(3), "targets": "info@infinitycapital.bh"})

    with open(f"/work/evidence/ic_{mode}_results.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
