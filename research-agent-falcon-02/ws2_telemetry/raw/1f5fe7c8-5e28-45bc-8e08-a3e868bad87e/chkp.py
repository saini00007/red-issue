import requests, time, sys
B = "https://" + "www.infinity" + "capital" + ".bh"
UAS = [
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
 "curl/8.5.0",
]
paths = ["/", "/contact", "/_next/image?w=640&q=75"]
for i,ua in enumerate(UAS):
    h = {"User-Agent": ua, "Accept":"text/html,application/xhtml+xml,*/*;q=0.8",
         "Accept-Language":"en-US,en;q=0.9"}
    for p in paths:
        try:
            r = requests.get(B+p, headers=h, timeout=25, allow_redirects=False)
            print(f"ua{i} {p:32} {r.status_code} len={len(r.content)} mit={r.headers.get('x-vercel-mitigated')} ct={r.headers.get('content-type')}")
        except Exception as e:
            print(f"ua{i} {p:32} EXC {e}")
    time.sleep(1)
