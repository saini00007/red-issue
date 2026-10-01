#!/usr/bin/env python3
"""Independent probe of POST /api/send on https://www.infinitycapital.bh/
Stage 1: NO-SEND probes only (empty / invalid recipient) to characterise endpoint.
Does NOT send any real email to any third party.
"""
import sys, json, requests

BASE = "https://www.infinitycapital.bh"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

HDRS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": BASE,
    "Referer": BASE + "/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def show(title, r):
    print("=" * 70)
    print(title)
    print("  status      :", r.status_code)
    print("  server      :", r.headers.get("server"))
    print("  mitigated   :", r.headers.get("x-vercel-mitigated"))
    print("  ctype       :", r.headers.get("content-type"))
    body = r.text
    print("  body[:400]  :", repr(body[:400]))
    print("  is_challenge:", "Vercel Security Checkpoint" in body)
    return r


def main():
    s = requests.Session()
    s.headers.update(HDRS)

    # Baseline: site reachability
    show("1) GET / (baseline reachability)", s.get(BASE + "/", timeout=40))

    # Empty POST, no fields at all -> no email can be sent
    show("2) POST /api/send  (no fields, no email possible)",
         s.post(BASE + "/api/send", timeout=40))

    # Field-name discovery with impossible recipient (RFC-invalid TLD)
    files = {
        "targets": (None, "not-a-real-domain.invalid"),
        "fname": (None, "Verifier"),
        "lname": (None, "Probe"),
        "cname": (None, "Probe Corp"),
        "subject": (None, "Probe"),
        "msg": (None, "harmless probe"),
        "tel": (None, "000"),
        "check": (None, "0"),
    }
    show("3) POST /api/send  (targets=*.invalid -> provider must reject, no mail sent)",
         s.post(BASE + "/api/send", files=files, timeout=40))


if __name__ == "__main__":
    main()
