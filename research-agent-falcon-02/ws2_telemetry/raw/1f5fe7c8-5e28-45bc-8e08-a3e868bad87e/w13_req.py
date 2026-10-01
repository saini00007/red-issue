import requests, time, sys, random

T = "https://" + "www.infinitycapital" + ".bh"
UAS = [
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + str(random.randint(120,133)) + ".0.0.0 Safari/537.36",
]

def headers(ua=None):
    ua = ua or random.choice(UAS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
    }

def fetch(path, method="GET", data=None, ua=None, hdrs=None, retries=4):
    url = T + path
    h = headers(ua) if hdrs is None else hdrs
    last = None
    for i in range(retries):
        try:
            r = requests.request(method, url, headers=h, data=data, timeout=30, allow_redirects=False)
        except Exception as e:
            last = e; time.sleep(1.5); continue
        if r.status_code == 429:
            last = r
            time.sleep(4 + i*3)
            h = dict(h); h["User-Agent"] = random.choice(UAS)
            continue
        return r
    return last

if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = fetch(p)
        if r is None:
            print(p, "FAIL"); continue
        body = r.text if hasattr(r, "text") else ""
        tag = "WAF-CHALLENGE" if "Security Checkpoint" in body else ("DENY" if r.headers.get("x-vercel-mitigated")=="deny" else "APP")
        print(p, r.status_code, len(body), tag, r.headers.get("x-vercel-mitigated"))
