#!/usr/bin/env python3
"""Independent verifier for /api/send email-relay claim on infinitycapital.bh.
Non-destructive: each request sends at most ONE message. Optional --sleep to
space calls out. Prints full status + headers + body for evidence.
"""
import argparse, json, sys, time, urllib.request, urllib.error, uuid

API = "https://www.infinitycapital.bh/api/send"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")


def send(targets, subject="Verifier probe", msg="independent verification probe",
         origin="https://www.infinitycapital.bh", referer="https://www.infinitycapital.bh/contact",
         extra=None, tag=""):
    body = {
        "fname": "Verifier", "lname": "Test", "areacode": "973",
        "tel": "5550001234", "cname": "Verifier Co",
        "subject": subject, "msg": msg, "check": "", "targets": targets,
    }
    boundary = "----vfy" + uuid.uuid4().hex
    parts = []
    for k, v in body.items():
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                      % (boundary, k, v)).encode())
    payload = b"".join(parts) + ("--%s--\r\n" % boundary).encode()

    hdrs = {
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "multipart/form-data; boundary=%s" % boundary,
        "Origin": origin,
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    if origin is None:
        hdrs.pop("Origin", None)
    if referer is None:
        hdrs.pop("Referer", None)
    if extra:
        hdrs.update(extra)

    req = urllib.request.Request(API, data=payload, headers=hdrs, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            status, rh, raw = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, rh, raw = e.code, dict(e.headers), e.read()
    except Exception as e:
        print("[%s] EXCEPTION %r" % (tag, e)); return None

    print("[%s] targets=%r" % (tag, targets))
    print("[%s] HTTP %s  (%.2fs)" % (tag, status, time.time() - t0))
    for k in ("x-vercel-mitigated", "x-matched-path", "x-vercel-id", "set-cookie",
              "content-type", "server", "x-robots-tag", "x-ratelimit-limit",
              "x-ratelimit-remaining", "retry-after"):
        if k in rh:
            print("[%s]   %s: %s" % (tag, k, rh[k]))
    body_txt = raw.decode("utf-8", "replace")
    print("[%s] BODY(%d): %s" % (tag, len(raw), body_txt[:700]))
    print()
    return {"targets": targets, "status": status, "headers": rh, "body": body_txt}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--sleep", type=float, default=0.0)
    ap.add_argument("--subject", default="Verifier probe")
    a = ap.parse_args()
    res = []
    for i, t in enumerate(a.targets, 1):
        r = send(t, subject=a.subject, tag="T%d" % i)
        if r:
            res.append(r)
        if a.sleep and i < len(a.targets):
            time.sleep(a.sleep)
    print(json.dumps([{k: r[k] for k in ("targets", "status", "body")} for r in res], indent=2))
