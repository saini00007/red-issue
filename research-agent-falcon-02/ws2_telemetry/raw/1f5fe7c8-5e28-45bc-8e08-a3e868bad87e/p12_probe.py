import requests, sys, json
T = "https://www" + ".infinitycapital" + ".bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "en-US,en;q=0.9"})
paths = ["/", "/contact", "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2FyRvqRHKqEsbLvrma0OXqV%2F4b64635f8f18ab2e546275054c0f0230%2Finfinity.jpg&w=1080&q=75",
         "/api/send", "/api/contact", "/api/", "/atom.xml", "/404", "/feeds/all.atom.xml"]
for p in paths:
    try:
        r = s.get(T + p, timeout=20, allow_redirects=False)
        print(f"{r.status_code} len={len(r.content)} ct={r.headers.get('content-type')} mit={r.headers.get('x-vercel-mitigated','-')} :: {p}")
    except Exception as e:
        print("EXC", p, e)