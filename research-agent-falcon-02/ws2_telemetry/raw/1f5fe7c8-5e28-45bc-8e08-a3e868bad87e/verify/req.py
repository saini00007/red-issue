#!/usr/bin/env python3
import json, sys, time, urllib.request, urllib.error, urllib.parse, uuid

BASE = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"

def post_multipart(fields, referer=BASE + "/contact", timeout=45):
    """fields: dict name -> (filename|None, value)"""
    b = uuid.uuid4().hex
    boundary = "----verify" + b
    parts = []
    for k, v in fields.items():
        parts.append(
            ("--%s\r\n" % boundary).encode() +
            ('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode() +
            (v if isinstance(v, bytes) else str(v).encode()) + b"\r\n")
    body = b"".join(parts) + ("--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(BASE + "/api/send", data=body, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Origin", BASE)
    req.add_header("Referer", referer)
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return -1, {}, str(e).encode()

def post_urlencoded(fields, referer=BASE + "/contact", timeout=45):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(BASE + "/api/send", data=data, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "*/*")
    req.add_header("Origin", BASE)
    req.add_header("Referer", referer)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return -1, {}, str(e).encode()

def show(tag, res):
    st, hdr, body = res
    keep = {k: v for k, v in hdr.items() if k.lower() in
            ("content-type", "x-vercel-id", "server", "date", "x-matched-path", "x-vercel-cache")}
    print("### %s" % tag)
    print("STATUS: %s" % st)
    print("HDRS: %s" % json.dumps(keep))
    print("BODY: %s" % body[:800].decode("utf-8", "replace"))
    print()
    return {"tag": tag, "status": st, "headers": keep, "body": body[:2000].decode("utf-8", "replace")}

if __name__ == "__main__":
    tag = sys.argv[1]
    tgt = sys.argv[2]
    subj = sys.argv[3] if len(sys.argv) > 3 else "Verifier probe"
    check = sys.argv[4] if len(sys.argv) > 4 else ""
    mode = sys.argv[5] if len(sys.argv) > 5 else "multipart"
    f = {
        "fname": "Verif", "lname": "Tester", "areacode": "+973", "tel": "5550100",
        "cname": "Independent Verifier", "subject": subj,
        "msg": "Message body from independent verifier. tag=%s" % tag,
        "check": check, "targets": tgt,
    }
    r = (post_multipart if mode == "multipart" else post_urlencoded)(f)
    out = show(tag, r)
    fn = "res_%s.json" % tag
    json.dump(out, open(fn, "w"), indent=1)
    print("saved ->", fn)
