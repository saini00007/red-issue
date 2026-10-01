import json, time, urllib.request, urllib.error

HOST = "www" + "." + "infinitycapital" + ".bh"
BASE = "https://" + HOST
PATH = "/api/send"

def send(fields, label, referer=None):
    boundary = "----vrf" + str(int(time.time() * 1000))
    parts = []
    for k, v in fields.items():
        parts.append('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, k, v))
    body = ("".join(parts) + "--%s--\r\n" % boundary).encode("utf-8", "replace")
    req = urllib.request.Request(BASE + PATH, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
    if referer:
        req.add_header("Referer", referer)
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45)
        status, hdrs, data = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, hdrs, data = e.code, dict(e.headers), e.read()
    dt = time.time() - t0
    print("=== %s ===" % label)
    print("REQ  " + json.dumps(fields))
    print("HTTP %s in %.2fs  content-type=%s" % (status, dt, hdrs.get("content-type")))
    print("BODY(%d): %s" % (len(data), data[:600].decode("utf-8", "replace")))
    print()
    return status, data

official = "info@" + HOST
base = {
    "fname": "Verify", "lname": "Tester", "areacode": "+973", "tel": "3600000",
    "cname": "recon-baseline", "subject": "Investment Opportunities",
    "msg": "Baseline verification message from an independent security verifier.",
    "check": "0", "targets": official,
}
send(base, "TEST 1 - baseline: targets = official address (" + official + ")")
