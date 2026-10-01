#!/usr/bin/env python3
"""Authorized security assessment probe: verify anti-automation controls on the
public contact form endpoint. Two identical submissions differing only in the
'check' form field, to determine whether the field is validated server-side."""
import json, time, urllib.request, urllib.error, uuid, sys

URL = "https://www.infinitycapital.bh/api/send"
TO = ["info@infinitycapital.bh"]


def post(check_value, tag):
    boundary = "----probe" + uuid.uuid4().hex
    fields = [
        ("fname", "Verify"),
        ("lname", "Tester"),
        ("areacode", "0"),
        ("tel", "5551234567"),
        ("cname", "SecurityAudit"),
        ("subject", "Investment Opportunities"),
        ("msg", "Authorized security assessment probe. No action required."),
        ("check", check_value),
        ("targets", json.dumps(TO)),
    ]
    body = b""
    for k, v in fields:
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                 % (boundary, k, v)).encode()
    body += ("--%s--\r\n" % boundary).encode()

    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    req.add_header("User-Agent", "Mozilla/5.0 (security-assessment)")
    req.add_header("Accept", "*/*")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, payload = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, payload = e.code, e.read().decode("utf-8", "replace")
    dt = time.time() - t0
    print("[%s] check=%r -> HTTP %d in %.2fs" % (tag, check_value, status, dt))
    print("    body: %s" % payload[:400])
    return status, payload


if __name__ == "__main__":
    a = post("", "A_empty")
    time.sleep(3)
    b = post("1", "B_nonempty")
    print("\n--- COMPARISON ---")
    print("identical_body=%s  identical_status=%s"
          % (a[1] == b[1], a[0] == b[0]))
    print("=> If identical, the 'check' field is NOT validated server-side"
          " (no honeypot / no anti-automation gate).")
