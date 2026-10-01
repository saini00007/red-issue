#!/usr/bin/env python3
# Independent reproduction of open-email-relay claim on Infinity Capital /api/send
import sys, json, urllib.request, urllib.error, uuid, ssl

HOST = "https://" + "infinitycapital" + ".bh"
EP   = HOST + "/api/send"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

def multipart(fields):
    b = "----IVR" + uuid.uuid4().hex
    out = []
    for k, v in fields:
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    out.append(f"--{b}--\r\n")
    return b, "".join(out).encode()

def send(fields, label, send_origin=True):
    b, body = multipart(fields)
    hdrs = {
        "User-Agent": UA,
        "Content-Type": f"multipart/form-data; boundary={b}",
        "Accept": "*/*",
        "Content-Length": str(len(body)),
    }
    if send_origin:
        hdrs["Origin"] = "https://www." + "infinitycapital" + ".bh"
        hdrs["Referer"] = "https://www." + "infinitycapital" + ".bh/contact"
    req = urllib.request.Request(EP, data=body, headers=hdrs, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=45)
        code, txt, extra = r.status, r.read(4000).decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        code, txt, extra = e.code, e.read(4000).decode("utf-8", "replace"), dict(e.headers)
    except Exception as e:
        code, txt, extra = "ERR", repr(e), {}
    rec = {
        "label": label,
        "url": EP,
        "multipart_body": body.decode("utf-8", "replace"),
        "origin_header_sent": send_origin,
        "status": code,
        "resp_headers": {k: v for k, v in extra.items()
                         if k.lower() in ("x-vercel-id", "x-matched-path", "x-robots-tag",
                                          "content-type", "server", "set-cookie")},
        "resp_body": txt,
    }
    print("=" * 78)
    print(f"[{label}] HTTP {code}")
    print("-" * 78)
    print("REQUEST FIELDS:", {k: v for k, v in fields})
    print("RESPONSE:", txt[:600])
    return rec

if __name__ == "__main__":
    results = []
    base = [
        ("fname", "Verifier"), ("lname", "Test"), ("areacode", "+973"),
        ("tel", "5551234"), ("cname", "Verifier QA"),
        ("subject", "Independent relay verification"),
        ("msg", "Independent verifier probe - please ignore."),
        ("check", "on"),
    ]
    results.append(send(base + [("targets", "info@infinitycapital.bh")],
                        "A/site-own-mailbox", send_origin=True))
    results.append(send(base, "B/no-targets-field", send_origin=True))
    with open(sys.argv[1] if len(sys.argv) > 1 else "/work/IVRFN/phase1.json", "w") as fh:
        json.dump(results, fh, indent=1)
