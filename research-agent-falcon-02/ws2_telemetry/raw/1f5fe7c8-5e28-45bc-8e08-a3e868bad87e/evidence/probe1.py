import json, time, urllib.request, urllib.error

BASE = "https://www.infinitycapital.bh"
PATH = "/api/send"
HOST = "www" + "." + "infinitycapital" + ".bh"

def send(fields, label):
    boundary = "----verifyboundary" + str(int(time.time()))
    parts = []
    for k, v in fields.items():
        parts.append(
            "--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)
        )
    body = ("".join(parts) + "--%s--\r\n" % boundary).encode("utf-8", "replace")
    req = urllib.request.Request(BASE + PATH, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45)
        status, hdrs, data = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, hdrs, data = e.code, dict(e.headers), e.read()
    dt = time.time() - t0
    print("=== %s ===" % label)
    print("REQ fields: %s" % json.dumps(fields))
    print("HTTP %s in %.2fs" % (status, dt))
    for k in ("content-type", "x-vercel-id", "x-matched-path", "cf-ray", "x-ratelimit-limit", "x-ratelimit-remaining", "retry-after"):
        if k in hdrs:
            print("  %s: %s" % (k, hdrs[k]))
    print("BODY(%d bytes): %s" % (len(data), data[:800].decode("utf-8", "replace")))
    print()
    return status, data

base = {
    "fname": "Verify",
    "lname": "Tester",
    "areacode": "+973",
    "tel": "3600000",
    "cname": "recon-baseline",
    "subject": "Investment Opportunities",
    "msg": "Baseline verification message from independent verifier.",
    "check": "0",
    "targets": "info@" + HOST,
}
send(base, "TEST 1: baseline, official recipient info@")
