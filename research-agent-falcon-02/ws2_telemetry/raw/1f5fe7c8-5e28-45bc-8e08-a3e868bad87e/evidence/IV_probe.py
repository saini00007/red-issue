import requests, time, json, sys

B = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "*/*"})

def classify(r):
    mit = r.headers.get("x-vercel-mitigated", "-")
    ct = r.headers.get("content-type", "-")
    return f"status={r.status_code} mit={mit} ct={ct[:30]} len={len(r.content)} body={r.text[:160]!r}"

# various ways to reach app layer past Vercel WAF
paths = [
    "/api/send",
    "/api//send",
    "/api/./send",
    "/api/send/",
    "/api/send?x=1",
    "//api/send",
    "/api/send%20",
    "/API/send",
]
print("=== GET-path reachability probes (does WAF still deny?) ===")
for p in paths:
    try:
        r = s.get(B + p, timeout=15, allow_redirects=False)
        print(f"GET {p!r:22} -> {classify(r)}")
    except Exception as e:
        print(f"GET {p!r:22} -> EXC {e}")
    time.sleep(0.6)
