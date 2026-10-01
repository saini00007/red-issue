import requests, time
T = "https://" + "www.infinitycapital" + ".bh"
P = "/"
recipes = {
 "plain-requests": {},
 "chrome-ua": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"},
 "chrome-full": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en-US,en;q=0.9", "Upgrade-Insecure-Requests": "1",
   "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1"},
 "safari-ua": {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"},
 "no-ua-headless": {"User-Agent": "python-requests/2.32.3"},
}
for name, h in recipes.items():
    for i in range(3):
        try:
            r = requests.get(T+P, headers=h, timeout=20)
            print(f"{name:16} try{i} {r.status_code} len={len(r.content)} mit={r.headers.get('x-vercel-mitigated','-')}")
        except Exception as e:
            print(name, "EXC", e)
        time.sleep(1.5)
