import json, time, urllib.request, urllib.error, uuid, ssl

U = "https://www.infinitycapital.bh/api/send"
SITE_DOMAIN = "infinitycapital.bh"
SITE_EMAIL  = "info@" + SITE_DOMAIN

def post(fields, timeout=45):
    # Build multipart/form-data
    boundary = "----VerifyBoundary" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            ("--%s\r\n" % boundary).encode() +
            ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode() +
            (v if isinstance(v, bytes) else str(v).encode()) + b"\r\n"
        )
    body = b"".join(parts) + ("--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(U, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, "EXC:" + str(e)

def base(targets, tag, **over):
    f = {
        "fname": "VerifyX", "lname": "Probe", "areacode": "+973",
        "tel": "5550000", "cname": "QA", "subject": "ZZprobe-" + tag,
        "msg": "probe body", "check": "zzfilled", "targets": targets,
    }
    f.update(over)
    return f

results = []
tests = [
    ("OWN",   SITE_EMAIL),
    ("EXT_invalid", "zz%d@mailinator.invalid" % int(time.time())),
    ("EXT_alt",      "zz%d@dispostable.invalid" % int(time.time())),
    ("no_at",        "notanemail"),
    ("multi",        "a%d@x.invalid, b%d@y.invalid" % (int(time.time()), int(time.time()))),
]
for tag, tgt in tests:
    st, body = post(base(tgt, tag))
    results.append({"tag": tag, "targets": tgt, "status": st, "body": body})
    print("=== %-12s targets=%s" % (tag, tgt))
    print("    status=%s body=%s" % (st, body.strip()[:400]))
    time.sleep(2)

open("/work/evidence/V_relay_test.json", "w").write(json.dumps(results, indent=2))
print("\nSaved V_relay_test.json")
