import requests, time, sys, random

B = "https://" + "www.infinity" + "capital" + ".bh"
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
})


def get(path, tries=6, delay=6.0, **kw):
    """Paced GET: returns (code, body_bytes, headers) once not 429."""
    for i in range(tries):
        try:
            r = S.get(B + path, timeout=30, **kw)
        except Exception as e:
            return 0, repr(e).encode(), {}
        if r.status_code != 429:
            return r.status_code, r.content, dict(r.headers)
        time.sleep(delay + random.uniform(0, 2))
    return 429, b"", {}


if __name__ == "__main__":
    for d in [6, 10, 20, 35, 60, 90]:
        c, b, h = get("/", tries=1)
        print(f"delta={d:3}s -> {c} len={len(b)}", flush=True)
        if c == 200:
            break
        time.sleep(d)
