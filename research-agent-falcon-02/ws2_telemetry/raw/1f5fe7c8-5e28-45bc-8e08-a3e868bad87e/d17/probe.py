import requests
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
tests = [
 ("IMG-valid", "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"),
 ("IMG-empty", "/_next/image?url=&w=1080&q=75"),
 ("IMG-127", "/_next/image?url=http%3A%2F%2F127.0.0.1%2F&w=1080&q=75"),
 ("API-send-GET", "/api/send"),
 ("API-root", "/api/?id=1"),
 ("404q", "/404?q=test"),
 ("home-page2", "/?page=2"),
 ("contact-cb", "/contact?cb=1"),
]
import os
os.makedirs('d17', exist_ok=True)
for name, p in tests:
    try:
        r = requests.get(T+p, headers=H, timeout=25, allow_redirects=True)
        print(name, r.status_code, len(r.content), r.headers.get('content-type'), r.headers.get('x-vercel-mitigated'), r.headers.get('x-matched-path'))
        open('d17/%s.bin'%name.replace('/','_'),'wb').write(r.content)
    except Exception as e:
        print(name, "ERR", e)
