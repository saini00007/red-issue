import requests, sys
s = requests.Session()
s.verify = False
import urllib3; urllib3.disable_warnings()
BASE = "https://www.infinitycapital.bh"
headers = {
 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"+"120.0.0.0 Safari/537.36",
 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
 "Accept-Language": "en-US,en;q=0.9",
 "Accept-Encoding": "gzip, deflate, br",
 "Upgrade-Insecure-Requests": "1",
 "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
}
paths = ["/", "/about", "/contact", "/api/", "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75",
         "/favicon.ico", "/robots.txt", "/sitemap.xml", "/atom.xml", "/login", "/admin", "/.env", "/.git/config",
         "/api/health", "/api/v1", "/_next/static/chunks/main.js", "/nonexistentpath-zzz"]
for p in paths:
    try:
        r = s.get(BASE+p, headers=headers, timeout=15, allow_redirects=True)
        print(f"{r.status_code} {len(r.content):8d} {p}  -> {r.url}")
        if r.status_code == 200:
            open("/work_path/out_"+p.strip('/').replace('/','_').replace('?','_')[:40]+".bin","wb").write(r.content)
    except Exception as e:
        print("ERR", p, e)
