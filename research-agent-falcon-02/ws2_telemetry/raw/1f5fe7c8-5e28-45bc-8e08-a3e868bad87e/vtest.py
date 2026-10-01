import requests
B = "https://" + "www.infinity" + "capital" + ".bh"
s = requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36","Accept":"text/html,application/xhtml+xml,*/*;q=0.8"})
variants = [
 ("plain", {}),
 ("xff", {"X-Forwarded-For":"1.1.1.1"}),
 ("gbot", {"User-Agent":"Googlebot/2.1"}),
 ("bingbot", {"User-Agent":"Mozilla/5.0 (compatible; bingbot/2.0)"}),
 ("ps", {"User-Agent":"PostmanRuntime/7.36.0"}),
 ("curl", {"User-Agent":"curl/8.5.0"}),
 ("sm", {"User-Agent":"sqLiMaP/1.10.8"}),
]
for name, h in variants:
    hh = dict(s.headers); hh.update(h)
    try:
        r = s.get(B+"/", headers=hh, timeout=20)
        print(f"{name:12} {r.status_code} len={len(r.content)} mit={r.headers.get('x-vercel-mitigated','-')}")
    except Exception as e:
        print(name, "EXC", e)
