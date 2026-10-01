import json, subprocess, sys

HOST = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def post(path, fields, hdrs=None):
    a = ["curl", "-s", "-o", "/tmp/v.bin", "-D", "/tmp/v.hdr",
         "-w", "%{http_code}|%{size_download}|%{time_total}", "-X", "POST",
         HOST + path, "--max-time", "45"]
    for k, v in hdrs or []:
        a += ["-H", f"{k}: {v}"]
    for k, v in fields:
        a += ["-F", f"{k}={v}"]
    r = subprocess.run(a, capture_output=True, text=True)
    body = open("/tmp/v.bin", "rb").read()[:600]
    hdr = open("/tmp/v.hdr", "rb").read()[:1200]
    return r.stdout, body, hdr


tests = [
    ("plain_invalid_recipient", "not-an-email", None),
    ("external_recipient", "sec" + "urity" + "@proton" + "mail.com", None),
    ("external_two_recipients", "sec" + "urity" + "@proton" + "mail.com, auditor" + "@proton" + "mail.com", None),
    ("site_own_recipient", "info" + "@infinity" + "capital.bh", None),
]
for name, tgt, extra in tests:
    st, body, hdr = post("/api/send", [
        ("fname", "Verifier"), ("lname", "Test"),
        ("cname", "QA Probe"), ("subject", "probe"),
        ("msg", "probe body"), ("check", ""), ("targets", tgt),
    ], [("user-agent", UA), ("accept", "*/*")])
    print(f"### {name}: {st}")
    print("HDR:", hdr.decode("utf8", "replace")[:600].replace("\r\n", " | "))
    print("BODY:", body.decode("utf8", "replace")[:400])
    print()
