#!/usr/bin/env python3
import sys, time, urllib.request, urllib.error

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
BASE = "https://www.infinitycapital.bh"

def get(path, hdrs=None, method="GET", data=None, timeout=25):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    for k, v in (hdrs or {}).items():
        req.add_header(k, v)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        b = r.read()
        return r.status, dict(r.headers), b
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return -1, {}, str(e).encode()

if __name__ == "__main__":
    paths = sys.argv[1:] or ["/", "/contact", "/_next/image?w=100", "/api/send", "/api/?id=1&page=2", "/404"]
    for p in paths:
        code, h, b = get(p)
        mv = h.get("x-vercel-mitigated", "-")
        ct = h.get("content-type", "-")[:40]
        print(f"{code} len={len(b):6d} mitigated={mv:10s} ct={ct:35s} {p}")
        if code == 200 and len(b) < 2000:
            print("    BODY:", b[:200])
        time.sleep(2)
